"""
NEXUS — Advanced Analytics Router
==================================
Advanced analytics endpoints for trend analysis, forecasting, what-if scenarios.

Endpoints:
  GET  /api/analytics/trends               — Get trend analysis for key metrics
  GET  /api/analytics/forecast             — Get demand/supply forecasts
  POST /api/analytics/what-if              — Run what-if scenarios
  GET  /api/analytics/comparative          — Get comparative analysis
  GET  /api/analytics/performance          — Get performance metrics
"""

import logging
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Body  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy import func, and_, or_  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.models import SupplyData  # type: ignore
from app.core.errors import (  # type: ignore
    NotFoundError,
    ValidationError,
    EngineUnavailableError,
    NoDataError,
)
from app.core.orchestrator import get_analysis_result  # type: ignore

logger = logging.getLogger("nexus.advanced_analytics")

router = APIRouter(prefix="/api/analytics", tags=["Advanced Analytics"])


# ── Pydantic Models ────────────────────────────────────────────────────────────

class TrendPeriod(str, Enum):
    """Trend analysis period options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class WhatIfScenario(BaseModel):
    """Model for what-if scenario parameters."""
    scenario_name: str = Field(..., max_length=200)
    delay_increase_pct: Optional[float] = Field(None, ge=-100, le=500)
    cost_increase_pct: Optional[float] = Field(None, ge=-100, le=500)
    supplier_disruption: Optional[str] = Field(None, max_length=500)
    region_impact: Optional[str] = Field(None, max_length=200)
    duration_days: Optional[int] = Field(None, ge=1, le=365)


class ComparativeRequest(BaseModel):
    """Model for comparative analysis."""
    metric: str = Field(..., description="Metric to compare: delay, cost, volume")
    group_by: str = Field(..., description="Group by: supplier, region, category")
    time_range: str = Field("30d", description="Time range: 7d, 30d, 90d, 1y")


# ── Trend Analysis Endpoints ───────────────────────────────────────────────────

@router.get("/trends")
def get_trend_analysis(
    metric: str = Query("delay_days", description="Metric to analyze: delay_days, cost, quantity"),
    period: TrendPeriod = TrendPeriod.WEEKLY,
    days: int = Query(90, ge=7, le=365, description="Time period in days"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Get trend analysis for key metrics over time.
    
    Supports analysis of delay_days, cost, and quantity across different time periods.
    """
    # Validate metric
    valid_metrics = ["delay_days", "cost", "quantity"]
    if metric not in valid_metrics:
        raise ValidationError(f"Invalid metric. Must be one of: {valid_metrics}")
    
    # Check if we have data
    total_records = db.query(func.count(SupplyData.id)).scalar()
    if total_records == 0:
        raise NoDataError("No data available for trend analysis")
    
    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get trend data based on period
        if period == TrendPeriod.DAILY:
            # Group by day
            date_format = func.date(SupplyData.order_date)
        elif period == TrendPeriod.WEEKLY:
            # Group by week
            date_format = func.date_trunc('week', SupplyData.order_date)
        elif period == TrendPeriod.MONTHLY:
            # Group by month
            date_format = func.date_trunc('month', SupplyData.order_date)
        else:  # QUARTERLY
            # Group by quarter
            date_format = func.date_trunc('quarter', SupplyData.order_date)
        
        # Build query based on metric
        if metric == "delay_days":
            query = db.query(
                date_format.label('period'),
                func.avg(SupplyData.delay_days).label('avg_value'),
                func.max(SupplyData.delay_days).label('max_value'),
                func.min(SupplyData.delay_days).label('min_value'),
                func.count(SupplyData.id).label('count')
            ).filter(
                SupplyData.order_date >= start_date,
                SupplyData.order_date <= end_date
            ).group_by(date_format).order_by(date_format)
        elif metric == "cost":
            query = db.query(
                date_format.label('period'),
                func.sum(SupplyData.cost).label('avg_value'),
                func.max(SupplyData.cost).label('max_value'),
                func.min(SupplyData.cost).label('min_value'),
                func.count(SupplyData.id).label('count')
            ).filter(
                SupplyData.order_date >= start_date,
                SupplyData.order_date <= end_date
            ).group_by(date_format).order_by(date_format)
        else:  # quantity
            query = db.query(
                date_format.label('period'),
                func.sum(SupplyData.quantity).label('avg_value'),
                func.max(SupplyData.quantity).label('max_value'),
                func.min(SupplyData.quantity).label('min_value'),
                func.count(SupplyData.id).label('count')
            ).filter(
                SupplyData.order_date >= start_date,
                SupplyData.order_date <= end_date
            ).group_by(date_format).order_by(date_format)
        
        results = query.all()
        
        # Format results
        trend_data = []
        for row in results:
            trend_data.append({
                "period": row.period.isoformat() if row.period else None,
                "avg_value": float(row.avg_value) if row.avg_value else 0,
                "max_value": float(row.max_value) if row.max_value else 0,
                "min_value": float(row.min_value) if row.min_value else 0,
                "count": row.count,
            })
        
        # Calculate trend direction
        if len(trend_data) >= 2:
            recent_avg = trend_data[-1]['avg_value']
            previous_avg = trend_data[-2]['avg_value']
            trend_direction = "increasing" if recent_avg > previous_avg else "decreasing"
            trend_change_pct = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg != 0 else 0
        else:
            trend_direction = "insufficient_data"
            trend_change_pct = 0
        
        return {
            "metric": metric,
            "period": period,
            "days": days,
            "trend_direction": trend_direction,
            "trend_change_pct": round(trend_change_pct, 2),
            "data": trend_data,
            "data_points": len(trend_data),
        }
    except Exception as e:
        logger.error("[NEXUS] Trend analysis failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")


