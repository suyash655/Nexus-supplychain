"""
NEXUS — Mitigation Router
===========================
Endpoints for the agentic mitigation loop.

GET  /mitigation/pending          — list all pending actions (awaiting approval)
GET  /mitigation/pending/{id}     — get one pending action with full detail
POST /mitigation/approve/{id}     — human approves → executes action
POST /mitigation/reject/{id}      — human rejects
GET  /mitigation/traces           — agent execution trace log (observability page)
GET  /mitigation/traces/{run_id}  — traces for a specific run
POST /mitigation/trigger          — manually trigger for a supplier (testing)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_auth
from app.models.agent_actions import AgentTrace
from app.models.supply import PendingAction

logger = logging.getLogger("nexus.routers.mitigation")
router = APIRouter(prefix="/mitigation", tags=["Mitigation"])


# ── Schemas ────────────────────────────────────────────────────────────────

class ApproveRequest(BaseModel):
    approved_by: str = Field("procurement_officer", max_length=200)


class RejectRequest(BaseModel):
    rejected_by: str = Field("procurement_officer", max_length=200)
    reason: str      = Field("", max_length=1000)


class ManualTriggerRequest(BaseModel):
    supplier:    str   = Field(..., min_length=1, max_length=200)
    risk_score:  float = Field(..., ge=0, le=100)
    sku:         Optional[str] = None


# ── Helpers ────────────────────────────────────────────────────────────────

def _pa_to_dict(pa: PendingAction) -> dict:
    return {
        "id":                   pa.id,
        "run_id":               pa.run_id,
        "supplier":             pa.supplier,
        "sku":                  pa.sku,
        "trigger_score":        pa.trigger_score,
        "action_type":          pa.action_type,
        "action_summary":       pa.action_summary,
        "action_detail":        pa.action_detail,
        "backup_suppliers":     pa.backup_suppliers,
        "monte_carlo_summary":  pa.monte_carlo_summary,
        "rag_context":          pa.rag_context,
        "llm_reasoning":        pa.llm_reasoning,
        "status":               pa.status,
        "approved_by":          pa.approved_by,
        "approved_at":          pa.approved_at.isoformat() if pa.approved_at else None,
        "executed_at":          pa.executed_at.isoformat() if pa.executed_at else None,
        "execution_log":        pa.execution_log,
        "created_at":           pa.created_at.isoformat() if pa.created_at else None,
    }


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/pending")
def list_pending_actions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit:  int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """List pending mitigation actions, newest first."""
    q = db.query(PendingAction).order_by(PendingAction.created_at.desc())
    if status:
        q = q.filter(PendingAction.status == status)
    items = q.limit(limit).all()
    return {
        "total": len(items),
        "items": [_pa_to_dict(pa) for pa in items],
    }


@router.get("/pending/{action_id}")
def get_pending_action(
    action_id: int,
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """Get a single pending action with full reasoning chain."""
    pa = db.query(PendingAction).filter(PendingAction.id == action_id).first()
    if not pa:
        raise HTTPException(status_code=404, detail=f"Action #{action_id} not found")
    return _pa_to_dict(pa)


@router.post("/approve/{action_id}")
def approve_pending_action(
    action_id: int,
    body: ApproveRequest,
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """
    Human approves a mitigation action.
    Server-side gate: only manager or admin (or active demo mode) can approve.
    Triggers execute_action.
    """
    allowed_roles = {"admin", "manager"}
    user_role = user.get("role", "viewer")
    if user_role not in allowed_roles and not user.get("demo", False):
        raise HTTPException(
            status_code=403,
            detail=f"Role '{user_role}' is not authorized to approve actions. Requires manager or admin.",
        )

    from agent.mitigation_graph import approve_action  # type: ignore
    result = approve_action(action_id, body.approved_by, role=user_role)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/reject/{action_id}")
def reject_pending_action(
    action_id: int,
    body: RejectRequest,
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """Human rejects a mitigation action. Server-side gate: manager or admin."""
    allowed_roles = {"admin", "manager"}
    user_role = user.get("role", "viewer")
    if user_role not in allowed_roles and not user.get("demo", False):
        raise HTTPException(
            status_code=403,
            detail=f"Role '{user_role}' is not authorized to reject actions. Requires manager or admin.",
        )

    from agent.mitigation_graph import reject_action  # type: ignore
    result = reject_action(action_id, body.rejected_by, body.reason, role=user_role)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/traces")
def list_traces(
    run_id: Optional[str] = Query(None),
    limit:  int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """
    Agent execution trace log — replaces paid observability tools.
    Shows every node's input, output, duration, and error for each agent run.
    """
    q = db.query(AgentTrace).order_by(AgentTrace.created_at.desc())
    if run_id:
        q = q.filter(AgentTrace.run_id == run_id)
    traces = q.limit(limit).all()
    return {
        "total": len(traces),
        "traces": [
            {
                "id":          t.id,
                "run_id":      t.run_id,
                "step":        t.step,
                "node_name":   t.node_name,
                "input":       t.input_json,
                "output":      t.output_json,
                "duration_ms": t.duration_ms,
                "error":       t.error,
                "created_at":  t.created_at.isoformat() if t.created_at else None,
            }
            for t in traces
        ],
    }


@router.get("/traces/{run_id}")
def get_run_traces(
    run_id: str,
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """Get all trace steps for a specific agent run, ordered by step."""
    traces = (
        db.query(AgentTrace)
        .filter(AgentTrace.run_id == run_id)
        .order_by(AgentTrace.step.asc())
        .all()
    )
    if not traces:
        raise HTTPException(status_code=404, detail=f"No traces found for run_id={run_id}")
    return {
        "run_id": run_id,
        "steps":  len(traces),
        "traces": [
            {
                "step":        t.step,
                "node_name":   t.node_name,
                "input":       t.input_json,
                "output":      t.output_json,
                "duration_ms": t.duration_ms,
                "error":       t.error,
            }
            for t in traces
        ],
    }


@router.post("/trigger")
def manual_trigger(
    body: ManualTriggerRequest,
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """
    Manually trigger the mitigation loop for testing.
    Useful for demos — no need to wait for the ML pipeline to cross a threshold.
    """
    from agent.mitigation_graph import CRITICAL_THRESHOLD, trigger_mitigation  # type: ignore
    from app.core.orchestrator import get_analysis_result  # type: ignore

    if body.risk_score < CRITICAL_THRESHOLD:
        raise HTTPException(
            status_code=422,
            detail=f"risk_score ({body.risk_score}) is below CRITICAL_THRESHOLD ({CRITICAL_THRESHOLD}). "
                   "Raise the score to trigger the mitigation loop."
        )

    # Fetch current risk data and graph for this supplier from cached analysis
    ml_res    = get_analysis_result(db, "ml", {})
    graph_res = get_analysis_result(db, "graph", {})

    risk_scores = ml_res.get("risk_scores", []) if ml_res else []
    risk_data   = next(
        (s for s in risk_scores if body.supplier.lower() in s.get("supplier", "").lower()),
        {"supplier": body.supplier, "risk_score": body.risk_score},
    )
    graph_data  = graph_res.get("visualization") if graph_res else None

    import threading
    action_id_holder = [None]

    def run():
        action_id_holder[0] = trigger_mitigation(
            supplier   = body.supplier,
            risk_score = body.risk_score,
            risk_data  = risk_data,
            graph_data = graph_data,
            sku        = body.sku,
        )

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout=45)  # max 45s to keep the HTTP response fast

    action_id = action_id_holder[0]
    if action_id and action_id > 0:
        return {
            "status":    "triggered",
            "action_id": action_id,
            "message":   f"Mitigation loop completed. Action #{action_id} awaiting approval.",
        }
    return {
        "status":  "triggered",
        "message": "Mitigation loop started. Check /mitigation/pending for results.",
    }


@router.get("/stats")
def mitigation_stats(
    db: Session = Depends(get_db),
    user: dict  = Depends(require_auth),
):
    """Summary stats for the agents dashboard KPI strip."""
    total     = db.query(PendingAction).count()
    pending   = db.query(PendingAction).filter(PendingAction.status == "awaiting_approval").count()
    executed  = db.query(PendingAction).filter(PendingAction.status == "executed").count()
    rejected  = db.query(PendingAction).filter(PendingAction.status == "rejected").count()
    return {
        "total_actions":    total,
        "awaiting_approval":pending,
        "executed":         executed,
        "rejected":         rejected,
        "approval_rate":    round(executed / max(executed + rejected, 1) * 100, 1),
    }
