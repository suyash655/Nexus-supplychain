"""Enterprise connector management endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.connectors import CONNECTOR_REGISTRY, ConnectorConfig, get_connector
from app.core.dependencies import get_db, require_auth
from app.auth.service import require_permission

router = APIRouter(prefix="/connectors", tags=["Connectors"])


CONNECTOR_TYPES = [
    {"id": "csv", "name": "CSV / Excel", "icon": "database", "description": "Flat-file ingestion for CSV and Excel uploads."},
    {"id": "database", "name": "Database", "icon": "database", "description": "SQL database extraction with table or query mode."},
    {"id": "s3", "name": "Cloud Storage", "icon": "cloud", "description": "S3-compatible object storage ingestion."},
    {"id": "api", "name": "REST API", "icon": "globe", "description": "Legacy REST API connector."},
    {"id": "sap", "name": "SAP RFC/BAPI", "icon": "plug", "description": "SAP ERP/S4 extraction and BAPI execution through RFC."},
    {"id": "mes", "name": "MES", "icon": "factory", "description": "Manufacturing execution orders, equipment state, and completions."},
    {"id": "wms", "name": "WMS", "icon": "warehouse", "description": "Inventory positions, allocations, and shipment confirmations."},
    {"id": "tms", "name": "TMS", "icon": "truck", "description": "Carrier status, tenders, milestones, and freight events."},
    {"id": "universal_rest", "name": "Universal REST", "icon": "globe", "description": "Configurable REST connector with bearer/basic/header auth."},
    {"id": "universal_soap", "name": "Universal SOAP", "icon": "globe", "description": "SOAP envelope execution and XML tabular extraction."},
]


class ConnectorCreate(BaseModel):
    name: str = Field(max_length=120)
    connector_type: str = Field(max_length=50)
    config: Dict[str, Any] = Field(default_factory=dict)
    schedule: Optional[str] = Field("manual", max_length=120)


class ConnectorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    config: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = Field(None, max_length=120)
    is_active: Optional[bool] = None


def _serialize(conn: ConnectorConfig) -> Dict[str, Any]:
    return {
        "id": conn.id,
        "name": conn.name,
        "type": conn.connector_type,
        "active": conn.is_active,
        "schedule": conn.schedule,
        "last_sync": conn.last_sync_at.isoformat() if conn.last_sync_at else None,
        "last_status": conn.last_sync_status,
        "last_rows": conn.last_sync_rows,
        "created_at": conn.created_at.isoformat() if conn.created_at else None,
    }


@router.get("/types")
def list_connector_types(user: dict = Depends(require_auth)):
    return {"types": CONNECTOR_TYPES, "registry": sorted(CONNECTOR_REGISTRY.keys())}


@router.get("")
def list_connectors(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    connectors = db.query(ConnectorConfig).order_by(ConnectorConfig.created_at.desc()).all()
    return {"connectors": [_serialize(conn) for conn in connectors]}


@router.post("")
def create_connector(request: ConnectorCreate, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    require_permission(user, "connectors:write")
    if request.connector_type not in CONNECTOR_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown connector type: {request.connector_type}")
    conn = ConnectorConfig(
        name=request.name,
        connector_type=request.connector_type,
        config_json={**request.config, "name": request.name},
        schedule=request.schedule or "manual",
        created_by=user.get("uid") or user.get("id"),
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return {"status": "success", "connector": _serialize(conn)}


@router.patch("/{connector_id}")
def update_connector(connector_id: int, request: ConnectorUpdate, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    require_permission(user, "connectors:write")
    conn = db.query(ConnectorConfig).filter(ConnectorConfig.id == connector_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connector not found")
    if request.name is not None:
        conn.name = request.name
    if request.config is not None:
        conn.config_json = {**request.config, "name": conn.name}
    if request.schedule is not None:
        conn.schedule = request.schedule
    if request.is_active is not None:
        conn.is_active = request.is_active
    db.commit()
    db.refresh(conn)
    return {"status": "success", "connector": _serialize(conn)}


@router.post("/{connector_id}/test")
def test_connector(connector_id: int, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    require_permission(user, "connectors:read")
    conn = db.query(ConnectorConfig).filter(ConnectorConfig.id == connector_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connector not found")
    result = get_connector(conn.connector_type, conn.config_json or {}).test_connection()
    conn.last_sync_status = "success" if result.get("status") in {"ok", "configured"} else "error"
    db.commit()
    return {"status": "success" if result.get("status") in {"ok", "configured"} else "error", **result}


@router.get("/{connector_id}/schema")
def get_connector_schema(connector_id: int, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    require_permission(user, "connectors:read")
    conn = db.query(ConnectorConfig).filter(ConnectorConfig.id == connector_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connector not found")
    return get_connector(conn.connector_type, conn.config_json or {}).get_schema()


@router.post("/{connector_id}/extract")
def extract_connector(connector_id: int, limit: int = 100, db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    require_permission(user, "connectors:execute")
    conn = db.query(ConnectorConfig).filter(ConnectorConfig.id == connector_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connector not found")
    connector = get_connector(conn.connector_type, conn.config_json or {})
    df = connector.extract()
    conn.last_sync_status = "success"
    conn.last_sync_rows = len(df)
    db.commit()
    return {
        "status": "success",
        "rows": len(df),
        "preview": df.head(limit).to_dict(orient="records"),
        "lineage": connector.compute_lineage(df, "supply_data"),
    }
