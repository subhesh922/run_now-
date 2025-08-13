# # server/agents/vectorstore_agent.py
# from __future__ import annotations

# import os
# import uuid
# from dataclasses import dataclass
# from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# from qdrant_client import QdrantClient
# from qdrant_client.http.models import (
#     Distance,
#     VectorParams,
#     PointStruct,
#     Filter,
#     FieldCondition,
#     MatchValue,
#     SearchRequest,
# )

# # -------------------------
# # Config dataclass
# # -------------------------
# @dataclass
# class QdrantConfig:
#     url: str = os.getenv("QDRANT_URL", "")
#     api_key: str = os.getenv("QDRANT_API_KEY", "")
#     collection: str = os.getenv("QDRANT_COLLECTION", "dfmea_corpus")
#     prefer_grpc: bool = False
#     https: bool = True
#     timeout: int = int(os.getenv("QDRANT_TIMEOUT_SEC", "120"))
#     verify: bool = False
#     distance: Distance = Distance.COSINE
#     on_missing_create: bool = True  # auto-create collection if missing
#     vectors: Optional[int] = None   # set at ensure_collection(dim) if None

# # -------------------------
# # Vector store wrapper
# # -------------------------
# class VectorStoreAgent:
#     """
#     Qdrant wrapper for DFMEA chunks.

#     Expects embedded items like:
#       {
#         "text" | "chunk": "<text>",
#         "vector" | "embedding": [float,...],
#         "meta" | "metadata": {
#             "product": "...",
#             "subproduct": "...",
#             "source_type": "kb|field|prd",
#             "file": "...",
#             "idx": <int>,
#             ... (anything else is preserved)
#         }
#       }
#     """

#     def __init__(self, cfg: Optional[QdrantConfig] = None):
#         self.cfg = cfg or QdrantConfig()
#         if not self.cfg.url:
#             raise RuntimeError("QDRANT_URL env var is required.")
#         self.client = QdrantClient(
#             url=self.cfg.url,
#             api_key=self.cfg.api_key or None,
#             prefer_grpc=self.cfg.prefer_grpc,
#             https=self.cfg.https,
#             timeout=self.cfg.timeout,
#             verify=self.cfg.verify,
#         )

#     # ---------- public API ----------

#     def ensure_collection(self, vector_dim: int) -> None:
#         """
#         Ensure collection exists with the requested vector dimension.
#         """
#         self.cfg.vectors = vector_dim
#         try:
#             self.client.get_collection(self.cfg.collection)
#             # If exists, we won't mutate vector size here.
#             return
#         except Exception:
#             pass

#         if not self.cfg.on_missing_create:
#             raise RuntimeError(f"Qdrant collection '{self.cfg.collection}' missing and auto-create disabled.")

#         self.client.recreate_collection(
#             collection_name=self.cfg.collection,
#             vectors_config=VectorParams(
#                 size=vector_dim,
#                 distance=self.cfg.distance,
#             ),
#         )

#     def upsert(self, items: Iterable[Dict[str, Any]]) -> int:
#         """
#         Upsert a batch of items into Qdrant.

#         Returns number of points written.
#         """
#         points: List[PointStruct] = []
#         vector_dim: Optional[int] = None

#         for it in items:
#             text = it.get("chunk") or it.get("text") or ""
#             vec = it.get("vector") or it.get("embedding")
#             meta = it.get("meta") or it.get("metadata") or {}
#             if not isinstance(vec, (list, tuple)) or not vec:
#                 # skip items without vectors
#                 continue

#             if vector_dim is None:
#                 vector_dim = len(vec)

#             payload = {
#                 "text": text,
#                 **meta,  # flatten meta for easy filtering (product, subproduct, source_type, file, idx, etc.)
#             }

#             points.append(
#                 PointStruct(
#                     id=str(uuid.uuid4()),
#                     vector=list(vec),
#                     payload=payload,
#                 )
#             )

#         if not points:
#             return 0

#         # Make sure collection exists with correct dim
#         if vector_dim is None:
#             raise RuntimeError("Cannot infer vector dimension from empty batch.")
#         self.ensure_collection(vector_dim)

#         self.client.upsert(collection_name=self.cfg.collection, points=points, wait=True)
#         return len(points)

#     def search(
#         self,
#         query_vector: Sequence[float],
#         *,
#         product: str,
#         subproduct: str,
#         limit: int = 12,
#         source_types: Optional[List[str]] = None,
#         with_payload: bool = True,
#         score_threshold: Optional[float] = None,
#     ) -> List[Dict[str, Any]]:
#         """
#         Search top-K similar points filtered by product/subproduct (and optionally source_types).
#         """
#         if not query_vector:
#             return []

#         conds = [
#             FieldCondition(key="product", match=MatchValue(product)),
#             FieldCondition(key="subproduct", match=MatchValue(subproduct)),
#         ]
#         if source_types:
#             # OR over multiple source_types -> use multiple SearchRequest calls or a single filter with "should" once available
#             # Simple approach: pass list and rely on MatchValue(list) semantics (supported by qdrant-client)
#             conds.append(FieldCondition(key="source_type", match=MatchValue(source_types)))

