"""Unified IBP orchestration API."""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.service import require_permission
from app.core.dependencies import require_auth
from app.core.ibp_orchestrator import ibp_orchestrator

router = APIRouter(prefix="/ibp-orchestrator", tags=["IBP Orchestrator"])


class DataFlowRequest(BaseModel):
    template_id: str = Field("monthly_ibp", max_length=80)


class ScenarioRequest(BaseModel):
    name: str = Field(max_length=160)
    scenario_type: str = Field("what_if", max_length=80)
    assumptions: Dict[str, Any] = Field(default_factory=dict)


@router.get("/overview")
def overview(user: dict = Depends(require_auth)):
    require_permission(user, "ibp:read")
    return ibp_orchestrator.get_overview()


@router.post("/data-flow/run")
def run_data_flow(request: DataFlowRequest, user: dict = Depends(require_auth)):
    require_permission(user, "ibp:execute")
    return ibp_orchestrator.run_data_flow(request.template_id)


@router.get("/templates")
def templates(user: dict = Depends(require_auth)):
    require_permission(user, "ibp:read")
    return {"status": "success", "templates": ibp_orchestrator.templates}


@router.post("/scenarios")
def create_scenario(request: ScenarioRequest, user: dict = Depends(require_auth)):
    require_permission(user, "ibp:execute")
    return ibp_orchestrator.create_scenario(request.name, request.scenario_type, request.assumptions)


@router.get("/scenarios")
def list_scenarios(user: dict = Depends(require_auth)):
    require_permission(user, "ibp:read")
    return ibp_orchestrator.list_scenarios()
