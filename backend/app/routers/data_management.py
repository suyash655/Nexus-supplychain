"""
NEXUS — Data Management Router
================================
CRUD operations for supply chain data with enhanced error handling.

Endpoints:
  PUT    /api/data/records/{id}         — Update a specific supply chain record
  DELETE /api/data/records/{id}         — Delete a specific supply chain record
  POST   /api/data/records/bulk-delete  — Bulk delete records
  GET    /api/data/records/search       — Advanced search with filters
  POST   /api/data/records/bulk-update  — Bulk update records
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.errors import (  # type: ignore
    InvalidOperationError,
    NotFoundError,
    ValidationError,
)
from app.models import SupplyData  # type: ignore

logger = logging.getLogger("nexus.data_management")

router = APIRouter(prefix="/api/data", tags=["Data Management"])


# ── Pydantic Models ────────────────────────────────────────────────────────────

class SupplyDataUpdate(BaseModel):
    """Model for updating supply chain records."""
    supplier: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, max_length=200)
    warehouse: Optional[str] = Field(None, max_length=200)
    region: Optional[str] = Field(None, max_length=200)
    shipment_id: Optional[str] = Field(None, max_length=200)
    order_date: Optional[str] = Field(None, max_length=100)
    delivery_date: Optional[str] = Field(None, max_length=100)
    delay_days: Optional[int] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=200)
    quality_score: Optional[float] = Field(None, ge=0, le=100)


class BulkDeleteRequest(BaseModel):
    """Model for bulk delete operations."""
    record_ids: List[int] = Field(..., min_length=1, max_length=1000)


class BulkUpdateRequest(BaseModel):
    """Model for bulk update operations."""
    filters: Dict[str, Any] = Field(default_factory=dict)
    updates: SupplyDataUpdate
    max_records: int = Field(100, ge=1, le=1000)


class SearchFilters(BaseModel):
    """Model for advanced search filters."""
    supplier: Optional[str] = None
    sku: Optional[str] = None
    region: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None
    min_delay_days: Optional[int] = Field(None, ge=0)
    max_delay_days: Optional[int] = Field(None, ge=0)
    min_cost: Optional[float] = Field(None, ge=0)
    max_cost: Optional[float] = Field(None, ge=0)
    min_quality_score: Optional[float] = Field(None, ge=0, le=100)
    max_quality_score: Optional[float] = Field(None, ge=0, le=100)


# ── CRUD Endpoints ─────────────────────────────────────────────────────────────

@router.put("/records/{record_id}")
def update_record(
    record_id: int,
    update_data: SupplyDataUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Update a specific supply chain record.

    Supports partial updates - only provided fields will be updated.
    """
    # Validate that record exists
    record = db.query(SupplyData).filter(SupplyData.id == record_id).first()
    if not record:
        raise NotFoundError(f"Record with ID {record_id} not found")

    # Build update dictionary with only non-None fields
    update_dict = {}
    for field, value in update_data.model_dump(exclude_unset=True).items():
        update_dict[field] = value

    if not update_dict:
        raise ValidationError("No valid fields provided for update")

    try:
        # Apply updates
        for field, value in update_dict.items():
            setattr(record, field, value)

        record.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(record)

        logger.info("[NEXUS] Record %d updated by user %s", record_id, user.get("id", "unknown"))

        return {
            "status": "success",
            "record_id": record_id,
            "updated_fields": list(update_dict.keys()),
            "record": {
                "id": record.id,
                "supplier": record.supplier,
                "sku": record.sku,
                "warehouse": record.warehouse,
                "region": record.region,
                "delay_days": record.delay_days,
                "cost": record.cost,
                "updated_at": record.updated_at.isoformat() if record.updated_at else None,
            }
        }
    except Exception as e:
        db.rollback()
        logger.error("[NEXUS] Failed to update record %d: %s", record_id, e, exc_info=True)
        raise InvalidOperationError(f"Failed to update record: {str(e)}")


