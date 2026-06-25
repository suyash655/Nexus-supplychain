from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Index
from app.models.base import Base, _utcnow

class SupplyData(Base):
    __tablename__ = "supply_data"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    supplier = Column(String)         # no separate single-col index — covered by composites below
    sku = Column(String)              # same
    warehouse = Column(String, nullable=True)
    region = Column(String, nullable=True)
    shipment_id = Column(String, nullable=True)
    order_date = Column(String, nullable=True)
    delivery_date = Column(String, nullable=True)
    delay_days = Column(Integer, default=0)
    cost = Column(Float, default=0)
    quantity = Column(Integer, default=0)
    category = Column(String, nullable=True)
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        # ── Analytics: GROUP BY supplier, ORDER BY avg(delay_days)
        # Covers /analytics/suppliers query. The tenant_id prefix ensures
        # tenant isolation is enforced at the index level (no full-table scan
        # when multiple tenants share the table).
        Index("ix_supply_tenant_supplier", "tenant_id", "supplier"),

        # ── Analytics: GROUP BY sku (potential future breakdown by SKU)
        # Also used by upload dedup checks. Omit a bare sku index because
        # it would only help sku-only lookups which don't exist yet.
        Index("ix_supply_tenant_sku", "tenant_id", "sku"),

        # ── Analytics: GROUP BY region (regional breakdown queries)
        # region has low cardinality (~5-20 values) so a single-col index
        # gives little benefit; composite with tenant_id is the right choice.
        Index("ix_supply_tenant_region", "tenant_id", "region"),

        # ── Time-range queries: WHERE order_date BETWEEN ... ORDER BY order_date
        # Stored as String not Date, so we can't use a range index efficiently
        # on the value itself, but the index still eliminates the full table scan
        # for tenant-scoped date filtering. If order_date is ever migrated to
        # a proper Date column this index becomes a range-scan index.
        Index("ix_supply_tenant_order_date", "tenant_id", "order_date"),

        # ── NOT indexed: delay_days, cost, quantity, quality_score
        # These are aggregate targets (func.avg, func.sum), not filter columns.
        # Indexing them would add write overhead for every INSERT with zero
        # read benefit — SQLite/Postgres does not use an index to speed up
        # aggregates across all rows in a group.
        #
        # ── NOT indexed: warehouse, category, delivery_date
        # Not referenced in any current WHERE/GROUP BY/ORDER BY clause in
        # analytics.py. Adding speculative indexes only costs write overhead.
    )

class SupplierProfile(Base):
    __tablename__ = "supplier_profiles"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    name = Column(String, unique=True, index=True)
    location = Column(String, nullable=True)
    tier = Column(String, default="standard")
    risk_score = Column(Float, default=0)
    reliability_score = Column(Float, default=100)
    avg_delay = Column(Float, default=0)
    total_shipments = Column(Integer, default=0)
    total_cost = Column(Float, default=0)
    anomaly_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=_utcnow)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    analysis_type = Column(String, index=True)
    result_json = Column(JSON)
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

class UploadHistory(Base):
    __tablename__ = "upload_history"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    filename = Column(String)
    file_type = Column(String)
    rows_total = Column(Integer)
    rows_inserted = Column(Integer)
    rows_rejected = Column(Integer)
    columns_detected = Column(JSON)
    column_mapping = Column(JSON, nullable=True)
    data_quality_report = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

class ESGProfile(Base):
    __tablename__ = "esg_profiles"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    supplier = Column(String, index=True)
    total_emissions_kg = Column(Float, default=0)
    carbon_tier = Column(String, nullable=True)
    compliance_flags = Column(JSON, nullable=True)
    esg_score = Column(Float, nullable=True)
    region = Column(String, nullable=True)
    transport_mode = Column(String, nullable=True)
    last_assessed = Column(DateTime, default=_utcnow)

class KPIMetric(Base):
    __tablename__ = "kpi_metrics"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    metric_name = Column(String, index=True)
    value = Column(Float)
    unit = Column(String, nullable=True)
    period = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

class ScheduledIngestion(Base):
    __tablename__ = "scheduled_ingestions"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    job_name = Column(String, index=True)
    connector_type = Column(String)
    connector_config = Column(JSON)
    schedule_cron = Column(String)
    schedule_label = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_status = Column(String, nullable=True)
    last_rows_ingested = Column(Integer, nullable=True)
    total_runs = Column(Integer, default=0)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
