"""
NEXUS — Monitoring Router
==========================
System monitoring and metrics endpoints.

Endpoints:
  GET /api/monitoring/metrics          — Get system error metrics
  GET /api/monitoring/summary         — Get error summary for time period
  GET /api/monitoring/recent-errors   — Get recent errors with filtering
  GET /api/monitoring/health          — Get detailed system health
  GET /api/monitoring/status          — Get system status overview
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.utils.error_monitoring import (  # type: ignore
    error_monitor,
    get_error_metrics,
    get_error_summary,
    get_recent_errors,
)
from app.core.errors import NotFoundError  # type: ignore

logger = logging.getLogger("nexus.monitoring")

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/metrics")
def get_system_metrics(
    user: dict = Depends(require_auth),
):
    """
    Get current system error metrics.
    
    Returns aggregated error statistics including error rates, 
    error types, and recent error counts.
    """
    try:
        metrics = get_error_metrics()
        return {
            "status": "success",
            "timestamp": error_monitor.metrics.last_error_time.isoformat() if error_monitor.metrics.last_error_time else None,
            "metrics": metrics,
        }
    except Exception as e:
        logger.error("[NEXUS] Failed to get error metrics: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": "Failed to retrieve error metrics",
            "error": str(e),
        }


@router.get("/summary")
def get_error_summary_endpoint(
    minutes: int = Query(60, ge=1, le=1440, description="Time period in minutes (max 24 hours)"),
    user: dict = Depends(require_auth),
):
    """
    Get error summary for a specified time period.
    
    Provides aggregated error statistics for the specified time window,
    including top error types, codes, and endpoints.
    """
    try:
        summary = get_error_summary(minutes)
        return {
            "status": "success",
            "summary": summary,
        }
    except Exception as e:
        logger.error("[NEXUS] Failed to get error summary: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": "Failed to retrieve error summary",
            "error": str(e),
        }


@router.get("/recent-errors")
def get_recent_errors_endpoint(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of errors to return"),
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    error_type: Optional[str] = Query(None, description="Filter by error type"),
    user: dict = Depends(require_auth),
):
    """
    Get recent errors with optional filtering.
    
    Returns detailed error records with stack traces and metadata.
    """
    try:
        errors_data = get_recent_errors(limit, severity, error_type)
        return {
            "status": "success",
            "data": errors_data,
        }
    except Exception as e:
        logger.error("[NEXUS] Failed to get recent errors: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": "Failed to retrieve recent errors",
            "error": str(e),
        }


@router.get("/health")
def get_detailed_health(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Get detailed system health information.
    
    Includes database status, error metrics, and system overview.
    """
    try:
        # Database health check
        from sqlalchemy import text  # type: ignore
        import time
        
        db_start = time.time()
        db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - db_start) * 1000, 2)
        
        # Get error metrics
        error_metrics = get_error_metrics()
        
        # Check engine status
        from app.main import engines  # type: ignore
        engine_status = {
            "ml_analyzer": engines.ml_analyzer is not None,
            "graph_engine": engines.graph_engine is not None,
            "ai_copilot": engines.ai_copilot is not None,
            "xai_engine": engines.xai_engine is not None,
            "causal_engine": engines.causal_engine is not None,
            "quality_engine": engines.quality_engine is not None,
            "monte_carlo_engine": engines.monte_carlo_engine is not None,
            "kpi_engine": engines.kpi_engine_instance is not None,
            "tgnn_engine": engines.tgnn_engine_instance is not None,
            "sop_engine": engines.sop_engine is not None,
            "response_planning_engine": engines.response_planning_engine is not None,
        }
        
        # Calculate overall health
        healthy_engines = sum(1 for status in engine_status.values() if status)
        total_engines = len(engine_status)
        engine_health_pct = (healthy_engines / total_engines * 100) if total_engines > 0 else 0
        
        # Determine overall status
        if db_latency_ms > 1000 or error_metrics["total_errors"] > 1000:
            overall_status = "degraded"
        elif engine_health_pct < 80:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": "success",
            "health": {
                "overall": overall_status,
                "database": {
                    "status": "connected",
                    "latency_ms": db_latency_ms,
                },
                "engines": {
                    "total": total_engines,
                    "healthy": healthy_engines,
                    "health_percentage": round(engine_health_pct, 2),
                    "details": engine_status,
                },
                "errors": error_metrics,
            },
        }
    except Exception as e:
        logger.error("[NEXUS] Failed to get health status: %s", e, exc_info=True)
        return {
            "status": "error",
            "health": {
                "overall": "unhealthy",
                "error": str(e),
            }
        }


@router.get("/status")
def get_system_status(
    user: dict = Depends(require_auth),
):
    """
    Get system status overview.
    
    Quick status check for monitoring dashboards.
    """
    try:
        error_metrics = get_error_metrics()
        
        # Determine if system is experiencing issues
        error_rate = error_metrics.get("error_rate_per_minute", 0)
        total_errors = error_metrics.get("total_errors", 0)
        
        if error_rate > 10 or total_errors > 500:
            status = "warning"
        elif error_rate > 5 or total_errors > 200:
            status = "degraded"
        else:
            status = "operational"
        
        return {
            "status": "success",
            "system_status": status,
            "error_rate_per_minute": error_rate,
            "total_errors": total_errors,
            "last_error_time": error_metrics.get("last_error_time"),
        }
    except Exception as e:
        logger.error("[NEXUS] Failed to get system status: %s", e, exc_info=True)
        return {
            "status": "error",
            "system_status": "unknown",
            "error": str(e),
        }