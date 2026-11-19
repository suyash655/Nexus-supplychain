"""
NEXUS — Analytics Router
"""


from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy import func  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.orchestrator import get_analysis_result  # type: ignore
from app.models import SupplyData, WorldEvent  # type: ignore
from app.utils.supply_metrics import completeness_score  # type: ignore

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class WorldEventRequest(BaseModel):
    title: str = Field("Manual Event", max_length=500)
    description: str = Field("No description provided.", max_length=2000)
    severity: str = Field("MEDIUM", max_length=50)
    region: str = Field("Global", max_length=200)
    impact_score: float = Field(50.0, ge=0.0, le=100.0)


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Enhanced analytics summary."""
    # Always compute live DB counts first — this is fast (single aggregation query)
    # and guarantees the UI reflects the actual ingested data immediately after upload.
    row = db.query(
        func.count(SupplyData.id).label("total_rows"),
        func.avg(SupplyData.delay_days).label("avg_delay"),
        func.max(SupplyData.delay_days).label("max_delay"),
        func.sum(SupplyData.cost).label("total_cost"),
        func.count(func.distinct(SupplyData.supplier)).label("unique_suppliers"),
        func.count(func.distinct(SupplyData.sku)).label("unique_skus"),
        func.count(func.distinct(SupplyData.region)).label("unique_regions"),
        func.count(func.distinct(SupplyData.warehouse)).label("unique_warehouses"),
    ).one()

    db_summary = {
        "total_records":    int(row.total_rows or 0),
        "avg_delay_days":   round(float(row.avg_delay or 0), 1),
        "max_delay_days":   int(row.max_delay or 0),
        "total_cost":       round(float(row.total_cost or 0), 2),
        "unique_suppliers": int(row.unique_suppliers or 0),
        "unique_skus":      int(row.unique_skus or 0),
        "unique_regions":   int(row.unique_regions or 0),
        "unique_warehouses":int(row.unique_warehouses or 0),
        "is_demo_data":     int(row.total_rows or 0) == 0,
    }

    # If ML analysis is available AND its summary has a non-zero total_records
    # that matches what we see in the DB, prefer the ML result (richer data).
    ml_res = get_analysis_result(db, "ml")
    if ml_res and isinstance(ml_res.get("summary"), dict):
        ml_summary = ml_res["summary"]
        ml_total = ml_summary.get("total_records", 0)
        # Only trust the ML summary if it covers the actual DB row count (±20% tolerance)
        if ml_total > 0 and db_summary["total_records"] > 0:
            ratio = ml_total / db_summary["total_records"]
            if 0.8 <= ratio <= 1.2:
                # Merge: use DB total_records as ground truth, ML for enriched fields
                enriched = {**ml_summary, "total_records": db_summary["total_records"], "is_demo_data": db_summary["is_demo_data"]}
                return enriched

    return db_summary


@router.get("/suppliers")
def supplier_analytics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Supplier risk analytics — returns plain array matching frontend expectation."""
    ml_res = get_analysis_result(db, "ml")
    if ml_res:
        data = ml_res.get("risk_scores", [])
        # risk_scores may itself be wrapped in {data: [...]} from older saves — unwrap
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        # Only use ML risk scores if they are non-empty; otherwise fall through to DB query
        if data:
            return {
                "data": data[skip : skip + limit],
                "total": len(data),
                "skip": skip,
                "limit": limit
            }

    # Live DB query: always returns real ingested supplier data.
    # risk_score=0 and tier="unknown" are placeholder values shown until
    # the ML analysis pipeline completes and populates AnalysisResult.
    total = db.query(func.count(func.distinct(SupplyData.supplier))).scalar() or 0
    rows = (
        db.query(
            SupplyData.supplier,
            func.count(SupplyData.id).label("rows"),
            func.avg(SupplyData.delay_days).label("avg_delay"),
            func.sum(SupplyData.cost).label("total_cost"),
        )
        .filter(SupplyData.supplier.isnot(None))
        .group_by(SupplyData.supplier)
        .order_by(func.avg(SupplyData.delay_days).desc())
        .offset(skip).limit(limit)
        .all()
    )

    data = [
        {
            "supplier": str(r.supplier or "Unknown"),
            "total_shipments": int(r.rows or 0),
            "avg_delay": round(float(r.avg_delay or 0), 1),
            "total_cost": round(float(r.total_cost or 0), 2),
            "risk_score": 0,
            "tier": "unknown",
        }
        for r in rows
    ]

    return {
        "data": data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/time-series")
def time_series_analytics(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Time-series trends and forecasts."""
    ml_res = get_analysis_result(db, "ml")
    if ml_res:
        return ml_res["time_series"]
    return {"delay_trend": [], "cost_trend": [], "volume_trend": [], "forecast": {}}


@router.get("/world-events")
def get_world_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Retrieve active world disruptions — returns plain array."""
    total = db.query(func.count(WorldEvent.id)).scalar() or 0
    if total == 0:
        seed = [
            WorldEvent(
                title="Red Sea Crisis",
                description="Maritime shipments diverted; 20% increase in lead times for Asia-Europe routes.",
                severity="CRITICAL", region="Middle East", impact_score=float(88.2), status="ACTIVE",
            ),
            WorldEvent(
                title="Panama Canal Congestion",
                description="Drought conditions limiting transit slots; backlog of 100+ vessels.",
                severity="HIGH", region="Americas", impact_score=float(72.5), status="ACTIVE",
            ),
        ]
        db.add_all(seed)
        db.commit()

    events = db.query(WorldEvent).order_by(WorldEvent.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id":           e.id,
            "title":        e.title,
            "description":  e.description,
            "severity":     e.severity,
            "region":       e.region,
            "impact_score": e.impact_score,
            "status":       e.status,
            "created_at":   e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


@router.post("/world-events/simulate")
def simulate_world_event(
    event: WorldEventRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Inject a simulated disruption for stress testing."""
    new_event = WorldEvent(
        title=event.title,
        description=event.description,
        severity=event.severity,
        region=event.region,
        impact_score=event.impact_score,
        status="ACTIVE",
    )
    db.add(new_event)
    db.commit()
    return {"status": "success", "id": new_event.id}


@router.get("/world-impact")
def world_impact(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get cached world event impact analysis."""
    res = get_analysis_result(db, "world_event_impact")
    if res:
        return res
    return {"impact_summary": "No data", "disrupted_suppliers": []}


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get all Decision Velocity KPIs."""
    cached = get_analysis_result(db, "kpis")
    if cached:
        return cached
    from app.core.orchestrator import _load_dataframe, save_analysis_result  # type: ignore
    from app.main import engines  # type: ignore
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=400, detail="No data available. Upload data first.")
    ml_cached = get_analysis_result(db, "ml", {})
    kpi = engines.kpi_engine_instance
    if not kpi:
        raise HTTPException(status_code=503, detail="KPI engine unavailable.")
    kpi_res = kpi.compute_all_kpis(
        df,
        risk_scores=ml_cached.get("risk_scores", []) if ml_cached else [],
        anomalies=ml_cached.get("anomalies", {}) if ml_cached else {},
    )
    save_analysis_result(db, "kpis", kpi_res)
    return kpi_res


@router.get("/data-quality")
def data_quality(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """
    Return a lightweight data quality summary for the current dataset.

    Metrics:
      completeness   — fraction of rows with no null fields (0.0–1.0)
      duplicate_rate — fraction of duplicate shipment_id values (0.0–1.0)
      outlier_count  — rows flagged as outliers by the IQR method on delay_days
      total_records  — total row count
    """
    import pandas as pd  # type: ignore

    from app.core.orchestrator import _load_dataframe  # type: ignore

    df = _load_dataframe()
    if df.empty:
        return {
            "completeness": 0.0,
            "duplicate_rate": 0.0,
            "outlier_count": 0,
            "total_records": 0,
        }

    total = len(df)

    # Completeness: required supply-chain fields only.
    completeness = round(completeness_score(df), 4)

    # Duplicate rate on shipment_id (ignore nulls)
    if "shipment_id" in df.columns:
        sid = df["shipment_id"].dropna()
        dup_count = int(sid.duplicated().sum())
        duplicate_rate = round(dup_count / total, 4)
    else:
        duplicate_rate = 0.0

    # Outlier count on delay_days via IQR
    outlier_count = 0
    if "delay_days" in df.columns:
        delays = pd.to_numeric(df["delay_days"], errors="coerce").dropna()
        if len(delays) > 3:
            q1 = float(delays.quantile(0.25))
            q3 = float(delays.quantile(0.75))
            iqr = q3 - q1
            outlier_count = int(((delays < q1 - 1.5 * iqr) | (delays > q3 + 1.5 * iqr)).sum())

    return {
        "completeness": completeness,
        "duplicate_rate": duplicate_rate,
        "outlier_count": outlier_count,
        "total_records": total,
    }
