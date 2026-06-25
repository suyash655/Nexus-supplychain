"""
RAG document ingestion pipeline.
Ingests: PostgreSQL event logs, S3 PDFs, BCI graph outputs.
Chunks, embeds, and stores to vector index.
"""
import boto3  # type: ignore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings  # type: ignore
from llama_index.core.node_parser import SentenceSplitter  # type: ignore
from llama_index.llms.bedrock import Bedrock  # type: ignore
from llama_index.embeddings.bedrock import BedrockEmbedding  # type: ignore

# Configure LlamaIndex to use Bedrock globally
Settings.llm = Bedrock(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-east-1",
)
Settings.embed_model = BedrockEmbedding(
    model="amazon.titan-embed-text-v2:0",
    region_name="us-east-1",
)
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)

def build_index_from_s3(bucket: str, prefix: str = "documents/") -> VectorStoreIndex:
    """Download PDFs from S3, parse, embed, return index."""
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    local_dir = "/tmp/nexus_docs"
    import os; os.makedirs(local_dir, exist_ok=True)
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".pdf"):
                local_path = os.path.join(local_dir, os.path.basename(key))
                s3.download_file(bucket, key, local_path)
    docs = SimpleDirectoryReader(local_dir).load_data()
    return VectorStoreIndex.from_documents(docs)

async def build_index_from_postgres(db_events: list[dict]) -> VectorStoreIndex:
    """Convert supply chain events to documents and index them."""
    from llama_index.core import Document  # type: ignore
    documents = [
        Document(
            text=f"Event: {e['event_type']} | Supplier: {e['supplier_id']} | "
                 f"Timestamp: {e['timestamp']} | Severity: {e['severity']} | "
                 f"Notes: {e.get('notes', '')}",
            metadata={"supplier_id": e['supplier_id'], "event_type": e['event_type']},
        )
        for e in db_events
    ]
    return VectorStoreIndex.from_documents(documents)
