from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.models.base import Base, _utcnow
from datetime import datetime, timezone

class RiskEvent(Base):
    __tablename__ = "risk_events"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    event_type = Column(String)
    severity = Column(String)
    risk_score = Column(Float)
    supplier = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    region = Column(String, nullable=True)
    description = Column(Text)
    root_cause = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

class WorldEvent(Base):
    __tablename__ = "world_events"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    title = Column(String)
    description = Column(Text)
    severity = Column(String)
    region = Column(String)
    impact_score = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
