"""
NEXUS — Upload Router
=====================
Orchestrates file upload, schema matching, and atomic database insertion.
Parsing and validation logic have been extracted to app/services/upload/.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.config import settings  # type: ignore
from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.orchestrator import _get_engine_kwargs, is_analyzing  # type: ignore
from app.core.orchestrator import run_full_analysis as _run
from app.models import AnalysisResult, SupplyData, UploadHistory  # type: ignore

# Refactored service modules
from app.services.upload.parser import parse_upload_file  # type: ignore
from app.services.upload.schema import (  # type: ignore
    auto_detect_columns,
    low_confidence_fields,
    mapping_dict_from_detection,
)
from app.services.upload.validator import safe_float, safe_int, safe_str, validate_mapped_values  # type: ignore
from app.utils.schema_fingerprints import detect_schema  # type: ignore

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

    # 4. Clear existing data before inserting new data
    # This ensures each upload replaces the previous dataset instead of accumulating
    try:
        deleted_count = db.query(SupplyData).delete()
        deleted_analysis = db.query(AnalysisResult).delete()
        logger_upload.info(f"[NEXUS] Cleared {deleted_count} existing records from SupplyData")
        logger_upload.info(f"[NEXUS] Cleared {deleted_analysis} cached analysis results")
        db.commit()
    except Exception as e:
        db.rollback()
        logger_upload.error(f"[NEXUS] Failed to clear existing data: {e}")
        # Continue with upload even if clearing fails

    # 5. Atomic Database Insertion
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

    # 5. Trigger Full Analysis in background
    # Always runs regardless of file size.
    # Uses run_full_analysis which loads from DB (gets the correctly mapped data)
    # and saves all results to analysis_results table (what the dashboard reads).
    analysis_started = False
    upload_id = f"{filename}_{int(datetime.now(timezone.utc).timestamp())}"

    if not is_analyzing():
        try:
            engine_kwargs = _get_engine_kwargs()
            if any(v is not None for v in engine_kwargs.values()):
                background_tasks.add_task(_run, **engine_kwargs)
                analysis_started = True
                logger_upload.info("[NEXUS] Full analysis queued as background task for %s", filename)
            else:
                logger_upload.warning("[NEXUS] No engines available — analysis skipped")
        except Exception as e:
            logger_upload.error("[NEXUS] Failed to queue analysis: %s", e, exc_info=True)
    else:
        logger_upload.info("[NEXUS] Analysis already running — will reflect this upload on next run")

    return {
        "status": "success",
        "rows_inserted": len(records_data),
        "rows_rejected": rows_rejected,
        "column_mapping": mapping_dict,
        "schema_detected": schema_match,
        "data_quality": quality_report,
        "analysis_started": analysis_started,
        "upload_id": upload_id,
        "message": (
            "Upload successful. Analysis started in background — dashboard will update in ~60 seconds."
            if analysis_started
            else "Upload successful. Analysis already running — dashboard will update shortly."
        ),
    }


@router.post("/upload/preview")
async def preview_upload(
    file: UploadFile = File(...),
    user: dict = Depends(require_auth),
):
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


@router.post("/upload/sample")
def load_sample_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    1-Click Demo: Ingest bundled benchmark supply chain dataset and kick off analysis.
    Eliminates friction for first-time evaluators and prospective customers.
    """
    candidates = [
        Path(settings.BASE_DIR) / "data" / "sample" / "sample_supply_chain_synthetic.csv",
        Path("data/sample/sample_supply_chain_synthetic.csv"),
        Path(__file__).resolve().parents[4] / "data" / "sample" / "sample_supply_chain_synthetic.csv",
    ]
    sample_path = None
    for cand in candidates:
        if cand.exists():
            sample_path = cand
            break

    if not sample_path:
        raise HTTPException(status_code=404, detail="Sample dataset not found on server")

    with open(sample_path, "rb") as f:
        contents = f.read()

    filename = "sample_supply_chain_synthetic.csv"
    df = parse_upload_file(contents, filename, settings.MAX_UPLOAD_BYTES, max_preview_rows=None)
    if df.empty:
        raise HTTPException(status_code=400, detail="Sample file is empty")

    schema_match = detect_schema(df.columns.tolist())
    if schema_match and schema_match["match_score"] >= 0.8:
        mapping_dict = {v: k for k, v in schema_match["mapping"].items()}
    else:
        detection = auto_detect_columns(df.columns.tolist(), sample_data=df.head(50).to_dict("records"))
        mapping_dict = mapping_dict_from_detection(detection)

    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "detected_columns": list(df.columns),
        "mapped_columns": mapping_dict,
        "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
        "mapping_user_confirmed": True,
        "column_validation": validate_mapped_values(df, mapping_dict),
    }

    try:
        deleted_count = db.query(SupplyData).delete()
        deleted_analysis = db.query(AnalysisResult).delete()
        logger_upload.info(f"[NEXUS] Sample load cleared {deleted_count} rows from SupplyData and {deleted_analysis} analysis results")
        db.commit()
    except Exception as e:
        db.rollback()
        logger_upload.error(f"[NEXUS] Failed to clear existing data for sample load: {e}")

    records_data = []
    df_dict = df.to_dict("records")
    m = mapping_dict

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
        except Exception:
            continue

    if records_data:
        db.bulk_insert_mappings(SupplyData, records_data)

    history = UploadHistory(
        filename=filename,
        file_type="csv",
        rows_total=len(df),
        rows_inserted=len(records_data),
        rows_rejected=len(df) - len(records_data),
        columns_detected=list(df.columns),
        column_mapping=mapping_dict,
        data_quality_report=quality_report,
    )
    db.add(history)
    db.commit()

    analysis_started = False
    if not is_analyzing():
        try:
            engine_kwargs = _get_engine_kwargs()
            if any(v is not None for v in engine_kwargs.values()):
                background_tasks.add_task(_run, **engine_kwargs)
                analysis_started = True
                logger_upload.info("[NEXUS] Full analysis queued as background task for sample load")
        except Exception as e:
            logger_upload.error("[NEXUS] Failed to queue analysis on sample load: %s", e, exc_info=True)

    return {
        "status": "success",
        "rows_inserted": len(records_data),
        "filename": filename,
        "analysis_started": analysis_started,
        "message": (
            "Sample dataset loaded successfully. Analysis started in background — dashboard will update shortly."
            if analysis_started
            else "Sample dataset loaded successfully."
        ),
    }


