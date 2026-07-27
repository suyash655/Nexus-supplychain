"""
NEXUS — Decision Velocity KPI Framework
==========================================
Enterprise KPIs that measure HOW FAST and HOW ACCURATELY NEXUS enables decisions,
not just supply chain health states.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

import numpy as np  # type: ignore
import pandas as pd  # type: ignore


class KPIEngine:
    """Computes NEXUS platform performance KPIs for the BI layer."""

    def compute_all_kpis(
        self,
        df: pd.DataFrame,
        risk_scores: Optional[List[Dict]] = None,
        anomalies: Optional[Dict[str, Any]] = None,
        analysis_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Compute all six core Decision Velocity KPIs."""
        kpis: Dict[str, Any] = {
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {},
        }

        # 1. MTTD — Mean Time to Disruption Detection
        kpis["metrics"]["mttd"] = self._compute_mttd(df, anomalies)

        # 2. MTTR — Mean Time to Remediation Recommendation
        kpis["metrics"]["mttr"] = self._compute_mttr(analysis_history)

        # 3. RAR — Recommendation Acceptance Rate
        kpis["metrics"]["rar"] = self._compute_rar(analysis_history)

        # 4. FPR — False Positive Rate
        kpis["metrics"]["fpr"] = self._compute_fpr(risk_scores, df)

        # 5. FIP — Financial Impact Prevented
        kpis["metrics"]["fip"] = self._compute_fip(risk_scores, df)

        # 6. TCD — Tier Coverage Depth
        kpis["metrics"]["tcd"] = self._compute_tcd(df)

        # Overall platform health score
        kpis["platform_health_score"] = self._compute_health_score(kpis["metrics"])

        return kpis

    def _compute_mttd(self, df: pd.DataFrame, anomalies: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Mean Time to Disruption Detection.
        Measures seconds from potential disruption signal to in-platform alert.
        Currently estimated from data upload → anomaly detection pipeline time.
        """
        anomaly_count = 0
        if anomalies:
            anomaly_count = anomalies.get("anomaly_count", 0)

        from app.core.database import SessionLocal
        from app.models.supply import AgentTrace
        db = SessionLocal()
        try:
            traces = db.query(AgentTrace).limit(100).all()
            if traces:
                avg_ms = sum(t.duration_ms or 0 for t in traces) / len(traces)
                mttd_seconds = round(avg_ms / 1000, 1)
            else:
                mttd_seconds = None
        finally:
            db.close()

        return {
            "name": "Mean Time to Disruption Detection",
            "abbreviation": "MTTD",
            "value": mttd_seconds,
            "unit": "seconds",
            "status": "measured" if mttd_seconds else "needs_data",
            "note": "Computed from agent trace logs" if mttd_seconds else "No agent traces yet — trigger an analysis to populate",
            "anomalies_detected": anomaly_count,
            "category": "speed",
        }

    def _compute_mttr(self, analysis_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Mean Time to Remediation Recommendation.
        Time from disruption detection to actionable ranked recommendation list.
        """
        if analysis_history and len(analysis_history) > 0:
            durations = [
                h.get("duration_ms", 5000) for h in analysis_history
                if h.get("duration_ms") is not None
            ]
            avg_ms = float(np.mean(durations)) if durations else 5000.0
        else:
            avg_ms = 5000.0  # Default 5s

        return {
            "name": "Mean Time to Remediation Recommendation",
            "abbreviation": "MTTR",
            "value": round(avg_ms / 1000, 1),
            "unit": "seconds",
            "benchmark": "4-72 hours (traditional process)",
            "target": "< 30 seconds",
            "status": "on_target" if avg_ms < 30000 else "needs_improvement",
            "category": "speed",
        }

    def _compute_rar(self, analysis_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Recommendation Acceptance Rate.
        What % of agent-generated sourcing alternatives are accepted.
        """
        from app.core.database import SessionLocal
        from app.models.supply import PendingAction
        db = SessionLocal()
        try:
            total = db.query(PendingAction).filter(
                PendingAction.status.in_(["executed", "rejected"])
            ).count()
            accepted = db.query(PendingAction).filter(
                PendingAction.status == "executed"
            ).count()
        finally:
            db.close()

        rate = round(accepted / total * 100, 1) if total > 0 else 0.0

        return {
            "name": "Recommendation Acceptance Rate",
            "abbreviation": "RAR",
            "value": rate,
            "unit": "%",
            "total_recommendations": total,
            "accepted": accepted,
            "target": "> 60%",
            "status": "on_target" if rate >= 60 else "needs_data" if total == 0 else "needs_improvement",
            "category": "quality",
        }

    def _compute_fpr(self, risk_scores: Optional[List[Dict]] = None, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        False Positive Rate on Risk Scores.
        Estimated by comparing high-risk flagged suppliers against their actual performance.
        """
        if not risk_scores or df is None or len(df) == 0:
            return {
                "name": "False Positive Rate",
                "abbreviation": "FPR",
                "value": 0.0,
                "unit": "%",
                "status": "needs_data",
                "category": "quality",
            }

        high_risk_suppliers = [s for s in risk_scores if s.get("risk_score", 0) >= 70]
        false_positives = 0

        for supplier_data in high_risk_suppliers:
            supplier = supplier_data["supplier"]
            if "supplier" in df.columns and "delay_days" in df.columns:
                supplier_delays = pd.to_numeric(
                    df[df["supplier"] == supplier]["delay_days"], errors="coerce"
                ).dropna()
                if len(supplier_delays) > 0:
                    # If flagged as high-risk but actual avg delay < 2 days → false positive
                    if float(supplier_delays.mean()) < 2.0:
                        false_positives += 1

        total_flagged = len(high_risk_suppliers)
        fpr = round(false_positives / max(total_flagged, 1) * 100, 1)

        return {
            "name": "False Positive Rate",
            "abbreviation": "FPR",
            "value": fpr,
            "unit": "%",
            "total_flagged": total_flagged,
            "false_positives": false_positives,
            "target": "< 15%",
            "status": "on_target" if fpr < 15 else "needs_improvement",
            "category": "quality",
        }

    def _compute_fip(self, risk_scores: Optional[List[Dict]] = None, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Financial Impact Prevented (estimate).

        Uses the supplier's actual `total_cost` from transaction data as the
        base, rather than hardcoded dollar amounts. The estimate is:
            prevented ≈ total_cost × (risk_score / 100) × 0.15

        The 0.15 factor is a conservative assumption: an early warning avoids
        roughly 15% of total spend exposure (partial mitigation, not full prevention).
        This is labelled as an estimate and the methodology is included in the
        response so users understand the basis.

        Note: suppliers with `low_data_warning=True` (fewer than 10 shipments)
        have wide confidence intervals on their risk scores — their FIP
        contributions are labelled unreliable.
        """
        if not risk_scores or df is None:
            return {
                "name": "Financial Impact Prevented",
                "abbreviation": "FIP",
                "value": 0,
                "unit": "USD",
                "status": "needs_data",
                "category": "value",
            }

        PREVENTION_FACTOR = 0.15  # conservative early-warning mitigation assumption
        RISK_THRESHOLD    = 50

        total_prevented    = 0.0
        reliable_prevented = 0.0
        contributors: List[Dict] = []

        for supplier_data in risk_scores:
            risk = supplier_data.get("risk_score", 0)
            if risk < RISK_THRESHOLD:
                continue

            # Use actual transaction cost from the risk scorer's aggregation
            total_cost    = float(supplier_data.get("total_cost", 0))
            prevented     = total_cost * (risk / 100.0) * PREVENTION_FACTOR
            is_reliable   = not supplier_data.get("low_data_warning", False)

            total_prevented += prevented
            if is_reliable:
                reliable_prevented += prevented

            contributors.append({
                "supplier":  supplier_data["supplier"],
                "risk_score": risk,
                "total_cost": total_cost,
                "prevented_estimate": round(prevented, 2),
                "reliable": is_reliable,
            })

        return {
            "name":             "Financial Impact Prevented",
            "abbreviation":     "FIP",
            "value":            round(total_prevented, 2),
            "reliable_value":   round(reliable_prevented, 2),
            "formatted_value":  f"${total_prevented:,.0f}",
            "unit":             "USD",
            "high_risk_suppliers": len(contributors),
            "contributors":     sorted(contributors, key=lambda x: x["prevented_estimate"], reverse=True)[:10],
            "methodology": (
                f"total_cost × (risk_score/100) × {PREVENTION_FACTOR} "
                f"for suppliers with risk_score ≥ {RISK_THRESHOLD}. "
                "Based on actual transaction costs — not hardcoded estimates. "
                "`reliable_value` excludes suppliers with fewer than 10 shipments."
            ),
            "category": "value",
        }

    def _compute_tcd(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Tier Coverage Depth.
        What % of the supply chain has been mapped beyond Tier 1.
        """
        if df is None or len(df) == 0:
            return {
                "name": "Tier Coverage Depth",
                "abbreviation": "TCD",
                "value": 0,
                "unit": "%",
                "status": "needs_data",
                "category": "coverage",
            }

        # Tier 1: direct suppliers
        tier_1 = df["supplier"].nunique() if "supplier" in df.columns else 0
        # Tier 2: warehouses (intermediate nodes)
        tier_2 = df["warehouse"].nunique() if "warehouse" in df.columns else 0
        # Tier 3: regions (end distribution)
        tier_3 = df["region"].nunique() if "region" in df.columns else 0

        total_entities = tier_1 + tier_2 + tier_3
        # Coverage: all 3 tiers mapped = 100%
        tiers_covered = sum([1 for t in [tier_1, tier_2, tier_3] if t > 0])
        coverage_pct = round(tiers_covered / 3 * 100, 1)

        return {
            "name": "Tier Coverage Depth",
            "abbreviation": "TCD",
            "value": coverage_pct,
            "unit": "%",
            "tiers": {
                "tier_1_suppliers": tier_1,
                "tier_2_warehouses": tier_2,
                "tier_3_regions": tier_3,
            },
            "total_entities_mapped": total_entities,
            "target": "100% (all 3 tiers)",
            "status": "complete" if coverage_pct >= 100 else "partial",
            "category": "coverage",
        }

    def _compute_health_score(self, metrics: Dict[str, Dict]) -> Dict[str, Any]:
        """Composite platform health score from all KPIs."""
        scores: List[float] = []

        # MTTD contribution (lower is better)
        mttd = metrics.get("mttd", {}).get("value", 60)
        scores.append(max(0, 100 - mttd))  # 0s = 100, 100s = 0

        # MTTR contribution (lower is better)
        mttr = metrics.get("mttr", {}).get("value", 30)
        scores.append(max(0, 100 - mttr * 2))

        # RAR contribution (higher is better)
        rar = metrics.get("rar", {}).get("value", 50)
        scores.append(rar)

        # FPR contribution (lower is better)
        fpr = metrics.get("fpr", {}).get("value", 20)
        scores.append(max(0, 100 - fpr * 2))

        # TCD contribution (higher is better)
        tcd = metrics.get("tcd", {}).get("value", 50)
        scores.append(tcd)

        composite = round(float(np.mean(scores)), 1) if scores else 50.0

        return {
            "score": composite,
            "grade": (
                "A+" if composite >= 95 else
                "A" if composite >= 85 else
                "B" if composite >= 70 else
                "C" if composite >= 50 else
                "D" if composite >= 30 else "F"
            ),
            "interpretation": (
                "Excellent platform performance" if composite >= 85 else
                "Good — room for improvement in coverage and accuracy" if composite >= 70 else
                "Needs attention — several KPIs below target" if composite >= 50 else
                "Critical — platform underperforming on key metrics"
            ),
        }
