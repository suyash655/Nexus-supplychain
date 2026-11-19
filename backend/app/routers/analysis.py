"""
NEXUS — Analysis Progress Router
=================================
API endpoints for tracking analysis progress and status.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.analysis_coordinator import coordinator
from app.core.dependencies import get_db, require_auth

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/progress/{upload_id}")
def get_analysis_progress(
    upload_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Get analysis progress for a specific upload."""
    progress = coordinator.get_progress(upload_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return progress


@router.post("/cancel/{upload_id}")
def cancel_analysis(
    upload_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Cancel an ongoing analysis."""
    success = coordinator.cancel_analysis(upload_id)

    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found or already completed")

    return {"status": "cancelled", "upload_id": upload_id}