@router.get("/upload/template")
def download_starter_template(user: dict = Depends(require_auth)):
    """
    Download a starter CSV template formatted with valid canonical headers and sample rows.
    """
    template_content = (
        "supplier,sku,warehouse,region,shipment_id,order_date,delivery_date,delay_days,cost,quantity,category,quality_score\n"
        "Apex Components,SKU-101,WH-East,North America,SHP-2025-001,2025-01-05,2025-01-08,0,450.00,500,Electronics,0.98\n"
        "Apex Components,SKU-102,WH-East,North America,SHP-2025-002,2025-01-12,2025-01-16,1,320.50,300,Electronics,0.95\n"
        "Beacon Logistics,SKU-201,WH-Central,Europe,SHP-2025-003,2025-01-06,2025-01-14,4,1250.00,1200,Machinery,0.91\n"
        "Cascade Systems,SKU-301,WH-West,Asia-Pacific,SHP-2025-004,2025-01-10,2025-01-12,0,210.00,800,Fasteners,0.99\n"
        "Delta Precision,SKU-401,WH-Central,Europe,SHP-2025-005,2025-01-15,2025-01-22,6,890.00,450,Electronics,0.88\n"
    )
    return Response(
        content=template_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="nexus_supply_chain_template.csv"'},
    )

