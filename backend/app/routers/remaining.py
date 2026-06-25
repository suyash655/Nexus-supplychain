"""
NEXUS — Remaining Routers: XAI, Export, Connectors, Pipeline, Causal, Agents, Contracts, Scheduler, System
===========================================================================================================
Groups the remaining smaller route domains to avoid an explosion of tiny files.
"""

import io
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Query, Depends, HTTPException  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.models import SupplyData, SupplierProfile, RiskEvent, AnalysisResult, UploadHistory, WorldEvent  # type: ignore
from app.core.orchestrator import get_analysis_result, _load_dataframe, save_analysis_result  # type: ignore
from app.core.errors import EngineUnavailableError, NoDataError  # type: ignore


# ── Request schemas ────────────────────────────────────────────────────────────────────

class ContractTextRequest(BaseModel):
    name: str = Field("Unnamed Contract", max_length=500)
    content: str = Field(..., min_length=1, description="Full text of the contract document")
    doc_type: str = Field("contract", max_length=100)


class ContractQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=50)
    document_id: Optional[str] = Field(None)


class ScheduledJobRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    schedule: str = Field("daily_6am", max_length=100)
    connector_type: str = Field("csv", max_length=50)
    connector_config: Dict[str, Any] = Field(default_factory=dict)


class JobUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    schedule: Optional[str] = Field(None, max_length=100)
    connector_config: Optional[Dict[str, Any]] = None


# ============================================================
# XAI
# ============================================================

xai_router = APIRouter(prefix="/xai", tags=["XAI"])


@xai_router.get("/feature-importance")
def feature_importance(db: Session = Depends(get_db)):
    """Get feature importance analysis."""
    xai_res = get_analysis_result(db, "xai")
    if xai_res:
        return xai_res["importance"]
    raise HTTPException(status_code=400, detail="No analysis available. Upload data first.")


