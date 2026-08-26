"""
NEXUS Agent — Phase 1.2: Agentic Mitigation Loop
==================================================
Triggered when a supplier's risk score crosses the CRITICAL threshold (≥70).

6-node LangGraph pipeline:

  Node 1 — get_backup_suppliers
    Wraps the existing Graph Engine to find alternate suppliers
    serving the same SKUs as the at-risk supplier.

  Node 2 — simulate_reroute_cost
    Wraps the Monte Carlo Engine to estimate the cost/delay impact
    of switching volume to each backup candidate.

  Node 3 — retrieve_relevant_context
    Calls the RAG hybrid retriever for SLA terms, incident history,
    and escalation playbook sections relevant to this supplier.

  Node 4 — draft_mitigation_action
    Calls Groq (or Gemini fallback) with all gathered context.
    Returns structured JSON: action_type, summary, detail, rationale.

  Node 5 — write_pending_action
    Persists the draft to the `pending_actions` table with
    status="awaiting_approval". Also writes every node's I/O to
    `agent_traces` for the observability page.

  Node 6 — execute_action  (called only after human approval)
    Logs a mock PO / notification. Does NOT call any external API —
    safe for demo. Returns an execution receipt.

Usage:
    from agent.mitigation_graph import trigger_mitigation, approve_action

    # Called from orchestrator after risk scoring:
    run_id = trigger_mitigation(supplier="Apex Materials", risk_score=78, ...)

    # Called from POST /mitigation/approve/{action_id}:
    result = approve_action(action_id=42, approved_by="procurement@acme.com")
"""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

logger = logging.getLogger("nexus.agent.mitigation")

# ── Risk threshold above which the loop fires ─────────────────────────────
CRITICAL_THRESHOLD = 70.0


# ── State ──────────────────────────────────────────────────────────────────

class MitigationState(TypedDict, total=False):
    # Trigger context
    run_id:        str
    supplier:      str
    sku:           Optional[str]
    trigger_score: float
    risk_data:     Dict[str, Any]     # full risk scorer output for this supplier
    graph_data:    Optional[Dict]     # cached graph visualization

    # Node 1 output
    backup_suppliers: List[Dict[str, Any]]

    # Node 2 output
    monte_carlo_summary: Dict[str, Any]

    # Node 3 output
    rag_context: List[Dict[str, Any]]

    # Node 4 output
    action_type:    str
    action_summary: str
    action_detail:  Dict[str, Any]
    llm_reasoning:  str

    # Node 5 output
    pending_action_id: int

    # Trace accumulator
    traces: List[Dict[str, Any]]
    error:  Optional[str]


# ── Trace helper ───────────────────────────────────────────────────────────

def _trace(state: MitigationState, step: int, node: str,
           inp: Any, out: Any, ms: int, error: Optional[str] = None) -> MitigationState:
    entry = {
        "run_id":    state["run_id"],
        "step":      step,
        "node_name": node,
        "input":     inp,
        "output":    out,
        "duration_ms": ms,
        "error":     error,
    }
    traces = list(state.get("traces", []))
    traces.append(entry)
    return {**state, "traces": traces}


# ── Node 1: Get backup suppliers ───────────────────────────────────────────

