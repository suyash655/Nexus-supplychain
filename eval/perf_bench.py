"""
NEXUS Evaluation — Performance and Scalability Benchmark
==========================================================
Benchmarks full ML pipeline execution time (anomaly detection, risk scoring,
forecasting, bullwhip analysis, data quality) and peak memory usage across
1k, 5k, and 20k rows.
"""

import json
import os
import platform
import subprocess
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
backend_path = os.path.join(REPO_ROOT, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.engines.analyzer import SupplyChainAnalyzer


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
        return res.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def generate_benchmark_dataset(n_rows: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_suppliers = max(5, n_rows // 100)
    suppliers = [f"Supplier-{i}" for i in range(n_suppliers)]

    base_date = pd.Timestamp("2025-01-01")
    days = rng.integers(0, 365, size=n_rows)
    dates = [base_date + pd.Timedelta(days=int(d)) for d in days]

    df = pd.DataFrame({
        "supplier": rng.choice(suppliers, size=n_rows),
        "order_date": [d.strftime("%Y-%m-%d") for d in dates],
        "delivery_date": [(d + pd.Timedelta(days=int(rng.integers(2, 10)))).strftime("%Y-%m-%d") for d in dates],
        "delay_days": np.clip(rng.normal(2.5, 2.0, size=n_rows), 0, 45).round(1),
        "cost": np.clip(rng.normal(250.0, 50.0, size=n_rows), 10, 5000).round(2),
        "order_quantity": rng.integers(50, 1000, size=n_rows),
        "defect_rate": np.clip(rng.normal(0.02, 0.01, size=n_rows), 0, 0.5).round(4),
        "sku": rng.choice([f"SKU-{i}" for i in range(25)], size=n_rows),
    })
    return df


def benchmark_pipeline(row_counts: List[int] = None) -> Dict[str, Any]:
    if row_counts is None:
        row_counts = [1000, 5000, 20000]

    analyzer = SupplyChainAnalyzer()
    benchmarks = []

    for rows in row_counts:
        df = generate_benchmark_dataset(rows)

        # Measure latency & peak memory
        tracemalloc.start()
        start_time = time.perf_counter()

        _ = analyzer.full_analysis(df)

        elapsed_sec = time.perf_counter() - start_time
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_mem / (1024 * 1024)
        throughput = rows / elapsed_sec if elapsed_sec > 0 else 0.0

        benchmarks.append({
            "rows": rows,
            "elapsed_seconds": round(float(elapsed_sec), 3),
            "throughput_rows_sec": round(float(throughput), 1),
            "peak_memory_mb": round(float(peak_mb), 2),
        })

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor(),
        "benchmarks": benchmarks,
    }

    out_file = os.path.join(REPO_ROOT, "eval", "results", "perf_bench.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

    return output


def print_summary_table(data: Dict[str, Any]):
    print(f"\n### Pipeline Performance Benchmark ({data['platform']})\n")
    print("| Row Count | Latency (s) | Throughput (rows/s) | Peak Memory (MB) |")
    print("|---|---|---|---|")
    for b in data["benchmarks"]:
        print(f"| {b['rows']:,} | {b['elapsed_seconds']:.2f} s | {b['throughput_rows_sec']:,.0f} | {b['peak_memory_mb']:.1f} MB |")
    print("\nResults written to: eval/results/perf_bench.json\n")


if __name__ == "__main__":
    results = benchmark_pipeline()
    print_summary_table(results)
