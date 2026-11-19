"""
NEXUS Evaluation — Anomaly Detection Benchmark
================================================
Compares NEXUS's Isolation Forest pipeline against standard statistical baselines
(Z-Score and IQR) across 5 independent random seeds with ground-truth labels.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

# Ensure backend and supex1 are on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
backend_path = os.path.join(REPO_ROOT, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.engines.analyzer import AnomalyDetector
from eval.synth_data import generate_synthetic_supply_chain_data


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def run_zscore_baseline(df: pd.DataFrame, threshold: float = 3.0) -> np.ndarray:
    n = len(df)
    flags = np.zeros(n, dtype=int)
    for col in ["delay_days", "cost"]:
        if col in df.columns:
            vals = df[col].astype(float).values
            mean = np.mean(vals)
            std = np.std(vals)
            if std > 1e-6:
                z = np.abs((vals - mean) / std)
                flags[z > threshold] = 1
    return flags


def run_iqr_baseline(df: pd.DataFrame, multiplier: float = 1.5) -> np.ndarray:
    n = len(df)
    flags = np.zeros(n, dtype=int)
    for col in ["delay_days", "cost"]:
        if col in df.columns:
            vals = df[col].astype(float).values
            q25, q75 = np.percentile(vals, [25, 75])
            iqr = q75 - q25
            if iqr > 1e-6:
                lower = q25 - multiplier * iqr
                upper = q75 + multiplier * iqr
                flags[(vals < lower) | (vals > upper)] = 1
    return flags


def run_nexus_detector(df: pd.DataFrame) -> np.ndarray:
    n = len(df)
    flags = np.zeros(n, dtype=int)
    detector = AnomalyDetector(contamination=0.08)
    res = detector.detect(df)
    for item in res.get("anomalies", []):
        idx = item.get("index")
        if idx is not None and 0 <= idx < n:
            flags[idx] = 1
    return flags


def run_anomaly_evaluation(seeds: List[int] = None) -> Dict[str, Any]:
    if seeds is None:
        seeds = [0, 1, 2, 3, 4]

    results_by_method = {
        "Z-score baseline": {"precision": [], "recall": [], "f1": []},
        "IQR baseline": {"precision": [], "recall": [], "f1": []},
        "Isolation Forest (NEXUS)": {"precision": [], "recall": [], "f1": []},
    }

    per_seed_details = []

    for seed in seeds:
        df_data, df_labels = generate_synthetic_supply_chain_data(seed=seed, n_suppliers=20, n_periods=18)
        y_true = df_labels["is_anomaly"].values

        pred_z = run_zscore_baseline(df_data)
        pred_iqr = run_iqr_baseline(df_data)
        pred_nexus = run_nexus_detector(df_data)

        eval_z = evaluate_predictions(y_true, pred_z)
        eval_iqr = evaluate_predictions(y_true, pred_iqr)
        eval_nexus = evaluate_predictions(y_true, pred_nexus)

        results_by_method["Z-score baseline"]["precision"].append(eval_z["precision"])
        results_by_method["Z-score baseline"]["recall"].append(eval_z["recall"])
        results_by_method["Z-score baseline"]["f1"].append(eval_z["f1"])

        results_by_method["IQR baseline"]["precision"].append(eval_iqr["precision"])
        results_by_method["IQR baseline"]["recall"].append(eval_iqr["recall"])
        results_by_method["IQR baseline"]["f1"].append(eval_iqr["f1"])

        results_by_method["Isolation Forest (NEXUS)"]["precision"].append(eval_nexus["precision"])
        results_by_method["Isolation Forest (NEXUS)"]["recall"].append(eval_nexus["recall"])
        results_by_method["Isolation Forest (NEXUS)"]["f1"].append(eval_nexus["f1"])

        per_seed_details.append({
            "seed": seed,
            "total_rows": len(df_data),
            "true_anomalies": int(np.sum(y_true)),
            "zscore": eval_z,
            "iqr": eval_iqr,
            "nexus": eval_nexus,
        })

    summary = {}
    for method, metrics in results_by_method.items():
        summary[method] = {
            "precision_mean": round(float(np.mean(metrics["precision"])), 4),
            "precision_std": round(float(np.std(metrics["precision"])), 4),
            "recall_mean": round(float(np.mean(metrics["recall"])), 4),
            "recall_std": round(float(np.std(metrics["recall"])), 4),
            "f1_mean": round(float(np.mean(metrics["f1"])), 4),
            "f1_std": round(float(np.std(metrics["f1"])), 4),
        }

    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "python_version": sys.version.split()[0],
        "seeds": seeds,
        "n_seeds": len(seeds),
        "summary": summary,
        "per_seed_runs": per_seed_details,
    }

    out_file = os.path.join(REPO_ROOT, "eval", "results", "anomaly_eval.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2)

    return output_data


def print_summary_table(data: Dict[str, Any]):
    print("\n### Anomaly Detection Evaluation (5 seeds, N=1,800 rows per seed)\n")
    print("| Method | Precision | Recall | F1 Score |")
    print("|---|---|---|---|")
    for method, s in data["summary"].items():
        p_str = f"{s['precision_mean']:.3f} ± {s['precision_std']:.3f}"
        r_str = f"{s['recall_mean']:.3f} ± {s['recall_std']:.3f}"
        f1_str = f"{s['f1_mean']:.3f} ± {s['f1_std']:.3f}"
        print(f"| {method} | {p_str} | {r_str} | {f1_str} |")
    print("\nResults written to: eval/results/anomaly_eval.json\n")


if __name__ == "__main__":
    results = run_anomaly_evaluation()
    print_summary_table(results)
