# Claims and Architecture Audit

Recorded: 2026-11-15  
Repository: `suyash655/Nexus-supplychain`  
Author: Suyash Jaysawal  

---

## 1. Claims Verification Table

| Claim | Status | File & Line Evidence | Details / Ground Truth |
| :--- | :--- | :--- | :--- |
| **30 API route modules; +20 more engines** | **PARTIAL** | `backend/app/main.py:422-451`<br/>`backend/app/routers/`<br/>`backend/app/engines/` | **29 routers** are mounted in `main.py` (`rag_router` is commented out at line 431). Route files in `routers/` number 20. There are **12 engine files** in `engines/` + 1 causal engine + 1 demand engine. Claiming "+20 more engines" is an exaggeration; total engines is ~14. |
| **6-node LangGraph agent** | **PARTIAL** | `backend/agent/mitigation_graph.py:548-560`<br/>`backend/agent/mitigation_graph.py:473-535` | The compiled `StateGraph` contains **5 nodes**: `get_backup_suppliers`, `simulate_reroute_cost`, `retrieve_context`, `draft_action`, `write_pending_action`. A 6th function `node_execute_action` exists as the human-approved execution handler executed post-approval outside the graph. |
| **ChromaDB RAG over past incidents** | **VERIFIED** | `backend/rag/ingest.py:38,111-125`<br/>`data/documents/`<br/>`backend/agent/tools.py:18-43` | File-backed ChromaDB (`data/chroma_db`) stores embeddings (`all-MiniLM-L6-v2`) over 5 synthetic supply chain incident/policy documents in `data/documents/` (`Apex_Materials_SLA.txt`, `GlobalTech_Incident_Report_2024.txt`, etc.). Querying is integrated via `agent/tools.py:retrieve_documents()`. |
| **Isolation Forest, Holt-Winters, DBSCAN, composite risk score, Monte Carlo** | **PARTIAL** | `backend/app/engines/analyzer.py:127,216`<br/>`backend/app/engines/forecaster.py:290`<br/>`backend/app/engines/monte_carlo.py:16` | **Isolation Forest**: VERIFIED (`analyzer.py:127`).<br/>**Holt-Winters**: VERIFIED (`forecaster.py:290`).<br/>**Composite risk score**: VERIFIED (`analyzer.py:216`).<br/>**Monte Carlo**: VERIFIED (`monte_carlo.py:16`).<br/>**DBSCAN**: **NOT FOUND** (0 occurrences in backend code; mentioned only in README/ARCHITECTURE). |
| **NetworkX centrality, cascade simulation, failure-impact scoring** | **VERIFIED** | `backend/app/engines/graph_engine.py:363-413`<br/>`backend/app/engines/graph_engine.py:416-478`<br/>`backend/app/engines/graph_engine.py:657-752` | Full implementation using NetworkX: degree & betweenness centrality, recursive/BFS cascade simulation across supplier-SKU-warehouse-region topology, and differential failure-impact analysis (`simulate_failure`). |
| **SHAP importance and counterfactual explanations** | **PARTIAL** | `backend/app/engines/xai_engine.py:28-85`<br/>`backend/app/engines/xai_engine.py:103-165` | **SHAP**: **NOT FOUND** (0 imports of `shap` in repo).<br/>Feature importance is implemented using **scikit-learn `RandomForestRegressor` and `permutation_importance`** (`xai_engine.py:28,69`). Counterfactuals are heuristic what-if adjustments (`generate_counterfactuals`). |
| **JWT 60-min access, 30-day rotating refresh, bcrypt cost 12, RBAC 4 roles, rate limiting, audit trail** | **VERIFIED** | `backend/app/core/config.py:41,43`<br/>`backend/app/auth/utils.py:31`<br/>`backend/app/auth/service.py:16-21`<br/>`backend/app/main.py:331,334`<br/>`backend/app/middleware/audit.py:14-45` | **60-min access**: `ACCESS_TOKEN_EXPIRE_MINUTES = 60`.<br/>**30-day refresh**: `REFRESH_TOKEN_EXPIRE_DAYS = 30`.<br/>**bcrypt cost 12**: `rounds=12`.<br/>**RBAC 4 roles**: `admin`, `manager`, `analyst`, `viewer`.<br/>**Rate limiting**: `slowapi.Limiter`.<br/>**Audit trail**: `AuditMiddleware` persists HTTP calls to `AuditLog`. |
| **WebSocket alert feed with auto-reconnect; root cause correlation** | **VERIFIED** | `backend/app/routers/websocket.py:39,205`<br/>`frontend/app/control-tower/page.tsx:265-357`<br/>`backend/app/engines/control_tower.py:423-560` | `/ws/connect` and `/ws/control-tower` streaming endpoints. Next.js UI auto-reconnects on 5s backoff. `alert_correlation_analysis` clusters time-correlated alerts to hypothesize root causes. |
| **Alembic migrations; tenant_id on every table; row-level security SQL in migrations/** | **PARTIAL** | `backend/migrations/001_rls_tenant_isolation.sql`<br/>`backend/app/models/supply.py:7` | `tenant_id` is indexed across all primary entity models. `001_rls_tenant_isolation.sql` provides Postgres RLS policies. However, **Alembic is NOT FOUND** (no `alembic.ini` or migration scripts folder; migration is raw SQL). |
| **"Kafka-ready connector interfaces", DataScheduler, streaming processor in data_lake.py** | **PARTIAL** | `backend/app/engines/scheduler.py:41`<br/>`backend/app/core/data_lake.py:616` | **DataScheduler**: VERIFIED (`scheduler.py:41`).<br/>**StreamingDataProcessor**: VERIFIED (`data_lake.py:616`).<br/>**Kafka**: **NOT FOUND** in backend code (no Kafka library or broker integration; conceptual only). |
| **Multi-stage Dockerfiles; CI test/build/Lighthouse/deploy ECS; AWS CDK stack** | **VERIFIED** | `backend/Dockerfile:1-16`<br/>`frontend/Dockerfile.frontend:1-18`<br/>`.github/workflows/deploy.yml`<br/>`infra/lib/nexus-stack.ts:26-228` | Multi-stage Docker builds exist. CI workflow runs pytest, pip-audit, npm test/build, Playwright e2e, Lighthouse a11y, and ECR/ECS deploy. CDK defines VPC, RDS, ECS Fargate, ALB, CloudWatch. |
| **Server refuses to start in production mode with default SECRET_KEY** | **VERIFIED** | `backend/app/core/config.py:84-88`<br/>`backend/app/main.py:52` | Startup validation check: if `DEBUG=False` and `SECRET_KEY == "nexus-dev-secret-change-in-production"`, raises `RuntimeError` and terminates process. |
| **Offline LLM fallback; Groq and Bedrock providers** | **VERIFIED** | `backend/app/engines/ai_copilot.py:33-143`<br/>`backend/agent/mitigation_graph.py:353-370` | Tri-mode provider support: Groq API primary, AWS Bedrock (`amazon.nova-lite-v1:0`) secondary, and deterministic rule-based offline fallback when no credentials are configured. |
| **TGNNEngine and CausalGenomeEngine descriptions vs actual code** | **PARTIAL / ALIGNED** | `backend/app/engines/tgnn_engine.py:1-27`<br/>`backend/app/causal/__init__.py:1-24`<br/>`docs/ML_AI_HONESTY.md` | Both engines contain honest internal docstrings:<br/>- `TGNNEngine` is a **Temporal Trend Engine** (linear regression + Holt trend on graph edges, no neural network or gradients).<br/>- `CausalGenomeEngine` is a **Risk Propagation Engine** (BFS exposure diffusion on graph, no do-calculus or causal discovery). |

---

## 2. ML Engine Real Entry-Point Reference

For rigorous evaluation and testing without hallucinations, use the verified entry-point signatures below:

### A. Anomaly Detection
- **Class:** `AnomalyDetector`
- **Location:** `backend/app/engines/analyzer.py`
- **Entry point:** `detect_anomalies(df: pd.DataFrame, reference_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]`
  - **Inputs:** `df` (DataFrame with numeric metrics and optional `supplier`, `sku`, `delay_days`, `cost`, `quality_score`), optional baseline `reference_df`.
  - **Outputs:** Dict with keys: `"anomalies"` (List of anomaly dicts containing `index`, `type`, `severity`, `risk_score`, `supplier`, `sku`, `details`), `"total_records"`, `"anomaly_count"`, `"methods_used"`, `"baseline_used"`.
- **Internal method:** `_isolation_forest(df: pd.DataFrame, cols: List[str], train_df: Optional[pd.DataFrame] = None) -> List[Dict]`

### B. Time Series Forecasting
- **Class:** `TimeSeriesForecaster`
- **Location:** `backend/app/engines/forecaster.py`
- **Entry point:** `analyze_trends(df: pd.DataFrame) -> Dict[str, Any]`
  - **Inputs:** `df` (DataFrame with `order_date` or `date` and `delay_days` or `cost`).
  - **Outputs:** Dict containing `"forecast"` (with sub-keys per metric: `"next_periods"`, `"trend_direction"`, `"fallback_reason"`), `"summary"`.
- **Direct forecasting methods:**
  - `_holt_winters_forecast(values: List[float], periods: int = 3, seasonal_periods: int = 4) -> Tuple[List[Dict], Dict]`
  - `_exp_smoothing_forecast(values: List[float], periods: int = 3) -> Tuple[List[Dict], Dict]`

### C. Composite Risk Scoring
- **Class:** `CompositeRiskScorer`
- **Location:** `backend/app/engines/analyzer.py`
- **Entry point:** `score_suppliers(df: pd.DataFrame) -> List[Dict[str, Any]]`
  - **Inputs:** `df` (DataFrame containing `supplier`, `delay_days`, optional `cost`, `quality_score`).
  - **Outputs:** List of supplier score dicts: `[{"supplier": str, "composite_risk_score": float (0-100), "risk_level": "critical"|"high"|"medium"|"low", "factors": {...}, "score_confidence_interval": float, "is_reliable": bool}]`.

### D. Graph Centrality and Cascade Analysis
- **Class:** `SupplyChainGraph`
- **Location:** `backend/app/engines/graph_engine.py`
- **Entry points:**
  - `build_from_dataframe(df: pd.DataFrame) -> nx.DiGraph`
  - `get_centrality_scores() -> Dict[str, List[Dict]]` (returns degree and betweenness centralities).
  - `simulate_cascade(failed_nodes: List[str]) -> Dict[str, Any]` (returns affected downstream nodes and cascade impact).
  - `simulate_failure(node_id: str) -> Dict[str, Any]` (returns pre/post centrality shifts and failure impact).

### E. Explainability (Feature Importance & Counterfactuals)
- **Class:** `XAIEngine`
- **Location:** `backend/app/engines/xai_engine.py`
- **Entry points:**
  - `compute_feature_importance(df: pd.DataFrame, target_col: str = "delay_days") -> Dict[str, Any]`
    - **Inputs:** `df`, target variable string.
    - **Outputs:** Dict with `"features"` (list sorted by importance with permutation scores), `"top_driver"`, `"model_score"`, `"methodology"`.
  - `generate_counterfactuals(df: pd.DataFrame, risk_scores: List[Dict], graph_engine: Any = None) -> List[Dict]`

### F. Monte Carlo Disruption Simulation
- **Class:** `MonteCarloEngine`
- **Location:** `backend/app/engines/monte_carlo.py`
- **Entry point:** `simulate_disruption(supplier_id: str, df: pd.DataFrame, iterations: int = 1000) -> Dict[str, Any]`
  - **Outputs:** Dict with probabilistic disruption distribution, expected cost/delay, percentiles (p10, p50, p90).

### G. LangGraph Mitigation Agent
- **Module:** `backend/agent/mitigation_graph.py`
- **Entry points:**
  - `run_mitigation_workflow(supplier: str, trigger_score: float, run_id: Optional[str] = None) -> Dict[str, Any]`
    - **Execution:** Runs the 5-node graph (`get_backup_suppliers` → `simulate_reroute_cost` → `retrieve_context` → `draft_action` → `write_pending_action`).
    - **Outputs:** Dict containing the drafted action, backup suppliers, reroute simulations, RAG context, and `pending_action_id` awaiting human approval.
  - `node_execute_action(action_id: int, approved_by: str) -> Dict[str, Any]`
    - **Execution:** Human approval checkpoint. Verifies `status == 'awaiting_approval'`, transitions to `status = 'executed'`, records audit timestamp and execution receipt.
