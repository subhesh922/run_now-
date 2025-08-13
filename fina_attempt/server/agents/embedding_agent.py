# server/agents/embedding_agent.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Tuple

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import RateLimitError, APIConnectionError, InternalServerError

# Optional tokenizer for token accounting
try:
    from tiktoken import get_encoding
    _tok = get_encoding("cl100k_base")
except Exception:  # pragma: no cover
    _tok = None

# Your Azure client helper (must exist in your repo)
from server.utils.azure_openai_client import (
    get_azure_openai_client,
    AZURE_EMBEDDING_DEPLOYMENT,
)

def _as_text_and_meta(item: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Accepts either:
      - {"chunk": "<text>", "meta": {...}}
      - {"text": "<text>", "metadata": {...}}
    and normalizes to (text, metadata).
    """
    if "chunk" in item or "meta" in item:
        text = str(item.get("chunk", "") or "")
        meta = dict(item.get("meta", {}) or {})
    else:
        text = str(item.get("text", "") or "")
        meta = dict(item.get("metadata", {}) or {})
    return text, meta

def _should_embed(meta: Dict[str, Any]) -> bool:
    """
    Follow your rule:
      - embed only when metadata.embed == True
      - if flag is missing, infer:
          True for non-field sources, False for field
    """
    if "embed" in meta:
        return bool(meta.get("embed"))
    src = (meta.get("source_type") or meta.get("source") or "").lower()
    return src != "field"  # default: embed kb/prd, skip field

def _count_tokens(text: str) -> int:
    if not _tok:
        # rough fallback ~4 chars/token
        return max(1, len(text or "") // 4)
    return len(_tok.encode(text or ""))

class EmbeddingAgent:
    """
    Azure OpenAI embeddings with batching, retries, and cooldowns.

    INPUT (either shape works):
      - {"chunk": "<text>", "meta": {...}}                      # from our chunker
      - {"text": "<text>", "metadata": {...}}                   # from your prior code

    OUTPUT:
      {
        "text": "<original text>",
        "embedding": [float,...],
        "vector": [float,...],           # alias for convenience
        "metadata": {...},               # always returned under 'metadata'
        "tokens": <int>
      }

    Notes:
      - Only items with metadata.embed == True are embedded.
      - If 'embed' missing, we infer True for non-field sources.
      - Skips empty/whitespace-only texts.
    """

    def __init__(self):
        self.client = get_azure_openai_client()
        self.deployment = AZURE_EMBEDDING_DEPLOYMENT
        if not self.deployment:
            raise RuntimeError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT is not set.")

        # tune via env if needed
        self.batch_size = int(os.getenv("EMBED_BATCH_SIZE", "50"))
        self.cooldown = float(os.getenv("EMBED_BATCH_COOLDOWN_SEC", "2"))

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convenience wrapper that mirrors our earlier agent signature:
        takes chunked items and returns embedded records.
        """
        # Convert to the structure your existing code expects: {"text","metadata"}
        normalized = []
        for it in (items or []):
            text, meta = _as_text_and_meta(it)
            # ensure consistent key spelling for downstream
            normalized.append({"text": text, "metadata": meta})

        return self.embed_chunks_sync(normalized)

    def embed_chunks_sync(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batches calls to Azure OpenAI embeddings API.

        Returns: list of
          { "text", "embedding", "vector", "metadata", "tokens" }
        """
        to_embed = []
        for c in (chunks or []):
            text = c.get("text", "")
            meta = c.get("metadata", {}) or {}
            if not isinstance(text, str) or not text.strip():
                continue
            if _should_embed(meta):
                to_embed.append({"text": text, "metadata": meta})

        skipped = (len(chunks) if chunks else 0) - len(to_embed)
        print(f"[EmbeddingAgent] Preparing to embed {len(to_embed)} chunk(s); skipped {skipped} non-embeddable/empty item(s).")

        embedded: List[Dict[str, Any]] = []
        if not to_embed:
            self._log_token_usage(embedded)
            return embedded

        for i in range(0, len(to_embed), self.batch_size):
            batch = to_embed[i : i + self.batch_size]
            texts = [b["text"] for b in batch]
            metas = [b["metadata"] for b in batch]

            # Guard again against unexpected empties
            keep = [(t, m) for (t, m) in zip(texts, metas) if isinstance(t, str) and t.strip()]
            if not keep:
                continue
            texts, metas = zip(*keep)

            try:
                resp = self._embed_with_retry(list(texts))
                # Azure/OpenAI returns embeddings in resp.data[j].embedding
                for j, item in enumerate(resp.data):
                    text = texts[j]
                    meta = metas[j]
                    vec = item.embedding
                    embedded.append({
                        "text": text,
                        "embedding": vec,
                        "vector": vec,         # alias
                        "metadata": meta,
                        "tokens": _count_tokens(text),
                    })
            except Exception as e:
                print(f"[EmbeddingAgent] Batch {i//self.batch_size+1} failed after retries: {type(e).__name__}: {e}")

            time.sleep(self.cooldown)

        self._log_token_usage(embedded)
        return embedded

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError, InternalServerError)),
        reraise=True,
    )
    def _embed_with_retry(self, texts: List[str]):
        return self.client.embeddings.create(input=texts, model=self.deployment)

    def _log_token_usage(self, embedded: List[Dict[str, Any]]):
        total_tokens = sum(item.get("tokens", 0) for item in embedded)
        kb_tokens = sum(
            item.get("tokens", 0)
            for item in embedded
            if ((item.get("metadata") or {}).get("source") == "knowledge_bank")
            or ((item.get("metadata") or {}).get("source_type") == "kb")
        )
        field_tokens = sum(
            item.get("tokens", 0)
            for item in embedded
            if ((item.get("metadata") or {}).get("source") == "field_reported_issues")
            or ((item.get("metadata") or {}).get("source_type") == "field")
        )

        print("\n🔍 [EmbeddingAgent] Token Usage Summary")
        print(f"  • Embedded Items        : {len(embedded)}")
        print(f"  • Total Tokens          : {total_tokens:,}")
        print(f"  • Knowledge Bank Tokens : {kb_tokens:,}")
        print(f"  • Field Issues Tokens   : {field_tokens:,} (should be 0 if you keep embed=False for field)")
