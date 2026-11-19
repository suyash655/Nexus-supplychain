"""
NEXUS — Supply Chain Event Schemas
====================================
Pydantic models for event ingestion and SSE streaming.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field  # type: ignore


class SupplyChainEventCreate(BaseModel):
    """Schema for ingesting a new supply chain event."""
    event_type: str = Field(
        ...,
        description="Type of event: DELAY, DISRUPTION, QUALITY_ISSUE, SHORTAGE, GEOPOLITICAL, NATURAL_DISASTER",
        examples=["DISRUPTION"],
    )
    supplier_id: str = Field(..., description="Unique supplier identifier")
    severity: str = Field(
        ...,
        description="Event severity: LOW, MEDIUM, HIGH, CRITICAL",
        examples=["HIGH"],
    )
    description: str = Field(..., description="Human-readable event description")
    region: Optional[str] = Field(None, description="Affected geographic region")
    sku: Optional[str] = Field(None, description="Affected SKU, if applicable")
    impact_score: Optional[float] = Field(
        None, ge=0.0, le=100.0,
        description="Estimated impact score (0-100)",
    )
    notes: Optional[str] = Field(None, description="Additional notes or context")
    tenant_id: str = Field(..., description="Tenant identifier for data isolation")


class SupplyChainEventResponse(BaseModel):
    """Schema for returning a supply chain event."""
    id: int
    event_id: str
    event_type: str
    supplier_id: str
    severity: str
    description: str
    region: Optional[str] = None
    sku: Optional[str] = None
    impact_score: Optional[float] = None
    notes: Optional[str] = None
    tenant_id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class SSEEvent(BaseModel):
    """Schema for Server-Sent Event payloads."""
    type: str = Field(..., description="SSE event type: new_event, heartbeat, error")
    data: Optional[dict] = None
    event_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
