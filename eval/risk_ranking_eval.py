"""
NEXUS Evaluation — Risk Ranking & Prioritization Benchmark
============================================================
Evaluates whether the composite RiskScorer reliably elevates high-risk suppliers
above normal suppliers, measuring Recall@k and Spearman rank correlation.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
backend_path = os.path.join(REPO_ROOT, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.engines.analyzer import RiskScorer


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def generate_risk_ranking_dataset(seed: int) -> Tuple[pd.DataFrame, Dict[str, float]]:
    rng = np.random.default_rng(seed)
    n_normal = 15
    n_critical = 5

    records = []
    supplier_true_risk = {}

    # 15 Normal suppliers
    for i in range(n_normal):
        name = f"Supplier-Norm-{i+1}"
        base_delay = rng.uniform(0.5, 2.0)
        true_risk = rng.uniform(15.0, 35.0)
        supplier_true_risk[name] = true_risk

        for _ in range(25):
            delay = max(0.0, rng.normal(base_delay, 1.0))
            cost = max(50.0, rng.normal(200.0, 15.0))
            defects = max(0.0, rng.normal(0.01, 0.005))
            records.append({
                "supplier": name,
                "delay_days": round(float(delay), 1),
                "cost": round(float(cost), 2),
                "order_quantity": 500,
                "defect_rate": round(float(defects), 4),
            })

    # 5 High-risk / Critical suppliers with graded severity
    severities = [60.0, 70.0, 80.0, 88.0, 95.0]
    for i in range(n_critical):
        name = f"Supplier-Crit-{i+1}"
        true_risk = severities[i]
        supplier_true_risk[name] = true_risk

        # Mean delay and cost variance scaled with severity
        mean_delay = 5.0 + (i * 3.5)
        cost_std = 30.0 + (i * 20.0)

        for _ in range(25):
            delay = max(0.0, rng.normal(mean_delay, 2.5))
            cost = max(50.0, rng.normal(200.0, cost_std))
            defects = max(0.0, rng.normal(0.05 + (i * 0.03), 0.01))
            records.append({
                "supplier": name,
                "delay_days": round(float(delay), 1),
                "cost": round(float(cost), 2),
                "order_quantity": 500,
                "defect_rate": round(float(defects), 4),
            })

    df = pd.DataFrame(records)
    return df, supplier_true_risk


def run_risk_ranking_evaluation(seeds: List[int] = None) -> Dict[str, Any]:
    if seeds is None:
        seeds = [0, 1, 2, 3, 4]

    scorer = RiskScorer()

    recall_at_3 = []
    recall_at_5 = []
    spearman_corrs = []

    per_seed_runs = []

    for seed in seeds:
        df, true_risk_dict = generate_risk_ranking_dataset(seed)
        scored_suppliers = scorer.score_suppliers(df)

        # Sort descending by risk score
        scored_sorted = sorted(scored_suppliers, key=lambda x: x.get("risk_score", 0), reverse=True)
        ranked_names = [s["supplier"] for s in scored_sorted]

        # Ground truth top 5 critical names
        true_sorted = sorted(true_risk_dict.items(), key=lambda x: x[1], reverse=True)
        true_top_3 = {item[0] for item in true_sorted[:3]}
        true_top_5 = {item[0] for item in true_sorted[:5]}

        pred_top_3 = set(ranked_names[:3])
        pred_top_5 = set(ranked_names[:5])

        r3 = len(pred_top_3.intersection(true_top_3)) / 3.0
        r5 = len(pred_top_5.intersection(true_top_5)) / 5.0

        # Spearman rank correlation across all 20 suppliers
        pred_scores = [next(s["risk_score"] for s in scored_suppliers if s["supplier"] == name) for name in true_risk_dict.keys()]
        actual_scores = [true_risk_dict[name] for name in true_risk_dict.keys()]

        corr, _ = stats.spearmanr(actual_scores, pred_scores)

        recall_at_3.append(r3)
        recall_at_5.append(r5)
        spearman_corrs.append(corr)

        per_seed_runs.append({
            "seed": seed,
            "recall_at_3": round(float(r3), 4),
            "recall_at_5": round(float(r5), 4),
            "spearman_corr": round(float(corr), 4),
            "top_3_predicted": ranked_names[:3],
        })

    summary = {
        "recall_at_3_mean": round(float(np.mean(recall_at_3)), 4),
        "recall_at_3_std": round(float(np.std(recall_at_3)), 4),
        "recall_at_5_mean": round(float(np.mean(recall_at_5)), 4),
        "recall_at_5_std": round(float(np.std(recall_at_5)), 4),
        "spearman_corr_mean": round(float(np.mean(spearman_corrs)), 4),
        "spearman_corr_std": round(float(np.std(spearman_corrs)), 4),
    }

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "python_version": sys.version.split()[0],
        "seeds": seeds,
        "summary": summary,
        "per_seed_runs": per_seed_runs,
    }

    out_file = os.path.join(REPO_ROOT, "eval", "results", "risk_ranking_eval.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

    return output


def print_summary_table(data: Dict[str, Any]):
    print("\n### Risk Ranking Evaluation (5 planted critical suppliers, 15 normal, 5 seeds)\n")
    print("| Metric | Mean ± Std | Target / Baseline |")
    print("|---|---|---|")
    s = data["summary"]
    print(f"| Recall@3 | {s['recall_at_3_mean']:.3f} ± {s['recall_at_3_std']:.3f} | 1.000 |")
    print(f"| Recall@5 | {s['recall_at_5_mean']:.3f} ± {s['recall_at_5_std']:.3f} | 1.000 |")
    print(f"| Spearman Rank Correlation (ρ) | {s['spearman_corr_mean']:.3f} ± {s['spearman_corr_std']:.3f} | > 0.850 |")
    print("\nResults written to: eval/results/risk_ranking_eval.json\n")


if __name__ == "__main__":
    results = run_risk_ranking_evaluation()
    print_summary_table(results)
