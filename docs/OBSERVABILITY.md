# Agent Observability and Tracing

NEXUS implements structured JSON node-level logging and optional integration with [Langfuse](https://langfuse.com) for production agent telemetry.

---

## 1. Structured Node Logging

Every node in the mitigation agent (`get_backup_suppliers`, `simulate_reroute_cost`, `retrieve_context`, `draft_action`, `write_pending_action`, `execute_action`) records structured telemetry.

### JSON Log Format
```json
{
  "timestamp": 1711234567.89,
  "run_id": "c7a8b9d0-1234-4567-89ab-cdef01234567",
  "node": "draft_action",
  "latency_ms": 420,
  "status": "success",
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "prompt_tokens": 850,
  "completion_tokens": 180,
  "total_tokens": 1030,
  "cost_usd": 0.000644,
  "input_summary": {"supplier": "Apex Materials", "trigger_score": 82.5},
  "output_summary": {"action_type": "dual_source", "confidence": 0.85}
}
```

---

## 2. Token Usage and Cost Computation

Cost is computed strictly from verified API pricing and actual token counts returned by the upstream provider. When token counts are unavailable (e.g. mock runs or unmetered streams), cost is recorded as `null` rather than estimated.

| Model / Provider | Input Pricing ($ / 1M tokens) | Output Pricing ($ / 1M tokens) |
| :--- | :--- | :--- |
| **Groq (`llama-3.3-70b-versatile`)** | \$0.59 | \$0.79 |
| **AWS Bedrock (`amazon.nova-lite-v1:0`)** | \$0.06 | \$0.24 |
| **Offline Heuristic Mode** | \$0.00 | \$0.00 |

---

## 3. Optional Langfuse Integration

Langfuse provides distributed trace visualization, latency waterfall charts, and token cost aggregation.

### Enabling Langfuse
Set the following environment variables in `backend/.env`:
```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # or self-hosted endpoint
```

If these keys are not set, the observability module runs in **zero-overhead no-op mode** with no external network calls.
