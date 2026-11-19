"""
NEXUS — Suppliers Router (Sub-Tier Discovery)
===============================================
P0 Gap Fix: Multi-tier supplier graph with sub-tier discovery.

Endpoints:
  GET /api/suppliers/{id}/subtier — Discover sub-tier supplier relationships
"""

import logging

from fastapi import APIRouter, Depends, Query  # type: ignore

from app.core.dependencies import require_auth  # type: ignore

logger = logging.getLogger("nexus.suppliers")

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/{supplier_id}/subtier")
async def get_subtier_suppliers(
    supplier_id: str,
    max_depth: int = Query(3, ge=1, le=5, description="Maximum tier depth to discover"),
    user: dict = Depends(require_auth),
):
    """
    Discover sub-tier (Tier 2, Tier 3, ... Tier N) suppliers for a given supplier.

    Uses the Temporal Trend Engine's sub-tier discovery method.
    Currently returns mock data — designed to be swapped for real data sources
    (Dun & Bradstreet, Panjiva/S&P trade data, ERP connectors).

    Returns:
        - supplier_id: Unique identifier for the sub-tier supplier
        - name: Display name
        - tier: Tier level (2, 3, etc.)
        - relationship_type: RAW_MATERIAL, COMPONENT, KNOWN_PARTNER
        - parent_id: The supplier this sub-tier feeds into
        - location: Geographic location
        - risk_score: Risk assessment (0-100, null if unknown)
        - confidence: Discovery confidence (0-1)
        - data_source: Where the relationship was discovered
        - products: Products supplied
    """
    # Get the temporal trend engine from the app engines singleton.
    from app.main import engines  # type: ignore

    tgnn = engines.tgnn_engine_instance
    if tgnn is None:
        # Return mock data even if engine is not initialised
        # This ensures the API contract is stable regardless of engine state
        logger.warning("Temporal trend engine not available, returning minimal mock data")
        return {
            "supplier_id": supplier_id,
            "subtier_count": 0,
            "max_depth_searched": max_depth,
            "subtiers": [],
            "data_source": "unavailable",
            "note": "Temporal Trend Engine not initialised. Upload data to enable sub-tier discovery.",
        }

    # Discover sub-tier relationships
    subtiers = tgnn.discover_subtier_relationships(supplier_id)

    # Filter by max depth
    filtered = [s for s in subtiers if s.get("tier", 2) <= max_depth + 1]

    # Build tier hierarchy summary
    tier_summary = {}
    for s in filtered:
        tier = s.get("tier", 2)
        tier_summary[f"tier_{tier}"] = tier_summary.get(f"tier_{tier}", 0) + 1

    return {
        "supplier_id": supplier_id,
        "subtier_count": len(filtered),
        "max_depth_searched": max_depth,
        "tier_summary": tier_summary,
        "subtiers": filtered,
        "data_source": "temporal_graph + mock",
        "note": (
            "Sub-tier data is currently mocked. In production, this endpoint will "
            "pull from Dun & Bradstreet, Panjiva, or your ERP system."
        ),
    }
