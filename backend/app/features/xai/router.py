import io
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_auth
from app.core.orchestrator import get_analysis_result

xai_router = APIRouter(prefix="/xai", tags=["XAI"])

@xai_router.get("/feature-importance")
def feature_importance(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get feature importance analysis."""
    xai_res = get_analysis_result(db, "xai")
    if xai_res:
        return xai_res["importance"]
    raise HTTPException(status_code=400, detail="No analysis available. Upload data first.")

@xai_router.get("/counterfactuals")
def counterfactuals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Get counterfactual explanations."""
    xai_res = get_analysis_result(db, "xai")
    data = xai_res["counterfactuals"] if xai_res else []
    return {
        "data": data[skip : skip + limit],
        "total": len(data),
        "skip": skip,
        "limit": limit,
    }
