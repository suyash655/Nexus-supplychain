"""
NEXUS — Multi-Source Connector Framework
==========================================
Abstract connector interface + implementations for CSV, Database, S3, and API sources.
This is what separates a "script" from a "platform."
"""

import os
import io
import json
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import pandas as pd  # type: ignore
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.models import Base  # type: ignore


# ──────────────────────────────────────────────
# Connector Model (persisted configuration)
# ──────────────────────────────────────────────

def _utcnow():
    return datetime.now(timezone.utc)


class ConnectorConfig(Base):
    """Saved connector configurations for repeatable data ingestion."""
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    connector_type = Column(String)  # csv, database, s3, api, webhook
    config_json = Column(JSON)       # connection details (encrypted in prod)
    schedule = Column(String, nullable=True)  # cron expression or "manual"
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String, nullable=True)  # success, error, running
    last_sync_rows = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)  # user_id
    created_at = Column(DateTime, default=_utcnow)


class DataLineage(Base):
    """Column-level data lineage tracking for audit and governance."""
    __tablename__ = "data_lineage"

    id = Column(Integer, primary_key=True, index=True)
    source_connector = Column(String)        # connector name
    source_table = Column(String, nullable=True)
    source_column = Column(String, nullable=True)
    target_table = Column(String)
    target_column = Column(String)
    transformation = Column(Text, nullable=True)  # description of transform
    data_hash = Column(String, nullable=True)      # hash for change detection
    row_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)


# ──────────────────────────────────────────────
# Abstract Connector
# ──────────────────────────────────────────────

class BaseConnector(ABC):
    """Abstract base class for all data connectors."""

    connector_type: str = "base"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test that the connector can reach the data source."""
        pass

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data from the source and return a DataFrame."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Return the schema of the data source."""
        try:
            df = self.extract()
            return {
                "columns": [
                    {"name": col, "dtype": str(df[col].dtype), "sample": str(df[col].iloc[0]) if len(df) > 0 else None}
                    for col in df.columns
                ],
                "row_count": len(df),
            }
        except Exception as e:
            return {"error": str(e)}

    def compute_lineage(self, df: pd.DataFrame, target_table: str) -> List[Dict[str, Any]]:
        """Generate lineage records for the extracted data."""
        records = []
        for col in df.columns:
            col_hash = hashlib.md5(df[col].astype(str).to_json().encode()).hexdigest()[:16]
            records.append({
                "source_connector": self.config.get("name", self.connector_type),
                "source_column": col,
                "target_table": target_table,
                "target_column": col,
                "transformation": "raw_ingest",
                "data_hash": col_hash,
                "row_count": len(df),
            })
        return records


# ──────────────────────────────────────────────
# CSV Connector
# ──────────────────────────────────────────────

class CSVConnector(BaseConnector):
    """Ingest from CSV/Excel files (local or uploaded)."""

    connector_type = "csv"

    def test_connection(self) -> Dict[str, Any]:
        path = self.config.get("file_path", "")
        if path and os.path.exists(path):
            return {"status": "ok", "message": f"File found: {path}"}
        # For uploaded content (bytes)
        if self.config.get("content"):
            return {"status": "ok", "message": "Content provided directly"}
        return {"status": "error", "message": "No file found"}

    def extract(self) -> pd.DataFrame:
        content = self.config.get("content")
        file_path = self.config.get("file_path", "")
        file_type = self.config.get("file_type", "csv")

        if content:
            if file_type == "xlsx":
                return pd.read_excel(io.BytesIO(content))
            return pd.read_csv(io.BytesIO(content) if isinstance(content, bytes) else io.StringIO(content))
        
        if file_path:
            if file_path.endswith(".xlsx"):
                return pd.read_excel(file_path)
            return pd.read_csv(file_path)
        
        raise ValueError("No file content or path provided")


# ──────────────────────────────────────────────
# Database Connector
# ──────────────────────────────────────────────

