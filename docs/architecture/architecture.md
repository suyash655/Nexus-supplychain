# Architecture — Project Nexus

## System Overview

Nexus is a layered AI platform. Each layer has a single responsibility and communicates only with the layer directly below it.

```
┌─────────────────────────────────────────────────┐
│  Presentation Layer  (Next.js 14 / TypeScript)  │
├─────────────────────────────────────────────────┤
│  API Gateway Layer   (FastAPI / Python 3.10)    │
├─────────────────────────────────────────────────┤
│  Engine Layer        (AI / ML / Graph Engines)  │
├─────────────────────────────────────────────────┤
│  Data Layer          (SQLAlchemy / SQLite / PG) │
└─────────────────────────────────────────────────┘
```

---

## Layer 1 — Presentation (Frontend)

**Stack:** Next.js 14 App Router · TypeScript · Vanilla CSS (design tokens)

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/` | KPI cards, risk heatmap, live graph |
| Demo | `/demo` | Interactive upload + analysis |
| Explainability | `/explainability` | XAI attribution charts |
| Evaluation | `/evaluation` | Model metrics and benchmarks |

**Frontend → Backend communication:** REST + JSON over HTTP.  
All API calls are encapsulated in `frontend/lib/api.ts` — components never call `fetch` directly.

---

## Layer 2 — API Gateway (FastAPI)

**Entry point:** `backend/app/main.py`

Responsibilities:
- Register all routers via `app.include_router(...)`
- Instantiate engine singletons (one per process)
- Configure CORS middleware with `settings.CORS_ORIGINS`
- Provide `SafeJSONResponse` to neutralize `NaN`/`Inf` floats
- Start / stop the `DataScheduler` background loop on lifespan events

### Router Map

| File | Prefix | Handles |
|------|--------|---------|
| `routers/upload.py` | `/upload` | CSV/XLSX ingestion, data cleaning |
| `routers/analytics.py` | `/analytics` | Risk summary, KPIs, alerts |
| `routers/graph.py` | `/graph` | Network topology, centrality, paths |
| `routers/copilot.py` | `/copilot` | LLM natural-language queries |
| `routers/ml.py` | `/ml` | Raw ML predictions, uncertainty |
| `routers/auth_routes.py` | `/auth` | Login, token refresh, user CRUD |
| `routers/remaining.py` | various | XAI, export, causal, agents, ESG, contracts, scheduler |

### Dependency Injection

`core/dependencies.py` provides:
- `get_db()` — yields `SessionLocal` database session
- `get_current_user()` — validates JWT and returns user record
- `require_admin()` — role-gated guard

---

## Layer 3 — Engine Layer

Engines are **stateful singletons** initialized once at startup. They hold no HTTP state; each method call is independent.

### SupplyChainAnalyzer (`engines/analyzer.py`)

Three-stage risk pipeline:
1. **Isolation Forest** — anomaly detection on numerical KPIs
2. **Holt-Winters** — exponential smoothing for demand forecasting
3. **IQR statistical bounds** — rule-based threshold alerts

### SupplyChainGraph (`engines/graph_engine.py`)

- Builds a `networkx.DiGraph` from supplier-buyer relationships
- Computes degree, betweenness, and eigenvector centrality
- Detects communities (Louvain method)
- Simulates cascade failures via node removal

### TGNNEngine (`engines/tgnn_engine.py`)

- Temporal Graph Neural Network over rolling time windows
- Node embeddings updated per time step
- Predicts next-period supply disruption probability
- Identifies **latent bottlenecks** invisible to static models

### CausalGenomeEngine (`causal/`)

- Bayesian Directed Acyclic Graph (DAG) inference
- Supports interventional queries: `do(X=x)` → effect on `Y`
- Counterfactual "What-If" simulations
- ~94% fidelity against historical disruption outcomes

### AICopilot (`engines/ai_copilot.py`)

- LLM-backed natural language interface
- Provider abstraction: `groq` → `bedrock` → `offline`
- Context injection: live KPIs + graph summary → prompt
- Returns structured JSON reasoning + executive narrative

### MonteCarloEngine (`engines/monte_carlo.py`)

- Stochastic disruption cost simulations (10,000 trials default)
- Output: probability distribution over disruption scenarios
- Used for: supplier diversification ROI analysis

### ESGEngine (`engines/esg_engine.py`)

- Scores suppliers on Environmental, Social, Governance dimensions
- Automated compliance flagging against configurable thresholds
- Generates audit-ready ESG reports

### KPIEngine (`engines/kpi_engine.py`)

- Tracks: OTIF, lead time, inventory turnover, supplier fill rate
- Anomaly alerting with severity levels (critical / warning / info)
- Historical trend computation with delta comparisons

### ContractIntelligence (`engines/contract_intelligence.py`)

- NLP extraction of key contract terms (SLAs, penalties, force majeure)
- Risk scoring per contract clause
- Cross-contract inconsistency detection

### DataScheduler (`engines/scheduler.py`)

- Background thread that runs ingestion jobs on cron schedules
- Configurable via `ScheduledIngestion` DB records
- Integrates with `connectors/` for external data pulls

---

## Layer 4 — Data Layer

### ORM Models (`models/`)

| Model | Table | Key Fields |
|-------|-------|-----------|
| `SupplyData` | `supply_data` | supplier, product, cost, lead_time, risk_score |
| `SupplierProfile` | `supplier_profiles` | name, country, tier, esg_score |
| `AnalysisResult` | `analysis_results` | upload_id, risk_level, recommendations |
| `RiskEvent` | `risk_events` | supplier_id, event_type, severity, timestamp |
| `WorldEvent` | `world_events` | type, region, impact_score, date |
| `User` | `users` | email, hashed_password, role |
| `AuditLog` | `audit_logs` | user_id, action, entity, timestamp |

### Database Configuration

- **Development:** SQLite with WAL journal mode for concurrent read/write
- **Production:** PostgreSQL (set `DATABASE_URL` env var)
- **Connection pooling:** `pool_recycle=300s` prevents stale handles

---

## Cross-Cutting Concerns

### Authentication
JWT (HS256). Tokens expire per `ACCESS_TOKEN_EXPIRE_MINUTES` (default 720 min).  
All non-public routes require `Authorization: Bearer <token>` header.

### Error Handling
`SafeJSONResponse` (in `main.py`) intercepts `NaN`/`Inf` float values and replaces them with `null` before serialization — prevents client-side JSON parse failures from ML outputs.

### Configuration
All settings centralized in `core/config.py` via `Settings` class. Values sourced from environment variables; `.env` file supported via `python-dotenv`.

### Data Quality
`pipeline/` (`DataQualityEngine`) runs before ML analysis:
- Missing value detection and imputation strategy selection
- Outlier flagging
- Schema validation
- Quality score: `DATA_QUALITY_THRESHOLD` (default 0.85) gates analysis

---

## Request Lifecycle (Upload → Analyze)

```
1.  POST /upload  (multipart/form-data, CSV or XLSX)
        │
