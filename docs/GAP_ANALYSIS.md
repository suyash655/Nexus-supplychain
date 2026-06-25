# Nexus — Competitive Gap Analysis

> **Last updated:** 2026-06-15
> **Author:** Nexus Engineering
> **Purpose:** Brutally honest comparison of Project Nexus against direct competitors.
> Identifies every material gap and provides a prioritised fix plan for each.

---

## 1 — Competitor Profiles

### 1.1 Resilinc (resilinc.ai)
| Dimension | Detail |
|-----------|--------|
| **Multi-tier mapping** | Validated Tier 1 → Tier N supplier discovery (automated) |
| **Agentic AI** | MCP + Agent-to-Agent (A2A) interop (launched March 2026) |
| **Disruption management** | 24/7 autonomous agents with governance guardrails |
| **Event monitoring** | EventWatchAI — real-time news, geopolitical, natural disaster signals |
| **Risk scoring** | RiskShield — per-supplier scoring across thousands of feeds |
| **Compliance** | Human Rights (UFLPA) + Tariff compliance agents |
| **Enterprise posture** | SOC 2, tenant isolation, full audit trail |

**Where Nexus is stronger than Resilinc:**
- Open BCI (Bayesian Causal Inference) engine with interpretable causal graphs
- Temporal Graph Networks for time-aware node-level risk propagation
- Fully open-source, self-hostable — zero vendor lock-in
- Cost: $0 vs Resilinc's six-figure enterprise contracts

### 1.2 Everstream Analytics
| Dimension | Detail |
|-----------|--------|
| **Predictive intelligence** | Disruption prediction across logistics, climate, ESG, geopolitics |
| **API-first** | Plugs into ERP and TMS systems via REST/GraphQL |
| **Sustainability** | Deep ESG metrics alongside risk scoring |
| **Data ingestion** | Structured + unstructured global data at scale |

**Where Nexus is stronger than Everstream:**
- Causal inference (Everstream is correlational — BCI gives WHY, not just WHAT)
- Graph-native temporal reasoning via TGN
- Full code ownership and auditability of AI models

### 1.3 SAP Ariba (Supply Chain Risk Module)
| Dimension | Detail |
|-----------|--------|
| **ERP integration** | Native SAP ecosystem integration |
| **Procurement** | Risk + procurement in one platform |
| **Supplier network** | Largest global supplier network (millions of companies) |

**Nexus gap vs SAP Ariba:**
- No ERP/SAP connector
- No procurement workflow
- No supplier portal

### 1.4 LlamaIndex / LangChain (Enterprise RAG Platforms)
These are NOT supply chain tools but represent the state-of-the-art agentic RAG
pipeline that Nexus's planned RAG agent must match or exceed.

| Benchmark | Target |
|-----------|--------|
| Retrieval latency | Sub-500ms |
| Multi-document reasoning | ✅ Required |
| Source attribution | ✅ Required |
| Tool-calling loops | Multi-step ReAct, not single-shot |

---

## 2 — Gap Matrix

| # | Feature | Resilinc | Everstream | Nexus Current | Nexus Target | Priority |
|---|---------|----------|------------|---------------|--------------|----------|
| 1 | Real-time event monitoring | ✅ | ✅ | ❌ (poll only) | Webhook + SSE stream | **P0** |
| 2 | Multi-tier supplier graph | ✅ | ✅ | ❌ (flat list) | TGN sub-tier discovery | **P0** |
| 3 | Causal inference (WHY) | ❌ | ❌ | ✅ (BCI) | Differentiator — expand | **P0** |
| 4 | RAG agent over supply data | ✅ | Partial | ❌ | LlamaIndex + Bedrock | **P0** |
| 5 | ERP/API integration connector | ✅ | ✅ | ❌ | REST webhook ingest | P1 |
| 6 | Autonomous agentic actions | ✅ | ❌ | ❌ | Bedrock AgentCore | P1 |
| 7 | Compliance modules (ESG/UFLPA) | ✅ | ✅ | ❌ | Rule-based + LLM classifier | P1 |
| 8 | Per-tenant data isolation | ✅ | ✅ | ❌ (single DB) | Row-level security (Postgres) | **P0** |
| 9 | Audit trail / explainability | ✅ | Partial | ❌ | BCI explanation API | P1 |
| 10 | Real-time alerting | ✅ | ✅ | ❌ | SNS + WebSocket push | P1 |
| 11 | Mobile / PWA | ❌ | ❌ | ❌ | Next.js PWA manifest | P2 |
| 12 | SSO / enterprise auth | ✅ | ✅ | ❌ | NextAuth + Cognito | P1 |

---

## 3 — Fix Plans (Expanded)

### 3.1 — [P0] Real-Time Event Monitoring

**Current state:** Frontend polls backend on a timer. No push notifications.

