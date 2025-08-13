# server/utils/parsers.py
from __future__ import annotations

import os
from typing import List, Dict, Any, Iterable, Optional

import pandas as pd

from server.utils.excel_parser import (
    parse_excel_or_csv,
    df_to_normalized_rows,
)
from server.utils.docx_parser import parse_docx_to_rows


# --------- Public API ----------

def load_kb_files(
    paths: Iterable[str],
    *,
    product: str,
    subproduct: str,
    text_pref_cols: Iterable[str] = ("text", "notes", "description", "failure_mode", "failure mode"),
) -> List[Dict[str, Any]]:
    """Load Knowledge Bank CSV/XLSX files and normalize to row dicts."""
    out: List[Dict[str, Any]] = []
    for p in paths or []:
        if not (p and os.path.exists(p)):
            continue
        df = parse_excel_or_csv(p)
        rows = df_to_normalized_rows(
            df,
            product=product,
            subproduct=subproduct,
            source_type="kb",
            file_name=os.path.basename(p),
            text_pref_cols=text_pref_cols,
        )
        out.extend(rows)
    return out


def load_field_files(
    paths: Iterable[str],
    *,
    product: str,
    subproduct: str,
    text_pref_cols: Iterable[str] = ("issue", "description", "symptom", "failure", "problem", "observations"),
) -> List[Dict[str, Any]]:
    """Load Field Reported Issues CSV/XLSX files and normalize to row dicts."""
    out: List[Dict[str, Any]] = []
    for p in paths or []:
        if not (p and os.path.exists(p)):
            continue
        df = parse_excel_or_csv(p)
        rows = df_to_normalized_rows(
            df,
            product=product,
            subproduct=subproduct,
            source_type="field",
            file_name=os.path.basename(p),
            text_pref_cols=text_pref_cols,
        )
        out.extend(rows)
    return out


def load_prd_files(
    paths: Iterable[str],
    *,
    product: str,
    subproduct: str,
    include_tables: bool = True,
) -> List[Dict[str, Any]]:
    """
    Load PRD/spec files and normalize to row dicts.
    Supports:
      - DOCX/DOC: paragraphs + table cells (via python-docx)
      - CSV/XLSX/XLS: rows → best-effort text (treated as PRD source)
    """
    out: List[Dict[str, Any]] = []
    for p in paths or []:
        if not (p and os.path.exists(p)):
            continue
        low = p.lower()
        base = os.path.basename(p)

        if low.endswith((".docx", ".doc")):
            rows = parse_docx_to_rows(
                p,
                product=product,
                subproduct=subproduct,
                file_label=base,
                include_tables=include_tables,
            )
        elif low.endswith((".csv", ".xlsx", ".xls")):
            df = parse_excel_or_csv(p)
            # Prefer requirement-ish columns for PRDs; fall back to full row stringify
            rows = df_to_normalized_rows(
                df,
                product=product,
                subproduct=subproduct,
                source_type="prd",              # IMPORTANT: classify as PRD
                file_name=base,
                text_pref_cols=("requirement", "req", "id", "title", "text", "description", "notes"),
            )
        else:
            rows = []

        out.extend(rows)
    return out


def load_all_sources(
    *,
    product: str,
    subproduct: str,
    kb_paths: Optional[Iterable[str]] = None,
    field_paths: Optional[Iterable[str]] = None,
    prd_paths: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience: load KB + Field + PRD, return a single normalized list.
    Order preserved: Field first (bias retrieval), then PRD, then KB.
    """
    kb_paths = list(kb_paths or [])
    field_paths = list(field_paths or [])
    prd_paths = list(prd_paths or [])

    field_rows = load_field_files(field_paths, product=product, subproduct=subproduct)
    prd_rows = load_prd_files(prd_paths, product=product, subproduct=subproduct)
    kb_rows = load_kb_files(kb_paths, product=product, subproduct=subproduct)

    combined: List[Dict[str, Any]] = []
    combined.extend(field_rows)
    combined.extend(prd_rows)
    combined.extend(kb_rows)

    # strip empties
    combined = [r for r in combined if (r.get("text") or "").strip()]
    return combined
