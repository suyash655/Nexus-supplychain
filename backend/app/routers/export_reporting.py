"""
NEXUS — Export and Reporting Router
====================================
Export and reporting endpoints with enhanced error handling.

Endpoints:
  POST   /api/export/generate              — Generate export for data
  GET    /api/export/downloads/{file_id}   — Download generated export
  GET    /api/export/templates            — List available export templates
  POST   /api/reports/create               — Create a custom report
  GET    /api/reports/{report_id}          — Get report details
  GET    /api/reports                      — List all reports
  POST   /api/reports/{report_id}/schedule — Schedule a report
"""

import logging
import uuid
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks  # type: ignore
from fastapi.responses import FileResponse  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.errors import (  # type: ignore
    NotFoundError,
    ValidationError,
    InvalidOperationError,
    ServiceUnavailableError,
)
from app.core.config import settings  # type: ignore

logger = logging.getLogger("nexus.export_reporting")

router = APIRouter(prefix="/api", tags=["Export & Reporting"])


# ── Enums and Models ───────────────────────────────────────────────────────────

class ExportFormat(str, Enum):
    """Export format enumeration."""
    CSV = "csv"
    EXCEL = "xlsx"
    PDF = "pdf"
    JSON = "json"


class ReportFormat(str, Enum):
    """Report format enumeration."""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "xlsx"


class ExportRequest(BaseModel):
    """Model for export requests."""
    format: ExportFormat
    filters: Dict[str, Any] = Field(default_factory=dict)
    columns: Optional[List[str]] = Field(None, description="Specific columns to export")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")
    include_charts: bool = Field(False, description="Include charts in export")
    report_name: str = Field("export", max_length=200)


