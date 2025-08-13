# server/agents/extraction_agent.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from server.utils.parsers import load_all_sources  # ← central loaders (kb/field/prd)

# -------------------------
# Defaults (kept from old app spirit)
# -------------------------
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_files")

DEFAULT_KB = os.path.join(SAMPLE_DIR, "dfmea_knowledge_bank_3.csv")
DEFAULT_FIELD = os.path.join(SAMPLE_DIR, "field_reported_issues_3.xlsx")
DEFAULT_PRDS = [
    os.path.join(SAMPLE_DIR, "Display PRD_Quasar_cleaned.docx.docx"),
    os.path.join(SAMPLE_DIR, "TP PRD_Quasar_cleaned.docx.docx"),
    os.path.join(SAMPLE_DIR, "environmental spec_Quasar_cleaned.docx.docx"),
]

# -------------------------
# Config
# -------------------------
@dataclass
class ExtractionConfig:
    product: str = "Quasar"
    subproduct: str = "Display"
    kb_paths: Optional[List[str]] = None           # CSV/XLSX
    field_paths: Optional[List[str]] = None        # CSV/XLSX
    prd_paths: Optional[List[str]] = None          # DOCX

# -------------------------
# Agent
# -------------------------
class ExtractionAgent:
    """
    Unified loader for Knowledge Bank (CSV/XLSX), Field Issues (CSV/XLSX), and PRDs (DOCX).
    Output rows (normalized):
      {
        "product": product,
        "subproduct": subproduct,
        "source_type": "kb|field|prd",
        "file": "<basename>",
        "idx": <row/paragraph index>,
        "text": "<string>",
        # optional: "requirement_id": "<REQ-1234|Quasar-5091>"
      }
    """

    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        # preserve your old defaults if not provided
        if self.config.kb_paths is None:
            self.config.kb_paths = [p for p in [DEFAULT_KB] if os.path.exists(p)]
        if self.config.field_paths is None:
            self.config.field_paths = [p for p in [DEFAULT_FIELD] if os.path.exists(p)]
        if self.config.prd_paths is None:
            self.config.prd_paths = [p for p in DEFAULT_PRDS if os.path.exists(p)]

    def run(self) -> List[Dict[str, Any]]:
        """
        Returns normalized, concatenated items from Field → PRDs → KB (same order as before).
        """
        rows = load_all_sources(
            product=self.config.product,
            subproduct=self.config.subproduct,
            kb_paths=self.config.kb_paths,
            field_paths=self.config.field_paths,
            prd_paths=self.config.prd_paths,
        )
        # keep only rows with text
        return [r for r in rows if (r.get("text") or "").strip()]

# -------------------------
# Quick manual test
# -------------------------
if __name__ == "__main__":
    agent = ExtractionAgent(ExtractionConfig(product="Quasar", subproduct="Display"))
    items = agent.run()
    print(f"Loaded items: {len(items)}")
    for row in items[:5]:
        print(row["source_type"], row["file"], row["idx"], "->", row["text"][:120].replace("\n", " "))
