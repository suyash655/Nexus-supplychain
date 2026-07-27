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

# SAP IBP-style Planning Models

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, index=True)
    forecast_type = Column(String, default="statistical")  # statistical, ml, ensemble
    model_type = Column(String)  # arima, holt_winters, random_forest, etc.
    forecast_horizon = Column(Integer)
    forecast_data = Column(JSON)  # Array of forecast values with dates
    confidence_intervals = Column(JSON, nullable=True)  # Upper/lower bounds
    accuracy_metrics = Column(JSON, nullable=True)  # MAPE, MAE, RMSE
    parameters = Column(JSON, nullable=True)  # Model parameters
    version = Column(Integer, default=1)
    status = Column(String, default="active")  # active, deprecated
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)

class SupplyPlan(Base):
    __tablename__ = "supply_plans"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    plan_name = Column(String, index=True)
    plan_type = Column(String)  # production, distribution, capacity
    sku = Column(String, index=True)
    supplier = Column(String, nullable=True)
    warehouse = Column(String, nullable=True)
    planning_horizon = Column(Integer)
    plan_data = Column(JSON)  # Production schedule, DRP, etc.
    capacity_utilization = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String, default="draft")  # draft, approved, active
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, nullable=True)

class InventoryOptimization(Base):
    __tablename__ = "inventory_optimizations"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, index=True)
    warehouse = Column(String, index=True)
    optimization_type = Column(String)  # safety_stock, eoq, multi_echelon
    current_inventory = Column(Float, default=0)
    optimal_inventory = Column(Float, nullable=True)
    safety_stock = Column(Float, nullable=True)
    reorder_point = Column(Float, nullable=True)
    economic_order_quantity = Column(Float, nullable=True)
    service_level_target = Column(Float, default=0.95)
    holding_cost = Column(Float, nullable=True)
    ordering_cost = Column(Float, nullable=True)
    optimization_parameters = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)

class PlanningScenario(Base):
    __tablename__ = "planning_scenarios"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    scenario_name = Column(String, index=True)
    scenario_type = Column(String)  # demand, supply, network, financial
    base_scenario_id = Column(Integer, nullable=True)  # FK to scenarios table
    scenario_changes = Column(JSON)  # Changes from base scenario
    scenario_results = Column(JSON, nullable=True)  # Impact analysis
    comparison_metrics = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String, default="draft")  # draft, active, archived
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)

class ControlTowerAlert(Base):
    __tablename__ = "control_tower_alerts"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    alert_id = Column(String, unique=True, index=True)  # External alert ID
    alert_type = Column(String, index=True)  # anomaly, exception, kpi_breach
    alert_subtype = Column(String, nullable=True)
    severity = Column(String, index=True)  # info, warning, error, critical
    status = Column(String, index=True, default="open")  # open, acknowledged, resolved, closed
    message = Column(String)
    details = Column(JSON, nullable=True)
    affected_entities = Column(JSON, nullable=True)  # SKUs, suppliers, etc.
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    metric_name = Column(String, index=True)
    metric_category = Column(String, index=True)  # demand, supply, inventory, overall
    metric_value = Column(Float)
    metric_unit = Column(String, nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    target_value = Column(Float, nullable=True)
    threshold_warning = Column(Float, nullable=True)
    threshold_critical = Column(Float, nullable=True)
    trend = Column(String, nullable=True)  # increasing, decreasing, stable
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

class SOPProcess(Base):
    __tablename__ = "sop_processes"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    process_name = Column(String, index=True)
    process_type = Column(String)  # monthly, quarterly, annual
    cycle_start_date = Column(DateTime)
    cycle_end_date = Column(DateTime, nullable=True)
    participants = Column(JSON, nullable=True)  # List of user IDs/roles
    consensus_forecast = Column(JSON, nullable=True)
    financial_integration = Column(JSON, nullable=True)
    performance_tracking = Column(JSON, nullable=True)
    approval_workflow = Column(JSON, nullable=True)
    status = Column(String, default="in_progress")  # in_progress, completed, cancelled
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)

