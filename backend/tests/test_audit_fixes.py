from pathlib import Path

import pandas as pd

from app.engines.analyzer import RiskScorer, SupplyChainAnalyzer
from app.pipeline import DataQualityEngine
from app.routers import control_tower
from app.utils.supply_metrics import completeness_score, on_time_mask


def test_otif_uses_one_day_tolerance(monkeypatch):
    df = pd.DataFrame({"delay_days": [1, 1, 1]})
    monkeypatch.setattr(control_tower, "_load_dataframe", lambda: df)

    metrics = control_tower.get_performance_metrics(db=None, user={"email": "test@example.com"})
    by_name = {metric["metric"]: metric for metric in metrics}

    assert by_name["OTIF Rate"]["current"] == 100.0
    assert by_name["Supplier On-Time"]["current"] == 100.0


def test_performance_metrics_do_not_emit_hardcoded_forecast_or_turnover(monkeypatch):
    df = pd.DataFrame({"delay_days": [0, 1, 2]})
    monkeypatch.setattr(control_tower, "_load_dataframe", lambda: df)

    metrics = control_tower.get_performance_metrics(db=None, user={"email": "test@example.com"})
    by_name = {metric["metric"]: metric for metric in metrics}

    assert by_name["Forecast Accuracy"]["current"] is None
    assert by_name["Forecast Accuracy"]["period"] == "Not yet available"
    assert by_name["Inventory Turnover"]["current"] is None
    assert by_name["Inventory Turnover"]["period"] == "Not yet available"


def test_completeness_is_column_aware_across_callers():
    df = pd.DataFrame(
        {
            "supplier": ["SUP-1", "SUP-2"],
            "sku": ["SKU-1", "SKU-2"],
            "warehouse": ["WH-1", "WH-1"],
            "region": ["NA", "NA"],
            "shipment_id": ["S1", "S2"],
            "order_date": ["2026-01-01", "2026-01-02"],
            "delivery_date": ["2026-01-03", "2026-01-04"],
            "delay_days": [0, 1],
            "cost": [10.0, 12.0],
            "quantity": [1, 2],
            "quality_score": [None, 99.0],
        }
    )

    assert completeness_score(df) == 1.0
    pipeline_report = DataQualityEngine.run_checks(df)
    analyzer_report = SupplyChainAnalyzer()._assess_quality(df)

    assert pipeline_report["checks"][0]["score"] == 1.0
    assert analyzer_report["completeness_pct"] == 100.0


def test_risk_scorer_delay_frequency_uses_same_tolerance():
    df = pd.DataFrame(
        {
            "supplier": ["SUP-A", "SUP-A", "SUP-B", "SUP-B"],
            "delay_days": [1, 1, 1, 3],
            "cost": [100.0, 100.0, 100.0, 100.0],
            "quality_score": [90.0, 90.0, 90.0, 90.0],
        }
    )

    scores = {row["supplier"]: row for row in RiskScorer().score_suppliers(df)}

    assert scores["SUP-A"]["factors"]["delay_frequency"] == 0.0
    assert scores["SUP-B"]["factors"]["delay_frequency"] == 50.0


def test_ibp_fallback_steps_are_not_visually_ready():
    source = Path(__file__).resolve().parents[2] / "frontend" / "app" / "ibp-unified" / "page.tsx"
    text = source.read_text(encoding="utf-8")

    assert 'status: "not_started"' in text
    assert 'status: "ready"' not in text
    assert "not run" in text


def test_sample_data_shares_warehouses_and_regions_across_suppliers():
    sample = Path(__file__).resolve().parents[2] / "data" / "samples" / "sample_supply_chain_data.csv"
    df = pd.read_csv(sample)

    shared_hubs = df.groupby(["warehouse", "region"])["supplier"].nunique()

    assert (shared_hubs >= 2).any()
    assert "WH-West" not in set(df["warehouse"])
    assert bool(on_time_mask(pd.Series([1])).iloc[0]) is True
