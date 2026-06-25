# Project Nexus — Causal-AI Supply Chain Engine

> **Enterprise-grade Supply Chain Intelligence** fusing Bayesian Causal Inference, Temporal Graph Networks, and Structural Stability analysis into a single antifragile decision-support platform.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│           Next.js 14 · TypeScript · Glassmorphism UI             │
│  [ Dashboard ] [ Graph ] [ AI Co-Pilot ] [ Evaluation ]          │
└──────────────────┬───────────────────────────────────────────────┘
                   │ REST / JSON
┌──────────────────▼───────────────────────────────────────────────┐
│                      FASTAPI GATEWAY                             │
│  backend/app/main.py · CORS · Auth middleware · SafeJSONResponse │
│                                                                  │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐  │
│  │ /upload │ │/analytics│ │/graph  │ │/copilot │ │ /auth    │  │
│  └────┬────┘ └────┬─────┘ └───┬────┘ └────┬────┘ └─────┬────┘  │
│       │           │           │            │             │       │
│  ┌────▼───────────▼───────────▼────────────▼─────────────▼────┐ │
│  │                    ENGINE LAYER (Singletons)                │ │
│  │                                                             │ │
│  │  SupplyChainAnalyzer  ──► ML pipeline (IsoForest, HW, IQR) │ │
│  │  SupplyChainGraph     ──► NetworkX topology + centrality    │ │
│  │  TGNNEngine           ──► Temporal Graph Neural Network     │ │
│  │  CausalGenomeEngine   ──► Bayesian DAG + interventions      │ │
│  │  AICopilot            ──► Groq / Bedrock LLM reasoning      │ │
│  │  MonteCarloEngine     ──► Stochastic risk simulation        │ │
│  │  ESGEngine            ──► ESG scoring + compliance          │ │
│  │  KPIEngine            ──► KPI tracking + anomaly alerts     │ │
│  │  XAIEngine            ──► Explainable AI attributions       │ │
│  │  ContractIntelligence ──► NLP contract risk analysis        │ │
│  │  DataScheduler        ──► Background ingestion scheduler    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  SQLite (dev) · PostgreSQL (prod)  ·  data/synchain.db           │
│  Models: SupplyData · AnalysisResult · RiskEvent · User · AuditLog│
└──────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
nexus/
├── README.md                     ← You are here
├── docs/
│   ├── architecture.md           ← Detailed system design
│   ├── data-model.md             ← Database schema reference
│   ├── api-endpoints.md          ← All API routes + payloads
│   └── evaluation.md             ← Model metrics + benchmarks
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               ← FastAPI entry point + router registration
│       ├── core/
│       │   ├── config.py         ← Settings (env vars + defaults)
│       │   ├── database.py       ← SQLAlchemy engine + SessionLocal
│       │   ├── dependencies.py   ← Auth + DB dependency injection
│       │   └── orchestrator.py   ← Analysis pipeline orchestration
│       ├── models/               ← SQLAlchemy ORM models
│       │   ├── base.py
│       │   ├── supply.py
│       │   ├── risk.py
│       │   └── auth.py
│       ├── schemas/              ← Pydantic request/response schemas
│       │   ├── supply.py
│       │   ├── analytics.py
│       │   └── auth.py
│       ├── routers/              ← API route handlers
│       │   ├── upload.py
│       │   ├── analytics.py
│       │   ├── graph.py
│       │   ├── copilot.py
│       │   ├── ml.py
│       │   ├── auth_routes.py
│       │   └── remaining.py      ← xai, export, causal, agents, esg, etc.
│       ├── engines/              ← AI/ML computation engines
│       │   ├── analyzer.py       ← Risk scoring pipeline
│       │   ├── graph_engine.py   ← Supply chain graph + topology
│       │   ├── tgnn_engine.py    ← Temporal Graph Neural Network
│       │   ├── ai_copilot.py     ← LLM reasoning (Groq / Bedrock)
│       │   ├── monte_carlo.py    ← Monte Carlo simulations
│       │   ├── esg_engine.py     ← ESG compliance scoring
│       │   ├── kpi_engine.py     ← KPI monitoring + alerts
│       │   ├── xai_engine.py     ← Explainability attributions
│       │   ├── forecaster.py     ← Time-series forecasting
│       │   ├── contract_intelligence.py ← Contract NLP analysis
│       │   └── scheduler.py      ← Background data scheduler
│       ├── services/             ← Business logic (thin wrappers)
│       │   ├── data_ingestion.py
│       │   ├── ml_service.py
│       │   ├── graph_service.py
│       │   ├── xai_service.py
│       │   └── copilot_service.py
│       ├── agents/               ← Autonomous agent orchestration
│       ├── causal/               ← Bayesian causal genome engine
│       ├── pipeline/             ← Data quality pipeline
│       ├── connectors/           ← External data source connectors
│       ├── auth/                 ← JWT auth helpers
│       └── tasks/                ← Async background tasks
│
├── frontend/                     ← Next.js 14 app
│   ├── app/                      ← App Router pages
│   ├── lib/                      ← API client + utilities
│   └── public/
│
├── data/
│   └── synchain.db               ← SQLite database (dev)
│
└── scripts/
    ├── generate_splits.py
    ├── reorganize_dataset.py
    └── smoke_test.py
```

---

## Core Pillars

| Pillar | Technology | Key Metric |
|--------|-----------|------------|
| **Causal Supply Chain Graph (CSCG)** | Bayesian DAG + interventional queries | ~94% fidelity in What-If simulations |
| **Temporal Graph Intelligence** | T-GNN dynamic node embeddings | 2.5× more latent bottlenecks detected |
| **Structural Fragility Framework** | Taleb-inspired vulnerability index | ~45% reduction in systemic risk |
| **AI Co-Pilot** | Groq LLaMA-3.3 / AWS Bedrock | Executive health summaries + NLP queries |
| **Monte Carlo Risk** | Stochastic simulation engine | Probability distributions over disruption cost |
| **ESG Engine** | Compliance scoring + audit trail | Automated ESG reporting |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Redis for caching

### Backend

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
cp .env.example .env            # edit GROQ_API_KEY etc.

# 4. Start server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API Docs → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev

# App → http://localhost:3000
```

### Docker (full stack)

```bash
docker-compose up --build
```

---

## API Overview

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/upload` | Ingest CSV/Excel supply chain data |
| `POST` | `/analyze` | Run full ML + causal analysis pipeline |
| `GET`  | `/analytics/summary` | Risk summary + KPI dashboard data |
| `GET`  | `/graph/topology` | Supply chain network graph |
| `POST` | `/copilot/query` | Natural language AI Co-Pilot query |
| `POST` | `/causal/intervention` | What-If causal intervention |
| `GET`  | `/esg/scores` | ESG compliance scores |
| `POST` | `/contracts/analyze` | Contract risk NLP analysis |
| `GET`  | `/health` | System health check |

Full reference → [`docs/api-endpoints.md`](docs/api-endpoints.md)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/synchain.db` | Database connection string |
| `SECRET_KEY` | `nexus-dev-secret` | JWT signing key (**change in prod**) |
| `GROQ_API_KEY` | — | Groq API key for LLM Co-Pilot |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model ID |
| `LLM_PROVIDER` | `groq` | `groq` \| `bedrock` \| `offline` |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `ALLOW_DEMO` | `true` | Enable demo mode with synthetic data |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for caching (optional) |

---

## License

Research and evaluation use only. Not licensed for production deployment without review.
