import asyncio
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import AuthService
from app.core.dependencies import require_auth
from app.engines.kpi_engine import KPIEngine
from app.models import AnalysisResult, Base, SupplyData
from app.services.upload.parser import parse_upload_file


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_refresh_token_rotation_rejects_reuse():
    db = _session()
    try:
        registered = AuthService.register(
            db,
            "rotation@example.com",
            "rotation_user",
            "correct-horse-battery-staple",
        )

        first_refresh = registered["refresh_token"]
        rotated = AuthService.refresh(db, first_refresh)
        reused = AuthService.refresh(db, first_refresh)

        assert "refresh_token" in rotated
        assert rotated["refresh_token"] != first_refresh
        assert reused == {"error": "Invalid or expired refresh token"}
    finally:
        db.close()


def test_allow_demo_false_blocks_missing_auth(monkeypatch):
    monkeypatch.setenv("ALLOW_DEMO", "false")

    with pytest.raises(Exception) as exc_info:
        asyncio.run(require_auth(None))

    assert getattr(exc_info.value, "status_code", None) == 401


def test_allow_demo_true_allows_missing_auth(monkeypatch):
    monkeypatch.setenv("ALLOW_DEMO", "true")

    user = asyncio.run(require_auth(None))

    assert user["demo"] is True


def test_kpi_engine_uses_real_agent_trace_model_import():
    result = KPIEngine().compute_all_kpis(
        pd.DataFrame(
            {
                "supplier": ["SUP-1"],
                "warehouse": ["WH-1"],
                "region": ["NA"],
                "delay_days": [0],
            }
        ),
        risk_scores=[],
        anomalies={"anomaly_count": 0},
    )

    assert result["metrics"]["mttd"]["status"] in {"needs_data", "measured"}


def test_upload_parser_rejects_oversize_with_actionable_message():
    try:
        parse_upload_file(b"a,b\n1,2\n", "sample.csv", max_bytes=1)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 413
        assert "Maximum allowed size" in str(getattr(exc, "detail", ""))
    else:
        raise AssertionError("Expected oversize upload to be rejected")


def test_upload_parser_accepts_utf16_csv():
    contents = "supplier,sku,delay_days\nSUP-1,SKU-1,1\n".encode("utf-16")

    df = parse_upload_file(contents, "utf16.csv", max_bytes=1024)

    assert df.iloc[0]["supplier"] == "SUP-1"


def test_upload_parser_handles_header_only_as_empty():
    df = parse_upload_file(b"supplier,sku,delay_days\n", "header.csv", max_bytes=1024)

    assert df.empty


def test_seed_data_supplier_variance_and_shared_hubs():
    sample = Path(__file__).resolve().parents[2] / "data" / "samples" / "sample_supply_chain_data.csv"
    df = pd.read_csv(sample)
    supplier_delay = df.groupby("supplier")["delay_days"].mean()
    supplier_quality = df.groupby("supplier")["quality_score"].mean()
    shared_hubs = df.groupby(["warehouse", "region"])["supplier"].nunique()

    assert supplier_delay.max() - supplier_delay.min() >= 5.0
    assert supplier_quality.max() - supplier_quality.min() >= 10.0
    assert (shared_hubs >= 2).any()


def test_stale_analysis_cache_can_be_cleared_on_upload_boundary():
    db = _session()
    try:
        db.add(AnalysisResult(analysis_type="kpis", result_json={"stale": True}))
        db.commit()

        assert db.query(AnalysisResult).count() == 1
        db.query(AnalysisResult).delete()
        db.commit()

        assert db.query(AnalysisResult).count() == 0
    finally:
        db.close()


def test_download_starter_template():
    from app.features.upload.router import download_starter_template
    res = download_starter_template(user={"id": 1, "role": "admin"})
    assert res.status_code == 200
    assert b"supplier,sku,warehouse,region" in res.body
    assert b"Apex Components" in res.body


def test_load_sample_data_endpoint():
    from fastapi import BackgroundTasks

    from app.features.upload.router import load_sample_data
    db = _session()
    bg = BackgroundTasks()
    try:
        res = load_sample_data(background_tasks=bg, db=db, user={"id": 1, "role": "admin"})
        assert res["status"] == "success"
        assert res["rows_inserted"] > 0
        assert db.query(SupplyData).count() == res["rows_inserted"]
    finally:
        db.close()


def test_export_executive_memo_json_and_markdown():
    from app.features.export.router import export_executive_memo
    db = _session()
    try:
        # Pre-seed supply data and analysis result
        db.add(SupplyData(supplier="Titan Test", sku="SKU-1", delay_days=10, cost=500.0))
        db.add(AnalysisResult(analysis_type="ml", result_json={
            "risk_scores": [{"supplier": "Titan Test", "risk_score": 85.0, "tier": "critical", "primary_factors": ["delay_frequency"]}],
            "anomalies": {"anomalies": [{"index": 0, "reason": "delay"}]}
        }))
        db.commit()

        # Test JSON format
        res_json = export_executive_memo(format="json", db=db, user={"id": 1, "role": "admin"})
        assert res_json["status"] == "success"
        assert res_json["metrics"]["total_suppliers"] == 1
        assert res_json["metrics"]["critical_count"] == 1
        assert "Titan Test" in res_json["markdown"]

        # Test Markdown format
        res_md = export_executive_memo(format="markdown", db=db, user={"id": 1, "role": "admin"})
        assert res_md.status_code == 200
        assert b"# NEXUS Executive Risk Intelligence Memorandum" in res_md.body
        assert b"Titan Test" in res_md.body
    finally:
        db.close()

