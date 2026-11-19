"""Shared supply-chain metric definitions."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

ON_TIME_DELAY_TOLERANCE_DAYS = 1

CORE_COMPLETENESS_COLUMNS = (
    "supplier",
    "sku",
    "warehouse",
    "region",
    "shipment_id",
    "order_date",
    "delivery_date",
    "delay_days",
    "cost",
    "quantity",
)


def on_time_mask(delays: pd.Series, tolerance_days: int = ON_TIME_DELAY_TOLERANCE_DAYS) -> pd.Series:
    """Return True for shipments within the agreed delivery tolerance."""
    numeric_delays = pd.to_numeric(delays, errors="coerce")
    return numeric_delays.notna() & (numeric_delays <= tolerance_days)


def completeness_score(
    df: pd.DataFrame,
    required_columns: Iterable[str] = CORE_COMPLETENESS_COLUMNS,
) -> float:
    """Column-aware completeness over required columns only, returned 0.0-1.0."""
    if df.empty:
        return 0.0

    columns = [col for col in required_columns if col in df.columns]
    if not columns:
        return 0.0

    required = df[columns]
    total_cells = required.shape[0] * required.shape[1]
    if total_cells == 0:
        return 0.0

    present_cells = int(required.notna().sum().sum())
    return float(present_cells / total_cells)


def completeness_detail(
    df: pd.DataFrame,
    required_columns: Iterable[str] = CORE_COMPLETENESS_COLUMNS,
) -> dict[str, float]:
    """Per-required-column completeness, returned as 0.0-1.0 scores."""
    return {
        col: round(float(df[col].notna().mean()), 4)
        for col in required_columns
        if col in df.columns and len(df) > 0
    }
