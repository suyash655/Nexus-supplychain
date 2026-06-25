# Data Model — Project Nexus

## Entity Relationship Overview

```
UploadHistory ──┐
                ▼
           SupplyData ──────── SupplierProfile
                │                    │
                ▼                    ▼
         AnalysisResult          ESGProfile
                │
                ├──► RiskEvent
                └──► KPIMetric

User ──► APIKey
User ──► AuditLog
WorldEvent  (standalone, no FK to Supply)
ScheduledIngestion  (standalone, scheduler config)
```

---

## Tables

### `supply_data`

Core fact table. Each row is one record from an uploaded file.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `upload_id` | VARCHAR | Groups rows from the same upload batch |
| `supplier_name` | VARCHAR | Supplier entity name |
| `product_category` | VARCHAR | Product or commodity category |
| `country_of_origin` | VARCHAR | ISO country code or name |
| `lead_time_days` | FLOAT | Average lead time in days |
| `unit_cost` | FLOAT | Per-unit cost (USD) |
| `order_quantity` | FLOAT | Units ordered |
| `on_time_delivery_rate` | FLOAT | 0.0–1.0 delivery reliability |
| `defect_rate` | FLOAT | Quality defect ratio |
| `risk_score` | FLOAT | Computed ML risk score (0–100) |
| `risk_level` | VARCHAR | `low` / `medium` / `high` / `critical` |
| `anomaly_flag` | BOOLEAN | Isolation Forest anomaly flag |
| `created_at` | DATETIME | Row creation timestamp |

---

### `supplier_profiles`

Enriched per-supplier metadata, updated across uploads.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `name` | VARCHAR UNIQUE | Canonical supplier name |
| `country` | VARCHAR | Country of operation |
| `tier` | INTEGER | Supply chain tier (1 = direct) |
| `reliability_score` | FLOAT | Historical OTIF-based score |
| `esg_score` | FLOAT | Composite ESG score |
| `risk_level` | VARCHAR | Current risk classification |
| `last_updated` | DATETIME | |

---

### `analysis_results`

One row per analysis run; links back to the upload batch.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `upload_id` | VARCHAR | FK (logical) to `supply_data.upload_id` |
| `risk_level` | VARCHAR | Aggregate risk for this batch |
| `total_records` | INTEGER | Records analyzed |
| `high_risk_count` | INTEGER | Records flagged high/critical |
| `recommendations` | TEXT (JSON) | AI-generated action list |
| `causal_dag` | TEXT (JSON) | Serialized Bayesian DAG |
| `graph_metrics` | TEXT (JSON) | Network centrality + community data |
| `created_at` | DATETIME | |

---

### `risk_events`

Time-series event log for supplier risk signals.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `supplier_id` | INTEGER | FK → `supplier_profiles.id` |
| `event_type` | VARCHAR | `delay` / `quality` / `financial` / `geopolitical` |
| `severity` | VARCHAR | `low` / `medium` / `high` / `critical` |
| `description` | TEXT | Event narrative |
| `impact_score` | FLOAT | Estimated business impact (0–100) |
| `event_date` | DATETIME | When the event occurred |
| `created_at` | DATETIME | When it was logged |

---

### `world_events`

External disruption events (geopolitical, climate, pandemic) mapped to regions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `event_type` | VARCHAR | `geopolitical` / `natural_disaster` / `pandemic` / `economic` |
| `region` | VARCHAR | Affected geographic region |
| `impact_score` | FLOAT | Severity score 0–100 |
| `description` | TEXT | Event summary |
| `event_date` | DATE | Date of occurrence |

---

### `esg_profiles`

Per-supplier ESG compliance scores.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `supplier_id` | INTEGER | FK → `supplier_profiles.id` |
| `environmental_score` | FLOAT | Carbon, waste, water (0–100) |
| `social_score` | FLOAT | Labor, safety, community (0–100) |
| `governance_score` | FLOAT | Transparency, compliance (0–100) |
| `composite_score` | FLOAT | Weighted average |
| `compliance_flags` | TEXT (JSON) | List of failing checks |
| `assessed_at` | DATETIME | |

---

### `kpi_metrics`

Tracked KPI values per upload batch.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `upload_id` | VARCHAR | Batch reference |
| `metric_name` | VARCHAR | e.g. `otif_rate`, `inventory_turnover` |
| `value` | FLOAT | Computed metric value |
| `benchmark` | FLOAT | Industry benchmark |
| `delta` | FLOAT | Change vs. previous period |
| `alert_level` | VARCHAR | `ok` / `warning` / `critical` |
| `computed_at` | DATETIME | |

---

### `scheduled_ingestions`

Configured data ingestion schedules.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `name` | VARCHAR | Human-readable schedule name |
| `source_type` | VARCHAR | `csv` / `api` / `s3` / `erp` |
| `connection_config` | TEXT (JSON) | Source credentials / URL |
| `cron_expression` | VARCHAR | e.g. `0 6 * * *` |
| `is_active` | BOOLEAN | Enable / disable |
| `last_run_at` | DATETIME | |
| `next_run_at` | DATETIME | |

---

### `users`

Authentication principals.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `email` | VARCHAR UNIQUE | Login identifier |
| `hashed_password` | VARCHAR | bcrypt hash |
| `full_name` | VARCHAR | |
| `role` | VARCHAR | `admin` / `analyst` / `viewer` |
| `is_active` | BOOLEAN | Account enabled |
| `created_at` | DATETIME | |

---

### `api_keys`

Machine-to-machine access tokens.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `user_id` | INTEGER | FK → `users.id` |
| `key_hash` | VARCHAR | SHA-256 of the raw key |
| `name` | VARCHAR | Key label |
| `expires_at` | DATETIME | Nullable = no expiry |
| `is_active` | BOOLEAN | |

---

### `audit_logs`

Immutable event trail for compliance.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `user_id` | INTEGER | FK → `users.id` |
| `action` | VARCHAR | `upload` / `analyze` / `export` / `login` etc. |
| `entity_type` | VARCHAR | Model name affected |
| `entity_id` | VARCHAR | ID of affected record |
| `details` | TEXT (JSON) | Action parameters |
| `ip_address` | VARCHAR | Client IP |
| `timestamp` | DATETIME | |

---

## JSON Blobs

Several columns store JSON-serialized complex objects:

- **`analysis_results.recommendations`** — array of `{action, priority, supplier, rationale}`
- **`analysis_results.causal_dag`** — `{nodes: [], edges: [{from, to, strength}]}`
- **`analysis_results.graph_metrics`** — `{centrality: {}, communities: [], diameter: int}`
- **`esg_profiles.compliance_flags`** — array of `{check, status, threshold, actual}`
- **`scheduled_ingestions.connection_config`** — source-specific config dict
