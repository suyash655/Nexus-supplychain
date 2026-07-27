"""
NEXUS Agent — LangGraph Agent Graph
======================================
A three-node graph:

  [extract_intent] → [retrieve_docs] → [generate_answer]

extract_intent:  parses the question to extract supplier names and mode
retrieve_docs:   calls hybrid RAG + reranker; skips if no doc store available
generate_answer: builds prompt from live data + retrieved chunks, calls LLM,
                 returns answer + structured citations

The graph is compiled once at module import and reused across requests.
"""

import json
import logging
import re
from typing import Any, Dict

logger = logging.getLogger("nexus.agent")


# ── LLM caller (with Groq primary, Gemini fallback) ────────────────────────

def _call_llm(prompt: str, system_prompt: str, groq_key: str, groq_model: str) -> str:
    """Call Groq; fall back to Gemini if Groq fails or key missing."""
    # ── Groq ──
    if groq_key:
        try:
            import httpx  # type: ignore
            resp = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": prompt},
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.3,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning("Groq call failed: %s — trying Gemini fallback", e)

    # ── Gemini fallback ──
    try:
        import os
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            return ""
        from google import genai  # type: ignore
        client = genai.Client(api_key=gemini_key)
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system_prompt}\n\n{prompt}",
        )
        return resp.text or ""
    except Exception as e:
        logger.error("Gemini fallback also failed: %s", e)
        return ""


# ── Node 1: Extract intent ─────────────────────────────────────────────────

def node_extract_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the question to detect:
    - supplier_filter: any supplier name mentioned (for RAG pre-filtering)
    - mode is already set by the caller
    """
    question = state.get("question", "")
    risk_scores = state.get("risk_scores", [])

    # Try to match a supplier name from the live risk scores
    supplier_filter = None
    q_lower = question.lower()
    for s in risk_scores:
        name = s.get("supplier", "")
        if name.lower() in q_lower:
            supplier_filter = name
            break

    logger.debug("intent: supplier_filter=%s", supplier_filter)
    return {**state, "supplier_filter": supplier_filter}


# ── Node 2: Retrieve documents ─────────────────────────────────────────────

def node_retrieve_docs(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hybrid retrieval + rerank. Gracefully returns empty list if RAG is unavailable.
    """
    question        = state.get("question", "")
    supplier_filter = state.get("supplier_filter")

    try:
        from agent.tools import retrieve_documents  # type: ignore
        chunks = retrieve_documents(question, supplier_filter=supplier_filter, top_k=3)
        logger.info("Retrieved %d chunks for: %s…", len(chunks), question[:50])
    except Exception as e:
        logger.warning("RAG retrieval skipped: %s", e)
        chunks = []

    return {**state, "retrieved_chunks": chunks}


