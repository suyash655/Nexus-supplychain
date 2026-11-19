"""
NEXUS — Response Planning Engine (SAP IBP-style)
================================================
What-if scenario analysis, real-time rebalancing,
and DDMRP (Demand-Driven Material Requirements Planning).
"""

import copy
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

logger_rp = logging.getLogger("nexus.response_planning")


class ScenarioType(Enum):
    """Types of planning scenarios."""
    DEMAND = "demand"
    SUPPLY = "supply"
    NETWORK = "network"
    FINANCIAL = "financial"
    CAPACITY = "capacity"
    GEOPOLITICAL = "geopolitical"
    CLIMATE = "climate"
    PANDEMIC = "pandemic"
    MARKET = "market"


@dataclass
class ScenarioParameter:
    """Parameter for scenario analysis."""
    name: str
    base_value: float
    min_value: float
    max_value: float
    distribution: str = "uniform"  # uniform, normal, triangular
    confidence_level: float = 0.95


class BufferZone(Enum):
    """DDMRP buffer zones."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class BufferProfile(Enum):
    """DDMRP buffer profiles."""
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"


class ReplenishmentTrigger(Enum):
    """DDMRP replenishment triggers."""
    NO_ACTION = "no_action"
    MONITOR = "monitor"
    ORDER_NOW = "order_now"
    EXPEDITE = "expedite"


class ResponsePlanningEngine:
    """
    Enterprise response planning with what-if analysis,
    real-time rebalancing, and DDMRP capabilities.
    """

    def __init__(self):
        self.scenarios = {}
        self.ddmrp_buffers = {}
        self.rebalancing_plan = {}
        self.monte_carlo_results = {}
        self.sensitivity_analysis = {}
        self._initialised = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize response planning with configuration.

        Args:
            config: Configuration dict with DDMRP and planning parameters
        """
        try:
            default_config = {
                "ddmrp": {
                    "green_zone_multiplier": 0.3,
                    "yellow_zone_multiplier": 0.5,
                    "red_zone_multiplier": 0.2,
                    "lead_time_factor": 1.5
                },
                "rebalancing": {
                    "max_transfer_distance": 500,  # km
                    "min_transfer_quantity": 100,
                    "transfer_cost_per_km": 0.5
                },
                "scenarios": {
                    "default_horizon": 12,  # weeks
                    "confidence_levels": [0.5, 0.7, 0.9],
                    "monte_carlo_iterations": 10000,
                    "sensitivity_step_size": 0.1
                }
            }

            config = config or default_config
            self.config = config

            self._initialised = True

            return {
                "status": "success",
                "ddmrp_configured": True,
                "rebalancing_configured": True,
                "initialised_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error initializing response planning: {e}")
            return {"error": str(e), "initialised": False}

    def create_what_if_scenario(self,
                                base_plan: Dict[str, Any],
                                scenario_changes: Dict[str, Any],
                                scenario_type: ScenarioType,
                                scenario_name: str) -> Dict[str, Any]:
        """
        Create what-if scenario for planning analysis.

        Args:
            base_plan: Base planning scenario (demand, supply, inventory)
            scenario_changes: Changes to apply to base plan
            scenario_type: Type of scenario (demand, supply, network, financial)
            scenario_name: Name for the scenario
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            # Apply scenario changes based on type
            modified_plan = self._apply_scenario_changes(base_plan, scenario_changes, scenario_type)

            # Calculate impact
            impact_analysis = self._calculate_scenario_impact(base_plan, modified_plan, scenario_type)

            # Store scenario
            scenario_id = f"SCENARIO-{scenario_type.value.upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

            self.scenarios[scenario_id] = {
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "scenario_type": scenario_type.value,
                "base_plan": base_plan,
                "modified_plan": modified_plan,
                "scenario_changes": scenario_changes,
                "impact_analysis": impact_analysis,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            return {
                "status": "success",
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "impact_analysis": impact_analysis,
                "modified_plan": modified_plan,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error creating what-if scenario: {e}")
            return {"error": str(e)}

    def _apply_scenario_changes(self, base_plan: Dict[str, Any],
                               changes: Dict[str, Any],
                               scenario_type: ScenarioType) -> Dict[str, Any]:
        """Apply scenario changes to base plan."""
        modified_plan = base_plan.copy()

        if scenario_type == ScenarioType.DEMAND:
            # Apply demand changes
            if "demand_multiplier" in changes:
                multiplier = changes["demand_multiplier"]
                for sku in modified_plan.get("demand_forecast", {}):
                    modified_plan["demand_forecast"][sku] = [
                        d * multiplier for d in modified_plan["demand_forecast"][sku]
                    ]

            if "sku_specific_changes" in changes:
                for sku, change in changes["sku_specific_changes"].items():
                    if sku in modified_plan.get("demand_forecast", {}):
                        modified_plan["demand_forecast"][sku] = [
                            d * change for d in modified_plan["demand_forecast"][sku]
                        ]

        elif scenario_type == ScenarioType.SUPPLY:
            # Apply supply changes
            if "capacity_changes" in changes:
                for resource, change in changes["capacity_changes"].items():
                    if "capacity_utilization" in modified_plan:
                        if resource in modified_plan["capacity_utilization"]:
                            old_capacity = modified_plan["capacity_utilization"][resource]["total_capacity"]
                            modified_plan["capacity_utilization"][resource]["total_capacity"] = old_capacity * change

            if "supplier_failures" in changes:
                failed_suppliers = changes["supplier_failures"]
                # Adjust production schedule to account for failed suppliers
                if "production_schedule" in modified_plan:
                    for sku in modified_plan["production_schedule"]:
                        for period in modified_plan["production_schedule"][sku]:
                            # Reduce production to account for supplier failures
                            period["production"] *= (1 - len(failed_suppliers) * 0.1)

        elif scenario_type == ScenarioType.NETWORK:
            # Apply network changes
            if "facility_closures" in changes:
                closures = changes["facility_closures"]
                # Redirect demand from closed facilities
                if "distribution_plan" in modified_plan:
                    for closure in closures:
                        # Logic to redistribute would go here
                        pass

        elif scenario_type == ScenarioType.FINANCIAL:
            # Apply financial changes
            if "cost_changes" in changes:
                for cost_type, change in changes["cost_changes"].items():
                    if "financials" in modified_plan:
                        if cost_type in modified_plan["financials"]:
                            modified_plan["financials"][cost_type] *= change

        elif scenario_type == ScenarioType.CAPACITY:
            # Apply capacity changes
            if "capacity_adjustments" in changes:
                for resource, adjustment in changes["capacity_adjustments"].items():
                    if "capacity_utilization" in modified_plan:
                        if resource in modified_plan["capacity_utilization"]:
                            old_capacity = modified_plan["capacity_utilization"][resource]["total_capacity"]
                            modified_plan["capacity_utilization"][resource]["total_capacity"] = old_capacity + adjustment

        return modified_plan

    def _calculate_scenario_impact(self, base_plan: Dict[str, Any],
                                 modified_plan: Dict[str, Any],
                                 scenario_type: ScenarioType) -> Dict[str, Any]:
        """Calculate impact of scenario changes."""
        impact = {
            "scenario_type": scenario_type.value,
            "metric_changes": {},
            "constraint_violations": [],
            "risk_assessment": {},
            "recommendations": []
        }

        # Calculate demand changes
        if "demand_forecast" in base_plan and "demand_forecast" in modified_plan:
            base_demand = sum(sum(d) for d in base_plan["demand_forecast"].values())
            modified_demand = sum(sum(d) for d in modified_plan["demand_forecast"].values())

            if base_demand > 0:
                demand_change_pct = ((modified_demand - base_demand) / base_demand) * 100
                impact["metric_changes"]["total_demand"] = {
                    "base": round(base_demand, 2),
                    "modified": round(modified_demand, 2),
                    "change": round(modified_demand - base_demand, 2),
                    "change_percentage": round(demand_change_pct, 2)
                }

        # Calculate capacity utilization changes
        if "capacity_utilization" in base_plan and "capacity_utilization" in modified_plan:
            capacity_changes = {}
            for resource in base_plan["capacity_utilization"]:
                base_util = base_plan["capacity_utilization"][resource]["utilization_percentage"]
                modified_util = modified_plan["capacity_utilization"][resource]["utilization_percentage"]

                capacity_changes[resource] = {
                    "base_utilization": base_util,
                    "modified_utilization": modified_util,
                    "change": round(modified_util - base_util, 2)
                }

                # Check for constraint violations
                if modified_util > 100:
                    impact["constraint_violations"].append({
                        "type": "capacity_overload",
                        "resource": resource,
                        "utilization": modified_util,
                        "severity": "CRITICAL" if modified_util > 110 else "HIGH"
                    })

            impact["metric_changes"]["capacity_utilization"] = capacity_changes

        # Risk assessment
        impact["risk_assessment"] = self._assess_scenario_risk(impact)

        # Generate recommendations
        impact["recommendations"] = self._generate_scenario_recommendations(impact)

        return impact

    def _assess_scenario_risk(self, impact: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level of scenario."""
        risk_factors = []

        # Demand volatility risk
        demand_change = impact.get("metric_changes", {}).get("total_demand", {}).get("change_percentage", 0)
        if abs(demand_change) > 30:
            risk_factors.append({
                "factor": "demand_volatility",
                "severity": "HIGH",
                "value": abs(demand_change)
            })

        # Capacity constraint risk
        violations = impact.get("constraint_violations", [])
        if violations:
            risk_factors.append({
                "factor": "capacity_constraints",
                "severity": "CRITICAL" if any(v["severity"] == "CRITICAL" for v in violations) else "HIGH",
                "count": len(violations)
            })

        # Overall risk assessment
        if risk_factors:
            overall_risk = "CRITICAL" if any(r["severity"] == "CRITICAL" for r in risk_factors) else "HIGH"
        else:
            overall_risk = "LOW"

        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "mitigation_required": overall_risk in ["HIGH", "CRITICAL"]
        }

    def _generate_scenario_recommendations(self, impact: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scenario impact."""
        recommendations = []

        # Demand-based recommendations
        demand_change = impact.get("metric_changes", {}).get("total_demand", {}).get("change_percentage", 0)
        if demand_change > 20:
            recommendations.append("Significant demand increase - consider capacity expansion")
        elif demand_change < -20:
            recommendations.append("Significant demand decrease - review production schedules")

        # Capacity-based recommendations
        violations = impact.get("constraint_violations", [])
        if violations:
            recommendations.append(f"Address {len(violations)} capacity constraint violations")

        # Risk-based recommendations
        risk_assessment = impact.get("risk_assessment", {})
        if risk_assessment.get("mitigation_required"):
            recommendations.append("Develop mitigation plan for identified risks")

        return recommendations

    def setup_ddmrp_buffers(self,
                           inventory_data: pd.DataFrame,
                           demand_profiles: Dict[str, Dict[str, float]],
                           lead_times: Dict[str, int],
                           buffer_profiles: Optional[Dict[str, BufferProfile]] = None,
                           on_order_inventory: Optional[Dict[str, float]] = None,
                           in_transit_inventory: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Setup DDMRP buffers for demand-driven replenishment with advanced features.

        Args:
            inventory_data: Current inventory data with sku, location, current_inventory
            demand_profiles: SKU -> {avg_daily_demand, demand_variability}
            lead_times: SKU -> lead time in days
            buffer_profiles: SKU -> buffer profile (strategic, tactical, operational)
            on_order_inventory: SKU -> quantity on order
            in_transit_inventory: SKU -> quantity in transit
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            ddmrp_config = self.config.get("ddmrp", {})
            green_multiplier = ddmrp_config.get("green_zone_multiplier", 0.3)
            yellow_multiplier = ddmrp_config.get("yellow_zone_multiplier", 0.5)
            red_multiplier = ddmrp_config.get("red_zone_multiplier", 0.2)
            lead_time_factor = ddmrp_config.get("lead_time_factor", 1.5)

            buffer_setup = {}

            for (sku, location), group in inventory_data.groupby(["sku", "location"]):
                current_inventory = group["current_inventory"].iloc[0] if "current_inventory" in group.columns else 0

                # Get demand profile
                profile = demand_profiles.get(sku, {})
                avg_demand = profile.get("avg_daily_demand", 10)
                demand_variability = profile.get("demand_variability", 0.2)

                lead_time = lead_times.get(sku, 7)

                # Get buffer profile
                buffer_profile = buffer_profiles.get(sku, BufferProfile.OPERATIONAL)

                # Adjust multipliers based on buffer profile
                profile_multipliers = self._get_buffer_profile_multipliers(buffer_profile)
                adjusted_green = green_multiplier * profile_multipliers["green"]
                adjusted_yellow = yellow_multiplier * profile_multipliers["yellow"]
                adjusted_red = red_multiplier * profile_multipliers["red"]

                # Calculate DDMRP components
                # Lead Time Demand (LTD)
                ltd = avg_demand * lead_time

                # Decoupled Lead Time Demand (DLTD)
                dltd = ltd * lead_time_factor

                # Buffer Zone Calculation with profile adjustments
                green_zone = dltd * adjusted_green
                yellow_zone = dltd * adjusted_yellow
                red_zone = dltd * adjusted_red

                # Buffer Top (Order point)
                buffer_top = green_zone + yellow_zone + red_zone

                # Buffer Bottom
                buffer_bottom = green_zone

                # Advanced Net Flow Position calculation
                on_order_qty = on_order_inventory.get(sku, 0) if on_order_inventory else 0
                in_transit_qty = in_transit_inventory.get(sku, 0) if in_transit_inventory else 0
                net_flow_position = current_inventory + on_order_qty + in_transit_qty

                # Determine current zone
                current_zone = self._determine_buffer_zone(net_flow_position, buffer_bottom, buffer_top)

                # Advanced replenishment trigger
                replenishment_trigger = self._determine_replenishment_trigger(
                    current_zone, net_flow_position, buffer_bottom, buffer_top
                )

                buffer_setup[f"{sku}_{location}"] = {
                    "sku": sku,
                    "location": location,
                    "current_inventory": current_inventory,
                    "on_order_inventory": on_order_qty,
                    "in_transit_inventory": in_transit_qty,
                    "net_flow_position": round(net_flow_position, 2),
                    "avg_daily_demand": round(avg_demand, 2),
                    "demand_variability": demand_variability,
                    "lead_time_days": lead_time,
                    "buffer_profile": buffer_profile.value,
                    "lead_time_demand": round(ltd, 2),
                    "decoupled_lead_time_demand": round(dltd, 2),
                    "buffer_top": round(buffer_top, 2),
                    "buffer_bottom": round(buffer_bottom, 2),
                    "green_zone": round(green_zone, 2),
                    "yellow_zone": round(yellow_zone, 2),
                    "red_zone": round(red_zone, 2),
                    "current_zone": current_zone.value,
                    "replenishment_trigger": replenishment_trigger.value,
                    "order_quantity": round(buffer_top, 2),
                    "suggested_order_qty": self._calculate_suggested_order_quantity(
                        replenishment_trigger, buffer_top, net_flow_position, avg_demand, lead_time
                    )
                }

            # Store buffer setup
            buffer_id = f"DDMRP-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.ddmrp_buffers[buffer_id] = {
                "buffer_id": buffer_id,
                "buffers": buffer_setup,
                "buffer_profiles_configured": buffer_profiles is not None,
                "advanced_net_flow_enabled": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            return {
                "status": "success",
                "buffer_id": buffer_id,
                "buffers": buffer_setup,
                "total_buffers": len(buffer_setup),
                "setup_summary": self._summarize_ddmrp_setup(buffer_setup),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error setting up DDMRP buffers: {e}")
            return {"error": str(e)}

    def _determine_buffer_zone(self, net_flow_position: float,
                              buffer_bottom: float,
                              buffer_top: float) -> BufferZone:
        """Determine current buffer zone based on net flow position."""
        if net_flow_position >= buffer_bottom:
            return BufferZone.GREEN
        elif net_flow_position >= buffer_bottom * 0.5:
            return BufferZone.YELLOW
        else:
            return BufferZone.RED

    def _get_reorder_status(self, zone: BufferZone) -> str:
        """Get reorder status based on buffer zone."""
        if zone == BufferZone.GREEN:
            return "NO_ACTION"
        elif zone == BufferZone.YELLOW:
            return "MONITOR"
        else:
            return "ORDER_NOW"

    def _get_buffer_profile_multipliers(self, profile: BufferProfile) -> Dict[str, float]:
        """Get zone multipliers based on buffer profile."""
        if profile == BufferProfile.STRATEGIC:
            # Strategic buffers: larger red zone for critical items
            return {"green": 0.25, "yellow": 0.45, "red": 0.30}
        elif profile == BufferProfile.TACTICAL:
            # Tactical buffers: balanced zones
            return {"green": 0.30, "yellow": 0.50, "red": 0.20}
        else:  # OPERATIONAL
            # Operational buffers: larger green zone for fast-moving items
            return {"green": 0.40, "yellow": 0.40, "red": 0.20}

    def _determine_replenishment_trigger(self,
                                         zone: BufferZone,
                                         net_flow_position: float,
                                         buffer_bottom: float,
                                         buffer_top: float) -> ReplenishmentTrigger:
        """Determine advanced replenishment trigger based on zone and position."""
        if zone == BufferZone.GREEN:
            return ReplenishmentTrigger.NO_ACTION
        elif zone == BufferZone.YELLOW:
            # Check if trending toward red
            if net_flow_position < buffer_bottom * 0.75:
                return ReplenishmentTrigger.ORDER_NOW
            else:
                return ReplenishmentTrigger.MONITOR
        else:  # RED zone
            # Check if critically low
            if net_flow_position < buffer_bottom * 0.25:
                return ReplenishmentTrigger.EXPEDITE
            else:
                return ReplenishmentTrigger.ORDER_NOW

    def _calculate_suggested_order_quantity(self,
                                           trigger: ReplenishmentTrigger,
                                           buffer_top: float,
                                           net_flow_position: float,
                                           avg_daily_demand: float,
                                           lead_time: int) -> float:
        """Calculate suggested order quantity based on trigger."""
        if trigger == ReplenishmentTrigger.NO_ACTION:
            return 0
        elif trigger == ReplenishmentTrigger.MONITOR:
            return 0
        elif trigger == ReplenishmentTrigger.ORDER_NOW:
            # Order up to buffer top
            return max(0, buffer_top - net_flow_position)
        else:  # EXPEDITE
            # Emergency order - smaller quantity but faster
            emergency_qty = avg_daily_demand * lead_time * 0.5
            return max(emergency_qty, buffer_top - net_flow_position)

    def _summarize_ddmrp_setup(self, buffer_setup: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize DDMRP buffer setup."""
        zone_counts = defaultdict(int)
        trigger_counts = defaultdict(int)
        profile_counts = defaultdict(int)

        for buffer_key, buffer_data in buffer_setup.items():
            zone_counts[buffer_data["current_zone"]] += 1
            trigger_counts[buffer_data.get("replenishment_trigger", "unknown")] += 1
            profile_counts[buffer_data.get("buffer_profile", "operational")] += 1

        return {
            "total_buffers": len(buffer_setup),
            "zone_distribution": dict(zone_counts),
            "trigger_distribution": dict(trigger_counts),
            "profile_distribution": dict(profile_counts),
            "buffers_requiring_action": zone_counts.get("red", 0),
            "buffers_to_monitor": zone_counts.get("yellow", 0),
            "healthy_buffers": zone_counts.get("green", 0),
            "expedite_required": trigger_counts.get("expedite", 0),
            "order_now_required": trigger_counts.get("order_now", 0)
        }

    def generate_demand_driven_replenishment_orders(self,
                                                   buffer_id: str,
                                                   current_inventory_updates: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Generate demand-driven replenishment orders based on current buffer status.

        Args:
            buffer_id: ID of the DDMRP buffer setup
            current_inventory_updates: Optional SKU -> current inventory updates
        """
        if buffer_id not in self.ddmrp_buffers:
            return {"error": "Buffer setup not found"}

        try:
            buffer_setup = self.ddmrp_buffers[buffer_id]["buffers"]
            replenishment_orders = []

            for buffer_key, buffer_data in buffer_setup.items():
                sku = buffer_data["sku"]
                location = buffer_data["location"]

                # Apply inventory updates if provided
                current_inventory = buffer_data["current_inventory"]
                if current_inventory_updates and sku in current_inventory_updates:
                    current_inventory = current_inventory_updates[sku]

                # Recalculate net flow position
                on_order = buffer_data.get("on_order_inventory", 0)
                in_transit = buffer_data.get("in_transit_inventory", 0)
                net_flow_position = current_inventory + on_order + in_transit

                # Get current trigger
                trigger_str = buffer_data.get("replenishment_trigger", "no_action")
                trigger = ReplenishmentTrigger(trigger_str) if isinstance(trigger_str, str) else trigger_str

                # Generate order if needed
                if trigger in [ReplenishmentTrigger.ORDER_NOW, ReplenishmentTrigger.EXPEDITE]:
                    order_qty = buffer_data.get("suggested_order_qty", 0)

                    if order_qty > 0:
                        order = {
                            "order_id": f"ORD-{sku}-{location}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
                            "sku": sku,
                            "location": location,
                            "order_quantity": round(order_qty, 2),
                            "trigger_type": trigger.value,
                            "priority": "URGENT" if trigger == ReplenishmentTrigger.EXPEDITE else "NORMAL",
                            "buffer_top": buffer_data["buffer_top"],
                            "current_net_flow": round(net_flow_position, 2),
                            "lead_time_days": buffer_data["lead_time_days"],
                            "buffer_profile": buffer_data.get("buffer_profile", "operational"),
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                        replenishment_orders.append(order)

            # Sort by priority
            replenishment_orders.sort(key=lambda x: x["priority"] == "URGENT", reverse=True)

            return {
                "status": "success",
                "buffer_id": buffer_id,
                "replenishment_orders": replenishment_orders,
                "total_orders": len(replenishment_orders),
                "urgent_orders": len([o for o in replenishment_orders if o["priority"] == "URGENT"]),
                "total_order_quantity": round(sum(o["order_quantity"] for o in replenishment_orders), 2),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error generating replenishment orders: {e}")
            return {"error": str(e)}

    def dynamic_buffer_adjustment(self,
                                  buffer_id: str,
                                  demand_changes: Dict[str, float],
                                  lead_time_changes: Dict[str, int],
                                  on_order_changes: Optional[Dict[str, float]] = None,
                                  in_transit_changes: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Dynamically adjust DDMRP buffers based on changing conditions with advanced features.

        Args:
            buffer_id: ID of the DDMRP buffer setup
            demand_changes: SKU -> demand change percentage
            lead_time_changes: SKU -> lead time change in days
            on_order_changes: SKU -> on-order inventory change
            in_transit_changes: SKU -> in-transit inventory change
        """
        if buffer_id not in self.ddmrp_buffers:
            return {"error": "Buffer setup not found"}

        try:
            buffer_setup = self.ddmrp_buffers[buffer_id]["buffers"]
            adjusted_buffers = {}

            for buffer_key, buffer_data in buffer_setup.items():
                sku = buffer_data["sku"]

                # Apply demand changes
                demand_change_pct = demand_changes.get(sku, 0)
                new_avg_demand = buffer_data["avg_daily_demand"] * (1 + demand_change_pct / 100)

                # Apply lead time changes
                lead_time_change = lead_time_changes.get(sku, 0)
                new_lead_time = buffer_data["lead_time_days"] + lead_time_change

                # Apply on-order and in-transit changes
                current_on_order = buffer_data.get("on_order_inventory", 0)
                current_in_transit = buffer_data.get("in_transit_inventory", 0)

                new_on_order = current_on_order + (on_order_changes.get(sku, 0) if on_order_changes else 0)
                new_in_transit = current_in_transit + (in_transit_changes.get(sku, 0) if in_transit_changes else 0)

                # Recalculate buffer zones with profile considerations
                ddmrp_config = self.config.get("ddmrp", {})
                lead_time_factor = ddmrp_config.get("lead_time_factor", 1.5)

                dltd = new_avg_demand * new_lead_time * lead_time_factor

                # Get buffer profile multipliers
                buffer_profile_str = buffer_data.get("buffer_profile", "operational")
                buffer_profile = BufferProfile(buffer_profile_str) if isinstance(buffer_profile_str, str) else buffer_profile_str
                profile_multipliers = self._get_buffer_profile_multipliers(buffer_profile)

                green_multiplier = ddmrp_config.get("green_zone_multiplier", 0.3) * profile_multipliers["green"]
                yellow_multiplier = ddmrp_config.get("yellow_zone_multiplier", 0.5) * profile_multipliers["yellow"]
                red_multiplier = ddmrp_config.get("red_zone_multiplier", 0.2) * profile_multipliers["red"]

                new_green_zone = dltd * green_multiplier
                new_yellow_zone = dltd * yellow_multiplier
                new_red_zone = dltd * red_multiplier
                new_buffer_top = new_green_zone + new_yellow_zone + new_red_zone
                new_buffer_bottom = new_green_zone

                # Recalculate net flow position
                new_net_flow_position = buffer_data["current_inventory"] + new_on_order + new_in_transit

                # Determine new zone
                current_zone = self._determine_buffer_zone(
                    new_net_flow_position,
                    new_buffer_bottom,
                    new_buffer_top
                )

                # Determine new replenishment trigger
                new_trigger = self._determine_replenishment_trigger(
                    current_zone, new_net_flow_position, new_buffer_bottom, new_buffer_top
                )

                adjusted_buffers[buffer_key] = {
                    **buffer_data,
                    "avg_daily_demand": round(new_avg_demand, 2),
                    "lead_time_days": new_lead_time,
                    "on_order_inventory": new_on_order,
                    "in_transit_inventory": new_in_transit,
                    "net_flow_position": round(new_net_flow_position, 2),
                    "decoupled_lead_time_demand": round(dltd, 2),
                    "buffer_top": round(new_buffer_top, 2),
                    "buffer_bottom": round(new_buffer_bottom, 2),
                    "green_zone": round(new_green_zone, 2),
                    "yellow_zone": round(new_yellow_zone, 2),
                    "red_zone": round(new_red_zone, 2),
                    "current_zone": current_zone.value,
                    "replenishment_trigger": new_trigger.value,
                    "suggested_order_qty": self._calculate_suggested_order_quantity(
                        new_trigger, new_buffer_top, new_net_flow_position, new_avg_demand, new_lead_time
                    ),
                    "adjustment_applied": True
                }

            # Update buffer setup
            self.ddmrp_buffers[buffer_id]["buffers"] = adjusted_buffers
            self.ddmrp_buffers[buffer_id]["last_adjusted"] = datetime.now(timezone.utc).isoformat()

            return {
                "status": "success",
                "buffer_id": buffer_id,
                "adjusted_buffers": adjusted_buffers,
                "adjustment_summary": self._summarize_ddmrp_setup(adjusted_buffers),
                "adjusted_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in dynamic buffer adjustment: {e}")
            return {"error": str(e)}

    def real_time_rebalancing(self,
                             inventory_data: pd.DataFrame,
                             demand_forecast: Dict[str, List[float]],
                             transportation_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Perform real-time network rebalancing.

        Optimizes inventory distribution across the network based on
        demand forecasts and transportation costs.

        Args:
            inventory_data: Current inventory with sku, location, current_inventory
            demand_forecast: SKU -> demand by period
            transportation_matrix: Location -> Location -> cost per unit
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            rebalancing_config = self.config.get("rebalancing", {})
            rebalancing_config.get("max_transfer_distance", 500)
            min_transfer_quantity = rebalancing_config.get("min_transfer_quantity", 100)

            rebalancing_plan = {
                "transfers": [],
                "total_transfer_cost": 0,
                "service_level_improvements": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            # Analyze inventory imbalances
            location_demand = {}
            location_inventory = {}

            for (sku, location), group in inventory_data.groupby(["sku", "location"]):
                current_inv = group["current_inventory"].iloc[0] if "current_inventory" in group.columns else 0
                forecast = demand_forecast.get(sku, [0] * 12)
                total_demand = sum(forecast)

                if location not in location_demand:
                    location_demand[location] = 0
                    location_inventory[location] = 0

                location_demand[location] += total_demand
                location_inventory[location] += current_inv

            # Identify surplus and deficit locations
            surplus_locations = {
                loc: inv - demand
                for loc, (inv, demand) in zip(location_inventory.keys(),
                                             zip(location_inventory.values(), location_demand.values()))
                if inv > demand * 1.2  # 20% buffer
            }

            deficit_locations = {
                loc: demand - inv
                for loc, (inv, demand) in zip(location_inventory.keys(),
                                             zip(location_inventory.values(), location_demand.values()))
                if inv < demand * 0.8  # Below 80% of demand
            }

            # Generate transfer recommendations
            for surplus_loc, surplus_qty in surplus_locations.items():
                for deficit_loc, deficit_qty in deficit_locations.items():
                    if surplus_loc == deficit_loc:
                        continue

                    # Check transportation cost
                    transfer_cost = transportation_matrix.get(surplus_loc, {}).get(deficit_loc, float('inf'))

                    if transfer_cost == float('inf'):
                        continue

                    # Calculate transfer quantity
                    transfer_qty = min(surplus_qty, deficit_qty)

                    if transfer_qty >= min_transfer_quantity:
                        # Calculate cost savings
                        transfer_cost_total = transfer_qty * transfer_cost
                        stockout_cost_avoided = deficit_qty * 50  # Assume $50 per unit stockout cost

                        if stockout_cost_avoided > transfer_cost_total:
                            rebalancing_plan["transfers"].append({
                                "from_location": surplus_loc,
                                "to_location": deficit_loc,
                                "quantity": round(transfer_qty, 2),
                                "transfer_cost": round(transfer_cost_total, 2),
                                "estimated_savings": round(stockout_cost_avoided - transfer_cost_total, 2),
                                "priority": "HIGH" if deficit_qty > surplus_qty * 0.5 else "MEDIUM"
                            })

                            rebalancing_plan["total_transfer_cost"] += transfer_cost_total

            # Sort by priority and estimated savings
            rebalancing_plan["transfers"].sort(
                key=lambda x: (x["priority"] == "HIGH", x["estimated_savings"]),
                reverse=True
            )

            # Store rebalancing plan
            plan_id = f"REBALANCE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.rebalancing_plan[plan_id] = rebalancing_plan

            return {
                "status": "success",
                "plan_id": plan_id,
                "rebalancing_plan": rebalancing_plan,
                "total_transfers": len(rebalancing_plan["transfers"]),
                "total_cost": round(rebalancing_plan["total_transfer_cost"], 2),
                "estimated_savings": round(sum(t["estimated_savings"] for t in rebalancing_plan["transfers"]), 2),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in real-time rebalancing: {e}")
            return {"error": str(e)}

    def constraint_based_scheduling(self,
                                   production_requests: List[Dict[str, Any]],
                                   constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform constraint-based production scheduling.

        Args:
            production_requests: List of production requests with sku, quantity, due_date
            constraints: Capacity, material, and time constraints
        """
        try:
            # Sort requests by priority and due date
            sorted_requests = sorted(
                production_requests,
                key=lambda x: (x.get("priority", "MEDIUM") == "HIGH", x.get("due_date"))
            )

            schedule = []
            used_capacity = defaultdict(int)

            # Simple greedy scheduling (would use optimization solver in production)
            for request in sorted_requests:
                sku = request["sku"]
                quantity = request["quantity"]
                due_date = request["due_date"]

                # Check capacity constraints
                required_capacity = quantity / constraints.get("daily_capacity", 1000)
                available_capacity = constraints.get("total_capacity", 10000) - sum(used_capacity.values())

                if required_capacity <= available_capacity:
                    # Check material constraints
                    material_available = True
                    if "material_requirements" in constraints:
                        for material, req_qty in constraints["material_requirements"].get(sku, {}).items():
                            if constraints.get("material_inventory", {}).get(material, 0) < req_qty * quantity:
                                material_available = False
                                break

                    if material_available:
                        # Schedule the production
                        schedule.append({
                            "sku": sku,
                            "quantity": quantity,
                            "scheduled_date": due_date - timedelta(days=constraints.get("production_lead_time", 7)),
                            "due_date": due_date,
                            "status": "SCHEDULED"
                        })

                        used_capacity[sku] += required_capacity
                    else:
                        schedule.append({
                            "sku": sku,
                            "quantity": quantity,
                            "due_date": due_date,
                            "status": "MATERIAL_CONSTRAINT",
                            "reason": "Insufficient materials"
                        })
                else:
                    schedule.append({
                        "sku": sku,
                        "quantity": quantity,
                        "due_date": due_date,
                        "status": "CAPACITY_CONSTRAINT",
                        "reason": "Insufficient capacity"
                    })

            return {
                "status": "success",
                "schedule": schedule,
                "scheduled_count": len([s for s in schedule if s["status"] == "SCHEDULED"]),
                "constraint_violations": len([s for s in schedule if s["status"] != "SCHEDULED"]),
                "capacity_utilization": {
                    "used": round(sum(used_capacity.values()), 2),
                    "total": constraints.get("total_capacity", 10000),
                    "utilization_pct": round((sum(used_capacity.values()) / constraints.get("total_capacity", 10000)) * 100, 2)
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in constraint-based scheduling: {e}")
            return {"error": str(e)}

    def get_scenario_comparison(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple scenarios side by side.

        Args:
            scenario_ids: List of scenario IDs to compare
        """
        try:
            scenarios = []

            for scenario_id in scenario_ids:
                if scenario_id not in self.scenarios:
                    continue

                scenario = self.scenarios[scenario_id]
                scenarios.append({
                    "scenario_id": scenario_id,
                    "name": scenario["scenario_name"],
                    "type": scenario["scenario_type"],
                    "impact": scenario["impact_analysis"],
                    "created_at": scenario["created_at"]
                })

            # Generate comparison matrix
            comparison = {
                "scenarios": scenarios,
                "comparison_matrix": self._generate_comparison_matrix(scenarios),
                "best_scenario": self._find_best_scenario(scenarios),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

            return {
                "status": "success",
                "comparison": comparison
            }

        except Exception as e:
            logger_rp.error(f"Error in scenario comparison: {e}")
            return {"error": str(e)}

    def _generate_comparison_matrix(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparison matrix for scenarios."""
        matrix = {}

        for scenario in scenarios:
            scenario_id = scenario["scenario_id"]
            impact = scenario["impact"]

            matrix[scenario_id] = {
                "demand_change": impact.get("metric_changes", {}).get("total_demand", {}).get("change_percentage", 0),
                "capacity_violations": len(impact.get("constraint_violations", [])),
                "risk_level": impact.get("risk_assessment", {}).get("overall_risk", "LOW"),
                "recommendations_count": len(impact.get("recommendations", []))
            }

        return matrix

    def _find_best_scenario(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find best scenario based on multiple criteria."""
        if not scenarios:
            return {"scenario_id": "none", "reason": "No scenarios to compare"}

        best_scenario = scenarios[0]
        best_score = -float('inf')

        for scenario in scenarios:
            impact = scenario["impact"]

            # Simple scoring: lower risk and fewer violations is better
            risk_penalty = {"LOW": 0, "MEDIUM": 10, "HIGH": 20, "CRITICAL": 50}
            risk_score = risk_penalty.get(impact.get("risk_assessment", {}).get("overall_risk", "LOW"), 0)
            violation_score = len(impact.get("constraint_violations", [])) * 5

            total_score = -(risk_score + violation_score)

            if total_score > best_score:
                best_score = total_score
                best_scenario = scenario

        return {
            "scenario_id": best_scenario["scenario_id"],
            "name": best_scenario["name"],
            "reason": "Lowest risk and fewest constraint violations"
        }

    def monte_carlo_simulation(self,
                              base_plan: Dict[str, Any],
                              parameters: List[ScenarioParameter],
                              iterations: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform Monte Carlo simulation for advanced scenario analysis.

        Args:
            base_plan: Base planning scenario
            parameters: List of uncertain parameters to simulate
            iterations: Number of simulation iterations (default from config)
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            iterations = iterations or self.config.get("scenarios", {}).get("monte_carlo_iterations", 10000)

            # Store simulation results
            simulation_results = {
                "parameters": parameters,
                "iterations": iterations,
                "outcomes": {},
                "statistics": {},
                "risk_analysis": {}
            }

            # Initialize outcome tracking
            outcomes = {
                "total_cost": [],
                "service_level": [],
                "revenue": [],
                "inventory_value": [],
                "stockout_events": []
            }

            # Run Monte Carlo simulation
            for i in range(iterations):
                # Sample parameter values
                sampled_plan = self._sample_scenario_parameters(base_plan, parameters)

                # Calculate outcome for this sample
                outcome = self._calculate_scenario_outcome(sampled_plan)

                # Store outcomes
                for key, value in outcome.items():
                    if key in outcomes:
                        outcomes[key].append(value)

            # Calculate statistics
            for metric, values in outcomes.items():
                if values:
                    simulation_results["outcomes"][metric] = values
                    simulation_results["statistics"][metric] = {
                        "mean": round(np.mean(values), 2),
                        "std": round(np.std(values), 2),
                        "min": round(np.min(values), 2),
                        "max": round(np.max(values), 2),
                        "median": round(np.median(values), 2),
                        "percentile_5": round(np.percentile(values, 5), 2),
                        "percentile_95": round(np.percentile(values, 95), 2)
                    }

            # Risk analysis
            simulation_results["risk_analysis"] = self._analyze_monte_carlo_risks(simulation_results["statistics"])

            # Store simulation results
            simulation_id = f"MC-SIM-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.monte_carlo_results[simulation_id] = simulation_results

            return {
                "status": "success",
                "simulation_id": simulation_id,
                "results": simulation_results,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in Monte Carlo simulation: {e}")
            return {"error": str(e)}

    def _sample_scenario_parameters(self, base_plan: Dict[str, Any],
                                   parameters: List[ScenarioParameter]) -> Dict[str, Any]:
        """Sample parameter values for Monte Carlo simulation."""
        sampled_plan = copy.deepcopy(base_plan)

        for param in parameters:
            if param.distribution == "uniform":
                value = np.random.uniform(param.min_value, param.max_value)
            elif param.distribution == "normal":
                mean = (param.min_value + param.max_value) / 2
                std = (param.max_value - param.min_value) / 4  # Approx 95% CI
                value = np.random.normal(mean, std)
                value = np.clip(value, param.min_value, param.max_value)
            elif param.distribution == "triangular":
                value = np.random.triangular(param.min_value, param.base_value, param.max_value)
            else:
                value = param.base_value

            # Apply sampled value to plan
            self._apply_parameter_to_plan(sampled_plan, param.name, value)

        return sampled_plan

    def _apply_parameter_to_plan(self, plan: Dict[str, Any], param_name: str, value: float):
        """Apply sampled parameter value to plan."""
        # Apply to relevant parts of the plan based on parameter name
        if "demand" in param_name.lower():
            if "demand_forecast" in plan:
                for sku in plan["demand_forecast"]:
                    plan["demand_forecast"][sku] = [d * value for d in plan["demand_forecast"][sku]]
        elif "capacity" in param_name.lower():
            if "capacity_utilization" in plan:
                for resource in plan["capacity_utilization"]:
                    plan["capacity_utilization"][resource]["total_capacity"] *= value
        elif "cost" in param_name.lower():
            if "financials" in plan:
                for cost_type in plan["financials"]:
                    plan["financials"][cost_type] *= value

    def _calculate_scenario_outcome(self, plan: Dict[str, Any]) -> Dict[str, float]:
        """Calculate outcome metrics for a scenario."""
        outcome = {
            "total_cost": 0,
            "service_level": 0,
            "revenue": 0,
            "inventory_value": 0,
            "stockout_events": 0
        }

        # Calculate total demand
        if "demand_forecast" in plan:
            total_demand = sum(sum(d) for d in plan["demand_forecast"].values())
            outcome["revenue"] = total_demand * 100  # Assume $100 per unit
        else:
            total_demand = 0

        # Calculate total cost
        if "financials" in plan:
            outcome["total_cost"] = sum(plan["financials"].values())

        # Calculate service level
        if "capacity_utilization" in plan:
            total_capacity = sum(r["total_capacity"] for r in plan["capacity_utilization"].values())
            if total_demand > 0 and total_capacity > 0:
                outcome["service_level"] = min(100, (total_capacity / total_demand) * 100)

        # Calculate inventory value
        if "inventory_status" in plan:
            outcome["inventory_value"] = plan["inventory_status"].get("total_inventory_value", 0)

        # Calculate stockout events
        if total_demand > 0 and outcome["service_level"] < 95:
            outcome["stockout_events"] = int(total_demand * (1 - outcome["service_level"] / 100))

        return outcome

    def _analyze_monte_carlo_risks(self, statistics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze risks from Monte Carlo simulation results."""
        risk_analysis = {
            "value_at_risk": {},
            "expected_shortfall": {},
            "risk_factors": []
        }

        confidence_levels = [0.90, 0.95, 0.99]

        for metric, stats in statistics.items():
            if metric == "total_cost":
                # VaR for cost (we want to minimize cost, so look at high percentiles)
                for cl in confidence_levels:
                    percentile = (1 - cl) * 100
                    var_key = f"VaR_{int(cl*100)}"
                    risk_analysis["value_at_risk"][f"{metric}_{var_key}"] = stats.get(f"percentile_{int(percentile)}", 0)
            elif metric == "service_level":
                # VaR for service level (we want high service level, so look at low percentiles)
                for cl in confidence_levels:
                    percentile = cl * 100
                    var_key = f"VaR_{int(cl*100)}"
                    risk_analysis["value_at_risk"][f"{metric}_{var_key}"] = stats.get(f"percentile_{int(percentile)}", 0)

            # Expected Shortfall (average of worst outcomes)
            if metric == "total_cost":
                risk_analysis["expected_shortfall"][metric] = stats.get("percentile_95", 0) * 1.1  # Approximation

        # Identify key risk factors
        if statistics.get("service_level", {}).get("percentile_5", 100) < 90:
            risk_analysis["risk_factors"].append({
                "factor": "service_level_risk",
                "severity": "HIGH",
                "description": "5% of scenarios show service level below 90%"
            })

        if statistics.get("total_cost", {}).get("percentile_95", 0) > statistics.get("total_cost", {}).get("mean", 0) * 1.5:
            risk_analysis["risk_factors"].append({
                "factor": "cost_volatility",
                "severity": "MEDIUM",
                "description": "High cost volatility in worst-case scenarios"
            })

        return risk_analysis

    def sensitivity_analysis(self,
                           base_plan: Dict[str, Any],
                           parameters: List[ScenarioParameter],
                           outcome_metrics: List[str] = None) -> Dict[str, Any]:
        """
        Perform sensitivity analysis to identify critical parameters.

        Args:
            base_plan: Base planning scenario
            parameters: Parameters to analyze for sensitivity
            outcome_metrics: Metrics to analyze (default: all)
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            outcome_metrics = outcome_metrics or ["total_cost", "service_level", "revenue"]
            step_size = self.config.get("scenarios", {}).get("sensitivity_step_size", 0.1)

            sensitivity_results = {
                "parameters": [],
                "sensitivity_matrix": {},
                "tornado_chart_data": {},
                "critical_parameters": []
            }

            # Calculate base outcome
            base_outcome = self._calculate_scenario_outcome(base_plan)

            # Analyze each parameter
            for param in parameters:
                param_sensitivity = {
                    "parameter": param.name,
                    "effects": {}
                }

                # Test parameter variations (+/- step_size)
                variations = [-step_size, -step_size/2, step_size/2, step_size]

                for variation in variations:
                    # Apply variation
                    modified_plan = copy.deepcopy(base_plan)
                    perturbed_value = param.base_value * (1 + variation)
                    self._apply_parameter_to_plan(modified_plan, param.name, perturbed_value)

                    # Calculate outcome
                    outcome = self._calculate_scenario_outcome(modified_plan)

                    # Calculate sensitivity
                    for metric in outcome_metrics:
                        if metric in base_outcome and base_outcome[metric] > 0:
                            change_pct = ((outcome[metric] - base_outcome[metric]) / base_outcome[metric]) * 100
                            param_sensitivity["effects"][f"{metric}_{variation:+.2f}"] = round(change_pct, 2)

                sensitivity_results["parameters"].append(param_sensitivity)

            # Build sensitivity matrix
            for param_data in sensitivity_results["parameters"]:
                param_name = param_data["parameter"]
                sensitivity_results["sensitivity_matrix"][param_name] = param_data["effects"]

            # Generate tornado chart data
            for metric in outcome_metrics:
                tornado_data = []
                for param_data in sensitivity_results["parameters"]:
                    param_name = param_data["parameter"]
                    effects = param_data["effects"]

                    # Get max effect for this parameter on this metric
                    metric_effects = [v for k, v in effects.items() if metric in k]
                    if metric_effects:
                        max_effect = max(abs(e) for e in metric_effects)
                        tornado_data.append({
                            "parameter": param_name,
                            "effect": max_effect,
                            "direction": "positive" if max_effect > 0 else "negative"
                        })

                # Sort by effect magnitude
                tornado_data.sort(key=lambda x: x["effect"], reverse=True)
                sensitivity_results["tornado_chart_data"][metric] = tornado_data

            # Identify critical parameters (highest sensitivity)
            for metric in outcome_metrics:
                if metric in sensitivity_results["tornado_chart_data"]:
                    top_params = sensitivity_results["tornado_chart_data"][metric][:3]
                    sensitivity_results["critical_parameters"].append({
                        "metric": metric,
                        "critical_parameters": [p["parameter"] for p in top_params]
                    })

            # Store sensitivity analysis
            analysis_id = f"SENS-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.sensitivity_analysis[analysis_id] = sensitivity_results

            return {
                "status": "success",
                "analysis_id": analysis_id,
                "results": sensitivity_results,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in sensitivity analysis: {e}")
            return {"error": str(e)}

    def create_cascading_scenario(self,
                                 base_plan: Dict[str, Any],
                                 trigger_event: Dict[str, Any],
                                 propagation_steps: int = 5) -> Dict[str, Any]:
        """
        Create cascading failure scenario for network resilience analysis.

        Args:
            base_plan: Base planning scenario
            trigger_event: Initial disruption event
            propagation_steps: Number of steps to simulate cascading effects
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            cascading_results = {
                "trigger_event": trigger_event,
                "propagation_steps": propagation_steps,
                "cascade_path": [],
                "impact_timeline": [],
                "total_impact": {}
            }

            current_plan = copy.deepcopy(base_plan)
            current_impact = trigger_event

            for step in range(propagation_steps):
                # Calculate impact at current step
                step_impact = self._calculate_cascade_impact(current_plan, current_impact, step)

                # Store step results
                cascading_results["cascade_path"].append({
                    "step": step,
                    "impact_type": current_impact.get("type", "unknown"),
                    "affected_entities": current_impact.get("affected_entities", []),
                    "impact_magnitude": current_impact.get("magnitude", 0)
                })

                cascading_results["impact_timeline"].append(step_impact)

                # Propagate to next step
                if step < propagation_steps - 1:
                    current_impact = self._propagate_cascade(current_impact, step)

                    # Check if cascade stops
                    if current_impact.get("magnitude", 0) < 0.1:  # Threshold to stop
                        break

            # Calculate total impact
            total_impact = self._aggregate_cascade_impact(cascading_results["impact_timeline"])
            cascading_results["total_impact"] = total_impact

            # Store scenario
            scenario_id = f"CASCADE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.scenarios[scenario_id] = {
                "scenario_id": scenario_id,
                "scenario_name": f"Cascading Failure: {trigger_event.get('type', 'Unknown')}",
                "scenario_type": ScenarioType.NETWORK.value,
                "base_plan": base_plan,
                "cascade_results": cascading_results,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            return {
                "status": "success",
                "scenario_id": scenario_id,
                "cascade_results": cascading_results,
                "total_impact": total_impact,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error creating cascading scenario: {e}")
            return {"error": str(e)}

    def _calculate_cascade_impact(self, plan: Dict[str, Any], impact: Dict[str, Any],
                                 step: int) -> Dict[str, Any]:
        """Calculate impact at a specific cascade step."""
        step_impact = {
            "step": step,
            "demand_impact": 0,
            "supply_impact": 0,
            "cost_impact": 0,
            "service_impact": 0
        }

        magnitude = impact.get("magnitude", 0)
        affected_entities = impact.get("affected_entities", [])

        # Apply impact based on type
        if impact.get("type") == "supplier_failure":
            step_impact["supply_impact"] = magnitude * len(affected_entities)
            step_impact["cost_impact"] = magnitude * 1000  # Assume $1000 per unit
        elif impact.get("type") == "demand_surge":
            step_impact["demand_impact"] = magnitude
            step_impact["service_impact"] = magnitude * 0.5
        elif impact.get("type") == "transportation_disruption":
            step_impact["supply_impact"] = magnitude * 0.3
            step_impact["cost_impact"] = magnitude * 500

        return step_impact

    def _propagate_cascade(self, current_impact: Dict[str, Any], step: int) -> Dict[str, Any]:
        """Propagate cascade to next step."""
        # Decay factor to reduce impact over time
        decay_factor = 0.8 ** step

        propagated_impact = {
            "type": current_impact.get("type", "unknown"),
            "magnitude": current_impact.get("magnitude", 0) * decay_factor,
            "affected_entities": current_impact.get("affected_entities", [])
        }

        # Add some randomness to simulate network effects
        propagated_impact["magnitude"] *= np.random.uniform(0.9, 1.1)

        return propagated_impact

    def _aggregate_cascade_impact(self, timeline: List[Dict[str, Any]]) -> Dict[str, float]:
        """Aggregate total impact from cascade timeline."""
        total_impact = {
            "total_demand_impact": 0,
            "total_supply_impact": 0,
            "total_cost_impact": 0,
            "total_service_impact": 0,
            "cascade_duration": len(timeline)
        }

        for step_impact in timeline:
            total_impact["total_demand_impact"] += step_impact.get("demand_impact", 0)
            total_impact["total_supply_impact"] += step_impact.get("supply_impact", 0)
            total_impact["total_cost_impact"] += step_impact.get("cost_impact", 0)
            total_impact["total_service_impact"] += step_impact.get("service_impact", 0)

        return total_impact

    def strategic_buffer_placement(self,
                                  network_data: pd.DataFrame,
                                  demand_profiles: Dict[str, Dict[str, float]],
                                  service_level_targets: Dict[str, float]) -> Dict[str, Any]:
        """
        Optimize strategic buffer placement across the supply network.

        Args:
            network_data: Network topology with nodes, edges, distances
            demand_profiles: SKU/location demand profiles
            service_level_targets: Node-level service level targets
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            buffer_recommendations = {
                "placement_strategy": "strategic_decoupling",
                "buffer_locations": [],
                "network_analysis": {},
                "optimization_results": {}
            }

            # Analyze network structure
            network_analysis = self._analyze_network_structure(network_data)
            buffer_recommendations["network_analysis"] = network_analysis

            # Identify critical decoupling points
            decoupling_points = self._identify_decoupling_points(
                network_data, demand_profiles, network_analysis
            )

            # Calculate optimal buffer levels at each point
            for point in decoupling_points:
                location = point["location"]
                sku = point["sku"]

                # Get demand profile
                profile = demand_profiles.get(f"{sku}_{location}", demand_profiles.get(sku, {}))
                avg_demand = profile.get("avg_daily_demand", 10)
                demand_variability = profile.get("demand_variability", 0.2)

                # Get service level target
                service_target = service_level_targets.get(location, 0.95)

                # Calculate strategic buffer
                buffer_calculation = self._calculate_strategic_buffer(
                    avg_demand, demand_variability, service_target, point
                )

                buffer_recommendations["buffer_locations"].append({
                    "location": location,
                    "sku": sku,
                    "strategic_importance": point["importance"],
                    "decoupling_reason": point["reason"],
                    "buffer_calculation": buffer_calculation,
                    "justification": self._generate_buffer_justification(point, buffer_calculation)
                })

            # Sort by strategic importance
            buffer_recommendations["buffer_locations"].sort(
                key=lambda x: x["strategic_importance"], reverse=True
            )

            # Calculate total investment required
            total_investment = sum(
                loc["buffer_calculation"]["total_buffer_investment"]
                for loc in buffer_recommendations["buffer_locations"]
            )

            buffer_recommendations["optimization_results"] = {
                "total_locations": len(buffer_recommendations["buffer_locations"]),
                "total_investment": round(total_investment, 2),
                "high_priority_locations": len([l for l in buffer_recommendations["buffer_locations"] if l["strategic_importance"] > 0.8]),
                "estimated_service_level_improvement": round(
                    sum(l["buffer_calculation"]["expected_service_level"] for l in buffer_recommendations["buffer_locations"]) /
                    len(buffer_recommendations["buffer_locations"]) if buffer_recommendations["buffer_locations"] else 0, 2
                )
            }

            return {
                "status": "success",
                "buffer_recommendations": buffer_recommendations,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in strategic buffer placement: {e}")
            return {"error": str(e)}

    def _analyze_network_structure(self, network_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze supply network structure for buffer placement."""
        # Simplified network analysis
        analysis = {
            "total_nodes": len(network_data) if "node" in network_data.columns else 0,
            "network_depth": 0,
            "critical_paths": [],
            "bottlenecks": []
        }

        if "node" in network_data.columns and "type" in network_data.columns:
            # Count by type
            node_types = network_data["type"].value_counts().to_dict()
            analysis["node_types"] = node_types

            # Identify potential bottlenecks (simplified)
            if "capacity" in network_data.columns:
                low_capacity = network_data[network_data["capacity"] < network_data["capacity"].quantile(0.25)]
                analysis["bottlenecks"] = low_capacity["node"].tolist()

        return analysis

    def _identify_decoupling_points(self, network_data: pd.DataFrame,
                                   demand_profiles: Dict[str, Dict[str, float]],
                                   network_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimal decoupling points in the network."""
        decoupling_points = []

        # Simplified logic - in production would use network analysis algorithms
        if "node" in network_data.columns:
            for _, row in network_data.iterrows():
                node = row["node"]
                node_type = row.get("type", "unknown")

                # Calculate importance score
                importance = 0.5  # Base importance

                if node_type == "factory":
                    importance += 0.3
                elif node_type == "warehouse":
                    importance += 0.2
                elif node_type == "distribution_center":
                    importance += 0.1

                # Check if node serves high demand
                for sku_key, profile in demand_profiles.items():
                    if node in sku_key or node in str(profile):
                        demand = profile.get("avg_daily_demand", 0)
                        if demand > 100:  # High demand threshold
                            importance += 0.2

                # Determine decoupling reason
                reason = "standard"
                if importance > 0.8:
                    reason = "high_demand_uncoupling"
                elif node_type == "factory":
                    reason = "production_decoupling"
                elif node in network_analysis.get("bottlenecks", []):
                    reason = "bottleneck_decoupling"

                decoupling_points.append({
                    "location": node,
                    "sku": "ALL",  # Would be specific in production
                    "importance": min(1.0, importance),
                    "reason": reason,
                    "node_type": node_type
                })

        return decoupling_points

    def _calculate_strategic_buffer(self, avg_demand: float, demand_variability: float,
                                   service_target: float, point: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate strategic buffer levels for a decoupling point."""
        # Calculate safety stock based on service level
        z_score = stats.norm.ppf(service_target)
        safety_stock = z_score * avg_demand * demand_variability

        # Calculate cycle stock (based on lead time)
        lead_time = point.get("lead_time", 7)  # Default 7 days
        cycle_stock = avg_demand * lead_time

        # Calculate strategic buffer
        strategic_multiplier = 1.0 + (point["importance"] * 0.5)  # Higher importance = more buffer
        total_buffer = (cycle_stock + safety_stock) * strategic_multiplier

        # Calculate buffer zones
        green_zone = total_buffer * 0.3
        yellow_zone = total_buffer * 0.5
        red_zone = total_buffer * 0.2

        return {
            "cycle_stock": round(cycle_stock, 2),
            "safety_stock": round(safety_stock, 2),
            "strategic_multiplier": round(strategic_multiplier, 2),
            "total_buffer": round(total_buffer, 2),
            "green_zone": round(green_zone, 2),
            "yellow_zone": round(yellow_zone, 2),
            "red_zone": round(red_zone, 2),
            "expected_service_level": round(service_target * 100, 2),
            "total_buffer_investment": round(total_buffer * 50, 2)  # Assume $50 per unit
        }

    def _generate_buffer_justification(self, point: Dict[str, Any],
                                     buffer_calc: Dict[str, Any]) -> str:
        """Generate justification for buffer placement."""
        justifications = []

        if point["importance"] > 0.8:
            justifications.append(f"High strategic importance ({point['importance']:.2f})")

        if point["reason"] == "production_decoupling":
            justifications.append("Decouples production from demand variability")
        elif point["reason"] == "bottleneck_decoupling":
            justifications.append("Protects against network bottlenecks")
        elif point["reason"] == "high_demand_uncoupling":
            justifications.append("Handles high demand uncertainty")

        if buffer_calc["expected_service_level"] > 97:
            justifications.append(f"Target service level {buffer_calc['expected_service_level']}%")

        return "; ".join(justifications) if justifications else "Standard placement optimization"

    def multi_ecHELON_ddmrp(self,
                           network_data: pd.DataFrame,
                           echelon_data: Dict[str, List[str]],
                           demand_profiles: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Implement multi-echelon DDMRP across multiple supply chain levels.

        Args:
            network_data: Network topology data
            echelon_data: Echelon structure (e.g., {"echelon_1": ["factory1"], "echelon_2": ["dc1", "dc2"]})
            demand_profiles: Demand profiles by SKU/location
        """
        if not self._initialised:
            return {"error": "Response planning not initialised"}

        try:
            multi_echelon_results = {
                "echelon_structure": echelon_data,
                "echelon_buffers": {},
                "net_flow_analysis": {},
                "coordination_strategy": {}
            }

            # Process each echelon
            for echelon, locations in echelon_data.items():
                echelon_buffers = {}

                for location in locations:
                    # Calculate buffers for this location
                    location_buffers = {}

                    for sku_key, profile in demand_profiles.items():
                        if location in sku_key:
                            sku = sku_key.split("_")[0] if "_" in sku_key else sku_key

                            # Calculate echelon-specific buffer
                            buffer_result = self._calculate_echelon_buffer(
                                profile, echelon, location
                            )

                            location_buffers[sku] = buffer_result

                    echelon_buffers[location] = location_buffers

                multi_echelon_results["echelon_buffers"][echelon] = echelon_buffers

            # Analyze net flow between echelons
            multi_echelon_results["net_flow_analysis"] = self._analyze_echelon_net_flow(
                multi_echelon_results["echelon_buffers"], echelon_data
            )

            # Generate coordination strategy
            multi_echelon_results["coordination_strategy"] = self._generate_echelon_coordination(
                multi_echelon_results["echelon_buffers"], multi_echelon_results["net_flow_analysis"]
            )

            return {
                "status": "success",
                "multi_echelon_results": multi_echelon_results,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_rp.error(f"Error in multi-echelon DDMRP: {e}")
            return {"error": str(e)}

    def _calculate_echelon_buffer(self, profile: Dict[str, float],
                                echelon: str, location: str) -> Dict[str, Any]:
        """Calculate buffer for specific echelon."""
        avg_demand = profile.get("avg_daily_demand", 10)
        profile.get("demand_variability", 0.2)

        # Echelon-specific multipliers
        echelon_multipliers = {
            "echelon_1": 1.5,  # Factory - higher buffer
            "echelon_2": 1.2,  # Distribution center
            "echelon_3": 1.0,  # Retail - standard buffer
            "echelon_4": 0.8   # Last mile - lower buffer
        }

        multiplier = echelon_multipliers.get(echelon, 1.0)

        # Calculate buffer components
        lead_time = profile.get("lead_time", 7)
        ltd = avg_demand * lead_time * multiplier

        # Buffer zones
        green_zone = ltd * 0.3
        yellow_zone = ltd * 0.5
        red_zone = ltd * 0.2

        return {
            "avg_daily_demand": round(avg_demand, 2),
            "lead_time_demand": round(ltd, 2),
            "echelon_multiplier": round(multiplier, 2),
            "green_zone": round(green_zone, 2),
            "yellow_zone": round(yellow_zone, 2),
            "red_zone": round(red_zone, 2),
            "buffer_top": round(ltd, 2),
            "buffer_bottom": round(green_zone, 2)
        }

    def _analyze_echelon_net_flow(self, echelon_buffers: Dict[str, Dict],
                                 echelon_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze net flow between echelons."""
        net_flow_analysis = {
            "echelon_balances": {},
            "flow_opportunities": [],
            "risks": []
        }

        # Calculate echelon-level balances
        for echelon, locations in echelon_data.items():
            total_buffer = 0
            total_demand = 0

            for location in locations:
                if location in echelon_buffers.get(echelon, {}):
                    for sku, buffer_data in echelon_buffers[echelon][location].items():
                        total_buffer += buffer_data["buffer_top"]
                        total_demand += buffer_data["avg_daily_demand"]

            net_flow_analysis["echelon_balances"][echelon] = {
                "total_buffer": round(total_buffer, 2),
                "total_demand": round(total_demand, 2),
                "coverage_ratio": round(total_buffer / total_demand, 2) if total_demand > 0 else 0
            }

        # Identify flow opportunities
        echelons = list(echelon_data.keys())
        for i in range(len(echelons) - 1):
            current_echelon = echelons[i]
            next_echelon = echelons[i + 1]

            current_coverage = net_flow_analysis["echelon_balances"][current_echelon]["coverage_ratio"]
            next_coverage = net_flow_analysis["echelon_balances"][next_echelon]["coverage_ratio"]

            if current_coverage > 1.2 and next_coverage < 0.8:
                net_flow_analysis["flow_opportunities"].append({
                    "from": current_echelon,
                    "to": next_echelon,
                    "reason": "Surplus to deficit"
                })

        return net_flow_analysis

    def _generate_echelon_coordination(self, echelon_buffers: Dict[str, Dict],
                                      net_flow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate coordination strategy for multi-echelon DDMRP."""
        coordination = {
            "synchronization_points": [],
            "pull_strategy": "sequential",
            "escalation_rules": []
        }

        # Define synchronization points
        for echelon in echelon_buffers.keys():
            coordination["synchronization_points"].append({
                "echelon": echelon,
                "sync_frequency": "daily" if "echelon_1" in echelon else "weekly",
                "sync_trigger": "buffer_zone_yellow"
            })

        # Define escalation rules
        for opportunity in net_flow_analysis.get("flow_opportunities", []):
            coordination["escalation_rules"].append({
                "trigger": f"{opportunity['from']}_surplus",
                "action": f"transfer_to_{opportunity['to']}",
                "priority": "HIGH"
            })

        return coordination
