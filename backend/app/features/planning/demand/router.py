"""
NEXUS — SAP IBP-Style Demand Planning API Router
==================================================
REST API endpoints for demand planning, forecasting,
and demand shaping capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timezone, timedelta

from app.core.dependencies import get_db, get_current_user
from app.features.planning.demand.engine import DemandPlanningEngine
from app.models.supply import (DemandForecast, SupplyData, CausalFactor, PromotionData, 
                                HolidayCalendar, EconomicIndicator, ExternalDataConnector, DemandSignal)

router = APIRouter(prefix="/ibp/demand", tags=["Demand Planning"])

# Global demand planning engine instance
demand_engine = DemandPlanningEngine()


class ForecastRequest(BaseModel):
    """Request model for demand forecasting."""
    horizon: int = 12
    sku_filter: Optional[List[str]] = None
    use_ensemble: bool = False
    model_types: Optional[List[str]] = None


class DemandSensingRequest(BaseModel):
    """Request model for demand sensing."""
    lookback_days: int = 30


class DemandShapingRequest(BaseModel):
    """Request model for demand shaping."""
    uplift_factor: float = 1.2
    target_skus: Optional[List[str]] = None
    promotion_description: Optional[str] = None


class HierarchicalForecastRequest(BaseModel):
    """Request model for hierarchical forecasting."""
    horizon: int = 12
    hierarchy: Dict[str, List[str]]


@router.post("/forecast/train")
async def train_demand_models(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Train demand forecasting models on historical data.
    
    Supports multiple statistical models:
    - Linear Regression (baseline)
    - Random Forest (non-linear)
    - ARIMA (time series)
    - Holt-Winters (exponential smoothing)
    """
    try:
        # Get historical demand data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "date": s.order_date,
            "sku": s.sku,
            "quantity": s.quantity,
            "supplier": s.supplier,
            "region": s.region,
            "warehouse": s.warehouse
        } for s in supply_data])
        
        # Train models
        result = demand_engine.fit(df)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/generate")
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate demand forecasts for specified horizon.
    
    Args:
        request: Forecast request with horizon and SKU filter
    """
    try:
        if not demand_engine._fitted:
            raise HTTPException(status_code=400, detail="Models not trained. Call /train first.")
        
        # Generate forecast
        result = demand_engine.forecast(
            horizon=request.horizon,
            sku_filter=request.sku_filter
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Save forecast to database
        for sku, forecast_data in result["forecasts"].items():
            forecast_record = DemandForecast(
                tenant_id=current_user.get("tenant_id", "default"),
                sku=sku,
                forecast_type="statistical",
                model_type=forecast_data.get("model_type", "unknown"),
                forecast_horizon=request.horizon,
                forecast_data=forecast_data,
                confidence_intervals=forecast_data.get("confidence_intervals"),
                accuracy_metrics=demand_engine.accuracy_metrics.get(sku),
                status="active"
            )
            db.add(forecast_record)
        
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demand-sensing")
async def demand_sensing(
    request: DemandSensingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform real-time demand sensing to detect emerging trends.
    
    Analyzes recent demand patterns and identifies significant changes.
    """
    try:
        # Get recent demand data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "date": s.order_date,
            "sku": s.sku,
            "quantity": s.quantity
        } for s in supply_data])
        
        # Perform demand sensing
        result = demand_engine.demand_sensing(df, lookback_days=request.lookback_days)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demand-shaping")