@router.get("/forecast")
def get_forecast(
    forecast_type: str = Query("demand", description="Type: demand, supply, delay"),
    horizon_days: int = Query(30, ge=1, le=365, description="Forecast horizon in days"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Get demand/supply forecasts using ML engines.
    
    Uses the ML analyzer to generate forecasts for demand, supply, or delays.
    """
    # Validate forecast type
    valid_types = ["demand", "supply", "delay"]
    if forecast_type not in valid_types:
        raise ValidationError(f"Invalid forecast type. Must be one of: {valid_types}")
    
    # Check if ML analysis is available
    ml_res = get_analysis_result(db, "ml")
    if not ml_res:
        raise NoDataError("No ML analysis available. Upload data and run analysis first.")
    
    try:
        # Check if forecaster engine is available
        from app.main import engines  # type: ignore
        forecaster = engines.ml_analyzer  # Use ML analyzer for forecasting
        
        if not forecaster:
            raise EngineUnavailableError("Forecasting engine not available")
        
        # Load dataframe for forecasting
        from app.core.orchestrator import _load_dataframe  # type: ignore
        df = _load_dataframe()
        
        if df.empty:
            raise NoDataError("No data available for forecasting")
        
        # Generate forecast based on type
        forecast_data = {}
        if forecast_type == "demand":
            # Forecast demand based on historical quantity
            forecast_data = {
                "type": "demand_forecast",
                "horizon_days": horizon_days,
                "method": "moving_average",
                "forecast": _generate_simple_forecast(df, "quantity", horizon_days),
                "confidence": "medium",
            }
        elif forecast_type == "supply":
            # Forecast supply based on historical shipment data
            forecast_data = {
                "type": "supply_forecast",
                "horizon_days": horizon_days,
                "method": "moving_average",
                "forecast": _generate_simple_forecast(df, "quantity", horizon_days),
                "confidence": "medium",
            }
        else:  # delay
            # Forecast delays based on historical delay_days
            forecast_data = {
                "type": "delay_forecast",
                "horizon_days": horizon_days,
                "method": "moving_average",
                "forecast": _generate_simple_forecast(df, "delay_days", horizon_days),
                "confidence": "medium",
            }
        
        return forecast_data
    except (EngineUnavailableError, NoDataError):
        raise
    except Exception as e:
        logger.error("[NEXUS] Forecast generation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


def _generate_simple_forecast(df, column, horizon_days):
    """Generate a simple moving average forecast."""
    import pandas as pd  # type: ignore
    
    if column not in df.columns:
        return {"error": f"Column {column} not found in data"}
    
    # Get recent values
    recent_values = df[column].tail(30).dropna()
    
    if len(recent_values) == 0:
        return {"error": "No valid data for forecasting"}
    
    # Calculate moving average
    avg_value = recent_values.mean()
    std_value = recent_values.std()
    
    # Generate forecast with confidence intervals
    forecast = []
    for day in range(horizon_days):
        forecast_date = datetime.now(timezone.utc) + timedelta(days=day + 1)
        forecast.append({
            "date": forecast_date.isoformat(),
            "predicted_value": float(avg_value),
            "lower_bound": float(avg_value - 1.96 * std_value),
            "upper_bound": float(avg_value + 1.96 * std_value),
        })
    
    return {
        "method": "moving_average",
        "base_avg": float(avg_value),
        "base_std": float(std_value),
        "values": forecast,
    }


@router.post("/what-if")
def run_what_if_scenario(
    scenario: WhatIfScenario,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Run what-if scenarios to simulate the impact of disruptions.
    
    Allows testing the impact of supplier disruptions, cost increases, etc.
    """
    # Check if we have data
    total_records = db.query(func.count(SupplyData.id)).scalar()
    if total_records == 0:
        raise NoDataError("No data available for what-if analysis")
    
    try:
        # Get baseline metrics
        baseline = db.query(
            func.avg(SupplyData.delay_days).label('avg_delay'),
            func.sum(SupplyData.cost).label('total_cost'),
            func.count(SupplyData.id).label('total_records')
        ).first()
        
        # Build query for scenario simulation
        query = db.query(SupplyData)
        
        # Apply scenario filters
        if scenario.supplier_disruption:
            query = query.filter(SupplyData.supplier.ilike(f"%{scenario.supplier_disruption}%"))
        if scenario.region_impact:
            query = query.filter(SupplyData.region.ilike(f"%{scenario.region_impact}%"))
        
        affected_records = query.count()
        
        # Calculate impact
        impacted_data = query.all()
        
        total_impact_cost = 0
        total_impact_delay = 0
        
        for record in impacted_data:
            # Apply cost increase
            if scenario.cost_increase_pct:
                impact_cost = record.cost * (scenario.cost_increase_pct / 100)
                total_impact_cost += impact_cost
            
            # Apply delay increase
            if scenario.delay_increase_pct:
                impact_delay = record.delay_days * (scenario.delay_increase_pct / 100)
                total_impact_delay += impact_delay
        
        # Calculate affected percentage
        affected_pct = (affected_records / total_records * 100) if total_records > 0 else 0
        
        return {
            "scenario_name": scenario.scenario_name,
            "baseline": {
                "avg_delay": float(baseline.avg_delay) if baseline.avg_delay else 0,
                "total_cost": float(baseline.total_cost) if baseline.total_cost else 0,
                "total_records": baseline.total_records,
            },
            "impact": {
                "affected_records": affected_records,
                "affected_percentage": round(affected_pct, 2),
                "additional_cost": round(total_impact_cost, 2),
                "additional_delay_days": round(total_impact_delay, 2),
                "new_avg_delay": round(float(baseline.avg_delay) + (total_impact_delay / total_records), 2) if total_records > 0 else 0,
                "new_total_cost": round(float(baseline.total_cost) + total_impact_cost, 2),
            },
            "parameters": {
                "delay_increase_pct": scenario.delay_increase_pct,
                "cost_increase_pct": scenario.cost_increase_pct,
                "supplier_disruption": scenario.supplier_disruption,
                "region_impact": scenario.region_impact,
                "duration_days": scenario.duration_days,
            },
        }
    except Exception as e:
        logger.error("[NEXUS] What-if scenario failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"What-if scenario failed: {str(e)}")


@router.get("/comparative")
def get_comparative_analysis(
    request: ComparativeRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Get comparative analysis across different dimensions.
    
    Compare metrics across suppliers, regions, or categories.
    """
    # Validate metric
    valid_metrics = ["delay", "cost", "volume"]
    if request.metric not in valid_metrics:
        raise ValidationError(f"Invalid metric. Must be one of: {valid_metrics}")
    
    # Validate group_by
    valid_groups = ["supplier", "region", "category"]
    if request.group_by not in valid_groups:
        raise ValidationError(f"Invalid group_by. Must be one of: {valid_groups}")
    
    # Check if we have data
    total_records = db.query(func.count(SupplyData.id)).scalar()
    if total_records == 0:
        raise NoDataError("No data available for comparative analysis")
    
    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        if request.time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif request.time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif request.time_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # Build query based on group_by and metric
        group_column = getattr(SupplyData, request.group_by)
        
        if request.metric == "delay":
            query = db.query(
                group_column.label('group'),
                func.avg(SupplyData.delay_days).label('avg_value'),
                func.max(SupplyData.delay_days).label('max_value'),
                func.min(SupplyData.delay_days).label('min_value'),
                func.count(SupplyData.id).label('count')
            ).filter(
                SupplyData.order_date >= start_date,
                SupplyData.order_date <= end_date
            ).group_by(group_column).order_by(func.avg(SupplyData.delay_days).desc())
        elif request.metric == "cost":
            query = db.query(
                group_column.label('group'),
                func.sum(SupplyData.cost).label('avg_value'),
                func.max(SupplyData.cost).label('max_value'),
                func.min(SupplyData.cost).label('min_value'),
                func.count(SupplyData.id).label('count')
            ).filter(
                SupplyData.order_date >= start_date,
                SupplyData.order_date <= end_date
            ).group_by(group_column).order_by(func.sum(SupplyData.cost).desc())
        else:  # volume
            query = db.query(
                group_column.label('group'),
                func.sum(SupplyData.quantity).label('avg_value'),
                func.max(SupplyData.quantity).label('max_value'),
                func.min(SupplyData.quantity).label('min_value'),
                func.count(SupplyData.id).label('count')
            ).filter(
                SupplyData.order_date >= start_date,
                SupplyData.order_date <= end_date
            ).group_by(group_column).order_by(func.sum(SupplyData.quantity).desc())
        
        results = query.all()
        
        # Format results
        comparison_data = []
        for row in results:
            comparison_data.append({
                "group": str(row.group) if row.group else "Unknown",
                "avg_value": float(row.avg_value) if row.avg_value else 0,
                "max_value": float(row.max_value) if row.max_value else 0,
                "min_value": float(row.min_value) if row.min_value else 0,
                "count": row.count,
            })
        
        # Calculate top performer
        if comparison_data:
            if request.metric == "delay":
                top_performer = min(comparison_data, key=lambda x: x['avg_value'])
            else:
                top_performer = max(comparison_data, key=lambda x: x['avg_value'])
        else:
            top_performer = None
        
        return {
            "metric": request.metric,
            "group_by": request.group_by,
            "time_range": request.time_range,
            "top_performer": top_performer,
            "data": comparison_data,
            "total_groups": len(comparison_data),
        }
    except Exception as e:
        logger.error("[NEXUS] Comparative analysis failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparative analysis failed: {str(e)}")


@router.get("/performance")
def get_performance_metrics(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Get comprehensive performance metrics.
    
    Returns key performance indicators across multiple dimensions.
    """
    # Check if we have data
    total_records = db.query(func.count(SupplyData.id)).scalar()
    if total_records == 0:
        raise NoDataError("No data available for performance metrics")
    
    try:
        # Get overall metrics
        overall = db.query(
            func.count(SupplyData.id).label('total_records'),
            func.avg(SupplyData.delay_days).label('avg_delay'),
            func.max(SupplyData.delay_days).label('max_delay'),
            func.sum(SupplyData.cost).label('total_cost'),
            func.avg(SupplyData.quality_score).label('avg_quality'),
        ).first()
        
        # Get supplier performance
        supplier_perf = db.query(
            SupplyData.supplier,
            func.count(SupplyData.id).label('count'),
            func.avg(SupplyData.delay_days).label('avg_delay'),
            func.avg(SupplyData.quality_score).label('avg_quality'),
        ).group_by(SupplyData.supplier).order_by(func.avg(SupplyData.delay_days).asc()).limit(10).all()
        
        # Get regional performance
        regional_perf = db.query(
            SupplyData.region,
            func.count(SupplyData.id).label('count'),
            func.avg(SupplyData.delay_days).label('avg_delay'),
            func.sum(SupplyData.cost).label('total_cost'),
        ).group_by(SupplyData.region).order_by(func.avg(SupplyData.delay_days).asc()).limit(10).all()
        
        return {
            "overall": {
                "total_records": overall.total_records,
                "avg_delay_days": round(float(overall.avg_delay), 2) if overall.avg_delay else 0,
                "max_delay_days": overall.max_delay,
                "total_cost": round(float(overall.total_cost), 2) if overall.total_cost else 0,
                "avg_quality_score": round(float(overall.avg_quality), 2) if overall.avg_quality else 0,
            },
            "top_suppliers": [
                {
                    "supplier": str(s.supplier) if s.supplier else "Unknown",
                    "count": s.count,
                    "avg_delay": round(float(s.avg_delay), 2) if s.avg_delay else 0,
                    "avg_quality": round(float(s.avg_quality), 2) if s.avg_quality else 0,
                }
                for s in supplier_perf
            ],
            "top_regions": [
                {
                    "region": str(r.region) if r.region else "Unknown",
                    "count": r.count,
                    "avg_delay": round(float(r.avg_delay), 2) if r.avg_delay else 0,
                    "total_cost": round(float(r.total_cost), 2) if r.total_cost else 0,
                }
                for r in regional_perf
            ],
        }
    except Exception as e:
        logger.error("[NEXUS] Performance metrics failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")
