"""
NEXUS — SAP IBP-Style Supply Planning API Router
=================================================
REST API endpoints for supply planning, production scheduling,
capacity optimization, and multi-site planning.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timezone, timedelta

from app.core.dependencies import get_db, get_current_user
from app.features.planning.supply.engine import SupplyPlanningEngine
from app.models.supply import (SupplyData, SupplyPlan, CapacityConstraint)

router = APIRouter(prefix="/ibp/supply", tags=["Supply Planning"])

# Global supply planning engine instance
supply_engine = SupplyPlanningEngine()


class ProductionScheduleRequest(BaseModel):
    """Request model for production scheduling."""
    demand_forecast: Dict[str, List[float]]
    lead_times: Dict[str, int]
    capacity: Dict[str, float]


class ConstraintOptimizationRequest(BaseModel):
    """Request model for constraint-based optimization."""
    demand_forecast: Dict[str, List[float]]
    constraints: Dict[str, Any]


class MultiSitePlanningRequest(BaseModel):
    """Request model for multi-site planning."""
    demand_forecast: Dict[str, List[float]]
    sites: Dict[str, Dict[str, Any]]
    transfer_costs: Dict[str, Dict[str, float]]


class SupplierCapacityRequest(BaseModel):
    """Request model for supplier capacity planning."""
    demand_forecast: Dict[str, List[float]]
    suppliers: Dict[str, Dict[str, Any]]


class TransportationRequest(BaseModel):
    """Request model for transportation planning."""
    shipments: List[Dict[str, Any]]
    routes: Dict[str, Dict[str, Any]]
    constraints: Dict[str, Any]


class RoughCutCapacityRequest(BaseModel):
    """Request model for rough-cut capacity planning."""
    long_term_demand: Dict[str, float]
    resources: Dict[str, Dict[str, Any]]
    planning_horizon_months: int = 12


class DRPRequest(BaseModel):
    """Request model for distribution requirements planning."""
    demand_forecast: Dict[str, List[float]]
    lead_times: Dict[str, int]


@router.post("/initialize")
async def initialize_supply_planning(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Initialize supply planning with supply chain data.
    """
    try:
        # Get supply data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "sku": s.sku,
            "supplier": s.supplier,
            "warehouse": s.warehouse,
            "region": s.region,
            "lead_time_days": s.delay_days,
            "capacity_daily": 1000,  # Default capacity
            "safety_stock": 100,  # Default safety stock
            "current_inventory": s.quantity
        } for s in supply_data])
        
        # Initialize engine
        result = supply_engine.initialize(df)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/production-schedule")
