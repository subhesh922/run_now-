# server/agents/chunking_agent.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Any, List, Iterable, Optional

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(])")

@dataclass
class ChunkingConfig:
    # Approximate chunk sizes by characters (keeps things dependency-free)
    chunk_size: int = 900          # target characters per chunk
    chunk_overlap: int = 150       # overlap between consecutive chunks
    min_chunk_size: int = 200      # avoid tiny fragments
    sentence_aware: bool = True    # try to cut along sentence boundaries first
    normalize_ws: bool = True      # condense whitespace
    trim_quotes: bool = True       # strip matching leading/trailing quotes

def _clean_text(text: str, cfg: ChunkingConfig) -> str:
    s = text or ""
    if cfg.normalize_ws:
        s = re.sub(r"\s+", " ", s)
    s = s.strip()
    if cfg.trim_quotes and len(s) >= 2:
        quotes = [("“", "”"), ("\"", "\""), ("'", "'")]
        for ql, qr in quotes:
            if s.startswith(ql) and s.endswith(qr):
                s = s[1:-1].strip()
                break
    return s

def _split_sentences(text: str) -> List[str]:
    # Simple sentence splitter (punctuation-based). Keeps things lightweight.
    if not text:
        return []
    parts = _SENT_SPLIT.split(text)
    # Merge micro-sentences (e.g., headings) with neighbors if needed
    merged: List[str] = []
    buf = ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if not buf:
            buf = p
        else:
            # Attach very short “sentences” to buffer
            if len(p) < 40 or len(buf) < 60:
                buf = f"{buf} {p}"
            else:
                merged.append(buf)
                buf = p
    if buf:
        merged.append(buf)
    return merged

def _windowed_chunks_by_chars(text: str, cfg: ChunkingConfig) -> List[str]:
    # Hard windowing by characters, with overlap
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    size = max(cfg.chunk_size, cfg.min_chunk_size)
    ov = max(0, min(cfg.chunk_overlap, size - 1))
    while start < n:
        end = min(n, start + size)
        chunk = text[start:end]
        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(end - ov, start + 1)
    return chunks

def _sentence_aware_chunks(text: str, cfg: ChunkingConfig) -> List[str]:
    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks: List[str] = []
    cur = ""
    for s in sentences:
        # If adding this sentence keeps us under or near the target, add it
        if len(cur) + 1 + len(s) <= cfg.chunk_size:
            cur = s if not cur else f"{cur} {s}"
        else:
            # If current is too small, try to squeeze more; else flush
            if cur:
                if len(cur) < cfg.min_chunk_size and len(s) < cfg.chunk_size:
                    cur = f"{cur} {s}"
                else:
                    chunks.append(cur.strip())
                    cur = s
            else:
                # Very long single sentence → hard split by chars
                chunks.extend(_windowed_chunks_by_chars(s, cfg))
                cur = ""
    if cur:
        chunks.append(cur.strip())

    # Add overlap by duplicating trailing/leading tails
    if cfg.chunk_overlap > 0 and len(chunks) > 1:
        ov = cfg.chunk_overlap
        with_overlap: List[str] = []
        for i, ch in enumerate(chunks):
            if i == 0:
                with_overlap.append(ch)
                continue
            prev = with_overlap[-1]
            tail = prev[-ov:] if len(prev) > ov else prev
            # Only add overlap if it’s not already present at the start
            if not ch.startswith(tail):
                ch = (tail + " " + ch).strip()
            with_overlap.append(ch)
        chunks = with_overlap

    return chunks

class ChunkingAgent:
    """
    Splits normalized items into overlapping text chunks while preserving metadata.

    Input items (from ExtractionAgent.run()):
        {
          "product": "...",
          "subproduct": "...",
          "source_type": "kb|field|prd",
          "file": "<basename>",
          "idx": <row_or_paragraph_index>,
          "text": "<clean string>"
        }

    Output:
        {
          "chunk": "<text slice>",
          "meta": {
            "product": "...",
            "subproduct": "...",
            "source_type": "...",
            "file": "...",
            "idx": <origin idx>,
            "chunk_id": <sequential int per input row>,
          }
        }
    """

    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.cfg = config or ChunkingConfig()

    def run(self, items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for it in items:
            text = _clean_text(it.get("text", ""), self.cfg)
            if not text:
                continue

            # Choose strategy
            if self.cfg.sentence_aware:
                chunks = _sentence_aware_chunks(text, self.cfg)
            else:
                chunks = _windowed_chunks_by_chars(text, self.cfg)

            if not chunks:
                continue

            # Emit with preserved metadata
            seq = 0
            base_meta = {
                "product": it.get("product", ""),
                "subproduct": it.get("subproduct", ""),
                "source_type": it.get("source_type", ""),
                "file": it.get("file", ""),
                "idx": int(it.get("idx", 0)),
            }
            for ch in chunks:
                out.append({
                    "chunk": ch,
                    "meta": {**base_meta, "chunk_id": seq},
                })
                seq += 1

        return out

# Quick manual test
if __name__ == "__main__":
    sample_items = [
        {
            "product": "Quasar",
            "subproduct": "Display",
            "source_type": "prd",
            "file": "Display PRD.docx",
            "idx": 12,
            "text": "Readability in Sunlight: Device terminal display shall be readable outdoors in direct sunlight at 20,000 lux when at full backlight. Measured with the complete terminal stack up."
        },
        {
            "product": "Quasar",
            "subproduct": "Touch Panel",
            "source_type": "prd",
            "file": "TP PRD.docx",
            "idx": 3,
            "text": "The touch panel shall have minimum 85% light transmission. Base SKU shall use Gorilla Glass 5 or better."
        },
    ]

    agent = ChunkingAgent()
    chunks = agent.run(sample_items)
    print(f"Generated {len(chunks)} chunks")
    for c in chunks[:4]:
        print(c["meta"], "->", c["chunk"][:90].replace("\n", " "))
