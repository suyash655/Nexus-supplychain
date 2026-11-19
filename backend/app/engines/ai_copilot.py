"""
NEXUS — AI Co-Pilot
=====================
AI-driven insights, executive summaries, and natural language querying.
Supports multiple LLM providers: Groq (free), AWS Bedrock, or offline heuristics.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx  # type: ignore

from app.core.config import settings  # type: ignore

logger = logging.getLogger("nexus.copilot")


class AICopilot:
    """AI engine for generating summaries and answering user queries."""

    SYSTEM_PROMPT = (
        "You are NEXUS, an expert supply chain intelligence analyst. "
        "You provide concise, data-driven insights based on the operational data provided. "
        "Always reference specific numbers and suppliers from the context. "
        "Format responses in clean markdown with bullet points and bold key findings. "
        "Keep responses under 400 words."
    )

    def __init__(self):
        self.provider = settings.LLM_PROVIDER  # groq, bedrock, offline
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL

        # Bedrock setup (optional fallback)
        self.bedrock: Any = None
        self.has_bedrock = False
        if self.provider == "bedrock" or (self.provider == "groq" and not self.groq_api_key):
            try:
                import boto3  # type: ignore
                self.bedrock = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=settings.AWS_REGION,
                )
                self.has_bedrock = True
            except Exception as e:
                logger.error("[NEXUS] Bedrock initialization failed: %s", e)

        # Determine active provider
        if self.groq_api_key and self.provider in ("groq", "auto"):
            self._active_provider = "groq"
        elif self.has_bedrock:
            self._active_provider = "bedrock"
        else:
            self._active_provider = "offline"

        # Log a clear, actionable warning if no LLM is configured
        if self._active_provider == "offline":
            logger.warning(
                "[NEXUS] AI Copilot running in OFFLINE mode — no LLM available. "
                "Set GROQ_API_KEY in backend/.env to enable AI responses. "
                "Get a free key at https://console.groq.com"
            )
        else:
            logger.info("[NEXUS] AI Copilot initialized — provider: %s", self._active_provider)

    @property
    def is_online(self) -> bool:
        return self._active_provider in ("groq", "bedrock")

    def get_provider_info(self) -> Dict[str, Any]:
        """Return info about the active LLM provider."""
        return {
            "active_provider": self._active_provider,
            "groq_configured": bool(self.groq_api_key),
            "bedrock_configured": self.has_bedrock,
            "model": self.groq_model if self._active_provider == "groq" else settings.BEDROCK_MODEL_ID,
            "status": "online" if self.is_online else "offline (heuristic mode)",
        }

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the active LLM provider with a prompt."""
        sys_prompt = system_prompt or self.SYSTEM_PROMPT

        if self._active_provider == "groq":
            return self._call_groq(prompt, sys_prompt)
        elif self._active_provider == "bedrock":
            return self._call_bedrock(prompt, sys_prompt)
        return ""

    def _call_groq(self, prompt: str, system_prompt: str) -> str:
        """Call Groq API (free tier: Llama 3.3 70B, Mixtral, etc.)."""
        try:
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.3,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("[NEXUS] Groq API call failed: %s", e)
            # Fallback to bedrock if available
            if self.has_bedrock:
                return self._call_bedrock(prompt, system_prompt)
            return ""

    def _call_bedrock(self, prompt: str, system_prompt: str) -> str:
        """Call Amazon Bedrock with a prompt."""
        if not self.has_bedrock or not self.bedrock:
            return ""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
                "system": system_prompt,
            })
            response = self.bedrock.invoke_model(
                body=body,
                modelId=settings.BEDROCK_MODEL_ID,
                accept="application/json",
                contentType="application/json",
            )
            response_body = json.loads(response.get("body").read())
            return response_body.get("content", [{}])[0].get("text", "")
        except Exception as e:
            logger.error("[NEXUS] Bedrock call failed: %s", e)
            return ""

    def generate_executive_summary(
        self, summary: Dict[str, Any], risk_scores: List[Dict[str, Any]], anomalies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a high-level executive summary using LLM reasoning."""
        avg_risk = 0.0
        if risk_scores:
            avg_risk = sum(float(s.get("risk_score", 0)) for s in risk_scores) / len(risk_scores)
        anomaly_count = int(anomalies.get("anomaly_count", 0))

        # Build concise prompt
        if self.is_online:
            top_risks = json.dumps(risk_scores[:5], default=str) if risk_scores else "[]"  # type: ignore
            top_anomalies = json.dumps(anomalies.get("anomalies", [])[:5], default=str)
            prompt = (
                f"## Supply Chain Data\n"
                f"- Total records: {summary.get('total_records', 0)}\n"
                f"- Suppliers: {summary.get('unique_suppliers', 0)}\n"
                f"- Avg delay: {summary.get('avg_delay_days', 0)} days\n"
                f"- Delayed shipments: {summary.get('delayed_shipments_pct', 0)}%\n"
                f"- Avg quality: {summary.get('avg_quality', 'N/A')}\n\n"
                f"## Top Risk Suppliers\n{top_risks}\n\n"
                f"## Anomalies ({anomaly_count} total)\n{top_anomalies}\n\n"
                f"Provide:\n"
                f"1. A 2-3 sentence executive narrative\n"
                f"2. Top 3 prioritized recommendations with estimated impact\n"
                f"Format as clean markdown."
            )
            narrative = self._call_llm(prompt)
            if not narrative:
                narrative = self._heuristic_narrative(summary, avg_risk, anomaly_count)
        else:
            narrative = self._heuristic_narrative(summary, avg_risk, anomaly_count)

        # Risk level determination
        if avg_risk > 60 or anomaly_count > 10:
            risk_level, risk_color = "CRITICAL", "#ef4444"
        elif avg_risk > 30 or anomaly_count > 3:
            risk_level, risk_color = "ELEVATED", "#f59e0b"
        else:
            risk_level, risk_color = "STABLE", "#22c55e"

        # Extract structured recommendations
        recommendations = self._extract_recommendations(narrative, risk_scores)

        return {
            "overall_risk_level": risk_level,
            "risk_color": risk_color,
            "narrative": narrative,
            "recommendations": recommendations,
            "key_metrics": {
                "avg_risk_score": round(float(avg_risk), 1),  # type: ignore
                "anomaly_rate": round(float(anomaly_count / max(summary.get("total_records", 1), 1) * 100), 2),  # type: ignore
            },
            "provider": self._active_provider,
        }

    def _heuristic_narrative(self, summary: Dict, avg_risk: float, anomaly_count: int) -> str:
        """Generate a data-driven narrative without LLM."""
        total = summary.get("total_records", 0)
        suppliers = summary.get("unique_suppliers", 0)
        avg_delay = summary.get("avg_delay_days", 0)
        delayed_pct = summary.get("delayed_shipments_pct", 0)

        parts = [f"Analysis of **{total:,}** shipment records across **{suppliers}** suppliers reveals "]
        if avg_risk > 60:
            parts.append(f"**critical risk levels** (avg score: {avg_risk:.1f}/100). ")
        elif avg_risk > 30:
            parts.append(f"**elevated risk** (avg score: {avg_risk:.1f}/100). ")
        else:
            parts.append(f"**stable operations** (avg score: {avg_risk:.1f}/100). ")

        if delayed_pct > 30:
            parts.append(f"**{delayed_pct:.0f}%** of shipments experienced delays (avg: {avg_delay:.1f} days). ")
        elif delayed_pct > 0:
            parts.append(f"{delayed_pct:.0f}% of shipments were delayed, averaging {avg_delay:.1f} days. ")

        if anomaly_count > 0:
            parts.append(f"Detected **{anomaly_count}** anomalies requiring attention.")

        return "".join(parts)

    def _extract_recommendations(self, narrative: str, risk_scores: Optional[List[Dict[str, Any]]] = None) -> List[Dict]:
        """Try to extract recommendations from LLM output, fall back to defaults."""
        defaults = []
        if risk_scores and len(risk_scores) > 0:
            top_risk = risk_scores[0]
            defaults.append({
                "priority": "high",
                "action": f"Review {top_risk.get('supplier', 'Top Supplier')}",
                "detail": f"Address elevated risk score of {top_risk.get('risk_score', 'unknown')}.",
                "estimated_impact": "+10% Resilience"
            })
            if len(risk_scores) > 1:
                second_risk = risk_scores[1]
                defaults.append({
                    "priority": "medium",
                    "action": f"Diversify {second_risk.get('supplier', 'Supplier')}",
                    "detail": "Reduce dependency to mitigate ripple effects.",
                    "estimated_impact": "-15% Risk Exposure"
                })
        if not defaults:
            defaults = [
                {"priority": "high", "action": "Review Critical Suppliers", "detail": "Focus on top-risk suppliers with elevated delay patterns.", "estimated_impact": "+10% Resilience"},
                {"priority": "medium", "action": "Diversify Supply Base", "detail": "Reduce single-supplier dependencies for critical SKUs.", "estimated_impact": "-15% Risk Exposure"},
            ]
        try:
            json_match = re.search(r"\[.*\]", narrative, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
        except Exception:
            pass
        return defaults

    def answer_question(
        self, question: str, risk_scores: List[Dict[str, Any]], anomalies: Dict[str, Any],
        summary: Dict[str, Any], graph_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Answer a natural language question using LLM."""
        if self.is_online:
            context = (
                f"## Current Supply Chain State\n"
                f"Summary: {json.dumps(summary, default=str)}\n"
                f"Top 10 Suppliers by Risk: {json.dumps(risk_scores[:10], default=str)}\n"  # type: ignore
                f"Network: {json.dumps(graph_data, default=str) if graph_data else 'Not available'}\n\n"
                f"## Question\n{question}\n\n"
                f"Answer based ONLY on the data above. Be specific and cite numbers."
            )
            answer = self._call_llm(context)
        else:
            answer = (
                "I'm running in **Heuristic Mode** (no LLM configured).\n\n"
                "To enable AI-powered responses, add your Groq API key to `.env`:\n"
                "```\nGROQ_API_KEY=gsk_your_key_here\n```\n"
                "Get a free key at [console.groq.com](https://console.groq.com)"
            )

        return {
            "question": question,
            "answer": answer,
            "confidence": None,  # TODO: Implement dynamic confidence scoring based on retrieval quality
            "sources": [self._active_provider, "NEXUS Analytics"],
            "provider": self._active_provider,
        }

    def what_if_simulation(
        self, scenario: str, risk_scores: List[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]], summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate a what-if scenario using LLM reasoning."""
        if self.is_online:
            context = (
                f"## Scenario\n{scenario}\n\n"
                f"## Current Network\n{json.dumps(graph_data, default=str) if graph_data else 'N/A'}\n"
                f"## Current Risks\n{json.dumps(risk_scores[:5], default=str)}\n\n"  # type: ignore
                f"Analyze ripple effects on suppliers, warehouses, and SKUs. "
                f"Identify most vulnerable nodes and suggest 3 specific mitigations."
            )
            analysis = self._call_llm(context)
        else:
            analysis = "What-if simulation requires an active LLM. Configure Groq API key in `.env`."

        return {
            "scenario": scenario,
            "impact_analysis": analysis,
            "recommendation": "See analysis for specific mitigation steps.",
            "confidence_score": None,  # TODO: Implement dynamic confidence scoring based on retrieval quality
            "provider": self._active_provider,
        }

    def analyze_world_events(
        self, world_events: List[Dict[str, Any]], suppliers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze how world events impact the supplier base."""
        if not self.is_online:
            return {"impact_summary": "AI offline — cannot analyze world events.", "disrupted_suppliers": []}

        context = (
            f"## Active World Events\n{json.dumps(world_events, default=str)}\n\n"
            f"## Supplier Base (top 20)\n{json.dumps(suppliers[:20], default=str)}\n\n"  # type: ignore
            f"Identify which suppliers are at risk due to these events. "
            f"Return JSON: {{\"impact_summary\": \"...\", \"disrupted_suppliers\": [{{\"id\": \"...\", \"reason\": \"...\", \"risk_increment\": 15}}]}}"
        )

        res = self._call_llm(context)
        try:
            json_match = re.search(r"\{.*\}", res, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {"impact_summary": res or "Analysis unavailable.", "disrupted_suppliers": []}