class DatabaseConnector(BaseConnector):
    """Ingest from SQL databases (PostgreSQL, MySQL, SQLite)."""

    connector_type = "database"

    def test_connection(self) -> Dict[str, Any]:
        try:
            from sqlalchemy import create_engine, text  # type: ignore
            conn_str = self.config.get("connection_string", "")
            eng = create_engine(conn_str)
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "ok", "message": "Connected successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def extract(self) -> pd.DataFrame:
        from sqlalchemy import create_engine  # type: ignore
        conn_str = self.config.get("connection_string", "")
        query = self.config.get("query", "")
        table = self.config.get("table", "")
        
        eng = create_engine(conn_str)
        if query:
            return pd.read_sql(query, eng)
        elif table:
            return pd.read_sql_table(table, eng)
        raise ValueError("No query or table specified")


# ──────────────────────────────────────────────
# S3 / Cloud Storage Connector
# ──────────────────────────────────────────────

class S3Connector(BaseConnector):
    """Ingest from AWS S3, MinIO, or Azure Blob Storage."""

    connector_type = "s3"

    def test_connection(self) -> Dict[str, Any]:
        try:
            import boto3  # type: ignore
            s3 = boto3.client("s3",
                endpoint_url=self.config.get("endpoint_url"),
                aws_access_key_id=self.config.get("access_key"),
                aws_secret_access_key=self.config.get("secret_key"),
            )
            bucket = self.config.get("bucket", "")
            s3.head_bucket(Bucket=bucket)
            return {"status": "ok", "message": f"Bucket '{bucket}' accessible"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def extract(self) -> pd.DataFrame:
        import boto3  # type: ignore
        s3 = boto3.client("s3",
            endpoint_url=self.config.get("endpoint_url"),
            aws_access_key_id=self.config.get("access_key"),
            aws_secret_access_key=self.config.get("secret_key"),
        )
        bucket = self.config.get("bucket", "")
        key = self.config.get("key", "")
        
        obj = s3.get_object(Bucket=bucket, Key=key)
        content = obj["Body"].read()
        
        if key.endswith(".csv"):
            return pd.read_csv(io.BytesIO(content))
        elif key.endswith(".json"):
            return pd.read_json(io.BytesIO(content))
        elif key.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(content))
        elif key.endswith(".parquet"):
            return pd.read_parquet(io.BytesIO(content))
        raise ValueError(f"Unsupported file type: {key}")


# ──────────────────────────────────────────────
# REST API Connector
# ──────────────────────────────────────────────

class APIConnector(BaseConnector):
    """Ingest from REST APIs and webhooks."""

    connector_type = "api"

    def test_connection(self) -> Dict[str, Any]:
        try:
            import urllib.request
            url = self.config.get("url", "")
            req = urllib.request.Request(url, method="HEAD")
            for k, v in self.config.get("headers", {}).items():
                req.add_header(k, v)
            urllib.request.urlopen(req, timeout=10)
            return {"status": "ok", "message": f"API reachable: {url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def extract(self) -> pd.DataFrame:
        import urllib.request
        url = self.config.get("url", "")
        headers = self.config.get("headers", {})
        data_path = self.config.get("data_path", "")  # JSONPath-like: "results.data"

        req = urllib.request.Request(url)
        for k, v in headers.items():
            req.add_header(k, v)
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        # Navigate to nested data
        if data_path:
            for key in data_path.split("."):
                if isinstance(data, dict):
                    data = data.get(key, data)
                elif isinstance(data, list) and key.isdigit():
                    data = data[int(key)]

        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        raise ValueError("API response is not tabular")


# ──────────────────────────────────────────────
# Connector Registry
# ──────────────────────────────────────────────

CONNECTOR_REGISTRY: Dict[str, type] = {
    "csv": CSVConnector,
    "database": DatabaseConnector,
    "s3": S3Connector,
    "api": APIConnector,
}


def get_connector(connector_type: str, config: Dict[str, Any]) -> BaseConnector:
    """Factory method to get a connector by type."""
    cls = CONNECTOR_REGISTRY.get(connector_type)
    if not cls:
        raise ValueError(f"Unknown connector type: {connector_type}. Available: {list(CONNECTOR_REGISTRY.keys())}")
    return cls(config)
