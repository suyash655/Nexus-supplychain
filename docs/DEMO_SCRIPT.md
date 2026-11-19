# NEXUS — 3-Minute Walkthrough Video Script

**Target Duration**: 3:00 (180 seconds)  
**Speaker**: Suyash Jaysawal  
**Sample Dataset**: [`data/sample/sample_supply_chain_synthetic.csv`](file:///d:/supex1/data/sample/sample_supply_chain_synthetic.csv)  
**Required Local Setup**:
1. Backend running: `cd backend && python -m uvicorn app.main:app --port 8000`
2. Frontend running: `cd frontend && npm run dev` (open `http://localhost:3000`)

---

## Timeline & Scene Progression

### Scene 1: The Problem & The Hook (0:00 – 0:25)
- **Visual**: NEXUS landing page (`http://localhost:3000`), dark UI with high-contrast metrics.
- **Action**: Hover over the headline: *"Supply Chain Risk Intelligence Platform"*. Click **"Skip to Demo"** to access the live workspace.
- **Audio / Voiceover**:
  > *"A single delayed shipment from a Tier-2 supplier rarely stays isolated. It cascades down the graph into component shortages, factory downtime, and missed customer SLAs. But most supply chain teams are stuck either reacting weeks late in spreadsheets or waiting months for heavyweight ERP integrations.
  >
  > I built NEXUS to solve this: go from a raw supplier CSV to ranked risk scores, explainable predictions, and an actionable mitigation plan drafted by an AI agent—with a strict human-in-the-loop approval gate—in under 60 seconds."*

---

### Scene 2: Data Ingestion & Pipeline (`/upload`) (0:25 – 0:50)
- **Visual**: Navigate to `http://localhost:3000/upload`.
- **Action**: Drag and drop `data/sample/sample_supply_chain_synthetic.csv` into the upload zone. Click **"Run Full Analysis"**.
- **Audio / Voiceover**:
  > *"Let's upload a sample dataset containing 1,800 shipments across 20 suppliers. 
  > 
  > In the background, FastAPI's upload parser inspects the file, sanitizes against formula injections, and atomically stores the records. 
  > 
  > Instead of blocking the UI, a multi-stage ML pipeline runs in the background: Isolation Forest for multivariate anomaly detection, Holt-Winters exponential smoothing for delay forecasting, and NetworkX for topological graph analysis. Cached results write directly to SQLite or PostgreSQL, keeping frontend dashboards instant."*

---

### Scene 3: Executive Dashboard & Forecasting (`/dashboard` & `/analytics`) (0:50 – 1:25)
- **Visual**: Navigate to `http://localhost:3000/dashboard`, then click over to `/analytics`.
- **Action**: Point to KPI cards (Supplier Risk Index, Critical Anomalies, Projected Disruptions). Scroll down to the Holt-Winters Forecast chart showing the P10/P90 confidence cone.
- **Audio / Voiceover**:
  > *"On the dashboard, we immediately see our high-risk vendors prioritized. 
  > 
  > Over on the Analytics page, our time-series forecaster evaluates delay trends with quarterly seasonality. For series with sufficient history, it fits an additive Holt-Winters model with grid-searched alpha, beta, and gamma parameters.
  > 
  > Notice the shaded confidence bands: those are empirical P10 and P90 prediction intervals scaled by horizon depth. Instead of just giving a single point estimate, NEXUS communicates statistical uncertainty directly to the analyst."*

---

### Scene 4: Graph Cascade & Blast Radius Simulation (`/graph`) (1:25 – 1:55)
- **Visual**: Navigate to `http://localhost:3000/graph`.
- **Action**: View the interactive 2D force-directed supplier graph. Click on node `Supplier-A1`. Click the **"Simulate Cascade Failure"** button. Watch downstream factory nodes and warehouses turn red.
- **Audio / Voiceover**:
  > *"Traditional risk tables treat suppliers in isolation. In the Graph Explorer, we model suppliers, SKUs, and distribution centers as a directed NetworkX graph.
  > 
  > When I click 'Simulate Cascade Failure' on Supplier-A1, the engine traverses downstream edges, calculating blast radius and terminal impact based on betweenness centrality and inventory buffer depth. 
  > 
  > We see exactly which finished products and distribution facilities are vulnerable before the physical delay occurs."*

---

### Scene 5: LangGraph Mitigation Agent & Human Approval Gate (`/mitigation`) (1:55 – 2:35)
- **Visual**: Navigate to `http://localhost:3000/mitigation`.
- **Action**: Open the pending mitigation card for `Supplier-A1`. Highlight the 5-node workflow trace (Assess Risk → Backup Search → Monte Carlo Simulation → RAG Retrieval → Draft Plan). Show the **"Pending Human Approval"** badge. Click **"Approve Plan"**.
- **Audio / Voiceover**:
  > *"When a supplier's composite risk crosses our critical threshold of 75, our LangGraph mitigation agent triggers automatically.
  > 
  > It searches the network for alternative suppliers, runs a Monte Carlo rerouting cost simulation, retrieves past incident playbooks via ChromaDB, and drafts an operational action plan.
  > 
  > Here is the critical design decision: the agent never acts autonomously. Every proposal is schema-validated with Pydantic and halted at a server-side RBAC approval gate. Only authorized managers or admins can execute an action. I'll click 'Approve'—the plan is logged to the immutable audit trail, and notifications dispatch."*

---

### Scene 6: Observability, Offline Capability & Close (2:35 – 3:00)
- **Visual**: Quickly show `docs/OBSERVABILITY.md` or the terminal log showing sanitized `<UNTRUSTED_DATA>` blocks and structured JSON agent traces. Return to GitHub repository.
- **Action**: Scroll through the README evaluation tables.
- **Audio / Voiceover**:
  > *"Under the hood, all untrusted spreadsheet text is wrapped in XML data boundary tags with automated prompt injection filtering. The system runs fully offline without external API keys using deterministic fallbacks, but integrates seamlessly with Groq, AWS Bedrock, and Langfuse tracing.
  > 
  > Every metric in the README—from anomaly detection F1 scores to pipeline throughput—is 100% reproducible with `python -m eval.run_all`.
  > 
  > The code is available on GitHub at `github.com/suyash655/Nexus-supplychain`. Thank you for watching."*