2.  upload.py router
        │  validates file type + size
        │  delegates to services/data_ingestion.py
        │
3.  data_ingestion.py
        │  parses → DataFrame
        │  cleans + normalizes
        │  persists → SupplyData rows
        │  triggers DataQualityEngine score
        │
4.  POST /analyze  (with upload_id)
        │
5.  core/orchestrator.py  (coordinates all engines)
        │
        ├─► SupplyChainAnalyzer.run()      → risk_scores[]
        ├─► SupplyChainGraph.build()       → graph topology
        ├─► TGNNEngine.predict()           → disruption_probs[]
        ├─► CausalGenomeEngine.fit()       → causal_dag
        ├─► KPIEngine.compute()            → kpi_metrics{}
        └─► ESGEngine.score()              → esg_scores{}
                │
6.  AnalysisResult persisted → DB
        │
7.  JSON response → Frontend dashboard
```

---

## Scalability Notes

- **Horizontal scaling:** Stateless routers; engine singletons can be moved to worker processes via Celery if needed.
- **Database:** SQLite adequate for demo/dev. Switch `DATABASE_URL` to PostgreSQL for production; no code changes required.
- **LLM cost control:** `offline` provider mode available — returns cached/template responses without API calls.
- **Caching:** Redis integration points available in `core/config.py`; currently used for session storage; extend to engine result caching as needed.