async def demand_shaping(
    request: DemandShapingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Simulate demand shaping scenarios (promotions, pricing changes).
    
    Calculates expected demand uplift from promotional activities.
    """
    try:
        # Get demand data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "sku": s.sku,
            "quantity": s.quantity
        } for s in supply_data])
        
        # Perform demand shaping
        scenario = {
            "uplift_factor": request.uplift_factor,
            "target_skus": request.target_skus or [],
            "description": request.promotion_description
        }
        
        result = demand_engine.demand_shaping(df, scenario)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/ensemble")
async def ensemble_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create ensemble forecast by combining multiple models.
    
    Ensemble methods often outperform individual models by averaging
    out biases and reducing variance.
    """
    try:
        if not demand_engine._fitted:
            raise HTTPException(status_code=400, detail="Models not trained. Call /train first.")
        
        # Generate forecasts from different models
        # For now, we'll use the existing forecast as a placeholder
        # In a full implementation, you'd generate forecasts from multiple model types
        
        result = demand_engine.forecast(
            horizon=request.horizon,
            sku_filter=request.sku_filter
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Placeholder for ensemble logic
        # In full implementation, you'd combine multiple model forecasts
        ensemble_result = {
            "status": "success",
            "message": "Ensemble forecasting - single model used as placeholder",
            "forecasts": result["forecasts"],
            "ensemble_weights": {"random_forest": 1.0}
        }
        
        return ensemble_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/hierarchical")
async def hierarchical_forecast(
    request: HierarchicalForecastRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform hierarchical forecasting with reconciliation.
    
    Generates forecasts at multiple levels (SKU, category, region)
    and ensures consistency across the hierarchy.
    """
    try:
        # Get demand data with hierarchy columns
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "date": s.order_date,
            "sku": s.sku,
            "quantity": s.quantity,
            "category": s.category,
            "region": s.region
        } for s in supply_data])
        
        # Perform hierarchical forecasting
        result = demand_engine.hierarchical_forecast(
            df=df,
            hierarchy=request.hierarchy,
            horizon=request.horizon
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasts")
async def list_forecasts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List stored demand forecasts.
    """
    try:
        forecasts = db.query(DemandForecast).filter(
            DemandForecast.tenant_id == current_user.get("tenant_id", "default")
        ).order_by(DemandForecast.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "status": "success",
            "forecasts": [
                {
                    "id": f.id,
                    "sku": f.sku,
                    "model_type": f.model_type,
                    "forecast_horizon": f.forecast_horizon,
                    "created_at": f.created_at.isoformat(),
                    "status": f.status
                }
                for f in forecasts
            ],
            "total": len(forecasts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{forecast_id}")
async def get_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific forecast details.
    """
    try:
        forecast = db.query(DemandForecast).filter(
            DemandForecast.id == forecast_id,
            DemandForecast.tenant_id == current_user.get("tenant_id", "default")
        ).first()
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        return {
            "status": "success",
            "forecast": {
                "id": forecast.id,
                "sku": forecast.sku,
                "forecast_type": forecast.forecast_type,
                "model_type": forecast.model_type,
                "forecast_horizon": forecast.forecast_horizon,
                "forecast_data": forecast.forecast_data,
                "confidence_intervals": forecast.confidence_intervals,
                "accuracy_metrics": forecast.accuracy_metrics,
                "created_at": forecast.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/causal-factors/add")
async def add_causal_factor(
    factor_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a causal factor (promotion, holiday, economic indicator) for demand planning.
    """
    try:
        causal_factor = CausalFactor(
            tenant_id=current_user.get("tenant_id", "default"),
            factor_type=factor_data.get("factor_type"),
            factor_name=factor_data.get("factor_name"),
            factor_category=factor_data.get("factor_category"),
            description=factor_data.get("description"),
            start_date=pd.to_datetime(factor_data.get("start_date")),
            end_date=pd.to_datetime(factor_data.get("end_date")) if factor_data.get("end_date") else None,
            impact_regions=factor_data.get("impact_regions"),
            impact_skus=factor_data.get("impact_skus"),
            impact_coefficient=factor_data.get("impact_coefficient", 1.0),
            confidence_level=factor_data.get("confidence_level", 0.5),
            is_active=1
        )
        
        db.add(causal_factor)
        db.commit()
        
        return {
            "status": "success",
            "causal_factor_id": causal_factor.id,
            "message": "Causal factor added successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/causal-factors")
async def list_causal_factors(
    factor_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List causal factors for demand planning.
    """
    try:
        query = db.query(CausalFactor).filter(
            CausalFactor.tenant_id == current_user.get("tenant_id", "default")
        )
        
        if factor_type:
            query = query.filter(CausalFactor.factor_type == factor_type)
        
        factors = query.order_by(CausalFactor.start_date.desc()).all()
        
        return {
            "status": "success",
            "causal_factors": [
                {
                    "id": f.id,
                    "factor_type": f.factor_type,
                    "factor_name": f.factor_name,
                    "start_date": f.start_date.isoformat(),
                    "end_date": f.end_date.isoformat() if f.end_date else None,
                    "impact_coefficient": f.impact_coefficient,
                    "confidence_level": f.confidence_level,
                    "is_active": f.is_active
                }
                for f in factors
            ],
            "total": len(factors)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ensemble/optimize")
async def optimize_ensemble(
    validation_data: Dict[str, Any],
    method: str = "performance_based",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Optimize ensemble model weights using automated weight tuning.
    """
    try:
        if not demand_engine._fitted:
            raise HTTPException(status_code=400, detail="Models not trained. Call /train first.")
        
        # Convert validation data to DataFrame
        df = pd.DataFrame(validation_data.get("data", []))
        
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="No validation data provided")
        
        # Optimize ensemble weights
        result = demand_engine.optimize_ensemble_weights(df, method=method)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hierarchical/reconcile")
async def hierarchical_reconciliation(
    forecast_data: Dict[str, Any],
    hierarchy_mapping: Dict[str, Dict[str, List[str]]],
    method: str = "bottom_up",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform hierarchical reconciliation across product/region hierarchies.
    """
    try:
        if not demand_engine._fitted:
            raise HTTPException(status_code=400, detail="Models not trained. Call /train first.")
        
        # Perform reconciliation
        result = demand_engine.hierarchical_reconciliation(
            bottom_up_forecasts=forecast_data.get("forecasts", {}),
            hierarchy_mapping=hierarchy_mapping,
            method=method
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/external-connectors/add")
async def add_external_connector(
    connector_config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add external data connector for real-time demand sensing.
    """
    try:
        # Add to database
        connector = ExternalDataConnector(
            tenant_id=current_user.get("tenant_id", "default"),
            connector_name=connector_config.get("connector_name"),
            connector_type=connector_config.get("connector_type"),
            config=connector_config.get("config"),
            endpoint_url=connector_config.get("endpoint_url"),
            authentication=connector_config.get("authentication"),
            refresh_interval_minutes=connector_config.get("refresh_interval_minutes", 60),
            data_fields=connector_config.get("data_fields"),
            mapping_rules=connector_config.get("mapping_rules"),
            is_active=1
        )
        
        db.add(connector)
        db.commit()
        
        # Add to engine
        engine_result = demand_engine.add_external_data_connector(
            connector_name=connector_config.get("connector_name"),
            connector_config=connector_config.get("config", {})
        )
        
        return {
            "status": "success",
            "connector_id": connector.id,
            "engine_result": engine_result
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/external-signals/fetch")
async def fetch_external_signals(
    connector_name: str,
    hours_back: int = 24,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch real-time demand signals from external data sources.
    """
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        result = demand_engine.fetch_external_demand_signals(
            connector_name=connector_name,
            time_range=(start_time, end_time)
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Store signals in database
        for signal in result.get("demand_signals", {}).get("signals", []):
            demand_signal = DemandSignal(
                tenant_id=current_user.get("tenant_id", "default"),
                signal_type=signal.get("signal_type"),
                source_connector=connector_name,
                timestamp=pd.to_datetime(signal.get("timestamp")),
                sku=signal.get("sku"),
                signal_data=signal,
                signal_strength=signal.get("signal_strength", 0.5),
                confidence=signal.get("confidence", 0.5),
                region=signal.get("location"),
                processed=0
            )
            db.add(demand_signal)
        
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/external-signals/integrate")
async def integrate_external_signals(
    base_forecast: Dict[str, Any],
    hours_back: int = 24,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Integrate real-time external signals into base demand forecast.
    """
    try:
        # Get recent signals from database
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        demand_signals = db.query(DemandSignal).filter(
            DemandSignal.tenant_id == current_user.get("tenant_id", "default"),
            DemandSignal.timestamp >= start_time,
            DemandSignal.timestamp <= end_time,
            DemandSignal.processed == 0
        ).all()
        
        if not demand_signals:
            return {
                "status": "success",
                "message": "No new signals to integrate",
                "adjusted_forecast": base_forecast
            }
        
        # Convert signals to list format
        external_signals = []
        for signal in demand_signals:
            signal_data = signal.signal_data
            signal_data["sku"] = signal.sku
            signal_data["signal_strength"] = signal.signal_strength
            external_signals.append(signal_data)
        
        # Integrate signals
        result = demand_engine.integrate_real_time_signals(base_forecast, external_signals)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Mark signals as processed
        for signal in demand_signals:
            signal.processed = 1
            signal.impact_applied = result.get("adjusted_forecast", {}).get("forecasts", {}).get(signal.sku, {}).get("signal_adjustment", {}).get("adjustment_factor")
        
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demand-shaping/optimize")
async def optimize_demand_shaping(
    base_demand: Dict[str, float],
    constraints: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Optimize demand shaping scenarios (pricing, promotion planning).
    """
    try:
        result = demand_engine.demand_shaping_optimization(base_demand, constraints)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/with-causal-factors")
async def forecast_with_causal_factors(
    causal_data: Dict[str, Any],
    horizon: int = 12,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Train and generate forecasts with causal factor integration.
    """
    try:
        # Get historical demand data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "date": s.order_date,
            "sku": s.sku,
            "quantity": s.quantity,
            "supplier": s.supplier,
            "region": s.region
        } for s in supply_data])
        
        # Convert causal data to DataFrames
        causal_dfs = {}
        for key, data in causal_data.items():
            if isinstance(data, list) and len(data) > 0:
                causal_dfs[key] = pd.DataFrame(data)
        
        # Train with causal factors
        result = demand_engine.fit_with_causal_factors(df, causal_dfs)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Generate forecast
        forecast_result = demand_engine.forecast(horizon=horizon)
        
        if forecast_result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Combine results
        combined_result = {
            "status": "success",
            "training_result": result,
            "forecast_result": forecast_result,
            "causal_factors_enabled": True
        }
        
        return combined_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hyperparameter-tuning")
async def hyperparameter_tuning(
    model_type: str = "random_forest",
    param_grid: Optional[Dict[str, List]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform hyperparameter tuning for specified model type.
    """
    try:
        # Get historical demand data
        supply_data = db.query(SupplyData).filter(
            SupplyData.tenant_id == current_user.get("tenant_id", "default")
        ).all()
        
        if not supply_data:
            raise HTTPException(status_code=404, detail="No supply data found")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            "date": s.order_date,
            "sku": s.sku,
            "quantity": s.quantity
        } for s in supply_data])
        
        # Perform hyperparameter tuning
        result = demand_engine.hyperparameter_tuning(df, model_type, param_grid)
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagnostics")
async def get_model_diagnostics():
    """
    Get diagnostic information from advanced ML models.
    """
    try:
        diagnostics = demand_engine.get_model_diagnostics()
        return {
            "status": "success",
            "diagnostics": diagnostics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
