"""
NEXUS — Copilot Router
"""

from fastapi import APIRouter, Depends  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.errors import EngineUnavailableError  # type: ignore
from app.core.orchestrator import get_analysis_result  # type: ignore

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
    """
    Simulate execution of an AI-recommended fix.

    Computes a data-driven resilience delta by checking whether any
    pending mitigation actions of this type exist and using their
    monte_carlo_summary to estimate impact. Falls back to a clearly
    labelled estimate when no simulation data is available.

    # TODO: wire to actual execution (PO dispatch, email) when
    #       external integrations are added.
    """
    from app.models.supply import PendingAction  # type: ignore

    fix_type = body.type or "unknown"

    # Look for a recently-drafted mitigation action of this type to get
    # a data-driven resilience estimate
    recent = (
        db.query(PendingAction)
        .filter(PendingAction.action_type == fix_type)
        .order_by(PendingAction.created_at.desc())
        .first()
    )

    if recent and recent.monte_carlo_summary:
        mc = recent.monte_carlo_summary
        p50_risk = mc.get("system_risk_score")
        if p50_risk is not None:
            trigger = float(recent.trigger_score or 70)
            delta_pts = round(trigger - float(p50_risk), 1)
            resilience_delta = f"+{delta_pts} pts risk reduction (P50 simulation)"
        else:
            resilience_delta = "# TODO: not yet computed — Monte Carlo not fitted"
    else:
        # No simulation data — label it explicitly rather than showing a fake number
        resilience_delta = "# TODO: not yet computed — trigger an analysis first"

    return {
        "status": "simulated",
        "type":   fix_type,
        "resilience_delta": resilience_delta,
        "message": (
            f"Fix of type '{fix_type}' logged. "
            "Awaiting human approval in the Mitigation queue before execution."
        ),
        "approval_url": "/mitigation/pending",
    }