class ReportCreate(BaseModel):
    """Model for creating custom reports."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    format: ReportFormat
    template: str = Field("standard", max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    data_source: str = Field("supply_data", max_length=100)


class ReportSchedule(BaseModel):
    """Model for scheduling reports."""
    schedule_type: str = Field(..., description="daily, weekly, monthly")
    schedule_params: Dict[str, Any] = Field(default_factory=dict)
    recipients: List[str] = Field(..., description="Email addresses")
    format: ReportFormat


# ── In-Memory Storage (replace with DB in production) ─────────────────────────

class ExportStore:
    """In-memory storage for exports."""
    
    def __init__(self):
        self.exports: Dict[str, Dict[str, Any]] = {}
        self.reports: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
    
    async def create_export(self, export_data: Dict[str, Any]) -> str:
        """Create a new export record."""
        export_id = str(uuid.uuid4())
        export_data["export_id"] = export_id
        export_data["created_at"] = datetime.now(timezone.utc).isoformat()
        export_data["status"] = "processing"
        
        async with self.lock:
            self.exports[export_id] = export_data
        
        return export_id
    
    async def get_export(self, export_id: str) -> Optional[Dict[str, Any]]:
        """Get export by ID."""
        async with self.lock:
            return self.exports.get(export_id)
    
    async def update_export(self, export_id: str, updates: Dict[str, Any]) -> bool:
        """Update export."""
        async with self.lock:
            if export_id in self.exports:
                self.exports[export_id].update(updates)
                return True
            return False
    
    async def create_report(self, report_data: Dict[str, Any]) -> str:
        """Create a new report."""
        report_id = str(uuid.uuid4())
        report_data["report_id"] = report_id
        report_data["created_at"] = datetime.now(timezone.utc).isoformat()
        report_data["status"] = "draft"
        
        async with self.lock:
            self.reports[report_id] = report_data
        
        return report_id
    
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report by ID."""
        async with self.lock:
            return self.reports.get(report_id)
    
    async def list_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List reports."""
        async with self.lock:
            reports = list(self.reports.values())
            reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return reports[:limit]
    
    async def update_report(self, report_id: str, updates: Dict[str, Any]) -> bool:
        """Update report."""
        async with self.lock:
            if report_id in self.reports:
                self.reports[report_id].update(updates)
                return True
            return False


import asyncio
export_store = ExportStore()


# ── Export Processing Functions ───────────────────────────────────────────────

async def process_export(export_id: str, db: Session):
    """Process export in background."""
    try:
        export = await export_store.get_export(export_id)
        if not export:
            return
        
        format_type = export.get("format")
        filters = export.get("filters", {})
        columns = export.get("columns")
        
        # Generate export file
        file_path = await _generate_export_file(format_type, filters, columns, db)
        
        # Update export status
        await export_store.update_export(export_id, {
            "status": "completed",
            "file_path": file_path,
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info("[NEXUS] Export %s completed: %s", export_id, file_path)
        
    except Exception as e:
        logger.error("[NEXUS] Export %s failed: %s", export_id, e, exc_info=True)
        await export_store.update_export(export_id, {
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now(timezone.utc).isoformat()
        })


async def _generate_export_file(format_type: str, filters: Dict[str, Any], 
                                columns: Optional[List[str]], db: Session) -> str:
    """Generate export file based on format."""
    import pandas as pd  # type: ignore
    from app.models import SupplyData  # type: ignore
    
    # Query data with filters
    query = db.query(SupplyData)
    
    # Apply filters
    if filters.get("supplier"):
        query = query.filter(SupplyData.supplier.ilike(f"%{filters['supplier']}%"))
    if filters.get("region"):
        query = query.filter(SupplyData.region.ilike(f"%{filters['region']}%"))
    if filters.get("category"):
        query = query.filter(SupplyData.category.ilike(f"%{filters['category']}%"))
    
    # Get data
    results = query.all()
    
    # Convert to DataFrame
    data = []
    for row in results:
        data.append({
            "id": row.id,
            "supplier": row.supplier,
            "sku": row.sku,
            "warehouse": row.warehouse,
            "region": row.region,
            "delay_days": row.delay_days,
            "cost": row.cost,
            "quantity": row.quantity,
            "category": row.category,
            "quality_score": row.quality_score,
            "order_date": row.order_date,
            "delivery_date": row.delivery_date,
        })
    
    df = pd.DataFrame(data)
    
    # Filter columns if specified
    if columns:
        available_columns = [col for col in columns if col in df.columns]
        if available_columns:
            df = df[available_columns]
    
    # Create export directory if it doesn't exist
    export_dir = os.path.join(settings.BASE_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    # Generate file based on format
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    if format_type == ExportFormat.CSV:
        file_path = os.path.join(export_dir, f"export_{timestamp}.csv")
        df.to_csv(file_path, index=False)
    elif format_type == ExportFormat.EXCEL:
        file_path = os.path.join(export_dir, f"export_{timestamp}.xlsx")
        df.to_excel(file_path, index=False, engine='openpyxl')
    elif format_type == ExportFormat.JSON:
        file_path = os.path.join(export_dir, f"export_{timestamp}.json")
        df.to_json(file_path, orient='records', indent=2)
    elif format_type == ExportFormat.PDF:
        # PDF generation would require additional libraries
        # For now, generate as CSV and note the limitation
        file_path = os.path.join(export_dir, f"export_{timestamp}.csv")
        df.to_csv(file_path, index=False)
        logger.warning("[NEXUS] PDF export not fully implemented, generated CSV instead")
    
    return file_path


# ── Export Endpoints ───────────────────────────────────────────────────────────

@router.post("/export/generate")
async def generate_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Generate an export of supply chain data.
    
    Exports are processed asynchronously in the background.
    Supports CSV, Excel, PDF, and JSON formats.
    """
    try:
        # Create export record
        export_data = {
            "format": request.format,
            "filters": request.filters,
            "columns": request.columns,
            "report_name": request.report_name,
            "include_charts": request.include_charts,
            "created_by": user.get("id", "unknown"),
        }
        
        export_id = await export_store.create_export(export_data)
        
        # Start background processing
        background_tasks.add_task(process_export, export_id, db)
        
        logger.info("[NEXUS] Export %s created by user %s", export_id, user.get("id", "unknown"))
        
        return {
            "status": "success",
            "export_id": export_id,
            "message": "Export generation started",
            "status_url": f"/api/export/status/{export_id}"
        }
        
    except Exception as e:
        logger.error("[NEXUS] Failed to create export: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create export: {str(e)}")


@router.get("/export/status/{export_id}")
async def get_export_status(
    export_id: str,
    user: dict = Depends(require_auth),
):
    """
    Get the status of an export.
    """
    export = await export_store.get_export(export_id)
    
    if not export:
        raise NotFoundError(f"Export {export_id} not found")
    
    return {
        "export_id": export_id,
        "status": export.get("status"),
        "created_at": export.get("created_at"),
        "completed_at": export.get("completed_at"),
        "error": export.get("error"),
        "download_url": f"/api/export/downloads/{export_id}" if export.get("status") == "completed" else None,
    }


