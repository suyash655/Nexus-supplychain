"""
NEXUS Evaluation — Synthetic Supply Chain Data Generator
=========================================================
Generates reproducible synthetic supply chain transaction data with known,
ground-truth anomaly injections for evaluation and benchmarking.
"""

import argparse
import os
from datetime import datetime, timedelta
from typing import Tuple

import numpy as np
import pandas as pd


def generate_synthetic_supply_chain_data(
    seed: int = 42,
    n_suppliers: int = 20,
    n_periods: int = 18,
    shipments_per_supplier_per_period: int = 5,
    anomaly_rate: float = 0.08,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic supply-chain transactions and ground-truth anomaly labels.

    Injected anomaly types:
      - delay_spike: extreme delay (>3 sigma above baseline)
      - cost_surge: unexpected price multiplier (>2.5x base cost)
      - defect_burst: elevated quality defects (>4x base defect rate)
      - level_shift: sudden structural shift in supplier delivery reliability
    """
    rng = np.random.default_rng(seed)

    supplier_names = [f"Supplier-{chr(65 + (i % 26))}{i // 26 + 1}" for i in range(n_suppliers)]
    regions = ["North America", "Europe", "APAC", "Latin America"]
    skus = [f"SKU-{100 + i}" for i in range(15)]

    # Assign persistent baseline parameters to each supplier
    supplier_profiles = {}
    for name in supplier_names:
        supplier_profiles[name] = {
            "region": rng.choice(regions),
            "base_delay": rng.uniform(0.5, 3.5),
            "delay_sigma": rng.uniform(0.5, 1.5),
            "base_cost": rng.uniform(50.0, 500.0),
            "cost_sigma": rng.uniform(5.0, 30.0),
            "base_defects": rng.uniform(0.005, 0.03),
            "skus": list(rng.choice(skus, size=rng.integers(2, 6), replace=False)),
        }

    records = []
    labels = []
    row_idx = 0

    base_start_date = datetime(2025, 1, 1)

    for period in range(n_periods):
        period_date = base_start_date + timedelta(days=period * 30)

        for supplier in supplier_names:
            prof = supplier_profiles[supplier]

            # In period 12 onwards, simulate a structural level-shift for 2 specific suppliers
            is_level_shift_active = (period >= 12) and (supplier in supplier_names[:2])

            for _ in range(shipments_per_supplier_per_period):
                shipment_date = period_date + timedelta(days=int(rng.integers(0, 28)))
                sku = rng.choice(prof["skus"])
                order_qty = int(rng.integers(50, 2000))

                # Baseline natural values
                delay = max(0.0, rng.normal(prof["base_delay"], prof["delay_sigma"]))
                cost = max(10.0, rng.normal(prof["base_cost"], prof["cost_sigma"]))
                defects = max(0.0, min(0.15, rng.normal(prof["base_defects"], 0.005)))

                if is_level_shift_active:
                    delay += 8.0
                    cost *= 1.4

                # Decide if an injected anomaly occurs
                is_anomaly = False
                anomaly_type = "none"

                if rng.random() < anomaly_rate:
                    is_anomaly = True
                    atype_roll = rng.random()
                    if atype_roll < 0.40:
                        anomaly_type = "delay_spike"
                        delay += rng.uniform(12.0, 25.0)
                    elif atype_roll < 0.70:
                        anomaly_type = "cost_surge"
                        cost *= rng.uniform(2.5, 4.0)
                    elif atype_roll < 0.90:
                        anomaly_type = "defect_burst"
                        defects = min(0.60, defects + rng.uniform(0.20, 0.45))
                    else:
                        anomaly_type = "compound"
                        delay += rng.uniform(10.0, 20.0)
                        cost *= rng.uniform(2.0, 3.5)
                        defects = min(0.50, defects + rng.uniform(0.15, 0.35))

                delivery_date = shipment_date + timedelta(days=int(round(delay + 2.0)))

                records.append({
                    "row_id": row_idx,
                    "supplier": supplier,
                    "sku": sku,
                    "region": prof["region"],
                    "order_date": shipment_date.strftime("%Y-%m-%d"),
                    "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                    "delay_days": round(float(delay), 1),
                    "cost": round(float(cost), 2),
                    "order_quantity": order_qty,
                    "defect_rate": round(float(defects), 4),
                })

                labels.append({
                    "row_id": row_idx,
                    "supplier": supplier,
                    "period": period,
                    "is_anomaly": int(is_anomaly),
                    "anomaly_type": anomaly_type,
                })

                row_idx += 1

    df_data = pd.DataFrame(records)
    df_labels = pd.DataFrame(labels)
    return df_data, df_labels


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic supply chain evaluation dataset.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for generation.")
    parser.add_argument("--n-suppliers", type=int, default=20, help="Number of distinct suppliers.")
    parser.add_argument("--n-periods", type=int, default=18, help="Number of monthly periods.")
    parser.add_argument("--out", type=str, default="data/sample/sample_supply_chain_synthetic.csv", help="Data output path.")
    parser.add_argument("--out-labels", type=str, default="data/sample/sample_supply_chain_synthetic_labels.csv", help="Labels output path.")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    df_data, df_labels = generate_synthetic_supply_chain_data(
        seed=args.seed,
        n_suppliers=args.n_suppliers,
        n_periods=args.n_periods,
    )

    df_data.to_csv(args.out, index=False)
    df_labels.to_csv(args.out_labels, index=False)

    anomaly_count = df_labels["is_anomaly"].sum()
    print(f"Generated {len(df_data)} rows across {args.n_suppliers} suppliers ({args.n_periods} periods).")
    print(f"Injected ground-truth anomalies: {anomaly_count} ({anomaly_count / len(df_data):.1%})")
    print(f"Saved dataset to: {args.out}")
    print(f"Saved labels to:  {args.out_labels}")


if __name__ == "__main__":
    main()
