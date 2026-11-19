"""
NEXUS — SAP IBP-Style Response Planning API Router
==================================================
REST API endpoints for what-if scenario analysis,
real-time rebalancing, and DDMRP capabilities.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.engines.response_planning import ResponsePlanningEngine, ScenarioType

router = APIRouter(prefix="/ibp/response", tags=["Response Planning"])

# Global response planning engine instance
response_engine = ResponsePlanningEngine()


class ScenarioRequest(BaseModel):
    """Request model for what-if scenario creation."""
    base_plan: Dict[str, Any]
    scenario_changes: Dict[str, Any]
    scenario_type: str  # "demand", "supply", "network", "financial", "capacity"
    scenario_name: str


class DDMRPSetupRequest(BaseModel):
    """Request model for DDMRP buffer setup."""
    inventory_data: List[Dict[str, Any]]
    demand_profiles: Dict[str, Dict[str, float]]
    lead_times: Dict[str, int]


class BufferAdjustmentRequest(BaseModel):
    """Request model for dynamic buffer adjustment."""
    buffer_id: str
    demand_changes: Dict[str, float]
    lead_time_changes: Dict[str, int]


class RebalancingRequest(BaseModel):
    """Request model for real-time rebalancing."""
    inventory_data: List[Dict[str, Any]]
    demand_forecast: Dict[str, List[float]]
    transportation_matrix: Dict[str, Dict[str, float]]


class SchedulingRequest(BaseModel):
    """Request model for constraint-based scheduling."""
    production_requests: List[Dict[str, Any]]
    constraints: Dict[str, Any]


@router.post("/initialize")
async def initialize_response_planning(
    config: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Initialize response planning engine with configuration.
    """
    try:
        result = response_engine.initialize(config)

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/create")
async def create_scenario(
    request: ScenarioRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create what-if scenario for planning analysis.

    Supports demand, supply, network, financial, and capacity scenarios
    with impact analysis and recommendations.
    """
    try:
        # Convert scenario type string to enum
        try:
            scenario_type = ScenarioType(request.scenario_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scenario type. Must be one of: {[t.value for t in ScenarioType]}"
            )

        result = response_engine.create_what_if_scenario(
            base_plan=request.base_plan,
            scenario_changes=request.scenario_changes,
            scenario_type=scenario_type,
            scenario_name=request.scenario_name
        )

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ddmrp/setup")
async def setup_ddmrp_buffers(
    request: DDMRPSetupRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Setup DDMRP buffers for demand-driven replenishment.

    Calculates buffer zones (green, yellow, red) based on
    demand profiles and lead times for each SKU-location combination.
    """
    try:
        # Convert inventory data to DataFrame
        df = pd.DataFrame(request.inventory_data)

        result = response_engine.setup_ddmrp_buffers(
            inventory_data=df,
            demand_profiles=request.demand_profiles,
            lead_times=request.lead_times
        )

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ddmrp/adjust")
async def adjust_ddmrp_buffers(
    request: BufferAdjustmentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Dynamically adjust DDMRP buffers based on changing conditions.

    Recalculates buffer zones when demand patterns or lead times change.
    """
    try:
        result = response_engine.dynamic_buffer_adjustment(
            buffer_id=request.buffer_id,
            demand_changes=request.demand_changes,
            lead_time_changes=request.lead_time_changes
        )

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebalancing")
async def real_time_rebalancing(
    request: RebalancingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Perform real-time network rebalancing.

    Optimizes inventory distribution across the network based on
    demand forecasts and transportation costs.
    """
    try:
        # Convert inventory data to DataFrame
        df = pd.DataFrame(request.inventory_data)

        result = response_engine.real_time_rebalancing(
            inventory_data=df,
            demand_forecast=request.demand_forecast,
            transportation_matrix=request.transportation_matrix
        )

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduling")
async def constraint_based_scheduling(
    request: SchedulingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Perform constraint-based production scheduling.

    Schedules production requests while respecting capacity,
    material, and time constraints.
    """
    try:
        result = response_engine.constraint_based_scheduling(
            production_requests=request.production_requests,
            constraints=request.constraints
        )

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/compare")
async def compare_scenarios(
    scenario_ids: List[str] = Query(..., description="List of scenario IDs to compare"),
    current_user: dict = Depends(get_current_user)
):
    """
    Compare multiple scenarios side by side.
    """
    try:
        result = response_engine.get_scenario_comparison(scenario_ids)

        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios")
async def list_scenarios(
    scenario_type: Optional[str] = Query(None, description="Filter by scenario type"),
    current_user: dict = Depends(get_current_user)
):
    """
    List all available scenarios.
    """
    try:
        scenarios = []

        for scenario_id, scenario_data in response_engine.scenarios.items():
            if scenario_type and scenario_data["scenario_type"] != scenario_type.lower():
                continue

            scenarios.append({
                "scenario_id": scenario_id,
                "name": scenario_data["scenario_name"],
                "type": scenario_data["scenario_type"],
                "created_at": scenario_data["created_at"],
                "impact_summary": {
                    "risk_level": scenario_data["impact_analysis"]["risk_assessment"]["overall_risk"],
                    "constraint_violations": len(scenario_data["impact_analysis"]["constraint_violations"])
                }
            })

        # Sort by creation date
        scenarios.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "status": "success",
            "scenarios": scenarios,
            "total_scenarios": len(scenarios)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/{scenario_id}")
async def get_scenario(
    scenario_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific scenario details.
    """
    try:
        if scenario_id not in response_engine.scenarios:
            raise HTTPException(status_code=404, detail="Scenario not found")

        scenario = response_engine.scenarios[scenario_id]

        return {
            "status": "success",
            "scenario_id": scenario_id,
            "scenario": scenario
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ddmrp/{buffer_id}")
async def get_ddmrp_buffers(
    buffer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific DDMRP buffer setup.
    """
    try:
        if buffer_id not in response_engine.ddmrp_buffers:
            raise HTTPException(status_code=404, detail="Buffer setup not found")

        buffers = response_engine.ddmrp_buffers[buffer_id]

        return {
            "status": "success",
            "buffer_id": buffer_id,
            "buffers": buffers
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rebalancing/{plan_id}")
async def get_rebalancing_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific rebalancing plan.
    """
    try:
        if plan_id not in response_engine.rebalancing_plan:
            raise HTTPException(status_code=404, detail="Rebalancing plan not found")

        plan = response_engine.rebalancing_plan[plan_id]

        return {
            "status": "success",
            "plan_id": plan_id,
            "rebalancing_plan": plan
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