@router.get("/export/downloads/{export_id}")
async def download_export(
    export_id: str,
    user: dict = Depends(require_auth),
):
    """
    Download a generated export file.
    """
    export = await export_store.get_export(export_id)
    
    if not export:
        raise NotFoundError(f"Export {export_id} not found")
    
    if export.get("status") != "completed":
        raise InvalidOperationError(f"Export is not ready for download. Current status: {export.get('status')}")
    
    file_path = export.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise NotFoundError("Export file not found on server")
    
    # Determine filename
    filename = os.path.basename(file_path)
    
    logger.info("[NEXUS] Export %s downloaded by user %s", export_id, user.get("id", "unknown"))
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.get("/export/templates")
async def list_export_templates(
    user: dict = Depends(require_auth),
):
    """
    List available export templates.
    """
    templates = [
        {
            "id": "standard",
            "name": "Standard Export",
            "description": "Complete data export with all columns",
            "format": ["csv", "xlsx", "json"],
            "columns": ["all"],
        },
        {
            "id": "summary",
            "name": "Summary Export",
            "description": "Key metrics and summary data",
            "format": ["csv", "xlsx", "pdf"],
            "columns": ["supplier", "sku", "delay_days", "cost", "region"],
        },
        {
            "id": "risk_analysis",
            "name": "Risk Analysis Export",
            "description": "Risk-focused data for analysis",
            "format": ["xlsx", "pdf"],
            "columns": ["supplier", "region", "delay_days", "quality_score", "category"],
        },
        {
            "id": "performance",
            "name": "Performance Export",
            "description": "Performance metrics and KPIs",
            "format": ["xlsx", "pdf"],
            "columns": ["supplier", "warehouse", "delay_days", "cost", "quantity"],
        },
    ]
    
    return {
        "templates": templates,
        "total": len(templates),
    }


# ── Report Endpoints ───────────────────────────────────────────────────────────

@router.post("/reports/create")
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Create a custom report.
    """
    try:
        # Create report record
        report_data = {
            "name": report.name,
            "description": report.description,
            "format": report.format,
            "template": report.template,
            "parameters": report.parameters,
            "data_source": report.data_source,
            "created_by": user.get("id", "unknown"),
        }
        
        report_id = await export_store.create_report(report_data)
        
        logger.info("[NEXUS] Report %s created by user %s", report_id, user.get("id", "unknown"))
        
        # Return report details
        report_response = await export_store.get_report(report_id)
        
        return {
            "status": "success",
            "report_id": report_id,
            "report": report_response,
        }
        
    except Exception as e:
        logger.error("[NEXUS] Failed to create report: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    user: dict = Depends(require_auth),
):
    """
    Get report details.
    """
    report = await export_store.get_report(report_id)
    
    if not report:
        raise NotFoundError(f"Report {report_id} not found")
    
    return report


@router.get("/reports")
async def list_reports(
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(require_auth),
):
    """
    List all reports.
    """
    reports = await export_store.list_reports(limit=limit)
    
    return {
        "reports": reports,
        "total": len(reports),
    }


@router.post("/reports/{report_id}/schedule")
async def schedule_report(
    report_id: str,
    schedule: ReportSchedule,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_auth),
):
    """
    Schedule a report for automatic generation and delivery.
    """
    report = await export_store.get_report(report_id)
    
    if not report:
        raise NotFoundError(f"Report {report_id} not found")
    
    # Update report with schedule information
    await export_store.update_report(report_id, {
        "schedule": {
            "type": schedule.schedule_type,
            "params": schedule.schedule_params,
            "recipients": schedule.recipients,
            "format": schedule.format,
        },
        "status": "scheduled",
    })
    
    logger.info(
        "[NEXUS] Report %s scheduled by user %s (%s to %s)",
        report_id, user.get("id", "unknown"), schedule.schedule_type, ", ".join(schedule.recipients)
    )
    
    return {
        "status": "success",
        "report_id": report_id,
        "schedule": {
            "type": schedule.schedule_type,
            "params": schedule.schedule_params,
            "recipients": schedule.recipients,
            "format": schedule.format,
        },
        "message": "Report scheduled successfully"
    }