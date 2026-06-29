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
            # Try multiple CSV parsing approaches for robustness
            encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252", "iso-8859-1"]
            last_error = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding=encoding, nrows=max_preview_rows)
                    if not df.empty:
                        return df
                except UnicodeDecodeError as e:
                    last_error = e
                    continue
                except Exception as e:
                    # If it's not a decoding error, try the next encoding
                    last_error = e
                    continue
            
            # If all encodings fail, try with error handling
            try:
                return pd.read_csv(io.BytesIO(contents), encoding_errors="replace", nrows=max_preview_rows)
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to parse CSV file with all encodings. Last error: {str(last_error or e)}"
                )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
