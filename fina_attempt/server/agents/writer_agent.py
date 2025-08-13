# server/agents/writer_agent.py
from __future__ import annotations

import io
from typing import Any, Dict, List, Tuple

import pandas as pd


DFMEA_COLUMNS = [
    "ID",
    "Function",
    "Failure Mode",
    "Effects",
    "Causes",
    "Prevention Controls",
    "Detection Controls",
    "Severity",
    "Occurrence",
    "Detection",
    "RPN",
    "Recommendations",
    "Owner",
    "Target Date",
]

EVIDENCE_COLUMNS = [
    "ID",
    "Source Type",
    "File",
    "Idx",
    "Snippet",
    "CitationID",
]

# --- key mapping helpers (tolerant to different casings/styles) ---

_KEY_MAP = {
    "id": "ID",
    "item": "ID",
    "function": "Function",
    "Function": "Function",

    "failure_mode": "Failure Mode",
    "FailureMode": "Failure Mode",
    "Failure Mode": "Failure Mode",

    "effects": "Effects",
    "Effects": "Effects",

    "causes": "Causes",
    "Causes": "Causes",

    "current_controls_prevention": "Prevention Controls",
    "prevention_controls": "Prevention Controls",
    "Prev Controls": "Prevention Controls",
    "current_controls_detection": "Detection Controls",
    "detection_controls": "Detection Controls",
    "Det Controls": "Detection Controls",

    "severity": "Severity",
    "Severity": "Severity",
    "occurrence": "Occurrence",
    "Occurrence": "Occurrence",
    "detection": "Detection",
    "Detection": "Detection",
    "rpn": "RPN",
    "RPN": "RPN",

    "recommendations": "Recommendations",
    "Recommendations": "Recommendations",
    "responsible_owner": "Owner",
    "owner": "Owner",
    "Owner": "Owner",
    "target_date": "Target Date",
    "Target Date": "Target Date",
}

_LISTY = {"Effects", "Causes", "Prevention Controls", "Detection Controls", "Recommendations"}


def _to_list_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, list):
        return "; ".join(str(x) for x in v if x is not None and str(x).strip())
    return str(v)


def _coerce_int(v: Any, default: int = 1) -> int:
    try:
        i = int(v)
        return max(1, min(10, i))
    except Exception:
        return default


def _normalize_entry(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Map a raw DFMEA dict (LLM or rule-based) into normalized DFMEA row + evidence rows.

    Supports two evidence styles:
      1) 'evidence': [{source_type,file,idx,snippet,...}, ...]
      2) 'citations': ["kb_id_1", "kb_id_2", ...]   # legacy simple ids
    """
    # 1) remap keys
    norm: Dict[str, Any] = {k: raw.get(k) for k in raw}
    out: Dict[str, Any] = {c: "" for c in DFMEA_COLUMNS}

    for k, v in list(norm.items()):
        tgt = _KEY_MAP.get(k, None)
        if tgt:
            out[tgt] = v

    # 2) list-like fields to strings
    for k in _LISTY:
        out[k] = _to_list_str(out.get(k, ""))

    # 3) numeric ranks and RPN
    sev = _coerce_int(out.get("Severity", 1))
    occ = _coerce_int(out.get("Occurrence", 1))
    det = _coerce_int(out.get("Detection", 1))
    out["Severity"], out["Occurrence"], out["Detection"] = sev, occ, det
    try:
        out["RPN"] = int(out.get("RPN") or sev * occ * det)
    except Exception:
        out["RPN"] = sev * occ * det

    # Ensure ID exists
    if not str(out.get("ID", "")).strip():
        out["ID"] = raw.get("ID") or raw.get("item") or raw.get("id") or ""

    # 4) evidence/citations extraction
    ev_rows: List[Dict[str, Any]] = []

    # new style: evidence list of dicts
    evidence = raw.get("evidence") or []
    if isinstance(evidence, list) and evidence:
        for ev in evidence:
            if not isinstance(ev, dict):
                continue
            ev_rows.append({
                "ID": out.get("ID", ""),
                "Source Type": ev.get("source_type", ""),
                "File": ev.get("file", ""),
                "Idx": ev.get("idx", ""),
                "Snippet": (ev.get("snippet") or "")[:900],
                "CitationID": ev.get("kb_id") or ev.get("uuid") or "",
            })

    # legacy: citations = list of kb_ids
    citations = raw.get("citations") or []
    if isinstance(citations, list) and citations:
        for cid in citations:
            ev_rows.append({
                "ID": out.get("ID", ""),
                "Source Type": "",
                "File": "",
                "Idx": "",
                "Snippet": "",
                "CitationID": str(cid),
            })

    return out, ev_rows


class WriterAgent:
    """
    Turns DFMEA entries (list[dict]) into an Excel workbook:
      - DFMEA          (normalized rows)
      - Evidence       (flattened evidence/citations)
      - Summary        (Top-10 by RPN)

    Use:
        writer = WriterAgent()
        xlsx_bytes = writer.to_excel_bytes(entries, meta={"product":"Quasar","subproduct":"Display"})
        # write to disk if needed:
        with open("DFMEA_Quasar_Display.xlsx","wb") as f:
            f.write(xlsx_bytes)
    """

    def to_excel_bytes(self, entries: List[Dict[str, Any]], meta: Dict[str, Any] | None = None) -> bytes:
        rows: List[Dict[str, Any]] = []
        ev_rows: List[Dict[str, Any]] = []

        for r in entries or []:
            nr, er = _normalize_entry(r)
            rows.append(nr)
            ev_rows.extend(er)

        df_dfmea = pd.DataFrame(rows, columns=DFMEA_COLUMNS)
        df_evidence = pd.DataFrame(ev_rows, columns=EVIDENCE_COLUMNS)

        # Enrich with meta columns (visible and helpful)
        if meta:
            for k, v in meta.items():
                col = str(k).strip().title()
                df_dfmea.insert(0, col, v)
                if not df_evidence.empty:
                    df_evidence.insert(0, col, v)

        # Summary sheet: top-10 by RPN
        if not df_dfmea.empty:
            df_summary = df_dfmea.sort_values(by="RPN", ascending=False).head(10).reset_index(drop=True)
        else:
            df_summary = pd.DataFrame(columns=df_dfmea.columns)

        # Build Excel in-memory
        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df_dfmea.to_excel(writer, index=False, sheet_name="DFMEA")
            df_evidence.to_excel(writer, index=False, sheet_name="Evidence")
            df_summary.to_excel(writer, index=False, sheet_name="Summary")

            # basic formatting
            wb = writer.book
            for sheet in ("DFMEA", "Evidence", "Summary"):
                ws = writer.sheets.get(sheet)
                if not ws:
                    continue
                ws.freeze_panes(1, 1)

                # auto width (rough)
                df = df_dfmea if sheet == "DFMEA" else (df_evidence if sheet == "Evidence" else df_summary)
                for i, col in enumerate(df.columns):
                    width = min(60, max(12, int(df[col].astype(str).map(len).max() if not df.empty else 12)))
                    ws.set_column(i, i, width)

        bio.seek(0)
        return bio.read()
