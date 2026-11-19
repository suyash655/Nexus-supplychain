# NEXUS Evaluation Suite

This directory contains the automated, reproducible evaluation and benchmarking framework for NEXUS.

Every metric in the project documentation and README is generated directly by this code.

---

## 1. Directory Structure

```
eval/
├── __init__.py
├── synth_data.py          # Ground-truth synthetic supply chain dataset generator
├── anomaly_eval.py        # Isolation Forest vs. Z-Score and IQR baselines (5 seeds)
├── forecast_eval.py       # Holt-Winters vs. Naive and Seasonal-Naive baselines (5 seeds)
├── risk_ranking_eval.py   # Composite RiskScorer Recall@k and Spearman rank correlation
├── perf_bench.py          # Pipeline latency and memory benchmark (1k, 5k, 20k rows)
├── run_all.py             # Master runner executing all benchmarks sequentially
├── render_readme.py       # Inject verified results directly into README.md
├── requirements.txt       # Dependencies required for running evaluation
├── agent/
│   ├── harness.py         # 5-node mitigation agent reliability and injection test harness
│   └── scenarios/         # 5 operational and adversarial test scenarios (JSON)
└── results/               # Committed JSON metric outputs with Git commit SHAs
    ├── anomaly_eval.json
    ├── forecast_eval.json
    ├── risk_ranking_eval.json
    ├── agent_eval.json
    ├── perf_bench.json
    └── run_all_summary.json
```

---

## 2. Quick Reproduction

To run the entire evaluation suite from scratch:

```bash
# 1. Ensure Python dependencies are installed
pip install -r eval/requirements.txt

# 2. Generate the sample synthetic supply chain dataset
python eval/synth_data.py

# 3. Run all evaluation benchmarks
python -m eval.run_all

# 4. Render updated benchmark numbers into README.md
python eval/render_readme.py
```

---

## 3. Evaluated Components & Ground Truth Methodology

1. **Anomaly Detection (`anomaly_eval.py`)**:
   Generates 1,800 transactions per seed across 20 suppliers with injected anomalies (delay spikes $>3\sigma$, cost surges $>2.5\times$, defect bursts, level shifts). Evaluates Precision, Recall, and F1 across 5 fixed random seeds ($0, 1, 2, 3, 4$).
2. **Time Series Forecasting (`forecast_eval.py`)**:
   Generates 24-month delay time series per supplier with trend and quarterly seasonality. Evaluates sMAPE, MAE, and RMSE against held-out last 3 periods.
3. **Risk Prioritization (`risk_ranking_eval.py`)**:
   Plants 5 critical suppliers with graded degradation among 15 normal suppliers. Measures Recall@3, Recall@5, and Spearman rank correlation ($\rho$).
4. **Agent Reliability & Safety (`agent/harness.py`)**:
   Tests the 5-node LangGraph mitigation workflow across 5 scenarios (including adversarial prompt injection attempts). Enforces `MitigationPlan` Pydantic schema validation, tool allowlist enforcement, and server-side RBAC approval gating.
5. **Throughput & Scalability (`perf_bench.py`)**:
   Benchmarks full end-to-end execution of `SupplyChainAnalyzer.full_analysis()` at 1,000, 5,000, and 20,000 rows, logging latency and peak heap memory via `tracemalloc`.