# Causal Factor Models for Demand Planning

class CausalFactor(Base):
    __tablename__ = "causal_factors"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    factor_type = Column(String, index=True)  # promotion, holiday, economic, weather, social
    factor_name = Column(String, index=True)
    factor_category = Column(String, nullable=True)  # sub-category for grouping
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, nullable=True)
    impact_regions = Column(JSON, nullable=True)  # List of affected regions
    impact_skus = Column(JSON, nullable=True)  # List of affected SKUs
    impact_coefficient = Column(Float, default=1.0)  # Demand impact multiplier
    confidence_level = Column(Float, default=0.5)  # Confidence in impact estimate
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class PromotionData(Base):
    __tablename__ = "promotion_data"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    promotion_id = Column(String, unique=True, index=True)
    promotion_name = Column(String)
    promotion_type = Column(String)  # discount, bundle, loyalty, seasonal
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)
    discount_percentage = Column(Float, default=0)
    affected_skus = Column(JSON)  # List of SKUs
    affected_categories = Column(JSON, nullable=True)  # List of product categories
    regions = Column(JSON, nullable=True)  # Affected regions
    channels = Column(JSON, nullable=True)  # Sales channels (online, retail, etc.)
    baseline_demand = Column(JSON, nullable=True)  # Pre-promotion demand levels
    uplift_percentage = Column(Float, nullable=True)  # Actual uplift observed
    cost = Column(Float, default=0)  # Promotion cost
    roi = Column(Float, nullable=True)  # Return on investment
    status = Column(String, default="planned")  # planned, active, completed, cancelled
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)

class HolidayCalendar(Base):
    __tablename__ = "holiday_calendar"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    holiday_name = Column(String, index=True)
    holiday_date = Column(DateTime, index=True)
    holiday_type = Column(String)  # national, regional, religious, observance
    region = Column(String, index=True)  # Affected region
    impact_level = Column(String, default="medium")  # low, medium, high
    affected_categories = Column(JSON, nullable=True)  # Product categories affected
    demand_adjustment = Column(Float, default=1.0)  # Demand adjustment factor
    pre_holiday_days = Column(Integer, default=3)  # Days before holiday affected
    post_holiday_days = Column(Integer, default=2)  # Days after holiday affected
    is_recurring = Column(Integer, default=0)  # 1 if recurring annually
    created_at = Column(DateTime, default=_utcnow)

class EconomicIndicator(Base):
    __tablename__ = "economic_indicators"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    indicator_name = Column(String, index=True)
    indicator_code = Column(String, index=True)  # e.g., GDP, CPI, UNEMPLOYMENT
    data_date = Column(DateTime, index=True)
    value = Column(Float)
    unit = Column(String, nullable=True)  # e.g., %, billions, index
    region = Column(String, index=True)
    source = Column(String, nullable=True)  # Data source (BLS, World Bank, etc.)
    frequency = Column(String, default="monthly")  # daily, weekly, monthly, quarterly
    confidence = Column(Float, nullable=True)  # Data confidence/reliability
    impact_correlation = Column(JSON, nullable=True)  # Correlation with demand by SKU/category
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class ExternalDataConnector(Base):
    __tablename__ = "external_data_connectors"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    connector_name = Column(String, unique=True, index=True)
    connector_type = Column(String)  # pos_system, social_media, weather_api, economic_api
    config = Column(JSON)  # Connection configuration
    endpoint_url = Column(String, nullable=True)
    authentication = Column(JSON, nullable=True)  # API keys, tokens
    refresh_interval_minutes = Column(Integer, default=60)
    last_fetch_at = Column(DateTime, nullable=True)
    last_fetch_status = Column(String, nullable=True)
    data_fields = Column(JSON, nullable=True)  # Expected data fields
    mapping_rules = Column(JSON, nullable=True)  # Field mapping to internal schema
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class DemandSignal(Base):
    __tablename__ = "demand_signals"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    signal_type = Column(String, index=True)  # pos_transaction, social_sentiment, weather_impact
    source_connector = Column(String, index=True)  # Reference to connector
    timestamp = Column(DateTime, index=True)
    sku = Column(String, nullable=True, index=True)
    signal_data = Column(JSON)  # Signal-specific data
    signal_strength = Column(Float, default=0.5)  # 0-1 scale
    confidence = Column(Float, default=0.5)  # Confidence in signal
    region = Column(String, nullable=True)
    location = Column(String, nullable=True)
    processed = Column(Integer, default=0)  # 1 if processed in forecast
    impact_applied = Column(Float, nullable=True)  # Actual impact applied to forecast
    created_at = Column(DateTime, default=_utcnow)

