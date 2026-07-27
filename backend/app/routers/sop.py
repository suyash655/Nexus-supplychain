"""
NEXUS — SAP IBP-Style S&OP API Router
=====================================
REST API endpoints for Sales & Operations Planning,
consensus forecasting, and executive dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import pandas as pd

from app.core.dependencies import get_db, get_current_user
from app.engines.sop_engine import SOPEngine

router = APIRouter(prefix="/ibp/sop", tags=["Sales & Operations Planning"])

# Global S&OP engine instance
sop_engine = SOPEngine()


class ConsensusForecastRequest(BaseModel):
    """Request model for consensus forecasting."""
    functional_inputs: Dict[str, Dict[str, List[float]]]
    weights: Optional[Dict[str, float]] = None


class ForecastSubmissionRequest(BaseModel):
    """Request model for forecast submission."""
    forecast_id: str
    submitter: str
    comments: Optional[str] = ""


class ApprovalRequest(BaseModel):
    """Request model for forecast approval."""
    forecast_id: str
    approver: str
    level: str
    comments: Optional[str] = ""


class RejectionRequest(BaseModel):
    """Request model for forecast rejection."""
    forecast_id: str
    rejecter: str
    level: str
    reason: str


class ExecutiveDashboardRequest(BaseModel):
    """Request model for executive dashboard."""
    demand_forecasts: Dict[str, List[float]]
    supply_plan: Dict[str, Any]
    inventory_status: Dict[str, Any]
    financial_data: Optional[Dict[str, Any]] = None


class PerformanceManagementRequest(BaseModel):
    """Request model for performance management."""
    historical_forecasts: Dict[str, List[float]]
    actuals: Dict[str, List[float]]
    targets: Optional[Dict[str, float]] = None


class ScenarioComparisonRequest(BaseModel):
    """Request model for scenario comparison."""
    base_scenario: Dict[str, Any]
    comparison_scenarios: List[Dict[str, Any]]


@router.post("/initialize")
async def initialize_sop(
    config: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Initialize S&OP engine with configuration.
    """
    try:
        result = sop_engine.initialize(config)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consensus-forecast")
async def create_consensus_forecast(
    request: ConsensusForecastRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create consensus forecast by combining functional inputs.
    
    Combines forecasts from sales, marketing, finance, and operations
    into a single consensus forecast with variance analysis.
    """
    try:
        result = sop_engine.create_consensus_forecast(
            functional_inputs=request.functional_inputs,
            weights=request.weights
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/submit")
async def submit_forecast(
    request: ForecastSubmissionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit consensus forecast for approval workflow.
    """
    try:
        result = sop_engine.submit_forecast_for_approval(
            forecast_id=request.forecast_id,
            submitter=request.submitter,
            comments=request.comments
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/approve")
async def approve_forecast(
    request: ApprovalRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve forecast at specified level.
    """
    try:
        result = sop_engine.approve_forecast(
            forecast_id=request.forecast_id,
            approver=request.approver,
            level=request.level,
            comments=request.comments
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/reject")
async def reject_forecast(
    request: RejectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Reject forecast at specified level.
    """
    try:
        result = sop_engine.reject_forecast(
            forecast_id=request.forecast_id,
            rejecter=request.rejecter,
            level=request.level,
            reason=request.reason
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard")
async def generate_executive_dashboard(
    request: ExecutiveDashboardRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate executive dashboard with key metrics and insights.
    
    Provides comprehensive view of demand, supply, inventory, and
    financial metrics with actionable recommendations.
    """
    try:
        result = sop_engine.generate_executive_dashboard(
            demand_forecasts=request.demand_forecasts,
            supply_plan=request.supply_plan,
            inventory_status=request.inventory_status,
            financial_data=request.financial_data
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance")
async def performance_management(
    request: PerformanceManagementRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate performance metrics and track against targets.
    
    Evaluates forecast accuracy, inventory performance, customer
    service levels, and financial metrics.
    """
    try:
        result = sop_engine.performance_management(
            historical_forecasts=request.historical_forecasts,
            actuals=request.actuals,
            targets=request.targets
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasts/versions")
async def get_forecast_version_history(
    sku: Optional[str] = Query(None, description="Filter by SKU"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get version history of forecasts.
    """
    try:
        result = sop_engine.get_forecast_version_history(sku=sku)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/compare")
async def compare_scenarios(
    request: ScenarioComparisonRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Compare multiple planning scenarios side by side.
    
    Enables comparison of demand scenarios, supply scenarios,
    and financial scenarios for decision support.
    """
    try:
        result = sop_engine.scenario_comparison(
            base_scenario=request.base_scenario,
            comparison_scenarios=request.comparison_scenarios
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consensus/{forecast_id}")
async def get_consensus_forecast(
    forecast_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific consensus forecast details.
    """
    try:
        if forecast_id not in sop_engine.consensus_forecasts:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        forecast = sop_engine.consensus_forecasts[forecast_id]
        
        return {
            "status": "success",
            "forecast_id": forecast_id,
            "forecast": forecast
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{dashboard_id}")
async def get_executive_dashboard(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific executive dashboard snapshot.
    """
    try:
        if dashboard_id not in sop_engine.executive_metrics:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        dashboard = sop_engine.executive_metrics[dashboard_id]
        
        return {
            "status": "success",
            "dashboard_id": dashboard_id,
            "dashboard": dashboard
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
