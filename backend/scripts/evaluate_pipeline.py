"""
NEXUS — Offline Evaluation Harness
====================================
Replaces the unverified "~94% simulation fidelity" claim with honest
precision/recall metrics measured against labelled historical outcomes.

Usage
-----
1. Prepare a disruption events file (see DISRUPTION_EVENTS below or
   supply a JSON file via --events-file).
2. Point --data-file at your supply chain CSV.
3. Run:
   python scripts/evaluate_pipeline.py \\
       --data-file data/samples/sample_supply_chain_data.csv \\
       --output-dir data/evaluation_results

What it measures
----------------
- Precision @ risk_score > threshold  (of flagged suppliers, % that actually disrupted)
- Recall    @ risk_score > threshold  (of disrupted suppliers, % that were flagged)
- F1 score
- Mean Absolute Error on delay forecast vs actual
- Lead time: how many days before the disruption was the supplier first flagged

Output
------
Writes evaluation_results.json and evaluation_report.md to --output-dir.

How to add real disruption events
----------------------------------
Edit DISRUPTION_EVENTS or supply a JSON file with the same structure:
[
  {
    "id": "event-001",
    "description": "Supplier X quality failure",
    "disruption_date": "2024-03-01",          # first day of disruption
    "affected_suppliers": ["Supplier_X"],      # ground truth
    "disruption_type": "quality_failure"
  }
]
The harness will:
  - Train on all data BEFORE disruption_date
  - Evaluate predictions made from that training window
  - Compare predicted high-risk suppliers against affected_suppliers
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd

# Ensure the backend package is importable
_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND))

from app.engines.analyzer import SupplyChainAnalyzer  # type: ignore
from app.engines.forecaster import TimeSeriesForecaster  # type: ignore


# ── Default disruption events (sample — replace with real history) ──────────
# Format each entry as explained in the module docstring.
SAMPLE_DISRUPTION_EVENTS: List[Dict] = [
    # These are placeholder events. Replace with real historical disruptions
    # where you know which supplier actually failed and when.
    # {
    #     "id": "event-001",
    #     "description": "Supplier quality failure (replace with real event)",
    #     "disruption_date": "2024-06-01",
    #     "affected_suppliers": ["SupplierNameHere"],
    #     "disruption_type": "quality_failure",
    # },
]


# ── Evaluation logic ─────────────────────────────────────────────────────────

def _precision_recall_f1(
    predicted_high_risk: List[str],
    actual_disrupted: List[str],
) -> Dict[str, float]:
    predicted = set(s.lower() for s in predicted_high_risk)
    actual    = set(s.lower() for s in actual_disrupted)

    tp = len(predicted & actual)
    fp = len(predicted - actual)
    fn = len(actual - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return {
        "true_positives":  tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision":       round(precision, 3),
        "recall":          round(recall, 3),
        "f1":              round(f1, 3),
    }


def _forecast_mae(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    forecaster: TimeSeriesForecaster,
) -> Optional[float]:
    """
    Compute Mean Absolute Error between forecast and actual delays
    in the test window.
    """
    date_col = next(
        (c for c in ["order_date", "delivery_date", "date"] if c in train_df.columns),
        None,
    )
    if not date_col or "delay_days" not in train_df.columns:
        return None

    trends = forecaster.analyze_trends(train_df)
    delay_forecast = trends.get("forecast", {}).get("delay", {})
    next_periods   = delay_forecast.get("next_periods", [])
    if not next_periods:
        return None

    # Actual: mean delay in the test window
    actual_mean = float(
        pd.to_numeric(test_df["delay_days"], errors="coerce").dropna().mean()
        if "delay_days" in test_df.columns
        else 0.0
    )

    predicted_p50 = next_periods[0].get("p50", next_periods[0].get("predicted_value", 0))
    mae = abs(float(predicted_p50) - actual_mean)
    return round(mae, 2)


def evaluate_event(
    full_df: pd.DataFrame,
    event: Dict,
    risk_threshold: float,
    analyzer: SupplyChainAnalyzer,
    forecaster: TimeSeriesForecaster,
) -> Dict[str, Any]:
    """
    Evaluate predictions for a single disruption event.

    Split strategy:
      - Train: all rows with order_date < disruption_date
      - Test:  all rows with order_date >= disruption_date

    Returns a result dict with precision, recall, F1, MAE, and lead time.
    """
    disruption_date = pd.to_datetime(event["disruption_date"])
    affected        = event.get("affected_suppliers", [])

    # ── Time split ──
    date_col = next(
        (c for c in ["order_date", "delivery_date", "date"] if c in full_df.columns),
        None,
    )
    if date_col:
        dates = pd.to_datetime(full_df[date_col], errors="coerce")
        train_df = full_df[dates < disruption_date].copy()
        test_df  = full_df[dates >= disruption_date].copy()
    else:
        # No date column — use row order (first 80% / last 20%)
        split = int(len(full_df) * 0.8)
        train_df = full_df.iloc[:split].copy()
        test_df  = full_df.iloc[split:].copy()

    if len(train_df) < 10:
        return {
            "event_id":    event["id"],
            "error":       f"Insufficient training data ({len(train_df)} rows before {event['disruption_date']})",
            "skipped":     True,
        }

    # ── Run risk scoring on training window ──
    ml_result    = analyzer.full_analysis(train_df)
    risk_scores  = ml_result.get("risk_scores", [])

    if not risk_scores:
        return {
            "event_id": event["id"],
            "error":    "Risk scoring returned no results",
            "skipped":  True,
        }

    # ── Predict high-risk suppliers ──
    predicted_high_risk = [
        s["supplier"] for s in risk_scores
        if s.get("risk_score", 0) >= risk_threshold
    ]

    # ── Precision / Recall ──
    metrics = _precision_recall_f1(predicted_high_risk, affected)

    # ── Forecast MAE ──
    mae = _forecast_mae(train_df, test_df, forecaster)

    # ── Lead time: days before disruption the highest-risk affected supplier was flagged ──
    lead_time_days: Optional[int] = None
    if date_col and affected:
        for supplier_name in affected:
            supplier_score = next(
                (s for s in risk_scores if s["supplier"].lower() == supplier_name.lower()),
                None,
            )
            if supplier_score and supplier_score.get("risk_score", 0) >= risk_threshold:
                # Last training date — days between it and disruption
                last_train_date = pd.to_datetime(
                    train_df[date_col], errors="coerce"
                ).max()
                if pd.notna(last_train_date):
                    lead_time_days = (disruption_date - last_train_date).days

    # ── Per-supplier risk scores for the affected suppliers ──
    affected_scores = [
        {
            "supplier":    s["supplier"],
            "risk_score":  s.get("risk_score", 0),
            "tier":        s.get("tier", "unknown"),
            "confidence":  s.get("score_confidence", "unknown"),
            "flagged":     s.get("risk_score", 0) >= risk_threshold,
        }
        for s in risk_scores
        if s["supplier"].lower() in [a.lower() for a in affected]
    ]

    return {
        "event_id":              event["id"],
        "description":           event.get("description", ""),
        "disruption_date":       event["disruption_date"],
        "disruption_type":       event.get("disruption_type", "unknown"),
        "affected_suppliers":    affected,
        "training_rows":         len(train_df),
        "test_rows":             len(test_df),
        "risk_threshold_used":   risk_threshold,
        "predicted_high_risk":   predicted_high_risk,
        "metrics":               metrics,
        "forecast_mae_days":     mae,
        "lead_time_days":        lead_time_days,
        "affected_supplier_scores": affected_scores,
        "skipped":               False,
    }


def run_evaluation(
    data_path: str,
    events: List[Dict],
    output_dir: str,
    risk_threshold: float = 70.0,
) -> Dict[str, Any]:
    """
    Run the full evaluation across all disruption events.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"[EVAL] Loading data from {data_path}")
    try:
        if data_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(data_path)
        else:
            try:
                df = pd.read_csv(data_path, encoding="utf-8-sig")
            except UnicodeDecodeError:
                df = pd.read_csv(data_path, encoding="latin-1")
    except Exception as e:
        print(f"[EVAL] ERROR: Could not load data file: {e}")
        sys.exit(1)

    print(f"[EVAL] Loaded {len(df):,} rows, {len(df.columns)} columns")
    print(f"[EVAL] Running evaluation across {len(events)} disruption event(s)")

    analyzer   = SupplyChainAnalyzer()
    forecaster = TimeSeriesForecaster()

    event_results = []
    for event in events:
        print(f"[EVAL]   Event {event['id']}: {event.get('description', '')}")
        result = evaluate_event(df, event, risk_threshold, analyzer, forecaster)
        event_results.append(result)
        if result.get("skipped"):
            print(f"[EVAL]   ⚠ Skipped: {result.get('error')}")
        else:
            m = result["metrics"]
            print(
                f"[EVAL]   Precision={m['precision']:.1%}  "
                f"Recall={m['recall']:.1%}  "
                f"F1={m['f1']:.1%}  "
                f"MAE={result.get('forecast_mae_days', 'N/A')} days"
            )

    # ── Aggregate across all events ──
    valid_results = [r for r in event_results if not r.get("skipped")]
    aggregate: Dict[str, Any] = {}
    if valid_results:
        aggregate = {
            "events_evaluated": len(valid_results),
            "avg_precision":    round(np.mean([r["metrics"]["precision"] for r in valid_results]), 3),
            "avg_recall":       round(np.mean([r["metrics"]["recall"]    for r in valid_results]), 3),
            "avg_f1":           round(np.mean([r["metrics"]["f1"]        for r in valid_results]), 3),
            "avg_forecast_mae": round(
                float(np.mean([r["forecast_mae_days"] for r in valid_results if r.get("forecast_mae_days") is not None])),
                2,
            ) if any(r.get("forecast_mae_days") is not None for r in valid_results) else None,
            "avg_lead_time_days": round(
                float(np.mean([r["lead_time_days"] for r in valid_results if r.get("lead_time_days") is not None])),
                1,
            ) if any(r.get("lead_time_days") is not None for r in valid_results) else None,
        }

    full_report = {
        "evaluated_at":    datetime.now(timezone.utc).isoformat(),
        "data_file":       data_path,
        "risk_threshold":  risk_threshold,
        "total_data_rows": len(df),
        "aggregate":       aggregate,
        "events":          event_results,
        "note": (
            "This report replaces the unverified '~94% simulation fidelity' claim. "
            "All metrics are computed against labelled ground-truth disruption events. "
            "To improve these numbers: add more disruption events to --events-file, "
            "tune risk_threshold, and increase training data coverage."
        ),
    }

    # ── Write JSON ──
    json_path = output_path / "evaluation_results.json"
    with open(json_path, "w") as f:
        json.dump(full_report, f, indent=2, default=str)
    print(f"[EVAL] Results written to {json_path}")

    # ── Write Markdown report ──
    _write_markdown_report(full_report, output_path / "evaluation_report.md")
    print(f"[EVAL] Report written to {output_path / 'evaluation_report.md'}")

    return full_report


