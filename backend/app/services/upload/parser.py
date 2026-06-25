"""
NEXUS — Upload Parser
=====================
Reads raw file bytes into Pandas DataFrames, handling size limits and encoding.
"""

import io
import pandas as pd  # type: ignore
from fastapi import HTTPException  # type: ignore


def parse_upload_file(contents: bytes, filename: str, max_bytes: int, max_preview_rows: int = None) -> pd.DataFrame:
    """
    Parse a CSV or Excel file into a Pandas DataFrame.
    Enforces maximum file size to prevent memory DoS.
    """
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File too large ({len(contents) / 1_048_576:.1f} MB). "
                f"Maximum allowed size is {max_bytes // 1_048_576} MB."
            ),
        )

    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if file_ext in ("xlsx", "xls"):
            return pd.read_excel(io.BytesIO(contents), engine="openpyxl", nrows=max_preview_rows)
        else:
            try:
                return pd.read_csv(io.BytesIO(contents), encoding="utf-8-sig", nrows=max_preview_rows)
            except UnicodeDecodeError:
                return pd.read_csv(io.BytesIO(contents), encoding="latin-1", nrows=max_preview_rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
