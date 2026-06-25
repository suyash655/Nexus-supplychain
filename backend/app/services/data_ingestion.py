import io
import json
import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.supply import SupplyData, UploadHistory
from app.utils.sanitizers import _safe_str, _safe_int, _safe_float

COLUMN_SYNONYMS = {
    "supplier": ["supplier", "vendor", "supplier_name", "vendor_name", "manufacturer", "source", "ven_no", "vendor_id", "supplier_code", "sup_name", "sup_id", "supp", "Category Name"],
    "sku": ["sku", "product", "item", "product_id", "item_id", "part_number", "product_code", "item_code", "material", "material_id", "part_no", "pn", "Product Name", "Product Card Id"],
    "delay_days": ["delay_days", "delay", "days_late", "lead_time_variance", "late_days", "shipment_delay", "delay_d", "days_delayed", "lt_variance"],
    "cost": ["cost", "price", "amount", "value", "total_cost", "unit_price", "total_amount", "unit_cost", "inv_amount", "invoice_amount", "spend", "Order Item Total", "Product Price"],
    "warehouse": ["warehouse", "warehouse_name", "distribution_center", "dc", "facility", "storage", "wh", "depot", "plant", "warehouse_id", "wh_name"],
    "region": ["region", "location", "area", "zone", "territory", "country", "city", "geo", "geography", "market", "dest_country", "origin", "Order Region", "Order Country", "Customer Country"],
    "shipment_id": ["shipment_id", "shipment", "order_id", "order_number", "tracking", "po_number", "po", "purchase_order", "invoice_no", "ref_no", "reference"],
    "order_date": ["order_date", "order_dt", "purchase_date", "created_date", "po_date", "order_created", "ordered_on", "order_date_(dateorders)"],
    "delivery_date": ["delivery_date", "delivery_dt", "received_date", "arrival_date", "ship_date", "delivered_on", "recv_date", "eta", "actual_delivery", "shipping_date_(dateorders)", "shipping_date"],
    "quantity": ["quantity", "qty", "units", "volume", "count", "pieces", "pcs", "qty_ordered", "qty_shipped", "num_units", "Order Item Quantity"],
    "category": ["category", "product_category", "type", "segment", "classification", "group", "product_group", "prod_cat", "item_type"],
    "quality_score": ["quality_score", "quality", "rating", "grade", "score", "performance", "quality_rating", "qc_score", "inspection_score"],
}

def auto_detect_columns(columns: List[str]) -> Dict[str, str]:
    import re
    from difflib import get_close_matches
    detected: Dict[str, str] = {}
    normalized: Dict[str, str] = {c.lower().strip().replace(" ", "_"): c for c in columns}
    used_columns: set = set()
    for target_col, synonyms in COLUMN_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in normalized and normalized[synonym] not in used_columns:
                detected[target_col] = normalized[synonym]
                used_columns.add(normalized[synonym])
                break
    def _tokenize(s: str) -> set:
        parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', s)
        tokens = set(re.split(r'[_\s\-\.]+', parts.lower()))
        return {t for t in tokens if len(t) > 1}
    for target_col, synonyms in COLUMN_SYNONYMS.items():
        if target_col in detected:
            continue
        target_tokens = _tokenize(target_col) | set(synonyms)
        best_score = 0.0
        best_col = None
        for norm_col, orig_col in normalized.items():
            if orig_col in used_columns:
                continue
            col_tokens = _tokenize(norm_col) | _tokenize(orig_col)
            overlap = len(target_tokens & col_tokens)
            if overlap > 0:
                score = overlap / max(len(col_tokens), 1)
                if score > best_score and score >= 0.3:
                    best_score = score
                    best_col = orig_col
        if best_col:
            detected[target_col] = best_col
            used_columns.add(best_col)
    all_synonyms_flat = []
    for target_col, synonyms in COLUMN_SYNONYMS.items():
        if target_col not in detected:
            all_synonyms_flat.extend([(syn, target_col) for syn in synonyms])
    for norm_col, orig_col in normalized.items():
        if orig_col in used_columns:
            continue
        close = get_close_matches(norm_col, [s[0] for s in all_synonyms_flat], n=1, cutoff=0.7)
        if close:
            matched_synonym = close[0]
            for syn, target_col in all_synonyms_flat:
                if syn == matched_synonym and target_col not in detected:
                    detected[target_col] = orig_col
                    used_columns.add(orig_col)
                    break
    return detected

def ingest_dataframe(df: pd.DataFrame, filename: str, file_type: str, mapping_dict: dict, db: Session) -> dict:
    inserted = 0
    rejected = 0
    batch_size = 1000
    records_to_insert = []
    m = dict(mapping_dict)
    
    for row in df.to_dict('records'):
        try:
            record = SupplyData(
                supplier=_safe_str(row.get(m.get('supplier'))) or "Unknown Source",
                sku=_safe_str(row.get(m.get('sku'))) or "N/A",
                warehouse=_safe_str(row.get(m.get('warehouse'))),
                region=_safe_str(row.get(m.get('region'))),
                shipment_id=_safe_str(row.get(m.get('shipment_id'))),
                order_date=_safe_str(row.get(m.get('order_date'))),
                delivery_date=_safe_str(row.get(m.get('delivery_date'))),
                delay_days=_safe_int(row.get(m.get('delay_days')), 0),
                cost=_safe_float(row.get(m.get('cost')), 0.0),
                quantity=_safe_int(row.get(m.get('quantity')), 0),
                category=_safe_str(row.get(m.get('category'))),
                quality_score=_safe_float(row.get(m.get('quality_score')), None),
            )
            records_to_insert.append(record)
            if len(records_to_insert) >= batch_size:
                db.add_all(records_to_insert)
                db.commit()
                inserted += len(records_to_insert)
                records_to_insert = []
        except Exception as e:
            rejected += 1
            db.rollback()

    if records_to_insert:
        try:
            db.add_all(records_to_insert)
            db.commit()
            inserted += len(records_to_insert)
        except Exception:
            db.rollback()
            for r in records_to_insert:
                try:
                    db.add(r)
                    db.commit()
                    inserted += 1
                except Exception:
                    db.rollback()
                    rejected += 1

    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "detected_columns": list(df.columns),
        "mapped_columns": mapping_dict,
        "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
    }

    try:
        history = UploadHistory(
            filename=filename,
            file_type=file_type,
            rows_total=len(df),
            rows_inserted=inserted,
            rows_rejected=rejected,
            columns_detected=list(df.columns),
            column_mapping=mapping_dict,
            data_quality_report=quality_report,
        )
        db.add(history)
        db.commit()
    except Exception as e:
        db.rollback()

    return {
        "status": "success",
        "rows_inserted": inserted,
        "rows_rejected": rejected,
        "column_mapping": mapping_dict,
        "data_quality": quality_report,
    }
