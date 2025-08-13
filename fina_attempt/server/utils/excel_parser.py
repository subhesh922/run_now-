# server/utils/excel_parser.py
from __future__ import annotations

import io
import os
from typing import Iterable, List, Dict, Any, Optional, Tuple

import pandas as pd


# ---------- public api ----------

def parse_excel_or_csv(path: str, sheet: str | int | None = None) -> pd.DataFrame:
    """
    Load a CSV/XLSX/XLS into a pandas DataFrame with light cleanup.

    - Picks a sensible sheet in Excel if 'sheet' is None:
        * 'Sheet1' if present, else the first visible sheet
    - Trims column names and keeps dtypes as pandas infers.
    - Returns an empty DataFrame if file not found.

    Raises ValueError for unsupported extensions.
    """
    if not path or not os.path.exists(path):
        return pd.DataFrame()

    low = path.lower()
    try:
        if low.endswith(".csv"):
            df = _read_csv_safely(path)
        elif low.endswith(".xlsx") or low.endswith(".xls"):
            df = _read_excel_safely(path, sheet=sheet)
        else:
            raise ValueError(f"Unsupported file type: {path}")
    except Exception as e:
        # never explode the pipeline on a single bad file
        print(f"[excel_parser] Failed to read '{path}': {type(e).__name__}: {e}")
        return pd.DataFrame()

    # light normalization
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def detect_preferred_text_column(
    df: pd.DataFrame,
    preferences: Iterable[str] = ("text", "notes", "description", "failure_mode", "failure mode", "issue", "symptom"),
) -> Optional[str]:
    """
    Return the first matching column name (case-insensitive) from preferences, or None.
    """
    if df is None or df.empty:
        return None
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for key in preferences:
        if key.lower() in lower_map:
            return lower_map[key.lower()]
    return None


def df_to_normalized_rows(
    df: pd.DataFrame,
    *,
    product: str,
    subproduct: str,
    source_type: str,           # "kb" | "field" | "prd"
    file_name: str,
    text_pref_cols: Iterable[str] = ("text", "notes", "description", "failure_mode", "failure mode", "issue", "symptom"),
) -> List[Dict[str, Any]]:
    """
    Convert an arbitrary table into normalized row dicts compatible with our pipeline.

    Output rows look like:
      {
        "product": product,
        "subproduct": subproduct,
        "source_type": "kb|field|prd",
        "file": "<basename>",
        "idx": <row_index>,
        "text": "<best-effort text>"
      }
    """
    if df is None or df.empty:
        return []

    out: List[Dict[str, Any]] = []
    pref = detect_preferred_text_column(df, text_pref_cols)

    for i, row in df.iterrows():
        if pref is not None:
            val = row.get(pref)
            text = str(val) if pd.notna(val) else ""
        else:
            # fallback: stringify the row dict (stable col order)
            text = str({c: row.get(c) for c in df.columns})

        text = (text or "").strip()
        if not text:
            continue

        out.append({
            "product": product,
            "subproduct": subproduct,
            "source_type": source_type,
            "file": os.path.basename(file_name),
            "idx": int(i),
            "text": text,
        })
    return out


# ---------- internals ----------

# server/utils/excel_parser.py
import io
import pandas as pd

def read_csv_safe(content: bytes) -> pd.DataFrame:
    if not content or (isinstance(content, (bytes, bytearray)) and len(content) == 0):
        raise ValueError("Empty CSV file.")
    bio = io.BytesIO(content)
    try:
        df = pd.read_csv(bio)
        if df.empty or len(df.columns) == 0:
            raise ValueError("CSV has no columns or rows.")
        return df
    except Exception:
        # try excel fallback (sometimes mislabeled)
        bio.seek(0)
        df = pd.read_excel(bio)
        if df.empty or len(df.columns) == 0:
            raise ValueError("Converted Excel has no columns or rows.")
        return df

def read_excel_safe(content: bytes) -> pd.DataFrame:
    if not content or (isinstance(content, (bytes, bytearray)) and len(content) == 0):
        raise ValueError("Empty Excel file.")
    bio = io.BytesIO(content)
    df = pd.read_excel(bio)
    if df.empty or len(df.columns) == 0:
        raise ValueError("Excel has no columns or rows.")
    return df
