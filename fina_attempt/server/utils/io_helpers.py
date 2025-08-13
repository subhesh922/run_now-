# server/utils/io_helpers.py
from __future__ import annotations

import os
import re
import tempfile
from typing import Iterable, List, Optional, Tuple

from fastapi import UploadFile


SAFE_CHARS = re.compile(r"[^A-Za-z0-9._\- ]+")


# ---------- Path/name helpers ----------

def safe_basename(name: str, fallback: str = "file") -> str:
    """
    Sanitize a user-supplied filename to a safe basename.
    """
    if not name:
        return fallback
    base = os.path.basename(name)
    base = SAFE_CHARS.sub("_", base).strip(" .")
    return base or fallback


def ensure_dir(path: str) -> str:
    """
    Create directory if missing; return the path.
    """
    os.makedirs(path, exist_ok=True)
    return path


def is_csv(name: str) -> bool:
    n = (name or "").lower()
    return n.endswith(".csv")


def is_excel(name: str) -> bool:
    n = (name or "").lower()
    return n.endswith(".xlsx") or n.endswith(".xls")


def is_docx(name: str) -> bool:
    n = (name or "").lower()
    return n.endswith(".docx") or n.endswith(".doc")


def choose_ext_from_name(name: str) -> str:
    """
    Pick a sensible extension based on the original file name.
    Default to .bin if unknown.
    """
    if is_csv(name):
        return ".csv"
    if is_excel(name):
        return ".xlsx"
    if is_docx(name):
        return ".docx"
    return ".bin"


# ---------- Temp file helpers ----------

def save_uploads(
    files: Optional[Iterable[UploadFile]],
    *,
    prefix: str,
    dirpath: Optional[str] = None,
) -> List[str]:
    """
    Save FastAPI UploadFile objects to temp files. Returns list of file paths.
    """
    paths: List[str] = []
    if not files:
        return paths

    for f in files:
        if not f:
            continue
        orig = safe_basename(f.filename or "")
        ext = choose_ext_from_name(orig)
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext, prefix=f"{prefix}_", dir=dirpath)
        data = f.file.read()  # synchronous read is fine here
        tf.write(data)
        tf.flush()
        tf.close()
        paths.append(tf.name)
    return paths


def save_bytes(
    data: bytes,
    *,
    prefix: str = "dfmea",
    suffix: str = ".bin",
    dirpath: Optional[str] = None,
) -> str:
    """
    Save raw bytes to a temp file and return the path.
    """
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=f"{prefix}_", dir=dirpath)
    tf.write(data or b"")
    tf.flush()
    tf.close()
    return tf.name
