"""
NEXUS — Copilot Router
"""

from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.orchestrator import get_analysis_result  # type: ignore
from app.core.errors import EngineUnavailableError, ValidationError  # type: ignore

router = APIRouter(prefix="/copilot", tags=["Copilot"])


# ── Request schemas ──────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="Question for the AI co-pilot")


class WhatIfRequest(BaseModel):
    scenario: str = Field(..., min_length=1, max_length=2000, description="Scenario description for simulation")


class ExecuteFixRequest(BaseModel):
    type: str = Field("unknown", max_length=200, description="The fix type to simulate")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _require_copilot():
    from app.main import engines  # type: ignore
    if not engines.ai_copilot:
        raise EngineUnavailableError("AI Copilot engine is unavailable. Check startup logs.")
    return engines.ai_copilot


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/providers")
def get_providers(user: dict = Depends(require_auth)):
    """Show available LLM providers and active configuration."""
    copilot = _require_copilot()
    return copilot.get_provider_info()


@router.get("/summary")
def executive_summary(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get AI-generated executive risk summary."""
    exec_res = get_analysis_result(db, "executive")
    if exec_res:
        return exec_res
    return {
        "overall_risk_level": "UNKNOWN",
        "risk_color": "#64748b",
        "narrative": "Upload data to generate analysis.",
        "recommendations": [],
        "key_metrics": {},
    }


@router.post("/ask")
def copilot_ask(
    body: AskRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Ask the AI Co-Pilot a question."""
    copilot = _require_copilot()
    ml_res   = get_analysis_result(db, "ml", {})
    graph_res = get_analysis_result(db, "graph", {})

    risk_scores = ml_res.get("risk_scores", [])
    anomalies   = ml_res.get("anomalies", {})
    summary     = ml_res.get("summary", {})
    graph_data  = graph_res.get("visualization") if graph_res else None

    return copilot.answer_question(body.question, risk_scores, anomalies, summary, graph_data)


@router.post("/what-if")
def copilot_whatif(
    body: WhatIfRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Run a what-if scenario simulation."""
    copilot   = _require_copilot()
    ml_res    = get_analysis_result(db, "ml", {})
    graph_res = get_analysis_result(db, "graph", {})

    risk_scores = ml_res.get("risk_scores", [])
    summary     = ml_res.get("summary", {})
    graph_data  = graph_res.get("visualization") if graph_res else None

    return copilot.what_if_simulation(body.scenario, risk_scores, graph_data, summary)


@router.post("/execute-fix")
def execute_fix(
    body: ExecuteFixRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Simulate execution of an AI-recommended fix."""
    return {
        "status": "Fix Simulated",
        "type": body.type,
        "resilience_delta": "+5.2%",
        "message": f"Successfully simulated '{body.type}' mitigation. Network risk reduced.",
    }
