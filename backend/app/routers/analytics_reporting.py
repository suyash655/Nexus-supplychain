"""
NEXUS - Advanced Analytics and Reporting Router
===============================================
Self-service analytics, report generation, scheduling, subscriptions, and
visualization configuration endpoints.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_auth
from app.core.orchestrator import _load_dataframe
from app.engines.analytics_engine import AnalyticsEngine

logger = logging.getLogger("nexus.analytics_reporting")

router = APIRouter(prefix="/analytics-reporting", tags=["Analytics Reporting"])

analytics_engine = AnalyticsEngine()


class TrendRequest(BaseModel):
    date_column: str = Field("order_date", max_length=100)
    value_columns: List[str] = Field(default_factory=lambda: ["delay_days", "cost", "quantity"])
    window_size: int = Field(7, ge=2, le=90)


class CorrelationRequest(BaseModel):
    method: str = Field("pearson", pattern="^(pearson|spearman|kendall)$")
    threshold: float = Field(0.5, ge=0, le=1)


class OutlierRequest(BaseModel):
    columns: List[str] = Field(default_factory=lambda: ["delay_days", "cost", "quantity"])
    method: str = Field("isolation_forest", pattern="^(isolation_forest|zscore|iqr)$")
    contamination: float = Field(0.1, gt=0, le=0.5)


class ReportSection(BaseModel):
    type: str
    title: Optional[str] = None
    kpis: List[Dict[str, Any]] = Field(default_factory=list)
    date_column: Optional[str] = None
    value_columns: List[str] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    method: Optional[str] = None
    threshold: Optional[float] = None


class ReportCreateRequest(BaseModel):
    title: str = Field("Supply Chain Analytics Report", max_length=200)
    description: str = Field("", max_length=1000)
    format: str = Field("html", pattern="^(html|pdf|excel|csv)$")
    sections: List[ReportSection] = Field(default_factory=list)


class ScheduleRequest(BaseModel):
    report_config: Dict[str, Any] = Field(default_factory=dict)
    schedule: str = Field("weekly", pattern="^(hourly|daily|weekly|monthly)$")


class SubscriptionRequest(BaseModel):
    email: str = Field(max_length=255)
    name: Optional[str] = Field(None, max_length=120)
    format: str = Field("pdf", pattern="^(html|pdf|excel|csv)$")
    delivery_method: str = Field("email", pattern="^(email|webhook|s3)$")
    delivery_config: Dict[str, Any] = Field(default_factory=dict)


def _ensure_engine() -> None:
    if not analytics_engine._initialised:
        analytics_engine.initialize()


def _dataframe_or_400():
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=400, detail="No data available. Upload data first.")
    return df


@router.post("/initialize")
def initialize_analytics_reporting(
    config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        return analytics_engine.initialize(config)
    except Exception as exc:
        logger.error("Error initializing analytics reporting: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/templates")
def get_report_templates(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    _ensure_engine()
    return {
        "status": "success",
        "templates": analytics_engine.report_templates,
        "total_count": len(analytics_engine.report_templates),
    }


@router.post("/trend-analysis")
def run_trend_analysis(
    request: TrendRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        df = _dataframe_or_400()
        return analytics_engine.trend_analysis(
            df,
            date_column=request.date_column,
            value_columns=request.value_columns,
            window_size=request.window_size,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error running trend analysis: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/correlation-analysis")
def run_correlation_analysis(
    request: CorrelationRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        return analytics_engine.correlation_analysis(
            _dataframe_or_400(),
            method=request.method,
            threshold=request.threshold,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error running correlation analysis: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/outlier-detection")
def run_outlier_detection(
    request: OutlierRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        return analytics_engine.outlier_detection(
            _dataframe_or_400(),
            columns=request.columns,
            method=request.method,
            contamination=request.contamination,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error running outlier detection: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reports")
def create_report(
    request: ReportCreateRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        sections = [section.model_dump(exclude_none=True) for section in request.sections]
        if not sections:
            sections = [
                {
                    "type": "kpi_overview",
                    "title": "KPI Overview",
                    "kpis": [
                        {"name": "Total Cost", "column": "cost", "aggregation": "sum", "format": "currency"},
                        {"name": "Average Delay", "column": "delay_days", "aggregation": "mean", "unit": "days"},
                        {"name": "Total Quantity", "column": "quantity", "aggregation": "sum"},
                    ],
                },
                {"type": "correlation_analysis", "title": "Correlation Analysis", "method": "pearson", "threshold": 0.5},
            ]

        return analytics_engine.create_report(
            {
                "title": request.title,
                "description": request.description,
                "format": request.format,
                "sections": sections,
            },
            _dataframe_or_400(),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error creating report: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reports/schedule")
def schedule_report(
    request: ScheduleRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        return analytics_engine.schedule_report(request.report_config, request.schedule)
    except Exception as exc:
        logger.error("Error scheduling report: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reports/{report_id}/subscriptions")
def subscribe_to_report(
    report_id: str,
    request: SubscriptionRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        return analytics_engine.subscribe_to_report(
            report_id,
            {
                "email": request.email,
                "name": request.name,
                "format": request.format,
                "delivery_method": request.delivery_method,
                "delivery_config": request.delivery_config,
            },
        )
    except Exception as exc:
        logger.error("Error subscribing to report: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/visualizations/{chart_type}")
def get_visualization_config(
    chart_type: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        return analytics_engine.get_visualization_config(chart_type, _dataframe_or_400())
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error generating visualization config: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/dashboard")
def get_reporting_dashboard(
    threshold: float = Query(0.5, ge=0, le=1),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        _ensure_engine()
        df = _dataframe_or_400()
        numeric_columns = list(df.select_dtypes(include="number").columns)
        date_column = "order_date" if "order_date" in df.columns else None
        trend = (
            analytics_engine.trend_analysis(df, date_column, numeric_columns[:4])
            if date_column and numeric_columns
            else {"status": "skipped", "reason": "No date column or numeric columns available"}
        )
        correlation = analytics_engine.correlation_analysis(df, threshold=threshold)
        viz = analytics_engine.get_visualization_config("heatmap", df)
        return {
            "status": "success",
            "summary": {
                "rows": len(df),
                "columns": len(df.columns),
                "numeric_columns": numeric_columns,
                "templates": len(analytics_engine.report_templates),
                "scheduled_reports": len(analytics_engine.scheduled_reports),
                "subscriptions": sum(len(v) for v in analytics_engine.report_subscriptions.values()),
            },
            "trend_analysis": trend,
            "correlation_analysis": correlation,
            "visualization": viz,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error loading reporting dashboard: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
