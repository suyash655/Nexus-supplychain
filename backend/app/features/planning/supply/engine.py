"""
NEXUS — Supply Planning Engine (SAP IBP-style)
==============================================
Production planning, distribution requirements planning,
and capacity optimization.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict

logger_sp = logging.getLogger("nexus.supply_planning")


class SupplyPlanningEngine:
    """
    Enterprise supply planning with production scheduling,
    distribution requirements planning (DRP), and capacity analysis.
    """

    def __init__(self):
        self.production_schedule = {}
        self.distribution_plan = {}
        self.capacity_constraints = {}
        self._initialised = False
        self.constraint_optimizer = None
        self.multi_site_plans = {}
        self.supplier_capacity = {}
        self.transportation_costs = {}
        self.rough_cut_capacity = {}

    def initialize(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Initialize supply planning with supply chain data.
        
        Expected columns:
        - sku: product identifier
        - supplier: source location
        - warehouse: destination warehouse
        - region: geographic region
        - lead_time_days: supplier lead time
        - capacity_daily: daily production/capacity
        - safety_stock: safety stock level
        - current_inventory: current inventory level
        """
        try:
            if "sku" not in df.columns:
                return {"error": "Missing required column: sku", "initialised": False}

            results = {
                "status": "success",
                "suppliers": [],
                "warehouses": [],
                "skus": [],
                "initialised_at": datetime.now(timezone.utc).isoformat()
            }

            # Extract supply chain entities
            results["suppliers"] = df["supplier"].unique().tolist() if "supplier" in df.columns else []
            results["warehouses"] = df["warehouse"].unique().tolist() if "warehouse" in df.columns else []
            results["skus"] = df["sku"].unique().tolist()
            
            # Build capacity constraints
            if "capacity_daily" in df.columns:
                capacity_data = df.groupby("supplier")["capacity_daily"].first().to_dict()
                self.capacity_constraints = {k: float(v) for k, v in capacity_data.items()}
                results["capacity_constraints"] = self.capacity_constraints

            self._initialised = True
            return results

        except Exception as e:
            logger_sp.error(f"Error initializing supply planning: {e}")
            return {"error": str(e), "initialised": False}

    def create_production_schedule(self, demand_forecast: Dict[str, List[float]],
                                  lead_times: Dict[str, int],
                                  capacity: Dict[str, float]) -> Dict[str, Any]:
        """
        Create optimized production schedule based on demand forecast.
        
        Args:
            demand_forecast: SKU -> list of demand quantities by period
            lead_times: SKU -> lead time in days
            capacity: supplier -> daily capacity
        """
        if not self._initialised:
            return {"error": "Supply planning not initialised"}

        try:
            schedule = {}
            capacity_utilization = {}
            
            for sku, demand in demand_forecast.items():
                lead_time = lead_times.get(sku, 7)  # Default 7 days
                periods = len(demand)
                
                # Calculate required production per period
                production_plan = []
                cumulative_demand = 0
                
                for period, demand_qty in enumerate(demand):
                    cumulative_demand += demand_qty
                    
                    # Account for lead time - produce in advance
                    production_period = max(0, period - int(lead_time / 7))
                    
                    # Simple heuristic: produce to meet demand + safety margin
                    safety_margin = 0.1  # 10% safety margin
                    required_production = demand_qty * (1 + safety_margin)
                    
                    production_plan.append({
                        "period": production_period,
                        "demand": demand_qty,
                        "production": round(required_production, 2),
                        "cumulative_demand": round(cumulative_demand, 2)
                    })
                
                schedule[sku] = production_plan
            
            # Calculate capacity utilization
            for supplier, daily_cap in capacity.items():
                total_production = sum(
                    sum(p["production"] for p in plan)
                    for plan in schedule.values()
                )
                periods = max(len(plan) for plan in schedule.values()) if schedule else 1
                total_capacity = daily_cap * periods * 7  # Weekly capacity
                
                utilization = (total_production / total_capacity * 100) if total_capacity > 0 else 0
                capacity_utilization[supplier] = {
                    "total_capacity": round(total_capacity, 2),
                    "required_production": round(total_production, 2),
                    "utilization_percentage": round(utilization, 2),
                    "status": self._classify_utilization(utilization)
                }
            
            return {
                "status": "success",
                "production_schedule": schedule,
                "capacity_utilization": capacity_utilization,
                "planning_horizon_periods": max(len(plan) for plan in schedule.values()) if schedule else 0,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error creating production schedule: {e}")
            return {"error": str(e)}

    def distribution_requirements_planning(self, inventory_data: pd.DataFrame,
                                          demand_forecast: Dict[str, List[float]],
                                          lead_times: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate distribution requirements planning (DRP).
        Determines when to replenish warehouses based on demand and lead times.
        """
        try:
            drp_plan = {}
            
            if "warehouse" not in inventory_data.columns or "sku" not in inventory_data.columns:
                return {"error": "Missing required columns: warehouse, sku"}

            # Process each warehouse-SKU combination
            for (warehouse, sku), group in inventory_data.groupby(["warehouse", "sku"]):
                current_inventory = group["current_inventory"].iloc[0] if "current_inventory" in group.columns else 0
                safety_stock = group["safety_stock"].iloc[0] if "safety_stock" in group.columns else 0
                lead_time = lead_times.get(sku, 7)
                
                forecast = demand_forecast.get(sku, [0] * 12)
                
                # Calculate DRP
                drp_periods = []
                inventory_position = current_inventory
                
                for period, demand in enumerate(forecast):
                    # Calculate projected inventory
                    projected_inventory = inventory_position - demand
                    
                    # Check if reorder point reached
                    reorder_point = safety_stock * 1.5
                    order_quantity = 0
                    
                    if projected_inventory <= reorder_point:
                        # Calculate order quantity (EOQ-like)
                        order_quantity = max(safety_stock * 2, demand * 2)
                        projected_inventory += order_quantity
                    
                    drp_periods.append({
                        "period": period,
                        "starting_inventory": round(inventory_position, 2),
                        "demand": demand,
                        "projected_inventory": round(projected_inventory, 2),
                        "order_quantity": round(order_quantity, 2),
                        "order_arrival_period": period + int(lead_time / 7) if order_quantity > 0 else None,
                        "reorder_point": round(reorder_point, 2)
                    })
                    
                    inventory_position = projected_inventory
                
                drp_plan[f"{warehouse}_{sku}"] = {
                    "warehouse": warehouse,
                    "sku": sku,
                    "current_inventory": current_inventory,
                    "safety_stock": safety_stock,
                    "lead_time_days": lead_time,
                    "plan": drp_periods
                }
            
            return {
                "status": "success",
                "drp_plan": drp_plan,
                "total_combinations": len(drp_plan),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in DRP calculation: {e}")
            return {"error": str(e)}

    def capacity_analysis(self, production_schedule: Dict[str, Any],
                         resources: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Analyze capacity constraints and identify bottlenecks.
        
        Args:
            production_schedule: Production schedule from create_production_schedule
            resources: Resource definitions with capacity and efficiency
        """
        try:
            bottlenecks = []
            resource_utilization = {}
            
            for resource_id, resource_info in resources.items():
                capacity = resource_info.get("capacity", 100)
                efficiency = resource_info.get("efficiency", 1.0)
                effective_capacity = capacity * efficiency
                
                # Calculate required capacity from schedule
                required_capacity = 0
                for sku, schedule in production_schedule.items():
                    for period in schedule:
                        required_capacity += period.get("production", 0)
                
                utilization = (required_capacity / effective_capacity * 100) if effective_capacity > 0 else 0
                
                resource_utilization[resource_id] = {
                    "nominal_capacity": capacity,
                    "efficiency_factor": efficiency,
                    "effective_capacity": round(effective_capacity, 2),
                    "required_capacity": round(required_capacity, 2),
                    "utilization_percentage": round(utilization, 2),
                    "available_capacity": round(effective_capacity - required_capacity, 2),
                    "status": self._classify_utilization(utilization)
                }
                
                # Identify bottlenecks
                if utilization > 90:
                    bottlenecks.append({
                        "resource": resource_id,
                        "utilization": round(utilization, 2),
                        "severity": "CRITICAL" if utilization > 100 else "HIGH",
                        "recommendation": f"Increase capacity or reduce production schedule by {round(utilization - 90, 2)}%"
                    })
                elif utilization > 80:
                    bottlenecks.append({
                        "resource": resource_id,
                        "utilization": round(utilization, 2),
                        "severity": "MEDIUM",
                        "recommendation": "Monitor closely, consider capacity expansion"
                    })
            
            return {
                "status": "success",
                "resource_utilization": resource_utilization,
                "bottlenecks": bottlenecks,
                "total_resources": len(resources),
                "bottleneck_count": len(bottlenecks),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in capacity analysis: {e}")
            return {"error": str(e)}

    def _classify_utilization(self, utilization: float) -> str:
        """Classify capacity utilization status."""
        if utilization > 100:
            return "OVERLOADED"
        elif utilization > 90:
            return "CRITICAL"
        elif utilization > 75:
            return "HIGH"
        elif utilization > 50:
            return "NORMAL"
        else:
            return "UNDERUTILIZED"

    def what_if_analysis(self, base_scenario: Dict[str, Any],
                        scenario_changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform what-if analysis for supply planning scenarios.
        
        Args:
            base_scenario: Base production/capacity scenario
            scenario_changes: Changes to apply (demand changes, capacity changes, etc.)
        """
        try:
            # Apply scenario changes
            modified_scenario = base_scenario.copy()
            
            # Apply demand changes
            if "demand_multiplier" in scenario_changes:
                multiplier = scenario_changes["demand_multiplier"]
                for sku in modified_scenario.get("production_schedule", {}):
                    for period in modified_scenario["production_schedule"][sku]:
                        period["demand"] *= multiplier
                        period["production"] *= multiplier
            
            # Apply capacity changes
            if "capacity_changes" in scenario_changes:
                for resource, change in scenario_changes["capacity_changes"].items():
                    if resource in modified_scenario.get("capacity_utilization", {}):
                        old_capacity = modified_scenario["capacity_utilization"][resource]["total_capacity"]
                        new_capacity = old_capacity * change
                        modified_scenario["capacity_utilization"][resource]["total_capacity"] = new_capacity
            
            # Recalculate with modified scenario
            # (This would call the relevant planning functions again)
            
            # Compare scenarios
            comparison = {
                "base_scenario": base_scenario,
                "modified_scenario": modified_scenario,
                "impact_analysis": self._analyze_scenario_impact(base_scenario, modified_scenario)
            }
            
            return {
                "status": "success",
                "scenario_comparison": comparison,
                "applied_changes": scenario_changes,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in what-if analysis: {e}")
            return {"error": str(e)}

    def _analyze_scenario_impact(self, base: Dict[str, Any], 
                               modified: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of scenario changes."""
        impact = {
            "capacity_changes": [],
            "cost_implications": [],
            "service_level_changes": []
        }
        
        # Compare capacity utilization
        if "capacity_utilization" in base and "capacity_utilization" in modified:
            for resource in base["capacity_utilization"]:
                base_util = base["capacity_utilization"][resource]["utilization_percentage"]
                mod_util = modified["capacity_utilization"][resource]["utilization_percentage"]
                
                impact["capacity_changes"].append({
                    "resource": resource,
                    "base_utilization": base_util,
                    "modified_utilization": mod_util,
                    "change": round(mod_util - base_util, 2)
                })
        
        return impact

    def constraint_based_optimization(self, demand_forecast: Dict[str, List[float]],
                                    constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced production scheduling with constraint optimization.
        
        Args:
            demand_forecast: SKU -> list of demand quantities by period
            constraints: Dictionary of constraints
                - capacity: Max production capacity per period
                - labor: Available labor hours
                - materials: Material availability
                - setup_time: Setup time between product changes
        """
        try:
            if not self._initialised:
                return {"error": "Supply planning not initialised"}
            
            optimized_schedule = {}
            constraint_status = {}
            constraint_violations = []
            
            max_capacity = constraints.get("capacity", 1000)
            labor_hours = constraints.get("labor", 100)
            material_constraints = constraints.get("materials", {})
            setup_time = constraints.get("setup_time", 0)
            quality_requirements = constraints.get("quality", 0.95)
            
            for sku, demand in demand_forecast.items():
                periods = len(demand)
                schedule = []
                
                cumulative_production = 0
                labor_used = 0
                current_capacity_used = 0
                setup_accumulator = 0
                
                for period, demand_qty in enumerate(demand):
                    # Calculate required production with constraints
                    required_production = demand_qty
                    
                    # Apply setup time reduction
                    if setup_time > 0 and period > 0:
                        setup_accumulator = setup_time
                        effective_capacity = max_capacity - setup_accumulator
                    else:
                        effective_capacity = max_capacity
                    
                    # Check capacity constraint
                    if current_capacity_used + required_production > effective_capacity:
                        # Split production across periods
                        available_capacity = effective_capacity - current_capacity_used
                        production_this_period = min(required_production, available_capacity)
                        deferred_production = required_production - production_this_period
                        
                        constraint_violations.append({
                            "sku": sku,
                            "period": period,
                            "constraint_type": "capacity",
                            "severity": "high",
                            "message": f"Capacity exceeded by {required_production - available_capacity:.2f} units"
                        })
                    else:
                        production_this_period = required_production
                        deferred_production = 0
                    
                    # Check labor constraint
                    labor_required = production_this_period * 0.5  # Assume 0.5 hours per unit
                    if labor_used + labor_required > labor_hours:
                        available_labor = labor_hours - labor_used
                        labor_limited_production = available_labor / 0.5
                        production_this_period = min(production_this_period, labor_limited_production)
                        
                        constraint_violations.append({
                            "sku": sku,
                            "period": period,
                            "constraint_type": "labor",
                            "severity": "medium",
                            "message": f"Labor constraint limited production by {production_this_period - labor_limited_production:.2f} units"
                        })
                    
                    # Check material constraints
                    material_limited = False
                    for material, required_qty in material_constraints.items():
                        available_qty = material_constraints.get(f"{material}_available", required_qty * 2)
                        if required_qty > available_qty:
                            material_limited = True
                            production_this_period = min(production_this_period, available_qty / required_qty * production_this_period)
                            
                            constraint_violations.append({
                                "sku": sku,
                                "period": period,
                                "constraint_type": "material",
                                "severity": "high",
                                "message": f"Material {material} shortage limited production"
                            })
                    
                    # Quality check simulation
                    quality_factor = 1.0
                    if quality_requirements < 1.0:
                        # Simulate quality rejects
                        quality_factor = quality_requirements + (np.random.random() * 0.05)
                        production_this_period *= quality_factor
                    
                    # Update resource usage
                    current_capacity_used += production_this_period
                    labor_used += production_this_period * 0.5
                    cumulative_production += production_this_period
                    
                    schedule.append({
                        "period": period,
                        "demand": demand_qty,
                        "planned_production": round(production_this_period, 2),
                        "deferred_production": round(deferred_production, 2),
                        "capacity_utilization": round((current_capacity_used / max_capacity) * 100, 2),
                        "labor_utilization": round((labor_used / labor_hours) * 100, 2),
                        "quality_factor": round(quality_factor, 3),
                        "constraints_active": {
                            "capacity_limited": current_capacity_used >= max_capacity * 0.9,
                            "labor_limited": labor_used >= labor_hours * 0.9,
                            "material_limited": material_limited,
                            "setup_time_impact": setup_accumulator > 0
                        }
                    })
                
                optimized_schedule[sku] = schedule
            
            # Calculate overall constraint status
            total_demand = sum(sum(demand) for demand in demand_forecast.values())
            total_production = sum(sum(p["planned_production"] for p in schedule) for schedule in optimized_schedule.values())
            
            constraint_status = {
                "total_demand": total_demand,
                "total_planned_production": total_production,
                "demand_satisfaction_rate": round((total_production / total_demand) * 100, 2) if total_demand > 0 else 0,
                "capacity_utilization_overall": round((total_production / (max_capacity * periods)) * 100, 2),
                "feasible": total_production >= total_demand * 0.95,  # 95% satisfaction threshold
                "constraint_violations_count": len(constraint_violations),
                "critical_violations": len([v for v in constraint_violations if v["severity"] == "high"])
            }
            
            return {
                "status": "success",
                "optimized_schedule": optimized_schedule,
                "constraint_status": constraint_status,
                "constraint_violations": constraint_violations,
                "constraints_applied": constraints,
                "optimization_summary": {
                    "total_deferred_production": round(sum(
                        sum(p["deferred_production"] for p in schedule) 
                        for schedule in optimized_schedule.values()
                    ), 2),
                    "average_capacity_utilization": round(np.mean([
                        p["capacity_utilization"] 
                        for schedule in optimized_schedule.values() 
                        for p in schedule
                    ]), 2) if optimized_schedule else 0
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in constraint-based optimization: {e}")
            return {"error": str(e)}

    def multi_site_planning(self, demand_forecast: Dict[str, List[float]],
                          sites: Dict[str, Dict[str, Any]],
                          transfer_costs: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Multi-site production planning optimization.
        
        Args:
            demand_forecast: SKU -> list of demand quantities by period
            sites: Dictionary of site configurations
                - site_id: {capacity, capabilities, fixed_cost, variable_cost}
            transfer_costs: Dictionary of transfer costs between sites
        """
        try:
            if not self._initialised:
                return {"error": "Supply planning not initialised"}
            
            multi_site_plan = {}
            site_utilization = {}
            
            for sku, demand in demand_forecast.items():
                sku_plan = {
                    "site_allocations": {},
                    "transfers": [],
                    "total_cost": 0
                }
                
                total_demand = sum(demand)
                
                # Allocate production across sites based on capacity and cost
                for site_id, site_config in sites.items():
                    site_capacity = site_config.get("capacity", 0)
                    variable_cost = site_config.get("variable_cost", 1.0)
                    capabilities = site_config.get("capabilities", [])
                    
                    # Check if site can produce this SKU
                    if sku not in capabilities and "all" not in capabilities:
                        continue
                    
                    # Calculate allocation based on capacity share
                    total_site_capacity = sum(s.get("capacity", 0) for s in sites.values())
                    capacity_share = site_capacity / total_site_capacity if total_site_capacity > 0 else 0
                    
                    allocation = min(total_demand * capacity_share, site_capacity)
                    
                    if allocation > 0:
                        sku_plan["site_allocations"][site_id] = {
                            "production_quantity": round(allocation, 2),
                            "capacity_utilization": round((allocation / site_capacity) * 100, 2),
                            "production_cost": round(allocation * variable_cost, 2)
                        }
                
                # Calculate transfers between sites if needed
                for source_site, source_alloc in sku_plan["site_allocations"].items():
                    for dest_site, dest_alloc in sku_plan["site_allocations"].items():
                        if source_site != dest_site:
                            transfer_cost = transfer_costs.get(source_site, {}).get(dest_site, 0)
                            if transfer_cost > 0:
                                # Assume 10% of production needs transfer
                                transfer_qty = source_alloc["production_quantity"] * 0.1
                                sku_plan["transfers"].append({
                                    "from_site": source_site,
                                    "to_site": dest_site,
                                    "quantity": round(transfer_qty, 2),
                                    "cost": round(transfer_qty * transfer_cost, 2)
                                })
                
                # Calculate total cost
                production_cost = sum(alloc["production_cost"] for alloc in sku_plan["site_allocations"].values())
                transfer_cost = sum(t["cost"] for t in sku_plan["transfers"])
                sku_plan["total_cost"] = round(production_cost + transfer_cost, 2)
                
                multi_site_plan[sku] = sku_plan
            
            # Calculate site utilization
            for site_id, site_config in sites.items():
                site_capacity = site_config.get("capacity", 0)
                total_production = 0
                
                for sku_plan in multi_site_plan.values():
                    if site_id in sku_plan["site_allocations"]:
                        total_production += sku_plan["site_allocations"][site_id]["production_quantity"]
                
                site_utilization[site_id] = {
                    "total_capacity": site_capacity,
                    "total_production": round(total_production, 2),
                    "utilization_rate": round((total_production / site_capacity) * 100, 2) if site_capacity > 0 else 0,
                    "fixed_cost": site_config.get("fixed_cost", 0),
                    "variable_cost": site_config.get("variable_cost", 0)
                }
            
            return {
                "status": "success",
                "multi_site_plan": multi_site_plan,
                "site_utilization": site_utilization,
                "total_cost": sum(plan["total_cost"] for plan in multi_site_plan.values()),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in multi-site planning: {e}")
            return {"error": str(e)}

    def supplier_capacity_planning(self, demand_forecast: Dict[str, List[float]],
                                  suppliers: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Supplier capacity planning and allocation.
        
        Args:
            demand_forecast: SKU -> list of demand quantities by period
            suppliers: Dictionary of supplier configurations
                - supplier_id: {capacity, lead_time, quality_score, cost_per_unit}
        """
        try:
            if not self._initialised:
                return {"error": "Supply planning not initialised"}
            
            capacity_plan = {}
            supplier_allocation = {}
            
            for sku, demand in demand_forecast.items():
                total_demand = sum(demand)
                periods = len(demand)
                
                # Allocate demand across suppliers
                supplier_allocations = {}
                
                for supplier_id, supplier_config in suppliers.items():
                    supplier_capacity = supplier_config.get("capacity", 0)
                    lead_time = supplier_config.get("lead_time", 7)
                    quality_score = supplier_config.get("quality_score", 1.0)
                    cost_per_unit = supplier_config.get("cost_per_unit", 1.0)
                    
                    # Calculate allocation based on capacity and quality
                    total_capacity = sum(s.get("capacity", 0) for s in suppliers.values())
                    capacity_share = supplier_capacity / total_capacity if total_capacity > 0 else 0
                    
                    # Adjust allocation based on quality (higher quality = higher allocation)
                    quality_adjusted_share = capacity_share * quality_score
                    
                    allocation = min(total_demand * quality_adjusted_share, supplier_capacity)
                    
                    if allocation > 0:
                        supplier_allocations[supplier_id] = {
                            "allocated_quantity": round(allocation, 2),
                            "capacity_utilization": round((allocation / supplier_capacity) * 100, 2),
                            "lead_time_days": lead_time,
                            "quality_score": quality_score,
                            "unit_cost": cost_per_unit,
                            "total_cost": round(allocation * cost_per_unit, 2),
                            "delivery_schedule": self._calculate_delivery_schedule(allocation, periods, lead_time)
                        }
                
                capacity_plan[sku] = {
                    "total_demand": total_demand,
                    "total_allocated": round(sum(a["allocated_quantity"] for a in supplier_allocations.values()), 2),
                    "allocation_percentage": round((sum(a["allocated_quantity"] for a in supplier_allocations.values()) / total_demand) * 100, 2) if total_demand > 0 else 0,
                    "supplier_allocations": supplier_allocations
                }
            
            # Calculate overall supplier utilization
            for supplier_id, supplier_config in suppliers.items():
                total_allocated = 0
                for sku_plan in capacity_plan.values():
                    if supplier_id in sku_plan["supplier_allocations"]:
                        total_allocated += sku_plan["supplier_allocations"][supplier_id]["allocated_quantity"]
                
                supplier_allocation[supplier_id] = {
                    "supplier_id": supplier_id,
                    "total_capacity": supplier_config.get("capacity", 0),
                    "total_allocated": round(total_allocated, 2),
                    "utilization_rate": round((total_allocated / supplier_config.get("capacity", 1)) * 100, 2),
                    "remaining_capacity": round(supplier_config.get("capacity", 0) - total_allocated, 2),
                    "quality_score": supplier_config.get("quality_score", 1.0)
                }
            
            return {
                "status": "success",
                "capacity_plan": capacity_plan,
                "supplier_allocation": supplier_allocation,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in supplier capacity planning: {e}")
            return {"error": str(e)}

    def _calculate_delivery_schedule(self, total_quantity: int, periods: int, 
                                   lead_time: int) -> List[Dict[str, Any]]:
        """Calculate delivery schedule based on lead time."""
        schedule = []
        quantity_per_period = total_quantity / periods
        
        for period in range(periods):
            delivery_period = period + int(lead_time / 7)  # Convert days to weeks
            schedule.append({
                "period": period,
                "delivery_period": delivery_period,
                "quantity": round(quantity_per_period, 2)
            })
        
        return schedule

    def transportation_planning(self, shipments: List[Dict[str, Any]],
                             routes: Dict[str, Dict[str, Any]],
                             constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transportation planning and route optimization.
        
        Args:
            shipments: List of shipment requirements
                - [{sku, quantity, origin, destination, urgency}]
            routes: Dictionary of available routes
                - route_id: {origin, destination, distance, cost_per_km, capacity, transit_time}
            constraints: Transportation constraints
                - max_cost, max_transit_time, vehicle_capacity
        """
        try:
            optimized_routes = {}
            total_cost = 0
            total_distance = 0
            
            for shipment in shipments:
                sku = shipment.get("sku")
                quantity = shipment.get("quantity")
                origin = shipment.get("origin")
                destination = shipment.get("destination")
                urgency = shipment.get("urgency", "normal")
                
                # Find best route for this shipment
                best_route = None
                best_score = -1
                
                for route_id, route_config in routes.items():
                    if route_config["origin"] != origin or route_config["destination"] != destination:
                        continue
                    
                    # Calculate route score based on cost, time, and capacity
                    cost = route_config["cost_per_km"] * route_config["distance"]
                    transit_time = route_config["transit_time"]
                    capacity = route_config["capacity"]
                    
                    # Check constraints
                    if quantity > capacity:
                        continue
                    
                    max_cost = constraints.get("max_cost", float('inf'))
                    max_transit_time = constraints.get("max_transit_time", float('inf'))
                    
                    if cost > max_cost or transit_time > max_transit_time:
                        continue
                    
                    # Calculate score (lower cost and time = higher score)
                    score = 1 / (cost * transit_time) if cost > 0 and transit_time > 0 else 0
                    
                    # Adjust for urgency
                    if urgency == "urgent":
                        score *= 2  # Prioritize faster routes
                    
                    if score > best_score:
                        best_score = score
                        best_route = {
                            "route_id": route_id,
                            "cost": cost,
                            "transit_time": transit_time,
                            "distance": route_config["distance"],
                            "capacity_utilization": round((quantity / capacity) * 100, 2)
                        }
                
                if best_route:
                    optimized_routes[f"{sku}_{origin}_{destination}"] = {
                        "sku": sku,
                        "quantity": quantity,
                        "origin": origin,
                        "destination": destination,
                        "selected_route": best_route,
                        "urgency": urgency
                    }
                    total_cost += best_route["cost"]
                    total_distance += best_route["distance"]
            
            return {
                "status": "success",
                "optimized_routes": optimized_routes,
                "total_cost": round(total_cost, 2),
                "total_distance": round(total_distance, 2),
                "shipments_optimized": len(optimized_routes),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in transportation planning: {e}")
            return {"error": str(e)}

    def rough_cut_capacity_planning(self, long_term_demand: Dict[str, float],
                                   resources: Dict[str, Dict[str, Any]],
                                   planning_horizon_months: int = 12) -> Dict[str, Any]:
        """
        Rough-cut capacity planning for long-term planning.
        
        Args:
            long_term_demand: SKU -> average monthly demand
            resources: Resource definitions
                - resource_id: {capacity, efficiency, cost_per_hour, availability}
            planning_horizon_months: Planning horizon in months
        """
        try:
            capacity_plan = {}
            resource_requirements = {}
            
            # Calculate monthly resource requirements
            for sku, monthly_demand in long_term_demand.items():
                # Assume resource requirements per unit (simplified)
                labor_hours_per_unit = 0.5
                machine_hours_per_unit = 0.3
                
                monthly_labor_hours = monthly_demand * labor_hours_per_unit
                monthly_machine_hours = monthly_demand * machine_hours_per_unit
                
                resource_requirements[sku] = {
                    "monthly_demand": monthly_demand,
                    "labor_hours_required": round(monthly_labor_hours, 2),
                    "machine_hours_required": round(monthly_machine_hours, 2),
                    "total_monthly_hours": round(monthly_labor_hours + monthly_machine_hours, 2)
                }
            
            # Calculate capacity gaps
            capacity_analysis = {}
            for resource_id, resource_config in resources.items():
                resource_capacity = resource_config.get("capacity", 0)  # hours per month
                efficiency = resource_config.get("efficiency", 1.0)
                effective_capacity = resource_capacity * efficiency
                cost_per_hour = resource_config.get("cost_per_hour", 0)
                
                # Calculate total requirement for this resource
                total_requirement = 0
                for sku_req in resource_requirements.values():
                    if "labor" in resource_id.lower():
                        total_requirement += sku_req["labor_hours_required"]
                    elif "machine" in resource_id.lower():
                        total_requirement += sku_req["machine_hours_required"]
                    else:
                        total_requirement += sku_req["total_monthly_hours"]
                
                capacity_gap = effective_capacity - total_requirement
                utilization_rate = (total_requirement / effective_capacity) * 100 if effective_capacity > 0 else 0
                
                capacity_analysis[resource_id] = {
                    "resource_id": resource_id,
                    "nominal_capacity": resource_capacity,
                    "efficiency_factor": efficiency,
                    "effective_capacity": round(effective_capacity, 2),
                    "total_requirement": round(total_requirement, 2),
                    "capacity_gap": round(capacity_gap, 2),
                    "utilization_rate": round(utilization_rate, 2),
                    "status": self._classify_capacity_status(utilization_rate),
                    "cost_per_month": round(total_requirement * cost_per_hour, 2),
                    "recommendations": self._generate_capacity_recommendations(utilization_rate, capacity_gap)
                }
            
            # Generate capacity plan for planning horizon
            monthly_plan = []
            for month in range(1, planning_horizon_months + 1):
                month_plan = {
                    "month": month,
                    "resource_requirements": {},
                    "capacity_status": {}
                }
                
                # Assume 5% demand growth per month (simplified)
                growth_factor = 1 + (month * 0.05)
                
                for resource_id, analysis in capacity_analysis.items():
                    adjusted_requirement = analysis["total_requirement"] * growth_factor
                    adjusted_gap = analysis["effective_capacity"] - adjusted_requirement
                    adjusted_utilization = (adjusted_requirement / analysis["effective_capacity"]) * 100 if analysis["effective_capacity"] > 0 else 0
                    
                    month_plan["resource_requirements"][resource_id] = round(adjusted_requirement, 2)
                    month_plan["capacity_status"][resource_id] = {
                        "utilization_rate": round(adjusted_utilization, 2),
                        "capacity_gap": round(adjusted_gap, 2),
                        "status": self._classify_capacity_status(adjusted_utilization)
                    }
                
                monthly_plan.append(month_plan)
            
            return {
                "status": "success",
                "resource_requirements": resource_requirements,
                "capacity_analysis": capacity_analysis,
                "monthly_capacity_plan": monthly_plan,
                "planning_horizon_months": planning_horizon_months,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_sp.error(f"Error in rough-cut capacity planning: {e}")
            return {"error": str(e)}

    def _classify_capacity_status(self, utilization_rate: float) -> str:
        """Classify capacity status based on utilization rate."""
        if utilization_rate > 100:
            return "CRITICAL_SHORTAGE"
        elif utilization_rate > 90:
            return "HIGH_UTILIZATION"
        elif utilization_rate > 75:
            return "NORMAL"
        elif utilization_rate > 50:
            return "UNDERUTILIZED"
        else:
            return "EXCESS_CAPACITY"

    def _generate_capacity_recommendations(self, utilization_rate: float, 
                                        capacity_gap: float) -> List[str]:
        """Generate capacity recommendations based on analysis."""
        recommendations = []
        
        if utilization_rate > 100:
            recommendations.append("Immediate capacity expansion required")
            recommendations.append("Consider outsourcing or overtime")
        elif utilization_rate > 90:
            recommendations.append("Plan capacity expansion in next quarter")
            recommendations.append("Monitor utilization closely")
        elif utilization_rate > 75:
            recommendations.append("Normal utilization - maintain current capacity")
        elif utilization_rate > 50:
            recommendations.append("Consider reducing capacity or increasing demand")
        else:
            recommendations.append("Significant excess capacity - consolidation recommended")
        
        if capacity_gap < 0:
            recommendations.append(f"Capacity gap of {abs(capacity_gap):.2f} hours needs to be addressed")
        
        return recommendations