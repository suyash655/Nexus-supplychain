"""
NEXUS — Upload Schema Detection
===============================
Handles auto-detecting column mappings using exact match, token overlap,
and value-based inference (for ERP codes).
"""

import re
import warnings
from typing import Dict, List, Optional

import pandas as pd  # type: ignore

# Suppress pandas date parsing warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*Parsing dates.*")


def _clean_currency_value(v) -> Optional[float]:
    """
    Clean currency values by removing symbols and handling international formats.
    Handles both US (1,234.56), European (1.234,56), and Indian (1,00,000.00) formats.
    """
    if v is None:
        return None

    cleaned = str(v).strip()

    # Remove currency symbols
    for symbol in ['$', '€', '£', '¥', '₹', 'R$', 'AUD', 'USD', 'EUR', 'GBP']:
        cleaned = cleaned.replace(symbol, '')

    # Handle different number formats
    if ',' in cleaned and '.' in cleaned:
        # Could be European (1.234,56) or US/Indian (1,234.56 or 1,00,000.00)
        parts_comma = cleaned.split(',')
        parts_dot = cleaned.split('.')

        # European format detection: comma is decimal, dot is thousand separator
        # Pattern: there are more than 2 parts when split by dot (indicating thousand separators)
        # OR the part after comma is exactly 2 digits (typical decimal precision)
        if len(parts_comma) == 2 and len(parts_comma[1]) <= 2 and len(parts_dot) > 1:
            # European format: 1.234,56 -> 1234.56
            cleaned = parts_comma[0].replace('.', '') + '.' + parts_comma[1]
        else:
            # US/Indian format: comma is thousand separator
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        parts = cleaned.split(',')
        # Check if it's European decimal (e.g., 123,45) or thousand separator
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely European decimal format
            cleaned = parts[0] + '.' + parts[1]
        else:
            # Thousand separator (US or Indian)
            cleaned = cleaned.replace(',', '')

    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

# Maps internal field name → list of HIGH-confidence column name synonyms
HIGH_CONFIDENCE_SYNONYMS: Dict[str, List[str]] = {
    "supplier": [
        "supplier", "vendor", "supplier_name", "vendor_name", "manufacturer",
        "ven_no", "vendor_id", "supplier_code", "sup_name", "sup_id", "supp",
        "supplier_id", "supplier_code", "vendor_code",
        "lifnr",  # SAP vendor code
    ],
    "sku": [
        "sku", "sku_id", "product_id", "item_id", "part_number", "product_code",
        "item_code", "material", "material_id", "part_no", "pn",
        "product", "item", "product_name", "material_number",
        "matnr",  # SAP material code
    ],
    "delay_days": [
        "delay_days", "days_late", "lead_time_variance", "late_days",
        "shipment_delay", "delay_d", "days_delayed", "lt_variance",
        "dlydays",  # SAP delay days
    ],
    "cost": [
        "cost", "unit_cost", "total_cost", "inv_amount", "invoice_amount",
        "unit_price", "total_amount", "spend",
        "netwr",  # SAP net value
    ],
    "warehouse": [
        "warehouse", "warehouse_name", "distribution_center", "dc",
        "facility", "wh", "depot", "plant", "warehouse_id", "wh_name",
        "location_name", "location", "storage_location", "storage",
        "lgort",  # SAP storage location
    ],
    "region": [
        "region", "origin_region", "supplier_region", "source_region",
        "dest_country", "origin", "area", "zone", "territory", "location_area",
        "regio",  # SAP region
    ],
    "shipment_id": [
        "shipment_id", "shipment", "order_id", "order_number", "tracking",
        "po_number", "po", "purchase_order", "invoice_no", "ref_no", "reference",
        "ebeln",  # SAP PO number
    ],
    "order_date": [
        "order_date", "order_dt", "purchase_date", "po_date",
        "order_created", "ordered_on", "order_date_(dateorders)",
        "created_date", "created", "order_created_date", "po_created_date",
        "bedat",  # SAP order date
    ],
    "delivery_date": [
        "delivery_date", "delivery_dt", "received_date", "arrival_date",
        "delivered_on", "recv_date", "eta", "actual_delivery",
        "shipping_date_(dateorders)", "shipping_date", "arrived_date", "arrival",
        "eindt",  # SAP delivery date
    ],
    "quantity": [
        "quantity", "qty", "units", "qty_ordered", "qty_shipped",
        "num_units", "pieces", "pcs",
        "menge",  # SAP quantity
    ],
    "category": [
        "category", "product_category", "product_group", "prod_cat",
        "item_type", "segment", "classification", "type", "type_name",
        "product_type", "item_category", "group",
        "matkl",  # SAP material group
    ],
    "quality_score": [
        "quality_score", "quality_rating", "qc_score", "inspection_score",
        "inspection_score", "inspection", "quality", "rating", "grade",
        "prüflos",  # SAP inspection lot
    ],
}

