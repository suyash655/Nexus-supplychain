<div align="center">

<img src="https://img.shields.io/badge/NEXUS-Supply%20Chain%20Intelligence-06b6d4?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkw3IDcgMiAxMmw1IDUgNSA1IDUtNSA1LTUtNS01LTUtNXoiIGZpbGw9IndoaXRlIi8+PC9zdmc+" alt="NEXUS Banner" />

# NEXUS — Autonomous Supply Chain Intelligence Platform

*Upload your CSV. Watch the graph build itself. Get AI-driven risk mitigations in seconds.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-FF6B6B?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-Research%20%26%20Evaluation-yellow?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/yourusername/nexus/deploy.yml?style=flat-square&label=CI)](https://github.com/yourusername/nexus/actions)

</div>

---

<!-- TODO: Replace with an actual screen recording GIF showing: upload CSV → dashboard populates → graph renders → mitigation agent fires -->
![NEXUS Demo](https://placehold.co/1200x600/030712/06b6d4?text=NEXUS+Dashboard+Demo+GIF+Here)
*↑ Replace with a screen recording of the full upload → analysis → graph → mitigation flow*

---

## The Problem

Supply chain risk is opaque. A delayed shipment from a Tier-2 supplier in Vietnam can cascade into a production halt in Germany — and most teams don't find out until it's too late.

Existing tools either **require expensive ERP integration** (SAP, Oracle) or are **spreadsheet dashboards** that show data without telling you what to *do* about it.

**NEXUS is neither.** Drop in a CSV, and within 60 seconds you get:
- A live network graph of your entire supplier topology
- ML-ranked risk scores with anomaly detection
- An AI agent that identifies the highest-risk suppliers and proposes mitigation plans — waiting for your approval before acting

---

## ✨ Key Features

- 🧠 **Multi-Engine ML Pipeline** — Isolation Forest anomaly detection, Holt-Winters forecasting, composite risk scoring, and Monte Carlo disruption simulations run automatically after every upload
- 🕸️ **Live Supply Chain Graph** — NetworkX-powered directed graph with centrality analysis, cascade simulation, and failure impact scoring. Nodes are your suppliers, SKUs, warehouses, and regions — edges are the relationships between them
- 🤖 **LangGraph Mitigation Agent** — A 6-node stateful agent that detects critical risk, searches past incident context via ChromaDB RAG, finds backup suppliers, runs probabilistic simulations, drafts an LLM action plan, then waits for human approval before executing
- 📊 **Explainability (XAI)** — SHAP-based feature importance and counterfactual explanations ("reduce Alpha Corp's delay by 3 days and risk drops 18 points")
- 🔒 **Production-Ready Auth** — JWT with 60-min access tokens, 30-day rotating refresh tokens, bcrypt hashing, RBAC (admin / manager / analyst / viewer), rate limiting, and a full audit trail on every API call
- 📡 **Real-Time Control Tower** — WebSocket-powered live alert feed with auto-reconnect, incident management, and correlation-based root cause analysis
- 🌐 **Works Offline** — All ML runs locally. The LLM copilot falls back to deterministic rule-based summaries when no API key is configured. No cloud dependency required for core functionality

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Frontend** | Next.js 15 (App Router) + TypeScript | App Router enables server components for layout; TypeScript catches API shape mismatches at compile time |
| **UI** | Tailwind CSS + custom design tokens | Dark glassmorphism theme, consistent spacing system via CSS variables |
| **Charts** | Recharts + react-force-graph-2d | Recharts for analytics charts; D3-backed force graph for the supply chain network |
| **State** | React `useApi` hook + module-level cache | Custom SWR-style hook with deduplication, TTL, and cache invalidation — no Redux needed |
| **Backend** | FastAPI (Python 3.11+) | Async request handling, auto-generated OpenAPI docs, Pydantic validation |
| **ML** | scikit-learn, NetworkX, statsmodels | Isolation Forest, DBSCAN clustering, Holt-Winters; all run in-process, no external services |
| **AI Agent** | LangGraph + LangChain | Explicit state machine with human-in-the-loop checkpoints; each node is traced and stored |
| **LLM** | Groq / AWS Bedrock / Offline fallback | Provider-agnostic abstraction — swap keys in `.env` with no code changes |
| **Vector DB** | ChromaDB | Local RAG over past supply chain incidents for agent context |
| **Database** | SQLite (dev) / PostgreSQL (prod) | SQLAlchemy ORM; WAL mode for SQLite concurrency; Alembic migrations |
| **Auth** | PyJWT + bcrypt + slowapi | HS256 tokens, bcrypt cost-12 hashing, IP-based rate limiting on auth endpoints |
| **DevOps** | Docker + GitHub Actions + AWS CDK | Multi-stage Dockerfiles; CI runs tests → build → Lighthouse → deploy to ECS Fargate |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     BROWSER (Next.js 15)                     │
│  Upload │ Dashboard │ Graph │ Copilot │ Mitigation │ Reports  │
└──────────────────┬───────────────────────────────────────────┘
                   │  REST + WebSocket
┌──────────────────▼───────────────────────────────────────────┐
│               FASTAPI BACKEND  :8000                         │
│                                                              │
│  Auth · Upload · Analytics · Graph · XAI · Control Tower     │
│  Mitigation · Planning · Export · Connectors  (+20 more)     │
│                                                              │
│  ── Orchestrator ──────────────────────────────────────────  │
│  On every upload → run_full_analysis() fires 6 engines in    │
│  sequence, saves JSON blobs to analysis_results table        │
│                                                              │
│  ── LangGraph Agent ───────────────────────────────────────  │
│  assess_risk → rag_context → find_backups → monte_carlo →    │
│  llm_plan → save_pending  [awaits human approval]            │
└──────────────────┬───────────────────────────────────────────┘
                   │  SQLAlchemy ORM
┌──────────────────▼───────────────────────────────────────────┐
│  SQLite / PostgreSQL   │   ChromaDB (RAG)                    │
│  supply_data           │   past incident embeddings          │
│  analysis_results      │                                     │
│  agent_traces          │                                     │
└──────────────────────────────────────────────────────────────┘
```

**Data flow in one sentence:** A CSV upload atomically replaces `supply_data`, triggers a background ML pipeline that writes results to `analysis_results`, and every dashboard page reads from that cache — so the UI is always fast regardless of data size.

> **Honesty note:** `TGNNEngine` is a temporal trend engine (not a true GNN). `CausalGenomeEngine` is graph-based risk propagation (not Bayesian do-calculus). See [`docs/ML_AI_HONESTY.md`](docs/ML_AI_HONESTY.md) for the complete accuracy log.

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | any | `git --version` |

### 1 · Clone

```bash
git clone https://github.com/yourusername/nexus.git
cd nexus
```

### 2 · Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv ../.venv

# Windows
..\.venv\Scripts\activate

# macOS / Linux
source ../.venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3 · Environment Variables

```bash
# Copy the example file
cp .env.example .env        # macOS/Linux
copy .env.example .env      # Windows
```

Open `.env` and configure:

```env
# ── Required ────────────────────────────────────────────────────────
DATABASE_URL=sqlite:///data/synchain.db
SECRET_KEY=change-me-to-a-random-64-char-string-in-production

# ── CORS ─────────────────────────────────────────────────────────────
CORS_ORIGINS=http://localhost:3000

# ── Demo Mode (disables auth requirement for local exploration) ──────
ALLOW_DEMO=true

# ── LLM (optional — system works fully offline without these) ────────
LLM_PROVIDER=offline          # or: groq | bedrock
GROQ_API_KEY=                 # get free key at console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile
```

> **Note:** `SECRET_KEY` must be changed before any non-local deployment. The server will refuse to start in production mode with the default value.

### 4 · Run the Backend

```bash
# From the backend/ directory, with .venv activated
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO  [NEXUS] ✓ SupplyChainAnalyzer initialised
INFO  [NEXUS] ✓ SupplyChainGraph initialised
INFO  [NEXUS] All engines initialised successfully — server ready
INFO  Uvicorn running on http://0.0.0.0:8000
```

### 5 · Frontend Setup

```bash
# In a new terminal, from the project root
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
```

### 6 · Open the App

| Service | URL |
|---|---|
| **Web App** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |

### Alternative: Docker Compose

```bash
# From project root — spins up both services
docker-compose up
```

---

## 📖 Usage

### Upload Your First Dataset

1. Navigate to **http://localhost:3000/upload**
2. Drop any CSV with supply chain data (supplier, SKU, delay_days, cost columns — others are auto-detected)
3. Review the column mapping preview and click **Upload & Analyze**
4. The dashboard auto-redirects and populates within ~60 seconds as the ML pipeline runs

**Don't have a CSV?** Run the included test data generator:

```bash
cd backend
python test_upload_flow.py   # generates 50-row pseudo CSV and runs full pipeline validation
```

### Exploring the Dashboard

```
/dashboard       → KPI strip, supplier risk leaderboard, trend charts
/graph           → Interactive supply chain network (click nodes, simulate failures)
/analytics       → Deep-dive: time-series, regional breakdown, data quality
/xai             → SHAP feature importance + counterfactual "what if" explanations
/control-tower   → Live alert feed, incident management, root cause correlation
/mitigation      → Review and approve/reject AI agent action plans
/copilot         → Natural language Q&A over your supply chain data
```

### Demo Mode (No Login Required)

Click **"Skip to demo →"** on the login page to explore with pre-loaded sample data. No credentials needed.

---

## 🔐 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/synchain.db` | SQLAlchemy connection string |
| `SECRET_KEY` | `dev-secret` | JWT signing key — **change in production** |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `ALLOW_DEMO` | `true` | Enables unauthenticated demo access |
| `LLM_PROVIDER` | `offline` | `offline` \| `groq` \| `bedrock` |
| `GROQ_API_KEY` | _(empty)_ | Groq API key for LLM features |
| `MAX_UPLOAD_BYTES` | `52428800` | Max upload file size (50 MB default) |
| `MAX_ANALYSIS_ROWS` | `100000` | Row cap for ML pipeline |
| `DEBUG` | `false` | Enables hot-reload and verbose logging |

---

## 🧩 Challenges & Learnings

### The Hardest Problem: Making Async Data Feel Synchronous

The core UX challenge was this: the ML pipeline takes 30–90 seconds after a CSV upload. If you just show a spinner, users bounce. If you redirect immediately, they see empty charts.

**What I tried first:** A single long-polling endpoint that blocked until analysis finished. This caused request timeouts and didn't scale past one user.

**What I built instead:** A three-layer freshness system:
1. The upload response returns immediately (rows inserted ✓)
2. The dashboard reads live DB aggregates for analytics (supplier counts, totals) — these are available *instantly*
3. Heavier analysis results (ML risk scores, graph topology) are served from an `analysis_results` cache table, which the pipeline populates asynchronously
4. The graph page polls `/graph/status` every 5 seconds and swaps in real data the moment it lands — showing demo fallback data in the meantime

This meant users see *something useful immediately* and *real data progressively* — which is exactly how production dashboards like Datadog and Grafana work.

**Key takeaways:**

- **Decouple write latency from read latency.** Background workers + result caches are the right pattern for any slow computation that multiple clients need to read.
- **Design for degraded mode.** Every engine in NEXUS can fail independently. The server starts in degraded mode and keeps serving the healthy endpoints. This forced me to think about fault isolation rather than assuming happy-path.
- **Data shape bugs are hard to debug without types.** The frontend is fully TypeScript with strict API response shapes. I caught at least a dozen bugs at compile time that would have been silent runtime `undefined` errors in plain JavaScript.

---

## 🔭 Future Enhancements

1. **Multi-tenant SaaS mode** — The DB schema already has a `tenant_id` column on every table and row-level security SQL in `migrations/`. Wiring this through the auth layer to a subscription system is the next step.

2. **Real-time streaming ML** — Currently the pipeline runs once per upload. The architecture (Kafka-ready connector interfaces, a DataScheduler engine, and the streaming processor in `data_lake.py`) is designed for continuous ingestion. Connecting a live ERP feed would make risk scores update in real time.

3. **True causal inference** — `CausalGenomeEngine` currently does graph-based propagation. Replacing the internals with [DoWhy](https://github.com/py-why/dowhy) or [CausalNex](https://github.com/quantumblacklabs/causalnex) would allow the system to answer "did this supplier's delay *cause* the cost increase?" rather than just "are they correlated?"

---

## 📁 Project Structure

```
nexus/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point, lifespan, middleware
│   │   ├── routers/             ← 30 API route modules (one domain per file)
│   │   ├── engines/             ← ML/AI engine singletons
│   │   ├── core/                ← Config, DB, errors, orchestrator
│   │   ├── models/              ← SQLAlchemy ORM models
│   │   ├── services/upload/     ← Parser, schema detector, validator
│   │   └── middleware/          ← JWT auth, audit trail
│   ├── agent/
│   │   ├── mitigation_graph.py  ← LangGraph 6-node agent
│   │   ├── llm_client.py        ← Groq/Bedrock/offline abstraction
│   │   └── tools.py             ← Supplier lookup, notification tools
│   ├── tests/                   ← Pytest suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/                     ← Next.js App Router pages
│   │   ├── dashboard/           ← Command center
│   │   ├── upload/              ← Upload wizard + column mapping
│   │   ├── graph/               ← Supply chain network (D3)
│   │   ├── analytics/           ← Deep analytics views
│   │   ├── control-tower/       ← Real-time ops board
│   │   ├── mitigation/          ← Agent approval UI
│   │   ├── xai/                 ← Explainability (SHAP)
│   │   └── copilot/             ← AI chat
│   ├── hooks/useApi.ts          ← Custom SWR-style data fetching
│   ├── lib/api.ts               ← Typed API client
│   └── Dockerfile.frontend
│
├── .github/workflows/deploy.yml ← CI/CD pipeline
├── docker-compose.yml
├── ARCHITECTURE.md              ← Deep-dive system design doc
└── README.md                    ← You are here
```

---

## 🤝 Contributing

This is a solo learning project, but issues and suggestions are welcome.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-idea`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push and open a Pull Request

---

## 📄 License

Distributed under a **Research & Evaluation License** — free to use, study, and build upon for non-commercial purposes. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

**Built by [Your Name](https://yourportfolio.com)**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-06b6d4?style=flat-square&logo=vercel)](https://yourportfolio.com)

*If this project helped you or impressed you — a ⭐ on GitHub goes a long way for a fresher's portfolio.*

</div>