# Capacity Planning Models

class CapacityConstraint(Base):
    __tablename__ = "capacity_constraints"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    resource_id = Column(String, index=True)  # Machine, labor, warehouse
    resource_type = Column(String, index=True)  # production, storage, transportation
    location = Column(String, nullable=True)
    max_capacity = Column(Float, default=0)  # Maximum capacity per period
    current_utilization = Column(Float, default=0)  # Current utilization percentage

# Additional Incident Management Tables for Advanced Features

class IncidentAlertCorrelation(Base):
    __tablename__ = "incident_alert_correlations"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    incident_id = Column(String, index=True)
    alert_id = Column(String, index=True)
    correlation_confidence = Column(Float, default=0)
    correlation_type = Column(String)  # root_cause, related, symptom
    correlation_notes = Column(Text, nullable=True)
    linked_at = Column(DateTime, default=_utcnow)
    created_at = Column(DateTime, default=_utcnow)

class PredictiveAlert(Base):
    __tablename__ = "predictive_alerts"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    alert_id = Column(String, unique=True, index=True)
    alert_type = Column(String, index=True)  # predictive_delay, predictive_cost, predictive_quality
    severity = Column(String, index=True)  # warning, critical
    confidence = Column(Float, default=0)  # 0-1
    predicted_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    trend = Column(Float, default=0)
    message = Column(Text)
    recommended_actions = Column(JSON, nullable=True)
    predicted_occurrence = Column(DateTime, nullable=True)
    status = Column(String, default="active", index=True)  # active, acknowledged, false_positive, occurred
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

# Inventory Lifecycle Management Models

