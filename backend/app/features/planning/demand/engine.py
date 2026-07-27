"""
NEXUS — Demand Planning Engine (SAP IBP-style)
==============================================
Advanced demand forecasting with multiple statistical models,
demand sensing, and demand shaping capabilities.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
import warnings
warnings.filterwarnings('ignore')

# Try to import advanced forecasting libraries
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger_dp.warning("statsmodels not available - advanced forecasting disabled")

# Try to import Prophet for advanced forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger_dp.warning("Prophet not available - Prophet forecasting disabled")

# Try to import TensorFlow/Keras for LSTM
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger_dp.warning("TensorFlow not available - LSTM forecasting disabled")

logger_dp = logging.getLogger("nexus.demand_planning")


class DemandPlanningEngine:
    """
    Enterprise-grade demand planning with statistical forecasting,
    causal factor analysis, and scenario modeling.
    """

    def __init__(self):
        self.models = {}
        self.forecasts = {}
        self.accuracy_metrics = {}
        self._fitted = False
        self._prophet_diagnostics = {}
        self._lstm_diagnostics = {}
        self.causal_factors = {}
        self.ensemble_weights = {}
        self.external_data_connectors = {}

    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train demand forecasting models on historical data.
        
        Expected columns:
        - date: shipment/order date
        - sku: product identifier
        - quantity: demand quantity
        - supplier: supplier (optional)
        - region: region (optional)
        - promotional_flag: boolean for promotions (optional)
        - seasonality_factor: seasonal adjustment (optional)
        """
        if "date" not in df.columns or "quantity" not in df.columns:
            return {"error": "Missing required columns: date, quantity", "fitted": False}

        try:
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            
            results = {
                "status": "success",
                "models_trained": [],
                "accuracy_metrics": {},
                "forecast_horizon": 12,  # 12 periods default
                "trained_at": datetime.now(timezone.utc).isoformat()
            }

            # Aggregate demand by date and SKU
            daily_demand = df.groupby(["date", "sku"]).agg({
                "quantity": "sum",
                "supplier": "first",
                "region": "first"
            }).reset_index()

            # Train models for each SKU
            for sku in daily_demand["sku"].unique():
                sku_data = daily_demand[daily_demand["sku"] == sku].copy()
                
                if len(sku_data) < 8:  # Need minimum data points
                    logger_dp.warning(f"Insufficient data for SKU {sku}, skipping")
                    continue

                model_result = self._train_sku_model(sku, sku_data)
                if model_result["status"] == "success":
                    self.models[sku] = model_result["model"]
                    self.accuracy_metrics[sku] = model_result["metrics"]
                    results["models_trained"].append(sku)
                    results["accuracy_metrics"][sku] = model_result["metrics"]

            self._fitted = len(self.models) > 0
            results["total_skus"] = len(daily_demand["sku"].unique())
            results["models_trained_count"] = len(self.models)
            
            return results

        except Exception as e:
            logger_dp.error(f"Error fitting demand planning models: {e}")
            return {"error": str(e), "fitted": False}

    def _train_sku_model(self, sku: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Train forecasting models for a specific SKU."""
        try:
            # Create features
            data = data.copy()
            data["day_of_week"] = data["date"].dt.dayofweek
            data["day_of_month"] = data["date"].dt.day
            data["month"] = data["date"].dt.month
            data["quarter"] = data["date"].dt.quarter
            data["week_of_year"] = data["date"].dt.isocalendar().week.astype(int)
            
            # Lag features
            data["lag_1"] = data["quantity"].shift(1)
            data["lag_7"] = data["quantity"].shift(7)
            data["lag_30"] = data["quantity"].shift(30) if len(data) >= 30 else np.nan
            
            # Rolling statistics
            data["rolling_mean_7"] = data["quantity"].rolling(7).mean()
            data["rolling_std_7"] = data["quantity"].rolling(7).std()
            
            # Trend component
            data["trend"] = range(len(data))
            
            # Drop NaN values
            data = data.dropna()
            
            if len(data) < 5:
                return {"status": "insufficient_data", "sku": sku}

            # Features and target
            feature_cols = ["day_of_week", "day_of_month", "month", "quarter", 
                          "week_of_year", "lag_1", "lag_7", "lag_30",
                          "rolling_mean_7", "rolling_std_7", "trend"]
            
            X = data[feature_cols].values
            y = data["quantity"].values
            
            # Split train/test
            split_idx = int(len(data) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train models
            models = {}
            predictions = {}
            
            # Linear Regression (baseline)
            lr = LinearRegression()
            lr.fit(X_train_scaled, y_train)
            lr_pred = lr.predict(X_test_scaled)
            models["linear"] = {"model": lr, "scaler": scaler}
            predictions["linear"] = lr_pred
            
            # Random Forest (non-linear)
            rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            rf.fit(X_train_scaled, y_train)
            rf_pred = rf.predict(X_test_scaled)
            models["random_forest"] = {"model": rf, "scaler": scaler}
            predictions["random_forest"] = rf_pred
            
            # Advanced statistical models (if available)
            if STATSMODELS_AVAILABLE and len(data) >= 24:  # Need sufficient data
                try:
                    # Prepare time series data
                    ts_data = data.set_index("date")["quantity"].asfreq('D').fillna(method='ffill')
                    
                    # ARIMA
                    if len(ts_data) >= 24:
                        arima_model = ARIMA(ts_data, order=(1, 1, 1))
                        arima_fit = arima_model.fit()
                        arima_pred = arima_fit.forecast(steps=len(y_test))
                        if len(arima_pred) == len(y_test):
                            models["arima"] = {"model": arima_fit, "type": "arima"}
                            predictions["arima"] = arima_pred.values
                except Exception as e:
                    logger_dp.warning(f"ARIMA failed for SKU {sku}: {e}")
                
                try:
                    # Holt-Winters
                    if len(ts_data) >= 24:
                        hw_model = ExponentialSmoothing(ts_data, trend='add', seasonal='add', seasonal_periods=7)
                        hw_fit = hw_model.fit()
                        hw_pred = hw_fit.forecast(steps=len(y_test))
                        if len(hw_pred) == len(y_test):
                            models["holt_winters"] = {"model": hw_fit, "type": "hw"}
                            predictions["holt_winters"] = hw_pred.values
                except Exception as e:
                    logger_dp.warning(f"Holt-Winters failed for SKU {sku}: {e}")

            # Prophet forecasting (if available)
            if PROPHET_AVAILABLE and len(data) >= 30:  # Prophet needs at least 30 data points
                try:
                    prophet_pred = self._train_prophet_model(data, y_test)
                    if prophet_pred is not None and len(prophet_pred) == len(y_test):
                        models["prophet"] = {"model": "prophet_trained", "type": "prophet"}
                        predictions["prophet"] = prophet_pred
                except Exception as e:
                    logger_dp.warning(f"Prophet failed for SKU {sku}: {e}")

            # LSTM forecasting (if available)
            if TENSORFLOW_AVAILABLE and len(data) >= 60:  # LSTM needs more data
                try:
                    lstm_pred = self._train_lstm_model(data, y_test)
                    if lstm_pred is not None and len(lstm_pred) == len(y_test):
                        models["lstm"] = {"model": "lstm_trained", "type": "lstm"}
                        predictions["lstm"] = lstm_pred
                except Exception as e:
                    logger_dp.warning(f"LSTM failed for SKU {sku}: {e}")
            
            # Calculate metrics
            metrics = {}
            for model_name, pred in predictions.items():
                # Ensure predictions match test set length
                if len(pred) != len(y_test):
                    continue
                    
                mae = mean_absolute_error(y_test, pred)
                rmse = np.sqrt(mean_squared_error(y_test, pred))
                mape = np.mean(np.abs((y_test - pred) / (y_test + 1e-8))) * 100  # Avoid division by zero
                
                metrics[model_name] = {
                    "mae": round(mae, 2),
                    "rmse": round(rmse, 2),
                    "mape": round(mape, 2),
                    "bias": round(np.mean(pred - y_test), 2)
                }
            
            # Select best model (lowest MAPE)
            if metrics:
                best_model = min(metrics.items(), key=lambda x: x[1]["mape"])[0]
            else:
                best_model = "linear"  # Fallback to baseline
            
            return {
                "status": "success",
                "sku": sku,
                "model": models.get(best_model, models.get("linear")),
                "model_type": best_model,
                "metrics": metrics.get(best_model, metrics.get("linear", {})),
                "all_metrics": metrics
            }
            
        except Exception as e:
            logger_dp.error(f"Error training model for SKU {sku}: {e}")
            return {"status": "error", "sku": sku, "error": str(e)}

    def _train_prophet_model(self, data: pd.DataFrame, y_test: np.ndarray) -> Optional[np.ndarray]:
        """Train Prophet model for forecasting with enhanced configuration."""
        try:
            # Prepare data for Prophet (requires columns: ds, y)
            prophet_data = data[["date", "quantity"]].copy()
            prophet_data.columns = ["ds", "y"]
            
            # Split into train/test
            split_idx = int(len(prophet_data) * 0.8)
            train_data = prophet_data[:split_idx]
            
            # Enhanced Prophet model with better hyperparameters
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05,  # More flexible trend
                seasonality_prior_scale=10.0,  # Stronger seasonality
                holidays_prior_scale=10.0,
                mcmc_samples=0,  # Faster training
                interval_width=0.95,  # 95% confidence intervals
                growth='linear'  # Can be 'logistic' for saturating growth
            )
            
            # Add custom seasonality if data supports it
            if len(train_data) >= 365:  # Add monthly seasonality for yearly data
                model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            
            # Add changepoints for known events if available
            # model.add_changepoints([...])  # Would be populated with known event dates
            
            model.fit(train_data)
            
            # Make predictions for test period
            future_dates = model.make_future_dataframe(periods=len(y_test))
            forecast = model.predict(future_dates)
            
            # Extract predictions for test period
            predictions = forecast['yhat'].values[-len(y_test):]
            
            # Ensure non-negative
            predictions = np.maximum(predictions, 0)
            
            # Store additional Prophet diagnostics
            self._prophet_diagnostics = {
                'components': forecast[['trend', 'seasonal', 'weekly', 'yearly']].tail(len(y_test)).values.tolist(),
                'confidence_intervals': {
                    'lower': forecast['yhat_lower'].values[-len(y_test):].tolist(),
                    'upper': forecast['yhat_upper'].values[-len(y_test):].tolist()
                }
            }
            
            return predictions
            
        except Exception as e:
            logger_dp.error(f"Error in Prophet training: {e}")
            return None

    def _train_lstm_model(self, data: pd.DataFrame, y_test: np.ndarray) -> Optional[np.ndarray]:
        """Train enhanced LSTM model for time series forecasting with feature engineering."""
        try:
            # Prepare time series data with features
            data = data.copy()
            data = data.sort_values("date")
            
            # Create additional features
            data["day_of_week"] = data["date"].dt.dayofweek
            data["day_of_month"] = data["date"].dt.day
            data["month"] = data["date"].dt.month
            data["quarter"] = data["date"].dt.quarter
            data["week_of_year"] = data["date"].dt.isocalendar().week.astype(int)
            
            # Lag features
            for lag in [1, 7, 14, 30]:
                data[f"lag_{lag}"] = data["quantity"].shift(lag)
            
            # Rolling statistics
            data["rolling_mean_7"] = data["quantity"].rolling(7).mean()
            data["rolling_std_7"] = data["quantity"].rolling(7).std()
            data["rolling_mean_14"] = data["quantity"].rolling(14).mean()
            
            # Drop NaN values
            data = data.dropna()
            
            if len(data) < 60:  # Need minimum data for LSTM
                return None
            
            # Prepare features
            feature_cols = ["quantity", "day_of_week", "day_of_month", "month", "quarter", 
                          "week_of_year", "lag_1", "lag_7", "lag_14", "lag_30",
                          "rolling_mean_7", "rolling_std_7", "rolling_mean_14"]
            
            feature_data = data[feature_cols].values
            
            # Normalize features
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(feature_data)
            
            # Create sequences for LSTM with multiple features
            sequence_length = 14  # Use 14 days to predict next day
            X, y = [], []
            
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:i + sequence_length, :])  # All features
                y.append(scaled_data[i + sequence_length, 0])  # Predict quantity (first column)
            
            X, y = np.array(X), np.array(y)
            
            # Split train/test
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test_scaled = y[:split_idx], y[split_idx:]
            
            # Build enhanced LSTM model
            model = Sequential([
                LSTM(64, return_sequences=True, input_shape=(sequence_length, len(feature_cols))),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32, return_sequences=False),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dense(8, activation='relu'),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Train with early stopping and learning rate reduction
            from tensorflow.keras.callbacks import ReduceLROnPlateau
            early_stopping = EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=0.0001)
            
            model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_test, y_test_scaled),
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Make predictions
            predictions_scaled = model.predict(X_test, verbose=0)
            
            # Inverse transform to original scale (only for quantity column)
            # Create a dummy array with same shape as original features
            dummy_array = np.zeros((len(predictions_scaled), len(feature_cols)))
            dummy_array[:, 0] = predictions_scaled.flatten()
            
            predictions = scaler.inverse_transform(dummy_array)[:, 0]
            
            # Ensure non-negative
            predictions = np.maximum(predictions, 0)
            
            # Store LSTM diagnostics
            self._lstm_diagnostics = {
                'training_history': {
                    'final_loss': model.history.history['loss'][-1] if model.history.history else 0,
                    'final_val_loss': model.history.history['val_loss'][-1] if model.history.history else 0
                },
                'feature_importance': {
                    'total_features': len(feature_cols),
                    'sequence_length': sequence_length
                }
            }
            
            return predictions
            
        except Exception as e:
            logger_dp.error(f"Error in LSTM training: {e}")
            return None

    def forecast(self, horizon: int = 12, sku_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate demand forecasts for specified horizon.
        
        Args:
            horizon: Number of periods to forecast
            sku_filter: Optional list of SKUs to forecast (default: all)
        """
        if not self._fitted:
            return {"error": "Models not fitted. Call fit() first."}

        try:
            skus_to_forecast = sku_filter if sku_filter else list(self.models.keys())
            forecasts = {}
            
            for sku in skus_to_forecast:
                if sku not in self.models:
                    continue
                
                model_data = self.models[sku]
                model = model_data["model"]
                scaler = model_data["scaler"]
                
                # Generate future dates
                last_date = datetime.now(timezone.utc)
                future_dates = [last_date + timedelta(days=i) for i in range(1, horizon + 1)]
                
                # Create features for future dates
                future_features = []
                for date in future_dates:
                    features = [
                        date.weekday(),
                        date.day,
                        date.month,
                        (date.month - 1) // 3 + 1,
                        date.isocalendar()[1],
                        0,  # lag_1 (will use forecast)
                        0,  # lag_7
                        0,  # lag_30
                        0,  # rolling_mean_7
                        0,  # rolling_std_7
                        len(future_features)  # trend
                    ]
                    future_features.append(features)
                
                X_future = scaler.transform(np.array(future_features))
                predictions = model.predict(X_future)
                
                # Ensure non-negative forecasts
                predictions = np.maximum(predictions, 0)
                
                forecasts[sku] = {
                    "dates": [d.isoformat() for d in future_dates],
                    "forecast": predictions.tolist(),
                    "confidence_intervals": self._calculate_confidence_intervals(predictions),
                    "model_type": model_data.get("model_type", "unknown")
                }
            
            return {
                "status": "success",
                "forecasts": forecasts,
                "horizon": horizon,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_skus": len(forecasts)
            }
            
        except Exception as e:
            logger_dp.error(f"Error generating forecasts: {e}")
            return {"error": str(e)}

    def _calculate_confidence_intervals(self, predictions: np.ndarray, 
                                        confidence: float = 0.95) -> Dict[str, List[float]]:
        """Calculate confidence intervals for forecasts."""
        std_dev = np.std(predictions) * 0.2  # Assume 20% variability
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        lower = predictions - z_score * std_dev
        upper = predictions + z_score * std_dev
        
        return {
            "lower": np.maximum(lower, 0).tolist(),
            "upper": upper.tolist(),
            "confidence": confidence
        }

    def demand_sensing(self, df: pd.DataFrame, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Real-time demand sensing using recent demand patterns.
        Identifies demand shifts and emerging trends.
        """
        try:
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            recent_data = df[df["date"] >= cutoff_date]
            
            if len(recent_data) == 0:
                return {"error": "No recent data available for demand sensing"}
            
            # Calculate demand velocity
            daily_demand = recent_data.groupby(["date", "sku"]).agg({
                "quantity": "sum"
            }).reset_index()
            
            # Compare with historical baseline
            historical_data = df[df["date"] < cutoff_date]
            historical_baseline = historical_data.groupby("sku")["quantity"].mean()
            
            sensed_signals = []
            
            for sku in daily_demand["sku"].unique():
                sku_recent = daily_demand[daily_demand["sku"] == sku]["quantity"].mean()
                sku_baseline = historical_baseline.get(sku, sku_recent)
                
                if sku_baseline > 0:
                    demand_change_pct = ((sku_recent - sku_baseline) / sku_baseline) * 100
                    
                    signal = {
                        "sku": sku,
                        "recent_demand": round(sku_recent, 2),
                        "baseline_demand": round(sku_baseline, 2),
                        "change_percentage": round(demand_change_pct, 2),
                        "signal": self._classify_demand_signal(demand_change_pct),
                        "confidence": self._calculate_signal_confidence(len(daily_demand[daily_demand["sku"] == sku]))
                    }
                    
                    if abs(demand_change_pct) > 15:  # Only significant changes
                        sensed_signals.append(signal)
            
            return {
                "status": "success",
                "signals": sensed_signals,
                "analysis_period": f"Last {lookback_days} days",
                "total_signals": len(sensed_signals),
                "significant_changes": len([s for s in sensed_signals if abs(s["change_percentage"]) > 25])
            }
            
        except Exception as e:
            logger_dp.error(f"Error in demand sensing: {e}")
            return {"error": str(e)}

    def _classify_demand_signal(self, change_pct: float) -> str:
        """Classify demand change signal."""
        if change_pct > 30:
            return "SURGE"
        elif change_pct > 15:
            return "INCREASE"
        elif change_pct < -30:
            return "PLUNGE"
        elif change_pct < -15:
            return "DECREASE"
        else:
            return "STABLE"

    def _calculate_signal_confidence(self, data_points: int) -> float:
        """Calculate confidence in demand signal based on data points."""
        return min(1.0, data_points / 10)  # More data = higher confidence

    def demand_shaping(self, df: pd.DataFrame, 
                      promotion_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate demand shaping scenarios (promotions, pricing changes).
        """
        try:
            # Extract baseline demand
            baseline_demand = df.groupby("sku")["quantity"].mean()
            
            # Apply scenario uplift
            uplift_factor = promotion_scenario.get("uplift_factor", 1.2)
            target_skus = promotion_scenario.get("target_skus", [])
            
            shaped_demand = {}
            
            for sku in baseline_demand.index:
                if sku in target_skus or not target_skus:
                    shaped_demand[sku] = {
                        "baseline": round(baseline_demand[sku], 2),
                        "shaped": round(baseline_demand[sku] * uplift_factor, 2),
                        "uplift": round((baseline_demand[sku] * uplift_factor - baseline_demand[sku]), 2),
                        "uplift_percentage": round((uplift_factor - 1) * 100, 2)
                    }
            
            total_baseline = sum(d["baseline"] for d in shaped_demand.values())
            total_shaped = sum(d["shaped"] for d in shaped_demand.values())
            
            return {
                "status": "success",
                "scenario": promotion_scenario,
                "results": shaped_demand,
                "summary": {
                    "total_baseline": round(total_baseline, 2),
                    "total_shaped": round(total_shaped, 2),
                    "total_uplift": round(total_shaped - total_baseline, 2),
                    "uplift_percentage": round(((total_shaped - total_baseline) / total_baseline) * 100, 2)
                }
            }
            
        except Exception as e:
            logger_dp.error(f"Error in demand shaping: {e}")
            return {"error": str(e)}

    def ensemble_forecast(self, forecasts: Dict[str, Dict[str, Any]], 
                         weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Create ensemble forecast by combining multiple models.
        
        Args:
            forecasts: Dictionary of model_name -> forecast results
            weights: Optional weights for each model (default: equal weights)
        """
        try:
            if not forecasts:
                return {"error": "No forecasts provided for ensemble"}
            
            # Get SKUs from first forecast
            sample_forecast = list(forecasts.values())[0]
            skus = sample_forecast.get("forecasts", {}).keys()
            
            # Default weights: equal weight for all models
            if weights is None:
                num_models = len(forecasts)
                weights = {model: 1.0/num_models for model in forecasts.keys()}
            
            # Normalize weights
            total_weight = sum(weights.values())
            weights = {k: v/total_weight for k, v in weights.items()}
            
            ensemble_results = {}
            
            for sku in skus:
                ensemble_forecast = []
                ensemble_lower = []
                ensemble_upper = []
                
                # Collect forecasts from all models for this SKU
                model_forecasts = []
                for model_name, forecast_data in forecasts.items():
                    sku_forecast = forecast_data.get("forecasts", {}).get(sku, {})
                    if sku_forecast and "forecast" in sku_forecast:
                        model_forecasts.append(sku_forecast)
                
                if not model_forecasts:
                    continue
                
                # Calculate weighted average
                for i in range(len(model_forecasts[0]["forecast"])):
                    weighted_sum = 0
                    weighted_lower = 0
                    weighted_upper = 0
                    
                    for model_name, sku_forecast in zip(forecasts.keys(), model_forecasts):
                        weight = weights[model_name]
                        weighted_sum += sku_forecast["forecast"][i] * weight
                        
                        if "confidence_intervals" in sku_forecast:
                            weighted_lower += sku_forecast["confidence_intervals"]["lower"][i] * weight
                            weighted_upper += sku_forecast["confidence_intervals"]["upper"][i] * weight
                    
                    ensemble_forecast.append(weighted_sum)
                    ensemble_lower.append(weighted_lower)
                    ensemble_upper.append(weighted_upper)
                
                ensemble_results[sku] = {
                    "dates": model_forecasts[0]["dates"],
                    "forecast": ensemble_forecast,
                    "confidence_intervals": {
                        "lower": ensemble_lower,
                        "upper": ensemble_upper,
                        "confidence": 0.95
                    },
                    "model_type": "ensemble",
                    "ensemble_weights": weights
                }
            
            return {
                "status": "success",
                "forecasts": ensemble_results,
                "ensemble_weights": weights,
                "models_combined": list(forecasts.keys()),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error in ensemble forecasting: {e}")
            return {"error": str(e)}

    def hierarchical_forecast(self, df: pd.DataFrame, hierarchy: Dict[str, List[str]],
                             horizon: int = 12) -> Dict[str, Any]:
        """
        Perform hierarchical forecasting with top-down and bottom-up reconciliation.
        
        Args:
            df: Demand data with date, sku, and hierarchy columns
            hierarchy: Dictionary defining hierarchy levels (e.g., {"category": ["A", "B"], "region": ["US", "EU"]})
            horizon: Forecast horizon
        """
        try:
            # Fit base models at lowest level
            base_result = self.fit(df)
            
            if base_result.get("status") != "success":
                return base_result
            
            # Generate forecasts at SKU level
            sku_forecasts = self.forecast(horizon)
            
            if sku_forecasts.get("status") != "success":
                return sku_forecasts
            
            # Aggregate forecasts up the hierarchy
            hierarchical_results = {
                "sku_level": sku_forecasts["forecasts"],
                "aggregated_levels": {}
            }
            
            # Aggregate by hierarchy levels
            for level, levels in hierarchy.items():
                if level not in df.columns:
                    continue
                
                level_forecasts = {}
                
                for level_value in levels:
                    # Get SKUs for this level
                    level_skus = df[df[level] == level_value]["sku"].unique()
                    
                    # Aggregate SKU forecasts
                    aggregated_forecast = []
                    for i in range(horizon):
                        period_sum = 0
                        for sku in level_skus:
                            if sku in sku_forecasts["forecasts"]:
                                period_sum += sku_forecasts["forecasts"][sku]["forecast"][i]
                        aggregated_forecast.append(period_sum)
                    
                    level_forecasts[f"{level}_{level_value}"] = {
                        "dates": sku_forecasts["forecasts"].get(list(sku_forecasts["forecasts"].keys())[0], {}).get("dates", []),
                        "forecast": aggregated_forecast,
                        "constituent_skus": list(level_skus),
                        "level": level,
                        "level_value": level_value
                    }
                
                hierarchical_results["aggregated_levels"][level] = level_forecasts
            
            return {
                "status": "success",
                "hierarchical_forecasts": hierarchical_results,
                "hierarchy_levels": list(hierarchy.keys()),
                "reconciliation_method": "bottom_up",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error in hierarchical forecasting: {e}")
            return {"error": str(e)}

    def hierarchical_reconciliation(self, bottom_up_forecasts: Dict[str, Any],
                                   hierarchy_mapping: Dict[str, Dict[str, List[str]]],
                                   method: str = "bottom_up") -> Dict[str, Any]:
        """
        Perform hierarchical reconciliation across product/region hierarchies.
        
        Args:
            bottom_up_forecasts: Forecasts at the lowest level (SKU)
            hierarchy_mapping: Dictionary defining hierarchy structure
                e.g., {"category": {"electronics": ["sku1", "sku2"]}, "region": {"US": ["sku1", "sku3"]}}
            method: Reconciliation method ('bottom_up', 'top_down', 'optimal')
        """
        try:
            reconciled_forecasts = {}
            
            if method == "bottom_up":
                # Bottom-up: Aggregate lower-level forecasts
                reconciled_forecasts = self._bottom_up_reconciliation(bottom_up_forecasts, hierarchy_mapping)
            
            elif method == "top_down":
                # Top-down: Disaggregate higher-level forecasts
                reconciled_forecasts = self._top_down_reconciliation(bottom_up_forecasts, hierarchy_mapping)
            
            elif method == "optimal":
                # Optimal reconciliation: Minimize forecast error
                reconciled_forecasts = self._optimal_reconciliation(bottom_up_forecasts, hierarchy_mapping)
            
            else:
                return {"error": f"Unknown reconciliation method: {method}"}
            
            return {
                "status": "success",
                "reconciled_forecasts": reconciled_forecasts,
                "reconciliation_method": method,
                "hierarchy_levels": list(hierarchy_mapping.keys()),
                "reconciled_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error in hierarchical reconciliation: {e}")
            return {"error": str(e)}

    def _bottom_up_reconciliation(self, forecasts: Dict[str, Any], 
                                 hierarchy: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """Bottom-up reconciliation: aggregate SKU forecasts to higher levels."""
        reconciled = {"sku_level": forecasts}
        
        for level, level_mapping in hierarchy.items():
            level_forecasts = {}
            
            for level_value, skus in level_mapping.items():
                # Aggregate forecasts for SKUs in this level
                if level_value not in level_forecasts:
                    level_forecasts[level_value] = {
                        "dates": [],
                        "forecast": [],
                        "constituent_skus": skus
                    }
                
                # Get forecast length from first SKU
                first_sku = skus[0] if skus else None
                if first_sku and first_sku in forecasts:
                    level_forecasts[level_value]["dates"] = forecasts[first_sku].get("dates", [])
                    forecast_length = len(forecasts[first_sku].get("forecast", []))
                else:
                    continue
                
                # Aggregate forecasts across SKUs
                for i in range(forecast_length):
                    period_sum = 0
                    for sku in skus:
                        if sku in forecasts and i < len(forecasts[sku].get("forecast", [])):
                            period_sum += forecasts[sku]["forecast"][i]
                    level_forecasts[level_value]["forecast"].append(period_sum)
            
            reconciled[f"{level}_level"] = level_forecasts
        
        return reconciled

    def _top_down_reconciliation(self, forecasts: Dict[str, Any], 
                               hierarchy: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """Top-down reconciliation: disaggregate higher-level forecasts to SKUs."""
        reconciled = {}
        
        # First, create aggregate forecasts
        aggregate_forecasts = {}
        for level, level_mapping in hierarchy.items():
            for level_value, skus in level_mapping.items():
                # Create aggregate forecast by summing SKU forecasts
                if level_value not in aggregate_forecasts:
                    aggregate_forecasts[level_value] = []
                
                first_sku = skus[0] if skus else None
                if first_sku and first_sku in forecasts:
                    forecast_length = len(forecasts[first_sku].get("forecast", []))
                    
                    for i in range(forecast_length):
                        period_sum = 0
                        for sku in skus:
                            if sku in forecasts and i < len(forecasts[sku].get("forecast", [])):
                                period_sum += forecasts[sku]["forecast"][i]
                        aggregate_forecasts[level_value].append(period_sum)
        
        # Then, disaggregate based on historical proportions
        reconciled["sku_level"] = {}
        for level, level_mapping in hierarchy.items():
            for level_value, skus in level_mapping.items():
                if level_value not in aggregate_forecasts:
                    continue
                
                # Calculate historical proportions (simplified - equal weights)
                proportions = {sku: 1.0/len(skus) for sku in skus}
                
                # Disaggregate aggregate forecast
                for sku in skus:
                    if sku not in reconciled["sku_level"]:
                        reconciled["sku_level"][sku] = {
                            "dates": forecasts.get(sku, {}).get("dates", []),
                            "forecast": [],
                            "disaggregated_from": f"{level}_{level_value}"
                        }
                    
                    for i, aggregate_value in enumerate(aggregate_forecasts[level_value]):
                        reconciled["sku_level"][sku]["forecast"].append(
                            aggregate_value * proportions[sku]
                        )
        
        # Add aggregate levels
        for level, level_mapping in hierarchy.items():
            reconciled[f"{level}_level"] = {}
            for level_value, skus in level_mapping.items():
                reconciled[f"{level}_level"][level_value] = {
                    "dates": forecasts.get(skus[0], {}).get("dates", []) if skus else [],
                    "forecast": aggregate_forecasts.get(level_value, []),
                    "constituent_skus": skus
                }
        
        return reconciled

    def _optimal_reconciliation(self, forecasts: Dict[str, Any], 
                              hierarchy: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """Optimal reconciliation: minimize forecast error using regression-based approach."""
        # Simplified optimal reconciliation using weighted approach
        reconciled = self._bottom_up_reconciliation(forecasts, hierarchy)
        
        # Apply smoothing weights based on forecast accuracy
        for sku in forecasts.keys():
            if sku in reconciled["sku_level"]:
                accuracy = self.accuracy_metrics.get(sku, {}).get("mape", 100)
                weight = max(0.1, 1.0 - (accuracy / 200))  # Higher accuracy = higher weight
                
                # Blend bottom-up with original forecast
                original_forecast = forecasts[sku].get("forecast", [])
                reconciled_forecast = reconciled["sku_level"][sku].get("forecast", [])
                
                if len(original_forecast) == len(reconciled_forecast):
                    blended_forecast = [
                        (1 - weight) * orig + weight * reconciled
                        for orig, reconciled in zip(original_forecast, reconciled_forecast)
                    ]
                    reconciled["sku_level"][sku]["forecast"] = blended_forecast
                    reconciled["sku_level"][sku]["reconciliation_weight"] = weight
        
        return reconciled

    def hyperparameter_tuning(self, df: pd.DataFrame, 
                            model_type: str = "random_forest",
                            param_grid: Optional[Dict[str, List]] = None) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning for specified model type.
        
        Args:
            df: Training data
            model_type: Type of model to tune ('random_forest', 'linear', etc.)
            param_grid: Custom parameter grid (default provided)
        """
        try:
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            
            # Prepare features
            df["day_of_week"] = df["date"].dt.dayofweek
            df["day_of_month"] = df["date"].dt.day
            df["month"] = df["date"].dt.month
            df["quarter"] = df["date"].dt.quarter
            df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
            df["lag_1"] = df["quantity"].shift(1)
            df["lag_7"] = df["quantity"].shift(7)
            df["rolling_mean_7"] = df["quantity"].rolling(7).mean()
            df["trend"] = range(len(df))
            
            df = df.dropna()
            
            if len(df) < 20:
                return {"error": "Insufficient data for hyperparameter tuning"}
            
            feature_cols = ["day_of_week", "day_of_month", "month", "quarter", 
                          "week_of_year", "lag_1", "lag_7", "rolling_mean_7", "trend"]
            
            X = df[feature_cols].values
            y = df["quantity"].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            tuning_results = {
                "model_type": model_type,
                "best_params": {},
                "best_score": 0,
                "cv_results": {}
            }
            
            if model_type == "random_forest":
                # Default parameter grid for Random Forest
                default_param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
                param_grid = param_grid or default_param_grid
                
                model = RandomForestRegressor(random_state=42)
                grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
                grid_search.fit(X_train_scaled, y_train)
                
                tuning_results["best_params"] = grid_search.best_params_
                tuning_results["best_score"] = -grid_search.best_score_
                tuning_results["cv_results"] = {
                    "mean_test_score": (-grid_search.cv_results_['mean_test_score']).tolist(),
                    "std_test_score": grid_search.cv_results_['std_test_score'].tolist()
                }
                
                # Evaluate on test set
                best_model = grid_search.best_estimator_
                y_pred = best_model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                tuning_results["test_mae"] = round(mae, 2)
                
            elif model_type == "linear":
                # Linear regression doesn't have many hyperparameters, but we can test different feature sets
                feature_sets = [
                    ["day_of_week", "month", "lag_1"],
                    ["day_of_week", "month", "lag_1", "lag_7", "rolling_mean_7"],
                    feature_cols
                ]
                
                best_mae = float('inf')
                best_features = None
                
                for features in feature_sets:
                    feature_indices = [feature_cols.index(f) for f in features if f in feature_cols]
                    X_train_subset = X_train_scaled[:, feature_indices]
                    X_test_subset = X_test_scaled[:, feature_indices]
                    
                    model = LinearRegression()
                    model.fit(X_train_subset, y_train)
                    y_pred = model.predict(X_test_subset)
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    if mae < best_mae:
                        best_mae = mae
                        best_features = features
                
                tuning_results["best_params"] = {"features": best_features}
                tuning_results["best_score"] = best_mae
                tuning_results["test_mae"] = round(best_mae, 2)
            
            return {
                "status": "success",
                "tuning_results": tuning_results,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error in hyperparameter tuning: {e}")
            return {"error": str(e)}

    def add_causal_factors(self, df: pd.DataFrame, 
                          causal_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Integrate causal factors (promotions, holidays, economic indicators) into demand planning.
        
        Args:
            df: Base demand data
            causal_data: Dictionary of causal factor DataFrames
                - promotions: DataFrame with promotion data (date, sku, promotion_type, discount_pct)
                - holidays: DataFrame with holiday data (date, holiday_name, region)
                - economic: DataFrame with economic indicators (date, indicator_name, value)
        """
        try:
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
            
            enhanced_data = df.copy()
            causal_features = {}
            
            # Process promotion data
            if "promotions" in causal_data:
                promo_df = causal_data["promotions"].copy()
                promo_df["date"] = pd.to_datetime(promo_df["date"])
                
                # Merge promotion data
                enhanced_data = enhanced_data.merge(
                    promo_df[["date", "sku", "promotion_type", "discount_pct"]], 
                    on=["date", "sku"], 
                    how="left"
                )
                
                # Fill missing promotion data
                enhanced_data["promotion_type"] = enhanced_data["promotion_type"].fillna("none")
                enhanced_data["discount_pct"] = enhanced_data["discount_pct"].fillna(0)
                
                # Create promotion impact features
                enhanced_data["is_promotion"] = (enhanced_data["promotion_type"] != "none").astype(int)
                enhanced_data["pre_promotion"] = enhanced_data["is_promotion"].shift(1).fillna(0).astype(int)
                enhanced_data["post_promotion"] = enhanced_data["is_promotion"].shift(-1).fillna(0).astype(int)
                
                # Add cumulative promotion impact
                enhanced_data["promotion_momentum"] = enhanced_data["is_promotion"].rolling(7).sum().fillna(0)
                
                causal_features["promotions"] = {
                    "promotion_types": enhanced_data["promotion_type"].unique().tolist(),
                    "avg_discount": enhanced_data["discount_pct"].mean(),
                    "promotion_frequency": enhanced_data["is_promotion"].sum() / len(enhanced_data),
                    "promotion_lift_estimate": self._estimate_promotion_lift(enhanced_data)
                }
            
            # Process holiday data
            if "holidays" in causal_data:
                holiday_df = causal_data["holidays"].copy()
                holiday_df["date"] = pd.to_datetime(holiday_df["date"])
                
                # Create holiday calendar
                holiday_dates = set(holiday_df["date"].dt.date)
                
                # Add holiday features
                enhanced_data["is_holiday"] = enhanced_data["date"].dt.date.isin(holiday_dates).astype(int)
                enhanced_data["pre_holiday"] = enhanced_data["is_holiday"].shift(1).fillna(0).astype(int)
                enhanced_data["post_holiday"] = enhanced_data["is_holiday"].shift(-1).fillna(0).astype(int)
                
                # Add weekend before holiday feature
                enhanced_data["is_weekend"] = (enhanced_data["date"].dt.dayofweek >= 5).astype(int)
                enhanced_data["weekend_before_holiday"] = (
                    (enhanced_data["is_weekend"] == 1) & 
                    (enhanced_data["is_holiday"].shift(-1).fillna(0) == 1)
                ).astype(int)
                
                # Add holiday seasonality
                enhanced_data["holiday_season_intensity"] = enhanced_data["is_holiday"].rolling(14).sum().fillna(0)
                
                causal_features["holidays"] = {
                    "total_holidays": len(holiday_dates),
                    "holiday_regions": holiday_df["region"].unique().tolist() if "region" in holiday_df.columns else [],
                    "holiday_impact_estimate": self._estimate_holiday_impact(enhanced_data)
                }
            
            # Process economic indicators
            if "economic" in causal_data:
                econ_df = causal_data["economic"].copy()
                econ_df["date"] = pd.to_datetime(econ_df["date"])
                
                # Pivot economic data to wide format
                econ_pivot = econ_df.pivot(index="date", columns="indicator_name", values="value")
                
                # Merge economic data
                enhanced_data = enhanced_data.merge(
                    econ_pivot, 
                    on="date", 
                    how="left"
                )
                
                # Forward fill missing economic data
                econ_columns = econ_pivot.columns
                for col in econ_columns:
                    if col in enhanced_data.columns:
                        enhanced_data[col] = enhanced_data[col].fillna(method="ffill")
                        enhanced_data[col] = enhanced_data[col].fillna(enhanced_data[col].mean())
                
                causal_features["economic"] = {
                    "indicators": econ_columns.tolist(),
                    "correlations": {}
                }
                
                # Calculate correlations with demand
                for col in econ_columns:
                    if col in enhanced_data.columns:
                        corr = enhanced_data[[col, "quantity"]].corr().iloc[0, 1]
                        causal_features["economic"]["correlations"][col] = round(corr, 3)
                
                # Add economic composite index
                enhanced_data["economic_index"] = enhanced_data[list(econ_columns)].mean(axis=1)
            
            # Store causal factor information
            self.causal_factors = {
                "features": causal_features,
                "data_columns": [col for col in enhanced_data.columns if col not in df.columns or col in ["promotion_type", "discount_pct"]]
            }
            
            return {
                "status": "success",
                "causal_features_added": len(self.causal_factors["data_columns"]),
                "feature_details": causal_features,
                "enhanced_data_shape": enhanced_data.shape,
                "original_data_shape": df.shape
            }
            
        except Exception as e:
            logger_dp.error(f"Error adding causal factors: {e}")
            return {"error": str(e)}

    def _estimate_promotion_lift(self, df: pd.DataFrame) -> float:
        """Estimate the average demand lift during promotions."""
        try:
            promo_demand = df[df["is_promotion"] == 1]["quantity"].mean()
            non_promo_demand = df[df["is_promotion"] == 0]["quantity"].mean()
            
            if non_promo_demand > 0:
                lift = ((promo_demand - non_promo_demand) / non_promo_demand) * 100
                return round(lift, 2)
            return 0.0
        except:
            return 0.0

    def _estimate_holiday_impact(self, df: pd.DataFrame) -> float:
        """Estimate the average demand impact during holidays."""
        try:
            holiday_demand = df[df["is_holiday"] == 1]["quantity"].mean()
            non_holiday_demand = df[df["is_holiday"] == 0]["quantity"].mean()
            
            if non_holiday_demand > 0:
                impact = ((holiday_demand - non_holiday_demand) / non_holiday_demand) * 100
                return round(impact, 2)
            return 0.0
        except:
            return 0.0

    def fit_with_causal_factors(self, df: pd.DataFrame, 
                               causal_data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
        """
        Train demand forecasting models with causal factor integration.
        
        Args:
            df: Base demand data
            causal_data: Optional causal factor data
        """
        try:
            # Add causal factors if provided
            if causal_data:
                causal_result = self.add_causal_factors(df, causal_data)
                if causal_result.get("status") == "success":
                    df = df.copy()
                    df["date"] = pd.to_datetime(df["date"])
                    
                    # Re-add causal features to training data
                    if "promotions" in causal_data:
                        promo_df = causal_data["promotions"].copy()
                        promo_df["date"] = pd.to_datetime(promo_df["date"])
                        df = df.merge(
                            promo_df[["date", "sku", "promotion_type", "discount_pct"]], 
                            on=["date", "sku"], 
                            how="left"
                        )
                        df["promotion_type"] = df["promotion_type"].fillna("none")
                        df["discount_pct"] = df["discount_pct"].fillna(0)
                        df["is_promotion"] = (df["promotion_type"] != "none").astype(int)
                    
                    if "holidays" in causal_data:
                        holiday_df = causal_data["holidays"].copy()
                        holiday_df["date"] = pd.to_datetime(holiday_df["date"])
                        holiday_dates = set(holiday_df["date"].dt.date)
                        df["is_holiday"] = df["date"].dt.date.isin(holiday_dates).astype(int)
                    
                    if "economic" in causal_data:
                        econ_df = causal_data["economic"].copy()
                        econ_df["date"] = pd.to_datetime(econ_df["date"])
                        econ_pivot = econ_df.pivot(index="date", columns="indicator_name", values="value")
                        df = df.merge(econ_pivot, on="date", how="left")
                        for col in econ_pivot.columns:
                            if col in df.columns:
                                df[col] = df[col].fillna(method="ffill").fillna(df[col].mean())
            
            # Call original fit method with enhanced data
            result = self.fit(df)
            
            if result.get("status") == "success":
                result["causal_factors_enabled"] = causal_data is not None
                result["causal_features"] = self.causal_factors.get("features", {})
            
            return result
            
        except Exception as e:
            logger_dp.error(f"Error fitting with causal factors: {e}")
            return {"error": str(e)}

    def optimize_ensemble_weights(self, validation_data: pd.DataFrame, 
                                 method: str = "performance_based") -> Dict[str, Any]:
        """
        Optimize ensemble model weights using automated weight tuning.
        
        Args:
            validation_data: Validation data for weight optimization
            method: Optimization method ('performance_based', 'equal', 'custom')
        """
        try:
            if not self._fitted:
                return {"error": "Models not fitted. Call fit() first."}
            
            validation_data = validation_data.copy()
            validation_data["date"] = pd.to_datetime(validation_data["date"])
            
            optimized_weights = {}
            
            for sku in self.models.keys():
                sku_data = validation_data[validation_data["sku"] == sku].copy()
                
                if len(sku_data) < 5:
                    continue
                
                # Create features for validation
                sku_data["day_of_week"] = sku_data["date"].dt.dayofweek
                sku_data["day_of_month"] = sku_data["date"].dt.day
                sku_data["month"] = sku_data["date"].dt.month
                sku_data["quarter"] = sku_data["date"].dt.quarter
                sku_data["week_of_year"] = sku_data["date"].dt.isocalendar().week.astype(int)
                sku_data["lag_1"] = sku_data["quantity"].shift(1)
                sku_data["lag_7"] = sku_data["quantity"].shift(7)
                sku_data["rolling_mean_7"] = sku_data["quantity"].rolling(7).mean()
                sku_data["trend"] = range(len(sku_data))
                
                sku_data = sku_data.dropna()
                
                if len(sku_data) < 3:
                    continue
                
                feature_cols = ["day_of_week", "day_of_month", "month", "quarter", 
                              "week_of_year", "lag_1", "lag_7", "rolling_mean_7", "trend"]
                
                X_val = sku_data[feature_cols].values
                y_val = sku_data["quantity"].values
                
                # Get predictions from different model types
                model_predictions = {}
                
                # Linear regression predictions
                if "linear" in self.models[sku]:
                    lr_model = self.models[sku]["linear"]["model"]
                    lr_scaler = self.models[sku]["linear"]["scaler"]
                    X_val_scaled = lr_scaler.transform(X_val)
                    model_predictions["linear"] = lr_model.predict(X_val_scaled)
                
                # Random forest predictions
                if "random_forest" in self.models[sku]:
                    rf_model = self.models[sku]["random_forest"]["model"]
                    rf_scaler = self.models[sku]["random_forest"]["scaler"]
                    X_val_scaled = rf_scaler.transform(X_val)
                    model_predictions["random_forest"] = rf_model.predict(X_val_scaled)
                
                # If we have multiple models, optimize weights
                if len(model_predictions) >= 2:
                    if method == "performance_based":
                        # Calculate weights based on inverse of MAE
                        mae_scores = {}
                        for model_name, pred in model_predictions.items():
                            mae = mean_absolute_error(y_val, pred)
                            mae_scores[model_name] = mae
                        
                        # Inverse MAE weighting (lower MAE = higher weight)
                        inv_mae = {k: 1/v for k, v in mae_scores.items()}
                        total_inv_mae = sum(inv_mae.values())
                        weights = {k: v/total_inv_mae for k, v in inv_mae.items()}
                        
                    elif method == "equal":
                        # Equal weights
                        weights = {k: 1.0/len(model_predictions) for k in model_predictions.keys()}
                    
                    else:
                        # Default to performance-based
                        weights = {k: 1.0/len(model_predictions) for k in model_predictions.keys()}
                    
                    optimized_weights[sku] = weights
                    
                    # Calculate ensemble performance
                    ensemble_pred = np.zeros_like(y_val, dtype=float)
                    for model_name, pred in model_predictions.items():
                        ensemble_pred += pred * weights[model_name]
                    
                    ensemble_mae = mean_absolute_error(y_val, ensemble_pred)
                    
                    optimized_weights[sku]["ensemble_mae"] = ensemble_mae
                    optimized_weights[sku]["individual_mae"] = {
                        k: mean_absolute_error(y_val, v) for k, v in model_predictions.items()
                    }
                else:
                    # Single model - weight = 1.0
                    optimized_weights[sku] = {
                        list(model_predictions.keys())[0]: 1.0,
                        "ensemble_mae": mean_absolute_error(y_val, list(model_predictions.values())[0])
                    }
            
            self.ensemble_weights = optimized_weights
            
            return {
                "status": "success",
                "optimized_weights": optimized_weights,
                "optimization_method": method,
                "skus_optimized": len(optimized_weights),
                "optimized_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error optimizing ensemble weights: {e}")
            return {"error": str(e)}

    def get_model_diagnostics(self) -> Dict[str, Any]:
        """
        Get diagnostic information from advanced ML models.
        """
        diagnostics = {
            "prophet_available": PROPHET_AVAILABLE,
            "lstm_available": TENSORFLOW_AVAILABLE,
            "prophet_diagnostics": self._prophet_diagnostics,
            "lstm_diagnostics": self._lstm_diagnostics
        }
        
        return diagnostics

    def add_external_data_connector(self, connector_name: str, 
                                   connector_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add external data connector for real-time demand sensing.
        
        Args:
            connector_name: Name of the connector (e.g., 'pos_system', 'social_media', 'weather_api')
            connector_config: Configuration for the connector
        """
        try:
            self.external_data_connectors[connector_name] = {
                "config": connector_config,
                "last_fetch": None,
                "status": "active"
            }
            
            return {
                "status": "success",
                "connector_added": connector_name,
                "connector_type": connector_config.get("type", "unknown"),
                "added_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error adding external data connector: {e}")
            return {"error": str(e)}

    def fetch_external_demand_signals(self, connector_name: str, 
                                    time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """
        Fetch real-time demand signals from external data sources.
        
        Args:
            connector_name: Name of the connector to use
            time_range: Time range for data fetch (start, end)
        """
        try:
            if connector_name not in self.external_data_connectors:
                return {"error": f"Connector {connector_name} not found"}
            
            connector = self.external_data_connectors[connector_name]
            config = connector["config"]
            
            # Simulate external data fetch (in production, this would call actual APIs)
            demand_signals = {
                "connector": connector_name,
                "data_type": config.get("type", "unknown"),
                "signals": [],
                "time_range": {
                    "start": time_range[0].isoformat(),
                    "end": time_range[1].isoformat()
                }
            }
            
            # Generate simulated signals based on connector type
            if config.get("type") == "pos_system":
                # Simulate POS data signals
                demand_signals["signals"] = self._generate_pos_signals(config, time_range)
            elif config.get("type") == "social_media":
                # Simulate social media sentiment signals
                demand_signals["signals"] = self._generate_social_signals(config, time_range)
            elif config.get("type") == "weather_api":
                # Simulate weather impact signals
                demand_signals["signals"] = self._generate_weather_signals(config, time_range)
            else:
                # Generic signals
                demand_signals["signals"] = self._generate_generic_signals(config, time_range)
            
            # Update connector status
            self.external_data_connectors[connector_name]["last_fetch"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "status": "success",
                "demand_signals": demand_signals,
                "signals_count": len(demand_signals["signals"]),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error fetching external demand signals: {e}")
            return {"error": str(e)}

    def _generate_pos_signals(self, config: Dict[str, Any], 
                            time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate simulated POS demand signals."""
        signals = []
        num_signals = config.get("signal_count", 10)
        
        for i in range(num_signals):
            signal_time = time_range[0] + timedelta(
                seconds=np.random.randint(0, int((time_range[1] - time_range[0]).total_seconds()))
            )
            
            signals.append({
                "timestamp": signal_time.isoformat(),
                "signal_type": "pos_transaction",
                "sku": f"SKU_{np.random.randint(1, 100)}",
                "quantity": np.random.randint(1, 50),
                "location": config.get("location", "store_1"),
                "signal_strength": np.random.uniform(0.5, 1.0)
            })
        
        return signals

    def _generate_social_signals(self, config: Dict[str, Any], 
                                time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate simulated social media sentiment signals."""
        signals = []
        num_signals = config.get("signal_count", 5)
        
        for i in range(num_signals):
            signal_time = time_range[0] + timedelta(
                seconds=np.random.randint(0, int((time_range[1] - time_range[0]).total_seconds()))
            )
            
            sentiment_score = np.random.uniform(-1, 1)
            signal_type = "positive" if sentiment_score > 0.3 else "negative" if sentiment_score < -0.3 else "neutral"
            
            signals.append({
                "timestamp": signal_time.isoformat(),
                "signal_type": "social_sentiment",
                "platform": config.get("platform", "twitter"),
                "sentiment_score": round(sentiment_score, 3),
                "signal_type": signal_type,
                "related_skus": [f"SKU_{np.random.randint(1, 100)}" for _ in range(np.random.randint(1, 3))],
                "signal_strength": abs(sentiment_score)
            })
        
        return signals

    def _generate_weather_signals(self, config: Dict[str, Any], 
                                  time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate simulated weather impact signals."""
        signals = []
        num_signals = config.get("signal_count", 3)
        
        for i in range(num_signals):
            signal_time = time_range[0] + timedelta(
                seconds=np.random.randint(0, int((time_range[1] - time_range[0]).total_seconds()))
            )
            
            weather_conditions = ["sunny", "rainy", "cloudy", "stormy", "snowy"]
            condition = np.random.choice(weather_conditions)
            
            signals.append({
                "timestamp": signal_time.isoformat(),
                "signal_type": "weather_impact",
                "condition": condition,
                "temperature": np.random.randint(-10, 35),
                "location": config.get("location", "region_1"),
                "impact_score": np.random.uniform(0.3, 1.0) if condition in ["stormy", "snowy"] else np.random.uniform(0.1, 0.5),
                "affected_categories": config.get("affected_categories", ["all"])
            })
        
        return signals

    def _generate_generic_signals(self, config: Dict[str, Any], 
                                 time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate generic external signals."""
        signals = []
        num_signals = config.get("signal_count", 5)
        
        for i in range(num_signals):
            signal_time = time_range[0] + timedelta(
                seconds=np.random.randint(0, int((time_range[1] - time_range[0]).total_seconds()))
            )
            
            signals.append({
                "timestamp": signal_time.isoformat(),
                "signal_type": "external_event",
                "event_type": config.get("event_type", "general"),
                "impact_level": np.random.choice(["low", "medium", "high"]),
                "signal_strength": np.random.uniform(0.3, 1.0)
            })
        
        return signals

    def integrate_real_time_signals(self, base_forecast: Dict[str, Any],
                                  external_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Integrate real-time external signals into base demand forecast.
        
        Args:
            base_forecast: Base forecast from statistical models
            external_signals: List of external demand signals
        """
        try:
            adjusted_forecast = base_forecast.copy()
            
            # Group signals by SKU
            sku_signals = {}
            for signal in external_signals:
                sku = signal.get("sku", "all")
                if sku not in sku_signals:
                    sku_signals[sku] = []
                sku_signals[sku].append(signal)
            
            # Apply signal adjustments to forecasts
            for sku, forecast_data in adjusted_forecast.get("forecasts", {}).items():
                relevant_signals = sku_signals.get(sku, []) + sku_signals.get("all", [])
                
                if not relevant_signals:
                    continue
                
                # Calculate aggregate signal impact
                total_impact = 0
                signal_count = 0
                
                for signal in relevant_signals:
                    signal_strength = signal.get("signal_strength", 0.5)
                    total_impact += signal_strength
                    signal_count += 1
                
                if signal_count > 0:
                    avg_impact = total_impact / signal_count
                    
                    # Apply adjustment factor
                    adjustment_factor = 1.0 + (avg_impact - 0.5) * 0.3  # Max 15% adjustment
                    
                    # Adjust forecast values
                    original_forecast = forecast_data.get("forecast", [])
                    adjusted_forecast["forecasts"][sku]["forecast"] = [
                        round(val * adjustment_factor, 2) for val in original_forecast
                    ]
                    adjusted_forecast["forecasts"][sku]["signal_adjustment"] = {
                        "adjustment_factor": round(adjustment_factor, 3),
                        "signals_applied": signal_count,
                        "average_signal_strength": round(avg_impact, 3)
                    }
            
            return {
                "status": "success",
                "adjusted_forecast": adjusted_forecast,
                "signals_integrated": len(external_signals),
                "skus_adjusted": len([s for s in adjusted_forecast.get("forecasts", {}).values() if "signal_adjustment" in s]),
                "adjusted_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_dp.error(f"Error integrating real-time signals: {e}")
            return {"error": str(e)}

    def demand_shaping_optimization(self, base_demand: Dict[str, float],
                                  constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize demand shaping scenarios (pricing, promotion planning).
        
        Args:
            base_demand: Base demand by SKU
            constraints: Shaping constraints (budget, max_uplift, etc.)
        """
        try:
            optimization_results = {}
            
            max_budget = constraints.get("max_budget", 10000)
            max_uplift = constraints.get("max_uplift", 1.5)  # 50% max uplift
            target_skus = constraints.get("target_skus", list(base_demand.keys()))
            
            # Simulate promotion scenarios
            scenarios = []
            
            for sku in target_skus:
                if sku not in base_demand:
                    continue
                
                baseline = base_demand[sku]
                
                # Generate different promotion scenarios
                promotion_types = [
                    {"type": "discount_10", "uplift": 1.15, "cost": baseline * 0.10},
                    {"type": "discount_20", "uplift": 1.25, "cost": baseline * 0.20},
                    {"type": "discount_30", "uplift": 1.35, "cost": baseline * 0.30},
                    {"type": "bundle", "uplift": 1.20, "cost": baseline * 0.15},
                    {"type": "loyalty", "uplift": 1.10, "cost": baseline * 0.05}
                ]
                
                for promo in promotion_types:
                    shaped_demand = baseline * promo["uplift"]
                    uplift_value = shaped_demand - baseline
                    roi = uplift_value / promo["cost"] if promo["cost"] > 0 else 0
                    
                    scenarios.append({
                        "sku": sku,
                        "promotion_type": promo["type"],
                        "baseline": baseline,
                        "shaped_demand": round(shaped_demand, 2),
                        "uplift_percentage": round((promo["uplift"] - 1) * 100, 2),
                        "cost": round(promo["cost"], 2),
                        "roi": round(roi, 2),
                        "feasible": promo["uplift"] <= max_uplift and promo["cost"] <= max_budget
                    })
            
            # Select optimal scenarios
            feasible_scenarios = [s for s in scenarios if s["feasible"]]
            
            if feasible_scenarios:
                # Sort by ROI
                feasible_scenarios.sort(key=lambda x: x["roi"], reverse=True)
                
                # Select top scenarios within budget
                selected_scenarios = []
                total_cost = 0
                
                for scenario in feasible_scenarios:
                    if total_cost + scenario["cost"] <= max_budget:
                        selected_scenarios.append(scenario)
                        total_cost += scenario["cost"]
                
                optimization_results["optimal_scenarios"] = selected_scenarios
                optimization_results["total_cost"] = round(total_cost, 2)
                optimization_results["total_uplift"] = round(sum(s["shaped_demand"] - s["baseline"] for s in selected_scenarios), 2)
                optimization_results["average_roi"] = round(sum(s["roi"] for s in selected_scenarios) / len(selected_scenarios), 2) if selected_scenarios else 0
            else:
                optimization_results["optimal_scenarios"] = []
                optimization_results["message"] = "No feasible scenarios within constraints"
            
            optimization_results["all_scenarios"] = scenarios
            optimization_results["constraints"] = constraints
            optimization_results["optimized_at"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "status": "success",
                "optimization_results": optimization_results
            }
            
        except Exception as e:
            logger_dp.error(f"Error in demand shaping optimization: {e}")
            return {"error": str(e)}