@router.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Delete a specific supply chain record.
    """
    # Validate that record exists
    record = db.query(SupplyData).filter(SupplyData.id == record_id).first()
    if not record:
        raise NotFoundError(f"Record with ID {record_id} not found")

    try:
        db.delete(record)
        db.commit()

        logger.info("[NEXUS] Record %d deleted by user %s", record_id, user.get("id", "unknown"))

        return {
            "status": "success",
            "record_id": record_id,
            "message": "Record deleted successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error("[NEXUS] Failed to delete record %d: %s", record_id, e, exc_info=True)
        raise InvalidOperationError(f"Failed to delete record: {str(e)}")


@router.post("/records/bulk-delete")
def bulk_delete_records(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Bulk delete multiple supply chain records.

    Returns summary of deleted records count and any failures.
    """
    # Validate that records exist
    records = db.query(SupplyData).filter(SupplyData.id.in_(request.record_ids)).all()
    found_ids = {r.id for r in records}
    missing_ids = set(request.record_ids) - found_ids

    if not records:
        raise NotFoundError("No records found with the provided IDs")

    try:
        deleted_count = 0
        for record in records:
            db.delete(record)
            deleted_count += 1

        db.commit()

        logger.info(
            "[NEXUS] Bulk delete: %d records deleted by user %s (missing: %d)",
            deleted_count, user.get("id", "unknown"), len(missing_ids)
        )

        return {
            "status": "success",
            "deleted_count": deleted_count,
            "requested_count": len(request.record_ids),
            "missing_ids": list(missing_ids) if missing_ids else None,
        }
    except Exception as e:
        db.rollback()
        logger.error("[NEXUS] Bulk delete failed: %s", e, exc_info=True)
        raise InvalidOperationError(f"Bulk delete failed: {str(e)}")


@router.get("/records/search")
def search_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    supplier: Optional[str] = Query(None),
    sku: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    warehouse: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_delay_days: Optional[int] = Query(None, ge=0),
    max_delay_days: Optional[int] = Query(None, ge=0),
    min_cost: Optional[float] = Query(None, ge=0),
    max_cost: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Advanced search with multiple filters.
    Supports pagination and various field filters.
    """
    # Build query with filters
    query = db.query(SupplyData)

    if supplier:
        query = query.filter(SupplyData.supplier.ilike(f"%{supplier}%"))
    if sku:
        query = query.filter(SupplyData.sku.ilike(f"%{sku}%"))
    if region:
        query = query.filter(SupplyData.region.ilike(f"%{region}%"))
    if warehouse:
        query = query.filter(SupplyData.warehouse.ilike(f"%{warehouse}%"))
    if category:
        query = query.filter(SupplyData.category.ilike(f"%{category}%"))
    if min_delay_days is not None:
        query = query.filter(SupplyData.delay_days >= min_delay_days)
    if max_delay_days is not None:
        query = query.filter(SupplyData.delay_days <= max_delay_days)
    if min_cost is not None:
        query = query.filter(SupplyData.cost >= min_cost)
    if max_cost is not None:
        query = query.filter(SupplyData.cost <= max_cost)

    # Get total count
    total = query.count()

    # Get paginated results
    records = query.order_by(SupplyData.id.desc()).offset(skip).limit(limit).all()

    return {
        "data": [
            {
                "id": r.id,
                "supplier": r.supplier,
                "sku": r.sku,
                "warehouse": r.warehouse,
                "region": r.region,
                "delay_days": r.delay_days,
                "cost": r.cost,
                "quantity": r.quantity,
                "category": r.category,
                "quality_score": r.quality_score,
                "order_date": r.order_date,
                "delivery_date": r.delivery_date,
            }
            for r in records
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/records/bulk-update")
def bulk_update_records(
    request: BulkUpdateRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Bulk update records matching filters.

    Allows updating multiple records that match specific criteria.
    Limited to max_records per operation to prevent excessive updates.
    """
    # Build query with filters
    query = db.query(SupplyData)

    filters = request.filters
    if filters.get("supplier"):
        query = query.filter(SupplyData.supplier.ilike(f"%{filters['supplier']}%"))
    if filters.get("sku"):
        query = query.filter(SupplyData.sku.ilike(f"%{filters['sku']}%"))
    if filters.get("region"):
        query = query.filter(SupplyData.region.ilike(f"%{filters['region']}%"))
    if filters.get("category"):
        query = query.filter(SupplyData.category.ilike(f"%{filters['category']}%"))

    # Get matching records
    records = query.limit(request.max_records).all()

    if not records:
        raise NotFoundError("No records found matching the provided filters")

    # Build update dictionary
    update_dict = {}
    for field, value in request.updates.model_dump(exclude_unset=True).items():
        update_dict[field] = value

    if not update_dict:
        raise ValidationError("No valid fields provided for update")

    try:
        updated_count = 0
        for record in records:
            for field, value in update_dict.items():
                setattr(record, field, value)
            record.updated_at = datetime.now(timezone.utc)
            updated_count += 1

        db.commit()

        logger.info(
            "[NEXUS] Bulk update: %d records updated by user %s",
            updated_count, user.get("id", "unknown")
        )

        return {
            "status": "success",
            "updated_count": updated_count,
            "max_records": request.max_records,
            "updated_fields": list(update_dict.keys()),
        }
    except Exception as e:
        db.rollback()
        logger.error("[NEXUS] Bulk update failed: %s", e, exc_info=True)
        raise InvalidOperationError(f"Bulk update failed: {str(e)}")
