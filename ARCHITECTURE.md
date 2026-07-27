# NEXUS — Architecture Guide

> **NEXUS** is an AI-powered Supply Chain Intelligence Platform.
> It ingests supply chain data, runs multi-engine ML analysis, and provides actionable risk mitigations through an agentic LLM loop — all from a modern Next.js dashboard.

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Directory Structure](#2-directory-structure)
3. [Backend Architecture](#3-backend-architecture)
4. [Frontend Architecture](#4-frontend-architecture)
5. [Data Flow](#5-data-flow)
6. [Security Model](#6-security-model)
7. [Agent Loop (Mitigation)](#7-agent-loop-mitigation)
8. [Deployment](#8-deployment)
9. [Key Design Decisions](#9-key-design-decisions)

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                      Next.js 14 (App Router)                    │
│  Dashboard | Upload | Analytics | Graph | Copilot | Mitigation  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / REST / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                    FASTAPI BACKEND  :8000                        │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Auth    │  │  Upload  │  │Analytics │  │ Mitigation     │  │
│  │  Router  │  │  Router  │  │  Router  │  │ Router (Agent) │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│                       +26 more routers                           │
│  ─────────────────────────────────────────────────────────────  │
│                        CORE LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Config  │  │  Database│  │ Errors   │  │ Orchestrator   │  │
│  │ Settings │  │  SQLAlch.│  │ Handlers │  │ (runs engines) │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│  ─────────────────────────────────────────────────────────────  │
│                       ENGINE LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  ML      │  │  Graph   │  │  XAI     │  │  Monte Carlo   │  │
│  │ Analyzer │  │  Engine  │  │  Engine  │  │  Engine        │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Causal  │  │   KPI    │  │  TGNN    │  │  AI Copilot    │  │
│  │  Genome  │  │  Engine  │  │  Engine  │  │  (LLM + RAG)   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│  ─────────────────────────────────────────────────────────────  │
│                       AGENT LAYER                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LangGraph Mitigation Agent (mitigation_graph.py)        │    │
│  │  Node 1→2→3→4→5→6: Assess→RAG→Backup→MonteCarlo→       │    │
│  │  LLM-Plan→Human-Approve→Execute                          │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQLAlchemy ORM
┌──────────────────────────▼──────────────────────────────────────┐
│                       DATA LAYER                                 │
│   SQLite (dev)  /  PostgreSQL (prod)       ChromaDB (RAG)        │
│   data/synchain.db                         data/chroma_db/       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

```
supex1/                          ← Project root
├── backend/                     ← FastAPI Python backend
│   ├── app/
│   │   ├── main.py              ← Entry point: FastAPI app, lifespan, middleware
│   │   ├── routers/             ← 30 API route modules (one domain per file)
│   │   ├── engines/             ← 16 ML/AI engine modules
│   │   ├── core/                ← Shared infrastructure (config, db, errors, orchestrator)
│   │   ├── models/              ← SQLAlchemy ORM models
│   │   ├── schemas/             ← Pydantic request/response schemas
│   │   ├── services/            ← Stateless business logic (upload parsing, etc.)
│   │   ├── middleware/          ← HTTP audit trail middleware
│   │   ├── auth/                ← JWT auth service + utils
│   │   ├── connectors/          ← External data source connectors (S3, DB, API)
│   │   ├── causal/              ← Causal inference engine
│   │   └── pipeline/            ← Data pipeline + quality engine
│   ├── agent/                   ← LangGraph agentic mitigation loop
│   │   ├── mitigation_graph.py  ← 6-node graph (core agent logic)
│   │   ├── llm_client.py        ← LLM provider abstraction (Groq/Bedrock)
│   │   ├── tools.py             ← Agent tools (supplier lookup, notifications)
│   │   └── state.py             ← LangGraph state schema
│   ├── rag/                     ← RAG document ingestion + ChromaDB
│   ├── migrations/              ← Alembic DB migrations
│   ├── tests/                   ← Pytest test suite
│   ├── Dockerfile               ← Backend Docker image
│   └── requirements.txt
│
├── frontend/                    ← Next.js 14 frontend
│   ├── app/                     ← App Router pages
│   │   ├── dashboard/           ← Main supply chain dashboard
│   │   ├── upload/              ← File upload + column mapping wizard
│   │   ├── analytics/           ← Advanced analytics views
│   │   ├── graph/               ← D3.js supply chain graph visualization
│   │   ├── copilot/             ← AI chat assistant
│   │   ├── mitigation/          ← Agent trace viewer + approval UI
│   │   ├── control-tower/       ← Real-time operations centre
│   │   ├── ibp-unified/         ← SAP IBP-style planning modules
│   │   └── login/               ← Auth pages
│   ├── hooks/                   ← React custom hooks
│   ├── lib/                     ← API client utilities
│   └── Dockerfile.frontend      ← Frontend Docker image
│
├── infra/                       ← AWS CDK Infrastructure-as-Code
│   ├── lib/                     ← CDK stack definitions
│   └── bin/                     ← CDK app entry point
│
├── docs/                        ← Technical documentation
├── data/                        ← Runtime data (DB, ChromaDB, sample CSVs)
├── docker-compose.yml           ← Local dev: spins up backend + frontend
├── .github/workflows/           ← CI/CD pipeline (GitHub Actions)
└── ARCHITECTURE.md              ← This file
```

---

## 3. Backend Architecture

### 3.1 Entry Point — `app/main.py`

The main file does three things only:
1. **Lifespan context manager** — initialises all engine singletons on startup, shuts them down gracefully. A single failing engine logs an error and puts the server in **degraded mode** rather than crashing.
2. **Middleware registration** — CORS, AuditMiddleware, request logging, rate-limit error handler.
3. **Router registration** — imports and mounts all 30 routers under the app.

### 3.2 Core Layer — `app/core/`

| Module | Purpose |
|--------|---------|
| `config.py` | Single `Settings` class; all config from env vars. Validates `SECRET_KEY` on startup — crashes in prod if using the default dev secret. |
| `database.py` | SQLAlchemy engine + `SessionLocal` factory |
| `dependencies.py` | Shared FastAPI Depends: `get_db()`, `require_auth()`, `require_admin()` |
| `errors.py` | Typed `NexusError` hierarchy + global exception handlers → consistent `{"status":"error","code":"...","message":"...","request_id":"..."}` envelope on every error |
| `orchestrator.py` | Coordinates all ML engine runs; saves results to `analysis_results` DB table |
| `analysis_coordinator.py` | Higher-level coordinator with progressive analysis stages |

### 3.3 Router Layer — `app/routers/`

Each file is a single, focused FastAPI `APIRouter`:

```
/upload         → upload.py          (CSV/Excel ingestion, schema detection)
/analytics      → analytics.py       (dashboard summary, time-series, KPIs)
/ml             → ml.py              (anomalies, risk scores, clustering)
/graph          → graph.py           (supply chain network analysis)
/copilot        → copilot.py         (AI assistant, LLM streaming)
/auth           → auth_routes.py     (register, login, refresh, logout)
/mitigation     → mitigation.py      (agent actions, approval, traces)
/xai            → remaining.py       (explainability: feature importance, counterfactuals)
/export         → remaining.py       (CSV/JSON data export)
/ibp/demand     → ibp_demand.py      (SAP IBP-style demand planning)
/ibp/supply     → supply_planning.py (SAP IBP-style supply planning)
/control-tower  → control_tower.py   (real-time ops monitoring)
/sop            → sop.py             (standard operating procedures)
/monitoring     → monitoring.py      (system health, engine status)
... + 16 more
```

### 3.4 Engine Layer — `app/engines/`

Engines are heavy ML/AI components initialized once at startup via `lifespan`:

| Engine | What it does |
|--------|-------------|
| `SupplyChainAnalyzer` | ML risk scoring (Isolation Forest, DBSCAN clustering) |
| `SupplyChainGraph` | NetworkX graph: supplier network, centrality, shortest paths |
| `XAIEngine` | SHAP feature importance + counterfactual explanations |
| `MonteCarloEngine` | Probabilistic risk simulations (10k iterations) |
| `CausalGenomeEngine` | Causal inference (DoWhy) — finds root causes not just correlations |
| `KPIEngine` | Platform performance KPIs (decision velocity, alert accuracy) |
| `TGNNEngine` | Temporal Graph Neural Network for dynamic risk propagation |
| `AICopilot` | LLM-powered Q&A over supply chain data |
| `SOPEngine` | Standard operating procedure generation and lookup |
| `ResponsePlanningEngine` | Scenario-based disruption response planning |
| `DemandPlanningEngine` | SAP IBP-style demand forecasting (multiple models) |
| `SupplyPlanningEngine` | Production scheduling + capacity optimization |
| `DataScheduler` | Background cron jobs for automated data refresh |

### 3.5 Service Layer — `app/services/`

Thin, stateless business logic extracted from routers:

```
services/upload/
  ├── parser.py      ← File parsing (CSV, Excel) with size limits
  ├── schema.py      ← Auto column-detection with confidence scoring
  └── validator.py   ← Type-safe value coercion (safe_int, safe_float, safe_str)
```

---

## 4. Frontend Architecture

**Framework:** Next.js 14 with App Router (TypeScript)

```
frontend/app/
├── layout.tsx          ← Root layout, global fonts, theme
├── page.tsx            ← Root redirect to /dashboard
├── globals.css         ← Design system tokens, glassmorphism utilities
├── tokens.ts           ← Shared design tokens (colors, spacing)
│
├── dashboard/          ← Main view: KPI strip, risk map, alerts
├── upload/
│   ├── page.tsx        ← Upload wizard: file drop → auto-detect → confirm mapping
│   └── map/            ← Column mapping confirmation step
├── analytics/          ← Time-series, supplier analytics, trends
├── graph/              ← D3.js force-directed supply chain network
├── copilot/            ← AI chat with streaming responses
├── mitigation/         ← Agent action cards, approve/reject, trace viewer
├── control-tower/      ← Real-time ops board
├── ibp-unified/        ← Unified SAP IBP-style planning dashboard
├── causal/             ← Causal inference explorer
└── xai/                ← Explainability (SHAP waterfall charts)
```

**Data fetching:** Direct `fetch()` calls to the FastAPI backend via `NEXT_PUBLIC_API_URL`. Auth token stored in `localStorage` as `nexus_token`.

---

## 5. Data Flow

### Upload → Analysis → Dashboard

```
User selects file
        │
        ▼
POST /upload/preview           ← Parse 20 rows, detect columns (no DB write)
        │
        ▼
POST /upload                   ← Full parse → clear old data → bulk insert → commit
        │                         (atomic: all rows succeed or all roll back)
        ▼
Background: run_full_analysis()
        │
        ├── SupplyChainAnalyzer → risk scores, anomalies, clustering
        ├── SupplyChainGraph    → network centrality, critical paths
        ├── XAIEngine           → SHAP importance, counterfactuals
        ├── MonteCarloEngine    → probabilistic simulations
        └── KPIEngine           → platform performance KPIs
        │
        ▼
Results saved → analysis_results table (keyed by analysis_type)
        │
        ▼
GET /analytics/summary         ← Dashboard reads from analysis_results cache
```

### Mitigation Agent Loop

```
ML flags supplier risk_score ≥ threshold (default 75)
        │
        ▼
trigger_mitigation() → LangGraph run begins
        │
        ├── Node 1: assess_risk        (load data, validate threshold)
        ├── Node 2: rag_context        (ChromaDB similarity search → past incidents)
        ├── Node 3: find_backup_suppliers (DB query → ranked alternatives)
        ├── Node 4: run_monte_carlo    (probabilistic cost/delay simulation)
        ├── Node 5: generate_plan      (LLM synthesizes action: PO, reroute, etc.)
        └── Node 6: save_pending       (write to pending_actions table)
                │
                ▼
        Human reviews in /mitigation UI
                │
        ┌───────┴────────┐
        ▼                ▼
    Approve           Reject
        │
        ▼
    execute_action() (mock PO send / notification)
        │
        ▼
    Action logged in agent_traces table
```

---

## 6. Security Model

### Authentication
- **JWT access tokens** — HS256, 60-minute lifetime, decoded on every request via `require_auth` FastAPI dependency
- **Refresh tokens** — 30-day lifetime, stored as SHA-256 hash in DB. Rotation on every `/auth/refresh` call (old token immediately revoked)
- **bcrypt** — password hashing with cost factor 12 (auto-salted)
- **Demo mode** — only activates when `ALLOW_DEMO=true` AND no `Authorization` header present at all. No magic bypass token exists.

### Authorization (RBAC)
```
admin   → all permissions (*)
manager → read, write, export, manage_team, connectors:*, ibp:*, reports:*
analyst → read, write, export, run_analysis, copilot, connectors:read, ibp:*
viewer  → read, connectors:read, ibp:read, reports:read
```

### Rate Limiting
- `POST /auth/login` → 10 requests/minute per IP
- `POST /auth/register` → 5 requests/minute per IP
- `POST /auth/refresh` → 5 requests/minute per IP
- Powered by `slowapi` (wrapper around `limits` library)

### Input Validation
- All request bodies use **Pydantic models** with field constraints (`min_length`, `max_length`, `pattern`, `ge`, `le`)
- Upload: file type whitelist (CSV/Excel), configurable size limit (`MAX_UPLOAD_BYTES`)
- SQL injection: no raw SQL. All queries use SQLAlchemy ORM or parameterized `text()` with validated inputs

### Audit Trail
- `AuditMiddleware` logs every non-health request to `audit_logs` DB table: method, path, user ID, IP, duration, status code
- Sensitive fields auto-masked (password, token, email, etc.) via `mask_sensitive_data()`

### Error Handling
- All errors return a consistent envelope — **stack traces never reach the client**
- `unhandled_exception_handler` catches everything, logs server-side, returns generic 500

### Production Guardrails
- `settings.validate()` — crashes on startup in non-debug mode if `SECRET_KEY` equals the default dev value
- `Cache-Control: no-store` on all responses (prevents browser caching of sensitive data)
- `X-Request-ID` on all responses (correlate client errors to server logs)

---

## 7. Agent Loop (Mitigation)

The mitigation agent uses **LangGraph** — a stateful graph execution framework:

```python
# Simplified structure (agent/mitigation_graph.py)
graph = StateGraph(MitigationState)

graph.add_node("assess_risk",          assess_risk_node)
graph.add_node("rag_context",          rag_context_node)
graph.add_node("find_backup_suppliers",find_backup_node)
graph.add_node("run_monte_carlo",      monte_carlo_node)
graph.add_node("generate_plan",        llm_plan_node)       # LLM call
graph.add_node("save_pending",         save_pending_node)

graph.set_entry_point("assess_risk")
graph.add_edge("assess_risk",           "rag_context")
graph.add_edge("rag_context",           "find_backup_suppliers")
graph.add_edge("find_backup_suppliers", "run_monte_carlo")
graph.add_edge("run_monte_carlo",       "generate_plan")
graph.add_edge("generate_plan",         "save_pending")
```

**Human-in-the-loop:** The agent always stops at `save_pending`. A procurement officer approves or rejects via the UI before any action is executed. Every node's input, output, and duration is recorded in `agent_traces` for full observability.

**LLM Abstraction:** `agent/llm_client.py` provides a single `call_llm(prompt)` function that routes to Groq (free tier), AWS Bedrock, or falls back to offline rule-based responses — making the system work without any paid API.

---

## 8. Deployment

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Docker Compose (local, full stack)
```bash
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Docs: http://localhost:8000/docs
```

### Production (AWS)
```
GitHub Actions (deploy.yml)
        │
        ├── Build backend Docker image → ECR
        ├── Build frontend Docker image → ECR
        └── Deploy CDK stacks (infra/) → ECS Fargate
                ├── backend service (ECS task)
                ├── frontend service (ECS task)
                └── ALB + Route53 + ACM
```

---

## 9. Key Design Decisions

### Why a single `main.py` lifespan for all engines?
Engines (ML models, graph engines) are expensive to initialise. Using FastAPI's `lifespan` context manager means:
- Each engine starts **once** (not per-request)
- A single failing engine logs an error but doesn't crash the server
- The server starts in **degraded mode** with a clear log of which engines failed
- Clean shutdown (scheduler stops, connections close)

### Why store analysis results in the DB?
Engines run in the background after upload. The dashboard needs to read results at any time without re-running ML. `analysis_results` table acts as a **cache layer**: keyed by `analysis_type`, always holds the latest run. This decouples the slow ML computation from fast API reads.

### Why `SafeJSONResponse`?
NumPy operations produce `NaN` and `Infinity` values that are valid in Python but **invalid JSON**. `SafeJSONResponse` sanitizes these to `null` before serialization — preventing crashes on the client that would be very hard to debug.

### Why `remaining.py` bundles multiple routers?
Several small feature areas (XAI, export, connectors, pipeline, causal, scheduler, system) each have only 2–4 endpoints. Keeping them in one file avoids an explosion of tiny files. Each is still an independent `APIRouter` — they're just imported together from one module.

### Why LangGraph for the agent?
LangGraph provides:
- **Explicit state machine** — every node transition is visible and debuggable
- **Persistence** — state can be saved mid-graph for human-in-the-loop approval
- **Observability** — each node execution is traced and stored in DB

---

*This document is the single source of truth for NEXUS architecture. Last updated: 2026-07-25.*
