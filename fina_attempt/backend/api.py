# # backend/api.py
# import base64
# import io
# import json
# import os
# from typing import List, Optional, Tuple

# from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Header
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# # --- Pipeline & utils ---
# from server.pipeline.dfmea_pipeline import DFMEAPipeline
# from server.utils.parsers import (
#     parse_docx_to_rows,        # expects bytes/BytesIO ok in our wrapper below
#     load_all_sources,          # if you already have a central loader, keep it
# )
# from server.utils.excel_parser import read_csv_safe, read_excel_safe  # (see file below)

# # ---------------- FastAPI app ----------------
# app = FastAPI(title="DFMEA Backend", version="1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # lock this down for prod
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------- Models ----------------
# class DFMEAResponse(BaseModel):
#     product: str
#     subproduct: str
#     entries: list
#     counts: dict = {}
#     excel_base64: Optional[str] = None

# # ---------------- Helpers ----------------
# def _is_legacy_doc(filename: str) -> bool:
#     name = (filename or "").lower()
#     return name.endswith(".doc") and not name.endswith(".docx")

# def _split_by_type(files: List[UploadFile]) -> Tuple[list, list, list, list]:
#     """
#     Split a mixed list of UploadFile into (docx_list, csv_list, xlsx_list, legacy_doc_list).
#     Returns lists of tuples: [(filename, bytes), ...]
#     """
#     docx, csvs, xlsxs, legacy = [], [], [], []
#     for uf in files or []:
#         fname = uf.filename or ""
#         if _is_legacy_doc(fname):
#             legacy.append(fname)
#             continue
#         data = uf.file.read() if hasattr(uf, "file") else None
#         if data is None or data == b"":
#             # try await uf.read() path if running in async context
#             try:
#                 data = uf.file.read()
#             except Exception:
#                 pass
#         if data is None:
#             try:
#                 data = uf.read()
#             except Exception:
#                 data = b""
#         name = fname.lower()
#         if name.endswith(".docx"):
#             docx.append((fname, data))
#         elif name.endswith(".csv"):
#             csvs.append((fname, data))
#         elif name.endswith(".xlsx"):
#             xlsxs.append((fname, data))
#         else:
#             # unknown types: ignore; DFMEA works off docx/csv/xlsx only
#             pass
#     return docx, csvs, xlsxs, legacy

# def _rows_from_docx_bytes(items: List[Tuple[str, bytes]]) -> list:
#     """
#     Convert a list of (filename, bytes) .docx into list[dict] rows with ['source','text'] at minimum.
#     Uses parse_docx_to_rows from your utils (which accepts path or bytes; we wrap to BytesIO).
#     """
#     rows = []
#     for fname, blob in items:
#         if not blob:
#             continue
#         bio = io.BytesIO(blob)
#         r = parse_docx_to_rows(bio, source_name=fname)  # your parser should handle a BytesIO
#         rows.extend(r or [])
#     return rows

# def _rows_from_table_files(csvs: List[Tuple[str, bytes]], xlsxs: List[Tuple[str, bytes]]) -> list:
#     """
#     Load CSV/XLSX tables into list[dict] rows. Keep original filename in 'source'.
#     """
#     rows = []
#     # CSVs
#     for fname, blob in csvs:
#         df = read_csv_safe(blob)
#         df["__source__"] = fname
#         rows.extend(df.to_dict(orient="records"))
#     # XLSXs
#     for fname, blob in xlsxs:
#         df = read_excel_safe(blob)
#         df["__source__"] = fname
#         rows.extend(df.to_dict(orient="records"))
#     return rows

# def _make_excel_download_bytes(entries: list) -> Optional[bytes]:
#     """
#     If your pipeline already returns an Excel, you can pass it through.
#     Otherwise, create a minimal Excel from entries here.
#     """
#     try:
#         import pandas as pd
#     except Exception:
#         return None
#     if not entries:
#         return None
#     try:
#         df = pd.DataFrame(entries)
#         bio = io.BytesIO()
#         with pd.ExcelWriter(bio, engine="openpyxl") as xw:
#             df.to_excel(xw, index=False, sheet_name="DFMEA")
#         return bio.getvalue()
#     except Exception:
#         return None

# # ---------------- Routes ----------------
# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/dfmea/generate", response_model=DFMEAResponse)
# def generate_dfmea(
#     # text fields
#     product: str = Form(...),
#     subproduct: str = Form(...),
#     subproducts: Optional[str] = Form(None),   # JSON array string (for multi support)
#     focus: Optional[str] = Form(None),

