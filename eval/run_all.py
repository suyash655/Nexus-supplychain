"""
NEXUS Evaluation Suite — Master Orchestration Script
=====================================================
Executes all evaluation benchmarks (anomaly detection, forecasting, risk scoring,
mitigation agent, and pipeline performance) and produces an aggregated run summary.

Usage:
    python -m eval.run_all
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
backend_path = os.path.join(REPO_ROOT, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from eval.agent.harness import print_summary_table as print_agent_table
from eval.agent.harness import run_all_scenarios
from eval.anomaly_eval import print_summary_table as print_anomaly_table
from eval.anomaly_eval import run_anomaly_evaluation
from eval.forecast_eval import print_summary_table as print_forecast_table
from eval.forecast_eval import run_forecast_evaluation
from eval.loophole_eval import evaluate_loophole_pipeline
from eval.perf_bench import benchmark_pipeline
from eval.perf_bench import print_summary_table as print_perf_table
from eval.risk_ranking_eval import print_summary_table as print_risk_table
from eval.risk_ranking_eval import run_risk_ranking_evaluation


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def main():
    start_total = time.perf_counter()
    print("=" * 72)
    print("       NEXUS PLATFORM COMPREHENSIVE EVALUATION SUITE")
    print("=" * 72)

    git_sha = get_git_commit()
    timestamp = datetime.now(timezone.utc).isoformat()
    py_ver = sys.version.split()[0]
    print(f"Git commit: {git_sha} | Python: {py_ver} | UTC: {timestamp}\n")

    summary_manifest: Dict[str, Any] = {
        "timestamp": timestamp,
        "git_commit": git_sha,
        "python_version": py_ver,
        "evaluations": {},
        "status": "success",
    }

    try:
        print("[1/5] Running Anomaly Detection Benchmark (5 seeds)...")
        anom_res = run_anomaly_evaluation(seeds=[0, 1, 2, 3, 4])
        print_anomaly_table(anom_res)
        summary_manifest["evaluations"]["anomaly_detection"] = anom_res["summary"]

        print("[2/5] Running Time Series Forecast Benchmark (5 seeds)...")
        fore_res = run_forecast_evaluation(seeds=[0, 1, 2, 3, 4])
        print_forecast_table(fore_res)
        summary_manifest["evaluations"]["forecasting"] = fore_res["summary"]

        print("[3/5] Running Risk Ranking & Prioritization Benchmark (5 seeds)...")
        risk_res = run_risk_ranking_evaluation(seeds=[0, 1, 2, 3, 4])
        print_risk_table(risk_res)
        summary_manifest["evaluations"]["risk_ranking"] = risk_res["summary"]

        print("[4/5] Running Agent Reliability and Adversarial Safety Harness...")
        agent_res = run_all_scenarios()
        print_agent_table(agent_res)
        summary_manifest["evaluations"]["agent_reliability"] = {
            "total_scenarios": agent_res["total_scenarios"],
            "passed": agent_res["passed"],
            "pass_rate_pct": agent_res["pass_rate_pct"],
        }

        print("[5/5] Running Performance and Scalability Benchmark (1k, 5k, 20k rows)...")
        perf_res = benchmark_pipeline(row_counts=[1000, 5000, 20000])
        print_perf_table(perf_res)
        summary_manifest["evaluations"]["performance"] = perf_res["benchmarks"]

        print("[6/6] Running Synthetic Ground-Truth & Loophole Verification Benchmark...")
        loophole_res = evaluate_loophole_pipeline()
        summary_manifest["evaluations"]["loophole_verification"] = loophole_res

    except Exception as e:
        print(f"\n[ERROR] Evaluation run encountered fatal failure: {e}", file=sys.stderr)
        summary_manifest["status"] = "failed"
        summary_manifest["error"] = str(e)
        raise

    total_duration = time.perf_counter() - start_total
    summary_manifest["total_duration_seconds"] = round(total_duration, 2)

    summary_file = os.path.join(REPO_ROOT, "eval", "results", "run_all_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary_manifest, f, indent=2)

    print("=" * 72)
    print(f" ALL EVALUATION SUITES COMPLETED IN {total_duration:.1f}s — ALL METRICS RECORDED")
    print(" Aggregated manifest written to: eval/results/run_all_summary.json")
    print("=" * 72)


if __name__ == "__main__":
    main()