# Maps internal field name → list of LOW-confidence synonyms (require user confirmation)
LOW_CONFIDENCE_SYNONYMS: Dict[str, List[str]] = {
    "supplier": ["source", "mfr", "mfg", "manufacturer_name"],
    "sku": ["product_code", "item_number", "stock_code"],
    "delay_days": ["delay", "lead_time", "lateness"],
    "cost": ["price", "amount", "value", "order_item_total", "unit_price"],
    "warehouse": ["storage", "location_code", "facility_name"],
    "region": ["location", "country", "city", "geo", "geography", "market", "order_country", "customer_country"],
    "shipment_id": ["id", "record_id", "tracking_id"],
    "order_date": ["date", "order_created_date", "po_created_date"],
    "delivery_date": ["ship_date", "arrival"],
    "quantity": ["volume", "count", "pieces"],
    "category": ["type", "group", "segment", "classification"],
    "quality_score": ["performance", "inspection_rating"],
}

AUTO_ACCEPT_THRESHOLD = 0.5  # Lowered from 0.8 to be more lenient


def _tokenize(s: str) -> set:
    """Split a column name into lowercase tokens."""
    parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', s)
    tokens = set(re.split(r'[_\s\-\.]+', parts.lower()))
    return {t for t in tokens if len(t) > 1}


def _infer_field_from_values(col: str, sample_values: list) -> Optional[str]:
    """
    Infer the internal field a column represents by examining its values,
    independent of the column name. Handles ERP code-name columns.
    """
    if not sample_values:
        return None

    non_null = [v for v in sample_values if v is not None and str(v).strip() not in ("", "nan", "NaN")]
    if len(non_null) < 3:
        return None

    str_vals = [str(v).strip() for v in non_null[:50]]

    # ── date detection ──
    date_hits = 0
    for v in str_vals[:20]:
        try:
            # Try multiple date parsing approaches to handle mixed formats
            date_str = str(v).strip()
            # Try with dayfirst for European formats
            result = pd.to_datetime(date_str, dayfirst=True, errors='coerce')
            if pd.notna(result):
                date_hits += 1
                continue
            # Try with monthfirst for US formats
            result = pd.to_datetime(date_str, dayfirst=False, errors='coerce')
            if pd.notna(result):
                date_hits += 1
                continue
            # Try with no format specified
            result = pd.to_datetime(date_str, errors='coerce')
            if pd.notna(result):
                date_hits += 1
        except Exception:
            pass
    if len(str_vals[:20]) > 0 and date_hits / max(len(str_vals[:20]), 1) >= 0.8:
        return None

    # ── quality score ──
    try:
        nums = [float(v) for v in str_vals]
        if all(0 <= n <= 100 for n in nums):
            # Quality scores are typically 0-100, often with decimal precision
            # Require at least some decimal values or specific patterns to distinguish from delay_days/units
            has_decimals = any(n != int(n) for n in nums)
            # Quality scores often cluster around higher values (70-100 range typical)
            has_high_values = any(n > 70 for n in nums)
            # Exclude if column name suggests quantity/units to avoid false positives
            quantity_like_terms = {'unit', 'qty', 'quantity', 'count', 'number', 'pieces', 'pcs', 'volume'}
            col_lower = col.lower()
            is_quantity_like = any(term in col_lower for term in quantity_like_terms)

            if (has_decimals or (has_high_values and len(set(nums)) > 1)) and not is_quantity_like:
                return "quality_score"
    except (ValueError, TypeError):
        pass

    # ── delay_days ──
    try:
        nums = [float(v) for v in str_vals]
        if all(-30 <= n <= 365 for n in nums) and all(n == int(n) for n in nums):
            if any(n >= 0 for n in nums):
                return "delay_days"
    except (ValueError, TypeError):
        pass

    # ── region / country ──
    # Check if values are typical region/country codes (2-3 uppercase letters)
    # Exclude if column name suggests product/sku to avoid false positives
    sku_like_terms = {'product', 'sku', 'item', 'part', 'material', 'code', 'id'}
    col_lower = col.lower()
    if not any(term in col_lower for term in sku_like_terms):
        if all(len(v) in (2, 3) and v.isupper() for v in str_vals[:10]):
            return "region"
        # Check if values are common geographic area names (but not company names)
        common_regions = {"North", "South", "East", "West", "Central", "Northeast", "Northwest", "Southeast", "Southwest",
                         "Europe", "Asia", "America", "Africa", "US", "UK", "EU", "APAC", "EMEA"}
        if all(v in common_regions or (len(v) <= 10 and v.isupper()) for v in str_vals[:10]):
            return "region"

    # ── cost ──
    try:
        cleaned_nums = []
        for v in str_vals:
            cleaned_val = _clean_currency_value(v)
            if cleaned_val is not None:
                cleaned_nums.append(cleaned_val)

        if cleaned_nums and all(n > 0 for n in cleaned_nums) and max(cleaned_nums) > 100:
            return "cost"
    except (ValueError, TypeError):
        pass

    return None


