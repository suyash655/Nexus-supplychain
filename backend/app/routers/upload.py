"""
NEXUS — Upload Router
=====================
Orchestrates file upload, schema matching, and atomic database insertion.
Parsing and validation logic have been extracted to app/services/upload/.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.models import SupplyData, UploadHistory  # type: ignore
from app.core.config import settings  # type: ignore
from app.core.orchestrator import is_analyzing, run_full_analysis as _run, _get_engine_kwargs  # type: ignore
from app.core.analysis_coordinator import coordinator  # type: ignore
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

    logger_upload.info(f"[NEXUS] Upload request: filename={filename}, size={len(contents)} bytes")

    # 1. Parse File (no row limit for full upload)
    df = parse_upload_file(contents, filename, settings.MAX_UPLOAD_BYTES, max_preview_rows=None)
    if df.empty:
        logger_upload.error(f"[NEXUS] File is empty: {filename}")
        raise HTTPException(status_code=400, detail="File is empty")

    logger_upload.info(f"[NEXUS] File parsed successfully: shape={df.shape}, columns={list(df.columns)}")

    # 2. Resolve Column Mapping
    user_supplied_mapping = False
    schema_match = None
    mapping_dict: Dict[str, str] = {}

    if mapping:
        try:
            raw_map = json.loads(mapping)
            mapping_dict = {k: (v["mapped_to"] if isinstance(v, dict) else v) for k, v in raw_map.items()}
            user_supplied_mapping = True
            logger_upload.info(f"[NEXUS] Using user-supplied mapping: {mapping_dict}")
        except Exception as e:
            logger_upload.warning(f"[NEXUS] Failed to parse user mapping: {e}")

    if not user_supplied_mapping:
        schema_match = detect_schema(df.columns.tolist())
        logger_upload.info(f"[NEXUS] Schema match result: {schema_match}")
        
        if schema_match and schema_match["match_score"] >= 0.8:
            # Schema detection returns {original_col: internal_field}, need to reverse it
            mapping_dict = {v: k for k, v in schema_match["mapping"].items()}
            user_supplied_mapping = True
            logger_upload.info(f"[NEXUS] Using schema-based mapping: {mapping_dict}")
        else:
            detection = auto_detect_columns(df.columns.tolist(), sample_data=df.head(50).to_dict("records"))
            low_conf = low_confidence_fields(detection)

            if low_conf:
                # Log warning but proceed with auto-detected mapping instead of aborting
                logger_upload.warning(
                    f"[NEXUS] Low confidence fields detected: {low_conf}. Proceeding with auto-detected mapping."
                )
                # Don't abort - proceed with auto-detected mapping
            mapping_dict = mapping_dict_from_detection(detection)
            logger_upload.info(f"[NEXUS] Using auto-detected mapping: {mapping_dict}")

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
    
    # Validate that we have at minimum required fields
    if not m.get("supplier") and not m.get("sku"):
        logger_upload.error(f"[NEXUS] Missing required fields in mapping. Mapping dict: {m}")
        raise HTTPException(
            status_code=400,
            detail=f"Mapping must include at least 'supplier' or 'sku' field. Current mapping: {m}"
        )

    try:
        # Use bulk insert for better performance with large datasets
        records_data = []
        df_dict = df.to_dict("records")
        
        for idx, row in enumerate(df_dict):
            try:
                record_data = {
                    "supplier": safe_str(row.get(m.get("supplier"))) or "Unknown Source",
                    "sku": safe_str(row.get(m.get("sku"))) or "N/A",
                    "warehouse": safe_str(row.get(m.get("warehouse"))),
                    "region": safe_str(row.get(m.get("region"))),
                    "shipment_id": safe_str(row.get(m.get("shipment_id"))),
                    "order_date": safe_str(row.get(m.get("order_date"))),
                    "delivery_date": safe_str(row.get(m.get("delivery_date"))),
                    "delay_days": safe_int(row.get(m.get("delay_days")), 0),
                    "cost": safe_float(row.get(m.get("cost")), 0.0),
                    "quantity": safe_int(row.get(m.get("quantity")), 0),
                    "category": safe_str(row.get(m.get("category"))),
                    "quality_score": safe_float(row.get(m.get("quality_score")), None),
                }
                records_data.append(record_data)
            except Exception as row_error:
                logger_upload.error(f"[NEXUS] Failed to process row {idx}: {row_error}")
                # Continue processing other rows instead of failing entire upload
                continue
        
        # Use bulk insert for better performance
        if records_data:
            db.bulk_insert_mappings(SupplyData, records_data)

        # Add UploadHistory to the SAME transaction
        rows_rejected = len(df) - len(records_data)
        history = UploadHistory(
            filename=filename, file_type=file_ext,
            rows_total=len(df), rows_inserted=len(records_data), rows_rejected=rows_rejected,
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

    # 5. Trigger Progressive Analysis
    skip_analysis = os.getenv("SKIP_ANALYSIS", "false").lower() == "true"
    analysis_started = False
    upload_id = f"{filename}_{int(datetime.now(timezone.utc).timestamp())}"
    
    if not skip_analysis:
        try:
            # Load dataframe for analysis
            analysis_df = df
            engine_kwargs = _get_engine_kwargs()
            
            logger_upload.info(f"[NEXUS] Engine kwargs: {list(engine_kwargs.keys())}")
            logger_upload.info(f"[NEXUS] Available engines: {[(k, v is not None) for k, v in engine_kwargs.items()]}")
            
            # Start progressive analysis
            coordinator.start_analysis(upload_id, analysis_df, engine_kwargs)
            analysis_started = True
            logger_upload.info(f"[NEXUS] Progressive analysis started for {upload_id}")
        except Exception as e:
            logger_upload.error(f"[NEXUS] Failed to start analysis: {e}", exc_info=True)

    return {
        "status": "success",
        "rows_inserted": len(records_data),
        "rows_rejected": rows_rejected,
        "column_mapping": mapping_dict,
        "schema_detected": schema_match,
        "data_quality": quality_report,
        "analysis_started": analysis_started,
        "upload_id": upload_id if analysis_started else None,
        "analysis_progress_url": f"/analysis/progress/{upload_id}" if analysis_started else None,
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