async def create_production_schedule(
    request: ProductionScheduleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create optimized production schedule based on demand forecast.
    """
    try:
        if not supply_engine._initialised:
            raise HTTPException(status_code=400, detail="Supply planning not initialized. Call /initialize first.")
        
        result = supply_engine.create_production_schedule(
            demand_forecast=request.demand_forecast,
            lead_times=request.lead_times,
            capacity=request.capacity
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="production_schedule",
            plan_type="production",
            planning_horizon=max(len(demand) for demand in request.demand_forecast.values()),
            plan_data=result,
            capacity_utilization=result.get("capacity_utilization"),
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/constraint-optimization")
async def constraint_based_optimization(
    request: ConstraintOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Advanced production scheduling with constraint optimization.
    """
    try:
        if not supply_engine._initialised:
            raise HTTPException(status_code=400, detail="Supply planning not initialized. Call /initialize first.")
        
        result = supply_engine.constraint_based_optimization(
            demand_forecast=request.demand_forecast,
            constraints=request.constraints
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="constraint_optimization",
            plan_type="production",
            planning_horizon=max(len(demand) for demand in request.demand_forecast.values()),
            plan_data=result,
            constraints=request.constraints,
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-site-planning")
async def multi_site_planning(
    request: MultiSitePlanningRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Multi-site production planning optimization.
    """
    try:
        if not supply_engine._initialised:
            raise HTTPException(status_code=400, detail="Supply planning not initialized. Call /initialize first.")
        
        result = supply_engine.multi_site_planning(
            demand_forecast=request.demand_forecast,
            sites=request.sites,
            transfer_costs=request.transfer_costs
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="multi_site_plan",
            plan_type="production",
            planning_horizon=max(len(demand) for demand in request.demand_forecast.values()),
            plan_data=result,
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/supplier-capacity")
async def supplier_capacity_planning(
    request: SupplierCapacityRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Supplier capacity planning and allocation.
    """
    try:
        if not supply_engine._initialised:
            raise HTTPException(status_code=400, detail="Supply planning not initialized. Call /initialize first.")
        
        result = supply_engine.supplier_capacity_planning(
            demand_forecast=request.demand_forecast,
            suppliers=request.suppliers
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="supplier_capacity_plan",
            plan_type="capacity",
            planning_horizon=max(len(demand) for demand in request.demand_forecast.values()),
            plan_data=result,
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transportation-planning")
async def transportation_planning(
    request: TransportationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Transportation planning and route optimization.
    """
    try:
        result = supply_engine.transportation_planning(
            shipments=request.shipments,
            routes=request.routes,
            constraints=request.constraints
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="transportation_plan",
            plan_type="distribution",
            planning_horizon=12,
            plan_data=result,
            constraints=request.constraints,
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rough-cut-capacity")
async def rough_cut_capacity_planning(
    request: RoughCutCapacityRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Rough-cut capacity planning for long-term planning.
    """
    try:
        result = supply_engine.rough_cut_capacity_planning(
            long_term_demand=request.long_term_demand,
            resources=request.resources,
            planning_horizon_months=request.planning_horizon_months
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="rough_cut_capacity_plan",
            plan_type="capacity",
            planning_horizon=request.planning_horizon_months,
            plan_data=result,
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drp")
async def distribution_requirements_planning(
    request: DRPRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate distribution requirements planning (DRP).
    """
    try:
        if not supply_engine._initialised:
            raise HTTPException(status_code=400, detail="Supply planning not initialized. Call /initialize first.")
        
        # Get inventory data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "warehouse": s.warehouse,
            "sku": s.sku,
            "current_inventory": s.quantity,
            "safety_stock": 100  # Default safety stock
        } for s in supply_data])
        
        result = supply_engine.distribution_requirements_planning(
            inventory_data=df,
            demand_forecast=request.demand_forecast,
            lead_times=request.lead_times
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save plan to database
        plan_record = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name="drp_plan",
            plan_type="distribution",
            planning_horizon=max(len(demand) for demand in request.demand_forecast.values()),
            plan_data=result,
            status="active"
        )
        db.add(plan_record)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capacity-analysis")
async def capacity_analysis(
    production_schedule: Dict[str, Any],
    resources: Dict[str, Dict[str, float]],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze capacity constraints and identify bottlenecks.
    """
    try:
        result = supply_engine.capacity_analysis(
            production_schedule=production_schedule,
            resources=resources
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/what-if")
async def what_if_analysis(
    base_scenario: Dict[str, Any],
    scenario_changes: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform what-if analysis for supply planning scenarios.
    """
    try:
        result = supply_engine.what_if_analysis(
            base_scenario=base_scenario,
            scenario_changes=scenario_changes
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans")
async def list_supply_plans(
    skip: int = 0,
    limit: int = 50,
    plan_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List stored supply plans.
    """
    try:
        query = db.query(SupplyPlan).filter(
            SupplyPlan.tenant_id == current_user.get("tenant_id", "default")
        )
        
        if plan_type:
            query = query.filter(SupplyPlan.plan_type == plan_type)
        
        plans = query.order_by(SupplyPlan.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "status": "success",
            "plans": [
                {
                    "id": p.id,
                    "plan_name": p.plan_name,
                    "plan_type": p.plan_type,
                    "planning_horizon": p.planning_horizon,
                    "created_at": p.created_at.isoformat(),
                    "status": p.status
                }
                for p in plans
            ],
            "total": len(plans)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan/{plan_id}")
async def get_supply_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific supply plan details.
    """
    try:
        plan = db.query(SupplyPlan).filter(
            SupplyPlan.id == plan_id,
            SupplyPlan.tenant_id == current_user.get("tenant_id", "default")
        ).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Supply plan not found")
        
        return {
            "status": "success",
            "plan": {
                "id": plan.id,
                "plan_name": plan.plan_name,
                "plan_type": plan.plan_type,
                "sku": plan.sku,
                "supplier": plan.supplier,
                "warehouse": plan.warehouse,
                "planning_horizon": plan.planning_horizon,
                "plan_data": plan.plan_data,
                "capacity_utilization": plan.capacity_utilization,
                "constraints": plan.constraints,
                "status": plan.status,
                "created_at": plan.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan/{plan_id}/approve")
async def approve_supply_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Approve a supply plan.
    """
    try:
        plan = db.query(SupplyPlan).filter(
            SupplyPlan.id == plan_id,
            SupplyPlan.tenant_id == current_user.get("tenant_id", "default")
        ).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Supply plan not found")
        
        plan.status = "active"
        plan.approved_at = datetime.now(timezone.utc)
        plan.approved_by = current_user.get("user_id")
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Supply plan approved successfully",
            "plan_id": plan_id,
            "approved_at": plan.approved_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan/{plan_id}/clone")
async def clone_supply_plan(
    plan_id: int,
    new_plan_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Clone an existing supply plan.
    """
    try:
        original_plan = db.query(SupplyPlan).filter(
            SupplyPlan.id == plan_id,
            SupplyPlan.tenant_id == current_user.get("tenant_id", "default")
        ).first()
        
        if not original_plan:
            raise HTTPException(status_code=404, detail="Supply plan not found")
        
        # Create cloned plan
        cloned_plan = SupplyPlan(
            tenant_id=current_user.get("tenant_id", "default"),
            plan_name=new_plan_name,
            plan_type=original_plan.plan_type,
            sku=original_plan.sku,
            supplier=original_plan.supplier,
            warehouse=original_plan.warehouse,
            planning_horizon=original_plan.planning_horizon,
            plan_data=original_plan.plan_data,
            capacity_utilization=original_plan.capacity_utilization,
            constraints=original_plan.constraints,
            version=original_plan.version + 1,
            status="draft",
            created_by=current_user.get("user_id")
        )
        
        db.add(cloned_plan)
        db.commit()
        
        return {
            "status": "success",
            "message": "Supply plan cloned successfully",
            "new_plan_id": cloned_plan.id,
            "original_plan_id": plan_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capacity-constraints")
async def list_capacity_constraints(
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List capacity constraints for supply planning.
    """
    try:
        query = db.query(CapacityConstraint).filter(
            CapacityConstraint.tenant_id == current_user.get("tenant_id", "default")
        )
        
        if resource_type:
            query = query.filter(CapacityConstraint.resource_type == resource_type)
        
        constraints = query.filter(CapacityConstraint.is_active == 1).all()
        
        return {
            "status": "success",
            "capacity_constraints": [
                {
                    "id": c.id,
                    "resource_id": c.resource_id,
                    "resource_type": c.resource_type,
                    "location": c.location,
                    "max_capacity": c.max_capacity,
                    "current_utilization": c.current_utilization,
                    "efficiency_factor": c.efficiency_factor,
                    "availability": c.availability,
                    "unit_of_measure": c.unit_of_measure,
                    "effective_date": c.effective_date.isoformat() if c.effective_date else None
                }
                for c in constraints
            ],
            "total": len(constraints)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capacity-constraints/add")
async def add_capacity_constraint(
    constraint_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a capacity constraint for supply planning.
    """
    try:
        constraint = CapacityConstraint(
            tenant_id=current_user.get("tenant_id", "default"),
            resource_id=constraint_data.get("resource_id"),
            resource_type=constraint_data.get("resource_type"),
            location=constraint_data.get("location"),
            max_capacity=constraint_data.get("max_capacity", 0),
            current_utilization=constraint_data.get("current_utilization", 0),
            efficiency_factor=constraint_data.get("efficiency_factor", 1.0),
            availability=constraint_data.get("availability", 1.0),
            unit_of_measure=constraint_data.get("unit_of_measure"),
            effective_date=pd.to_datetime(constraint_data.get("effective_date")) if constraint_data.get("effective_date") else datetime.now(timezone.utc),
            expiry_date=pd.to_datetime(constraint_data.get("expiry_date")) if constraint_data.get("expiry_date") else None,
            constraint_metadata=constraint_data.get("constraint_metadata"),
            is_active=1
        )
        
        db.add(constraint)
        db.commit()
        
        return {
            "status": "success",
            "constraint_id": constraint.id,
            "message": "Capacity constraint added successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