class InventoryLifecycle(Base):
    __tablename__ = "inventory_lifecycle"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, index=True)
    warehouse = Column(String, index=True)
    batch_id = Column(String, nullable=True)
    production_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    current_quantity = Column(Float, default=0)
    original_quantity = Column(Float, default=0)
    quality_score = Column(Float, nullable=True)
    lifecycle_stage = Column(String, default="active")  # active, near_expiry, expired, written_off
    age_days = Column(Integer, default=0)
    deterioration_rate = Column(Float, default=0.0)
    storage_conditions = Column(JSON, nullable=True)  # Temperature, humidity requirements
    last_quality_check = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class PerishableInventory(Base):
    __tablename__ = "perishable_inventory"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, index=True)
    shelf_life_days = Column(Integer, default=30)
    deterioration_rate = Column(Float, default=0.01)
    quality_threshold = Column(Float, default=0.8)
    storage_temperature_min = Column(Float, nullable=True)
    storage_temperature_max = Column(Float, nullable=True)
    humidity_requirements = Column(String, nullable=True)
    handling_instructions = Column(Text, nullable=True)
    fefo_required = Column(Integer, default=0)  # First-Expired-First-Out required
    waste_percentage = Column(Float, default=0.0)
    last_waste_calculation = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class ObsolescenceRisk(Base):
    __tablename__ = "obsolescence_risks"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, index=True)
    risk_score = Column(Float, default=0.0)  # 0-100
    risk_category = Column(String, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    lifecycle_stage = Column(String, default="unknown")  # introduction, growth, maturity, decline, end_of_life
    demand_decline_rate = Column(Float, default=0.0)
    days_of_supply = Column(Float, default=0.0)
    inventory_age_days = Column(Integer, default=0)
    potential_write_off = Column(Float, default=0.0)
    mitigation_actions = Column(JSON, nullable=True)
    last_assessment = Column(DateTime, default=_utcnow)
    next_review_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class ProductLifecycle(Base):
    __tablename__ = "product_lifecycles"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, unique=True, index=True)
    launch_date = Column(DateTime, nullable=True)
    maturity_date = Column(DateTime, nullable=True)
    decline_date = Column(DateTime, nullable=True)
    end_of_life_date = Column(DateTime, nullable=True)
    current_stage = Column(String, default="introduction")
    phase_out_strategy = Column(Text, nullable=True)
    replacement_sku = Column(String, nullable=True)
    inventory_disposition_plan = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class InventoryPositioning(Base):
    __tablename__ = "inventory_positioning"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    sku = Column(String, index=True)
    location = Column(String, index=True)
    echelon = Column(String, index=True)  # upstream, midstream, downstream
    positioning_strategy = Column(String, default="pull")  # push, pull, hybrid
    push_score = Column(Float, default=0.0)
    pull_score = Column(Float, default=0.0)
    optimal_inventory_level = Column(Float, nullable=True)
    capacity_limit = Column(Float, nullable=True)
    holding_cost = Column(Float, default=0.25)
    transportation_cost = Column(Float, default=1.0)
    stockout_cost = Column(Float, default=10.0)
    last_optimization = Column(DateTime, default=_utcnow)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class ProductionSite(Base):
    __tablename__ = "production_sites"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    site_id = Column(String, unique=True, index=True)
    site_name = Column(String)
    location = Column(String)
    site_type = Column(String)  # manufacturing, assembly, distribution
    total_capacity = Column(Float, default=0)
    fixed_cost = Column(Float, default=0)
    variable_cost = Column(Float, default=0)
    capabilities = Column(JSON, nullable=True)  # List of SKUs or categories
    lead_time_days = Column(Integer, default=7)
    quality_score = Column(Float, default=1.0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class MultiSitePlan(Base):
    __tablename__ = "multi_site_plans"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    plan_name = Column(String, index=True)
    planning_horizon = Column(Integer)
    site_allocations = Column(JSON)  # SKU -> site -> quantity
    transfer_plan = Column(JSON, nullable=True)  # Transfer quantities between sites
    total_cost = Column(Float, default=0)
    optimization_criteria = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String, default="draft")  # draft, approved, active
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)

class SupplierCapacity(Base):
    __tablename__ = "supplier_capacities"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    supplier_id = Column(String, index=True)
    supplier_name = Column(String)
    total_capacity = Column(Float, default=0)
    allocated_capacity = Column(Float, default=0)
    remaining_capacity = Column(Float, default=0)
    lead_time_days = Column(Integer, default=7)
    quality_score = Column(Float, default=1.0)
    cost_per_unit = Column(Float, default=0)
    reliability_score = Column(Float, default=100)
    capacity_allocation = Column(JSON, nullable=True)  # SKU -> allocated quantity
    effective_date = Column(DateTime, index=True)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class TransportationRoute(Base):
    __tablename__ = "transportation_routes"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    route_id = Column(String, unique=True, index=True)
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    distance_km = Column(Float, default=0)
    cost_per_km = Column(Float, default=0)
    transit_time_hours = Column(Float, default=0)
    capacity = Column(Float, default=0)
    vehicle_type = Column(String, nullable=True)
    carrier = Column(String, nullable=True)
    service_level = Column(String, default="standard")  # standard, expedited, economy
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class TransportationPlan(Base):
    __tablename__ = "transportation_plans"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    plan_name = Column(String, index=True)
    shipment_details = Column(JSON)  # List of shipments with routes
    total_cost = Column(Float, default=0)
    total_distance = Column(Float, default=0)
    optimization_constraints = Column(JSON, nullable=True)
    planned_shipment_date = Column(DateTime, nullable=True)
    status = Column(String, default="planned")  # planned, in_transit, delivered, cancelled
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)