def node_get_backup_suppliers(state: MitigationState) -> MitigationState:
    """
    Find alternate suppliers that cover the same SKUs as the at-risk supplier.
    Uses the graph analysis results already stored in the DB (no re-computation).
    """
    t0 = time.time()
    supplier    = state.get("supplier", "")
    graph_data  = state.get("graph_data") or {}
    risk_data   = state.get("risk_data", {})

    backups: List[Dict[str, Any]] = []

    try:
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        # Find all SKU nodes that this supplier feeds
        supplier_node_id = None
        supplier_cost = 0
        for n in nodes:
            if n.get("type") == "supplier" and supplier.lower() in n.get("name", "").lower():
                supplier_node_id = n.get("id")
                supplier_cost = n.get("total_cost", 0)
                break

        if supplier_node_id:
            # SKUs sourced by this supplier
            target_skus = {
                e["target"] for e in edges
                if e.get("source") == supplier_node_id
                and e.get("edge_type") == "supplies"
            }

            # Other suppliers that source the same SKUs
            alt_supplier_ids = {
                e["source"] for e in edges
                if e.get("target") in target_skus
                and e.get("edge_type") == "supplies"
                and e.get("source") != supplier_node_id
            }

            # Enrich with risk scores (lower = better for a backup)
            for nid in alt_supplier_ids:
                for n in nodes:
                    if n.get("id") == nid:
                        backups.append({
                            "supplier_id":           nid,
                            "name":                  n.get("name", nid),
                            "avg_delay":             n.get("avg_delay", 0),
                            "total_cost":            n.get("total_cost", 0),
                            "estimated_cost_delta":  f"{round((n.get('total_cost', 0) - supplier_cost) / max(supplier_cost, 1) * 100, 1)}%" if supplier_cost else None,
                            "shared_sku_count":      sum(
                                1 for e in edges
                                if e.get("source") == nid and e.get("target") in target_skus
                            ),
                        })

        # Sort by avg_delay ascending (least delayed first)
        backups.sort(key=lambda x: x.get("avg_delay", 999))

    except Exception as e:
        logger.error("node_get_backup_suppliers error: %s", e)
        state = {**state, "error": str(e)}

    ms = int((time.time() - t0) * 1000)
    state = _trace(state, 1, "get_backup_suppliers",
                   {"supplier": supplier}, {"backup_count": len(backups)}, ms)
    return {**state, "backup_suppliers": backups[:4]}  # top-4 alternatives


# ── Node 2: Simulate reroute cost ──────────────────────────────────────────

def node_simulate_reroute_cost(state: MitigationState) -> MitigationState:
    """
    Use Monte Carlo engine to estimate P50/P90 cost and delay impact of
    switching 30% of volume to backup suppliers.
    """
    t0 = time.time()
    backups = state.get("backup_suppliers", [])
    summary: Dict[str, Any] = {}

    try:
        from app.main import engines  # type: ignore
        mc = engines.monte_carlo_engine

        if mc and mc._fitted and backups:
            candidates = [b["name"] for b in backups[:2]]
            result = mc.simulate_disruption(
                target_suppliers=candidates,
                disruption_severity=0.3,   # 30% volume shift = moderate disruption
                num_trials=500,
            )
            agg = result.get("aggregate", {})
            summary = {
                "p50_delay_days":  agg.get("total_delay", {}).get("p50_median", "N/A"),
                "p90_delay_days":  agg.get("total_delay", {}).get("p90", "N/A"),
                "p50_cost_impact": agg.get("total_cost_exposure", {}).get("p50_median", "N/A"),
                "p90_cost_impact": agg.get("total_cost_exposure", {}).get("p90", "N/A"),
                "system_risk_score": agg.get("system_risk_score", "N/A"),
                "candidates_simulated": candidates,
            }
        else:
            # MC not fitted or no backups — provide conservative estimates
            # TODO: implement fallback calculation when MC is not fitted
            summary = {
                "p50_delay_days":    None,
                "p90_delay_days":    None,
                "p50_cost_impact":   None,
                "p90_cost_impact":   None,
                "system_risk_score": None,
                "note": "Estimate — Monte Carlo not fitted; upload data to improve",
            }

    except Exception as e:
        logger.error("node_simulate_reroute_cost error: %s", e)
        summary = {"error": str(e)}

    ms = int((time.time() - t0) * 1000)
    state = _trace(state, 2, "simulate_reroute_cost",
                   {"backup_count": len(backups)}, summary, ms)
    return {**state, "monte_carlo_summary": summary}


# ── Node 3: Retrieve relevant context ─────────────────────────────────────

