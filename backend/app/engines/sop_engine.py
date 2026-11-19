"""
NEXUS — Sales & Operations Planning Engine (SAP IBP-style)
=========================================================
Executive dashboard, consensus forecasting, and performance
management for integrated business planning.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger_sop = logging.getLogger("nexus.sop_engine")


class ForecastStatus(Enum):
    """Forecast status in consensus process."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class SOPEngine:
    """
    Enterprise Sales & Operations Planning with consensus forecasting,
    executive dashboard, and performance management.
    """

    def __init__(self):
        self.consensus_forecasts = {}
        self.forecast_versions = {}
        self.approval_workflow = {}
        self.executive_metrics = {}
        self._initialised = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize S&OP engine with configuration.

        Args:
            config: Configuration dict with S&OP parameters
        """
        try:
            default_config = {
                "planning_cycles": {
                    "daily": False,
                    "weekly": True,
                    "monthly": True
                },
                "approval_levels": [
                    "regional_manager",
                    "category_manager",
                    "director",
                    "vp"
                ],
                "forecast_horizons": {
                    "short_term": 4,    # weeks
                    "medium_term": 12,  # weeks
                    "long_term": 52     # weeks
                },
                "performance_targets": {
                    "forecast_accuracy": 90,
                    "inventory_turnover": 8,
                    "service_level": 95,
                    "working_capital_efficiency": 85
                }
            }

            config = config or default_config
            self.config = config

            self._initialised = True

            return {
                "status": "success",
                "planning_cycles_configured": len([k for k, v in config["planning_cycles"].items() if v]),
                "approval_levels": len(config["approval_levels"]),
                "initialised_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_sop.error(f"Error initializing S&OP engine: {e}")
            return {"error": str(e), "initialised": False}

    def create_consensus_forecast(self,
                                  functional_inputs: Dict[str, Dict[str, List[float]]],
                                  weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Create consensus forecast by combining functional inputs.

        Args:
            functional_inputs: Dictionary of function -> {sku -> forecast}
                e.g., {"sales": {"SKU001": [100, 110, 105]},
                       "marketing": {"SKU001": [120, 115, 130]},
                       "finance": {"SKU001": [110, 112, 108]}}
            weights: Optional weights for each function (default: equal)
        """
        if not self._initialised:
            return {"error": "S&OP engine not initialised"}

        try:
            # Get all SKUs from first function
            first_function = list(functional_inputs.keys())[0]
            skus = functional_inputs[first_function].keys()

            # Default weights: equal weight for all functions
            if weights is None:
                num_functions = len(functional_inputs)
                weights = dict.fromkeys(functional_inputs.keys(), 1.0 / num_functions)

            # Normalize weights
            total_weight = sum(weights.values())
            weights = {k: v/total_weight for k, v in weights.items()}

            consensus_results = {}
            variance_analysis = {}

            for sku in skus:
                # Collect forecasts from all functions for this SKU
                function_forecasts = []
                for function in functional_inputs.keys():
                    if sku in functional_inputs[function]:
                        function_forecasts.append(functional_inputs[function][sku])

                if not function_forecasts:
                    continue

                # Calculate weighted average at each period
                max_horizon = max(len(f) for f in function_forecasts)
                consensus_forecast = []
                period_variances = []

                for period in range(max_horizon):
                    period_values = []
                    weighted_sum = 0
                    weight_sum = 0

                    for idx, function in enumerate(functional_inputs.keys()):
                        if sku in functional_inputs[function] and period < len(functional_inputs[function][sku]):
                            value = functional_inputs[function][sku][period]
                            weight = weights.get(function, 0)
                            weighted_sum += value * weight
                            weight_sum += weight
                            period_values.append(value)

                    if weight_sum > 0:
                        consensus_value = weighted_sum / weight_sum
                        consensus_forecast.append(round(consensus_value, 2))

                        # Calculate variance (measure of disagreement)
                        if len(period_values) > 1:
                            period_variances.append(np.var(period_values))
                        else:
                            period_variances.append(0)
                    else:
                        consensus_forecast.append(0)
                        period_variances.append(0)

                # Calculate consensus metrics
                avg_variance = np.mean(period_variances) if period_variances else 0
                disagreement_score = min(100, (avg_variance / np.mean([np.mean(f) for f in function_forecasts if np.mean(f) > 0]) * 100) if np.mean([np.mean(f) for f in function_forecasts if np.mean(f) > 0]) > 0 else 0)

                consensus_results[sku] = {
                    "consensus_forecast": consensus_forecast,
                    "functional_inputs": {func: functional_inputs[func].get(sku, []) for func in functional_inputs.keys()},
                    "weights_used": weights,
                    "disagreement_score": round(disagreement_score, 2),
                    "variance_by_period": [round(v, 2) for v in period_variances]
                }

                variance_analysis[sku] = {
                    "average_disagreement": round(disagreement_score, 2),
                    "high_disagreement_periods": [i for i, v in enumerate(period_variances) if v > np.mean(period_variances) * 1.5],
                    "most_aligned_function": self._find_most_aligned_function(functional_inputs, sku),
                    "outlier_function": self._find_outlier_function(functional_inputs, sku)
                }

            # Store consensus forecast
            forecast_id = f"CONSENSUS-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.consensus_forecasts[forecast_id] = {
                "forecasts": consensus_results,
                "variance_analysis": variance_analysis,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": ForecastStatus.DRAFT.value
            }

            return {
                "status": "success",
                "forecast_id": forecast_id,
                "consensus_forecasts": consensus_results,
                "variance_analysis": variance_analysis,
                "total_skus": len(consensus_results),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_sop.error(f"Error creating consensus forecast: {e}")
            return {"error": str(e)}

    def _find_most_aligned_function(self, functional_inputs: Dict[str, Dict[str, List[float]]],
                                   sku: str) -> str:
        """Find the function whose forecast is closest to consensus."""
        try:
            # Calculate consensus for this SKU
            function_forecasts = [functional_inputs[func][sku] for func in functional_inputs.keys() if sku in functional_inputs[func]]
            if not function_forecasts:
                return "none"

            max_len = max(len(f) for f in function_forecasts)
            consensus = []

            for period in range(max_len):
                period_values = [f[period] for f in function_forecasts if period < len(f)]
                consensus.append(np.mean(period_values) if period_values else 0)

            # Find function closest to consensus
            best_function = "none"
            best_distance = float('inf')

            for function in functional_inputs.keys():
                if sku not in functional_inputs[function]:
                    continue

                forecast = functional_inputs[function][sku]
                distance = sum(abs(forecast[i] - consensus[i]) for i in range(min(len(forecast), len(consensus))))

                if distance < best_distance:
                    best_distance = distance
                    best_function = function

            return best_function

        except Exception as e:
            logger_sop.error(f"Error finding most aligned function: {e}")
            return "none"

    def _find_outlier_function(self, functional_inputs: Dict[str, Dict[str, List[float]]],
                              sku: str) -> str:
        """Find the function whose forecast deviates most from consensus."""
        try:
            function_forecasts = [functional_inputs[func][sku] for func in functional_inputs.keys() if sku in functional_inputs[func]]
            if not function_forecasts or len(function_forecasts) < 2:
                return "none"

            max_len = max(len(f) for f in function_forecasts)
            consensus = []

            for period in range(max_len):
                period_values = [f[period] for f in function_forecasts if period < len(f)]
                consensus.append(np.mean(period_values) if period_values else 0)

            # Find function furthest from consensus
            worst_function = "none"
            worst_distance = 0

            for function in functional_inputs.keys():
                if sku not in functional_inputs[function]:
                    continue

                forecast = functional_inputs[function][sku]
                distance = sum(abs(forecast[i] - consensus[i]) for i in range(min(len(forecast), len(consensus))))

                if distance > worst_distance:
                    worst_distance = distance
                    worst_function = function

            return worst_function

        except Exception as e:
            logger_sop.error(f"Error finding outlier function: {e}")
            return "none"

    def submit_forecast_for_approval(self, forecast_id: str,
                                    submitter: str,
                                    comments: str = "") -> Dict[str, Any]:
        """
        Submit consensus forecast for approval workflow.

        Args:
            forecast_id: ID of the consensus forecast
            submitter: User/role submitting the forecast
            comments: Optional comments about the submission
        """
        if forecast_id not in self.consensus_forecasts:
            return {"error": "Forecast not found"}

        try:
            forecast = self.consensus_forecasts[forecast_id]
            forecast["status"] = ForecastStatus.SUBMITTED.value
            forecast["submitted_by"] = submitter
            forecast["submitted_at"] = datetime.now(timezone.utc).isoformat()
            forecast["submission_comments"] = comments

            # Initialize approval workflow
            self.approval_workflow[forecast_id] = {
                "current_level": 0,
                "approvals": [],
                "rejections": [],
                "status": "pending_approval",
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            return {
                "status": "success",
                "forecast_id": forecast_id,
                "new_status": forecast["status"],
                "approval_levels": self.config.get("approval_levels", []),
                "message": "Forecast submitted for approval"
            }

        except Exception as e:
            logger_sop.error(f"Error submitting forecast for approval: {e}")
            return {"error": str(e)}

    def approve_forecast(self, forecast_id: str,
                        approver: str,
                        level: str,
                        comments: str = "") -> Dict[str, Any]:
        """
        Approve forecast at specified level.

        Args:
            forecast_id: ID of the consensus forecast
            approver: User/role approving the forecast
            level: Approval level (e.g., "regional_manager", "director")
            comments: Optional approval comments
        """
        if forecast_id not in self.consensus_forecasts:
            return {"error": "Forecast not found"}

        if forecast_id not in self.approval_workflow:
            return {"error": "Approval workflow not initialized"}

        try:
            workflow = self.approval_workflow[forecast_id]
            approval_levels = self.config.get("approval_levels", [])

            if level not in approval_levels:
                return {"error": f"Invalid approval level: {level}"}

            current_level_idx = workflow["current_level"]
            if level != approval_levels[current_level_idx]:
                return {"error": f"Must approve at current level: {approval_levels[current_level_idx]}"}

            # Record approval
            workflow["approvals"].append({
                "level": level,
                "approver": approver,
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "comments": comments
            })

            # Move to next level or complete
            if current_level_idx < len(approval_levels) - 1:
                workflow["current_level"] = current_level_idx + 1
                self.consensus_forecasts[forecast_id]["status"] = ForecastStatus.UNDER_REVIEW.value
                message = f"Approved at {level}, awaiting next level approval"
            else:
                workflow["status"] = "approved"
                self.consensus_forecasts[forecast_id]["status"] = ForecastStatus.APPROVED.value
                self.consensus_forecasts[forecast_id]["approved_at"] = datetime.now(timezone.utc).isoformat()
                message = "Forecast fully approved"

            return {
                "status": "success",
                "forecast_id": forecast_id,
                "workflow_status": workflow["status"],
                "current_level": workflow["current_level"],
                "message": message
            }

        except Exception as e:
            logger_sop.error(f"Error approving forecast: {e}")
            return {"error": str(e)}

    def reject_forecast(self, forecast_id: str,
                       rejecter: str,
                       level: str,
                       reason: str) -> Dict[str, Any]:
        """
        Reject forecast at specified level.

        Args:
            forecast_id: ID of the consensus forecast
            rejecter: User/role rejecting the forecast
            level: Approval level
            reason: Reason for rejection
        """
        if forecast_id not in self.consensus_forecasts:
            return {"error": "Forecast not found"}

        if forecast_id not in self.approval_workflow:
            return {"error": "Approval workflow not initialized"}

        try:
            workflow = self.approval_workflow[forecast_id]

            # Record rejection
            workflow["rejections"].append({
                "level": level,
                "rejecter": rejecter,
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason
            })

            workflow["status"] = "rejected"
            self.consensus_forecasts[forecast_id]["status"] = ForecastStatus.REJECTED.value
            self.consensus_forecasts[forecast_id]["rejected_at"] = datetime.now(timezone.utc).isoformat()

            return {
                "status": "success",
                "forecast_id": forecast_id,
                "workflow_status": workflow["status"],
                "message": "Forecast rejected and returned to draft"
            }

        except Exception as e:
            logger_sop.error(f"Error rejecting forecast: {e}")
            return {"error": str(e)}

    def generate_executive_dashboard(self,
                                    demand_forecasts: Dict[str, List[float]],
                                    supply_plan: Dict[str, Any],
                                    inventory_status: Dict[str, Any],
                                    financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate executive dashboard with key metrics and insights.

        Args:
            demand_forecasts: SKU -> demand forecast
            supply_plan: Supply planning results
            inventory_status: Inventory optimization results
            financial_data: Optional financial metrics
        """
        if not self._initialised:
            return {"error": "S&OP engine not initialised"}

        try:
            dashboard = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary_metrics": {},
                "demand_analysis": {},
                "supply_analysis": {},
                "inventory_analysis": {},
                "financial_analysis": {},
                "performance_tracking": {},
                "recommendations": [],
                "alerts": []
            }

            # Summary metrics
            total_demand = sum(sum(forecast) for forecast in demand_forecasts.values())
            total_skus = len(demand_forecasts)

            dashboard["summary_metrics"] = {
                "total_forecast_demand": round(total_demand, 2),
                "total_skus": total_skus,
                "forecast_horizon_weeks": max(len(f) for f in demand_forecasts.values()) if demand_forecasts else 0,
                "planning_currency": "USD"
            }

            # Demand analysis
            demand_growth = self._calculate_demand_growth(demand_forecasts)
            demand_volatility = self._calculate_demand_volatility(demand_forecasts)

            dashboard["demand_analysis"] = {
                "demand_growth_rate": demand_growth,
                "demand_volatility_index": demand_volatility,
                "top_demanded_skus": self._get_top_skus(demand_forecasts, top_n=5),
                "demand_concentration": self._calculate_demand_concentration(demand_forecasts)
            }

            # Supply analysis
            if supply_plan:
                dashboard["supply_analysis"] = {
                    "capacity_utilization": supply_plan.get("capacity_utilization", {}),
                    "bottlenecks": supply_plan.get("bottlenecks", []),
                    "production_schedule_status": "on_track" if not supply_plan.get("bottlenecks") else "constrained"
                }

            # Inventory analysis
            if inventory_status:
                dashboard["inventory_analysis"] = {
                    "total_inventory_value": inventory_status.get("total_inventory_value", 0),
                    "inventory_turnover": inventory_status.get("inventory_turnover", 0),
                    "service_levels": inventory_status.get("service_levels", {}),
                    "stockout_risk": inventory_status.get("stockout_risk", "low")
                }

            # Enhanced financial analysis
            if financial_data:
                dashboard["financial_analysis"] = self._calculate_financial_analysis(
                    financial_data, demand_forecasts, inventory_status
                )
            else:
                # Generate default financial analysis based on available data
                dashboard["financial_analysis"] = self._estimate_financial_metrics(
                    demand_forecasts, supply_plan, inventory_status
                )

            # Performance tracking with benchmarking
            dashboard["performance_tracking"] = self._calculate_performance_tracking(
                dashboard, demand_forecasts, supply_plan, inventory_status
            )

            # Generate recommendations
            dashboard["recommendations"] = self._generate_recommendations(
                dashboard["demand_analysis"],
                dashboard["supply_analysis"] if supply_plan else {},
                dashboard["inventory_analysis"] if inventory_status else {},
                dashboard["financial_analysis"]
            )

            # Generate alerts
            dashboard["alerts"] = self._generate_executive_alerts(dashboard)

            # Store dashboard
            dashboard_id = f"DASHBOARD-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            self.executive_metrics[dashboard_id] = dashboard

            return {
                "status": "success",
                "dashboard_id": dashboard_id,
                "dashboard": dashboard
            }

        except Exception as e:
            logger_sop.error(f"Error generating executive dashboard: {e}")
            return {"error": str(e)}

    def _calculate_demand_growth(self, forecasts: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate demand growth rates."""
        growth_rates = {}

        for sku, forecast in forecasts.items():
            if len(forecast) >= 4:  # Need at least 4 periods
                early_avg = np.mean(forecast[:2])
                late_avg = np.mean(forecast[-2:])

                if early_avg > 0:
                    growth_rate = ((late_avg - early_avg) / early_avg) * 100
                    growth_rates[sku] = round(growth_rate, 2)

        avg_growth = np.mean(list(growth_rates.values())) if growth_rates else 0

        return {
            "average_growth_rate": round(avg_growth, 2),
            "sku_growth_rates": growth_rates,
            "growing_skus": len([g for g in growth_rates.values() if g > 5]),
            "declining_skus": len([g for g in growth_rates.values() if g < -5])
        }

    def _calculate_demand_volatility(self, forecasts: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate demand volatility metrics."""
        volatility_scores = {}

        for sku, forecast in forecasts.items():
            if len(forecast) >= 3:
                cv = (np.std(forecast) / np.mean(forecast) * 100) if np.mean(forecast) > 0 else 0
                volatility_scores[sku] = round(cv, 2)

        avg_volatility = np.mean(list(volatility_scores.values())) if volatility_scores else 0

        return {
            "average_volatility": round(avg_volatility, 2),
            "sku_volatility": volatility_scores,
            "high_volatility_skus": len([v for v in volatility_scores.values() if v > 30]),
            "volatility_classification": self._classify_volatility(avg_volatility)
        }

    def _classify_volatility(self, volatility: float) -> str:
        """Classify overall volatility level."""
        if volatility < 15:
            return "LOW"
        elif volatility < 30:
            return "MODERATE"
        else:
            return "HIGH"

    def _get_top_skus(self, forecasts: Dict[str, List[float]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top SKUs by demand volume."""
        sku_totals = [(sku, sum(forecast)) for sku, forecast in forecasts.items()]
        sku_totals.sort(key=lambda x: x[1], reverse=True)

        return [
            {"sku": sku, "total_demand": round(demand, 2)}
            for sku, demand in sku_totals[:top_n]
        ]

    def _calculate_demand_concentration(self, forecasts: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate demand concentration (Pareto analysis)."""
        sku_totals = [sum(forecast) for forecast in forecasts.values()]
        sku_totals.sort(reverse=True)

        total_demand = sum(sku_totals)
        cumulative = 0
        pareto_skus = 0

        for demand in sku_totals:
            cumulative += demand
            pareto_skus += 1
            if cumulative >= total_demand * 0.8:  # 80% of demand
                break

        concentration_ratio = (pareto_skus / len(forecasts) * 100) if forecasts else 0

        return {
            "pareto_skus_count": pareto_skus,
            "total_skus": len(forecasts),
            "concentration_ratio": round(concentration_ratio, 2),
            "concentration_level": "HIGH" if concentration_ratio < 20 else "MODERATE" if concentration_ratio < 40 else "LOW"
        }

    def _generate_recommendations(self, demand_analysis: Dict[str, Any],
                                 supply_analysis: Dict[str, Any],
                                 inventory_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Demand-based recommendations
        growth_rate = demand_analysis.get("demand_growth_rate", {}).get("average_growth_rate", 0)
        if growth_rate > 15:
            recommendations.append("High demand growth detected - consider capacity expansion")
        elif growth_rate < -10:
            recommendations.append("Declining demand trend - review production schedules and inventory levels")

        volatility = demand_analysis.get("demand_volatility_index", {}).get("average_volatility", 0)
        if volatility > 30:
            recommendations.append("High demand volatility - increase safety stock and improve forecast accuracy")

        # Supply-based recommendations
        bottlenecks = supply_analysis.get("bottlenecks", [])
        if bottlenecks:
            recommendations.append(f"Address {len(bottlenecks)} capacity bottlenecks in production schedule")

        # Inventory-based recommendations
        turnover = inventory_analysis.get("inventory_turnover", 0)
        if turnover < 4:
            recommendations.append("Low inventory turnover - consider inventory reduction initiatives")

        return recommendations

    def _generate_executive_alerts(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate executive-level alerts."""
        alerts = []

        # Demand alerts
        growth_rate = dashboard["demand_analysis"].get("demand_growth_rate", {}).get("average_growth_rate", 0)
        if abs(growth_rate) > 20:
            alerts.append({
                "type": "demand_shift",
                "severity": "high" if abs(growth_rate) > 30 else "medium",
                "message": f"Significant demand {'growth' if growth_rate > 0 else 'decline'}: {growth_rate:.1f}%"
            })

        # Supply alerts
        bottlenecks = dashboard["supply_analysis"].get("bottlenecks", [])
        critical_bottlenecks = [b for b in bottlenecks if b.get("severity") == "CRITICAL"]
        if critical_bottlenecks:
            alerts.append({
                "type": "capacity_constraint",
                "severity": "critical",
                "message": f"{len(critical_bottlenecks)} critical capacity bottlenecks identified"
            })

        # Inventory alerts
        stockout_risk = dashboard["inventory_analysis"].get("stockout_risk", "low")
        if stockout_risk == "high":
            alerts.append({
                "type": "stockout_risk",
                "severity": "high",
                "message": "High stockout risk detected - review inventory levels"
            })

        return alerts

    def performance_management(self,
                               historical_forecasts: Dict[str, List[float]],
                               actuals: Dict[str, List[float]],
                               targets: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate performance metrics and track against targets.

        Args:
            historical_forecasts: Historical forecast data
            actuals: Actual demand data
            targets: Optional target values for metrics
        """
        try:
            targets = targets or self.config.get("performance_targets", {})

            performance_metrics = {
                "forecast_accuracy": {},
                "inventory_performance": {},
                "customer_service": {},
                "financial_performance": {},
                "overall_score": 0
            }

            # Calculate forecast accuracy metrics
            accuracy_results = self._calculate_forecast_accuracy(historical_forecasts, actuals)
            performance_metrics["forecast_accuracy"] = accuracy_results

            # Compare against targets
            target_accuracy = targets.get("forecast_accuracy", 90)
            current_accuracy = accuracy_results.get("weighted_mape", 100)

            performance_metrics["forecast_accuracy"]["target"] = target_accuracy
            performance_metrics["forecast_accuracy"]["gap"] = current_accuracy - target_accuracy
            performance_metrics["forecast_accuracy"]["status"] = "on_track" if current_accuracy <= target_accuracy else "off_track"

            # Calculate overall performance score
            metric_scores = []

            if current_accuracy <= target_accuracy:
                metric_scores.append(100)
            else:
                metric_scores.append(max(0, 100 - (current_accuracy - target_accuracy) * 2))

            performance_metrics["overall_score"] = round(np.mean(metric_scores), 2) if metric_scores else 0

            return {
                "status": "success",
                "performance_metrics": performance_metrics,
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_sop.error(f"Error in performance management: {e}")
            return {"error": str(e)}

    def _calculate_forecast_accuracy(self, forecasts: Dict[str, List[float]],
                                    actuals: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate forecast accuracy metrics."""
        accuracy_metrics = {
            "mape": [],
            "mad": [],
            "bias": [],
            "weighted_mape": 0
        }

        total_forecast = 0
        total_absolute_error = 0

        for sku in forecasts.keys():
            if sku not in actuals:
                continue

            forecast = forecasts[sku]
            actual = actuals[sku]

            # Align lengths
            min_len = min(len(forecast), len(actual))
            forecast = forecast[:min_len]
            actual = actual[:min_len]

            if not forecast or not actual:
                continue

            # Calculate metrics
            forecast_array = np.array(forecast)
            actual_array = np.array(actual)

            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actual_array - forecast_array) / (actual_array + 1e-8))) * 100
            accuracy_metrics["mape"].append(mape)

            # MAD (Mean Absolute Deviation)
            mad = np.mean(np.abs(actual_array - forecast_array))
            accuracy_metrics["mad"].append(mad)

            # Bias
            bias = np.mean(forecast_array - actual_array)
            accuracy_metrics["bias"].append(bias)

            # Weighted MAPE
            total_forecast += np.sum(forecast_array)
            total_absolute_error += np.sum(np.abs(actual_array - forecast_array))

        # Calculate aggregates
        if accuracy_metrics["mape"]:
            accuracy_metrics["average_mape"] = round(np.mean(accuracy_metrics["mape"]), 2)
            accuracy_metrics["average_mad"] = round(np.mean(accuracy_metrics["mad"]), 2)
            accuracy_metrics["average_bias"] = round(np.mean(accuracy_metrics["bias"]), 2)

        if total_forecast > 0:
            accuracy_metrics["weighted_mape"] = round((total_absolute_error / total_forecast) * 100, 2)

        return accuracy_metrics

    def get_forecast_version_history(self, sku: Optional[str] = None) -> Dict[str, Any]:
        """
        Get version history of forecasts.

        Args:
            sku: Optional SKU filter
        """
        try:
            versions = []

            for forecast_id, forecast_data in self.consensus_forecasts.items():
                if sku and sku not in forecast_data["forecasts"]:
                    continue

                versions.append({
                    "forecast_id": forecast_id,
                    "created_at": forecast_data["created_at"],
                    "status": forecast_data["status"],
                    "sku_count": len(forecast_data["forecasts"]),
                    "submitted_by": forecast_data.get("submitted_by"),
                    "approved_at": forecast_data.get("approved_at")
                })

            # Sort by creation date
            versions.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "status": "success",
                "versions": versions,
                "total_versions": len(versions)
            }

        except Exception as e:
            logger_sop.error(f"Error getting forecast version history: {e}")
            return {"error": str(e)}

    def scenario_comparison(self, base_scenario: Dict[str, Any],
                           comparison_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple planning scenarios side by side.

        Args:
            base_scenario: Base case scenario
            comparison_scenarios: List of alternative scenarios
        """
        try:
            comparison = {
                "base_scenario": base_scenario,
                "scenarios": [],
                "analysis": {}
            }

            for idx, scenario in enumerate(comparison_scenarios):
                scenario_analysis = {
                    "scenario_id": f"SCENARIO-{idx + 1}",
                    "name": scenario.get("name", f"Scenario {idx + 1}"),
                    "description": scenario.get("description", ""),
                    "metrics": scenario.get("metrics", {}),
                    "vs_base": self._compare_to_base(base_scenario, scenario)
                }
                comparison["scenarios"].append(scenario_analysis)

            # Overall analysis
            comparison["analysis"] = {
                "best_revenue_scenario": self._find_best_scenario(comparison["scenarios"], "revenue"),
                "best_cost_scenario": self._find_best_scenario(comparison["scenarios"], "cost"),
                "best_service_scenario": self._find_best_scenario(comparison["scenarios"], "service_level"),
                "recommendation": self._generate_scenario_recommendation(comparison["scenarios"])
            }

            return {
                "status": "success",
                "comparison": comparison,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_sop.error(f"Error in scenario comparison: {e}")
            return {"error": str(e)}

    def _compare_to_base(self, base: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Compare scenario to base case."""
        comparison = {}

        base_metrics = base.get("metrics", {})
        scenario_metrics = scenario.get("metrics", {})

        for metric in ["revenue", "cost", "service_level", "inventory_investment"]:
            if metric in base_metrics and metric in scenario_metrics:
                base_value = base_metrics[metric]
                scenario_value = scenario_metrics[metric]

                if base_value > 0:
                    change_pct = ((scenario_value - base_value) / base_value) * 100
                    comparison[metric] = {
                        "base": base_value,
                        "scenario": scenario_value,
                        "change": round(scenario_value - base_value, 2),
                        "change_percentage": round(change_pct, 2),
                        "direction": "positive" if change_pct > 0 else "negative"
                    }

        return comparison

    def _find_best_scenario(self, scenarios: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        """Find best scenario for specific metric."""
        best_scenario = None
        best_value = float('-inf') if metric in ["revenue", "service_level"] else float('inf')

        for scenario in scenarios:
            comparison = scenario.get("vs_base", {})
            if metric in comparison:
                value = comparison[metric].get("scenario", 0)

                if metric in ["revenue", "service_level"]:
                    if value > best_value:
                        best_value = value
                        best_scenario = scenario
                else:  # cost, inventory_investment (lower is better)
                    if value < best_value:
                        best_value = value
                        best_scenario = scenario

        return best_scenario or {"name": "none", "value": 0}

    def _generate_scenario_recommendation(self, scenarios: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on scenario analysis."""
        if not scenarios:
            return "No scenarios available for comparison"

        # Simple heuristic: recommend scenario with best balance
        # This would be more sophisticated in a real implementation
        positive_changes = []
        for scenario in scenarios:
            comparison = scenario.get("vs_base", {})
            revenue_change = comparison.get("revenue", {}).get("change_percentage", 0)
            cost_change = comparison.get("cost", {}).get("change_percentage", 0)

            if revenue_change > 5 and cost_change < 10:
                positive_changes.append(scenario["name"])

        if positive_changes:
            return f"Recommended: {positive_changes[0]} (positive revenue impact with controlled cost)"
        return "No clearly superior scenario identified - requires executive review"

    def _calculate_financial_analysis(self, financial_data: Dict[str, Any],
                                     demand_forecasts: Dict[str, List[float]],
                                     inventory_status: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive financial analysis."""
        try:
            financial_analysis = {
                "revenue_analysis": {},
                "cost_analysis": {},
                "margin_analysis": {},
                "working_capital_analysis": {},
                "profitability_metrics": {}
            }

            # Revenue analysis
            if "revenue_forecast" in financial_data:
                revenue = financial_data["revenue_forecast"]
                total_demand = sum(sum(f) for f in demand_forecasts.values())

                financial_analysis["revenue_analysis"] = {
                    "total_revenue": round(revenue, 2),
                    "revenue_per_unit": round(revenue / total_demand, 2) if total_demand > 0 else 0,
                    "revenue_growth": financial_data.get("revenue_growth", 0),
                    "revenue_by_sku": self._calculate_revenue_by_sku(demand_forecasts, financial_data)
                }

            # Cost analysis
            if "cost_forecast" in financial_data:
                cost = financial_data["cost_forecast"]
                total_demand = sum(sum(f) for f in demand_forecasts.values())

                financial_analysis["cost_analysis"] = {
                    "total_cost": round(cost, 2),
                    "cost_per_unit": round(cost / total_demand, 2) if total_demand > 0 else 0,
                    "cost_breakdown": financial_data.get("cost_breakdown", {
                        "production": 0.4,
                        "transportation": 0.2,
                        "inventory": 0.2,
                        "overhead": 0.2
                    }),
                    "cost_variance": financial_data.get("cost_variance", 0)
                }

            # Margin analysis
            if "margin_forecast" in financial_data:
                margin = financial_data["margin_forecast"]
                revenue = financial_data.get("revenue_forecast", 1)

                financial_analysis["margin_analysis"] = {
                    "gross_margin": round(margin, 2),
                    "margin_percentage": round((margin / revenue * 100) if revenue > 0 else 0, 2),
                    "margin_trend": financial_data.get("margin_trend", "stable"),
                    "contribution_margin": financial_data.get("contribution_margin", 0)
                }

            # Working capital analysis
            if "working_capital" in financial_data:
                working_capital = financial_data["working_capital"]

                financial_analysis["working_capital_analysis"] = {
                    "total_working_capital": round(working_capital, 2),
                    "inventory_investment": inventory_status.get("total_inventory_value", 0),
                    "receivables": financial_data.get("receivables", 0),
                    "payables": financial_data.get("payables", 0),
                    "cash_conversion_cycle": financial_data.get("cash_conversion_cycle", 0)
                }

            # Profitability metrics
            financial_analysis["profitability_metrics"] = {
                "roi": financial_data.get("roi", 0),
                "roa": financial_data.get("roa", 0),
                "roe": financial_data.get("roe", 0),
                "economic_value_added": financial_data.get("eva", 0)
            }

            return financial_analysis

        except Exception as e:
            logger_sop.error(f"Error calculating financial analysis: {e}")
            return {"error": str(e)}

    def _estimate_financial_metrics(self, demand_forecasts: Dict[str, List[float]],
                                   supply_plan: Dict[str, Any],
                                   inventory_status: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate financial metrics when not provided."""
        try:
            total_demand = sum(sum(f) for f in demand_forecasts.values())

            # Default assumptions for estimation
            avg_price = 100.0  # Default price per unit
            avg_cost = 60.0    # Default cost per unit

            estimated_revenue = total_demand * avg_price
            estimated_cost = total_demand * avg_cost
            estimated_margin = estimated_revenue - estimated_cost

            # Estimate working capital
            inventory_value = inventory_status.get("total_inventory_value", total_demand * avg_cost * 0.5)
            estimated_working_capital = inventory_value * 1.5

            return {
                "revenue_analysis": {
                    "total_revenue": round(estimated_revenue, 2),
                    "revenue_per_unit": avg_price,
                    "revenue_growth": 0,
                    "estimated": True
                },
                "cost_analysis": {
                    "total_cost": round(estimated_cost, 2),
                    "cost_per_unit": avg_cost,
                    "cost_breakdown": {
                        "production": 0.4,
                        "transportation": 0.2,
                        "inventory": 0.2,
                        "overhead": 0.2
                    },
                    "estimated": True
                },
                "margin_analysis": {
                    "gross_margin": round(estimated_margin, 2),
                    "margin_percentage": round((estimated_margin / estimated_revenue * 100) if estimated_revenue > 0 else 0, 2),
                    "estimated": True
                },
                "working_capital_analysis": {
                    "total_working_capital": round(estimated_working_capital, 2),
                    "inventory_investment": round(inventory_value, 2),
                    "estimated": True
                },
                "profitability_metrics": {
                    "roi": 15.0,  # Default assumption
                    "estimated": True
                }
            }

        except Exception as e:
            logger_sop.error(f"Error estimating financial metrics: {e}")
            return {"error": str(e)}

    def _calculate_revenue_by_sku(self, demand_forecasts: Dict[str, List[float]],
                                 financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate revenue contribution by SKU."""
        revenue_by_sku = {}

        # Use default price if not provided
        default_price = 100.0
        sku_prices = financial_data.get("sku_prices", {})

        for sku, forecast in demand_forecasts.items():
            price = sku_prices.get(sku, default_price)
            total_demand = sum(forecast)
            revenue_by_sku[sku] = round(total_demand * price, 2)

        return revenue_by_sku

    def _calculate_performance_tracking(self, dashboard: Dict[str, Any],
                                      demand_forecasts: Dict[str, List[float]],
                                      supply_plan: Dict[str, Any],
                                      inventory_status: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance tracking with benchmarking."""
        try:
            performance_tracking = {
                "kpi_metrics": {},
                "benchmarking": {},
                "trend_analysis": {},
                "scorecard": {}
            }

            # Get performance targets from config
            targets = self.config.get("performance_targets", {})

            # Forecast accuracy tracking
            forecast_accuracy = dashboard.get("demand_analysis", {}).get("demand_volatility_index", {}).get("average_volatility", 0)
            accuracy_score = max(0, 100 - forecast_accuracy)  # Convert volatility to accuracy score
            target_accuracy = targets.get("forecast_accuracy", 90)

            performance_tracking["kpi_metrics"]["forecast_accuracy"] = {
                "current": round(accuracy_score, 2),
                "target": target_accuracy,
                "variance": round(accuracy_score - target_accuracy, 2),
                "status": "on_track" if accuracy_score >= target_accuracy else "below_target"
            }

            # Inventory turnover tracking
            inventory_turnover = inventory_status.get("inventory_turnover", 0) if inventory_status else 0
            target_turnover = targets.get("inventory_turnover", 8)

            performance_tracking["kpi_metrics"]["inventory_turnover"] = {
                "current": round(inventory_turnover, 2),
                "target": target_turnover,
                "variance": round(inventory_turnover - target_turnover, 2),
                "status": "on_track" if inventory_turnover >= target_turnover else "below_target"
            }

            # Service level tracking
            service_levels = inventory_status.get("service_levels", {}) if inventory_status else {}
            avg_service_level = np.mean(list(service_levels.values())) if service_levels else 95
            target_service = targets.get("service_level", 95)

            performance_tracking["kpi_metrics"]["service_level"] = {
                "current": round(avg_service_level, 2),
                "target": target_service,
                "variance": round(avg_service_level - target_service, 2),
                "status": "on_track" if avg_service_level >= target_service else "below_target"
            }

            # Working capital efficiency
            working_capital = dashboard.get("financial_analysis", {}).get("working_capital_analysis", {}).get("total_working_capital", 0)
            revenue = dashboard.get("financial_analysis", {}).get("revenue_analysis", {}).get("total_revenue", 1)
            working_capital_efficiency = (working_capital / revenue * 100) if revenue > 0 else 0
            target_efficiency = targets.get("working_capital_efficiency", 85)

            performance_tracking["kpi_metrics"]["working_capital_efficiency"] = {
                "current": round(working_capital_efficiency, 2),
                "target": target_efficiency,
                "variance": round(working_capital_efficiency - target_efficiency, 2),
                "status": "on_track" if working_capital_efficiency <= target_efficiency else "above_target"
            }

            # Benchmarking (simplified - would use industry benchmarks in production)
            performance_tracking["benchmarking"] = {
                "forecast_accuracy": {
                    "current": round(accuracy_score, 2),
                    "industry_average": 85,
                    "top_quartile": 92,
                    "percentile": self._calculate_percentile(accuracy_score, 85, 92)
                },
                "inventory_turnover": {
                    "current": round(inventory_turnover, 2),
                    "industry_average": 6,
                    "top_quartile": 10,
                    "percentile": self._calculate_percentile(inventory_turnover, 6, 10)
                }
            }

            # Scorecard calculation
            scorecard_score = self._calculate_scorecard_score(performance_tracking["kpi_metrics"])
            performance_tracking["scorecard"] = {
                "overall_score": scorecard_score,
                "grade": self._calculate_grade(scorecard_score),
                "color": self._get_score_color(scorecard_score)
            }

            return performance_tracking

        except Exception as e:
            logger_sop.error(f"Error calculating performance tracking: {e}")
            return {"error": str(e)}

    def _calculate_percentile(self, value: float, average: float, top_quartile: float) -> str:
        """Calculate percentile bracket."""
        if value >= top_quartile:
            return "top_quartile"
        elif value >= average:
            return "above_average"
        else:
            return "below_average"

    def _calculate_scorecard_score(self, kpi_metrics: Dict[str, Any]) -> float:
        """Calculate overall scorecard score from KPI metrics."""
        scores = []

        for kpi_name, kpi_data in kpi_metrics.items():
            if kpi_data["status"] == "on_track":
                scores.append(100)
            else:
                # Calculate partial score based on variance
                variance = abs(kpi_data["variance"])
                scores.append(max(0, 100 - variance * 2))

        return round(np.mean(scores), 2) if scores else 0

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _get_score_color(self, score: float) -> str:
        """Get color code for score."""
        if score >= 90:
            return "green"
        elif score >= 70:
            return "yellow"
        else:
            return "red"
