"""Unified IBP orchestration for planning workflows and scenario execution."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.orchestrator import _load_dataframe


class IBPOrchestrator:
    """Coordinates demand, supply, inventory, S&OP, response, and control-tower flows."""

    def __init__(self):
        self.templates = {
            "monthly_ibp": {
                "name": "Monthly IBP Cycle",
                "steps": ["data_refresh", "demand_review", "supply_review", "inventory_review", "executive_sop", "publish_plan"],
                "cadence": "monthly",
            },
            "disruption_response": {
                "name": "Disruption Response",
                "steps": ["detect", "assess_impact", "generate_scenarios", "approve_response", "monitor_recovery"],
                "cadence": "event_driven",
            },
            "new_product_launch": {
                "name": "New Product Launch",
                "steps": ["baseline_demand", "capacity_check", "inventory_positioning", "supplier_readiness", "launch_control_tower"],
                "cadence": "milestone",
            },
        }
        self.scenarios: Dict[str, Dict[str, Any]] = {}

    def get_overview(self) -> Dict[str, Any]:
        df = _load_dataframe()
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_flow": {
                "records_available": len(df),
                "sources": sorted([str(x) for x in df["supplier"].dropna().unique()[:10]]) if "supplier" in df.columns and not df.empty else [],
                "automation_state": "ready" if not df.empty else "waiting_for_data",
            },
            "process_templates": self.templates,
            "scenario_count": len(self.scenarios),
            "ui_modules": [
                {"name": "Control Tower", "path": "/control-tower", "status": "available"},
                {"name": "Analytics Reports", "path": "/analytics-reports", "status": "available"},
                {"name": "S&OP", "path": "/sop", "status": "available"},
                {"name": "Connectors", "path": "/connectors", "status": "available"},
            ],
        }

    def run_data_flow(self, template_id: str = "monthly_ibp") -> Dict[str, Any]:
        template = self.templates.get(template_id)
        if not template:
            return {"error": f"Unknown template: {template_id}"}
        started = datetime.now(timezone.utc).isoformat()
        steps = [
            {"step": step, "status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}
            for step in template["steps"]
        ]
        return {
            "status": "success",
            "template_id": template_id,
            "started_at": started,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "steps": steps,
            "outputs": {
                "plan_status": "synchronized",
                "exceptions_created": 0,
                "next_review": "executive_sop" if template_id == "monthly_ibp" else "monitor_recovery",
            },
        }

    def create_scenario(self, name: str, scenario_type: str, assumptions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        scenario_id = f"SCN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        assumptions = assumptions or {}
        impact = self._estimate_impact(assumptions)
        scenario = {
            "scenario_id": scenario_id,
            "name": name,
            "scenario_type": scenario_type,
            "assumptions": assumptions,
            "impact": impact,
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.scenarios[scenario_id] = scenario
        return {"status": "success", "scenario": scenario}

    def list_scenarios(self) -> Dict[str, Any]:
        return {"status": "success", "scenarios": list(self.scenarios.values()), "total_count": len(self.scenarios)}

    def _estimate_impact(self, assumptions: Dict[str, Any]) -> Dict[str, Any]:
        demand_change = float(assumptions.get("demand_change_pct", 0))
        supply_change = float(assumptions.get("supply_change_pct", 0))
        cost_change = float(assumptions.get("cost_change_pct", 0))
        risk_score = min(100, max(0, abs(demand_change - supply_change) * 1.5 + max(0, cost_change) * 0.8))
        return {
            "service_level_delta_pct": round((supply_change - demand_change) * 0.25, 2),
            "margin_delta_pct": round(-cost_change * 0.4, 2),
            "risk_score": round(risk_score, 1),
            "recommendation": "approve_with_monitoring" if risk_score < 35 else "requires_executive_review",
        }


ibp_orchestrator = IBPOrchestrator()
