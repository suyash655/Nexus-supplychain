# Evaluation — Project Nexus

## Model Performance Summary

| Engine | Metric | Value | Notes |
|--------|--------|-------|-------|
| **Risk Scorer (ML Pipeline)** | What-If simulation fidelity | ~94% | vs. historical disruption outcomes |
| **T-GNN (Temporal Graph)** | Latent bottleneck detection | 2.5× baseline | vs. static predictive models |
| **Fragility Framework** | Systemic risk reduction | ~45% | via antifragile routing automation |
| **AI Co-Pilot** | Answer relevance | — | Provider-dependent (Groq / Bedrock) |

> ⚠️ These are reported figures from the research paper. Actual values depend on the dataset used.

---

## ML Pipeline Breakdown

### Stage 1 — Isolation Forest (Anomaly Detection)

- **Algorithm:** Isolation Forest (`sklearn`)
- **Purpose:** Detect statistical anomalies in supplier KPIs (cost spikes, delay outliers, quality drops)
- **Contamination:** Auto-tuned based on data distribution
- **Features used:** `delay_days`, `cost`, `quality_score`, `quantity`
- **Output:** Binary `anomaly_flag` + anomaly score per record

### Stage 2 — Holt-Winters (Demand Forecasting)

- **Algorithm:** Exponential Smoothing (additive trend + seasonality)
- **Purpose:** Forecast next-period demand at supplier-SKU level
- **Horizon:** 30 days
- **Output:** Time-series of `predicted_demand` with confidence intervals

### Stage 3 — IQR Statistical Bounds

- **Method:** Interquartile Range thresholding
- **Purpose:** Rule-based alert generation for extreme values
- **Thresholds:** Configurable via `DATA_QUALITY_THRESHOLD` env var
- **Output:** Severity-ranked alert list (`critical / warning / info`)

### Risk Score Computation

Final `risk_score` (0–100) is a weighted composite:

| Factor | Weight | Source |
|--------|--------|--------|
| Isolation Forest score | 35% | `analyzer.py` |
| Delay performance | 25% | `delay_days` column |
| Cost variance | 20% | `cost` vs. supplier baseline |
| Quality score | 15% | `quality_score` column |
| World event impact | 5% | `WorldEvent` table |

---

## Causal Genome Engine

### Methodology

1. **Structure Learning** — PC Algorithm over supplier relationship graph
2. **Parameter Estimation** — Bayesian estimation of conditional probability tables
3. **Interventional Queries** — `do(X=x)` operator (Pearl's do-calculus)
4. **Counterfactual Simulation** — Sample from posterior under intervention

### Validation

- **Fidelity:** ~94% match between `do(supplier=remove)` predictions and observed historical outcomes for 12 documented disruption events in the dataset.
- **Calibration:** Posterior probabilities within ±8% of observed frequencies.

---

## Temporal Graph Neural Network (T-GNN)

### Architecture

- **Base:** Temporal Graph Networks (Rossi et al., 2020)
- **Node features:** Risk score, centrality, delay trend, cost trend
- **Edge features:** Transaction volume, relationship age, delivery reliability
- **Time window:** Rolling 30-day window with hourly aggregation
- **Task:** Binary node classification — `disruption_risk = high/low`

### Performance vs Baselines

| Model | Latent Bottleneck Detection Rate |
|-------|----------------------------------|
| Static Graph + Threshold Rules | 1.0× (baseline) |
| Static GNN | 1.7× |
| **T-GNN (Nexus)** | **2.5×** |

---

## Structural Fragility Framework

### Vulnerability Index

Inspired by Nassim Taleb's antifragility framework. Each node receives a `fragility_score`:

```
fragility_score = α × betweenness_centrality
                + β × single_source_dependency
                + γ × cascade_depth
                - δ × redundancy_count
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| α | 0.40 | Centrality amplification factor |
| β | 0.30 | Dependency concentration penalty |
| γ | 0.20 | Cascade propagation depth |
| δ | 0.10 | Redundant supplier discount |

### Risk Reduction Results

- **Before framework:** Average systemic risk index = 0.82
- **After antifragile routing:** Average systemic risk index = 0.45
- **Reduction:** ~45%

---

## Data Quality Metrics

| Check | Pass Threshold | Action on Fail |
|-------|---------------|----------------|
| Missing values | < 15% per column | Impute with column median |
| Duplicate rows | < 5% | Auto-deduplicate |
| Schema compliance | All required cols present | Warn, continue |
| Outlier rate | < 10% | Flag, include in anomaly report |
| **Overall quality score** | ≥ 0.85 (configurable) | Analysis gated if below |

---

## Benchmarking Conditions

All reported metrics were evaluated on:

- **Dataset:** SynChain sample dataset (supply chain transactions, ~50K rows)
- **Hardware:** Standard CPU inference (no GPU required)
- **Baseline comparisons:** Traditional ERP threshold alerting + static supplier scorecards
- **Evaluation method:** 5-fold cross-validation on historical disruption outcomes

---

## Latency Profile

| Operation | Typical Duration | Notes |
|-----------|-----------------|-------|
| File upload + parse | < 2s | For files up to 50MB |
| Full ML analysis pipeline | 5–15s | Background task |
| Graph topology build | 1–3s | NetworkX computation |
| T-GNN inference | 2–5s | CPU-bound |
| Causal DAG build | 3–8s | Structure learning |
| AI Co-Pilot query | 1–3s | Groq API latency |
| ESG report generation | 2–4s | |
| Monte Carlo (10K trials) | 3–10s | CPU-bound |

---

## Known Limitations

1. **Dataset size sensitivity** — T-GNN and causal models degrade below ~500 records. Use IQR-only mode for small datasets.
2. **LLM dependency** — AI Co-Pilot quality is provider-dependent. `offline` mode returns templated responses.
3. **Single-tenant SQLite** — For concurrent users or high write volume, switch to PostgreSQL.
4. **No real-time streaming** — Scheduler minimum granularity is 15 minutes; true real-time requires Kafka/Flink integration.
5. **ESG scores are estimates** — Self-reported supplier data. No third-party verification built-in.
6. **Causal DAG validity** — Assumes stationarity of relationships. Model should be re-fit quarterly or on major dataset changes.

---

## Improvement Roadmap

| Priority | Enhancement | Expected Impact |
|----------|-------------|----------------|
| 🔴 High | PostgreSQL production backend | Concurrent users, data durability |
| 🔴 High | Real-time Kafka connector | Sub-minute disruption alerts |
| 🟡 Medium | Graph Attention Networks (GAT) | Better node embedding quality |
| 🟡 Medium | Third-party ESG data enrichment | Verified ESG scores |
| 🟡 Medium | ONNX export for ML models | 3–5× inference speedup |
| 🟢 Low | Active learning loop | Auto-improving risk model with user feedback |
| 🟢 Low | Mobile dashboard | Procurement officer on-the-go access |
