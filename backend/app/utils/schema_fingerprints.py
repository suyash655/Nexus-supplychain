"""
NEXUS — Known Schema Fingerprints
===================================
Pre-built column mappings for common ERP / TMS / customs export formats
whose column names are internal codes with no English synonyms.

When the upload router detects a fingerprint match it applies this mapping
directly instead of going through synonym matching, giving confidence=1.0
on every field that is in the fingerprint.

How to add a new schema:
  1. Get a sample export from the source system
  2. Identify the column name → internal field mapping
  3. Add an entry to KNOWN_SCHEMAS
  4. Add at least 2 identifying columns to the schema's "signature" key
     (columns that uniquely identify this schema vs. others)

The match algorithm:
  - Normalise the uploaded file's column names (lowercase, strip, replace spaces)
  - For each known schema, check how many of its "signature" columns are present
  - If ≥ 80% of signature columns match → apply the schema's mapping
  - Confidence = 1.0 for all fields that appear in the mapping
"""

from typing import Dict, List, Optional


# Each entry:
#   "signature"  : columns that uniquely identify this schema (normalised)
#   "mapping"    : {normalised_source_column: internal_field}
#   "label"      : human-readable name for the UI

KNOWN_SCHEMAS: Dict[str, Dict] = {

    "sap_mm_purchase": {
        "label": "SAP MM — Purchasing (ME2N / ME2M export)",
        "signature": ["lifnr", "matnr", "ebeln", "bedat", "eindt"],
        "mapping": {
            "lifnr":   "supplier",      # Vendor number
            "matnr":   "sku",           # Material number
            "lgort":   "warehouse",     # Storage location
            "regio":   "region",        # Region
            "werks":   "warehouse",     # Plant (alternative to lgort)
            "ebeln":   "shipment_id",   # Purchase order number
            "ebelp":   "shipment_id",   # PO line item (fallback)
            "bedat":   "order_date",    # PO creation date
            "eindt":   "delivery_date", # Delivery date
            "netwr":   "cost",          # Net value
            "menge":   "quantity",      # Quantity
            "matkl":   "category",      # Material group
            "prüflos": "quality_score", # Inspection lot (proxy)
        },
    },

    "sap_sd_delivery": {
        "label": "SAP SD — Outbound Delivery (VL06O export)",
        "signature": ["vbeln", "kunnr", "matnr", "wadat_ist", "ntgew"],
        "mapping": {
            "lifnr":     "supplier",
            "kunnr":     "supplier",        # Customer (used as origin in outbound)
            "matnr":     "sku",
            "lgnum":     "warehouse",
            "vbeln":     "shipment_id",     # Delivery document
            "wadat_ist": "delivery_date",   # Actual goods issue date
            "lddat":     "order_date",      # Loading date
            "vsbed":     "region",          # Shipping condition (proxy for region)
            "ntgew":     "quantity",        # Net weight
            "bdmng":     "quantity",        # Requirement quantity (alternative)
        },
    },

    "oracle_tms_freight": {
        "label": "Oracle TMS — Freight Order export",
        "signature": ["carriercode", "pro#", "shipdate", "delivdate", "transitdays"],
        "mapping": {
            "carriercode":   "supplier",
            "pro#":          "shipment_id",
            "reference":     "shipment_id",
            "shipdate":      "order_date",
            "delivdate":     "delivery_date",
            "transitdays":   "delay_days",
            "freightcharge": "cost",
            "weight":        "quantity",
            "origzip":       "warehouse",
            "destzip":       "region",
            "servicelevel":  "category",
            "conditionscore":"quality_score",
        },
    },

    "uk_customs_cds": {
        "label": "UK CDS / CHIEF — Customs Declaration export",
        "signature": ["declaration_no", "mrn", "hs_code", "date_of_acceptance", "cif_value_(usd)"],
        "mapping": {
            "declarant":         "supplier",
            "hs_code":           "category",
            "country_of_origin": "region",
            "port_of_loading":   "warehouse",
            "date_of_acceptance":"order_date",
            "release_date":      "delivery_date",
            "cif_value_(usd)":   "cost",
            "quantity_(units)":  "quantity",
            "declaration_no":    "shipment_id",
            "mrn":               "shipment_id",
        },
    },

    "shopify_orders": {
        "label": "Shopify — Orders export",
        "signature": ["name", "financial_status", "fulfillment_status", "vendor", "lineitem_sku"],
        "mapping": {
            "vendor":               "supplier",
            "lineitem_sku":         "sku",
            "lineitem_name":        "sku",
            "created_at":           "order_date",
            "fulfilled_at":         "delivery_date",
            "lineitem_price":       "cost",
            "lineitem_quantity":    "quantity",
            "shipping_province":    "region",
            "shipping_country":     "region",
            "name":                 "shipment_id",
        },
    },

    "netsuite_po": {
        "label": "NetSuite — Purchase Order export",
        "signature": ["internal_id", "vendor", "item", "expected_receipt_date", "amount"],
        "mapping": {
            "vendor":                "supplier",
            "vendor_id":             "supplier",
            "item":                  "sku",
            "item_id":               "sku",
            "location":              "warehouse",
            "subsidiary":            "region",
            "internal_id":           "shipment_id",
            "document_number":       "shipment_id",
            "date":                  "order_date",
            "expected_receipt_date": "delivery_date",
            "amount":                "cost",
            "quantity":              "quantity",
            "item_type":             "category",
        },
    },

    "dataco_supply_chain": {
        "label": "DataCo Smart Supply Chain",
        "signature": ["days_for_shipping_real", "days_for_shipment_scheduled", "late_delivery_risk", "order_item_total", "category_id"],
        "mapping": {
            "department_name":          "supplier",
            "product_name":             "sku",
            "days_for_shipping_real":   "delay_days",
            "order_item_total":         "cost",
            "order_date_dateorders":    "order_date",
            "shipping_date_dateorders": "delivery_date",
            "order_city":               "warehouse",
            "order_region":             "region",
            "order_item_quantity":      "quantity",
            "order_id":                 "shipment_id",
            "category_name":            "category",
        },
    },
}


