"""
NEXUS RAG — Cross-Encoder Reranker
=====================================
Takes the top-N chunks from hybrid retrieval and reranks them with a
cross-encoder model (local, CPU-only, zero API cost).

Model: cross-encoder/ms-marco-MiniLM-L-6-v2
  - 22MB download on first run
  - ~50ms per (query, chunk) pair on CPU
  - Significantly outperforms bi-encoder similarity for final ranking

Falls back to RRF order if cross-encoder is unavailable.
"""

import logging
from typing import List

logger = logging.getLogger("nexus.rag.reranker")


def rerank(query: str, chunks: list, top_k: int = 3) -> list:
    """
    Rerank a list of RetrievedChunk objects using a cross-encoder.

    Returns the top_k chunks sorted by cross-encoder relevance score (highest first).
    Each returned chunk gets a `rerank_score` attribute added.
    Falls back to original RRF order if cross-encoder fails.
    """
    if not chunks:
        return []

    if len(chunks) <= top_k:
        # Nothing to rerank
        for c in chunks:
            c.rerank_score = c.rrf_score
        return chunks

    try:
        from sentence_transformers import CrossEncoder  # type: ignore

        model = _get_cross_encoder()
        pairs = [(query, c.text) for c in chunks]
        scores = model.predict(pairs, show_progress_bar=False)

        for chunk, score in zip(chunks, scores):
            chunk.rerank_score = float(score)

        reranked = sorted(chunks, key=lambda c: c.rerank_score, reverse=True)
        logger.debug("Reranked %d → %d chunks for query: %s…", len(chunks), top_k, query[:40])
        return reranked[:top_k]

    except Exception as e:
        logger.warning("Cross-encoder rerank failed (%s) — using RRF order", e)
        for c in chunks:
            c.rerank_score = c.rrf_score
        return chunks[:top_k]


# ── Model singleton ────────────────────────────────────────────────────────

_cross_encoder = None


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder  # type: ignore
        _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        logger.info("Cross-encoder loaded: cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _cross_encoder
