"""
NEXUS — Upload Parser
=====================
Reads raw file bytes into Pandas DataFrames, enforcing size limits,
extension allowlists, encoding fallbacks, and row processing caps.
"""

import io
import logging

import pandas as pd  # type: ignore
from fastapi import HTTPException  # type: ignore

logger = logging.getLogger("nexus.upload.parser")

ALLOWED_EXTENSIONS = frozenset({"csv", "xlsx", "xls", "tsv"})


def parse_upload_file(contents: bytes, filename: str, max_bytes: int, max_preview_rows: int = None) -> pd.DataFrame:
    """
    Parse a CSV or Excel file into a Pandas DataFrame.
    Enforces extension allowlist, file size limits, and max rows to prevent memory DoS.
    """
    if not contents or len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File too large ({len(contents) / 1_048_576:.1f} MB). "
                f"Maximum allowed size is {max_bytes // 1_048_576} MB."
            ),
        )

    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '.{file_ext}'. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        )

    try:
        if file_ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(contents), engine="openpyxl", nrows=max_preview_rows)
        else:
            sep = "\t" if file_ext == "tsv" else ","
            # Try multiple encodings for robustness
            encodings = ["utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1", "cp1252", "iso-8859-1"]
            last_error = None
            df = None

            for encoding in encodings:
                try:
                    candidate = pd.read_csv(io.BytesIO(contents), encoding=encoding, sep=sep, nrows=max_preview_rows)
                    if any("\x00" in str(col) or "\ufffd" in str(col) for col in candidate.columns):
                        last_error = UnicodeDecodeError(encoding, contents, 0, 1, "decoded to invalid header")
                        continue
                    df = candidate
                    break
                except UnicodeDecodeError as e:
                    last_error = e
                    continue
                except Exception as e:
                    last_error = e
                    continue

            if df is None:
                # If all standard encodings fail, try with replacement
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding_errors="replace", sep=sep, nrows=max_preview_rows)
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to parse tabular file with standard encodings: {str(last_error or e)}",
                    )

        # Enforce max row cap on full uploads
        if max_preview_rows is None and df is not None:
            from app.core.config import settings
            max_rows = getattr(settings, "MAX_ANALYSIS_ROWS", 100000)
            if len(df) > max_rows:
                logger.warning("[UPLOAD] File '%s' has %d rows exceeding cap %d; capping at %d.", filename, len(df), max_rows, max_rows)
                df = df.iloc[:max_rows]

        return df

    except HTTPException:
        raise
    except Exception as e:
        logger.error("[UPLOAD] Parsing failed for '%s': %s", filename, e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
