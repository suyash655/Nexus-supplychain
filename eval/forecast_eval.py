"""
NEXUS Evaluation — Time Series Forecast Benchmark
===================================================
Evaluates the Holt-Winters exponential smoothing engine against standard
baselines (Naive and Seasonal-Naive) over held-out periods across 5 random seeds.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
backend_path = os.path.join(REPO_ROOT, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.engines.forecaster import TimeSeriesForecaster


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def compute_smape(actual: np.ndarray, predicted: np.ndarray) -> float:
    denom = np.abs(actual) + np.abs(predicted) + 1e-6
    return float(np.mean(200.0 * np.abs(actual - predicted) / denom))


def compute_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - predicted)))


def compute_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def generate_supplier_delay_series(seed: int, n_suppliers: int = 15, n_months: int = 24) -> List[List[float]]:
    """
    Simulate monthly average delivery delays with trend, quarterly seasonality,
    and autocorrelated noise.
    """
    rng = np.random.default_rng(seed)
    all_series = []

    # Seasonal quarters: Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec holiday rush)
    seasonal_effects = [-0.5, 0.2, -0.3, 1.8]

    for _ in range(n_suppliers):
        base = rng.uniform(2.0, 5.0)
        trend_slope = rng.uniform(-0.05, 0.12)
        noise_scale = rng.uniform(0.3, 0.8)

        series = []
        val = base
        for t in range(n_months):
            season = seasonal_effects[t % 4]
            noise = rng.normal(0, noise_scale)
            val = max(0.5, base + trend_slope * t + season + noise)
            series.append(round(float(val), 2))
        all_series.append(series)

    return all_series


def run_forecast_evaluation(seeds: List[int] = None, holdout_periods: int = 3) -> Dict[str, Any]:
    if seeds is None:
        seeds = [0, 1, 2, 3, 4]

    forecaster = TimeSeriesForecaster()

    metrics_by_method = {
        "Naive baseline": {"smape": [], "mae": [], "rmse": []},
        "Seasonal-naive baseline": {"smape": [], "mae": [], "rmse": []},
        "Holt-Winters (NEXUS)": {"smape": [], "mae": [], "rmse": []},
    }

    per_seed_runs = []

    for seed in seeds:
        series_list = generate_supplier_delay_series(seed=seed, n_suppliers=15, n_months=24)

        seed_actuals = []
        seed_naive = []
        seed_snaive = []
        seed_hw = []

        for series in series_list:
            train = series[:-holdout_periods]
            test = np.array(series[-holdout_periods:])

            # 1. Naive: repeat the last train value
            naive_pred = np.array([train[-1]] * holdout_periods)

            # 2. Seasonal-naive: repeat the value from 4 periods ago
            # For period t, use t-4
            snaive_pred = np.array([train[-4 + i] for i in range(holdout_periods)])

            # 3. Holt-Winters
            hw_forecasts, _ = forecaster._holt_winters_forecast(train, periods=holdout_periods)
            hw_pred = np.array([f["p50"] for f in hw_forecasts])

            seed_actuals.append(test)
            seed_naive.append(naive_pred)
            seed_snaive.append(snaive_pred)
            seed_hw.append(hw_pred)

        act_flat = np.concatenate(seed_actuals)
        naive_flat = np.concatenate(seed_naive)
        snaive_flat = np.concatenate(seed_snaive)
        hw_flat = np.concatenate(seed_hw)

        metrics_by_method["Naive baseline"]["smape"].append(compute_smape(act_flat, naive_flat))
        metrics_by_method["Naive baseline"]["mae"].append(compute_mae(act_flat, naive_flat))
        metrics_by_method["Naive baseline"]["rmse"].append(compute_rmse(act_flat, naive_flat))

        metrics_by_method["Seasonal-naive baseline"]["smape"].append(compute_smape(act_flat, snaive_flat))
        metrics_by_method["Seasonal-naive baseline"]["mae"].append(compute_mae(act_flat, snaive_flat))
        metrics_by_method["Seasonal-naive baseline"]["rmse"].append(compute_rmse(act_flat, snaive_flat))

        metrics_by_method["Holt-Winters (NEXUS)"]["smape"].append(compute_smape(act_flat, hw_flat))
        metrics_by_method["Holt-Winters (NEXUS)"]["mae"].append(compute_mae(act_flat, hw_flat))
        metrics_by_method["Holt-Winters (NEXUS)"]["rmse"].append(compute_rmse(act_flat, hw_flat))

        per_seed_runs.append({
            "seed": seed,
            "n_series": len(series_list),
            "holdout_periods": holdout_periods,
            "naive_smape": metrics_by_method["Naive baseline"]["smape"][-1],
            "snaive_smape": metrics_by_method["Seasonal-naive baseline"]["smape"][-1],
            "hw_smape": metrics_by_method["Holt-Winters (NEXUS)"]["smape"][-1],
        })

    summary = {}
    for method, mets in metrics_by_method.items():
        summary[method] = {
            "smape_mean": round(float(np.mean(mets["smape"])), 2),
            "smape_std": round(float(np.std(mets["smape"])), 2),
            "mae_mean": round(float(np.mean(mets["mae"])), 3),
            "mae_std": round(float(np.std(mets["mae"])), 3),
            "rmse_mean": round(float(np.mean(mets["rmse"])), 3),
            "rmse_std": round(float(np.std(mets["rmse"])), 3),
        }

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "python_version": sys.version.split()[0],
        "seeds": seeds,
        "holdout_periods": holdout_periods,
        "summary": summary,
        "per_seed_runs": per_seed_runs,
    }

    out_file = os.path.join(REPO_ROOT, "eval", "results", "forecast_eval.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

    return output


def print_summary_table(data: Dict[str, Any]):
    print("\n### Forecasting Evaluation (Hold-out last 3 periods, 5 seeds, N=15 suppliers)\n")
    print("| Method | sMAPE (%) | MAE (days) | RMSE (days) |")
    print("|---|---|---|---|")
    for method, s in data["summary"].items():
        smape_str = f"{s['smape_mean']:.1f}% ± {s['smape_std']:.1f}%"
        mae_str = f"{s['mae_mean']:.2f} ± {s['mae_std']:.2f}"
        rmse_str = f"{s['rmse_mean']:.2f} ± {s['rmse_std']:.2f}"
        print(f"| {method} | {smape_str} | {mae_str} | {rmse_str} |")
    print("\nResults written to: eval/results/forecast_eval.json\n")


if __name__ == "__main__":
    results = run_forecast_evaluation()
    print_summary_table(results)
