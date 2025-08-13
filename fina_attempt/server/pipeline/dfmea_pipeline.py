# server/pipeline/dfmea_pipeline.py
from __future__ import annotations

import os
from typing import Dict, List, Optional

import pandas as pd

from server.agents.extraction_agent import ExtractionAgent, ExtractionConfig
from server.agents.chunking_agent import ChunkingAgent, ChunkingConfig
from server.agents.embedding_agent import EmbeddingAgent
from server.agents.vectorstore_agent import VectorStoreAgent, QdrantConfig
from server.agents.context_agent import ContextAgent
from server.agents.writer_agent import WriterAgent


class DFMEAPipeline:
    """
    End-to-end pipeline:
      1) index():   load KB/Field/PRDs -> chunk -> embed -> upsert to Qdrant
      2) generate(): use ContextAgent.generate(field_issues_rows) to get DFMEA entries
      3) write_excel(): export DFMEA entries to Excel bytes
    """

    def __init__(
        self,
        *,
        product: str,
        subproduct: str,
        qdrant_collection: str | None = None,
    ):
        self.product = product
        self.subproduct = subproduct

        # Collection: allow override; otherwise read env or default
        self.collection = (
            qdrant_collection
            or os.getenv("QDRANT_COLLECTION")
            or "dfmea_corpus"
        )

        # Make sure the compat ContextAgent sees the same collection name (if it reads env)
        os.environ["QDRANT_COLLECTION"] = self.collection

        # Agents
        self.extractor = ExtractionAgent(
            ExtractionConfig(product=self.product, subproduct=self.subproduct)
        )
        self.chunker = ChunkingAgent(ChunkingConfig())

        # Azure embeddings (aligned agent)
        self.embedder = EmbeddingAgent()

        # Vector store
        self.vstore = VectorStoreAgent(QdrantConfig(collection=self.collection))

        # Context + Writer
        self.context = ContextAgent(collection_name=self.collection)
        self.writer = WriterAgent()

    # ---------------- Indexing ---------------- #

    def index(
        self,
        *,
        kb_paths: Optional[List[str]] = None,
        field_paths: Optional[List[str]] = None,
        prd_paths: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Build the corpus for (product, subproduct) by reading the provided files
        (KB/Field/PRDs), chunking, embedding, and upserting to Qdrant.

        Returns simple counts: {"items": X, "chunks": Y, "embedded": Z, "upserted": Z}
        """
        # Wire file paths (keep defaults if none provided)
        if kb_paths is not None:
            self.extractor.config.kb_paths = kb_paths
        if field_paths is not None:
            self.extractor.config.field_paths = field_paths
        if prd_paths is not None:
            self.extractor.config.prd_paths = prd_paths

        # 1) Extract normalized items
        items = self.extractor.run()
        items = [it for it in items if it.get("text")]
        n_items = len(items)

        # 2) Chunk (preserves meta)
        chunks = self.chunker.run(items)
        n_chunks = len(chunks)

        if n_chunks == 0:
            return {"items": n_items, "chunks": 0, "embedded": 0, "upserted": 0}

        # 3) Embed (uses Azure embeddings)
        embedded = self.embedder.run(chunks)
        n_emb = len(embedded)

        if n_emb == 0:
            return {"items": n_items, "chunks": n_chunks, "embedded": 0, "upserted": 0}

        # 4) Upsert to Qdrant
        wrote = self.vstore.upsert(embedded)

        return {"items": n_items, "chunks": n_chunks, "embedded": n_emb, "upserted": wrote}

    # ---------------- Generation ---------------- #

    def _fri_df_to_rows(
        self,
        fri_df: pd.DataFrame,
        *,
        product_key: str = None,
        subsystem_key: str = None,
        component_key: str = None,
        fault_code_key: str = None,
        fault_type_key: str = None,
    ) -> List[Dict]:
        """
        Convert Field Reported Issues DataFrame to the row dicts expected by ContextAgent.generate().
        We keep this tolerant—if keys are missing, we fill from pipeline product/subproduct.
        """
        rows: List[Dict] = []

        # Heuristic key guesses if not provided
        cols = {c.lower(): c for c in fri_df.columns}
        product_key = product_key or cols.get("product")
        subsystem_key = subsystem_key or cols.get("subsystem") or cols.get("sub_product") or cols.get("subproduct")
        component_key = component_key or cols.get("component") or subsystem_key  # default to subsystem if missing
        fault_code_key = fault_code_key or cols.get("fault_code") or cols.get("code")
        fault_type_key = fault_type_key or cols.get("fault_type") or cols.get("type")

        for _, r in fri_df.iterrows():
            rows.append(
                {
                    "product": str(r.get(product_key) if product_key else self.product),
                    "subsystem": str(r.get(subsystem_key) if subsystem_key else self.subproduct),
                    "component": str(r.get(component_key) if component_key else self.subproduct),
                    "fault_code": str(r.get(fault_code_key) or "") if fault_code_key else "",
                    "fault_type": str(r.get(fault_type_key) or "") if fault_type_key else "",
                }
            )
        return rows

    def generate(
        self,
        *,
        field_issues_df: pd.DataFrame,
        score_threshold: float = 0.48,
        top_k: int = 12,
        min_hits: int = 2,
        focus: str | None = None,
    ) -> List[Dict]:
        """
        Calls ContextAgent.generate(field_issues_rows) and returns DFMEA entries (list of dicts).
        """
        rows = self._fri_df_to_rows(field_issues_df)

        # tune thresholds to match your old behavior
        self.context.top_k = top_k
        self.context.score_threshold = score_threshold
        self.context.min_hits = min_hits

        # forward optional admin focus if supported
        try:
            entries = self.context.generate(field_issues=rows, focus=focus) or []
        except TypeError:
            entries = self.context.generate(field_issues=rows) or []
        return entries

    # ---------------- Writing ---------------- #

    def write_excel(self, entries: List[Dict]) -> bytes:
        """
        Convert DFMEA entries (list[dict]) to Excel bytes (DFMEA/Evidence/Summary).
        """
        meta = {"product": self.product, "subproduct": self.subproduct}
        return self.writer.to_excel_bytes(entries, meta=meta)