def node_retrieve_context(state: MitigationState) -> MitigationState:
    """
    Hybrid RAG retrieval for SLA terms, incident reports, and escalation
    playbook sections relevant to this supplier.
    """
    t0 = time.time()
    supplier = state.get("supplier", "")
    score    = state.get("trigger_score", 0)

    query = (
        f"What are the SLA terms, penalty clauses, and escalation procedures "
        f"for supplier {supplier} with risk score {score:.0f}?"
    )
    chunks: List[Dict[str, Any]] = []

    try:
        from agent.tools import retrieve_documents  # type: ignore
        chunks = retrieve_documents(query, supplier_filter=supplier, top_k=3)
        logger.info("RAG: %d chunks for supplier=%s", len(chunks), supplier)
    except Exception as e:
        logger.warning("node_retrieve_context RAG unavailable: %s", e)

    ms = int((time.time() - t0) * 1000)
    state = _trace(state, 3, "retrieve_relevant_context",
                   {"query": query[:80]}, {"chunks_retrieved": len(chunks)}, ms)
    return {**state, "rag_context": chunks}


# ── Node 4: Draft mitigation action ───────────────────────────────────────

_MITIGATION_SYSTEM = """You are NEXUS, an autonomous supply chain risk mitigation agent.
Given a supplier risk alert with supporting context, draft a specific mitigation action.

Output ONLY valid JSON in this exact schema — no prose, no markdown:
{
  "action_type": "dual_source" | "reroute" | "safety_stock" | "alert_only",
  "summary": "One sentence describing the action",
  "rationale": "2-3 sentences explaining why this action and not others",
  "steps": ["Step 1...", "Step 2...", "Step 3..."],
  "estimated_cost_impact": "string e.g. +8% procurement premium",
  "estimated_risk_reduction": "string e.g. Risk score drop from 78 → 52",
  "urgency": "immediate" | "within_48h" | "this_week",
  "confidence": 0.0–1.0
}"""


