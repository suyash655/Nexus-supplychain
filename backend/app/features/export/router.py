import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_auth
from app.core.orchestrator import _load_dataframe, get_analysis_result
from app.core.sanitize import sanitize_dataframe_formulas

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
    safe_df = sanitize_dataframe_formulas(df)
    safe_df.to_csv(output, index=False)
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

    {
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


@export_router.get("/executive-memo")
def export_executive_memo(
    format: str = Query("json", description="Export format: 'json' or 'markdown'"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Export an Executive Risk Memorandum synthesizing overall posture,
    top vulnerable suppliers, detected anomalies, and strategic mitigation directives.
    """
    df = _load_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="No supply chain data available for executive memo")

    ml_res = get_analysis_result(db, "ml", {})
    get_analysis_result(db, "kpi", {})
    risk_scores = ml_res.get("risk_scores", []) if ml_res else []
    anomalies = (ml_res.get("anomalies", {}) if ml_res else {}).get("anomalies", [])

    critical = [s for s in risk_scores if s.get("tier") == "critical"]
    elevated = [s for s in risk_scores if s.get("tier") == "elevated"]
    stable = [s for s in risk_scores if s.get("tier") == "stable"]
    top_vulnerable = risk_scores[:5]

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Construct clean markdown memo
    memo_lines = [
        "# NEXUS Executive Risk Intelligence Memorandum",
        f"**Date Generated:** {generated_at}  ",
        "**Prepared For:** Chief Supply Chain Officer (CSCO) & Executive Committee  ",
        "**Platform:** NEXUS 3.0 Autonomous Supply Chain Intelligence Platform  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Fleet Health",
        f"- **Total Monitored Suppliers:** {len(risk_scores)}",
        f"- **Critical Risk Suppliers:** {len(critical)} (Immediate containment required)",
        f"- **Elevated Risk Suppliers:** {len(elevated)} (Proactive monitoring and SLA audits advised)",
        f"- **Stable Suppliers:** {len(stable)} (Operating within acceptable tolerances)",
        f"- **Multivariate Anomalies Detected:** {len(anomalies)} irregular shipment and cost deviations flagged",
        "",
        "## 2. Priority Bottlenecks & High-Exposure Suppliers",
    ]

    if not top_vulnerable:
        memo_lines.append("_No suppliers currently analyzed or scored._")
    else:
        for idx, sup in enumerate(top_vulnerable, 1):
            s_name = sup.get("supplier", "Unknown")
            s_score = sup.get("risk_score", 0.0)
            s_tier = sup.get("tier", "unknown").upper()
            factors = sup.get("primary_factors", [])
            factors_str = ", ".join(factors) if factors else "composite operational drift"
            memo_lines.append(
                f"{idx}. **{s_name}** — Risk Score: **{s_score:.1f}/100** [{s_tier}]\n"
                f"   - *Primary Risk Drivers:* {factors_str}\n"
                f"   - *Executive Recommendation:* Initiate dual-sourcing contingency and buffer inventory."
            )

    memo_lines.extend([
        "",
        "## 3. Recommended Strategic Mitigation Directives",
        "1. **Dual-Sourcing Contingency:** For all single-source Critical-tier vendors, activate pre-qualified secondary sources to avert production halts.",
        "2. **Safety Stock Buffer Adjustments:** Elevate buffer thresholds by 15–20% on high-delay SKUs identified in the top risk decile.",
        "3. **Vendor SLA Review:** Schedule joint operational reviews with suppliers exhibiting recurrent delivery variance > 4 days.",
        "",
        "## 4. Privacy & Governance Guarantee",
        "All statistical analysis, Holt-Winters forecasting, Isolation Forest anomaly detection, and cascade simulations run entirely in-memory. Zero proprietary vendor pricing or route data is shared externally or used in public model training.",
    ])

    markdown_content = "\n".join(memo_lines)

    if format.lower() in ("markdown", "md"):
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": 'attachment; filename="nexus_executive_risk_memo.md"'},
        )

    return {
        "status": "success",
        "generated_at": generated_at,
        "metrics": {
            "total_suppliers": len(risk_scores),
            "critical_count": len(critical),
            "elevated_count": len(elevated),
            "stable_count": len(stable),
            "anomalies_detected": len(anomalies),
            "total_records": len(df),
        },
        "top_vulnerable_suppliers": top_vulnerable,
        "markdown": markdown_content,
    }