# ── Node 3: Generate answer ────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are NEXUS, an expert supply chain intelligence analyst.
You answer questions using ONLY the data provided below (live metrics + retrieved documents).
Rules:
- Be concise and precise. Use bullet points for lists.
- Always cite specific numbers from the data.
- If a retrieved document chunk is relevant, reference it: e.g. "Per Apex_Materials_SLA.pdf, clause 3.1..."
- If the data does not contain enough information to answer, say so clearly — do not hallucinate.
- Keep responses under 350 words.
- Format in clean markdown."""

_WHATIF_SYSTEM = """You are NEXUS, an expert supply chain scenario analyst.
Given the current supply chain state and retrieved documents, analyse the described scenario.
Rules:
- Identify the 3 most affected suppliers/nodes and why.
- Propose 3 specific mitigations with estimated impact.
- Reference contract terms or SLA clauses where relevant.
- Keep response under 400 words. Use markdown."""


def node_generate_answer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a grounded prompt from live data + retrieved chunks, call LLM,
    parse the answer, and return structured citations.
    """
    from agent.tools import format_supply_chain_context  # type: ignore
    from app.core.config import settings  # type: ignore  (imported here to avoid circular)

    question = state.get("question", "")
    mode     = state.get("mode", "ask")
    chunks   = state.get("retrieved_chunks", [])

    # ── Build live data context ──
    live_ctx = format_supply_chain_context(
        summary     = state.get("summary", {}),
        risk_scores = state.get("risk_scores", []),
        anomalies   = state.get("anomalies", {}),
    )

    # ── Build document context with citations ──
    doc_ctx = ""
    if chunks:
        doc_ctx = "\n\n## RETRIEVED DOCUMENTS\n"
        for i, c in enumerate(chunks, 1):
            doc_ctx += (
                f"\n[{i}] Source: {c['doc_name']} (relevance: {c.get('rerank_score', 0):.2f})\n"
                f"{c['text']}\n"
                f"---"
            )

    # ── Assemble prompt ──
    if mode == "what_if":
        prompt = (
            f"## SCENARIO\n{question}\n\n"
            f"{live_ctx}"
            f"{doc_ctx}\n\n"
            "Analyse the scenario's ripple effects and propose mitigations."
        )
        sys_prompt = _WHATIF_SYSTEM
    else:
        prompt = (
            f"## QUESTION\n{question}\n\n"
            f"{live_ctx}"
            f"{doc_ctx}\n\n"
            "Answer the question based strictly on the data above."
        )
        sys_prompt = _SYSTEM_PROMPT

    # ── Call LLM ──
    answer = _call_llm(
        prompt=prompt,
        system_prompt=sys_prompt,
        groq_key=settings.GROQ_API_KEY,
        groq_model=settings.GROQ_MODEL,
    )

    if not answer:
        answer = _offline_answer(state)

    # ── Build citations ──
    sources = [
        {
            "doc_name":        c["doc_name"],
            "excerpt":         c["text"][:180].strip() + ("…" if len(c["text"]) > 180 else ""),
            "relevance_score": c.get("rerank_score", 0),
        }
        for c in chunks
    ]

    provider = settings.GROQ_API_KEY and "groq" or "offline"

    return {
        **state,
        "answer":   answer,
        "sources":  sources,
        "provider": provider,
    }


def _offline_answer(state: Dict[str, Any]) -> str:
    """Heuristic answer when no LLM is available."""
    risk_scores = state.get("risk_scores", [])
    summary     = state.get("summary", {})
    top3 = [s["supplier"] for s in risk_scores[:3]] if risk_scores else []
    return (
        f"**Offline Mode** — LLM not configured.\n\n"
        f"Current data: {summary.get('total_records', 0):,} shipments, "
        f"{summary.get('unique_suppliers', 0)} suppliers, "
        f"avg delay {summary.get('avg_delay_days', 0):.1f}d.\n\n"
        f"Top risk suppliers: {', '.join(top3) or 'none'}.\n\n"
        "Add `GROQ_API_KEY` to `.env` for AI-powered answers."
    )


# ── Graph compilation ──────────────────────────────────────────────────────

def build_graph():
    """Build and compile the LangGraph agent. Returns a compiled graph."""
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
        from agent.state import AgentState           # type: ignore

        g = StateGraph(AgentState)
        g.add_node("extract_intent",   node_extract_intent)
        g.add_node("retrieve_docs",    node_retrieve_docs)
        g.add_node("generate_answer",  node_generate_answer)

        g.set_entry_point("extract_intent")
        g.add_edge("extract_intent",  "retrieve_docs")
        g.add_edge("retrieve_docs",   "generate_answer")
        g.add_edge("generate_answer", END)

        compiled = g.compile()
        logger.info("LangGraph agent compiled successfully")
        return compiled

    except ImportError as e:
        logger.warning("LangGraph not available (%s) — using fallback sequential runner", e)
        return None


# Module-level compiled graph (None if LangGraph unavailable)
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_agent(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the agent. Uses LangGraph if available, falls back to sequential
    node execution if not (works with older langgraph or missing install).
    """
    graph = get_graph()

    if graph is not None:
        try:
            result = graph.invoke(initial_state)
            return dict(result)
        except Exception as e:
            logger.error("LangGraph invoke failed: %s — falling back to sequential", e)

    # Sequential fallback
    state = dict(initial_state)
    for node_fn in [node_extract_intent, node_retrieve_docs, node_generate_answer]:
        try:
            state = node_fn(state)
        except Exception as e:
            logger.error("Node %s failed: %s", node_fn.__name__, e)
            state["error"] = str(e)
            break

    return state