def auto_detect_columns(columns: List[str], sample_data: Optional[List[dict]] = None) -> Dict[str, Dict]:
    """Auto-detect column mapping using exact match, token overlap, and value inference."""
    result: Dict[str, Dict] = {}
    normalized: Dict[str, str] = {
        c.lower().strip().replace(" ", "_"): c for c in columns
    }
    used_columns: set = set()

    def _record(target: str, orig_col: str, confidence: float, method: str):
        result[target] = {
            "mapped_to": orig_col,
            "confidence": round(confidence, 2),
            "requires_confirmation": confidence < AUTO_ACCEPT_THRESHOLD,
            "inferred_by": method,
        }
        used_columns.add(orig_col)

    # Validate inputs
    if not columns:
        return result

    # Pass 1: exact match HIGH_CONFIDENCE (moved up to prioritize over value inference)
    for target, synonyms in HIGH_CONFIDENCE_SYNONYMS.items():
        if target in result:
            continue
        for syn in synonyms:
            norm_syn = syn.lower().strip().replace(" ", "_")
            if norm_syn in normalized and normalized[norm_syn] not in used_columns:
                _record(target, normalized[norm_syn], 1.0, "exact_high_confidence")
                break

    # Pass 2: exact match LOW_CONFIDENCE
    for target, synonyms in LOW_CONFIDENCE_SYNONYMS.items():
        if target in result:
            continue
        for syn in synonyms:
            norm_syn = syn.lower().strip().replace(" ", "_")
            if norm_syn in normalized and normalized[norm_syn] not in used_columns:
                _record(target, normalized[norm_syn], 0.5, "exact_low_confidence")
                break

    # Pass 3: token overlap
    for target, synonyms in HIGH_CONFIDENCE_SYNONYMS.items():
        if target in result:
            continue
        target_tokens = _tokenize(target) | {
            tok for syn in synonyms for tok in _tokenize(syn)
        }
        best_score = 0.0
        best_col: Optional[str] = None
        for norm_col, orig_col in normalized.items():
            if orig_col in used_columns:
                continue
            col_tokens = _tokenize(norm_col) | _tokenize(orig_col)
            overlap = len(target_tokens & col_tokens)
            if overlap > 0:
                score = overlap / max(len(col_tokens), 1)
                if score > best_score and score >= 0.4:
                    best_score = score
                    best_col = orig_col
        if best_col:
            _record(target, best_col, min(0.75, best_score), "token_overlap")

    # Pass 4: value-based inference (moved to last as fallback)
    if sample_data:
        for col in columns:
            if col in used_columns:
                continue
            samples = [row.get(col) for row in sample_data[:50]]
            inferred = _infer_field_from_values(col, samples)
            if inferred and inferred not in result:
                # Use higher confidence for distinctive fields that have stronger patterns
                confidence = 0.9 if inferred in ["delay_days", "region"] else 0.7
                _record(inferred, col, confidence, "value_inference")

    return result


def mapping_dict_from_detection(detection: Dict[str, Dict]) -> Dict[str, str]:
    """Flatten detection result to {internal_field: original_column} for ingestion."""
    return {k: v["mapped_to"] for k, v in detection.items()}


def low_confidence_fields(detection: Dict[str, Dict]) -> List[str]:
    """Return field names whose mapping requires user confirmation."""
    return [k for k, v in detection.items() if v.get("requires_confirmation")]
