"""
NEXUS Agent — Tool Definitions
================================
Each function is a tool the agent can call. Tools are plain Python functions
wrapped by LangGraph nodes — no @tool decorator needed since we call them
directly inside graph nodes.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nexus.agent.tools")


# ── Tool 1: RAG Retrieval ──────────────────────────────────────────────────

def retrieve_documents(
    query: str,
    supplier_filter: Optional[str] = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Retrieve and rerank the most relevant document chunks for a query.
    Returns up to top_k chunks as dicts with text, doc_name, rerank_score.
    """
    try:
        from rag.reranker import rerank  # type: ignore
        from rag.retriever import get_retriever  # type: ignore

        retriever = get_retriever()
        raw = retriever.retrieve(query, supplier_filter=supplier_filter)
        reranked = rerank(query, raw, top_k=top_k)

        return [
            {
                "text":          c.text,
                "doc_name":      c.doc_name,
                "chunk_index":   c.chunk_index,
                "rerank_score":  round(getattr(c, "rerank_score", c.rrf_score), 4),
            }
            for c in reranked
        ]
    except Exception as e:
        logger.error("retrieve_documents failed: %s", e)
        return []


# ── Tool 2: Risk Score Lookup ──────────────────────────────────────────────

def get_supplier_risk(
    supplier_name: str,
    risk_scores: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Look up the current risk score and factors for a named supplier.
    Case-insensitive partial match.
    """
    name_lower = supplier_name.lower()
    for s in risk_scores:
        if name_lower in s.get("supplier", "").lower():
            return s
    return {"error": f"Supplier '{supplier_name}' not found in current risk data"}


# ── Tool 3: Top Anomalies ──────────────────────────────────────────────────

def get_top_anomalies(
    anomalies: Dict[str, Any],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Return the top N anomalies by risk_score from the current analysis."""
    items = anomalies.get("anomalies", [])
    sorted_items = sorted(items, key=lambda x: x.get("risk_score", 0), reverse=True)
    return sorted_items[:limit]


# ── Tool 4: Summary Formatter ──────────────────────────────────────────────

def format_supply_chain_context(
    summary: Dict[str, Any],
    risk_scores: List[Dict[str, Any]],
    anomalies: Dict[str, Any],
    top_n_suppliers: int = 5,
) -> str:
    """
    Build a compact, token-efficient context string from live data.
    This is injected into the LLM prompt alongside retrieved document chunks.
    """
    lines = [
        "## LIVE SUPPLY CHAIN METRICS",
        f"- Total shipments: {summary.get('total_records', 0):,}",
        f"- Unique suppliers: {summary.get('unique_suppliers', 0)}",
        f"- Avg delay: {summary.get('avg_delay_days', 0):.1f} days",
        f"- Delayed shipments: {summary.get('delayed_shipments_pct', 0):.1f}%",
        f"- Total cost: ${summary.get('total_cost', 0):,.0f}",
        "",
        "## TOP SUPPLIERS BY RISK SCORE",
    ]

    for s in risk_scores[:top_n_suppliers]:
        lines.append(
            f"- {s.get('supplier', 'Unknown')}: "
            f"score={s.get('risk_score', 0)}, "
            f"tier={s.get('tier', 'unknown')}, "
            f"avg_delay={s.get('avg_delay', 0)}d, "
            f"shipments={s.get('total_shipments', 0)}"
        )

    anomaly_count = anomalies.get("anomaly_count", 0)
    lines.append("")
    lines.append(f"## ANOMALIES: {anomaly_count} detected")

    top_anom = get_top_anomalies(anomalies, limit=3)
    for a in top_anom:
        lines.append(
            f"- {a.get('supplier', '?')} / {a.get('sku', '?')}: "
            f"type={a.get('type', '?')}, severity={a.get('severity', '?')}"
        )

    return "\n".join(lines)