def node_draft_action(state: MitigationState) -> MitigationState:
    """
    Call Groq (Gemini fallback) to draft a structured mitigation action
    from all gathered context. Returns clean JSON.
    """
    t0 = time.time()

    supplier  = state.get("supplier", "")
    score     = state.get("trigger_score", 0)
    backups   = state.get("backup_suppliers", [])
    mc        = state.get("monte_carlo_summary", {})
    chunks    = state.get("rag_context", [])
    risk_data = state.get("risk_data", {})

    # Build context block
    doc_ctx = ""
    if chunks:
        doc_ctx = "\n## RELEVANT DOCUMENTS\n"
        for c in chunks:
            doc_ctx += f"[{c['doc_name']}] {c['text'][:300]}\n---\n"

    backup_ctx = ""
    if backups:
        backup_ctx = "\n## AVAILABLE BACKUP SUPPLIERS\n"
        for b in backups[:3]:
            backup_ctx += (
                f"- {b['name']}: avg_delay={b.get('avg_delay', '?')}d, "
                f"shared_skus={b.get('shared_sku_count', '?')}, "
                f"est_cost_delta={b.get('estimated_cost_delta', '?')}\n"
            )

    prompt = (
        f"## RISK ALERT\n"
        f"Supplier: {supplier}\n"
        f"Risk score: {score:.1f}/100 (CRITICAL threshold: 70)\n"
        f"Avg delay: {risk_data.get('avg_delay', '?')} days\n"
        f"Tier: {risk_data.get('tier', '?')}\n"
        f"Total shipments: {risk_data.get('total_shipments', '?')}\n"
        f"\n## MONTE CARLO SIMULATION\n{json.dumps(mc, default=str)}"
        f"{backup_ctx}"
        f"{doc_ctx}"
        f"\nDraft the optimal mitigation action as JSON."
    )

    from app.core.config import settings  # type: ignore
    from agent.agent_graph import _call_llm  # type: ignore

    raw = _call_llm(
        prompt=prompt,
        system_prompt=_MITIGATION_SYSTEM,
        groq_key=settings.GROQ_API_KEY,
        groq_model=settings.GROQ_MODEL,
    )

    # Parse JSON from LLM response
    action_detail: Dict[str, Any] = {}
    action_type   = "alert_only"
    action_summary = f"Risk alert: {supplier} crossed critical threshold ({score:.0f}/100)"
    llm_reasoning = raw or ""

    if raw:
        try:
            import re
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                action_detail  = parsed
                action_type    = parsed.get("action_type", "alert_only")
                action_summary = parsed.get("summary", action_summary)
        except Exception as e:
            logger.warning("Failed to parse LLM JSON: %s", e)

    # Offline fallback when no LLM
    if not action_detail:
        action_type    = "dual_source" if backups else "alert_only"
        action_summary = (
            f"Initiate dual-sourcing for {supplier} — risk score {score:.0f} exceeds critical threshold"
            if backups else
            f"Escalate monitoring for {supplier} — risk score {score:.0f}/100"
        )
        action_detail = {
            "action_type":              action_type,
            "summary":                  action_summary,
            "rationale":                "Offline mode: LLM not configured. Using heuristic recommendation.",
            "steps":                    [
                f"Notify procurement team of {supplier} risk status",
                f"Issue RFQ to {backups[0]['name'] if backups else 'alternate suppliers'}",
                "Increase safety stock by 14 days for affected SKUs",
            ],
            "estimated_cost_impact":    "+8–15%",
            "estimated_risk_reduction": f"Risk score {score:.0f} → ~50",
            "urgency":                  "within_48h",
            "confidence":               0.6,
        }

    ms = int((time.time() - t0) * 1000)
    state = _trace(state, 4, "draft_mitigation_action",
                   {"prompt_length": len(prompt)},
                   {"action_type": action_type, "confidence": action_detail.get("confidence", 0)},
                   ms)
    return {
        **state,
        "action_type":    action_type,
        "action_summary": action_summary,
        "action_detail":  action_detail,
        "llm_reasoning":  llm_reasoning,
    }


# ── Node 5: Write pending action ───────────────────────────────────────────

def node_write_pending_action(state: MitigationState) -> MitigationState:
    """
    Persist the draft action to `pending_actions` (status="awaiting_approval")
    and write all trace steps to `agent_traces`.
    """
    t0 = time.time()

    try:
        from app.core.database import SessionLocal  # type: ignore
        from app.models.supply import PendingAction  # type: ignore
        from app.models.agent_actions import AgentTrace  # type: ignore

        db = SessionLocal()
        try:
            # Persist pending action
            pa = PendingAction(
                run_id              = state["run_id"],
                supplier            = state.get("supplier", ""),
                sku                 = state.get("sku"),
                trigger_score       = state.get("trigger_score", 0),
                action_type         = state.get("action_type", "alert_only"),
                action_summary      = state.get("action_summary", ""),
                action_detail       = state.get("action_detail"),
                backup_suppliers    = state.get("backup_suppliers"),
                monte_carlo_summary = state.get("monte_carlo_summary"),
                rag_context         = [
                    {"doc_name": c["doc_name"], "excerpt": c["text"][:200]}
                    for c in state.get("rag_context", [])
                ],
                llm_reasoning       = state.get("llm_reasoning", ""),
                status              = "awaiting_approval",
            )
            db.add(pa)
            db.flush()  # get pa.id before commit
            action_id = pa.id

            # Persist traces
            for t in state.get("traces", []):
                at = AgentTrace(
                    run_id     = t["run_id"],
                    step       = t["step"],
                    node_name  = t["node_name"],
                    input_json = t.get("input"),
                    output_json= t.get("output"),
                    duration_ms= t.get("duration_ms"),
                    error      = t.get("error"),
                )
                db.add(at)

            db.commit()
            logger.info("Pending action #%d written for supplier=%s", action_id, state.get("supplier"))

        finally:
            db.close()

    except Exception as e:
        logger.error("node_write_pending_action error: %s", e)
        action_id = -1
        state = {**state, "error": str(e)}

    ms = int((time.time() - t0) * 1000)
    state = _trace(state, 5, "write_pending_action",
                   {"status": "awaiting_approval"}, {"action_id": action_id}, ms)
    return {**state, "pending_action_id": action_id}


