# server/agents/context_agent.py
from __future__ import annotations
import json
import re
from typing import List, Dict, Any, Optional

from server.agents.vectorstore_agent import VectorStoreAgent
from server.utils.azure_openai_client import (
    get_azure_openai_client,
    AZURE_CHAT_DEPLOYMENT,
)

SAFE_SYSTEM_MSG = (
    "You are a DFMEA analyst.\n"
    "- Use ONLY the provided CONTEXT below.\n"
    "- If evidence is insufficient, return an empty JSON array [].\n"
    "- Every DFMEA entry you return must include a 'citations' array with kb_id(s) used. "
    "If you cannot cite, return [].\n"
    "- Return pure JSON (array) with no markdown/code fences.\n"
    "- Do NOT compute RPN; the system will handle S/O/D/RPN."
)

class ContextAgent:
    """
    Strict retrieval + cite-or-abstain.
    - Filters by product/subsystem/component
    - Applies a score threshold
    - Calls LLM only when evidence is strong
    - Output shape matches previous implementation exactly (list of dicts with 'citations')
    """

    def __init__(
        self,
        collection_name: str,
        batch_size: int = 5,                # kept for compatibility (not used in this sync version)
        product: Optional[str] = None,
        subsystem: Optional[str] = None,
        components: Optional[List[str]] = None,
        top_k: int = 12,
        score_threshold: float = 0.48,
        min_hits: int = 2,
    ):
        self.collection_name = collection_name
        self.vectorstore = VectorStoreAgent(collection_name=self.collection_name)
        self.batch_size = batch_size
        self.product = product
        self.subsystem = subsystem
        self.components = components or []
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.min_hits = min_hits

        # Azure client (shared factory)
        self.client = get_azure_openai_client()
        self.chat_deploy = AZURE_CHAT_DEPLOYMENT or "gpt-4o"
        self.system_msg = SAFE_SYSTEM_MSG

    # ---------- Primary API (kept) ----------
    def generate(self, field_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        field_issues rows should include:
          - product, subsystem, component
          - fault_code (optional), fault_type (optional)
        Returns a flat list of DFMEA entries (each with 'citations').
        Abstains (skips a row) if evidence is weak.
        """
        all_entries: List[Dict[str, Any]] = []
        next_id = 1

        for row in field_issues or []:
            norm = self._normalize_row(row)

            # 1) compact query string
            query = self._build_query(norm)

            # 2) strict retrieval (filters + score threshold)
            hits = self.vectorstore.search(
                query=query,
                top_k=self.top_k,
                product=norm["product"],
                subsystem=norm["subsystem"],
                components=[norm["component"]],
                score_threshold=self.score_threshold,
            )
            if not hits or len(hits) < self.min_hits:
                # not enough evidence → abstain on this row
                continue

            # 3) build context lines with bracketed kb_ids (so the model can cite)
            context_lines, kb_ids = self._context_from_hits(hits)
            if not context_lines:
                continue

            # 4) call LLM (low temp), expect pure JSON array; else abstain
            user_msg = self._build_user_message(field_issue=norm, context_texts=context_lines)
            raw = self._chat(self.system_msg, user_msg)
            entries = self._parse_llm_json(raw)
            if not entries:
                continue

            # 5) ensure IDs and citations (keep previous behavior)
            for e in entries:
                if "ID" not in e:
                    e["ID"] = next_id
                # If the model didn’t include citations, fall back to kb_ids we supplied
                if "citations" not in e or not e["citations"]:
                    e["citations"] = kb_ids
                next_id = max(next_id, int(e["ID"]) + 1)
                all_entries.append(e)

        return all_entries

    # ---------- Legacy API (kept, no-op) ----------
    def run(self, query: str, top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Legacy fallback: returns [] so old callers don’t crash.
        Please migrate to generate(field_issues=...).
        """
        return []

    # ---------- Helpers ----------
    def _chat(self, system_msg: str, user_msg: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.chat_deploy,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        return resp.choices[0].message.content or ""

    def _parse_llm_json(self, raw: str) -> List[Dict[str, Any]]:
        # Strip accidental code fences and tolerate whitespace
        cleaned = re.sub(r"^```(json)?", "", raw.strip(), flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
        try:
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    def _normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        product = (row.get("product") or self.product or "").strip()
        subsystem = (row.get("subsystem") or self.subsystem or "").strip()
        component = (row.get("component") or (self.components[0] if self.components else "")).strip()
        return {
            "product": product,
            "subsystem": subsystem,
            "component": component,
            "fault_code": (row.get("fault_code") or "").strip(),
            "fault_type": (row.get("fault_type") or "").strip(),
        }

    def _build_query(self, norm: Dict[str, Any]) -> str:
        parts = [norm["product"], norm["subsystem"], norm["component"]]
        if norm.get("fault_code"):
            parts.append(f"fault:{norm['fault_code']}")
        if norm.get("fault_type"):
            parts.append(f"type:{norm['fault_type']}")
        return " • ".join([p for p in parts if p])

    def _context_from_hits(self, hits: List[Dict[str, Any]]):
        """
        Convert vector matches into:
          - context text lines with bracketed kb_ids
          - a list of kb_ids (for fallback citations)
        Expect each hit to expose text + metadata with a kb_id/uuid if available.
        """
        lines, ids = [], []
        for idx, h in enumerate(hits or []):
            # Keep compatibility with your payload shape
            meta = h.get("metadata") or h.get("payload") or {}
            kb_id = meta.get("kb_id") or meta.get("uuid") or f"ctx_{idx+1}"
            txt = (h.get("text") or meta.get("text") or "").strip()
            if not txt:
                continue
            lines.append(f"[{kb_id}] {txt}")
            ids.append(kb_id)
        return lines, ids

    def _build_user_message(self, field_issue: Dict[str, Any], context_texts: List[str]) -> str:
        fi_block = json.dumps(
            {
                "Product": field_issue.get("product"),
                "Subsystem": field_issue.get("subsystem"),
                "Component": field_issue.get("component"),
                "Fault_Code": field_issue.get("fault_code") or None,
                "Fault_Type": field_issue.get("fault_type") or None,
            },
            indent=2,
        )
        ctx_block = "\n".join(context_texts[: self.top_k])

        return (
            "FIELD_ISSUE:\n" + fi_block + "\n\n"
            "CONTEXT:\n" + ctx_block + "\n\n"
            "TASK:\n"
            "Using ONLY the CONTEXT above, return DFMEA entries as a pure JSON array ([] if insufficient). "
            "Each entry must include 'citations' (kb_ids from the bracketed lines you used). "
            "Do NOT compute RPN; numeric fields will be handled by the system.\n"
        )