def _write_markdown_report(report: Dict, path: Path) -> None:
    agg = report.get("aggregate", {})
    events = report.get("events", [])

    lines = [
        "# NEXUS Pipeline Evaluation Report",
        f"\n**Evaluated at**: {report['evaluated_at']}",
        f"**Data file**: `{report['data_file']}`",
        f"**Total rows**: {report['total_data_rows']:,}",
        f"**Risk threshold**: {report['risk_threshold']}",
        "",
        "## Aggregate Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]

    if agg:
        lines += [
            f"| Events evaluated | {agg.get('events_evaluated', 0)} |",
            f"| Average Precision | {agg.get('avg_precision', 0):.1%} |",
            f"| Average Recall | {agg.get('avg_recall', 0):.1%} |",
            f"| Average F1 | {agg.get('avg_f1', 0):.1%} |",
            f"| Avg Forecast MAE | {agg.get('avg_forecast_mae', 'N/A')} days |",
            f"| Avg Lead Time Before Disruption | {agg.get('avg_lead_time_days', 'N/A')} days |",
        ]
    else:
        lines.append("| — | No valid events to aggregate |")

    lines += [
        "",
        "## Per-Event Results",
        "",
    ]

    for evt in events:
        lines.append(f"### Event: {evt['event_id']}")
        if evt.get("skipped"):
            lines.append(f"⚠ **Skipped**: {evt.get('error')}")
            lines.append("")
            continue

        m = evt["metrics"]
        lines += [
            f"- **Description**: {evt.get('description', '')}",
            f"- **Disruption date**: {evt['disruption_date']}",
            f"- **Affected suppliers**: {', '.join(evt['affected_suppliers'])}",
            f"- **Training rows**: {evt['training_rows']:,}",
            f"- **Risk threshold**: {evt['risk_threshold_used']}",
            f"- **Predicted high-risk**: {', '.join(evt['predicted_high_risk']) or 'none'}",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Precision | {m['precision']:.1%} |",
            f"| Recall | {m['recall']:.1%} |",
            f"| F1 | {m['f1']:.1%} |",
            f"| True Positives | {m['true_positives']} |",
            f"| False Positives | {m['false_positives']} |",
            f"| False Negatives | {m['false_negatives']} |",
            f"| Forecast MAE | {evt.get('forecast_mae_days', 'N/A')} days |",
            f"| Lead Time | {evt.get('lead_time_days', 'N/A')} days |",
            "",
        ]

        if evt.get("affected_supplier_scores"):
            lines.append("**Affected supplier scores at prediction time:**")
            lines.append("")
            lines.append("| Supplier | Risk Score | Tier | Confidence | Flagged? |")
            lines.append("|----------|-----------|------|------------|----------|")
            for s in evt["affected_supplier_scores"]:
                flagged = "✅ Yes" if s["flagged"] else "❌ No"
                lines.append(
                    f"| {s['supplier']} | {s['risk_score']} | "
                    f"{s['tier']} | {s['confidence']} | {flagged} |"
                )
            lines.append("")

    lines += [
        "---",
        "",
        "> " + report.get("note", ""),
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate the NEXUS prediction pipeline against labelled disruption events."
    )
    parser.add_argument(
        "--data-file",
        default="data/samples/sample_supply_chain_data.csv",
        help="Path to the supply chain CSV/Excel file to evaluate.",
    )
    parser.add_argument(
        "--events-file",
        default=None,
        help=(
            "Path to a JSON file containing disruption events. "
            "If omitted, uses the SAMPLE_DISRUPTION_EVENTS in this script."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="data/evaluation_results",
        help="Directory to write evaluation_results.json and evaluation_report.md",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=70.0,
        help="Risk score threshold above which a supplier is considered 'flagged' (default: 70).",
    )
    args = parser.parse_args()

    # Load events
    if args.events_file:
        with open(args.events_file) as f:
            events = json.load(f)
        print(f"[EVAL] Loaded {len(events)} event(s) from {args.events_file}")
    else:
        events = SAMPLE_DISRUPTION_EVENTS
        if not events:
            print(
                "[EVAL] WARNING: No disruption events defined.\n"
                "Edit SAMPLE_DISRUPTION_EVENTS in this script or supply --events-file.\n"
                "Running in demo mode with sample data — no ground truth comparison possible."
            )
            # Demo mode: run the pipeline and report what it would flag
            events = [
                {
                    "id":                  "demo-full-dataset",
                    "description":         "Full dataset scan (no ground truth — demo mode)",
                    "disruption_date":     "2099-01-01",  # far future → train on everything
                    "affected_suppliers":  [],
                    "disruption_type":     "demo",
                }
            ]

    run_evaluation(
        data_path=args.data_file,
        events=events,
        output_dir=args.output_dir,
        risk_threshold=args.threshold,
    )