#         qfilter = Filter(must=conds)

#         req = SearchRequest(
#             collection_name=self.cfg.collection,
#             vector=list(query_vector),
#             limit=limit,
#             with_payload=with_payload,
#             score_threshold=score_threshold,
#             filter=qfilter,
#         )

#         res = self.client.search_batch(requests=[req])[0]
#         out: List[Dict[str, Any]] = []
#         for sp in res:
#             # sp: ScoredPoint
#             payload = sp.payload or {}
#             out.append({
#                 "score": float(sp.score),
#                 "payload": payload,
#                 "vector_id": sp.id,
#             })
#         return out

#     def delete_collection(self) -> None:
#         try:
#             self.client.delete_collection(self.cfg.collection)
#         except Exception:
#             pass

#     def count(self) -> int:
#         try:
#             info = self.client.get_collection(self.cfg.collection)
#             # Qdrant doesn't return point count here; do a dummy scroll/count if needed.
#             # Cheap approach: try a small scroll and track 'total' meta, else return -1.
#             res = self.client.scroll(self.cfg.collection, limit=1, with_payload=False)
#             # res: (points, next_page_offset)
#             total = getattr(res, "total", None)
#             return int(total) if total is not None else -1
#         except Exception:
#             return -1


# # -------------------------
# # Quick manual test
# # -------------------------
# if __name__ == "__main__":
#     import random

#     # Env should have QDRANT_URL / QDRANT_API_KEY set
#     agent = VectorStoreAgent()

#     # Fake vectors (dim=8)
#     samples = []
#     for i in range(5):
#         samples.append({
#             "chunk": f"Sample text {i}",
#             "vector": [random.random() for _ in range(8)],
#             "meta": {
#                 "product": "Quasar",
#                 "subproduct": "Display",
#                 "source_type": "prd" if i % 2 == 0 else "kb",
#                 "file": "dummy",
#                 "idx": i,
#             }
#         })

#     wrote = agent.upsert(samples)
#     print("Upserted:", wrote)

#     q = [0.1] * 8
#     hits = agent.search(q, product="Quasar", subproduct="Display", limit=3)
#     print("Hits:", len(hits))
#     if hits:
#         print(hits[0])


import os
import logging
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from dotenv import load_dotenv
import uuid

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class VectorStoreAgent:
    def __init__(self, collection_name: str = None):
        self.qdrant_url = os.getenv("QDRANT_ENDPOINT")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.base_collection = os.getenv("QDRANT_COLLECTION", "dfmea_collection")
        self.session_id = str(uuid.uuid4())[:8]
        self.collection_name = collection_name or f"{self.base_collection}_{self.session_id}"
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key,
            prefer_grpc=False,  # Make HTTP-based async fallback smoother
            https=True,
            timeout=120,#incresed from 30 standard to 120 for better timeout handeling 
            verify=False
        )
        # Disable SSL verification for all requests
        self.ssl_verify = False

class VectorStoreAgent:
    def __init__(self, cfg: Optional[VectorStoreAgentConfig] = None):
        self.cfg = cfg or VectorStoreAgentConfig()
        try:
            self.client = QdrantClient(
                url=self.cfg.url,
                api_key=self.cfg.api_key or None,
                prefer_grpc=self.cfg.prefer_grpc,
                https=self.cfg.https,
                timeout=self.cfg.timeout,
                verify=self.cfg.verify,
            )
            logger.info(f"Connected to Qdrant at {self.cfg.url} (HTTPS={self.cfg.https}, verify={self.cfg.verify})")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def ensure_collection(self, vector_dim: int):
        try:
            collections = self.client.get_collections().collections
            if self.cfg.collection_name not in [c.name for c in collections]:
                logger.info(f"Creating Qdrant collection '{self.cfg.collection_name}' with dim={vector_dim}")
                self.client.create_collection(
                    collection_name=self.cfg.collection_name,
                    vectors_config=rest.VectorParams(
                        size=vector_dim,
                        distance=rest.Distance.COSINE
                    ),
                )
            else:
                logger.info(f"Collection '{self.cfg.collection_name}' already exists")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")
            raise

    def upsert(self, embeddings: List[List[float]], payloads: List[Dict[str, Any]]):
        try:
            if not embeddings or not payloads:
                raise ValueError("No embeddings or payloads provided for upsert")

            vector_dim = len(embeddings[0])
            logger.info(f"Upserting {len(embeddings)} vectors (dim={vector_dim}) into '{self.cfg.collection_name}'")
            logger.debug(f"First payload sample: {payloads[0]}")

            self.ensure_collection(vector_dim)

            points = [
                rest.PointStruct(id=i, vector=embeddings[i], payload=payloads[i])
                for i in range(len(embeddings))
            ]
            self.client.upsert(collection_name=self.cfg.collection_name, points=points)
            logger.info(f"Upsert completed for {len(points)} points.")
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            raise

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            if not query_vector:
                raise ValueError("Query vector is empty")

            logger.info(f"Searching top {top_k} in '{self.cfg.collection_name}' (dim={len(query_vector)})")
            results = self.client.search(
                collection_name=self.cfg.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )
            logger.debug(f"Search results: {results}")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
