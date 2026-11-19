"""
NEXUS RAG — Hybrid Retriever
==============================
Combines:
  1. Dense vector search  (ChromaDB + all-MiniLM-L6-v2)
  2. BM25 sparse search   (rank_bm25, exact keyword matching)

Merges results with Reciprocal Rank Fusion (RRF), then passes top-N to the
reranker for final ordering.

Why hybrid:
  - Vector search catches semantic matches ("force majeure" ↔ "act of God")
  - BM25 catches exact terms ("INC-2024-007", "clause 4.2", "SLA §3")
  - Neither alone is sufficient for enterprise document retrieval
"""

import logging
from typing import Any, Dict, List, Optional

from .ingest import _get_chroma, _get_embedder

logger = logging.getLogger("nexus.rag.retriever")

# Returned per chunk
class RetrievedChunk:
    def __init__(
        self,
        text: str,
        doc_name: str,
        chunk_index: int,
        vector_rank: Optional[int],
        bm25_rank: Optional[int],
        rrf_score: float,
    ):
        self.text        = text
        self.doc_name    = doc_name
        self.chunk_index = chunk_index
        self.vector_rank = vector_rank
        self.bm25_rank   = bm25_rank
        self.rrf_score   = rrf_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text":        self.text,
            "doc_name":    self.doc_name,
            "chunk_index": self.chunk_index,
            "rrf_score":   round(self.rrf_score, 4),
        }


def _rrf(vector_ids: List[str], bm25_ids: List[str], k: int = 60) -> Dict[str, float]:
    """
    Reciprocal Rank Fusion.
    score(id) = 1/(k + rank_vector) + 1/(k + rank_bm25)
    """
    scores: Dict[str, float] = {}
    for rank, cid in enumerate(vector_ids, start=1):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    for rank, cid in enumerate(bm25_ids, start=1):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    return scores


class HybridRetriever:
    """
    Lazy-loaded retriever. First call initialises ChromaDB + embedder + BM25 index.
    BM25 index is rebuilt on first retrieval and cached in memory.
    """

    def __init__(self, top_k_per_source: int = 8, final_top_k: int = 6):
        self.top_k         = top_k_per_source
        self.final_top_k   = final_top_k
        self._collection   = None
        self._embedder     = None
        self._bm25         = None
        self._bm25_docs: List[str]  = []
        self._bm25_ids:  List[str]  = []
        self._bm25_metas: List[Dict] = []

    def _ensure_loaded(self):
        if self._collection is None:
            self._collection = _get_chroma()
            self._embedder   = _get_embedder()
        if self._bm25 is None:
            self._build_bm25_index()

    def _build_bm25_index(self):
        """Pull all documents from Chroma and build an in-memory BM25 index."""
        try:
            from rank_bm25 import BM25Okapi  # type: ignore
            count = self._collection.count()
            if count == 0:
                logger.warning("ChromaDB is empty — run rag.ingest first")
                self._bm25 = None
                return

            # Fetch everything (cap at 10K for safety)
            result = self._collection.get(limit=min(count, 10_000))
            self._bm25_docs  = result["documents"] or []
            self._bm25_ids   = result["ids"]        or []
            self._bm25_metas = result["metadatas"]  or []

            tokenized = [doc.lower().split() for doc in self._bm25_docs]
            self._bm25 = BM25Okapi(tokenized)
            logger.info("BM25 index built: %d documents", len(self._bm25_docs))
        except Exception as e:
            logger.error("BM25 index build failed: %s", e)
            self._bm25 = None

    def retrieve(
        self,
        query: str,
        supplier_filter: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        """
        Retrieve top chunks for a query using hybrid search + RRF fusion.

        Args:
            query:           The user question or search phrase.
            supplier_filter: Optional supplier name to pre-filter results.
                             Matched as substring of doc_name (case-insensitive).
        """
        self._ensure_loaded()

        if self._collection is None or self._collection.count() == 0:
            logger.warning("No documents in vector store. Returning empty results.")
            return []

        # ── 1. Vector search ───────────────────────────────────────────────
        query_emb = self._embedder.encode([query]).tolist()
        if supplier_filter:
            # ChromaDB doesn't support substring match — filter post-retrieval
            pass

        try:
            vec_result = self._collection.query(
                query_embeddings=query_emb,
                n_results=min(self.top_k * 2, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )
            vec_ids   = vec_result["ids"][0]       if vec_result["ids"]       else []
            vec_docs  = vec_result["documents"][0]  if vec_result["documents"] else []
            vec_metas = vec_result["metadatas"][0]  if vec_result["metadatas"] else []
        except Exception as e:
            logger.error("Vector search failed: %s", e)
            vec_ids, vec_docs, vec_metas = [], [], []

        # ── 2. BM25 search ─────────────────────────────────────────────────
        bm25_ids: List[str] = []
        if self._bm25 is not None:
            try:
                scores = self._bm25.get_scores(query.lower().split())
                top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
                bm25_ids = [self._bm25_ids[i] for i in top_idx[:self.top_k * 2]]
            except Exception as e:
                logger.error("BM25 search failed: %s", e)

        # ── 3. RRF fusion ──────────────────────────────────────────────────
        rrf_scores = _rrf(vec_ids, bm25_ids)

        # Build id → chunk lookup
        id_to_chunk: Dict[str, Dict] = {}
        for cid, doc, meta in zip(vec_ids, vec_docs, vec_metas):
            id_to_chunk[cid] = {"text": doc, "meta": meta or {}}
        for i, cid in enumerate(self._bm25_ids):
            if cid not in id_to_chunk:
                id_to_chunk[cid] = {
                    "text": self._bm25_docs[i] if i < len(self._bm25_docs) else "",
                    "meta": self._bm25_metas[i] if i < len(self._bm25_metas) else {},
                }

        # Sort by RRF score
        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        chunks: List[RetrievedChunk] = []
        for cid, rrf_score in ranked[:self.final_top_k * 2]:
            chunk = id_to_chunk.get(cid, {})
            meta  = chunk.get("meta", {})
            text  = chunk.get("text", "")

            if not text:
                continue

            doc_name = meta.get("doc_name", "unknown")

            # Optional supplier filter (post-retrieval substring match)
            supplier_match = bool(supplier_filter and supplier_filter.lower() in (text + doc_name).lower())

            vec_rank  = vec_ids.index(cid) + 1  if cid in vec_ids  else None
            bm25_rank = bm25_ids.index(cid) + 1 if cid in bm25_ids else None

            chunk_obj = RetrievedChunk(
                text=text,
                doc_name=doc_name,
                chunk_index=meta.get("chunk_index", 0),
                vector_rank=vec_rank,
                bm25_rank=bm25_rank,
                rrf_score=rrf_score,
            )
            chunk_obj.supplier_match = supplier_match
            chunks.append(chunk_obj)

        return chunks[:self.final_top_k]

    def invalidate_bm25(self):
        """Call after ingesting new documents to rebuild the BM25 index."""
        self._bm25 = None


# Module-level singleton — shared across requests
_retriever: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever(top_k_per_source=8, final_top_k=6)
    return _retriever
