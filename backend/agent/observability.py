"""
NEXUS — Agent Observability and Tracing
=======================================
Provides structured JSON logging per agent node with execution latency, status,
token metrics, verifiable cost calculation, and optional Langfuse tracing.
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("nexus.agent.observability")

# Verified price table per 1,000,000 tokens (USD)
# Never fabricate: compute cost strictly from real usage data.
MODEL_PRICING = {
    # Groq Llama 3.3 70B
    "llama-3.3-70b-versatile": {
        "prompt_per_m": 0.59,
        "completion_per_m": 0.79,
    },
    # Amazon Nova Lite on Bedrock
    "amazon.nova-lite-v1:0": {
        "prompt_per_m": 0.06,
        "completion_per_m": 0.24,
    },
    # Offline deterministic mode has zero token cost
    "offline": {
        "prompt_per_m": 0.0,
        "completion_per_m": 0.0,
    },
}


def compute_token_cost(
    model: str,
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
) -> Optional[float]:
    """
    Compute USD cost from measured token counts using verified price tables.
    Returns None if token counts were not provided by the upstream LLM API.
    """
    if prompt_tokens is None and completion_tokens is None:
        return None

    pricing = MODEL_PRICING.get(model, MODEL_PRICING["offline"])
    p_tokens = prompt_tokens or 0
    c_tokens = completion_tokens or 0

    cost = (p_tokens / 1_000_000.0) * pricing["prompt_per_m"] + (c_tokens / 1_000_000.0) * pricing["completion_per_m"]
    return round(cost, 6)


class AgentObservability:
    """Singleton observability coordinator managing structured logs and optional Langfuse tracing."""

    def __init__(self):
        self._langfuse_client = None
        self._langfuse_enabled = False
        self._init_langfuse()

    def _init_langfuse(self):
        pub_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        sec_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if pub_key and sec_key:
            try:
                from langfuse import Langfuse  # type: ignore
                self._langfuse_client = Langfuse(
                    public_key=pub_key,
                    secret_key=sec_key,
                    host=host,
                )
                self._langfuse_enabled = True
                logger.info("[OBSERVABILITY] Langfuse tracing initialized with host: %s", host)
            except ImportError:
                logger.warning("[OBSERVABILITY] Langfuse keys present but 'langfuse' package is not installed; running in no-op mode.")
            except Exception as e:
                logger.warning("[OBSERVABILITY] Failed to initialize Langfuse client: %s", e)

    @property
    def is_langfuse_enabled(self) -> bool:
        return self._langfuse_enabled

    def record_node_execution(
        self,
        run_id: str,
        node_name: str,
        latency_ms: int,
        status: str = "success",
        provider: str = "offline",
        model: str = "offline",
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        input_summary: Optional[Dict[str, Any]] = None,
        output_summary: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a structured JSON execution event for an agent node.
        Outputs to application logs and passes to Langfuse if enabled.
        """
        cost_usd = compute_token_cost(model, prompt_tokens, completion_tokens)

        event = {
            "timestamp": time.time(),
            "run_id": run_id,
            "node": node_name,
            "latency_ms": latency_ms,
            "status": status,
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": (prompt_tokens or 0) + (completion_tokens or 0) if (prompt_tokens is not None or completion_tokens is not None) else None,
            "cost_usd": cost_usd,
            "input_summary": input_summary or {},
            "output_summary": output_summary or {},
            "error": error,
        }

        # Structured JSON log output
        log_line = json.dumps({k: v for k, v in event.items() if v is not None}, default=str)
        if status == "error":
            logger.error("[AGENT_NODE] %s", log_line)
        else:
            logger.info("[AGENT_NODE] %s", log_line)

        # Forward to Langfuse span if active
        if self._langfuse_enabled and self._langfuse_client:
            try:
                trace = self._langfuse_client.trace(id=run_id, name="nexus-mitigation-agent")
                trace.span(
                    name=node_name,
                    input=input_summary,
                    output=output_summary,
                    status_message=error,
                    level="ERROR" if status == "error" else "DEFAULT",
                    metadata={
                        "provider": provider,
                        "model": model,
                        "latency_ms": latency_ms,
                        "cost_usd": cost_usd,
                    },
                )
            except Exception as e:
                logger.debug("[OBSERVABILITY] Langfuse span logging failed: %s", e)

        return event


# Global observability singleton
agent_observer = AgentObservability()