# ── Node 6: Execute approved action ───────────────────────────────────────

def node_execute_action(action_id: int, approved_by: str) -> Dict[str, Any]:
    """
    Called ONLY after human approval via POST /mitigation/approve/{action_id}.

    Logs a mock PO / procurement notification — no external API calls.
    Returns an execution receipt.
    """
    # =========================================================================
    # MOCK EXECUTION MODE
    # The email addresses (e.g. procurement@nexus.ai) and execution steps below
    # are placeholders for demonstration purposes. They do not trigger real
    # external systems or emails.
    # =========================================================================
    try:
        from app.core.database import SessionLocal  # type: ignore
        from app.models.supply import PendingAction  # type: ignore

        db = SessionLocal()
        try:
            pa = db.query(PendingAction).filter(PendingAction.id == action_id).first()
            if not pa:
                return {"error": f"Action #{action_id} not found"}
            if pa.status != "awaiting_approval":
                return {"error": f"Action #{action_id} is already {pa.status}"}

            # ── Mock execution ────────────────────────────────────────────
            detail = pa.action_detail or {}
            action_type = pa.action_type

            if action_type == "dual_source":
                backups = pa.backup_suppliers or []
                top_backup = backups[0]["name"] if backups else "Alternate Supplier TBD"
                receipt = {
                    "action":  "dual_source",
                    "po_reference": f"PO-{uuid.uuid4().hex[:8].upper()}",
                    "message": f"Mock PO issued to {top_backup} for 30% volume of {pa.supplier} SKUs.",
                    "notified": ["procurement@nexus.ai", "coo@nexus.ai"],
                }

            elif action_type == "reroute":
                receipt = {
                    "action":  "reroute",
                    "reference": f"RT-{uuid.uuid4().hex[:8].upper()}",
                    "message": f"Shipment rerouting instruction logged for {pa.supplier}.",
                    "notified": ["logistics@nexus.ai"],
                }

            elif action_type == "safety_stock":
                receipt = {
                    "action":  "safety_stock",
                    "reference": f"SS-{uuid.uuid4().hex[:8].upper()}",
                    "message": f"Safety stock increase directive sent for {pa.supplier} SKUs.",
                    "notified": ["warehouse@nexus.ai"],
                }

            else:
                receipt = {
                    "action":  "alert_logged",
                    "reference": f"AL-{uuid.uuid4().hex[:8].upper()}",
                    "message": f"Escalation alert logged for {pa.supplier}.",
                    "notified": ["supply-ops@nexus.ai"],
                }

            # Update DB record
            pa.status       = "executed"
            pa.approved_by  = approved_by
            pa.approved_at  = datetime.now(timezone.utc)
            pa.executed_at  = datetime.now(timezone.utc)
            pa.execution_log = json.dumps(receipt)
            db.commit()

            logger.info("Action #%d executed by %s", action_id, approved_by)
            return {"status": "executed", "action_id": action_id, "receipt": receipt}

        finally:
            db.close()

    except Exception as e:
        logger.error("node_execute_action error: %s", e)
        return {"error": str(e)}


# ── Graph assembly ─────────────────────────────────────────────────────────

