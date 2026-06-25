"""
NEXUS — Upload Schema Detection
===============================
Handles auto-detecting column mappings using exact match, token overlap,
and value-based inference (for ERP codes).
"""

import re
import pandas as pd  # type: ignore
from typing import Optional, List, Dict

# Maps internal field name → list of HIGH-confidence column name synonyms
HIGH_CONFIDENCE_SYNONYMS: Dict[str, List[str]] = {
    "supplier": [
        "supplier", "vendor", "supplier_name", "vendor_name", "manufacturer",
        "ven_no", "vendor_id", "supplier_code", "sup_name", "sup_id", "supp",
    ],
    "sku": [
        "sku", "sku_id", "product_id", "item_id", "part_number", "product_code",
        "item_code", "material", "material_id", "part_no", "pn",
    ],
    "delay_days": [
        "delay_days", "days_late", "lead_time_variance", "late_days",
        "shipment_delay", "delay_d", "days_delayed", "lt_variance",
    ],
    "cost": [
        "cost", "unit_cost", "total_cost", "inv_amount", "invoice_amount",
        "unit_price", "total_amount", "spend",
    ],
    "warehouse": [
        "warehouse", "warehouse_name", "distribution_center", "dc",
        "facility", "wh", "depot", "plant", "warehouse_id", "wh_name",
    ],
    "region": [
        "region", "origin_region", "supplier_region", "source_region",
        "dest_country", "origin",
    ],
    "shipment_id": [
        "shipment_id", "shipment", "order_id", "order_number", "tracking",
        "po_number", "po", "purchase_order", "invoice_no", "ref_no", "reference",
    ],
    "order_date": [
        "order_date", "order_dt", "purchase_date", "po_date",
        "order_created", "ordered_on", "order_date_(dateorders)",
    ],
    "delivery_date": [
        "delivery_date", "delivery_dt", "received_date", "arrival_date",
        "delivered_on", "recv_date", "eta", "actual_delivery",
        "shipping_date_(dateorders)", "shipping_date",
    ],
    "quantity": [
        "quantity", "qty", "units", "qty_ordered", "qty_shipped",
        "num_units", "pieces", "pcs",
    ],
    "category": [
        "category", "product_category", "product_group", "prod_cat",
        "item_type", "segment", "classification",
    ],
    "quality_score": [
        "quality_score", "quality_rating", "qc_score", "inspection_score",
    ],
}

# Maps internal field name → list of LOW-confidence synonyms (require user confirmation)
LOW_CONFIDENCE_SYNONYMS: Dict[str, List[str]] = {
    "supplier": ["source", "mfr", "mfg"],
    "sku": ["product", "item", "product_name"],
    "delay_days": ["delay", "lead_time"],
    "cost": ["price", "amount", "value", "order_item_total"],
    "warehouse": ["storage", "location_code"],
    "region": ["location", "area", "zone", "territory", "country", "city",
                "geo", "geography", "market", "order_country", "customer_country"],
    "shipment_id": ["id", "record_id"],
    "order_date": ["created_date", "date"],
    "delivery_date": ["ship_date"],
    "quantity": ["volume", "count"],
    "category": ["type", "group"],
    "quality_score": ["quality", "rating", "grade", "score", "performance"],
}

AUTO_ACCEPT_THRESHOLD = 0.8


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
            pd.to_datetime(v)
            date_hits += 1
        except Exception:
            pass
    if date_hits / max(len(str_vals[:20]), 1) >= 0.8:
        return None

    # ── quality score ──
    try:
        nums = [float(v) for v in str_vals]
        if all(0 <= n <= 100 for n in nums) and any(n != int(n) for n in nums):
            return "quality_score"
    except (ValueError, TypeError):
        pass

    # ── delay_days ──
    try:
        nums = [float(v) for v in str_vals]
        if all(-7 <= n <= 120 for n in nums) and all(n == int(n) for n in nums):
            if any(n > 0 for n in nums):
                return "delay_days"
    except (ValueError, TypeError):
        pass

    # ── region / country ──
    if all(len(v) in (2, 3) and v.isupper() for v in str_vals[:10]):
        return "region"

    # ── cost ──
    try:
        nums = [float(v.replace(",", "").replace("$", "").replace("€", "").replace("£", "").strip())
                for v in str_vals]
        if all(n > 0 for n in nums) and max(nums) > 100:
            return None
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

    # Pass 0: value-based inference
    if sample_data:
        for col in columns:
            if col in used_columns:
                continue
            samples = [row.get(col) for row in sample_data[:50]]
            inferred = _infer_field_from_values(col, samples)
            if inferred and inferred not in result:
                _record(inferred, col, 0.7, "value_inference")

    # Pass 1: exact match HIGH_CONFIDENCE
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

    return result


def mapping_dict_from_detection(detection: Dict[str, Dict]) -> Dict[str, str]:
    """Flatten detection result to {internal_field: original_column} for ingestion."""
    return {k: v["mapped_to"] for k, v in detection.items()}


def low_confidence_fields(detection: Dict[str, Dict]) -> List[str]:
    """Return field names whose mapping requires user confirmation."""
    return [k for k, v in detection.items() if v.get("requires_confirmation")]