#     # files (multiple per field)
#     prds: List[UploadFile] = File(default_factory=list),
#     knowledge_base: List[UploadFile] = File(default_factory=list),
#     field_issues: List[UploadFile] = File(default_factory=list),

#     # admin header (optional)
#     x_admin_auth: Optional[str] = Header(default=None, alias="X-Admin-Auth"),
# ):
#     # ---- security: optional admin prompt gate
#     if focus and not x_admin_auth:
#         # You can relax this if you prefer, but this keeps focus prompt admin only
#         raise HTTPException(status_code=401, detail="Admin authentication required for focus prompt.")

#     # ---- collect & validate files
#     all_files = (prds or []) + (knowledge_base or []) + (field_issues or [])
#     # reject legacy .doc
#     _, _, _, legacy_bad = _split_by_type(all_files)
#     if legacy_bad:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Legacy .doc files are not supported: {', '.join(legacy_bad)}. Please upload .docx/.csv/.xlsx.",
#         )

#     # split by buckets (we’ll parse per bucket with stronger guards)
#     prd_docx, prd_csvs, prd_xlsxs, _ = _split_by_type(prds)
#     kb_docx, kb_csvs, kb_xlsxs, _ = _split_by_type(knowledge_base)
#     fri_docx, fri_csvs, fri_xlsxs, _ = _split_by_type(field_issues)

#     # ---- parse rows from each source type
#     prd_rows = _rows_from_docx_bytes(prd_docx) + _rows_from_table_files(prd_csvs, prd_xlsxs)
#     kb_rows  = _rows_from_docx_bytes(kb_docx)  + _rows_from_table_files(kb_csvs, kb_xlsxs)
#     fri_rows = _rows_from_docx_bytes(fri_docx) + _rows_from_table_files(fri_csvs, fri_xlsxs)

#     if not (prd_rows or kb_rows or fri_rows):
#         raise HTTPException(status_code=400, detail="No usable content detected in uploads.")

#     # ---- subproducts parsing (multi-support)
#     selected_subproducts = [subproduct]
#     if subproducts:
#         try:
#             arr = json.loads(subproducts)
#             if isinstance(arr, list) and len(arr) > 0:
#                 selected_subproducts = [str(x) for x in arr if str(x).strip()]
#         except Exception:
#             # ignore malformed JSON; continue with single subproduct
#             pass

#     # ---- build context package for pipeline
#     sources_payload = {
#         "product": product,
#         "subproducts": selected_subproducts,
#         "focus": (focus or "").strip(),
#         "data": {
#             "prds": prd_rows,
#             "knowledge_base": kb_rows,
#             "field_issues": fri_rows,
#         },
#     }

#     # ---- run pipeline
#     try:
#         pipe = DFMEAPipeline()
#         # Expect your pipeline to accept the structured dict and return:
#         #   entries: list of DFMEA rows (dicts),
#         #   counts: ingestion stats,
#         #   excel_bytes: optional ready-made Excel (bytes). If None, we synthesize below.
#         result = pipe.run(sources_payload)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

#     if not isinstance(result, dict):
#         raise HTTPException(status_code=500, detail="Pipeline returned invalid response.")

#     entries = result.get("entries", [])
#     counts = result.get("counts", {})
#     excel_bytes = result.get("excel_bytes", None)

#     if excel_bytes is None:
#         excel_bytes = _make_excel_download_bytes(entries)

#     excel_b64 = base64.b64encode(excel_bytes).decode("utf-8") if excel_bytes else None

#     # Backward-compat: FastAPI response_model forces keys present
#     return DFMEAResponse(
#         product=product,
#         subproduct=selected_subproducts[0],
#         entries=entries,
#         counts=counts,
#         excel_base64=excel_b64,
    # )
# backend/api.py
# backend/api.py
import base64
import io
import json
import os
import tempfile
import traceback
from typing import List, Optional, Tuple

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---- Config ----
DFMEA_DEBUG = os.getenv("DFMEA_DEBUG", "0") == "1"

# ---- Pipeline & utils ----
from server.pipeline.dfmea_pipeline import DFMEAPipeline
from server.utils.excel_parser import read_csv_safe, read_excel_safe
from server.utils.docx_parser import parse_docx_to_rows  # may have varying signature

