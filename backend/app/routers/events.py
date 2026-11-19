"""
NEXUS — Events Router (Real-Time Event Monitoring)
====================================================
P0 Gap Fix: Real-time event monitoring via webhook ingest + SSE stream.

Endpoints:
  POST /api/events/ingest  — Accept and store a supply chain event
  GET  /api/events/stream   — Server-Sent Events stream for real-time push
  GET  /api/events/recent   — Fetch recent events (polling fallback)
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.models.events import SupplyChainEvent  # type: ignore
from app.schemas.events import SupplyChainEventCreate, SupplyChainEventResponse  # type: ignore

logger = logging.getLogger("nexus.events")

router = APIRouter(prefix="/api/events", tags=["events"])

# ── In-memory event bus for SSE broadcasting ──
# In production, replace with Redis Pub/Sub for multi-process support.
_event_subscribers: list[asyncio.Queue] = []
_event_lock = asyncio.Lock()


async def _broadcast_event(event_data: dict):
    """Push an event to all active SSE subscribers."""
    async with _event_lock:
        dead_queues = []
        for queue in _event_subscribers:
            try:
                queue.put_nowait(event_data)
            except asyncio.QueueFull:
                dead_queues.append(queue)
        # Clean up dead subscribers
        for q in dead_queues:
            _event_subscribers.remove(q)


@router.post("/ingest", response_model=SupplyChainEventResponse)
async def ingest_event(
    payload: SupplyChainEventCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Ingest a new supply chain event.
    Stores in DB and broadcasts to all active SSE subscribers.
    """
    event = SupplyChainEvent(
        event_id=str(uuid.uuid4()),
        event_type=payload.event_type,
        supplier_id=payload.supplier_id,
        severity=payload.severity,
        description=payload.description,
        region=payload.region,
        sku=payload.sku,
        impact_score=payload.impact_score,
        notes=payload.notes,
        tenant_id=payload.tenant_id,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Broadcast to SSE subscribers
    event_data = {
        "id": event.id,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "supplier_id": event.supplier_id,
        "severity": event.severity,
        "description": event.description,
        "region": event.region,
        "sku": event.sku,
        "impact_score": event.impact_score,
        "notes": event.notes,
        "tenant_id": event.tenant_id,
        "timestamp": event.timestamp.isoformat(),
    }
    await _broadcast_event(event_data)
    logger.info("[NEXUS] Event ingested: %s (%s)", event.event_id, event.event_type)

    return event


@router.get("/stream")
async def event_stream(
    tenant_id: Optional[str] = Query(None, description="Filter events by tenant"),
):
    """
    Server-Sent Events stream for real-time event push.
    Connect from the frontend with: new EventSource('/api/events/stream?tenant_id=...')

    Sends:
      - 'new_event' when a supply chain event is ingested
      - 'heartbeat' every 30 seconds to keep the connection alive
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    async with _event_lock:
        _event_subscribers.append(queue)

    async def event_generator():
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"

            while True:
                try:
                    # Wait for an event with a 30-second timeout (for heartbeat)
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Filter by tenant if specified
                    if tenant_id and event_data.get("tenant_id") != tenant_id:
                        continue

                    yield f"event: new_event\ndata: {json.dumps(event_data)}\n\n"

                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f"event: heartbeat\ndata: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            async with _event_lock:
                if queue in _event_subscribers:
                    _event_subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/recent", response_model=list[SupplyChainEventResponse])
async def get_recent_events(
    tenant_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Fetch recent events (polling fallback for clients that don't support SSE).
    """
    query = db.query(SupplyChainEvent).order_by(SupplyChainEvent.timestamp.desc())
    if tenant_id:
        query = query.filter(SupplyChainEvent.tenant_id == tenant_id)
    events = query.limit(limit).all()
    return events
