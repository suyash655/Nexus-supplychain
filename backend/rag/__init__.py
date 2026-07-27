"""
NEXUS RAG package.
Public API:
    from rag.ingest    import ingest_all, ingest_file, get_collection_stats
    from rag.retriever import get_retriever
    from rag.reranker  import rerank
"""
from .ingest    import ingest_all, ingest_file, get_collection_stats
from .retriever import get_retriever
from .reranker  import rerank

__all__ = ["ingest_all", "ingest_file", "get_collection_stats", "get_retriever", "rerank"]
