"""
NEXUS — Data Pipeline & Quality Framework
============================================
DAG-based pipeline orchestration with built-in data quality checks and lineage.
"""

import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable

import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Text, Boolean  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.models import Base  # type: ignore
from app.utils.supply_metrics import completeness_detail, completeness_score


def _utcnow():
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────
# Pipeline Models
# ──────────────────────────────────────────────

class PipelineRun(Base):
    """Track each pipeline execution for observability."""
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    status = Column(String, default="running")  # running, success, failed, partial
    source_connector = Column(String, nullable=True)
    rows_ingested = Column(Integer, default=0)
    rows_accepted = Column(Integer, default=0)
    rows_rejected = Column(Integer, default=0)
    quality_score = Column(Float, nullable=True)  # 0.0 - 1.0
    quality_report = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)


class MetricDefinition(Base):
    """Semantic layer: Centralized metric/KPI definitions."""
    __tablename__ = "metric_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # e.g., "avg_lead_time"
    display_name = Column(String)                     # e.g., "Average Lead Time"
    formula = Column(Text)                            # SQL or Python expression
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)          # risk, cost, performance, quality
    unit = Column(String, nullable=True)              # days, $, %, count
    owner = Column(String, nullable=True)             # team/person responsible
    refresh_cadence = Column(String, default="daily") # real-time, hourly, daily
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)




# ──────────────────────────────────────────────
# Data Quality Engine
# ──────────────────────────────────────────────

class DataQualityEngine:
    """Automated data quality checks — the difference between a toy and production."""

    @staticmethod
    def run_checks(df: pd.DataFrame, rules: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Run comprehensive data quality checks on a DataFrame."""
        report: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "checks": [],
            "overall_score": 0.0,
            "grade": "F",
        }

        scores: List[float] = []

        # 1. Completeness — % of non-null values
        completeness = completeness_score(df)
        scores.append(completeness)
        report["checks"].append({
            "name": "Completeness",
            "score": round(float(completeness), 4),
            "detail": completeness_detail(df),
            "status": "pass" if completeness > 0.9 else "warn" if completeness > 0.7 else "fail",
        })

        # 2. Uniqueness — % of unique rows (dedup check)
        if len(df) > 0:
            uniqueness = len(df.drop_duplicates()) / len(df)
        else:
            uniqueness = 1.0
        scores.append(uniqueness)
        report["checks"].append({
            "name": "Uniqueness",
            "score": round(float(uniqueness), 4),
            "duplicate_count": len(df) - len(df.drop_duplicates()),
            "status": "pass" if uniqueness > 0.95 else "warn" if uniqueness > 0.8 else "fail",
        })

        # 3. Consistency — type consistency within columns
        type_issues = 0
        for col in df.columns:
            if df[col].dtype == object:
                # Mixed types in string columns
                types_in_col = df[col].dropna().apply(type).nunique()
                if types_in_col > 1:
                    type_issues += 1

        consistency = 1.0 - (type_issues / max(len(df.columns), 1))
        scores.append(consistency)
        report["checks"].append({
            "name": "Consistency",
            "score": round(float(consistency), 4),
            "type_issues": type_issues,
            "status": "pass" if consistency > 0.95 else "warn" if consistency > 0.8 else "fail",
        })

        # 4. Freshness — check for date columns
        freshness = 1.0
        date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
        if date_cols and len(df) > 0:
            for col in date_cols:
                try:
                    dates = pd.to_datetime(df[col], errors="coerce")
                    max_date = dates.max()
                    if pd.notna(max_date):
                        days_old = (datetime.now(timezone.utc) - max_date.to_pydatetime().replace(tzinfo=timezone.utc)).days
                        freshness = max(0, 1.0 - (days_old / 365))
                        break
                except Exception:
                    pass
        scores.append(freshness)
        report["checks"].append({
            "name": "Freshness",
            "score": round(float(freshness), 4),
            "status": "pass" if freshness > 0.8 else "warn" if freshness > 0.5 else "fail",
        })

        # 5. Validity — numeric ranges, string lengths
        validity_issues = 0
        for col in df.select_dtypes(include=[np.number]).columns:
            # Check for negative values in typically positive columns
            if any(keyword in col.lower() for keyword in ["cost", "price", "quantity", "score"]):
                neg_count = (df[col] < 0).sum()
                if neg_count > 0:
                    validity_issues += int(neg_count)

        validity = 1.0 - min(1.0, validity_issues / max(len(df), 1))
        scores.append(validity)
        report["checks"].append({
            "name": "Validity",
            "score": round(float(validity), 4),
            "issues": validity_issues,
            "status": "pass" if validity > 0.95 else "warn" if validity > 0.8 else "fail",
        })

        # Overall score
        overall = sum(scores) / len(scores) if scores else 0
        report["overall_score"] = round(float(overall), 4)

        if overall >= 0.95:
            report["grade"] = "A"
        elif overall >= 0.85:
            report["grade"] = "B"
        elif overall >= 0.70:
            report["grade"] = "C"
        elif overall >= 0.50:
            report["grade"] = "D"
        else:
            report["grade"] = "F"

        return report


# ──────────────────────────────────────────────
# Pipeline Orchestrator
# ──────────────────────────────────────────────

class PipelineOrchestrator:
    """Orchestrates data pipelines: Extract → Quality Check → Transform → Load."""

    def __init__(self, db: Session):
        self.db = db
        self.quality_engine = DataQualityEngine()

    def run_pipeline(
        self,
        pipeline_name: str,
        df: pd.DataFrame,
        source_connector: str = "manual_upload",
        transforms: Optional[List[Callable]] = None,
    ) -> Dict[str, Any]:
        """Execute a full data pipeline with quality checks."""
        start = time.time()
        run = PipelineRun(
            pipeline_name=pipeline_name,
            source_connector=source_connector,
            rows_ingested=len(df),
            status="running",
        )
        self.db.add(run)
        self.db.commit()

        try:
            # Step 1: Quality check on raw data
            quality_report = self.quality_engine.run_checks(df)
            run.quality_score = quality_report["overall_score"]
            run.quality_report = quality_report

            # Step 2: Apply transforms (if any)
            if transforms:
                for transform_fn in transforms:
                    df = transform_fn(df)

            # Step 3: Record accepted/rejected
            run.rows_accepted = len(df)
            run.rows_rejected = run.rows_ingested - len(df)
            run.status = "success"
            run.duration_ms = int((time.time() - start) * 1000)

        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            run.duration_ms = int((time.time() - start) * 1000)

        self.db.commit()
        self.db.refresh(run)

        return {
            "pipeline_id": run.id,
            "status": run.status,
            "rows_ingested": run.rows_ingested,
            "rows_accepted": run.rows_accepted,
            "rows_rejected": run.rows_rejected,
            "quality_score": run.quality_score,
            "quality_grade": quality_report.get("grade", "?"),
            "duration_ms": run.duration_ms,
            "quality_report": quality_report,
            "dataframe": df,  # Pass processed df for loading
        }
