"""
NEXUS — Centralized Configuration
==================================
All settings via environment variables with Pydantic validation.
"""

import os
from pathlib import Path
from typing import Optional
from datetime import timedelta

# Project root: backend/app/core/config.py → .parents[3] = project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_DEFAULT_SECRET = "nexus-dev-secret-change-in-production"


class Settings:
    """Application settings loaded from environment variables."""

    # ── App ──
    APP_NAME: str = "NEXUS"
    APP_VERSION: str = "3.0.0"
    APP_DESCRIPTION: str = "Autonomous Data Intelligence Platform for Supply Chain"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ── Database ──
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{_PROJECT_ROOT / 'data' / 'synchain.db'}"
    )

    # ── Redis (for caching, pub/sub, pipeline queues) ──
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ── Auth / JWT ──
    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_SECRET)
    JWT_ALGORITHM: str = "HS256"
    # Short-lived access tokens (60 min). Override via ACCESS_TOKEN_EXPIRE_MINUTES env var.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    # Long-lived refresh tokens (30 days). Override via REFRESH_TOKEN_EXPIRE_DAYS env var.
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # ── LLM Provider ──
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")  # groq, bedrock, offline
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── AWS / Bedrock ──
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

    # ── Demo Mode ──
    ALLOW_DEMO: bool = os.getenv("ALLOW_DEMO", "true").lower() == "true"

    # ── Storage (S3-compatible) ──
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    S3_ENDPOINT: Optional[str] = os.getenv("S3_ENDPOINT")  # MinIO compat

    # ── CORS ──
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    # ── Pipeline ──
    MAX_PIPELINE_WORKERS: int = int(os.getenv("MAX_PIPELINE_WORKERS", "4"))
    DATA_QUALITY_THRESHOLD: float = float(os.getenv("DATA_QUALITY_THRESHOLD", "0.85"))

    # ── Upload limits ──
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(500 * 1024 * 1024)))  # 500 MB default

    # ── Connector Types ──
    CONNECTOR_TYPES = [
        {"id": "csv", "name": "CSV / Excel", "icon": "file-spreadsheet", "description": "Upload or connect to CSV/Excel files"},
        {"id": "database", "name": "SQL Database", "icon": "database", "description": "PostgreSQL, MySQL, SQLite, etc."},
        {"id": "s3", "name": "Cloud Storage", "icon": "cloud", "description": "AWS S3, Azure Blob, MinIO"},
        {"id": "api", "name": "REST API", "icon": "globe", "description": "Connect to any REST endpoint or webhook"},
    ]

    def validate(self) -> None:
        """
        Crash loudly on startup if security-critical settings are misconfigured
        in a non-debug (production) environment.
        """
        if not self.DEBUG and self.SECRET_KEY == _DEFAULT_SECRET:
            raise RuntimeError(
                "[NEXUS] FATAL: SECRET_KEY is set to the default development value. "
                "Set a strong SECRET_KEY environment variable before running in production. "
                "Set DEBUG=true to suppress this check in local development."
            )

    @property
    def access_token_lifetime(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_lifetime(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
