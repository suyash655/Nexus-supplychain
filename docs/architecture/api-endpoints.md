# API Endpoints — Project Nexus

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`  
Auth: `Authorization: Bearer <jwt_token>` on all protected routes.

---

## Authentication

### `POST /auth/login`
Login and receive a JWT access token.

**Body**
```json
{ "username": "user@example.com", "password": "secret" }
```
**Response**
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### `POST /auth/register`
Register a new user (admin only in production).

### `GET /auth/me`
Returns the current authenticated user's profile.

---

## Upload

### `POST /upload`
**Auth required.** Upload CSV or XLSX supply chain data. Auto-detects column mappings (3-strategy fuzzy matching). Triggers background analysis immediately after ingestion.

**Form Fields**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | ✅ | CSV or XLSX file |
| `mapping` | JSON string | ❌ | Manual column override map |

**Response**
```json
{
  "status": "success",
  "rows_inserted": 1500,
  "rows_rejected": 3,
  "column_mapping": { "supplier": "Vendor Name", "cost": "Invoice Amount" },
  "data_quality": {
    "total_rows": 1503,
    "missing_values": { "delay_days": 12 }
  },
  "message": "Upload successful. Analysis started in background."
}
```

### `POST /upload/preview`
Preview 10 rows and auto-detected column map without importing data.

**Response**
```json
{
  "columns": ["Vendor Name", "Invoice Amount", "Delay (Days)"],
  "auto_mapping": { "supplier": "Vendor Name", "cost": "Invoice Amount" },
  "preview_rows": [...]
}
```

### `GET /upload/columns`
**Auth required.** Returns columns + mapping from the most recent upload.

### `POST /upload/confirm`
**Auth required.** Re-trigger analysis with the confirmed column mapping.

---

## Analytics

### `GET /analytics/summary`
Full risk summary dashboard data — KPIs, top risks, alerts, trends.

**Response** (abbreviated)
```json
{
  "risk_level": "high",
  "total_suppliers": 47,
  "high_risk_count": 8,
  "avg_risk_score": 62.4,
  "kpis": { "otif_rate": 0.87, "avg_lead_time": 14.2 },
  "top_risks": [{ "supplier": "Acme Corp", "risk_score": 91, "risk_tier": "critical" }],
  "alerts": [{ "type": "delay_spike", "severity": "high", "supplier": "Acme Corp" }]
}
```

### `GET /analytics/risk-scores`
Paginated list of all supplier risk scores.

**Query params:** `page`, `page_size`, `min_risk`

### `GET /analytics/trends`
Historical risk trend data for charting.

### `GET /analytics/alerts`
Active alert events sorted by severity.

---

## ML / Predictions

### `GET /ml/predictions`
Raw ML model output — risk scores + anomaly flags per supplier.

**Response**
```json
{
  "risk_scores": [
    { "supplier": "Acme Corp", "risk_score": 91, "tier": "critical", "anomaly": true }
  ],
  "anomalies": {
    "count": 12,
    "anomalies": [{ "supplier": "...", "reason": "IQR outlier on delay_days" }]
  },
  "forecast": {
    "next_30_days": [{ "date": "2025-11-01", "predicted_demand": 1204 }]
  }
}
```

### `GET /ml/anomalies`
Returns only records flagged as anomalies by the Isolation Forest.

### `GET /ml/forecast`
Holt-Winters demand forecast for the next 30 days.

---

## Graph / Network

### `GET /graph/topology`
Full supply chain network graph (nodes + edges + centrality metrics).

**Response**
```json
{
  "nodes": [{ "id": "Acme Corp", "risk_score": 91, "centrality": 0.73, "tier": 1 }],
  "edges": [{ "source": "Acme Corp", "target": "Warehouse A", "weight": 0.8 }],
  "metrics": { "diameter": 4, "avg_clustering": 0.31, "density": 0.18 }
}
```

### `GET /graph/centrality`
Betweenness, degree, and eigenvector centrality per node.

### `GET /graph/communities`
Community detection result (Louvain algorithm).

### `POST /graph/simulate-failure`
Simulate cascade failure from removing a specific node.

**Body:** `{ "node": "Acme Corp", "strategy": "remove" }`

**Response:** Affected nodes + propagation depth.

---

## AI Co-Pilot

### `POST /copilot/query`
Natural language query against the supply chain data.

**Body**
```json
{ "query": "Which suppliers have the highest risk of delay next month?" }
```

**Response**
```json
{
  "answer": "Based on current data, three suppliers are at elevated risk...",
  "sources": ["risk_scores", "graph_centrality"],
  "confidence": 0.87,
  "reasoning_steps": [...]
}
```

### `GET /copilot/health-summary`
Auto-generated executive health summary for the current dataset.

### `POST /copilot/what-if`
What-If scenario via natural language.

**Body:** `{ "scenario": "What if Acme Corp delays by 2 weeks?" }`

---

## Causal Genome

### `POST /causal/build`
Build the Bayesian Causal DAG from the current graph + risk data + world events.

**Response**
```json
{
  "nodes": 23, "edges": 41,
  "fragility_index": 0.74,
  "message": "Causal genome built successfully"
}
```

### `GET /causal/intervene`
Run an interventional query (do-calculus): remove/reduce a node and see downstream effects.

**Query params:** `target=Acme Corp`, `action=remove`

**Response**
```json
{
  "target": "Acme Corp",
  "action": "remove",
  "downstream_effects": [{ "node": "Warehouse A", "risk_delta": +0.34 }],
  "risk_change": +18.5,
  "recommendation": "Activate alternate supplier B"
}
```

### `GET /causal/chain`
Get the causal chain between two nodes.

**Query params:** `from=Port Shanghai`, `to=Distribution Center EU`

### `GET /causal/fragility`
Full Taleb-inspired fragility report with vulnerability index per node.

---

## XAI (Explainability)

### `GET /xai/feature-importance`
SHAP-style feature importance scores for the risk model.

**Response**
```json
{
  "delay_days": 0.38, "cost": 0.22, "quality_score": 0.19,
  "region": 0.11, "quantity": 0.10
}
```

### `GET /xai/counterfactuals`
Counterfactual examples: "What would need to change to move Acme Corp from critical → medium?"

---

## ESG

### `GET /esg/report`
Full ESG report for all suppliers in the current dataset.

**Response**
```json
{
  "overall_score": 64.2,
  "suppliers": [
    { "name": "Acme Corp", "environmental": 58, "social": 71, "governance": 60, "composite": 63 }
  ],
  "compliance_flags": [{ "supplier": "Acme Corp", "check": "carbon_disclosure", "status": "fail" }]
}
```

### `GET /esg/emissions`
Estimated carbon emissions per supplier (scope 3 estimation).

### `GET /esg/compliance`
Compliance screen against configurable ESG thresholds.

---

## Contract Intelligence

### `POST /contracts/upload`
Upload a contract PDF/TXT for NLP risk analysis.

**Form:** `file` (binary), `doc_type` (default: `contract`)

### `POST /contracts/upload-text`
Ingest contract text directly.

**Body:** `{ "name": "Acme SLA 2025", "content": "...", "doc_type": "sla" }`

### `POST /contracts/query`
Semantic search over ingested contracts.

**Body:** `{ "question": "What is the penalty clause for late delivery?", "top_k": 5 }`

### `GET /contracts/documents`
List all ingested contract documents.

### `GET /contracts/clauses/{document_id}`
Get extracted clause summary for a specific contract.

### `DELETE /contracts/{document_id}`
Delete a contract from the system.

---

## Agents

### `POST /agents/run`
Run the full autonomous agent pipeline (risk monitoring → incident creation → recommendations).

### `GET /agents/status`
Current status of all active agents.

### `GET /agents/incidents`
List all agent-detected incidents.

**Query params:** `status=open|resolved|pending_approval`

### `GET /agents/incidents/{incident_id}`
Get full incident detail + recommended actions.

### `POST /agents/incidents/{incident_id}/approve`
Approve an agent recommendation (human-in-the-loop).

**Query param:** `approved_by=procurement_officer`

### `GET /agents/audit-log`
Full immutable audit trail of all agent actions.

### `PUT /agents/thresholds`
Update agent alert thresholds.

**Body:** `{ "risk_score_critical": 80, "delay_days_alert": 5 }`

---

## Scheduler

### `POST /scheduler/jobs`
Create a new scheduled ingestion job.

**Body**
```json
{
  "name": "Daily ERP Sync",
  "schedule": "daily_6am",
  "connector_type": "api",
  "connector_config": { "url": "https://erp.company.com/supply/export" }
}
```

### `GET /scheduler/jobs`
List all configured jobs with next-run timestamps.

### `PUT /scheduler/jobs/{job_id}`
Update a scheduled job (schedule, config, active status).

### `DELETE /scheduler/jobs/{job_id}`
Delete a scheduled job.

### `POST /scheduler/jobs/{job_id}/trigger`
Manually trigger a job immediately.

### `GET /scheduler/history`
Ingestion run history with row counts and quality scores.

### `GET /scheduler/presets`
Available schedule presets (`every_15_minutes`, `hourly`, `daily_6am`, `weekly_monday`, `monthly_first`).

---

## Connectors

### `GET /connectors/types`
Available connector types (CSV, SQL Database, Cloud Storage, REST API).

### `GET /connectors`
List all configured connector instances.

### `POST /connectors`
Create a new connector configuration.

### `POST /connectors/{connector_id}/test`
Test connector connectivity and return status.

---

## Pipeline & Data Quality

### `POST /pipeline/quality-check`
Run data quality checks on the current dataset.

**Response**
```json
{
  "quality_score": 0.91,
  "checks": {
    "missing_values": "pass",
    "duplicates": "pass",
    "outliers": "warning",
    "schema_validation": "pass"
  },
  "issues": [{ "column": "delay_days", "issue": "12 outliers detected", "severity": "warning" }]
}
```

### `GET /pipeline/history`
Last 20 pipeline run records.

### `GET /pipeline/lineage`
Data lineage records — source → transformation → target column mapping.

---

## Export

### `GET /export/csv`
Export full dataset with computed risk scores as CSV (Tableau-compatible).

### `GET /export/json`
Export analysis results as JSON (Power BI-compatible).

### `GET /export/tableau-schema`
Tableau schema descriptor for direct data source configuration.

---

## System

### `GET /system/health`
Platform health status — module states, DB stats, last analysis timestamp.

**Response**
```json
{
  "status": "healthy",
  "platform": "NEXUS",
  "version": "3.0.0",
  "modules": { "ml": "active", "graph": "active", "ai_copilot": "active" },
  "stats": { "users": 3, "connectors": 2, "pipeline_runs": 47 },
  "last_analysis": "2025-10-31T06:12:00Z"
}
```

### `DELETE /system/reset`
⚠️ **Destructive.** Clears all supply data, upload history, risk events, and analysis results from the database.

### `GET /` (root)
Basic liveness check — returns API status and timestamp.