class RoughCutCapacityPlan(Base):
    __tablename__ = "rough_cut_capacity_plans"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    plan_name = Column(String, index=True)
    planning_horizon_months = Column(Integer)
    resource_requirements = Column(JSON)  # Monthly resource requirements
    capacity_analysis = Column(JSON)  # Capacity gap analysis
    monthly_capacity_plan = Column(JSON)  # Month-by-month capacity status
    assumptions = Column(JSON, nullable=True)  # Growth rates, efficiency assumptions
    recommendations = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    resource_id = Column(String, unique=True, index=True)
    resource_name = Column(String)
    resource_type = Column(String, index=True)  # labor, machine, storage, transportation
    location = Column(String, nullable=True)
    capacity_per_period = Column(Float, default=0)  # Hours, units, etc.
    efficiency = Column(Float, default=1.0)
    cost_per_hour = Column(Float, default=0)
    availability = Column(Float, default=1.0)
    skills = Column(JSON, nullable=True)  # For labor resources
    specifications = Column(JSON, nullable=True)  # For equipment
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

# Incident Management Models

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    incident_id = Column(String, unique=True, index=True)
    incident_type = Column(String, index=True)  # supply_disruption, quality_issue, delay, system_outage
    severity = Column(String, index=True)  # critical, high, medium, low
    priority = Column(String, default="medium")  # critical, high, medium, low
    status = Column(String, index=True, default="open")  # open, acknowledged, investigating, resolved, closed
    title = Column(String)
    description = Column(Text)
    affected_entities = Column(JSON, nullable=True)  # SKUs, suppliers, warehouses, etc.
    impact_assessment = Column(JSON, nullable=True)  # Financial, operational impact
    root_cause = Column(Text, nullable=True)
    assigned_to = Column(String, nullable=True)
    assigned_team = Column(String, nullable=True)
    escalation_level = Column(Integer, default=0)  # 0=None, 1=Team Lead, 2=Manager, 3=Director
    estimated_resolution_date = Column(DateTime, nullable=True)
    actual_resolution_date = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    prevention_actions = Column(JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

class IncidentTimeline(Base):
    __tablename__ = "incident_timelines"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    incident_id = Column(String, index=True)
    action = Column(String)  # created, acknowledged, assigned, updated, escalated, resolved, closed
    action_type = Column(String)  # status_change, assignment, note, escalation
    description = Column(Text)
    performed_by = Column(String, nullable=True)
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)  # Links to documents, screenshots
    created_at = Column(DateTime, default=_utcnow)

class IncidentWorkflow(Base):
    __tablename__ = "incident_workflows"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    workflow_name = Column(String, index=True)
    incident_type = Column(String, index=True)
    severity = Column(String, index=True)
    workflow_steps = Column(JSON)  # Ordered list of workflow steps
    approval_required = Column(Integer, default=0)  # 1 if approval required
    approvers = Column(JSON, nullable=True)  # List of approver roles/user IDs
    escalation_rules = Column(JSON, nullable=True)  # Auto-escalation rules
    sla_minutes = Column(Integer, nullable=True)  # SLA for resolution
    notification_settings = Column(JSON, nullable=True)  # Who to notify
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class IncidentTemplate(Base):
    __tablename__ = "incident_templates"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    template_name = Column(String, unique=True, index=True)
    incident_type = Column(String, index=True)
    template_description = Column(Text, nullable=True)
    default_severity = Column(String, default="medium")
    default_priority = Column(String, default="medium")
    required_fields = Column(JSON, nullable=True)  # Required information fields
    suggested_actions = Column(JSON, nullable=True)  # Pre-defined action items
    team_assignments = Column(JSON, nullable=True)  # Default team assignments
    communication_template = Column(Text, nullable=True)  # Default communication message
    is_active = Column(Integer, default=1)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

class IncidentEscalation(Base):
    __tablename__ = "incident_escalations"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    incident_id = Column(String, index=True)
    escalation_level = Column(Integer, default=0)
    escalated_from = Column(String, nullable=True)  # User/role escalating
    escalated_to = Column(String, nullable=True)  # User/role receiving escalation
    escalation_reason = Column(Text, nullable=True)
    escalation_time = Column(DateTime, default=_utcnow)
    acknowledged = Column(Integer, default=0)  # 1 if acknowledged
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

