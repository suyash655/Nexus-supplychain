"""
NEXUS — Upload Router
=====================
Orchestrates file upload, schema matching, and atomic database insertion.
Parsing and validation logic have been extracted to app/services/upload/.
"""

import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.models import SupplyData, UploadHistory  # type: ignore
from app.core.config import settings  # type: ignore
from app.core.orchestrator import is_analyzing, run_full_analysis as _run  # type: ignore
from app.main import _get_engine_kwargs  # type: ignore
from app.utils.schema_fingerprints import detect_schema  # type: ignore

# Refactored service modules
from app.services.upload.parser import parse_upload_file  # type: ignore
from app.services.upload.schema import (  # type: ignore
    auto_detect_columns,
    mapping_dict_from_detection,
    low_confidence_fields,
)
from app.services.upload.validator import (  # type: ignore
    safe_str, safe_int, safe_float, validate_mapped_values
)

router = APIRouter(prefix="", tags=["Upload"])
logger_upload = logging.getLogger("nexus.upload")


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mapping: str = Form(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Upload CSV or Excel file with auto column detection.
    Guarantees atomic insertion: if any row fails, the entire upload is rolled back.
    """
    filename = file.filename or "upload"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    contents = await file.read()

    # 1. Parse File
    df = parse_upload_file(contents, filename, settings.MAX_UPLOAD_BYTES)
    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty")

    # 2. Resolve Column Mapping
    user_supplied_mapping = False
    schema_match = None
    mapping_dict: Dict[str, str] = {}

    if mapping:
        try:
            raw_map = json.loads(mapping)
            mapping_dict = {k: (v["mapped_to"] if isinstance(v, dict) else v) for k, v in raw_map.items()}
            user_supplied_mapping = True
        except Exception:
            pass

    if not user_supplied_mapping:
        schema_match = detect_schema(df.columns.tolist())
        if schema_match and schema_match["match_score"] >= 0.8:
            mapping_dict = schema_match["mapping"]
            user_supplied_mapping = True
        else:
            detection = auto_detect_columns(df.columns.tolist(), sample_data=df.head(50).to_dict("records"))
            low_conf = low_confidence_fields(detection)

            if low_conf:
                # Need user confirmation. Log history and abort.
                history = UploadHistory(
                    filename=filename, file_type=file_ext,
                    rows_total=len(df), rows_inserted=0, rows_rejected=0,
                    columns_detected=list(df.columns),
                    column_mapping=mapping_dict_from_detection(detection),
                    data_quality_report={"status": "ambiguous_columns_aborted"},
                )
                db.add(history)
                db.commit()
                
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "ambiguous_column_mapping",
                        "message": "Ambiguous columns detected. Please confirm mapping.",
                        "ambiguous_fields": low_conf,
                        "suggested_mapping": detection,
                        "schema_hint": schema_match,
                    },
                )
            mapping_dict = mapping_dict_from_detection(detection)

    # 3. Validate Data Quality
    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "detected_columns": list(df.columns),
        "mapped_columns": mapping_dict,
        "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
        "mapping_user_confirmed": user_supplied_mapping,
        "column_validation": validate_mapped_values(df, mapping_dict),
    }

    # 4. Atomic Database Insertion
    records = []
    m = mapping_dict

    try:
        for row in df.to_dict("records"):
            record = SupplyData(
                supplier=safe_str(row.get(m.get("supplier"))) or "Unknown Source",
                sku=safe_str(row.get(m.get("sku"))) or "N/A",
                warehouse=safe_str(row.get(m.get("warehouse"))),
                region=safe_str(row.get(m.get("region"))),
                shipment_id=safe_str(row.get(m.get("shipment_id"))),
                order_date=safe_str(row.get(m.get("order_date"))),
                delivery_date=safe_str(row.get(m.get("delivery_date"))),
                delay_days=safe_int(row.get(m.get("delay_days")), 0),
                cost=safe_float(row.get(m.get("cost")), 0.0),
                quantity=safe_int(row.get(m.get("quantity")), 0),
                category=safe_str(row.get(m.get("category"))),
                quality_score=safe_float(row.get(m.get("quality_score")), None),
            )
            records.append(record)
        
        # Add all rows to session
        db.add_all(records)

        # Add UploadHistory to the SAME transaction
        history = UploadHistory(
            filename=filename, file_type=file_ext,
            rows_total=len(df), rows_inserted=len(records), rows_rejected=0,
            columns_detected=list(df.columns), column_mapping=mapping_dict,
            data_quality_report=quality_report,
        )
        db.add(history)

        # One single commit guarantees atomicity: either all SupplyData + History succeeds, or none of it does.
        db.commit()

    except Exception as e:
        db.rollback()
        logger_upload.error("[NEXUS] Upload transaction failed, rolled back: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Database insertion failed. The entire upload was rolled back. Error: {str(e)}"
        )

    # 5. Trigger Analysis
    analysis_queued = False
    if not is_analyzing():
        background_tasks.add_task(_run, **_get_engine_kwargs())
        analysis_queued = True

    return {
        "status": "success",
        "rows_inserted": len(records),
        "rows_rejected": 0,  # No longer rejecting individual rows; it's all or nothing
        "column_mapping": mapping_dict,
        "schema_detected": schema_match,
        "data_quality": quality_report,
        "analysis_queued": analysis_queued,
    }


@router.post("/upload/preview")
async def preview_upload(file: UploadFile = File(...)):
    """Preview file contents and auto-detected column mapping without ingesting."""
    filename = file.filename or "upload"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    contents = await file.read()

    try:
        df = parse_upload_file(contents, filename, settings.MAX_UPLOAD_BYTES, max_preview_rows=20)
    except Exception as e:
        logger_upload.error("[NEXUS] ERROR during preview parse: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

    schema_match = detect_schema(df.columns.tolist())
    detection = auto_detect_columns(df.columns.tolist(), sample_data=df.head(50).to_dict("records"))
    low_conf = low_confidence_fields(detection)

    return {
        "filename": filename,
        "file_type": file_ext,
        "columns": list(df.columns),
        "schema_detected": schema_match,
        "auto_mapping": detection,
        "flat_mapping": mapping_dict_from_detection(detection),
        "requires_confirmation": len(low_conf) > 0 and (not schema_match or schema_match["match_score"] < 0.8),
        "ambiguous_fields": low_conf,
        "preview_rows": df.head(10).fillna("").to_dict(orient="records"),
        "total_preview_rows": len(df),
    }


@router.get("/upload/columns")
def get_last_upload_columns(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Return columns from the most recent upload."""
    latest = db.query(UploadHistory).order_by(UploadHistory.id.desc()).first()
    if not latest or not latest.columns_detected:
        return {"columns": [], "mapping": {}}
    return {"columns": latest.columns_detected, "mapping": latest.column_mapping or {}}


@router.post("/upload/confirm")
def confirm_upload(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Accept user-confirmed column mapping and re-trigger analysis."""
    if is_analyzing():
        raise HTTPException(status_code=429, detail="Analysis already running.")

    background_tasks.add_task(_run, **_get_engine_kwargs())
    return {"status": "success", "message": "Analysis triggered with confirmed mapping"}