@xai_router.get("/counterfactuals")
def counterfactuals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get counterfactual explanations."""
    xai_res = get_analysis_result(db, "xai")
    data = xai_res["counterfactuals"] if xai_res else []
    return {
        "data": data[skip : skip + limit],
        "total": len(data),
        "skip": skip,
        "limit": limit,
    }


# ============================================================
# EXPORT
# ============================================================

export_router = APIRouter(prefix="/export", tags=["Export"])


@export_router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    """Export data as CSV for Tableau."""
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data to export")

    ml_res = get_analysis_result(db, "ml", {})
    risk_scores = ml_res.get("risk_scores", []) if ml_res else []
    risk_map = {s["supplier"]: s["risk_score"] for s in risk_scores}
    tier_map = {s["supplier"]: s["tier"] for s in risk_scores}

    df["risk_score"] = df["supplier"].map(risk_map).fillna(0)
    df["risk_tier"] = df["supplier"].map(tier_map).fillna("unknown")

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=synchain_export.csv"},
    )


@export_router.get("/json")
def export_json(db: Session = Depends(get_db)):
    """Export analysis results as JSON for Power BI."""
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data to export")

    ml_res = get_analysis_result(db, "ml", {})
    risk_scores = ml_res.get("risk_scores", []) if ml_res else []
    summary = ml_res.get("summary", {}) if ml_res else {}
    anomalies = ml_res.get("anomalies", {}) if ml_res else {}

    export_data = {
        "metadata": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "platform": "NEXUS 3.0",
            "total_records": len(df),
        },
        "summary": summary,
        "supplier_risk_scores": risk_scores,
        "anomalies": anomalies.get("anomalies", [])[:100],
        "raw_data": df.fillna("").to_dict(orient="records"),
    }

    output = json.dumps(export_data, indent=2, default=str)
    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=synchain_powerbi.json"},
    )


@export_router.get("/tableau-schema")
def tableau_schema():
    """Get Tableau-compatible schema description."""
    return {
        "table_name": "SynChain Supply Intelligence",
        "columns": [
            {"name": "supplier", "type": "string", "role": "dimension"},
            {"name": "sku", "type": "string", "role": "dimension"},
            {"name": "warehouse", "type": "string", "role": "dimension"},
            {"name": "region", "type": "string", "role": "dimension"},
            {"name": "delay_days", "type": "integer", "role": "measure"},
            {"name": "cost", "type": "float", "role": "measure"},
            {"name": "quantity", "type": "integer", "role": "measure"},
            {"name": "quality_score", "type": "float", "role": "measure"},
            {"name": "risk_score", "type": "float", "role": "measure"},
            {"name": "risk_tier", "type": "string", "role": "dimension"},
        ],
    }


# ============================================================
# CONNECTORS
# ============================================================

connectors_router = APIRouter(prefix="/connectors", tags=["Connectors"])


@connectors_router.get("/types")
def list_connector_types():
    return {
        "types": [
            {"id": "csv", "name": "CSV / Excel", "icon": "file-spreadsheet", "description": "Upload or connect to CSV/Excel files"},
            {"id": "database", "name": "SQL Database", "icon": "database", "description": "PostgreSQL, MySQL, SQLite, etc."},
            {"id": "s3", "name": "Cloud Storage", "icon": "cloud", "description": "AWS S3, Azure Blob, MinIO"},
            {"id": "api", "name": "REST API", "icon": "globe", "description": "Connect to any REST endpoint or webhook"},
        ]
    }


@connectors_router.get("")
def list_connectors(db: Session = Depends(get_db)):
    from app.connectors import ConnectorConfig, get_connector  # type: ignore
    connectors = db.query(ConnectorConfig).all()
    return {"connectors": [
        {"id": c.id, "name": c.name, "type": c.connector_type, "active": c.is_active,
         "last_sync": c.last_sync_at.isoformat() if c.last_sync_at else None,
         "last_status": c.last_sync_status, "last_rows": c.last_sync_rows}
        for c in connectors
    ]}


@connectors_router.post("")
def create_connector(
    name: str = Form(...), connector_type: str = Form(...),
    config_json: str = Form("{}"), schedule: str = Form("manual"),
    db: Session = Depends(get_db),
):
    from app.connectors import ConnectorConfig  # type: ignore
    import json as _json
    conn = ConnectorConfig(
        name=name, connector_type=connector_type,
        config_json=_json.loads(config_json), schedule=schedule,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return {"id": conn.id, "name": conn.name, "type": conn.connector_type, "status": "created"}


@connectors_router.post("/{connector_id}/test")
def test_connector(connector_id: int, db: Session = Depends(get_db)):
    from app.connectors import ConnectorConfig, get_connector  # type: ignore
    conn = db.query(ConnectorConfig).filter(ConnectorConfig.id == connector_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connector not found")
    try:
        connector = get_connector(conn.connector_type, conn.config_json or {})
        return connector.test_connection()
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# PIPELINE & DATA QUALITY
# ============================================================

pipeline_router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@pipeline_router.post("/quality-check")
def run_quality_check(db: Session = Depends(get_db)):
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=400, detail="No data loaded. Upload a file first.")
    from app.main import engines  # type: ignore
    if not engines.quality_engine:
        raise HTTPException(status_code=503, detail="Quality engine is unavailable.")
    return engines.quality_engine.run_checks(df)


@pipeline_router.get("/history")
def pipeline_history(db: Session = Depends(get_db)):
    from app.pipeline import PipelineRun  # type: ignore
    runs = db.query(PipelineRun).order_by(PipelineRun.created_at.desc()).limit(20).all()
    return {"runs": [
        {"id": r.id, "name": r.pipeline_name, "status": r.status,
         "rows_ingested": r.rows_ingested, "rows_accepted": r.rows_accepted,
         "quality_score": r.quality_score, "duration_ms": r.duration_ms,
         "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in runs
    ]}


@pipeline_router.get("/lineage")
def data_lineage(db: Session = Depends(get_db)):
    from app.connectors import DataLineage  # type: ignore
    records = db.query(DataLineage).order_by(DataLineage.created_at.desc()).limit(50).all()
    return {"lineage": [
        {"id": r.id, "source": r.source_connector, "source_col": r.source_column,
         "target_table": r.target_table, "target_col": r.target_column,
         "transform": r.transformation, "hash": r.data_hash}
        for r in records
    ]}


# ============================================================
# RISK PROPAGATION (labelled "Causal" in UI for continuity)
# ============================================================

causal_router = APIRouter(prefix="/causal", tags=["Risk Propagation"])


@causal_router.post("/build")
def build_causal_genome(db: Session = Depends(get_db)):
    """
    Build the risk propagation graph from current supply chain data.
    Maps how risk scores flow downstream through structural dependencies.
    """
    graph_res = get_analysis_result(db, "graph")
    if not graph_res:
        raise HTTPException(status_code=400, detail="Graph not built. Upload data first.")

    nodes = graph_res.get("visualization", {}).get("nodes", [])
    edges = graph_res.get("visualization", {}).get("edges", [])

    risk_res = get_analysis_result(db, "risk_scores")
    risk_data = risk_res.get("suppliers", []) if risk_res else []

    events = db.query(WorldEvent).filter(WorldEvent.status == "ACTIVE").all()
    world_events = [
        {
            "title": e.title,
            "region": e.region,
            "severity": e.severity,
            "impact_score": e.impact_score,
        }
        for e in events
    ]

    from app.main import engines  # type: ignore
    return engines.causal_engine.build_from_graph(nodes, edges, risk_data, world_events)


@causal_router.get("/intervene")
def causal_intervention(
    target: str = Query(...),
    action: str = Query("remove"),
    db: Session = Depends(get_db),
):
    """
    Simulate downstream risk exposure if a node is removed or disrupted.
    Returns structural dependency paths and accumulated propagation weights.
    Note: This is graph-based risk propagation, not do-calculus causal inference.
    """
    from app.main import engines  # type: ignore
    result = engines.causal_engine.simulate_removal(target, action)
    if "error" in result:
        build_result = build_causal_genome(db)
        if "error" in build_result:
            return build_result
        result = engines.causal_engine.simulate_removal(target, action)
    return result


@causal_router.get("/chain")
def causal_chain(
    from_node: str = Query(..., alias="from"),
    to_node: str = Query(..., alias="to"),
    db: Session = Depends(get_db),
):
    """
    Find the shortest structural dependency path between two nodes.
    Returns path steps and accumulated propagation weight.
    """
    from app.main import engines  # type: ignore
    result = engines.causal_engine.get_dependency_path(from_node, to_node)
    if "error" in result:
        build_causal_genome(db)
        result = engines.causal_engine.get_dependency_path(from_node, to_node)
    return result


@causal_router.get("/fragility")
def fragility_report(db: Session = Depends(get_db)):
    """
    Taleb-inspired fragility analysis based on graph topology.
    Classifies nodes as FRAGILE / ROBUST / ANTIFRAGILE based on
    upstream concentration, downstream exposure, and risk score.
    """
    from app.main import engines  # type: ignore
    result = engines.causal_engine.get_fragility_report()
    if "error" in result:
        build_causal_genome(db)
        result = engines.causal_engine.get_fragility_report()
    return result


# ============================================================
# SCHEDULER
# ============================================================

scheduler_router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@scheduler_router.post("/jobs")
def create_scheduled_job(job: ScheduledJobRequest, db: Session = Depends(get_db)):
    import uuid
    from app.main import engines  # type: ignore
    from app.models import ScheduledIngestion  # type: ignore
    job_id = str(uuid.uuid4())[:8]
    name = job.name or f"Job-{job_id}"

    result = engines.data_scheduler.add_job(
        job_id=job_id, name=name, schedule=job.schedule,
        connector_type=job.connector_type, connector_config=job.connector_config,
    )

    db_job = ScheduledIngestion(
        job_name=name, connector_type=job.connector_type,
        connector_config=job.connector_config,
        schedule_cron=result.get("schedule_cron", job.schedule),
        schedule_label=result.get("schedule_label", job.schedule),
    )
    db.add(db_job)
    db.commit()
    return result


@scheduler_router.get("/jobs")
def list_scheduled_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    from app.main import engines  # type: ignore
    data = engines.data_scheduler.list_jobs()
    return {
        "data": data[skip : skip + limit],
        "total": len(data),
        "skip": skip,
        "limit": limit,
    }


@scheduler_router.put("/jobs/{job_id}")
def update_scheduled_job(job_id: str, updates: JobUpdateRequest):
    from app.main import engines  # type: ignore
    return engines.data_scheduler.update_job(job_id, updates.model_dump(exclude_none=True))


@scheduler_router.delete("/jobs/{job_id}")
def delete_scheduled_job(job_id: str):
    from app.main import engines  # type: ignore
    return engines.data_scheduler.remove_job(job_id)


@scheduler_router.post("/jobs/{job_id}/trigger")
def trigger_job_now(job_id: str):
    from app.main import engines  # type: ignore
    return engines.data_scheduler.trigger_now(job_id)


@scheduler_router.get("/history")
def scheduler_history(limit: int = Query(50), job_id: Optional[str] = None):
    from app.main import engines  # type: ignore
    return engines.data_scheduler.get_history(limit=limit, job_id=job_id)


@scheduler_router.get("/presets")
def schedule_presets():
    from app.engines.scheduler import SchedulePreset  # type: ignore
    return {
        "presets": SchedulePreset.ALL,
        "examples": {
            "every_15_minutes": "Pulls data every 15 minutes",
            "hourly": "Pulls data at the start of every hour",
            "daily_6am": "Pulls data once daily at 6:00 AM UTC",
            "weekly_monday": "Pulls data every Monday at 6:00 AM UTC",
            "monthly_first": "Pulls data on the 1st of every month",
        },
    }


# ============================================================
# SYSTEM
# ============================================================

system_router = APIRouter(prefix="/system", tags=["System"])


@system_router.get("/health")
def health_status(db: Session = Depends(get_db)):
    """NEXUS platform health status."""
    from app.auth import User  # type: ignore
    from app.connectors import ConnectorConfig  # type: ignore
    from app.pipeline import PipelineRun  # type: ignore
    from app.core.config import settings  # type: ignore
    latest = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).first()
    user_count = db.query(User).count()
    connector_count = db.query(ConnectorConfig).count()
    pipeline_count = db.query(PipelineRun).count()
    return {
        "status": "healthy",
        "platform": "NEXUS",
        "version": settings.APP_VERSION,
        "modules": {
            "ml": "active", "graph": "active", "ai_copilot": "active",
            "causal_genome": "active", "connectors": "active",
        },
        "stats": {"users": user_count, "connectors": connector_count, "pipeline_runs": pipeline_count},
        "last_analysis": latest.created_at.isoformat() if latest else None,
    }


@system_router.delete("/reset")
def reset_data(db: Session = Depends(get_db)):
    """Clear all data and analysis cache."""
    try:
        db.query(SupplyData).delete()
        db.query(UploadHistory).delete()
        db.query(RiskEvent).delete()
        db.query(AnalysisResult).delete()
        db.query(SupplierProfile).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Reset error: {e}")
    return {"status": "reset_complete"}
