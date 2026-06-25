"""
NEXUS — Supply Chain Event Model
==================================
SQLAlchemy model for real-time supply chain events with tenant isolation.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text  # type: ignore
from app.models.base import Base, _utcnow
import uuid


class SupplyChainEvent(Base):
    """Stores ingested supply chain events for real-time monitoring and RAG indexing."""
    __tablename__ = "supply_chain_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, index=True, nullable=False)
    supplier_id = Column(String, index=True, nullable=False)
    severity = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    region = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    impact_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=_utcnow, index=True)