def _build_mitigation_graph():
    try:
        from langgraph.graph import StateGraph, END  # type: ignore

        g = StateGraph(MitigationState)
        g.add_node("get_backup_suppliers",  node_get_backup_suppliers)
        g.add_node("simulate_reroute_cost", node_simulate_reroute_cost)
        g.add_node("retrieve_context",      node_retrieve_context)
        g.add_node("draft_action",          node_draft_action)
        g.add_node("write_pending_action",  node_write_pending_action)

        g.set_entry_point("get_backup_suppliers")
        g.add_edge("get_backup_suppliers",  "simulate_reroute_cost")
        g.add_edge("simulate_reroute_cost", "retrieve_context")
        g.add_edge("retrieve_context",      "draft_action")
        g.add_edge("draft_action",          "write_pending_action")
        g.add_edge("write_pending_action",  END)

        compiled = g.compile()
        logger.info("Mitigation LangGraph compiled")
        return compiled
    except ImportError as e:
        logger.warning("LangGraph unavailable (%s) — sequential fallback", e)
        return None


_MITIGATION_GRAPH = None


def _get_graph():
    global _MITIGATION_GRAPH
    if _MITIGATION_GRAPH is None:
        _MITIGATION_GRAPH = _build_mitigation_graph()
    return _MITIGATION_GRAPH


# ── Public API ─────────────────────────────────────────────────────────────

def trigger_mitigation(
    supplier:   str,
    risk_score: float,
    risk_data:  Dict[str, Any],
    graph_data: Optional[Dict[str, Any]] = None,
    sku:        Optional[str] = None,
) -> Optional[int]:
    """
    Fire the agentic mitigation loop for a supplier that crossed the threshold.
    Returns the new PendingAction.id, or None on failure.
    Called from the analysis orchestrator.
    """
    if risk_score < CRITICAL_THRESHOLD:
        return None

    run_id = str(uuid.uuid4())
    logger.info("Mitigation triggered: run_id=%s supplier=%s score=%.1f",
                run_id, supplier, risk_score)

    initial: MitigationState = {
        "run_id":        run_id,
        "supplier":      supplier,
        "sku":           sku,
        "trigger_score": risk_score,
        "risk_data":     risk_data,
        "graph_data":    graph_data,
        "backup_suppliers": [],
        "monte_carlo_summary": {},
        "rag_context":   [],
        "action_type":   "",
        "action_summary":"",
        "action_detail": {},
        "llm_reasoning": "",
        "pending_action_id": -1,
        "traces":        [],
        "error":         None,
    }

    graph = _get_graph()
    if graph is not None:
        try:
            result = graph.invoke(initial)
            return dict(result).get("pending_action_id")
        except Exception as e:
            logger.error("LangGraph invoke failed: %s — sequential fallback", e)

    # Sequential fallback
    state = dict(initial)
    for fn in [
        node_get_backup_suppliers,
        node_simulate_reroute_cost,
        node_retrieve_context,
        node_draft_action,
        node_write_pending_action,
    ]:
        try:
            state = fn(state)
        except Exception as e:
            logger.error("Node %s failed: %s", fn.__name__, e)
            state["error"] = str(e)
            break

    return state.get("pending_action_id")


def approve_action(action_id: int, approved_by: str) -> Dict[str, Any]:
    """Human-gate: approve and execute a pending action."""
    return node_execute_action(action_id, approved_by)


def reject_action(action_id: int, rejected_by: str, reason: str = "") -> Dict[str, Any]:
    """Human-gate: reject a pending action."""
    try:
        from app.core.database import SessionLocal  # type: ignore
        from app.models.supply import PendingAction  # type: ignore

        db = SessionLocal()
        try:
            pa = db.query(PendingAction).filter(PendingAction.id == action_id).first()
            if not pa:
                return {"error": f"Action #{action_id} not found"}
            pa.status      = "rejected"
            pa.approved_by = rejected_by
            pa.approved_at = datetime.now(timezone.utc)
            pa.execution_log = json.dumps({"reason": reason})
            db.commit()
            return {"status": "rejected", "action_id": action_id}
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e)}
