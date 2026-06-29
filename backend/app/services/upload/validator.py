"""
NEXUS — Upload Validation & Sanitizers
======================================
Validates and sanitizes raw DataFrame values before DB insertion.
"""

import warnings
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from typing import Optional, Dict

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
        # Pattern: part after comma is exactly 2 digits (typical decimal precision)
        # AND part after dot has more than 2 digits (indicating it's a thousand separator)
        if len(parts_comma) == 2 and len(parts_comma[1]) <= 2:
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
        
        cleaned_val = _clean_currency_value(val)
        if cleaned_val is None:
            return default
        
        f = float(cleaned_val)
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
            cleaned_val = _clean_currency_value(v)
            if cleaned_val is None:
                return v is None or str(v).strip() in ("", "nan", "NaN")
            return cleaned_val >= -7
        except (ValueError, TypeError):
            return v is None or str(v).strip() in ("", "nan", "NaN")

    def _is_positive_number(v) -> bool:
        try:
            cleaned_val = _clean_currency_value(v)
            if cleaned_val is None:
                return v is None or str(v).strip() in ("", "nan", "NaN")
            return cleaned_val >= 0
        except (ValueError, TypeError):
            return v is None or str(v).strip() in ("", "nan", "NaN")

    def _is_parseable_date(v) -> bool:
        if v is None or str(v).strip() in ("", "nan", "NaT"):
            return True
        try:
            # Try multiple date parsing approaches to handle mixed formats
            date_str = str(v).strip()
            # Try with dayfirst for European formats
            result = pd.to_datetime(date_str, dayfirst=True, errors='coerce')
            if pd.notna(result):
                return True
            # Try with monthfirst for US formats
            result = pd.to_datetime(date_str, dayfirst=False, errors='coerce')
            if pd.notna(result):
                return True
            # Try with no format specified
            result = pd.to_datetime(date_str, errors='coerce')
            return pd.notna(result)
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
