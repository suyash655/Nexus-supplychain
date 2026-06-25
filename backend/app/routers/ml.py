"""
NEXUS — ML Router
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.orchestrator import get_analysis_result  # type: ignore

router = APIRouter(prefix="/ml", tags=["ML"])


@router.get("/anomalies")
def get_anomalies(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get detected anomalies."""
    ml_res = get_analysis_result(db, "ml")
    if ml_res:
        return ml_res["anomalies"]
    return {"anomalies": [], "anomaly_count": 0}


@router.get("/risk-scores")
def get_risk_scores(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Get supplier risk scores (0–100)."""
    ml_res = get_analysis_result(db, "ml")
    data = ml_res["risk_scores"] if ml_res else []
    return {
        "data": data[skip : skip + limit],
        "total": len(data),
        "skip": skip,
        "limit": limit,
    }


@router.get("/bullwhip")
def get_bullwhip(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get shipment volatility analysis (formerly labelled 'bullwhip ratio')."""
    ml_res = get_analysis_result(db, "ml")
    if ml_res:
        return ml_res.get("bullwhip_analysis", {})
    return {"shipment_volatility_index": 1.0, "status": "no_data"}


@router.get("/full-analysis")
def get_full_analysis(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get complete ML analysis results."""
    ml_res = get_analysis_result(db, "ml")
    if ml_res:
        return ml_res
    return {"error": "No analysis available. Upload data first."}


@router.post("/refresh")
def refresh_analysis(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Re-run the full ML analysis pipeline."""
    from app.core.orchestrator import run_full_analysis as _run  # type: ignore
    from app.main import _get_engine_kwargs  # type: ignore
    background_tasks.add_task(_run, **_get_engine_kwargs())
    return {"status": "success", "message": "Analysis refresh started in background."}
