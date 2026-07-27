import io
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_auth
from app.core.orchestrator import get_analysis_result, _load_dataframe

export_router = APIRouter(prefix="/export", tags=["Export"])

@export_router.get("/csv")
def export_csv(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
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
def export_json(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Export analysis results as JSON for Power BI."""
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data to export")

    ml_res = get_analysis_result(db, "ml", {})
    kpi_res = get_analysis_result(db, "kpi", {})

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "suppliers": json.loads(df.to_json(orient="records")),
        "ml_insights": ml_res,
        "kpi_metrics": kpi_res,
    }
    export_data = {
        "metadata": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "platform": "NEXUS 3.0",
            "total_records": len(df),
        },
        "summary": ml_res.get("summary", {}) if ml_res else {},
        "supplier_risk_scores": ml_res.get("risk_scores", []) if ml_res else [],
        "anomalies": (ml_res.get("anomalies", {}) if ml_res else {}).get("anomalies", [])[:100],
        "raw_data": df.fillna("").to_dict(orient="records"),
    }

    out_json = json.dumps(export_data, indent=2, default=str)
    return StreamingResponse(
        iter([out_json]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=synchain_powerbi.json"},
    )

@export_router.get("/tableau-schema")
def tableau_schema():
    """Get Tableau-compatible schema description."""
    from app.models import SupplyData  # type: ignore
    
    # Map SQLAlchemy types to Tableau-compatible strings
    def _sqlalchemy_to_tableau_type(sql_type):
        """Convert SQLAlchemy type to Tableau-compatible type string."""
        type_str = str(sql_type).lower()
        if "integer" in type_str or "int" in type_str:
            return "integer"
        elif "float" in type_str or "double" in type_str or "numeric" in type_str or "decimal" in type_str:
            return "float"
        else:
            return "string"
    
    # Introspect SupplyData.__table__.columns at runtime
    db_columns = []
    for column in SupplyData.__table__.columns:
        col_name = column.name
        col_type = _sqlalchemy_to_tableau_type(column.type)
        
        # Determine role based on type
        role = "measure" if col_type in ("integer", "float") else "dimension"
        
        db_columns.append({
            "name": col_name,
            "type": col_type,
            "role": role
        })
    
    # Append derived computed columns from ML result (not from DB table)
    derived_columns = [
        {"name": "risk_score", "type": "float", "role": "measure"},
        {"name": "risk_tier", "type": "string", "role": "dimension"},
    ]
    
    return {
        "table_name": "SynChain Supply Intelligence",
        "columns": db_columns + derived_columns,
    }