# ---------------- FastAPI app ----------------
app = FastAPI(title="DFMEA Backend", version="1.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Models ----------------
class DFMEAResponse(BaseModel):
    product: str
    subproduct: str
    entries: list
    counts: dict = {}
    excel_base64: Optional[str] = None
    message: Optional[str] = None  # helpful status note

# ---------------- Helpers ----------------
def _is_legacy_doc(filename: str) -> bool:
    if not filename:
        return False
    name = filename.lower()
    return name.endswith(".doc") and not name.endswith(".docx")

def _split_by_type(files: List[UploadFile]) -> Tuple[list, list, list, list, list]:
    """
    Split UploadFile list into (docx_list, csv_list, xlsx_list, empty_list, legacy_doc_list).
    Each list contains tuples (filename, bytes).
    """
    docx, csvs, xlsxs, empties, legacy = [], [], [], [], []
    for uf in files or []:
        fname = uf.filename or ""
        if _is_legacy_doc(fname):
            legacy.append(fname)
            continue

        # read bytes safely
        blob: bytes = b""
        try:
            uf.file.seek(0, io.SEEK_SET)
            blob = uf.file.read()
        except Exception:
            try:
                blob = uf.read()
            except Exception:
                blob = b""

        if not blob:
            empties.append(fname)
            continue

        name = fname.lower()
        if name.endswith(".docx"):
            docx.append((fname, blob))
        elif name.endswith(".csv"):
            csvs.append((fname, blob))
        elif name.endswith(".xlsx"):
            xlsxs.append((fname, blob))
        else:
            # ignore unknown extensions; we only support docx/csv/xlsx
            pass
    return docx, csvs, xlsxs, empties, legacy

def _normalize_rows(rows, fname: str) -> list:
    """Ensure rows is a list[dict] and each row has a 'source'."""
    norm = []
    if not rows:
        return norm
    for item in rows:
        if isinstance(item, dict):
            if "source" not in item:
                item["source"] = fname
            norm.append(item)
        else:
            # If parser returned strings or other objects, wrap into dict
            norm.append({"source": fname, "text": str(item)})
    return norm

def _parse_docx_anyway(fname: str, blob: bytes) -> list:
    """
    Try multiple call styles so we work with any parse_docx_to_rows signature:
      1) parse_docx_to_rows(BytesIO, source_name=fname)
      2) parse_docx_to_rows(BytesIO)
      3) write temp file and call parse_docx_to_rows(path)
    Normalize the returned rows to list[dict] with 'source'.
    """
    # 1) try keyword 'source_name'
    try:
        bio = io.BytesIO(blob)
        rows = parse_docx_to_rows(bio, source_name=fname)  # may raise TypeError if kw not supported
        return _normalize_rows(rows, fname)
    except TypeError:
        pass
    except Exception:
        # other parser error with kw path — surface later
        raise

    # 2) try without keyword
    try:
        bio = io.BytesIO(blob)
        rows = parse_docx_to_rows(bio)  # parser might accept only one arg
        return _normalize_rows(rows, fname)
    except TypeError:
        pass
    except Exception:
        # keep going, fallback to path
        ...

    # 3) fallback to temp file path
    try:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(blob)
            tmp_path = tmp.name
        try:
            rows = parse_docx_to_rows(tmp_path)
            return _normalize_rows(rows, fname)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    except Exception as e:
        raise e  # let caller wrap into HTTPException

def _rows_from_docx_bytes(items: List[Tuple[str, bytes]], bucket: str) -> list:
    rows = []
    for fname, blob in items:
        try:
            r = _parse_docx_anyway(fname, blob)
            if r:
                rows.extend(r)
        except Exception as e:
            _fail(400, f"{bucket} DOCX '{fname}' parse failed: {e}")
    return rows

def _rows_from_table_files(csvs: List[Tuple[str, bytes]], xlsxs: List[Tuple[str, bytes]], bucket: str) -> list:
    rows = []
    for fname, blob in csvs:
        try:
            df = read_csv_safe(blob)
            if df is None or df.empty:
                _fail(400, f"{bucket} CSV '{fname}' has no data.")
            df["__source__"] = fname
            rows.extend(df.to_dict(orient="records"))
        except Exception as e:
            _fail(400, f"{bucket} CSV '{fname}' parse failed: {e}")

    for fname, blob in xlsxs:
        try:
            df = read_excel_safe(blob)
            if df is None or df.empty:
                _fail(400, f"{bucket} Excel '{fname}' has no data.")
            df["__source__"] = fname
            rows.extend(df.to_dict(orient="records"))
        except Exception as e:
            _fail(400, f"{bucket} Excel '{fname}' parse failed: {e}")
    return rows

def _make_excel_download_bytes(entries: list) -> Optional[bytes]:
    try:
        import pandas as pd
        if not entries:
            return None
        df = pd.DataFrame(entries)
        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as xw:
            df.to_excel(xw, index=False, sheet_name="DFMEA")
        return bio.getvalue()
    except Exception:
        return None

def _fail(status: int, msg: str):
    if DFMEA_DEBUG:
        tb = traceback.format_exc()
        if "NoneType: None" not in tb:
            msg = f"{msg}\n{tb.splitlines()[-1]}"
    raise HTTPException(status_code=status, detail=msg)

# ---------------- Routes ----------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/dfmea/generate", response_model=DFMEAResponse)
def generate_dfmea(
    # text fields
    product: str = Form(...),
    subproduct: str = Form(...),
    subproducts: Optional[str] = Form(None),   # JSON array string (for multi support)
    focus: Optional[str] = Form(None),

    # files (multiple per field)
    prds: List[UploadFile] = File(default_factory=list),
    knowledge_base: List[UploadFile] = File(default_factory=list),
    field_issues: List[UploadFile] = File(default_factory=list),

    # admin header (optional)
    x_admin_auth: Optional[str] = Header(default=None, alias="X-Admin-Auth"),
):
    # ---- security: optional admin prompt gate
    if (focus or "").strip() and not x_admin_auth:
        _fail(401, "Admin authentication required for focus prompt.")

    # ---- collect & validate files
    all_files = (prds or []) + (knowledge_base or []) + (field_issues or [])
    # reject legacy .doc
    _, _, _, _, legacy_bad = _split_by_type(all_files)
    if legacy_bad:
        _fail(400, f"Legacy .doc files are not supported: {', '.join(legacy_bad)}. Please upload .docx/.csv/.xlsx.")

    # split by buckets
    prd_docx, prd_csvs, prd_xlsxs, prd_empty, _  = _split_by_type(prds)
    kb_docx,  kb_csvs,  kb_xlsxs,  kb_empty,  _  = _split_by_type(knowledge_base)
    fri_docx, fri_csvs, fri_xlsxs, fri_empty, _  = _split_by_type(field_issues)

    # empties
    empties = prd_empty + kb_empty + fri_empty
    if empties:
        _fail(400, f"Empty uploads detected: {', '.join([e or '(unnamed)'] for e in empties)}")

    # parse rows per bucket
    prd_rows = _rows_from_docx_bytes(prd_docx, "PRD") + _rows_from_table_files(prd_csvs, prd_xlsxs, "PRD")
    kb_rows  = _rows_from_docx_bytes(kb_docx,  "Knowledge Base") + _rows_from_table_files(kb_csvs, kb_xlsxs, "Knowledge Base")
    fri_rows = _rows_from_docx_bytes(fri_docx, "Field Issues")   + _rows_from_table_files(fri_csvs, fri_xlsxs, "Field Issues")

    if not (prd_rows or kb_rows or fri_rows):
        _fail(400, "No usable content detected in uploads. Provide .docx/.csv/.xlsx with valid data.")

    # subproducts parsing (multi-support)
    selected_subproducts = [subproduct] if (subproduct or "").strip() else []
    if subproducts:
        try:
            arr = json.loads(subproducts)
            if isinstance(arr, list):
                selected_subproducts = [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
    if not selected_subproducts:
        _fail(400, "No subproduct selected.")

    # build context for pipeline
    sources_payload = {
        "product": product,
        "subproducts": selected_subproducts,
        "focus": (focus or "").strip(),
        "data": {
            "prds": prd_rows,
            "knowledge_base": kb_rows,
            "field_issues": fri_rows,
        },
    }

    # run pipeline
    try:
        pipe = DFMEAPipeline(product=product, subproduct=selected_subproducts[0])
        # Must return dict with keys: entries, counts (optional), excel_bytes (optional)
        result = pipe.run(sources_payload)
    except HTTPException:
        raise
    except Exception as e:
        if DFMEA_DEBUG:
            tb = traceback.format_exc()
            _fail(500, f"Pipeline error: {e}\n{tb}")
        _fail(500, f"Pipeline error: {e}")

    if not isinstance(result, dict):
        _fail(500, "Pipeline returned invalid response (expected dict).")

    entries = result.get("entries", [])
    counts = result.get("counts", {})
    excel_bytes = result.get("excel_bytes", None)
    if excel_bytes is None:
        excel_bytes = _make_excel_download_bytes(entries)

    excel_b64 = base64.b64encode(excel_bytes).decode("utf-8") if excel_bytes else None

    return DFMEAResponse(
        product=product,
        subproduct=selected_subproducts[0],
        entries=entries,
        counts=counts,
        excel_base64=excel_b64,
        message="OK",
    )



