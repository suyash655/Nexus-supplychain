"""
NEXUS — Agent Action & Trace Models
=====================================
Two tables:
  agent_actions  — one row per proposed mitigation action, with status lifecycle
  agent_traces   — append-only log of every tool call made during an agent run
"""

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text

from app.models.base import Base, _utcnow


class AgentAction(Base):
    """
    A mitigation action proposed by the agentic pipeline.

    Lifecycle:  awaiting_approval → approved → executed
                                 → rejected

    The frontend renders one approval card per row with status=awaiting_approval.
    Clicking "Approve" calls POST /agent/approve/{id}.
    """
    __tablename__ = "agent_actions"

    id              = Column(Integer, primary_key=True, index=True)
    run_id          = Column(String, index=True)        # groups nodes from one agent run
    supplier_name   = Column(String, index=True)
    sku             = Column(String, nullable=True)
    risk_score      = Column(Float)
    trigger_reason  = Column(String)                   # e.g. "risk_score > 75"

    # Proposed action
    action_type     = Column(String)                   # "dual_source" | "increase_safety_stock" | "escalate"
    action_summary  = Column(Text)                     # 1-2 sentence human-readable description
    action_detail   = Column(JSON)                     # full structured payload

    # Alternatives evaluated
    backup_suppliers     = Column(JSON, nullable=True)  # [{supplier, risk_score, capacity_note}]
    reroute_cost_estimate= Column(Float, nullable=True)
    rag_context          = Column(JSON, nullable=True)  # [{doc_name, excerpt, relevance_score}]

    # LLM reasoning trace
    llm_reasoning   = Column(Text, nullable=True)      # raw LLM output

    # Status
    status          = Column(String, default="awaiting_approval", index=True)
    approved_by     = Column(String, nullable=True)
    approved_at     = Column(DateTime, nullable=True)
    rejected_reason = Column(Text, nullable=True)

    # Execution result (filled after approve)
    execution_log   = Column(Text, nullable=True)
    executed_at     = Column(DateTime, nullable=True)

    created_at      = Column(DateTime, default=_utcnow)


class AgentTrace(Base):
    """
    Append-only tool-call log — one row per tool invocation.
    Displayed on the /agent-traces frontend page.
    """
    __tablename__ = "agent_traces"

    id          = Column(Integer, primary_key=True, index=True)
    run_id      = Column(String, index=True)
    step        = Column(Integer)                  # 0-based step index within run
    node_name   = Column(String)                   # LangGraph node name
    tool_name   = Column(String)                   # function called
    input_json  = Column(JSON)
    output_json = Column(JSON)
    duration_ms = Column(Integer, nullable=True)
    created_at  = Column(DateTime, default=_utcnow)
