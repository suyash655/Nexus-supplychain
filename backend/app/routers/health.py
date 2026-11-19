import time

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.core.dependencies import get_db

router = APIRouter()

@router.get("/health")
async def health(db = Depends(get_db)):
    start = time.time()
    db.execute(text("SELECT 1"))
    db_latency_ms = round((time.time() - start) * 1000, 2)
    return {
        "status": "ok",
        "db": "connected",
        "db_latency_ms": db_latency_ms,
        "version": "0.1.0",
    }
