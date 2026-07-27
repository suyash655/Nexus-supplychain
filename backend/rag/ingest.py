"""
NEXUS RAG — Document Ingestion
================================
Chunks documents, embeds with local sentence-transformers (all-MiniLM-L6-v2,
CPU-only, zero API cost), and stores in ChromaDB (file-backed, no extra infra).

Usage:
    python -m rag.ingest                    # ingest all docs in DATA_DIR
    python -m rag.ingest --file path/to/doc  # ingest single file

Collection is idempotent: re-ingesting the same file replaces its chunks.
"""

import os
import re
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("nexus.rag.ingest")

# Try to import pypdf for PDF support (graceful fallback if not installed)
try:
    from pypdf import PdfReader  # type: ignore
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    logger.warning("pypdf not installed — PDF files will be skipped. Install with: pip install pypdf")

# ── Paths ──────────────────────────────────────────────────────────────────
# Use the resolved absolute path of this file as the anchor.
# backend/rag/ingest.py → parent = backend/rag → parent = backend → parent = project root
_HERE      = Path(__file__).resolve().parent          # d:\supex1\backend\rag
_BACKEND   = _HERE.parent                              # d:\supex1\backend
_REPO_ROOT = _BACKEND.parent                           # d:\supex1
DATA_DIR   = _REPO_ROOT / "data" / "documents"
CHROMA_DIR = _REPO_ROOT / "data" / "chroma_db"

# ── Chunking config ────────────────────────────────────────────────────────
CHUNK_SIZE    = 400   # tokens (approx chars / 4)
CHUNK_OVERLAP = 80


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks on paragraph boundaries where possible.
    Falls back to character-level split.
    """
    paragraphs = re.split(r"\n{2,}", text.strip())
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) < chunk_size * 4:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            current = para

    if current:
        chunks.append(current)

    # If any chunk is still too large, split on sentences
    final: List[str] = []
    for chunk in chunks:
        if len(chunk) <= chunk_size * 5:
            final.append(chunk)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", chunk)
            buf = ""
            for sent in sentences:
                if len(buf) + len(sent) < chunk_size * 4:
                    buf = (buf + " " + sent).strip()
                else:
                    if buf:
                        final.append(buf)
                    buf = sent
            if buf:
                final.append(buf)

    return [c for c in final if c.strip()]


def _file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF file using pypdf."""
    if not HAS_PYPDF:
        raise ImportError("pypdf is not installed — cannot read PDF files")
    
    try:
        reader = PdfReader(path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.error("Failed to read PDF %s: %s", path, e)
        raise


def _get_chroma():
    """Return the ChromaDB collection, creating it on first call."""
    try:
        import chromadb  # type: ignore
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        return client.get_or_create_collection(
            name="nexus_documents",
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as e:
        logger.error("ChromaDB init failed: %s", e)
        raise


def _get_embedder():
    """Load local sentence-transformer (downloads ~90MB on first run)."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        logger.error("Sentence-transformer init failed: %s", e)
        raise


def ingest_file(path: Path, collection=None, embedder=None) -> int:
    """
    Ingest a single document. Returns number of chunks stored.
    Existing chunks for this file are deleted before re-ingesting (idempotent).
    """
    if collection is None:
        collection = _get_chroma()
    if embedder is None:
        embedder = _get_embedder()

    # Handle different file types
    if path.suffix.lower() == ".pdf":
        text = _read_pdf(path)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
    
    doc_name = path.name
    doc_id   = _file_hash(path)

    # Delete existing chunks for this document
    try:
        existing = collection.get(where={"doc_name": doc_name})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
            logger.info("Replaced %d existing chunks for %s", len(existing["ids"]), doc_name)
    except Exception:
        pass

    chunks = _chunk_text(text)
    if not chunks:
        logger.warning("No chunks produced for %s", doc_name)
        return 0

    embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()

    ids        = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas  = [
        {
            "doc_name":   doc_name,
            "doc_path":   str(path),
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    logger.info("Ingested %s → %d chunks", doc_name, len(chunks))
    return len(chunks)


def ingest_all(docs_dir: Path = DATA_DIR) -> Dict[str, int]:
    """Ingest all .txt, .md, .pdf files in docs_dir. Returns {filename: chunk_count}."""
    if not docs_dir.exists():
        logger.warning("Documents directory not found: %s", docs_dir)
        return {}

    collection = _get_chroma()
    embedder   = _get_embedder()
    results: Dict[str, int] = {}

    for path in sorted(docs_dir.iterdir()):
        if path.suffix.lower() in (".txt", ".md", ".pdf"):
            try:
                n = ingest_file(path, collection=collection, embedder=embedder)
                results[path.name] = n
            except Exception as e:
                logger.error("Failed to ingest %s: %s", path.name, e)
                results[path.name] = 0

    logger.info("Ingestion complete: %d documents, %d total chunks",
                len(results), sum(results.values()))
    return results


def get_collection_stats() -> Dict[str, Any]:
    """Return stats about the current vector store."""
    try:
        col = _get_chroma()
        count = col.count()
        docs = set()
        if count > 0:
            sample = col.get(limit=min(count, 1000))
            for m in sample.get("metadatas", []):
                if m:
                    docs.add(m.get("doc_name", "unknown"))
        return {"total_chunks": count, "documents": sorted(docs)}
    except Exception as e:
        return {"error": str(e), "total_chunks": 0, "documents": []}


# ── CLI entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Ingest documents into NEXUS RAG store")
    parser.add_argument("--file", type=Path, help="Ingest a single file instead of all")
    args = parser.parse_args()

    if args.file:
        n = ingest_file(args.file)
        print(f"Ingested {args.file.name}: {n} chunks")
    else:
        results = ingest_all()
        for fname, n in results.items():
            print(f"  {fname}: {n} chunks")
        print(f"Total: {sum(results.values())} chunks across {len(results)} documents")
