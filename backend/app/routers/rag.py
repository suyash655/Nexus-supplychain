from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_auth
from app.rag.ingestion import build_index_from_postgres
from app.rag.agent import build_nexus_agent
import json
import logging

logger = logging.getLogger("nexus.rag")

router = APIRouter(prefix="/api/rag", tags=["rag"])

class RAGQuery(BaseModel):
    question: str
    tenant_id: str
    session_id: str | None = None

@router.post("/query")
async def rag_query(payload: RAGQuery, db = Depends(get_db), user: dict = Depends(require_auth)):
    # 1. Fetch recent events for this tenant from DB
    from sqlalchemy import text
    # Make sure we're querying synchronously or asynchronously based on the DB setup
    # In this app `get_db` yields a standard Session, so we execute synchronously
    result = db.execute(
        text("SELECT * FROM supply_chain_events WHERE tenant_id = :tid ORDER BY timestamp DESC LIMIT 500"),
        {"tid": payload.tenant_id},
    )
    events = [dict(row._mapping) for row in result]

    # 2. Build index from events
    index = await build_index_from_postgres(events)

    # 3. Build agent
    from app.main import engines
    bci = engines.causal_engine
    
    if bci is None:
        logger.warning("Causal engine not available. Agent will not be able to perform root cause analysis.")
        
    agent = build_nexus_agent(index, bci)

    # 4. Query
    try:
        response = agent.chat(payload.question)
        return {
            "answer": str(response),
            "sources": [n.text[:200] for n in response.source_nodes] if hasattr(response, 'source_nodes') else [],
            "session_id": payload.session_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG agent error: {str(e)}")

@router.post("/query/stream")
async def rag_query_stream(payload: RAGQuery, db = Depends(get_db), user: dict = Depends(require_auth)):
    """Streaming version — tokens arrive in real time to the frontend."""
    # 1. Fetch recent events
    from sqlalchemy import text
    result = db.execute(
        text("SELECT * FROM supply_chain_events WHERE tenant_id = :tid ORDER BY timestamp DESC LIMIT 500"),
        {"tid": payload.tenant_id},
    )
    events = [dict(row._mapping) for row in result]

    # 2. Build index
    index = await build_index_from_postgres(events)

    # 3. Build agent
    from app.main import engines
    bci = engines.causal_engine
    agent = build_nexus_agent(index, bci)
    
    async def generate():
        yield f"data: {json.dumps({'type': 'start'})}\n\n"
        try:
            # stream_chat provides a streaming response object in LlamaIndex
            response = agent.stream_chat(payload.question)
            for token in response.response_gen:
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as e:
             yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
             
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
    return StreamingResponse(generate(), media_type="text/event-stream")
