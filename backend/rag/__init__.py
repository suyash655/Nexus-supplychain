"""
NEXUS RAG package.
Public API:
    from rag.ingest    import ingest_all, ingest_file, get_collection_stats
    from rag.retriever import get_retriever
    from rag.reranker  import rerank
"""
from .ingest import get_collection_stats, ingest_all, ingest_file
from .reranker import rerank
from .retriever import get_retriever

__all__ = ["ingest_all", "ingest_file", "get_collection_stats", "get_retriever", "rerank"]
