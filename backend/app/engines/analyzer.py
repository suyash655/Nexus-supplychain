import logging
import math as _math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.engines.forecaster import TimeSeriesForecaster, _safe
from app.utils.supply_metrics import completeness_score, on_time_mask

logger_ml = logging.getLogger("nexus.ml_engine")

class AnomalyDetector:
    def __init__(self, contamination: float = 0.1):
        """
        Parameters
        ----------
        contamination : float
            Expected fraction of anomalies in the dataset (0.01–0.5).
            Default 0.1 (10%) is a reasonable starting point but should be
            tuned per customer. A clean supplier with 2% true anomalies will
            generate 80% false positives at contamination=0.1.
            Configurable via the ANOMALY_CONTAMINATION env var.
        """
        import os
        self.contamination = float(os.getenv("ANOMALY_CONTAMINATION", str(contamination)))
        self.scaler = StandardScaler()

    def detect(self, df: pd.DataFrame, reference_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Run all anomaly detectors and return a deduplicated result.

        Parameters
        ----------
        df : pd.DataFrame
            The dataset to score for anomalies (the "current" window).
        reference_df : pd.DataFrame, optional
            A stable historical baseline (e.g. first 90 days of data).
            When provided, Isolation Forest is TRAINED on reference_df and
            SCORED on df. This prevents the model from normalising gradual
            degradation (W2 fix).
            When None, the model trains and scores on df (original behaviour).

        Deduplication: each detector appends to a shared index-keyed dict
        so a row flagged by multiple methods is counted once (H2 fix).
        """
        anomaly_map: Dict[int, Dict] = {}

        def _merge(items: List[Dict]):
            for item in items:
                idx = item["index"]
                if idx not in anomaly_map:
                    anomaly_map[idx] = item
                    anomaly_map[idx]["type"] = [item["type"]]
                else:
                    if item["type"] not in anomaly_map[idx]["type"]:
                        anomaly_map[idx]["type"].append(item["type"])
                    anomaly_map[idx]["risk_score"] = max(
                        anomaly_map[idx]["risk_score"], item.get("risk_score", 0)
                    )
                    sev_order = {"medium": 0, "high": 1, "critical": 2}
                    if sev_order.get(item.get("severity", "medium"), 0) > sev_order.get(
                        anomaly_map[idx].get("severity", "medium"), 0
                    ):
                        anomaly_map[idx]["severity"] = item["severity"]

        methods_used = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) >= 2:
            _merge(self._isolation_forest(df, numeric_cols, train_df=reference_df))
            methods_used.append(
                "isolation_forest_with_baseline" if reference_df is not None
                else "isolation_forest"
            )
        if "delay_days" in df.columns:
            _merge(self._zscore_anomalies(df, "delay_days", "delay_spike", reference_df))
            methods_used.append("z_score_delay")
        if "cost" in df.columns:
            _merge(self._zscore_anomalies(df, "cost", "cost_surge", reference_df))
            methods_used.append("z_score_cost")
        if "quality_score" in df.columns and df["quality_score"].notna().sum() > 10:
            _merge(self._iqr_anomalies(df, "quality_score", "quality_drop"))
            methods_used.append("iqr_quality")

        anomalies = []
        for item in anomaly_map.values():
            types = item.get("type", [])
            item["type"] = types[0] if len(types) == 1 else types
            anomalies.append(item)

        return {
            "anomalies":     anomalies,
            "total_records": len(df),
            "anomaly_count": len(anomalies),
            "methods_used":  methods_used,
            "baseline_used": reference_df is not None,
        }

    def _isolation_forest(
        self,
        df: pd.DataFrame,
        cols: List[str],
        train_df: Optional[pd.DataFrame] = None,
    ) -> List[Dict]:
        """
        Train on `train_df` (or `df` if no baseline) and score `df`.
        Using a stable reference window prevents gradual degradation from
        being absorbed into the model's definition of "normal".
        """
        anomalies = []
        X_score = df[cols].fillna(0).values
        if len(X_score) < 10:
            return anomalies

        if train_df is not None and len(train_df) >= 10:
            # Train on stable baseline, score on current data
            X_train = train_df[cols].fillna(0).values
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_score_scaled = self.scaler.transform(X_score)
        else:
            X_train_scaled = self.scaler.fit_transform(X_score)
            X_score_scaled = X_train_scaled

        model = IsolationForest(
            contamination=self.contamination, random_state=42, n_estimators=100
        )
        model.fit(X_train_scaled)
        labels = model.predict(X_score_scaled)
        scores = model.decision_function(X_score_scaled)

        for i, (label, score) in enumerate(zip(labels, scores)):
            if label == -1:
                row = df.iloc[i]
                anomalies.append({
                    "index":      int(i),
                    "type":       "multivariate_anomaly",
                    "severity":   "high" if score < -0.3 else "medium",
                    "risk_score": round(min(100.0, max(0.0, _safe((1.0 - (score + 0.5)) * 100.0))), 1),
                    "supplier":   str(row.get("supplier", "Unknown")),
                    "sku":        str(row.get("sku", "Unknown")),
                    "details":    {col: _safe(row.get(col, 0)) for col in cols},
                })
        return anomalies

    def _zscore_anomalies(
        self,
        df: pd.DataFrame,
        col: str,
        event_type: str,
        reference_df: Optional[pd.DataFrame] = None,
    ) -> List[Dict]:
        """
        Z-score against reference_df statistics when available.
        This catches values that are normal relative to current degraded data
        but are outliers relative to the historical baseline.
        """
        anomalies = []
        values = pd.to_numeric(df[col], errors="coerce").fillna(0)

        if reference_df is not None and col in reference_df.columns:
            ref_vals = pd.to_numeric(reference_df[col], errors="coerce").fillna(0)
            ref_mean = float(ref_vals.mean())
            ref_std  = float(ref_vals.std())
        else:
            ref_mean = float(values.mean())
            ref_std  = float(values.std())

        if ref_std == 0:
            return anomalies

        z_scores = np.abs((values.values - ref_mean) / ref_std)
        threshold = 2.5

        for i, z in enumerate(z_scores):
            if z > threshold:
                row = df.iloc[i]
                anomalies.append({
                    "index":    int(i),
                    "type":     event_type,
                    "severity": "critical" if z > 4 else "high" if z > 3 else "medium",
                    "risk_score": round(min(100.0, float(z) * 20.0), 1),
                    "supplier": str(row.get("supplier", "Unknown")),
                    "sku":      str(row.get("sku", "Unknown")),
                    "value":    float(values.iloc[i]),
                    "z_score":  round(float(z), 2),
                    "baseline": "reference_period" if reference_df is not None else "dataset",
                })
        return anomalies

    def _iqr_anomalies(self, df: pd.DataFrame, col: str, event_type: str) -> List[Dict]:
        anomalies = []
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        for i, val in values.items():
            if val < lower or val > upper:
                row = df.iloc[i] if i < len(df) else {}
                anomalies.append({
                    "index": int(i),
                    "type": event_type,
                    "severity": "high" if val < (Q1 - 3 * IQR) or val > (Q3 + 3 * IQR) else "medium",
                    "risk_score": round(min(100.0, abs(val - values.median()) / max(float(IQR), 0.01) * 25.0), 1),
                    "supplier": str(row.get("supplier", "Unknown")) if hasattr(row, "get") else "Unknown",
                    "value": float(val),
                })
        return anomalies

class RiskScorer:
    """
    Composite supplier risk scorer using six weighted factors.

    Weight rationale (documented here for auditability):
      delay_frequency (0.30) — most directly predicts service impact
      delay_severity  (0.20) — how bad delays are when they occur
      cost_variance   (0.15) — financial predictability
      quality_factor  (0.15) — quality failures have downstream recall risk
      consistency     (0.10) — variance in on-time delivery
      (volume_reliability removed — see note below)

    NOTE on volume_reliability (W4 fix):
      The old formula `max(0, 50 - len(group))` penalised small suppliers
      just for having fewer shipments. A new supplier with 5 shipments and
      zero delays is not riskier — we just have less data about them.
      Volume is now used ONLY to compute a confidence interval on the score,
      not to inflate the score itself. See `score_confidence_interval`.

    NOTE on confidence intervals (W3 fix):
      Scores from suppliers with <10 shipments have high variance and are
      labelled `low_confidence`. The `score_confidence_interval` field gives
      a ±margin based on a normal approximation of the score's uncertainty,
      scaled to sample size. Use this to avoid over-acting on thin data.
    """

    WEIGHTS = {
        "delay_frequency": 0.35,
        "delay_severity":  0.25,
        "cost_variance":   0.20,
        "quality_factor":  0.20,
    }

    # Minimum shipments for a reliable score
    _MIN_RELIABLE_N = 10

    def score_suppliers(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "supplier" not in df.columns:
            return []
        results = []
        grouped = df.groupby("supplier")
        global_max_delay = float(df["delay_days"].max()) if "delay_days" in df.columns else 1.0
        global_max_delay = max(global_max_delay, 1.0)

        for supplier, group in grouped:
            n = len(group)
            factors: Dict[str, float] = {}

            if "delay_days" in group.columns:
                delays = pd.to_numeric(group["delay_days"], errors="coerce").fillna(0)
                factors["delay_frequency"] = _safe(min(100.0, float((~on_time_mask(delays)).mean() * 100)), 0.0)
                factors["delay_severity"]  = _safe(min(100.0, float(delays.mean() / global_max_delay * 100)), 0.0)
                # consistency used for display only, not in weighted score
                delay_mean = float(delays.mean())
                delay_std = float(delays.std()) if len(delays) > 1 else 0.0
                consistency_cv = _safe(delay_std / max(delay_mean, 0.01), 0.0)
            else:
                factors["delay_frequency"] = 0.0
                factors["delay_severity"]  = 0.0
                consistency_cv = 0.0

            if "cost" in group.columns:
                costs = pd.to_numeric(group["cost"], errors="coerce").fillna(0)
                cost_mean = float(costs.mean())
                cost_std = float(costs.std()) if len(costs) > 1 else 0.0
                cost_cv = _safe(cost_std / max(cost_mean, 0.01), 0.0)
                factors["cost_variance"] = _safe(min(100.0, cost_cv * 40), 0.0)
            else:
                factors["cost_variance"] = 0.0

            quality_data_available = False
            if "quality_score" in group.columns and group["quality_score"].notna().sum() > 0:
                avg_quality = float(group["quality_score"].mean())
                if 0.0 <= avg_quality <= 1.0:
                    avg_quality *= 100.0
                factors["quality_factor"] = _safe(max(0.0, min(100.0, 100.0 - avg_quality)), 30.0)
                quality_data_available = True
            else:
                factors["quality_factor"] = 30.0  # neutral default when missing

            # ── Weighted risk score ──
            risk_score = sum(factors[k] * w for k, w in self.WEIGHTS.items())
            risk_score = round(min(100.0, max(0.0, float(risk_score))), 1)

            # ── Confidence interval based on sample size (W3) ──
            # Uses a ±margin that shrinks as n grows. At n=5 the margin is ±20pts;
            # at n=50 it's ±6pts; at n=500 it's ±2pts. This is a heuristic
            # approximation — not a true statistical interval.
            score_margin = round(min(20.0, 100.0 / _math.sqrt(max(n, 1))), 1)
            confidence_label = (
                "low"    if n < self._MIN_RELIABLE_N
                else "medium" if n < 50
                else "high"
            )

            tier = (
                "critical" if risk_score >= 70
                else "elevated" if risk_score >= 40
                else "stable"
            )

            delays_col = pd.to_numeric(
                group.get("delay_days", pd.Series([0])), errors="coerce"
            ).fillna(0)
            costs_col = pd.to_numeric(
                group.get("cost", pd.Series([0])), errors="coerce"
            ).fillna(0)

            results.append({
                "supplier": str(supplier),
                "risk_score": risk_score,
                "tier": tier,
                "total_shipments": n,
                "avg_delay": round(float(delays_col.mean()), 1),
                "max_delay": int(delays_col.max()),
                "total_cost": round(float(costs_col.sum()), 2),
                "reliability_score": round(100.0 - risk_score, 1),
                # Confidence fields (W3)
                "score_confidence": confidence_label,
                "score_margin": score_margin,
                "score_range": [
                    round(max(0.0, risk_score - score_margin), 1),
                    round(min(100.0, risk_score + score_margin), 1),
                ],
                "low_data_warning": n < self._MIN_RELIABLE_N,
                "quality_data_available": quality_data_available,
                # Factor breakdown
                "factors": {
                    **factors,
                    "consistency_cv": round(consistency_cv, 3),
                },
            })

        results.sort(key=lambda x: x["risk_score"], reverse=True)
        return results

class SupplyChainAnalyzer:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.risk_scorer = RiskScorer()
        self.forecaster = TimeSeriesForecaster()

    # ── Reference period: first 30% of data (chronological) ──
    # Used as a stable baseline so gradual degradation doesn't
    # get normalised into the model's definition of "normal".
    _REFERENCE_FRACTION = 0.30
    _MIN_REFERENCE_ROWS = 20

    def _build_reference_df(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Return the earliest `_REFERENCE_FRACTION` of rows as a reference baseline,
        sorted by order_date if available, otherwise by row order.
        Returns None if there is insufficient data.
        """
        if len(df) < self._MIN_REFERENCE_ROWS:
            return None

        date_col = next(
            (c for c in ["order_date", "delivery_date", "date"] if c in df.columns),
            None,
        )
        if date_col:
            sorted_df = df.copy()
            sorted_df["_sort_date"] = pd.to_datetime(sorted_df[date_col], errors="coerce")
            sorted_df = sorted_df.dropna(subset=["_sort_date"]).sort_values("_sort_date")
        else:
            sorted_df = df

        n_ref = max(self._MIN_REFERENCE_ROWS, int(len(sorted_df) * self._REFERENCE_FRACTION))
        ref = sorted_df.iloc[:n_ref].copy()
        if "_sort_date" in ref.columns:
            ref = ref.drop(columns=["_sort_date"])
        return ref

    def full_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        result: Dict[str, Any] = {"generated_at": datetime.now(timezone.utc).isoformat()}

        reference_df = self._build_reference_df(df)

        for key, fn in [
            ("summary",          lambda: self._compute_summary(df)),
            ("risk_scores",      lambda: self.risk_scorer.score_suppliers(df)),
            ("anomalies",        lambda: self.anomaly_detector.detect(df, reference_df)),
            ("time_series",      lambda: self.forecaster.analyze_trends(df)),
            ("bullwhip_analysis",lambda: self._detect_bullwhip(df)),
            ("data_quality",     lambda: self._assess_quality(df)),
        ]:
            try:
                result[key] = fn()
            except Exception:
                logger_ml.exception("[ML Engine] %s step failed", key)
                result[key] = {"error": f"{key} analysis unavailable — check server logs"}

        result["reference_period_rows"] = len(reference_df) if reference_df is not None else 0
        return result

    def _compute_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        summary: Dict[str, Any] = {
            "total_records": len(df),
            "unique_suppliers": df["supplier"].nunique() if "supplier" in df.columns else 0,
            "unique_skus": df["sku"].nunique() if "sku" in df.columns else 0,
            "unique_regions": df["region"].nunique() if "region" in df.columns else 0,
            "unique_warehouses": df["warehouse"].nunique() if "warehouse" in df.columns else 0,
        }
        if "delay_days" in df.columns:
            delays = pd.to_numeric(df["delay_days"], errors="coerce").fillna(0)
            summary["avg_delay_days"] = round(float(delays.mean()), 1)
            summary["max_delay_days"] = int(delays.max())
            summary["median_delay"] = round(float(delays.median()), 1)
            summary["delayed_shipments_pct"] = round(float((delays > 0).mean() * 100.0), 1)
        if "cost" in df.columns:
            costs = pd.to_numeric(df["cost"], errors="coerce").fillna(0)
            summary["total_cost"] = round(float(costs.sum()), 2)
            summary["avg_cost"] = round(float(costs.mean()), 2)
        if "quality_score" in df.columns and df["quality_score"].notna().sum() > 0:
            summary["avg_quality"] = round(float(df["quality_score"].mean()), 1)
        return summary

    def _detect_bullwhip(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute a Shipment Volatility Index from weekly shipment counts.

        IMPORTANT — metric naming:
        The academic Bullwhip Effect ratio is defined as Var(Orders)/Var(Demand)
        and requires two-tier order/demand data (Lee et al., 1997).
        We have only one tier of shipment counts, so we compute the
        Coefficient of Variation (CV) of weekly shipments instead.
        This measures how erratically shipments arrive week-to-week —
        a useful signal, but NOT the same as the Bullwhip ratio.
        The field is labelled "shipment_volatility_index" to be precise.
        """
        if "cost" not in df.columns or len(df) < 10:
            return {"shipment_volatility_index": 1.0, "status": "insufficient_data"}

        date_col = next((c for c in ["order_date", "date"] if c in df.columns), None)
        if not date_col:
            chunk_size = max(1, len(df) // 5)
            shipments = [len(df.iloc[i:i + chunk_size]) for i in range(0, len(df), chunk_size)]
        else:
            try:
                df_copy = df.copy()
                df_copy["_dt"] = pd.to_datetime(df_copy[date_col], errors="coerce")
                shipments = (
                    df_copy.dropna(subset=["_dt"])
                    .resample("W", on="_dt")
                    .size()
                    .tolist()
                )
            except Exception:
                shipments = []

        if len(shipments) < 4:
            return {"shipment_volatility_index": 1.0, "status": "insufficient_time_series"}

        mean_shipments = float(np.mean(shipments))
        std_shipments = float(np.std(shipments))
        cv = (std_shipments / mean_shipments) if mean_shipments > 0 else 0.0

        # SVI > 0.5 = high week-to-week shipment volatility
        # SVI close to 0 = very consistent shipment cadence
        svi = round(float(cv), 3)

        return {
            "shipment_volatility_index": svi,
            "coefficient_of_variation": svi,
            "weekly_shipment_counts": shipments,
            "mean_weekly_shipments": round(mean_shipments, 1),
            "std_weekly_shipments": round(std_shipments, 1),
            "status": (
                "high" if svi > 0.5
                else "elevated" if svi > 0.3
                else "stable"
            ),
            "interpretation": (
                "High week-to-week shipment volatility detected — "
                "orders arrive very unevenly."
                if svi > 0.5
                else "Shipment cadence is relatively consistent."
            ),
            "methodology": (
                "Coefficient of Variation (std/mean) of weekly shipment counts. "
                "NOT the academic Bullwhip Effect ratio (Var(Orders)/Var(Demand)), "
                "which requires two-tier order and demand data."
            ),
        }

    def _assess_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = int(df.isnull().sum().sum())
        column_quality = {}
        for col in df.columns:
            missing = int(df[col].isnull().sum())
            column_quality[col] = {
                "missing_count": missing,
                "missing_pct": round(float(missing / len(df) * 100.0), 1) if len(df) > 0 else 0.0,
                "dtype": str(df[col].dtype),
                "unique_values": int(df[col].nunique()),
            }
        return {
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "completeness_pct": round(float(completeness_score(df) * 100.0), 1),
            "columns": column_quality,
            "row_count": len(df),
            "column_count": len(df.columns),
        }