**Fix plan:**
1. Create `SupplyChainEvent` schema (Pydantic) + SQLAlchemy model
2. `POST /api/events/ingest` — accepts JSON payloads matching the event schema
3. `GET /api/events/stream` — Server-Sent Events (SSE) endpoint pushing new events
4. Background task using `asyncio` periodic monitoring loop
5. Frontend: `useEventStream()` React hook connecting via `EventSource`
6. Zustand store for client-side event accumulation

**Acceptance criteria:**
- Ingested event appears in the SSE stream within 1 second
- Frontend renders the event without page refresh

---

### 3.2 — [P0] Multi-Tier Supplier Graph (Sub-Tier Discovery)

**Current state:** Supplier data is a flat list. No Tier 2/3/N relationships.

**Fix plan:**
1. Add `discover_subtier_relationships(node_id)` to `TemporalTrendEngine`
2. Returns `list[SupplierNode]` — mocked initially, interface ready for Dun & Bradstreet / Panjiva
3. Expose at `GET /api/suppliers/{id}/subtier`
4. Frontend: extend force-graph to render discovered sub-tiers as expandable clusters

**Acceptance criteria:**
- API returns valid sub-tier mock data for any supplier ID
- Interface is pluggable (swap mock for real API without code changes)

---

### 3.3 — [P0] Causal Inference Expansion (Differentiator)

**Current state:** BCI engine exists and works. It's already a differentiator.

**Fix plan:**
1. Document the causal inference advantage in DIFFERENTIATION.md
2. Add `/api/bci/explain` endpoint for human-readable causal explanations
3. Integrate BCI output as a RAG agent tool (Fix 24)

**Acceptance criteria:**
- BCI engine is used as a tool by the RAG agent
- Causal explanations are surfaced in chat responses

---

### 3.4 — [P0] RAG Agent Over Supply Chain Data

**Current state:** No RAG capability. Copilot is prompt-based, no retrieval.

**Fix plan:**
1. LlamaIndex + Bedrock (Claude 3.5 Sonnet) + Titan Embeddings v2
2. Ingestion: PostgreSQL events → documents, S3 PDFs → parsed + chunked
3. ReAct agent with tools: event search, BCI causal query, document retrieval
4. FastAPI endpoints: `/api/rag/query` (sync) + `/api/rag/query/stream` (SSE)
5. Frontend: `NexusChat.tsx` with streaming token display

**Acceptance criteria:**
- Agent answers "Which suppliers had disruptions?" using indexed event data
- Agent uses BCI tool for "why" questions
- Sub-500ms retrieval latency on indexed data

---

### 3.5 — [P0] Per-Tenant Data Isolation

**Current state:** Single SQLite DB, no tenant boundaries. All data visible to all users.

**Fix plan:**
1. Add `tenant_id: UUID` column to every table
2. Row Level Security (RLS) policies on PostgreSQL
3. Tenant-aware `get_db_for_tenant` FastAPI dependency
4. Set `app.current_tenant_id` on every DB session

**Acceptance criteria:**
- RLS SQL migration script is ready for PostgreSQL
- Tenant-aware dependency is available for all routers
- Backward compatible: existing SQLite dev mode continues to work

---

### 3.6 — [P1] ERP/API Integration Connector

**Target:** REST webhook ingest endpoint that accepts generic supply chain payloads
from SAP, Oracle, or any ERP system.

**Deferred to:** Phase 2 — after P0 items are stable.

---

### 3.7 — [P1] Autonomous Agentic Actions

**Target:** Bedrock AgentCore runtime with governed autonomous decision loops.

**Deferred to:** Phase 2 — requires AgentCore GA and governance framework.

---

### 3.8 — [P1] Compliance Modules (ESG/UFLPA)

**Target:** Rule-based + LLM classifier for ESG and UFLPA compliance screening.

**Deferred to:** Phase 2 — ESG engine exists but needs compliance rule sets.

---

### 3.9 — [P1] Audit Trail / Explainability

**Target:** BCI explanation API + full audit logging of all AI decisions.

**Deferred to:** Phase 2 — AuditLog model exists, needs BCI integration.

---

### 3.10 — [P1] Real-Time Alerting

**Target:** SNS + WebSocket push for critical risk alerts.

**Deferred to:** Phase 2 — SSE infrastructure (P0 Fix 5) provides the foundation.

---

### 3.11 — [P2] Mobile / PWA

**Target:** Next.js PWA manifest + service worker for offline-capable mobile access.

**Deferred to:** Phase 3.

---

### 3.12 — [P1] SSO / Enterprise Auth

**Target:** NextAuth + AWS Cognito for enterprise SSO (SAML, OIDC).

**Deferred to:** Phase 2 — JWT auth exists, needs Cognito integration.
