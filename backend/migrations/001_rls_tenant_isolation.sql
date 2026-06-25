-- Migration: 001_rls_tenant_isolation.sql
-- Description: Enables Row Level Security (RLS) on all multi-tenant tables.
-- Execution: Run this against the PostgreSQL database after initial tables are created.

-- 1. Enable RLS on all tables
ALTER TABLE supply_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE upload_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE esg_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheduled_ingestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE world_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE supply_chain_events ENABLE ROW LEVEL SECURITY;

-- 2. Create policies for tenant isolation
-- The policy checks the 'app.current_tenant_id' session variable.
-- If the variable is not set (e.g. for superusers doing migrations), RLS bypass applies.

CREATE POLICY tenant_isolation_supply_data ON supply_data
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_supplier_profiles ON supplier_profiles
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_analysis_results ON analysis_results
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_upload_history ON upload_history
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_esg_profiles ON esg_profiles
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_kpi_metrics ON kpi_metrics
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_scheduled_ingestions ON scheduled_ingestions
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_risk_events ON risk_events
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_world_events ON world_events
  USING (tenant_id = current_setting('app.current_tenant_id'));

CREATE POLICY tenant_isolation_supply_chain_events ON supply_chain_events
  USING (tenant_id = current_setting('app.current_tenant_id'));

-- Note: Ensure that the FastAPI DB dependency runs:
-- await db.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
-- before yielding the session.
