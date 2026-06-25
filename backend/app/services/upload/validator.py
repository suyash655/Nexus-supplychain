"""
NEXUS — Upload Validation & Sanitizers
======================================
Validates and sanitizes raw DataFrame values before DB insertion.
"""

import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from typing import Optional, Dict


def safe_str(val) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    s = str(val).strip()
    if s.lower() in ("nan", "none", "nat", ""):
        return None
    return s


def safe_int(val, default=0) -> int:
    try:
        if val is None:
            return default
        if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
            return default
        return int(float(val))
    except (ValueError, TypeError):
        return default


def safe_float(val, default=0.0) -> float:
    try:
        if val is None:
            return default
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def validate_mapped_values(df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Dict]:
    """
    Post-mapping value validation. Returns a per-field report of valid/invalid counts.
    """
    report: Dict[str, Dict] = {}

    def _check(field: str, check_fn, reason: str):
        col = mapping.get(field)
        if not col or col not in df.columns:
            return
        series = df[col]
        invalid_mask = series.apply(lambda v: not check_fn(v))
        invalid_count = int(invalid_mask.sum())
        report[field] = {
            "valid": len(series) - invalid_count,
            "invalid": invalid_count,
            "invalid_reason": reason if invalid_count > 0 else None,
            "invalid_row_indices": df.index[invalid_mask].tolist()[:10],
        }

    def _is_non_negative_number(v) -> bool:
        try:
            return float(str(v).replace(",", "").replace("$", "").strip()) >= -7
        except (ValueError, TypeError):
            return v is None or str(v).strip() in ("", "nan", "NaN")

    def _is_positive_number(v) -> bool:
        try:
            f = float(str(v).replace(",", "").replace("$", "").strip())
            return f >= 0
        except (ValueError, TypeError):
            return v is None or str(v).strip() in ("", "nan", "NaN")

    def _is_parseable_date(v) -> bool:
        if v is None or str(v).strip() in ("", "nan", "NaT"):
            return True
        try:
            pd.to_datetime(str(v))
            return True
        except Exception:
            return False

    def _is_valid_quality_score(v) -> bool:
        try:
            f = float(v)
            return 0 <= f <= 100
        except (ValueError, TypeError):
            return v is None or str(v).strip() in ("", "nan", "NaN")

    _check("delay_days", _is_non_negative_number, "negative delay_days values")
    _check("cost", _is_positive_number, "negative or non-numeric cost values")
    _check("order_date", _is_parseable_date, "unparseable date strings")
    _check("delivery_date", _is_parseable_date, "unparseable date strings")
    _check("quality_score", _is_valid_quality_score, "quality_score outside [0, 100]")

    return report
