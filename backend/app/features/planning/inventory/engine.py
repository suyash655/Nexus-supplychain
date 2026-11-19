"""
NEXUS — Inventory Optimization Engine (SAP IBP-style)
=====================================================
Multi-echelon inventory optimization, safety stock calculation,
and service level optimization.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

logger_io = logging.getLogger("nexus.inventory_optimization")


class InventoryOptimizationEngine:
    """
    Enterprise inventory optimization with multi-echelon analysis,
    safety stock optimization, and service level management.
    """

    def __init__(self):
        self.inventory_policies = {}
        self.service_levels = {}
        self._initialised = False

    def initialize(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Initialize inventory optimization with inventory data.

        Expected columns:
        - sku: product identifier
        - warehouse: location
        - current_inventory: current stock level
        - demand_rate: average daily demand
        - lead_time_days: supplier lead time
        - holding_cost: annual holding cost per unit
        - ordering_cost: cost per order
        - service_level_target: target service level (0-1)
        """
        try:
            if "sku" not in df.columns or "warehouse" not in df.columns:
                return {"error": "Missing required columns: sku, warehouse", "initialised": False}

            results = {
                "status": "success",
                "locations": [],
                "skus": [],
                "echelons": [],
                "initialised_at": datetime.now(timezone.utc).isoformat()
            }

            results["locations"] = df["warehouse"].unique().tolist()
            results["skus"] = df["sku"].unique().tolist()

            # Determine echelons (simplified: suppliers -> warehouses -> customers)
            if "supplier" in df.columns:
                results["echelons"] = ["supplier", "warehouse", "customer"]
            else:
                results["echelons"] = ["warehouse", "customer"]

            self._initialised = True
            return results

        except Exception as e:
            logger_io.error(f"Error initializing inventory optimization: {e}")
            return {"error": str(e), "initialised": False}

    def calculate_safety_stock(self, demand_data: pd.DataFrame,
                              lead_times: Dict[str, int],
                              service_levels: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate optimal safety stock levels using statistical methods.

        Args:
            demand_data: Historical demand data with sku, date, quantity
            lead_times: SKU -> lead time in days
            service_levels: SKU -> target service level (0-1)
        """
        try:
            safety_stocks = {}

            for sku in demand_data["sku"].unique():
                sku_data = demand_data[demand_data["sku"] == sku]["quantity"]

                # Calculate demand statistics
                mean_demand = sku_data.mean()
                std_demand = sku_data.std()

                if std_demand == 0:
                    std_demand = mean_demand * 0.2  # Assume 20% variability if no variation

                lead_time = lead_times.get(sku, 7)
                service_level = service_levels.get(sku, 0.95)

                # Calculate safety stock using normal distribution
                z_score = stats.norm.ppf(service_level)
                demand_std_during_lead = std_demand * np.sqrt(lead_time)
                safety_stock = z_score * demand_std_during_lead

                # Calculate reorder point
                reorder_point = (mean_demand * lead_time) + safety_stock

                safety_stocks[sku] = {
                    "mean_daily_demand": round(mean_demand, 2),
                    "demand_std_dev": round(std_demand, 2),
                    "lead_time_days": lead_time,
                    "service_level": service_level,
                    "z_score": round(z_score, 3),
                    "safety_stock": round(max(0, safety_stock), 2),
                    "reorder_point": round(reorder_point, 2),
                    "cycle_stock": round(mean_demand * lead_time, 2)
                }

            return {
                "status": "success",
                "safety_stocks": safety_stocks,
                "total_skus": len(safety_stocks),
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error calculating safety stock: {e}")
            return {"error": str(e)}

    def economic_order_quantity(self, demand_data: pd.DataFrame,
                               costs: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Calculate Economic Order Quantity (EOQ) for each SKU.

        Args:
            demand_data: Demand data with sku, annual_demand
            costs: SKU -> {holding_cost, ordering_cost}
        """
        try:
            eoq_results = {}

            for sku in demand_data["sku"].unique():
                sku_data = demand_data[demand_data["sku"] == sku]
                annual_demand = sku_data["quantity"].sum() * 12  # Monthly to annual

                holding_cost = costs.get(sku, {}).get("holding_cost", 0.25)
                ordering_cost = costs.get(sku, {}).get("ordering_cost", 50.0)

                # EOQ formula: sqrt(2 * D * S / H)
                # D = annual demand, S = ordering cost, H = holding cost per unit per year
                eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

                # Calculate total cost at EOQ
                total_holding_cost = (eoq / 2) * holding_cost
                total_ordering_cost = (annual_demand / eoq) * ordering_cost
                total_cost = total_holding_cost + total_ordering_cost

                # Calculate reorder frequency
                orders_per_year = annual_demand / eoq
                days_between_orders = 365 / orders_per_year

                eoq_results[sku] = {
                    "annual_demand": round(annual_demand, 2),
                    "holding_cost_per_unit": holding_cost,
                    "ordering_cost_per_order": ordering_cost,
                    "eoq": round(eoq, 2),
                    "total_holding_cost": round(total_holding_cost, 2),
                    "total_ordering_cost": round(total_ordering_cost, 2),
                    "total_cost": round(total_cost, 2),
                    "orders_per_year": round(orders_per_year, 2),
                    "days_between_orders": round(days_between_orders, 1)
                }

            return {
                "status": "success",
                "eoq_results": eoq_results,
                "total_skus": len(eoq_results),
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error calculating EOQ: {e}")
            return {"error": str(e)}

    def multi_echelon_optimization(self, network_data: pd.DataFrame,
                                   demand_forecast: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Perform multi-echelon inventory optimization.
        Optimizes inventory across multiple supply chain stages.

        Args:
            network_data: Network structure with sku, echelon, location, capacity
            demand_forecast: SKU -> demand by period
        """
        try:
            echelon_analysis = {}

            # Analyze each echelon
            for echelon in network_data["echelon"].unique() if "echelon" in network_data.columns else ["warehouse"]:
                echelon_data = network_data[network_data.get("echelon", pd.Series(["warehouse"] * len(network_data))) == echelon]

                echelon_analysis[echelon] = {
                    "locations": echelon_data["location"].unique().tolist() if "location" in echelon_data.columns else [],
                    "total_capacity": echelon_data["capacity"].sum() if "capacity" in echelon_data.columns else 0,
                    "skus_handled": echelon_data["sku"].nunique() if "sku" in echelon_data.columns else 0
                }

            # Calculate echelon service levels
            service_levels = {}
            for sku in demand_forecast.keys():
                # Simplified: calculate service level at each echelon
                base_service = 0.95
                echelon_service = {
                    "upstream": base_service * 0.98,  # Slightly lower at upstream
                    "midstream": base_service,
                    "downstream": base_service * 1.02  # Slightly higher at downstream
                }
                service_levels[sku] = echelon_service

            # Calculate inventory placement optimization
            # This is a simplified version - real implementation would use optimization algorithms
            placement_recommendations = []

            for sku, demand in demand_forecast.items():
                total_demand = sum(demand)

                # Recommend placement based on demand volume and variability
                if total_demand > 1000:
                    placement = "decentralized"  # High volume: stock at multiple locations
                elif total_demand > 100:
                    placement = "centralized"  # Medium volume: central warehouse
                else:
                    placement = "make-to-order"  # Low volume: no stock

                placement_recommendations.append({
                    "sku": sku,
                    "total_demand": total_demand,
                    "recommended_placement": placement,
                    "rationale": self._get_placement_rationale(placement, total_demand)
                })

            return {
                "status": "success",
                "echelon_analysis": echelon_analysis,
                "service_levels": service_levels,
                "placement_recommendations": placement_recommendations,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in multi-echelon optimization: {e}")
            return {"error": str(e)}

    def inventory_positioning_optimization(self, network_data: pd.DataFrame,
                                          demand_forecast: Dict[str, List[float]],
                                          cost_parameters: Dict[str, Dict[str, float]],
                                          lead_times: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Optimize inventory positioning (push vs pull strategies).
        Determines optimal placement of inventory across the supply chain network
        with advanced cost-benefit analysis and postponement strategy evaluation.

        Args:
            network_data: Network structure with sku, echelon, location, capacity, cost
            demand_forecast: SKU -> demand by period
            cost_parameters: Location -> {holding_cost, transportation_cost, stockout_cost}
            lead_times: Optional Location -> lead time in days
        """
        try:
            positioning_results = {}
            lead_times = lead_times or {}

            for sku in demand_forecast.keys():
                sku_network = network_data[network_data["sku"] == sku] if "sku" in network_data.columns else network_data
                total_demand = sum(demand_forecast[sku])
                demand_variability = np.std(demand_forecast[sku]) / (np.mean(demand_forecast[sku]) + 1e-8)

                # Analyze each location in the network
                location_analysis = []

                for _, location in sku_network.iterrows():
                    loc_name = location.get("location", "unknown")
                    echelon = location.get("echelon", "warehouse")
                    capacity = location.get("capacity", float('inf'))

                    # Calculate location-specific metrics
                    holding_cost = cost_parameters.get(loc_name, {}).get("holding_cost", 0.25)
                    transp_cost = cost_parameters.get(loc_name, {}).get("transportation_cost", 1.0)
                    stockout_cost = cost_parameters.get(loc_name, {}).get("stockout_cost", 10.0)
                    lead_time = lead_times.get(loc_name, 7)

                    # Calculate push vs pull suitability score
                    # Push: Centralized, low demand variability, high transportation cost
                    # Pull: Decentralized, high demand variability, low holding cost

                    # Push score factors
                    push_score = (
                        (1 / (demand_variability + 0.1)) * 0.4 +  # Low variability favors push
                        (transp_cost / 10.0) * 0.3 +  # High transport cost favors push
                        (1 / (holding_cost + 0.1)) * 0.3  # Low holding cost favors push
                    )

                    # Pull score factors
                    pull_score = (
                        demand_variability * 0.4 +  # High variability favors pull
                        (holding_cost / 10.0) * 0.3 +  # Low holding cost favors pull
                        (1 / (transp_cost + 0.1)) * 0.3  # Low transport cost favors pull
                    )

                    # Determine optimal strategy
                    if push_score > pull_score:
                        strategy = "push"
                        strategy_score = push_score
                    else:
                        strategy = "pull"
                        strategy_score = pull_score

                    # Calculate optimal inventory level at this location
                    if strategy == "push":
                        # Push: Stock based on forecast, push downstream
                        optimal_stock = total_demand * 0.8  # 80% of demand at central location
                    else:
                        # Pull: Stock based on local demand, replenish as needed
                        optimal_stock = total_demand / len(sku_network)  # Distribute evenly

                    # Calculate cost implications
                    holding_cost_total = optimal_stock * holding_cost
                    transp_cost_total = optimal_stock * transp_cost
                    expected_stockout_cost = (1 - 0.95) * total_demand * stockout_cost  # Assume 95% service level
                    total_location_cost = holding_cost_total + transp_cost_total + expected_stockout_cost

                    # Calculate postponement suitability
                    # Postponement: Delay final product configuration until demand is known
                    postponement_score = (
                        (demand_variability * 0.5) +  # High variability favors postponement
                        (1 / (lead_time + 1)) * 0.3 +  # Shorter lead times favor postponement
                        (holding_cost / 10.0) * 0.2  # Higher holding costs favor postponement
                    )

                    location_analysis.append({
                        "location": loc_name,
                        "echelon": echelon,
                        "capacity": capacity,
                        "lead_time_days": lead_time,
                        "push_score": round(push_score, 3),
                        "pull_score": round(pull_score, 3),
                        "optimal_strategy": strategy,
                        "strategy_score": round(strategy_score, 3),
                        "optimal_inventory_level": round(optimal_stock, 2),
                        "holding_cost": holding_cost,
                        "transportation_cost": transp_cost,
                        "stockout_cost": stockout_cost,
                        "cost_analysis": {
                            "holding_cost_total": round(holding_cost_total, 2),
                            "transportation_cost_total": round(transp_cost_total, 2),
                            "expected_stockout_cost": round(expected_stockout_cost, 2),
                            "total_location_cost": round(total_location_cost, 2)
                        },
                        "postponement_score": round(postponement_score, 3),
                        "postponement_recommended": postponement_score > 0.5
                    })

                # Aggregate network recommendations
                push_locations = [loc["location"] for loc in location_analysis if loc["optimal_strategy"] == "push"]
                pull_locations = [loc["location"] for loc in location_analysis if loc["optimal_strategy"] == "pull"]
                postponement_locations = [loc["location"] for loc in location_analysis if loc["postponement_recommended"]]

                # Calculate network-wide metrics
                avg_push_score = np.mean([loc["push_score"] for loc in location_analysis])
                avg_pull_score = np.mean([loc["pull_score"] for loc in location_analysis])
                avg_postponement_score = np.mean([loc["postponement_score"] for loc in location_analysis])

                network_strategy = "push" if avg_push_score > avg_pull_score else "pull"

                # Calculate total network cost
                total_network_cost = sum(loc["cost_analysis"]["total_location_cost"] for loc in location_analysis)

                positioning_results[sku] = {
                    "total_demand": total_demand,
                    "demand_variability": round(demand_variability, 3),
                    "network_strategy": network_strategy,
                    "push_locations": push_locations,
                    "pull_locations": pull_locations,
                    "postponement_locations": postponement_locations,
                    "location_analysis": location_analysis,
                    "network_efficiency_score": round(max(avg_push_score, avg_pull_score), 3),
                    "postponement_score": round(avg_postponement_score, 3),
                    "total_network_cost": round(total_network_cost, 2),
                    "recommendations": self._generate_positioning_recommendations(location_analysis, network_strategy, avg_postponement_score)
                }

            return {
                "status": "success",
                "positioning_optimization": positioning_results,
                "total_skus": len(positioning_results),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in inventory positioning optimization: {e}")
            return {"error": str(e)}

    def _generate_positioning_recommendations(self, location_analysis: List[Dict], network_strategy: str, avg_postponement_score: float) -> List[str]:
        """Generate recommendations based on positioning analysis."""
        recommendations = []

        if network_strategy == "push":
            recommendations.append("Implement push-based strategy with centralized inventory")
            recommendations.append("Establish central distribution center with high stock levels")
            recommendations.append("Use forecast-driven replenishment to downstream locations")
        else:
            recommendations.append("Implement pull-based strategy with decentralized inventory")
            recommendations.append("Stock inventory closer to demand points")
            recommendations.append("Use demand-driven replenishment (Kanban, reorder points)")

        # Mixed strategy recommendations
        push_count = sum(1 for loc in location_analysis if loc["optimal_strategy"] == "push")
        pull_count = len(location_analysis) - push_count

        if push_count > 0 and pull_count > 0:
            recommendations.append(f"Mixed strategy: {push_count} push locations, {pull_count} pull locations")
            recommendations.append("Consider hybrid push-pull strategy (postponement)")

        # Postponement recommendations
        if avg_postponement_score > 0.5:
            recommendations.append("High postponement suitability - consider delayed product differentiation")
            recommendations.append("Implement modular design for late-stage customization")
        elif avg_postponement_score > 0.3:
            recommendations.append("Moderate postponement potential - evaluate selective postponement")

        # Capacity-based recommendations
        constrained_locations = [loc for loc in location_analysis if loc.get("optimal_inventory_level", 0) > loc.get("capacity", float('inf'))]
        if constrained_locations:
            recommendations.append(f"Capacity constraints at {len(constrained_locations)} locations - consider expansion or redistribution")

        # Cost optimization recommendations
        high_cost_locations = [loc for loc in location_analysis if loc.get("cost_analysis", {}).get("total_location_cost", 0) > 10000]
        if high_cost_locations:
            recommendations.append(f"High costs at {len(high_cost_locations)} locations - review cost structure and optimization opportunities")

        return recommendations

    def _get_placement_rationale(self, placement: str, demand: float) -> str:
        """Get rationale for inventory placement recommendation."""
        if placement == "decentralized":
            return f"High demand ({demand}) justifies multiple stocking points"
        elif placement == "centralized":
            return f"Moderate demand ({demand}) suitable for central distribution"
        else:
            return f"Low demand ({demand}) - consider make-to-order"

    def service_level_optimization(self, current_service_levels: Dict[str, float],
                                  inventory_costs: Dict[str, float],
                                  stockout_costs: Dict[str, float],
                                  demand_std_dev: Optional[Dict[str, float]] = None,
                                  annual_demand: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Advanced service level optimization with cost trade-offs.
        Balances inventory holding costs vs. stockout costs using newsvendor model
        with multi-objective optimization and sensitivity analysis.

        Args:
            current_service_levels: SKU -> current service level
            inventory_costs: SKU -> annual holding cost per unit
            stockout_costs: SKU -> cost per stockout event
            demand_std_dev: Optional SKU -> demand standard deviation
            annual_demand: Optional SKU -> annual demand volume
        """
        try:
            optimized_levels = {}
            demand_std_dev = demand_std_dev or {}
            annual_demand = annual_demand or {}

            for sku in current_service_levels.keys():
                current_sl = current_service_levels[sku]
                holding_cost = inventory_costs.get(sku, 1.0)
                stockout_cost = stockout_costs.get(sku, 10.0)
                std_dev = demand_std_dev.get(sku, 10.0)
                ann_demand = annual_demand.get(sku, 1000.0)

                # Critical ratio (Newsvendor model)
                # CR = Cu / (Cu + Co) where Cu = cost of underage, Co = cost of overage
                critical_ratio = stockout_cost / (stockout_cost + holding_cost)

                # Convert critical ratio to service level
                optimal_sl = critical_ratio

                # Calculate safety stock at different service levels
                def calculate_safety_stock(sl):
                    return stats.norm.ppf(sl) * std_dev

                # Calculate total cost function
                def calculate_total_cost(sl):
                    ss = calculate_safety_stock(sl)
                    holding_cost_total = ss * holding_cost
                    # Expected stockout cost = (1 - SL) * stockout_cost * annual_demand
                    expected_stockouts = (1 - sl) * ann_demand
                    stockout_cost_total = expected_stockouts * stockout_cost
                    return holding_cost_total + stockout_cost_total

                # Calculate cost implications
                current_safety_stock = calculate_safety_stock(current_sl)
                optimal_safety_stock = calculate_safety_stock(optimal_sl)

                current_total_cost = calculate_total_cost(current_sl)
                optimal_total_cost = calculate_total_cost(optimal_sl)

                current_holding_cost = current_safety_stock * holding_cost
                optimal_holding_cost = optimal_safety_stock * holding_cost

                cost_change = optimal_total_cost - current_total_cost
                cost_savings_percentage = ((current_total_cost - optimal_total_cost) / current_total_cost * 100) if current_total_cost > 0 else 0

                # Sensitivity analysis - test service levels around optimal
                sensitivity_analysis = []
                test_sls = [max(0.5, optimal_sl - 0.1), optimal_sl, min(0.99, optimal_sl + 0.1)]
                for test_sl in test_sls:
                    test_cost = calculate_total_cost(test_sl)
                    sensitivity_analysis.append({
                        "service_level": round(test_sl, 3),
                        "total_cost": round(test_cost, 2),
                        "safety_stock": round(calculate_safety_stock(test_sl), 2)
                    })

                # Calculate cost curve for visualization
                cost_curve = []
                for sl in np.linspace(0.7, 0.99, 10):
                    cost_curve.append({
                        "service_level": round(sl, 3),
                        "total_cost": round(calculate_total_cost(sl), 2),
                        "holding_cost": round(calculate_safety_stock(sl) * holding_cost, 2),
                        "stockout_cost": round((1 - sl) * ann_demand * stockout_cost, 2)
                    })

                # Multi-objective analysis
                cost_weight = 0.6
                service_weight = 0.4
                normalized_cost = 1 - (optimal_total_cost / (current_total_cost + 1e-8))
                normalized_service = optimal_sl
                multi_objective_score = (cost_weight * normalized_cost) + (service_weight * normalized_service)

                optimized_levels[sku] = {
                    "current_service_level": round(current_sl, 3),
                    "optimal_service_level": round(optimal_sl, 3),
                    "critical_ratio": round(critical_ratio, 3),
                    "holding_cost_per_unit": holding_cost,
                    "stockout_cost_per_event": stockout_cost,
                    "demand_std_dev": round(std_dev, 2),
                    "annual_demand": round(ann_demand, 2),
                    "current_safety_stock": round(current_safety_stock, 2),
                    "optimal_safety_stock": round(optimal_safety_stock, 2),
                    "current_total_cost": round(current_total_cost, 2),
                    "optimal_total_cost": round(optimal_total_cost, 2),
                    "cost_change": round(cost_change, 2),
                    "cost_savings_percentage": round(cost_savings_percentage, 2),
                    "recommendation": "INCREASE" if optimal_sl > current_sl else "DECREASE",
                    "sensitivity_analysis": sensitivity_analysis,
                    "cost_curve": cost_curve,
                    "multi_objective_score": round(multi_objective_score, 3),
                    "cost_benefit_analysis": {
                        "holding_cost_reduction": round(max(0, current_holding_cost - optimal_holding_cost), 2),
                        "stockout_cost_change": round((optimal_total_cost - optimal_holding_cost) - (current_total_cost - current_holding_cost), 2),
                        "net_benefit": round(max(0, current_total_cost - optimal_total_cost), 2)
                    }
                }

            # Calculate aggregate metrics
            total_current_cost = sum(v["current_total_cost"] for v in optimized_levels.values())
            total_optimal_cost = sum(v["optimal_total_cost"] for v in optimized_levels.values())
            total_savings = total_current_cost - total_optimal_cost

            return {
                "status": "success",
                "optimized_service_levels": optimized_levels,
                "total_skus": len(optimized_levels),
                "aggregate_metrics": {
                    "total_current_cost": round(total_current_cost, 2),
                    "total_optimal_cost": round(total_optimal_cost, 2),
                    "total_potential_savings": round(total_savings, 2),
                    "savings_percentage": round((total_savings / total_current_cost * 100) if total_current_cost > 0 else 0, 2)
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in service level optimization: {e}")
            return {"error": str(e)}

    def inventory_turnover_analysis(self, inventory_data: pd.DataFrame,
                                   sales_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate inventory turnover and days inventory outstanding.
        Key metrics for inventory efficiency.
        """
        try:
            turnover_metrics = {}

            # Merge inventory and sales data
            merged_data = pd.merge(
                inventory_data,
                sales_data,
                on=["sku", "warehouse"],
                how="left"
            ).fillna(0)

            for (sku, warehouse), group in merged_data.groupby(["sku", "warehouse"]):
                avg_inventory = group["current_inventory"].mean()
                cogs = group.get("cost_of_goods_sold", pd.Series([0])).sum()

                # Inventory turnover = COGS / Average Inventory
                turnover = (cogs / avg_inventory) if avg_inventory > 0 else 0

                # Days inventory outstanding = 365 / Turnover
                dio = (365 / turnover) if turnover > 0 else 0

                turnover_metrics[f"{sku}_{warehouse}"] = {
                    "sku": sku,
                    "warehouse": warehouse,
                    "average_inventory": round(avg_inventory, 2),
                    "cost_of_goods_sold": round(cogs, 2),
                    "inventory_turnover": round(turnover, 2),
                    "days_inventory_outstanding": round(dio, 1),
                    "efficiency_rating": self._classify_turnover(turnover)
                }

            return {
                "status": "success",
                "turnover_metrics": turnover_metrics,
                "total_locations": len(turnover_metrics),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in inventory turnover analysis: {e}")
            return {"error": str(e)}

    def _classify_turnover(self, turnover: float) -> str:
        """Classify inventory turnover efficiency."""
        if turnover > 12:
            return "EXCELLENT"
        elif turnover > 8:
            return "GOOD"
        elif turnover > 4:
            return "AVERAGE"
        elif turnover > 2:
            return "POOR"
        else:
            return "CRITICAL"

    def dynamic_safety_stock_adjustment(self, demand_data: pd.DataFrame,
                                      lead_times: Dict[str, int],
                                      service_levels: Dict[str, float],
                                      volatility_window: int = 30,
                                      seasonal_adjustments: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate dynamic safety stock with demand volatility modeling.
        Adjusts safety stock based on demand variability, lead time uncertainty,
        seasonal patterns, and demand trends.

        Args:
            demand_data: Historical demand data with sku, date, quantity
            lead_times: SKU -> lead time in days
            service_levels: SKU -> target service level (0-1)
            volatility_window: Days to use for volatility calculation
            seasonal_adjustments: Optional SKU -> seasonal factor (0.5-2.0)
        """
        try:
            dynamic_stocks = {}
            seasonal_adjustments = seasonal_adjustments or {}

            for sku in demand_data["sku"].unique():
                sku_data = demand_data[demand_data["sku"] == sku].sort_values("date")

                # Calculate demand statistics with volatility
                quantities = sku_data["quantity"].values
                mean_demand = np.mean(quantities)
                std_demand = np.std(quantities)

                # Calculate demand volatility (coefficient of variation)
                cv_demand = (std_demand / mean_demand) if mean_demand > 0 else 0

                # Calculate demand trend (linear regression slope)
                if len(quantities) >= 3:
                    x = np.arange(len(quantities))
                    z = np.polyfit(x, quantities, 1)
                    demand_trend = z[0]  # Slope
                    r_squared = self._calculate_r_squared(x, quantities, z)
                else:
                    demand_trend = 0
                    r_squared = 0

                # Calculate rolling window volatility
                rolling_volatility = self._calculate_rolling_volatility(quantities, min(7, len(quantities)))
                avg_rolling_volatility = np.mean(rolling_volatility) if len(rolling_volatility) > 0 else cv_demand

                # Calculate lead time variability (if historical lead times available)
                lead_time = lead_times.get(sku, 7)
                lead_time_std = lead_time * 0.2  # Assume 20% variability

                # Calculate demand during lead time with volatility
                demand_during_lt = mean_demand * lead_time

                # Calculate safety stock with volatility adjustment
                service_level = service_levels.get(sku, 0.95)
                z_score = stats.norm.ppf(service_level)

                # Dynamic safety stock formula with volatility
                # SS = Z * sqrt((mean_demand * LT_var) + (LT * demand_var))
                variance_component = (mean_demand ** 2) * (lead_time_std ** 2)
                demand_component = (lead_time ** 2) * (std_demand ** 2)
                total_variance = variance_component + demand_component

                # Volatility adjustment factor
                volatility_adjustment = 1 + (cv_demand * 0.5)

                # Trend adjustment
                trend_adjustment = 1 + (abs(demand_trend) / mean_demand * 0.3) if mean_demand > 0 else 1

                # Seasonal adjustment
                seasonal_factor = seasonal_adjustments.get(sku, 1.0)
                seasonal_adjustment = seasonal_factor

                base_safety_stock = z_score * np.sqrt(total_variance)
                adjusted_safety_stock = base_safety_stock * volatility_adjustment * trend_adjustment * seasonal_adjustment

                # Calculate reorder point with dynamic adjustments
                reorder_point = demand_during_lt + adjusted_safety_stock

                # Calculate safety stock ranges for different scenarios
                scenarios = {
                    "low_volatility": z_score * np.sqrt(demand_component),
                    "high_volatility": z_score * np.sqrt(total_variance) * 1.5,
                    "trend_upward": z_score * np.sqrt(total_variance) * (1 + demand_trend/mean_demand) if mean_demand > 0 else adjusted_safety_stock,
                    "seasonal_peak": adjusted_safety_stock * max(1.0, seasonal_factor),
                    "seasonal_low": adjusted_safety_stock * min(1.0, seasonal_factor)
                }

                # Generate optimization recommendations
                recommendations = []
                if cv_demand > 0.5:
                    recommendations.append("High demand volatility - consider increasing safety stock buffer")
                if abs(demand_trend) > 0.1:
                    recommendations.append("Strong demand trend detected - adjust forecasts accordingly")
                if seasonal_factor > 1.2:
                    recommendations.append("Seasonal peak approaching - increase inventory levels")
                elif seasonal_factor < 0.8:
                    recommendations.append("Seasonal low period - can reduce safety stock")
                if lead_time_std > lead_time * 0.3:
                    recommendations.append("High lead time variability - consider supplier diversification")

                dynamic_stocks[sku] = {
                    "mean_daily_demand": round(mean_demand, 2),
                    "demand_std_dev": round(std_demand, 2),
                    "demand_volatility_cv": round(cv_demand, 3),
                    "rolling_volatility_avg": round(avg_rolling_volatility, 3),
                    "demand_trend": round(demand_trend, 3),
                    "trend_r_squared": round(r_squared, 3),
                    "lead_time_days": lead_time,
                    "lead_time_std_dev": round(lead_time_std, 2),
                    "service_level": service_level,
                    "z_score": round(z_score, 3),
                    "volatility_adjustment_factor": round(volatility_adjustment, 3),
                    "trend_adjustment_factor": round(trend_adjustment, 3),
                    "seasonal_adjustment_factor": round(seasonal_adjustment, 3),
                    "base_safety_stock": round(base_safety_stock, 2),
                    "adjusted_safety_stock": round(adjusted_safety_stock, 2),
                    "reorder_point": round(reorder_point, 2),
                    "cycle_stock": round(demand_during_lt, 2),
                    "scenarios": {k: round(v, 2) for k, v in scenarios.items()},
                    "volatility_risk": "HIGH" if cv_demand > 0.5 else "MEDIUM" if cv_demand > 0.3 else "LOW",
                    "trend_direction": "INCREASING" if demand_trend > 0.1 else "DECREASING" if demand_trend < -0.1 else "STABLE",
                    "seasonal_status": "PEAK" if seasonal_factor > 1.2 else "LOW" if seasonal_factor < 0.8 else "NORMAL",
                    "recommendations": recommendations,
                    "safety_stock_range": {
                        "minimum": round(scenarios["low_volatility"], 2),
                        "maximum": round(scenarios["high_volatility"], 2),
                        "recommended": round(adjusted_safety_stock, 2)
                    }
                }

            return {
                "status": "success",
                "dynamic_safety_stocks": dynamic_stocks,
                "total_skus": len(dynamic_stocks),
                "volatility_window_days": volatility_window,
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in dynamic safety stock adjustment: {e}")
            return {"error": str(e)}

    def _calculate_rolling_volatility(self, quantities: np.ndarray, window: int) -> List[float]:
        """Calculate rolling volatility over the demand history."""
        rolling_volatility = []
        for i in range(window, len(quantities) + 1):
            window_data = quantities[i-window:i]
            if len(window_data) > 1:
                cv = np.std(window_data) / (np.mean(window_data) + 1e-8)
                rolling_volatility.append(cv)
        return rolling_volatility

    def _calculate_r_squared(self, x: np.ndarray, y: np.ndarray, coeffs: np.ndarray) -> float:
        """Calculate R-squared for trend line fit."""
        if len(x) < 3:
            return 0.0
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    def abc_analysis(self, inventory_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform ABC analysis based on annual usage value.
        Classifies items into A (high value), B (medium), C (low).
        """
        try:
            # Calculate annual usage value
            inventory_data["annual_usage_value"] = (
                inventory_data["quantity"] * inventory_data["unit_cost"]
            )

            # Sort by annual usage value
            sorted_data = inventory_data.sort_values("annual_usage_value", ascending=False)

            # Calculate cumulative percentage
            total_value = sorted_data["annual_usage_value"].sum()
            sorted_data["cumulative_value"] = sorted_data["annual_usage_value"].cumsum()
            sorted_data["cumulative_percentage"] = (
                sorted_data["cumulative_value"] / total_value * 100
            )

            # Classify into ABC
            def classify_abc(row):
                if row["cumulative_percentage"] <= 70:
                    return "A"
                elif row["cumulative_percentage"] <= 90:
                    return "B"
                else:
                    return "C"

            sorted_data["abc_class"] = sorted_data.apply(classify_abc, axis=1)

            # Summary statistics
            abc_summary = sorted_data.groupby("abc_class").agg({
                "sku": "count",
                "annual_usage_value": "sum"
            }).to_dict("index")

            return {
                "status": "success",
                "abc_classification": sorted_data[["sku", "annual_usage_value", "abc_class"]].to_dict("records"),
                "summary": abc_summary,
                "total_items": len(sorted_data),
                "total_value": round(total_value, 2),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in ABC analysis: {e}")
            return {"error": str(e)}

    def perishable_inventory_management(self, inventory_data: pd.DataFrame,
                                        demand_forecast: Dict[str, List[float]],
                                        shelf_life_params: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Manage perishable inventory with expiration tracking and optimization.
        Includes FEFO (First-Expired-First-Out) optimization and waste reduction.

        Args:
            inventory_data: Inventory data with sku, quantity, production_date, expiration_date
            demand_forecast: SKU -> demand by period
            shelf_life_params: SKU -> {shelf_life_days, deterioration_rate, quality_threshold}
        """
        try:
            perishable_analysis = {}

            for sku in demand_forecast.keys():
                sku_inventory = inventory_data[inventory_data["sku"] == sku] if "sku" in inventory_data.columns else inventory_data

                # Get shelf life parameters
                shelf_life = shelf_life_params.get(sku, {}).get("shelf_life_days", 30)
                deterioration_rate = shelf_life_params.get(sku, {}).get("deterioration_rate", 0.01)
                quality_threshold = shelf_life_params.get(sku, {}).get("quality_threshold", 0.8)

                # Calculate expiration risk
                total_quantity = sku_inventory["quantity"].sum() if "quantity" in sku_inventory.columns else 0
                total_demand = sum(demand_forecast[sku])

                # Simulate expiration over time
                current_date = datetime.now(timezone.utc)

                if "expiration_date" in sku_inventory.columns:
                    sku_inventory["days_until_expiration"] = (
                        pd.to_datetime(sku_inventory["expiration_date"]) - current_date
                    ).dt.days

                    # Categorize by expiration risk
                    critical_expiration = sku_inventory[sku_inventory["days_until_expiration"] <= 7]
                    warning_expiration = sku_inventory[
                        (sku_inventory["days_until_expiration"] > 7) &
                        (sku_inventory["days_until_expiration"] <= 14)
                    ]
                    safe_expiration = sku_inventory[sku_inventory["days_until_expiration"] > 14]

                    critical_quantity = critical_expiration["quantity"].sum()
                    warning_quantity = warning_expiration["quantity"].sum()
                    safe_quantity = safe_expiration["quantity"].sum()
                else:
                    # Simulate expiration based on production date
                    critical_quantity = total_quantity * 0.1
                    warning_quantity = total_quantity * 0.2
                    safe_quantity = total_quantity * 0.7

                # Calculate waste probability
                if total_demand > 0:
                    waste_probability = max(0, (total_quantity - total_demand) / total_quantity)
                else:
                    waste_probability = 1.0

                # Optimize ordering for perishables
                # More frequent, smaller orders to reduce waste
                optimal_order_quantity = min(total_demand / 4, shelf_life * 2)  # Quarterly orders or shelf-life constrained
                order_frequency = max(1, int(shelf_life / 7))  # Order every week minimum

                # Calculate quality degradation
                quality_curve = []
                for day in range(0, shelf_life + 1, 7):
                    quality = max(0, 1 - (day / shelf_life) * deterioration_rate * 10)
                    quality_curve.append({"day": day, "quality": round(quality, 3)})

                # FEFO recommendations
                fefo_recommendations = []
                if critical_quantity > 0:
                    fefo_recommendations.append(f"URGENT: {critical_quantity:.0f} units expire within 7 days - prioritize for immediate sale/discount")
                if warning_quantity > 0:
                    fefo_recommendations.append(f"WARNING: {warning_quantity:.0f} units expire within 14 days - consider promotional pricing")
                if waste_probability > 0.3:
                    fefo_recommendations.append(f"HIGH WASTE RISK: {waste_probability:.1%} probability of waste - reduce order quantities")

                perishable_analysis[sku] = {
                    "total_inventory": round(total_quantity, 2),
                    "total_forecast_demand": round(total_demand, 2),
                    "shelf_life_days": shelf_life,
                    "deterioration_rate": deterioration_rate,
                    "quality_threshold": quality_threshold,
                    "expiration_breakdown": {
                        "critical_expiration_7d": round(critical_quantity, 2),
                        "warning_expiration_14d": round(warning_quantity, 2),
                        "safe_expiration": round(safe_quantity, 2)
                    },
                    "waste_probability": round(waste_probability, 3),
                    "optimal_order_quantity": round(optimal_order_quantity, 2),
                    "recommended_order_frequency_days": order_frequency,
                    "quality_degradation_curve": quality_curve,
                    "fefo_recommendations": fefo_recommendations,
                    "inventory_strategy": "FEFO" if critical_quantity > 0 else "FIFO",
                    "discount_recommendation": self._calculate_discount_recommendation(critical_quantity, total_quantity, waste_probability)
                }

            return {
                "status": "success",
                "perishable_analysis": perishable_analysis,
                "total_skus": len(perishable_analysis),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in perishable inventory management: {e}")
            return {"error": str(e)}

    def _calculate_discount_recommendation(self, critical_quantity: float, total_quantity: float, waste_prob: float) -> Dict[str, Any]:
        """Calculate discount recommendations for near-expiration items."""
        if critical_quantity == 0:
            return {"recommended": False, "discount_percentage": 0}

        critical_ratio = critical_quantity / (total_quantity + 1e-8)

        if critical_ratio > 0.3 or waste_prob > 0.5:
            return {
                "recommended": True,
                "discount_percentage": 30,
                "reason": "High expiration risk - aggressive discounting recommended"
            }
        elif critical_ratio > 0.15 or waste_prob > 0.3:
            return {
                "recommended": True,
                "discount_percentage": 20,
                "reason": "Moderate expiration risk - promotional pricing recommended"
            }
        else:
            return {
                "recommended": True,
                "discount_percentage": 10,
                "reason": "Low expiration risk - mild discount to accelerate turnover"
            }

    def obsolescence_risk_modeling(self, inventory_data: pd.DataFrame,
                                   demand_history: pd.DataFrame,
                                   product_lifecycle_params: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Model obsolescence risk and provide mitigation recommendations.
        Identifies slow-moving, end-of-life, and at-risk inventory.

        Args:
            inventory_data: Inventory data with sku, quantity, unit_cost, age_days
            demand_history: Historical demand data with sku, date, quantity
            lifecycle_params: SKU -> {launch_date, maturity_date, decline_date, end_of_life_date}
        """
        try:
            obsolescence_analysis = {}

            for sku in inventory_data["sku"].unique() if "sku" in inventory_data.columns else []:
                sku_inventory = inventory_data[inventory_data["sku"] == sku].iloc[0] if "sku" in inventory_data.columns else inventory_data
                sku_demand = demand_history[demand_history["sku"] == sku] if "sku" in demand_history.columns else demand_history

                # Calculate demand trend
                if len(sku_demand) > 1:
                    quantities = sku_demand["quantity"].values
                    recent_demand = np.mean(quantities[-4:]) if len(quantities) >= 4 else np.mean(quantities)
                    historical_demand = np.mean(quantities)
                    demand_decline_rate = (historical_demand - recent_demand) / (historical_demand + 1e-8)
                else:
                    demand_decline_rate = 0
                    recent_demand = 0
                    historical_demand = 0

                # Calculate inventory age and turnover
                current_inventory = sku_inventory.get("quantity", 0)
                unit_cost = sku_inventory.get("unit_cost", 0)
                inventory_age = sku_inventory.get("age_days", 0)

                # Calculate days of supply
                if recent_demand > 0:
                    days_of_supply = current_inventory / recent_demand
                else:
                    days_of_supply = float('inf')

                # Determine lifecycle stage
                lifecycle = product_lifecycle_params.get(sku, {})
                current_date = datetime.now(timezone.utc)

                launch_date = lifecycle.get("launch_date")
                maturity_date = lifecycle.get("maturity_date")
                decline_date = lifecycle.get("decline_date")
                eol_date = lifecycle.get("end_of_life_date")

                lifecycle_stage = "unknown"
                if eol_date and pd.to_datetime(eol_date) < current_date:
                    lifecycle_stage = "end_of_life"
                elif decline_date and pd.to_datetime(decline_date) < current_date:
                    lifecycle_stage = "decline"
                elif maturity_date and pd.to_datetime(maturity_date) < current_date:
                    lifecycle_stage = "maturity"
                elif launch_date and pd.to_datetime(launch_date) < current_date:
                    lifecycle_stage = "growth"
                else:
                    lifecycle_stage = "introduction"

                # Calculate obsolescence risk score (0-100)
                risk_factors = []

                # Demand decline factor
                if demand_decline_rate > 0.5:
                    risk_factors.append(40)
                elif demand_decline_rate > 0.3:
                    risk_factors.append(30)
                elif demand_decline_rate > 0.1:
                    risk_factors.append(20)

                # Days of supply factor
                if days_of_supply > 365:
                    risk_factors.append(30)
                elif days_of_supply > 180:
                    risk_factors.append(20)
                elif days_of_supply > 90:
                    risk_factors.append(10)

                # Lifecycle stage factor
                if lifecycle_stage == "end_of_life":
                    risk_factors.append(30)
                elif lifecycle_stage == "decline":
                    risk_factors.append(20)
                elif lifecycle_stage == "maturity":
                    risk_factors.append(5)

                # Inventory age factor
                if inventory_age > 365:
                    risk_factors.append(20)
                elif inventory_age > 180:
                    risk_factors.append(10)

                obsolescence_risk_score = min(100, sum(risk_factors))

                # Determine risk category
                if obsolescence_risk_score >= 70:
                    risk_category = "CRITICAL"
                elif obsolescence_risk_score >= 50:
                    risk_category = "HIGH"
                elif obsolescence_risk_score >= 30:
                    risk_category = "MEDIUM"
                else:
                    risk_category = "LOW"

                # Generate mitigation recommendations
                mitigation_recommendations = []

                if lifecycle_stage == "end_of_life":
                    mitigation_recommendations.append("Phase out inventory - stop replenishment")
                    mitigation_recommendations.append("Consider liquidation or discount to clear stock")
                elif lifecycle_stage == "decline":
                    mitigation_recommendations.append("Reduce order quantities significantly")
                    mitigation_recommendations.append("Monitor demand closely for further decline")

                if days_of_supply > 180:
                    mitigation_recommendations.append(f"Excess inventory: {days_of_supply:.0f} days of supply - implement reduction plan")

                if demand_decline_rate > 0.3:
                    mitigation_recommendations.append(f"Rapid demand decline: {demand_decline_rate:.1%} - investigate market changes")

                if obsolescence_risk_score >= 50:
                    mitigation_recommendations.append("Consider product substitution or bundling")
                    mitigation_recommendations.append("Review pricing strategy to stimulate demand")

                # Calculate financial impact
                inventory_value = current_inventory * unit_cost
                potential_write_off = inventory_value * (obsolescence_risk_score / 100) * 0.5

                obsolescence_analysis[sku] = {
                    "current_inventory": round(current_inventory, 2),
                    "unit_cost": round(unit_cost, 2),
                    "inventory_value": round(inventory_value, 2),
                    "inventory_age_days": inventory_age,
                    "recent_demand": round(recent_demand, 2),
                    "historical_demand": round(historical_demand, 2),
                    "demand_decline_rate": round(demand_decline_rate, 3),
                    "days_of_supply": round(days_of_supply, 1) if days_of_supply != float('inf') else "inf",
                    "lifecycle_stage": lifecycle_stage,
                    "obsolescence_risk_score": round(obsolescence_risk_score, 1),
                    "risk_category": risk_category,
                    "potential_write_off": round(potential_write_off, 2),
                    "mitigation_recommendations": mitigation_recommendations,
                    "risk_factors": {
                        "demand_decline": min(40, max(0, demand_decline_rate * 80)),
                        "excess_inventory": min(30, max(0, (days_of_supply / 365) * 30)) if days_of_supply != float('inf') else 30,
                        "lifecycle_stage": {"end_of_life": 30, "decline": 20, "maturity": 5, "growth": 0, "introduction": 0}.get(lifecycle_stage, 0),
                        "inventory_age": min(20, max(0, (inventory_age / 365) * 20))
                    }
                }

            return {
                "status": "success",
                "obsolescence_analysis": obsolescence_analysis,
                "total_skus": len(obsolescence_analysis),
                "high_risk_count": sum(1 for sku in obsolescence_analysis.values() if sku["risk_category"] in ["CRITICAL", "HIGH"]),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger_io.error(f"Error in obsolescence risk modeling: {e}")
            return {"error": str(e)}
