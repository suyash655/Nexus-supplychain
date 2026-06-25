"""
NEXUS — Monte Carlo Probabilistic Scenario Engine
=====================================================
Replaces binary "up/down" shock simulations with N-trial stochastic analysis.
Outputs probability distributions that CFOs and risk committees use for
capital allocation decisions.
"""

import math
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone


class MonteCarloEngine:
    """Probabilistic supply chain disruption simulator."""

    DEFAULT_TRIALS = 1000

    # ── Emission factor baselines (EPA / DEFRA simplified) ──
    # Used to estimate carbon-adjusted cost per corridor
    TRANSPORT_EMISSION_KG_PER_KM = {
        "ocean": 0.016,
        "air": 0.602,
        "rail": 0.028,
        "road": 0.062,
        "default": 0.040,
    }

    def __init__(self):
        self._delay_distributions: Dict[str, Dict[str, float]] = {}
        self._cost_distributions: Dict[str, Dict[str, float]] = {}
        self._fitted = False

    # ──────────────────────────────────────────────
    # Phase 1: Fit distributions from historical data
    # ──────────────────────────────────────────────

    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Learn delay and cost distributions per supplier from historical data."""
        self._delay_distributions = {}
        self._cost_distributions = {}

        if "supplier" not in df.columns:
            return {"error": "No 'supplier' column found", "fitted": False}

        suppliers_fitted = 0

        for supplier, group in df.groupby("supplier"):
            supplier_name = str(supplier)

            # Delay distribution
            if "delay_days" in group.columns:
                delays = pd.to_numeric(group["delay_days"], errors="coerce").dropna()
                if len(delays) >= 3:
                    self._delay_distributions[supplier_name] = {
                        "mean": float(delays.mean()),
                        "std": max(float(delays.std()), 0.5),  # floor at 0.5 to avoid degenerate distributions
                        "min": float(delays.min()),
                        "max": float(delays.max()),
                        "skew": float(delays.skew()) if len(delays) >= 8 else 0.0,
                        "n_samples": len(delays),
                    }

            # Cost distribution
            if "cost" in group.columns:
                costs = pd.to_numeric(group["cost"], errors="coerce").dropna()
                if len(costs) >= 3:
                    self._cost_distributions[supplier_name] = {
                        "mean": float(costs.mean()),
                        "std": max(float(costs.std()), 1.0),
                        "min": float(costs.min()),
                        "max": float(costs.max()),
                        "n_samples": len(costs),
                    }

            suppliers_fitted += 1

        self._fitted = True
        return {
            "fitted": True,
            "suppliers_fitted": suppliers_fitted,
            "delay_distributions": len(self._delay_distributions),
            "cost_distributions": len(self._cost_distributions),
        }

    # ──────────────────────────────────────────────
    # Phase 2: Monte Carlo simulation
    # ──────────────────────────────────────────────

    def simulate_disruption(
        self,
        target_suppliers: List[str],
        disruption_severity: float = 0.5,
        num_trials: int = DEFAULT_TRIALS,
        affected_skus: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for disruption at one or more suppliers.

        Parameters:
            target_suppliers: List of supplier names to simulate failure for
            disruption_severity: 0.0 (minor) to 1.0 (total shutdown)
            num_trials: Number of Monte Carlo trials (default 1000)
            affected_skus: Optional SKU filter; if None, all SKUs affected

        Returns:
            Probability distributions for delay, cost impact, and stockout risk.
        """
        if not self._fitted:
            return {"error": "Engine not fitted. Call fit(df) first."}

        results: Dict[str, Any] = {
            "simulation_id": datetime.now(timezone.utc).isoformat(),
            "target_suppliers": target_suppliers,
            "disruption_severity": disruption_severity,
            "num_trials": num_trials,
            "supplier_results": [],
            "aggregate": {},
        }

        all_total_delays = np.zeros(num_trials)
        all_total_costs = np.zeros(num_trials)

        for supplier in target_suppliers:
            supplier_result = self._simulate_single_supplier(
                supplier, disruption_severity, num_trials
            )
            results["supplier_results"].append(supplier_result)

            if "delay_trials" in supplier_result:
                all_total_delays += np.array(supplier_result["delay_trials"])
            if "cost_trials" in supplier_result:
                all_total_costs += np.array(supplier_result["cost_trials"])

        # Aggregate across all suppliers
        results["aggregate"] = self._compute_statistics(
            all_total_delays, all_total_costs, num_trials
        )

        # Remove raw trial arrays from response (too large for JSON)
        for sr in results["supplier_results"]:
            sr.pop("delay_trials", None)
            sr.pop("cost_trials", None)

        return results

    def _simulate_single_supplier(
        self, supplier: str, severity: float, num_trials: int
    ) -> Dict[str, Any]:
        """Run simulation for a single supplier."""
        delay_dist = self._delay_distributions.get(supplier)
        cost_dist = self._cost_distributions.get(supplier)

        result: Dict[str, Any] = {
            "supplier": supplier,
            "has_historical_data": delay_dist is not None or cost_dist is not None,
        }

        if delay_dist:
            # Sample delays: use log-normal to model right-skewed delivery delays
            mean_delay = delay_dist["mean"]
            std_delay = delay_dist["std"]

            # Disruption multiplier increases both mean and variance
            disrupted_mean = mean_delay * (1.0 + severity * 3.0)
            disrupted_std = std_delay * (1.0 + severity * 2.0)

            # Use log-normal for realistic right-skewed delays
            if disrupted_mean > 0:
                sigma = math.sqrt(math.log(1 + (disrupted_std / disrupted_mean) ** 2))
                mu = math.log(disrupted_mean) - 0.5 * sigma**2
                delay_samples = np.random.lognormal(mu, sigma, num_trials)
            else:
                delay_samples = np.abs(np.random.normal(disrupted_mean, disrupted_std, num_trials))

            delay_samples = np.maximum(delay_samples, 0)  # No negative delays
            result["delay_trials"] = delay_samples.tolist()
            result["delay_stats"] = {
                "p10": round(float(np.percentile(delay_samples, 10)), 1),
                "p25": round(float(np.percentile(delay_samples, 25)), 1),
                "p50_median": round(float(np.percentile(delay_samples, 50)), 1),
                "p75": round(float(np.percentile(delay_samples, 75)), 1),
                "p90": round(float(np.percentile(delay_samples, 90)), 1),
                "p95": round(float(np.percentile(delay_samples, 95)), 1),
                "mean": round(float(np.mean(delay_samples)), 1),
                "std": round(float(np.std(delay_samples)), 1),
                "max_observed": round(float(np.max(delay_samples)), 1),
                "baseline_mean": round(mean_delay, 1),
            }

            # Stockout probability: delay > X days (configurable threshold)
            STOCKOUT_THRESHOLD_DAYS = 14
            stockout_count = int(np.sum(delay_samples > STOCKOUT_THRESHOLD_DAYS))
            result["stockout_probability"] = round(stockout_count / num_trials * 100, 1)
            result["stockout_threshold_days"] = STOCKOUT_THRESHOLD_DAYS
        else:
            # No historical data — use a generic disruption model
            generic_delays = np.random.exponential(scale=7 * severity + 1, size=num_trials)
            result["delay_trials"] = generic_delays.tolist()
            result["delay_stats"] = {
                "p50_median": round(float(np.percentile(generic_delays, 50)), 1),
                "p90": round(float(np.percentile(generic_delays, 90)), 1),
                "mean": round(float(np.mean(generic_delays)), 1),
                "note": "Based on generic model — no historical data for this supplier",
            }
            result["stockout_probability"] = round(
                float(np.sum(generic_delays > 14) / num_trials * 100), 1
            )

        if cost_dist:
            mean_cost = cost_dist["mean"]
            std_cost = cost_dist["std"]

            # Cost during disruption: higher mean + higher variance
            disrupted_cost_mean = mean_cost * (1.0 + severity * 0.8)
            disrupted_cost_std = std_cost * (1.0 + severity * 1.5)

            # Use log-normal, not Normal:
            # - Logistics costs are bounded below by zero
            # - Real disruption cost distributions are right-skewed (heavy upper tail)
            # - Normal would generate negative samples and understate tail risk
            # Consistent with the log-normal used for delay sampling above.
            if disrupted_cost_mean > 0 and disrupted_cost_std > 0:
                sigma_c = math.sqrt(
                    math.log(1 + (disrupted_cost_std / disrupted_cost_mean) ** 2)
                )
                mu_c = math.log(disrupted_cost_mean) - 0.5 * sigma_c ** 2
                cost_samples = np.random.lognormal(mu_c, sigma_c, num_trials)
            else:
                cost_samples = np.full(num_trials, max(disrupted_cost_mean, 0.0))

            result["cost_trials"] = cost_samples.tolist()
            result["cost_impact"] = {
                "p10": round(float(np.percentile(cost_samples, 10)), 2),
                "p50_median": round(float(np.percentile(cost_samples, 50)), 2),
                "p90": round(float(np.percentile(cost_samples, 90)), 2),
                "p95": round(float(np.percentile(cost_samples, 95)), 2),
                "mean": round(float(np.mean(cost_samples)), 2),
                "total_exposure_p90": round(float(np.percentile(cost_samples, 90) * 10), 2),
                "baseline_mean": round(mean_cost, 2),
                "cost_increase_pct": round(
                    ((disrupted_cost_mean - mean_cost) / max(mean_cost, 1)) * 100, 1
                ),
                "distribution": "log-normal",
            }

        # Risk tier classification
        stockout_prob = result.get("stockout_probability", 0)
        if stockout_prob > 60:
            result["risk_tier"] = "CRITICAL"
        elif stockout_prob > 30:
            result["risk_tier"] = "HIGH"
        elif stockout_prob > 10:
            result["risk_tier"] = "ELEVATED"
        else:
            result["risk_tier"] = "MANAGEABLE"

        return result

    def _compute_statistics(
        self, total_delays: np.ndarray, total_costs: np.ndarray, num_trials: int
    ) -> Dict[str, Any]:
        """Compute aggregate statistics across all suppliers."""
        agg: Dict[str, Any] = {}

        if np.any(total_delays > 0):
            agg["total_delay"] = {
                "p10": round(float(np.percentile(total_delays, 10)), 1),
                "p50_median": round(float(np.percentile(total_delays, 50)), 1),
                "p90": round(float(np.percentile(total_delays, 90)), 1),
                "mean": round(float(np.mean(total_delays)), 1),
                "confidence_interval_95": [
                    round(float(np.percentile(total_delays, 2.5)), 1),
                    round(float(np.percentile(total_delays, 97.5)), 1),
                ],
            }
            # Narrative for executive summary
            p50 = agg["total_delay"]["p50_median"]
            p90 = agg["total_delay"]["p90"]
            agg["narrative"] = (
                f"In 50% of simulations, total delay is ≤{p50} days. "
                f"In worst-case scenarios (P90), delay reaches {p90} days."
            )

        if np.any(total_costs > 0):
            agg["total_cost_exposure"] = {
                "p10": round(float(np.percentile(total_costs, 10)), 2),
                "p50_median": round(float(np.percentile(total_costs, 50)), 2),
                "p90": round(float(np.percentile(total_costs, 90)), 2),
                "mean": round(float(np.mean(total_costs)), 2),
                "confidence_interval_95": [
                    round(float(np.percentile(total_costs, 2.5)), 2),
                    round(float(np.percentile(total_costs, 97.5)), 2),
                ],
            }

        # Overall system risk score (0–100)
        stockout_proxy = float(np.sum(total_delays > 14) / num_trials * 100)
        agg["system_risk_score"] = round(min(100, stockout_proxy * 1.2), 1)

        return agg

    # ──────────────────────────────────────────────
    # Scenario comparison
    # ──────────────────────────────────────────────

    def compare_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        num_trials: int = DEFAULT_TRIALS,
    ) -> Dict[str, Any]:
        """
        Compare multiple what-if scenarios side by side.

        Each scenario dict has:
            - name: str
            - target_suppliers: List[str]
            - disruption_severity: float
        """
        comparison: Dict[str, Any] = {
            "scenarios": [],
            "recommendation": "",
        }

        best_scenario = None
        best_risk = float("inf")

        for scenario in scenarios:
            result = self.simulate_disruption(
                target_suppliers=scenario.get("target_suppliers", []),
                disruption_severity=scenario.get("disruption_severity", 0.5),
                num_trials=num_trials,
            )
            scenario_summary = {
                "name": scenario.get("name", "Unnamed"),
                "aggregate": result.get("aggregate", {}),
                "supplier_count": len(scenario.get("target_suppliers", [])),
            }
            comparison["scenarios"].append(scenario_summary)

            risk = result.get("aggregate", {}).get("system_risk_score", 100)
            if risk < best_risk:
                best_risk = risk
                best_scenario = scenario.get("name", "Unnamed")

        if best_scenario:
            comparison["recommendation"] = (
                f"Scenario '{best_scenario}' has the lowest system risk score ({best_risk}). "
                f"Recommend prioritizing mitigation for this configuration."
            )

        return comparison