class IncidentSLA(Base):
    __tablename__ = "incident_slas"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default", nullable=False)
    incident_type = Column(String, index=True)
    severity = Column(String, index=True)
    response_time_minutes = Column(Integer, default=60)  # Time to first response
    acknowledgement_time_minutes = Column(Integer, default=30)  # Time to acknowledge
    resolution_time_minutes = Column(Integer, default=480)  # Time to resolve
    update_frequency_minutes = Column(Integer, default=240)  # Frequency of status updates
    breach_notification = Column(JSON, nullable=True)  # Who to notify on breach
    working_hours_only = Column(Integer, default=0)  # 1 if only business hours count
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


# ── Phase 1.2: Agentic mitigation loop tables ─────────────────────────────

class PendingAction(Base):
    """
    An AI-proposed mitigation action awaiting human approval.

    Lifecycle: awaiting_approval → approved | rejected → executed | failed
    The frontend renders these as approval cards in the agents feed.
    """
    __tablename__ = "pending_actions"

    id             = Column(Integer, primary_key=True, index=True)
    run_id         = Column(String, index=True, nullable=False)   # agent run UUID
    supplier       = Column(String, index=True, nullable=False)
    sku            = Column(String, nullable=True)
    trigger_score  = Column(Float, nullable=False)                # risk score that triggered the run
    action_type    = Column(String, nullable=False)               # dual_source | reroute | safety_stock | alert
    action_summary = Column(Text, nullable=False)                 # one-line human-readable summary
    action_detail  = Column(JSON, nullable=True)                  # full structured payload from LLM
    backup_suppliers = Column(JSON, nullable=True)                # [{name, risk_score, estimated_cost_delta}]
    monte_carlo_summary = Column(JSON, nullable=True)             # {p50_delay_reduction, p90_cost_impact}
    rag_context    = Column(JSON, nullable=True)                  # [{doc_name, excerpt, relevance_score}]
    llm_reasoning  = Column(Text, nullable=True)                  # raw LLM reasoning chain
    status         = Column(String, index=True, default="awaiting_approval")
    approved_by    = Column(String, nullable=True)
    approved_at    = Column(DateTime, nullable=True)
    executed_at    = Column(DateTime, nullable=True)
    execution_log  = Column(Text, nullable=True)
    created_at     = Column(DateTime, default=_utcnow)


# ── Graph failure simulation history ───────────────────────────────────────

class ScenarioRun(Base):
    """
    Persists every graph failure simulation run.
    Shown on the Risk Propagation page as a history of what-if analyses.
    Created by POST /graph/simulate-failure.
    """
    __tablename__ = "scenario_runs"

    id                   = Column(Integer, primary_key=True, index=True)
    run_id               = Column(String, unique=True, index=True, nullable=False)
    node_id              = Column(String, nullable=False)           # e.g. "supplier:Apex Materials"
    node_name            = Column(String, nullable=False)
    node_type            = Column(String, nullable=False)           # supplier | sku | warehouse | region
    pre_betweenness      = Column(JSON, nullable=True)              # top-20 before removal
    post_betweenness     = Column(JSON, nullable=True)              # top-20 after removal
    pre_pagerank         = Column(JSON, nullable=True)
    post_pagerank        = Column(JSON, nullable=True)
    newly_critical_nodes = Column(JSON, nullable=True)              # nodes whose centrality jumped
    unreachable_skus     = Column(JSON, nullable=True)              # SKUs with no remaining supplier
    affected_regions     = Column(JSON, nullable=True)              # regions downstream of failed node
    cascade_result       = Column(JSON, nullable=True)              # full cascade output
    total_affected       = Column(Integer, default=0)
    risk_assessment      = Column(String, default="contained")      # contained|significant|severe|catastrophic
    created_by           = Column(String, default="system")
    created_at           = Column(DateTime, default=_utcnow)
