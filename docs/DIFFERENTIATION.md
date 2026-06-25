# Nexus — Competitive Differentiation

> **Purpose:** This document articulates what makes Project Nexus genuinely different
> from every competitor in the supply chain intelligence space. This is the moat.
> Use this in portfolio presentations, investor conversations, and technical interviews.

---

## 1 — CAUSAL INTELLIGENCE (vs Correlational Risk)

Nexus is the **only** platform in this competitive landscape that uses
**Bayesian Causal Inference (BCI)**.

### What competitors do (Resilinc, Everstream):
They surface correlations:
> *"Supplier X disruption correlates with delivery delay at Customer Y."*

This tells you WHAT happened but not WHY.

### What Nexus does:
Nexus answers **WHY** — which upstream node in the causal graph actually caused
the downstream failure, and with what counterfactual impact.

**Technical detail:**
- The BCI engine constructs a directed acyclic graph (DAG) of supply chain
  relationships from historical transaction data
- It performs **do-calculus interventions** to estimate causal effects:
  *"If Supplier A had NOT experienced a port closure, would Customer Y's
  inventory shortage still have occurred?"*
- The answer comes with a **counterfactual probability** — not just a
  correlation coefficient

**Why this matters:**
- Correlational platforms trigger false alarms (correlation ≠ causation)
- Causal platforms identify root causes, enabling targeted interventions
- This is **publishable research-level AI**, not just ML feature engineering

**Enterprise value:**
- Reduces mean-time-to-root-cause from days to seconds
- Eliminates "blame the wrong supplier" risk
- Provides legally defensible explanations for procurement decisions

---

## 2 — TEMPORAL GRAPH NATIVE (vs Static Snapshots)

Temporal Graph Networks treat the supply chain as a **dynamic graph** where
edges and relationships evolve over time.

### What competitors do:
They take periodic snapshots of the supply chain network:
> *"Here's what the supplier graph looked like last month."*

Snapshots miss the dynamics — a supplier that was fine last month may be
degrading right now.

### What Nexus does:
Nexus provides **continuous, time-aware risk propagation**:
- A disruption at Node A at time T propagates with **learned temporal decay**
  to Node B at time T+k
- Edge weights (delay, cost, volume) are tracked monthly with trend detection
  via linear regression
- Holt's linear trend method forecasts where each supplier relationship is heading
- SPOF (Single Point of Failure) detection uses diversity ratios over time,
  not static thresholds

**Technical detail:**
- Per-node temporal memory tracks delay/cost history with exponential decay weighting
- Neighbourhood aggregation (2-round mean-pool with 0.7/0.3 self/neighbour blend)
  creates relationship-aware embeddings
- Seasonal autocorrelation detects cyclical disruption patterns
- Trajectory-adjusted risk scores penalise worsening trends more than
  stable-but-high baselines

**Why this matters:**
- A supplier with rising delays (from 2 → 5 days) is flagged as higher risk
  than a supplier with stable delays (steady at 7 days) — even though the
  second has higher absolute delays
- This catches problems BEFORE they become crises

---

## 3 — FULLY AUDITABLE & OPEN

Every inference is explainable. Every model is yours. No black box.

### What competitors do:
- Resilinc and Everstream are SaaS black boxes
- You get a risk score; you don't get the model that produced it
- You can't audit the weights, features, or training data
- You can't modify the model for your specific use case

### What Nexus does:
- **Full source code** — every algorithm, every weight, every decision tree
- **BCI explanations** — causal graphs with interventional probabilities
- **XAI engine** — SHAP-based feature importance for every ML prediction
- **Audit trail** — every API call, every model invocation, every decision logged

**Why this matters in regulated industries:**
| Industry | Requirement | Nexus Coverage |
|----------|------------|----------------|
| **Pharmaceuticals** | FDA 21 CFR Part 11 — audit trail for supply chain decisions | ✅ Full audit log |
| **Defense** | DFARS/CMMC — explainable AI for procurement | ✅ BCI + XAI |
| **Food Safety** | FSMA — traceable root cause for contamination events | ✅ Causal graph |
| **Automotive** | IATF 16949 — supplier risk assessment evidence | ✅ Temporal risk scores |

**In regulated industries, a black-box risk score is a legal liability.**
Nexus provides the evidence chain that regulators require.

---

## 4 — ZERO VENDOR LOCK-IN

Self-hosted on AWS, Azure, GCP, or a $5 VPS. Your data never leaves your network.

### Cost comparison:

| Platform | Annual Cost (Enterprise) | Deployment |
|----------|------------------------|------------|
| Resilinc | ~$150,000–500,000/yr | SaaS only |
| Everstream | ~$100,000–300,000/yr | SaaS only |
| SAP Ariba | ~$200,000+/yr (with SAP stack) | SaaS + on-prem SAP |
| **Nexus** | **$0 + your AWS bill** | Self-hosted anywhere |

### What "$0 + AWS bill" actually means:

| AWS Component | Monthly Cost (small deployment) |
|---------------|-------------------------------|
| ECS Fargate (2 tasks, 0.5 vCPU, 1GB) | ~$30 |
| RDS PostgreSQL (db.t3.micro) | ~$15 |
| ALB | ~$20 |
| S3 (10GB documents) | ~$0.25 |
| Bedrock (Claude 3.5 Sonnet, 1000 queries/mo) | ~$15 |
| **Total** | **~$80/month** |

That's **$960/year** vs **$150,000+/year** for Resilinc.

### Additional advantages:
- **No data residency concerns** — runs in your VPC, your region, your compliance boundary
- **No contract negotiations** — MIT license, deploy today
- **No feature gating** — every feature available at every tier
- **Fork and customise** — modify the BCI model for your industry, retrain on your data
- **No vendor sunset risk** — if the project goes dormant, you own the code

---

## 5 — SUMMARY: WHY NEXUS WINS

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEXUS COMPETITIVE MOAT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CAUSAL ≠ CORRELATIONAL                                     │
│     Only platform with Bayesian do-calculus on supply chains    │
│                                                                 │
│  2. TIME-AWARE ≠ SNAPSHOT                                      │
│     Continuous temporal risk propagation, not monthly reports    │
│                                                                 │
│  3. GLASS BOX ≠ BLACK BOX                                      │
│     Every decision auditable, explainable, legally defensible   │
│                                                                 │
│  4. $960/yr ≠ $150K/yr                                         │
│     Same intelligence, 150x cheaper, no lock-in                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6 — WHAT'S NEXT

The following P0 items are being implemented now to close the remaining gaps:

1. **Real-time event monitoring** (SSE stream) — eliminates the "poll only" gap
2. **Multi-tier supplier discovery** — extends flat list to Tier N graph
3. **RAG agent** (LlamaIndex + Bedrock) — natural language supply chain Q&A
4. **Per-tenant isolation** (RLS) — enterprise-ready data boundaries

Once these ship, Nexus will match Resilinc and Everstream on table-stakes features
while maintaining its unique advantages in causal intelligence, temporal reasoning,
auditability, and cost.
