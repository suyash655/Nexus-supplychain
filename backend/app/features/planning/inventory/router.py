"""
NEXUS — Inventory Optimization Router
======================================
API endpoints for inventory optimization including dynamic safety stock,
positioning optimization, perishable inventory management, and obsolescence risk.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_auth
from app.core.orchestrator import _load_dataframe
from app.features.planning.inventory.engine import InventoryOptimizationEngine

logger_io = logging.getLogger("nexus.inventory_optimization")

router = APIRouter(prefix="/inventory-optimization", tags=["Inventory Optimization"])

# Global engine instance
inventory_engine = InventoryOptimizationEngine()


class SafetyStockRequest(BaseModel):
    """Request model for safety stock calculation."""
    lead_times: Dict[str, int] = Field(default_factory=dict)
    service_levels: Dict[str, float] = Field(default_factory=dict)
    volatility_window: int = Field(30, ge=1, le=365)
    seasonal_adjustments: Optional[Dict[str, float]] = Field(default_factory=dict)


class PositioningOptimizationRequest(BaseModel):
    """Request model for inventory positioning optimization."""
    demand_forecast: Dict[str, list] = Field(default_factory=dict)
    cost_parameters: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    lead_times: Optional[Dict[str, int]] = Field(default_factory=dict)


class PerishableInventoryRequest(BaseModel):
    """Request model for perishable inventory management."""
    demand_forecast: Dict[str, list] = Field(default_factory=dict)
    shelf_life_params: Dict[str, Dict[str, float]] = Field(default_factory=dict)


class ObsolescenceRiskRequest(BaseModel):
    """Request model for obsolescence risk modeling."""
    product_lifecycle_params: Dict[str, Dict[str, float]] = Field(default_factory=dict)


@router.post("/initialize")
def initialize_optimization(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Initialize the inventory optimization engine with current data.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        result = inventory_engine.initialize(df)
        return result
    except Exception as e:
        logger_io.error(f"Error initializing inventory optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety-stock")
def calculate_safety_stock(
    request: SafetyStockRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Calculate safety stock levels using statistical methods.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Simulate demand data from current dataset
        demand_data = df.copy()
        if "date" not in demand_data.columns:
            demand_data["date"] = pd.date_range(start=datetime.now(timezone.utc), periods=len(demand_data), freq="D")
        if "quantity" not in demand_data.columns:
            demand_data["quantity"] = demand_data.get("quantity", 100)

        result = inventory_engine.calculate_safety_stock(
            demand_data,
            request.lead_times,
            request.service_levels
        )
        return result
    except Exception as e:
        logger_io.error(f"Error calculating safety stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dynamic-safety-stock")
def calculate_dynamic_safety_stock(
    request: SafetyStockRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Calculate dynamic safety stock with demand volatility modeling.
    Includes seasonal adjustments and trend analysis.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Simulate demand data from current dataset
        demand_data = df.copy()
        if "date" not in demand_data.columns:
            demand_data["date"] = pd.date_range(start=datetime.now(timezone.utc), periods=len(demand_data), freq="D")
        if "quantity" not in demand_data.columns:
            demand_data["quantity"] = demand_data.get("quantity", 100)

        result = inventory_engine.dynamic_safety_stock_adjustment(
            demand_data,
            request.lead_times,
            request.service_levels,
            request.volatility_window,
            request.seasonal_adjustments
        )
        return result
    except Exception as e:
        logger_io.error(f"Error calculating dynamic safety stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/eoq")
def calculate_eoq(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Calculate Economic Order Quantity (EOQ) for inventory items.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Simulate demand data
        demand_data = df.copy()
        if "quantity" not in demand_data.columns:
            demand_data["quantity"] = 100

        # Default cost parameters
        costs = {}
        for sku in demand_data.get("sku", ["default"]):
            costs[sku] = {
                "holding_cost": 0.25,
                "ordering_cost": 50.0
            }

        result = inventory_engine.economic_order_quantity(demand_data, costs)
        return result
    except Exception as e:
        logger_io.error(f"Error calculating EOQ: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/positioning-optimization")
def optimize_positioning(
    request: PositioningOptimizationRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Optimize inventory positioning (push vs pull strategies).
    Includes postponement strategy evaluation and cost-benefit analysis.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create network data from current dataset
        network_data = df.copy()
        if "echelon" not in network_data.columns:
            network_data["echelon"] = "warehouse"
        if "location" not in network_data.columns:
            network_data["location"] = "default_location"
        if "capacity" not in network_data.columns:
            network_data["capacity"] = 10000

        # Provide default demand forecast if not provided
        if not request.demand_forecast:
            skus = network_data.get("sku", ["default"]).unique() if "sku" in network_data else ["default"]
            request.demand_forecast = {sku: [100, 110, 105, 120, 115] for sku in skus}

        # Provide default cost parameters if not provided
        if not request.cost_parameters:
            locations = network_data.get("location", ["default"]).unique() if "location" in network_data else ["default"]
            request.cost_parameters = {
                loc: {
                    "holding_cost": 0.25,
                    "transportation_cost": 1.0,
                    "stockout_cost": 10.0
                }
                for loc in locations
            }

        # Provide default lead times if not provided
        if not request.lead_times:
            locations = network_data.get("location", ["default"]).unique() if "location" in network_data else ["default"]
            request.lead_times = dict.fromkeys(locations, 7)

        result = inventory_engine.inventory_positioning_optimization(
            network_data,
            request.demand_forecast,
            request.cost_parameters,
            request.lead_times
        )
        return result
    except Exception as e:
        logger_io.error(f"Error in positioning optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/perishable-management")
def manage_perishable_inventory(
    request: PerishableInventoryRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Manage perishable inventory with expiration tracking and optimization.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create inventory data
        inventory_data = df.copy()
        if "quantity" not in inventory_data.columns:
            inventory_data["quantity"] = 100

        # Provide default demand forecast if not provided
        if not request.demand_forecast:
            skus = inventory_data.get("sku", ["default"]).unique() if "sku" in inventory_data else ["default"]
            request.demand_forecast = {sku: [100, 110, 105, 120, 115] for sku in skus}

        # Provide default shelf life parameters if not provided
        if not request.shelf_life_params:
            skus = inventory_data.get("sku", ["default"]).unique() if "sku" in inventory_data else ["default"]
            request.shelf_life_params = {
                sku: {
                    "shelf_life_days": 30,
                    "deterioration_rate": 0.01,
                    "quality_threshold": 0.8
                }
                for sku in skus
            }

        result = inventory_engine.perishable_inventory_management(
            inventory_data,
            request.demand_forecast,
            request.shelf_life_params
        )
        return result
    except Exception as e:
        logger_io.error(f"Error in perishable inventory management: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/obsolescence-risk")
def model_obsolescence_risk(
    request: ObsolescenceRiskRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Model obsolescence risk and provide mitigation recommendations.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create inventory data
        inventory_data = df.copy()
        if "quantity" not in inventory_data.columns:
            inventory_data["quantity"] = 100
        if "unit_cost" not in inventory_data.columns:
            inventory_data["unit_cost"] = 10.0
        if "age_days" not in inventory_data.columns:
            inventory_data["age_days"] = 90

        # Create demand history
        demand_history = df.copy()
        if "date" not in demand_history.columns:
            demand_history["date"] = pd.date_range(start=datetime.now(timezone.utc), periods=len(demand_history), freq="D")
        if "quantity" not in demand_history.columns:
            demand_history["quantity"] = 100

        # Provide default lifecycle parameters if not provided
        if not request.product_lifecycle_params:
            skus = inventory_data.get("sku", ["default"]).unique() if "sku" in inventory_data else ["default"]
            current_date = datetime.now(timezone.utc)
            request.product_lifecycle_params = {
                sku: {
                    "launch_date": (current_date - pd.Timedelta(days=365)).isoformat(),
                    "maturity_date": (current_date - pd.Timedelta(days=180)).isoformat(),
                    "decline_date": (current_date + pd.Timedelta(days=180)).isoformat(),
                    "end_of_life_date": (current_date + pd.Timedelta(days=730)).isoformat()
                }
                for sku in skus
            }

        result = inventory_engine.obsolescence_risk_modeling(
            inventory_data,
            demand_history,
            request.product_lifecycle_params
        )
        return result
    except Exception as e:
        logger_io.error(f"Error in obsolescence risk modeling: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ServiceLevelOptimizationRequest(BaseModel):
    """Request model for service level optimization."""
    current_service_levels: Dict[str, float] = Field(default_factory=dict)
    inventory_costs: Dict[str, float] = Field(default_factory=dict)
    stockout_costs: Dict[str, float] = Field(default_factory=dict)
    demand_std_dev: Optional[Dict[str, float]] = Field(default_factory=dict)
    annual_demand: Optional[Dict[str, float]] = Field(default_factory=dict)


@router.post("/service-level-optimization")
def optimize_service_levels(
    request: ServiceLevelOptimizationRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Advanced service level optimization with cost trade-offs using newsvendor model.
    Includes sensitivity analysis and multi-objective optimization.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create sample data if not provided
        skus = df.get("sku", ["SKU-001"]).unique() if "sku" in df else ["SKU-001"]

        if not request.current_service_levels:
            request.current_service_levels = dict.fromkeys(skus, 0.95)
        if not request.inventory_costs:
            request.inventory_costs = dict.fromkeys(skus, 1.0)
        if not request.stockout_costs:
            request.stockout_costs = dict.fromkeys(skus, 10.0)
        if not request.demand_std_dev:
            request.demand_std_dev = dict.fromkeys(skus, 10.0)
        if not request.annual_demand:
            request.annual_demand = dict.fromkeys(skus, 1000.0)

        result = inventory_engine.service_level_optimization(
            request.current_service_levels,
            request.inventory_costs,
            request.stockout_costs,
            request.demand_std_dev,
            request.annual_demand
        )
        return result
    except Exception as e:
        logger_io.error(f"Error in service level optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-echelon")
def optimize_multi_echelon(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Perform multi-echelon inventory optimization.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create network data
        network_data = df.copy()
        if "echelon" not in network_data.columns:
            network_data["echelon"] = "warehouse"
        if "location" not in network_data.columns:
            network_data["location"] = "default_location"
        if "capacity" not in network_data.columns:
            network_data["capacity"] = 10000

        # Create demand forecast
        skus = network_data.get("sku", ["default"]).unique() if "sku" in network_data else ["default"]
        demand_forecast = {sku: [100, 110, 105, 120, 115] for sku in skus}

        result = inventory_engine.multi_echelon_optimization(network_data, demand_forecast)
        return result
    except Exception as e:
        logger_io.error(f"Error in multi-echelon optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abc-analysis")
def perform_abc_analysis(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Perform ABC analysis based on annual usage value.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create inventory data with required columns
        inventory_data = df.copy()
        if "quantity" not in inventory_data.columns:
            inventory_data["quantity"] = 100
        if "unit_cost" not in inventory_data.columns:
            inventory_data["unit_cost"] = 10.0
        if "sku" not in inventory_data.columns:
            inventory_data["sku"] = ["SKU-" + str(i) for i in range(len(inventory_data))]

        result = inventory_engine.abc_analysis(inventory_data)
        return result
    except Exception as e:
        logger_io.error(f"Error in ABC analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turnover-analysis")
def analyze_turnover(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Calculate inventory turnover and days inventory outstanding.
    """
    try:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Upload data first.")

        # Create inventory data
        inventory_data = df.copy()
        if "current_inventory" not in inventory_data.columns:
            inventory_data["current_inventory"] = 1000
        if "sku" not in inventory_data.columns:
            inventory_data["sku"] = ["SKU-" + str(i) for i in range(len(inventory_data))]
        if "warehouse" not in inventory_data.columns:
            inventory_data["warehouse"] = "WH-001"

        # Create sales data
        sales_data = df.copy()
        if "cost_of_goods_sold" not in sales_data.columns:
            sales_data["cost_of_goods_sold"] = 500
        if "sku" not in sales_data.columns:
            sales_data["sku"] = inventory_data["sku"]
        if "warehouse" not in sales_data.columns:
            sales_data["warehouse"] = "WH-001"

        result = inventory_engine.inventory_turnover_analysis(inventory_data, sales_data)
        return result
    except Exception as e:
        logger_io.error(f"Error in turnover analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
