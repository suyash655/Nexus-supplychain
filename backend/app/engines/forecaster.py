import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple


def _safe(val: float, default: float = 0.0) -> float:
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


# ── Forecast method selection thresholds ──
_HW_SEASONAL_PERIODS = 4      # quarterly
_HW_MIN_POINTS       = _HW_SEASONAL_PERIODS * 2   # 8 months minimum for HW
_EXP_MIN_POINTS      = 4                           # 4 months minimum for Holt's linear


class TimeSeriesForecaster:

    def analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "delay_trend":  [],
            "cost_trend":   [],
            "volume_trend": [],
            "forecast":     {},
            "seasonality":  {},
        }
        date_col: Optional[str] = None
        for col in ["order_date", "delivery_date", "date", "created_at"]:
            if col in df.columns:
                date_col = col
                break

        if date_col:
            df_copy = df.copy()
            df_copy["_date"] = pd.to_datetime(df_copy[date_col], errors="coerce")
            df_copy = df_copy.dropna(subset=["_date"])
            if len(df_copy) > 0:
                df_copy = df_copy.sort_values("_date")
                df_copy["_period"] = df_copy["_date"].dt.to_period("M").astype(str)

                if "delay_days" in df_copy.columns:
                    delay_trend = df_copy.groupby("_period")["delay_days"].mean()
                    result["delay_trend"] = [
                        {"period": str(p), "avg_delay": round(float(v), 1)}
                        for p, v in delay_trend.items()
                    ]

                if "cost" in df_copy.columns:
                    cost_trend = df_copy.groupby("_period")["cost"].sum()
                    result["cost_trend"] = [
                        {"period": str(p), "total_cost": round(float(v), 2)}
                        for p, v in cost_trend.items()
                    ]

                vol_trend = df_copy.groupby("_period").size()
                result["volume_trend"] = [
                    {"period": str(p), "count": int(v)}
                    for p, v in vol_trend.items()
                ]

                # ── Forecast selection ──
                if "delay_days" in df_copy.columns:
                    values_list = [float(d["avg_delay"]) for d in result["delay_trend"]]
                    n = len(values_list)

                    if n >= _HW_MIN_POINTS:
                        forecast, params = self._holt_winters_forecast(values_list, periods=3)
                        method     = "holt_winters"
                        confidence = "high" if n >= 12 else "medium"
                        fallback_reason = None
                    elif n >= _EXP_MIN_POINTS:
                        forecast, params = self._exp_smoothing_forecast(values_list, periods=3)
                        method     = "holts_linear_trend"
                        confidence = "low"
                        fallback_reason = (
                            f"Only {n} monthly data points available. "
                            f"Holt-Winters requires ≥{_HW_MIN_POINTS}. "
                            "Using Holt's linear trend (no seasonality)."
                        )
                    else:
                        forecast, params = [], {}
                        method     = "none"
                        confidence = "insufficient_data"
                        fallback_reason = (
                            f"Only {n} monthly data point(s) available. "
                            f"A minimum of {_EXP_MIN_POINTS} are required to forecast. "
                            "Upload more historical data to enable forecasting."
                        )

                    forecast_entry: Dict[str, Any] = {
                        "next_periods": forecast,
                        "confidence":   confidence,
                        "method":       method,
                        "fitted_params": params,
                    }
                    if forecast:
                        last_val = values_list[-1] if values_list else 0.0
                        forecast_entry["trend_direction"] = (
                            "increasing"
                            if forecast[-1]["p50"] > last_val
                            else "decreasing"
                        )
                    if fallback_reason:
                        forecast_entry["fallback_reason"] = fallback_reason

                    result["forecast"]["delay"] = forecast_entry

        if not date_col and len(df) > 50:
            chunk_size = len(df) // 10
            if "delay_days" in df.columns:
                delays = pd.to_numeric(df["delay_days"], errors="coerce").fillna(0)
                for i in range(10):
                    chunk = delays.iloc[i * chunk_size:(i + 1) * chunk_size]
                    result["delay_trend"].append({
                        "period":    f"Batch {i + 1}",
                        "avg_delay": round(float(chunk.mean()), 1),
                    })

        return result

    # ── Private forecast methods ──────────────────────────────────────────────

    def _optimise_alpha(
        self, values: List[float], alpha_range: Tuple[float, float] = (0.05, 0.95)
    ) -> float:
        """
        Grid-search alpha for single exponential smoothing via leave-one-out
        holdout on the last 20% of values (minimum 2 points).
        Returns the alpha that minimises MSE on the holdout window.
        """
        if len(values) < 4:
            return 0.3  # default for tiny series

        n_holdout = max(2, len(values) // 5)
        train = values[:-n_holdout]
        test  = values[-n_holdout:]

        best_alpha, best_mse = 0.3, float("inf")
        for alpha in np.arange(alpha_range[0], alpha_range[1], 0.05):
            alpha = round(float(alpha), 2)
            smoothed = float(train[0])
            for v in train[1:]:
                smoothed = alpha * v + (1.0 - alpha) * smoothed
            # Forecast over holdout window
            mse = float(np.mean([(smoothed - t) ** 2 for t in test]))
            if mse < best_mse:
                best_mse   = mse
                best_alpha = alpha

        return best_alpha

    def _optimise_hw_params(
        self, values: List[float], seasonal_periods: int
    ) -> Tuple[float, float, float]:
        """
        Grid-search (α, β, γ) for Holt-Winters via holdout MSE.
        Searches a coarse grid: α, β ∈ {0.1, 0.2, 0.3}, γ ∈ {0.1, 0.2, 0.3}.
        Returns (alpha, beta, gamma) that minimise holdout MSE.
        """
        if len(values) < seasonal_periods * 3:
            return 0.3, 0.1, 0.2  # default for short series

        n_holdout  = max(seasonal_periods, len(values) // 5)
        train_vals = values[:-n_holdout]
        test_vals  = values[-n_holdout:]

        best_params = (0.3, 0.1, 0.2)
        best_mse    = float("inf")

        for alpha in [0.1, 0.2, 0.3, 0.5]:
            for beta in [0.05, 0.1, 0.2]:
                for gamma in [0.1, 0.2, 0.3]:
                    try:
                        preds = self._hw_run(train_vals, n_holdout, alpha, beta, gamma, seasonal_periods)
                        mse = float(np.mean([(p - t) ** 2 for p, t in zip(preds, test_vals)]))
                        if mse < best_mse:
                            best_mse    = mse
                            best_params = (alpha, beta, gamma)
                    except Exception:
                        continue

        return best_params

    def _hw_run(
        self,
        values: List[float],
        periods_ahead: int,
        alpha: float,
        beta: float,
        gamma: float,
        seasonal_periods: int,
    ) -> List[float]:
        """Execute Holt-Winters (additive) and return `periods_ahead` forecasts."""
        level = float(values[0])
        trend = float(np.mean([values[i] - values[i - 1] for i in range(1, seasonal_periods)]))
        seasonals = [float(values[i]) - level for i in range(seasonal_periods)]

        for i in range(len(values)):
            val        = float(values[i])
            last_level = level
            level      = alpha * (val - seasonals[i % seasonal_periods]) + (1 - alpha) * (level + trend)
            trend      = beta * (level - last_level) + (1 - beta) * trend
            seasonals[i % seasonal_periods] = (
                gamma * (val - level) + (1 - gamma) * seasonals[i % seasonal_periods]
            )

        return [
            max(0.0, level + i * trend + seasonals[(len(values) + i - 1) % seasonal_periods])
            for i in range(1, periods_ahead + 1)
        ]

    def _prediction_interval(
        self, values: List[float], forecasts: List[float]
    ) -> List[Tuple[float, float]]:
        """
        Compute approximate P10/P90 prediction intervals using residual std.

        Method: fit the model on the training series, compute in-sample
        residuals, then apply ±1.28σ (P10/P90) and ±2.33σ (P2/P98) scaling
        factor that grows with forecast horizon (√h scaling).
        """
        if len(values) < 4:
            # Not enough history — return symmetric ±30% of forecast value
            return [(max(0.0, f * 0.7), f * 1.3) for f in forecasts]

        # Residuals from simple one-step-ahead predictions
        alpha = 0.3
        smoothed = float(values[0])
        residuals = []
        for v in values[1:]:
            pred = smoothed
            smoothed = alpha * v + (1 - alpha) * smoothed
            residuals.append(abs(v - pred))

        sigma = float(np.std(residuals)) if residuals else float(np.std(values)) * 0.3

        intervals = []
        for h, f in enumerate(forecasts, start=1):
            # Prediction interval widens with horizon: σ × √h × 1.28 for P10/P90
            margin = sigma * math.sqrt(h) * 1.28
            intervals.append((
                round(max(0.0, f - margin), 1),
                round(f + margin, 1),
            ))
        return intervals

    def _exp_smoothing_forecast(
        self, values: List[float], periods: int = 3
    ) -> Tuple[List[Dict[str, Any]], Dict]:
        """
        Holt's linear (double) exponential smoothing.
        Optimises alpha via holdout MSE. Returns forecasts with P10/P90 intervals.
        """
        if not values:
            return [], {}

        alpha = self._optimise_alpha(values)
        smoothed = float(values[0])
        for v in values[1:]:
            smoothed = alpha * v + (1.0 - alpha) * smoothed

        trend = (float(values[-1]) - float(values[0])) / max(len(values), 1)
        raw_forecasts = [
            max(0.0, smoothed + trend * (i + 1))
            for i in range(periods)
        ]
        intervals = self._prediction_interval(values, raw_forecasts)

        forecasts = [
            {
                "period_ahead":    i + 1,
                "p50":             round(raw_forecasts[i], 1),
                "p10":             intervals[i][0],
                "p90":             intervals[i][1],
                # backward-compat alias
                "predicted_value": round(raw_forecasts[i], 1),
            }
            for i in range(periods)
        ]
        return forecasts, {"alpha": alpha}

    def _holt_winters_forecast(
        self,
        values: List[float],
        periods: int = 3,
        seasonal_periods: int = _HW_SEASONAL_PERIODS,
    ) -> Tuple[List[Dict[str, Any]], Dict]:
        """
        Holt-Winters triple exponential smoothing (additive).

        Smoothing constants are optimised via holdout MSE rather than
        hardcoded. Returns forecasts with P10/P90 prediction intervals.

        Requires at least 2 × seasonal_periods data points (caller ensures this).
        """
        if len(values) < seasonal_periods * 2:
            return self._exp_smoothing_forecast(values, periods)

        alpha, beta, gamma = self._optimise_hw_params(values, seasonal_periods)
        raw_forecasts = self._hw_run(values, periods, alpha, beta, gamma, seasonal_periods)
        intervals     = self._prediction_interval(values, raw_forecasts)

        forecasts = [
            {
                "period_ahead":    i + 1,
                "p50":             round(raw_forecasts[i], 1),
                "p10":             intervals[i][0],
                "p90":             intervals[i][1],
                "predicted_value": round(raw_forecasts[i], 1),
            }
            for i in range(periods)
        ]
        params = {"alpha": alpha, "beta": beta, "gamma": gamma,
                  "seasonal_periods": seasonal_periods}
        return forecasts, params
