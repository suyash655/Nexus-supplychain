"""
NEXUS Agent — State Schema
============================
TypedDict that flows through every node of the LangGraph agent.
All fields are optional so partial updates work cleanly.
"""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    # ── Input ──────────────────────────────────────────────────────────────
    question:        str          # original user question
    mode:            str          # "ask" | "what_if"
    supplier_filter: Optional[str]  # extracted supplier name for RAG pre-filter

    # ── Live supply chain context (injected at call time) ──────────────────
    risk_scores:  List[Dict[str, Any]]
    anomalies:    Dict[str, Any]
    summary:      Dict[str, Any]
    graph_data:   Optional[Dict[str, Any]]

    # ── RAG results ────────────────────────────────────────────────────────
    retrieved_chunks: List[Dict[str, Any]]   # [{text, doc_name, rrf_score, rerank_score}]

    # ── LLM output ─────────────────────────────────────────────────────────
    answer:   str
    sources:  List[Dict[str, Any]]   # [{doc_name, excerpt, relevance_score}]

    # ── Routing / control ──────────────────────────────────────────────────
    error:    Optional[str]
    provider: str