def _normalise(col: str) -> str:
    """Normalise a column name for fingerprint comparison."""
    return col.lower().strip().replace(" ", "_").replace("(", "").replace(")", "")


def detect_schema(columns: List[str]) -> Optional[Dict]:
    """
    Compare uploaded file columns against known schema fingerprints.

    Returns:
        {
          "schema_id":   "sap_mm_purchase",
          "label":       "SAP MM — Purchasing ...",
          "match_score": 0.8,           # fraction of signature cols matched
          "mapping":     {...},          # {original_col: internal_field}
          "confidence":  1.0,
        }
        or None if no schema matches at ≥ 60% of signature columns.
    """
    normalised_cols = {_normalise(c): c for c in columns}

    best_schema_id:  Optional[str]  = None
    best_match_score: float          = 0.0

    for schema_id, schema in KNOWN_SCHEMAS.items():
        signature = schema["signature"]
        hits = sum(1 for s in signature if s in normalised_cols)
        score = hits / max(len(signature), 1)
        if score > best_match_score:
            best_match_score = score
            best_schema_id   = schema_id

    if best_schema_id is None or best_match_score < 0.6:
        return None

    schema   = KNOWN_SCHEMAS[best_schema_id]
    # Build mapping using original column names (not normalised)
    mapping: Dict[str, str] = {}
    for norm_col, orig_col in normalised_cols.items():
        if norm_col in schema["mapping"]:
            internal_field = schema["mapping"][norm_col]
            # First writer wins (don't overwrite a confirmed mapping)
            if internal_field not in mapping.values():
                mapping[orig_col] = internal_field

    return {
        "schema_id":   best_schema_id,
        "label":       schema["label"],
        "match_score": round(best_match_score, 2),
        "mapping":     mapping,
        "confidence":  1.0,
    }
