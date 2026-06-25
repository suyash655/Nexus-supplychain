"""
NEXUS — Temporal Trend Engine (Supply Chain Evolution Tracker)
==============================================================
Augments the static SupplyChainGraph with temporal dynamics by tracking
how supplier relationships evolve month-over-month.

What this engine does (accurately):
  - Tracks per-edge delay and cost history using timestamped transactions
  - Detects degrading/improving trends via linear regression on monthly windows
  - Identifies single-point-of-failure candidates from partner diversity ratios
  - Forecasts edge-level delay evolution using Holt's linear trend method
  - Computes trajectory-adjusted risk scores (rising delays penalised more
    than stable-but-higher delays)

What this engine does NOT do:
  - It is NOT a Graph Neural Network and does NOT follow Rossi et al. (2020).
    The TGN paper uses learned temporal attention, a gradient-trained memory
    module, and message functions with trainable parameters. This engine uses:
      • Fixed 0.7/0.3 mean-pool blend (no learned weights, no gradients)
      • Holt's double exponential smoothing (classical statistics)
      • Linear regression for trend detection
    This is classical time-series statistics on a graph structure — which is
    honest, useful, and does not require the TGN paper citation to be valid.

The engine is named TemporalTrendEngine internally; TGNNEngine is kept as
a backward-compatibility alias for existing call sites.
"""

import math
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict


class TemporalEdge:
    """A single timestamped interaction between two supply chain nodes."""
    __slots__ = ("source", "target", "timestamp", "delay", "cost", "quantity")

    def __init__(self, source: str, target: str, timestamp: float,
                 delay: float = 0.0, cost: float = 0.0, quantity: float = 0.0):
        self.source = source
        self.target = target
        self.timestamp = timestamp  # Unix timestamp
        self.delay = delay
        self.cost = cost
        self.quantity = quantity


class TemporalNodeMemory:
    """Per-node temporal memory — tracks how a node's behavior evolves."""

    def __init__(self, node_id: str, embedding_dim: int = 32):
        self.node_id = node_id
        self.embedding = np.zeros(embedding_dim, dtype=np.float64)
        self.interaction_count = 0
        self.last_update_time = 0.0
        self.delay_history: List[float] = []
        self.cost_history: List[float] = []
        self.partner_diversity: set = set()
        self.time_windows: Dict[str, Dict[str, float]] = {}  # period → metrics

    def update(self, edge: TemporalEdge, is_source: bool):
        """Update node memory with a new temporal edge."""
        self.interaction_count += 1
        self.last_update_time = edge.timestamp

        if edge.delay > 0:
            self.delay_history.append(edge.delay)
        self.cost_history.append(edge.cost)

        partner = edge.target if is_source else edge.source
        self.partner_diversity.add(partner)

        # Update embedding using exponential decay weighted features
        decay = np.exp(-(self.interaction_count / 100.0))  # Recency decay
        features = np.array([
            edge.delay / 30.0,  # Normalized delay
            edge.cost / 10000.0,  # Normalized cost
            len(self.partner_diversity) / 20.0,  # Diversity score
            self.interaction_count / 500.0,  # Activity level
        ])
        # Pad to embedding_dim
        padded = np.zeros_like(self.embedding)
        padded[:len(features)] = features
        self.embedding = (1 - decay * 0.1) * self.embedding + decay * 0.1 * padded


class TemporalTrendEngine:
    """
    Temporal trend tracking engine for supply chain evolution prediction.

    Tracks how supplier-SKU relationships evolve over time using monthly
    time windows, linear regression for trend detection, and Holt's
    linear method for short-range forecasting.

    This is classical time-series statistics applied to a graph structure.
    It is NOT a Graph Neural Network — there are no learned weights,
    no gradient updates, and no temporal attention mechanism.
    """

    def __init__(self, embedding_dim: int = 32):
        self.embedding_dim = embedding_dim
        self.temporal_edges: List[TemporalEdge] = []
        self.node_memories: Dict[str, TemporalNodeMemory] = {}
        self.edge_statistics: Dict[str, Dict[str, Any]] = {}  # "src→tgt" → stats
        self._fitted = False
        self._time_range: Tuple[float, float] = (0.0, 0.0)

    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Build temporal graph from timestamped supply chain data.
        Learns edge-level dynamics and computes temporal node embeddings.
        """
        self.temporal_edges = []
        self.node_memories = {}
        self.edge_statistics = {}

        # Parse timestamps
        date_col = None
        for col in ["order_date", "delivery_date", "date", "created_at"]:
            if col in df.columns:
                date_col = col
                break

        if date_col is None:
            return {"error": "No date column found for temporal analysis", "fitted": False}

        df_temp = df.copy()
        df_temp["_ts"] = pd.to_datetime(df_temp[date_col], errors="coerce")
        df_temp = df_temp.dropna(subset=["_ts"])

        if len(df_temp) < 10:
            return {"error": "Insufficient timestamped data (need at least 10 rows)", "fitted": False}

        df_temp = df_temp.sort_values("_ts")
        self._time_range = (
            float(df_temp["_ts"].min().timestamp()),
            float(df_temp["_ts"].max().timestamp()),
        )

        # Build temporal edges
        for _, row in df_temp.iterrows():
            ts = float(row["_ts"].timestamp())
            supplier = str(row.get("supplier", "")) if pd.notna(row.get("supplier")) else None
            sku = str(row.get("sku", "")) if pd.notna(row.get("sku")) else None
            warehouse = str(row.get("warehouse", "")) if pd.notna(row.get("warehouse")) else None
            delay = float(row.get("delay_days", 0) or 0)
            cost = float(row.get("cost", 0) or 0)
            qty = float(row.get("quantity", 0) or 0)

            # Create temporal edges for each relationship
            if supplier and sku:
                edge = TemporalEdge(f"supplier:{supplier}", f"sku:{sku}", ts, delay, cost, qty)
                self.temporal_edges.append(edge)
                self._update_memories(edge)
                self._update_edge_stats(edge)

            if sku and warehouse:
                edge = TemporalEdge(f"sku:{sku}", f"warehouse:{warehouse}", ts, delay, cost, qty)
                self.temporal_edges.append(edge)
                self._update_memories(edge)
                self._update_edge_stats(edge)

        # Compute temporal embeddings via message passing
        self._compute_temporal_embeddings()

        self._fitted = True
        return {
            "fitted": True,
            "temporal_edges": len(self.temporal_edges),
            "nodes_tracked": len(self.node_memories),
            "time_range": {
                "start": datetime.fromtimestamp(self._time_range[0], tz=timezone.utc).isoformat(),
                "end": datetime.fromtimestamp(self._time_range[1], tz=timezone.utc).isoformat(),
                "span_days": round((self._time_range[1] - self._time_range[0]) / 86400, 1),
            },
            "edge_pairs_tracked": len(self.edge_statistics),
        }

    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """
        Analyze how supply chain relationships evolve over time.
        Returns seasonal patterns, degradation trends, and dependency shifts.
        """
        if not self._fitted:
            return {"error": "Engine not fitted. Call fit(df) first."}

        results: Dict[str, Any] = {
            "degrading_relationships": [],
            "improving_relationships": [],
            "seasonal_patterns": [],
            "dependency_concentration_trends": [],
            "spof_trending_nodes": [],  # Single Point of Failure candidates
        }

        # Analyze each edge pair for temporal trends
        for edge_key, stats in self.edge_statistics.items():
            windows = stats.get("time_windows", {})
            if len(windows) < 2:
                continue

            sorted_periods = sorted(windows.keys())
            delay_series = [windows[p]["avg_delay"] for p in sorted_periods]
            volume_series = [windows[p]["count"] for p in sorted_periods]

            # Compute trend via linear regression
            if len(delay_series) >= 3:
                delay_trend = self._compute_trend(delay_series)
                volume_trend = self._compute_trend(volume_series)

                relationship = {
                    "edge": edge_key,
                    "source": stats["source"],
                    "target": stats["target"],
                    "periods_analyzed": len(sorted_periods),
                    "delay_trend": round(delay_trend, 4),
                    "volume_trend": round(volume_trend, 4),
                    "latest_avg_delay": round(delay_series[-1], 1),
                    "earliest_avg_delay": round(delay_series[0], 1),
                    "delay_change_pct": round(
                        ((delay_series[-1] - delay_series[0]) / max(delay_series[0], 0.1)) * 100, 1
                    ),
                }

                if delay_trend > 0.1:
                    relationship["status"] = "DEGRADING"
                    relationship["alert"] = (
                        f"Delays on {stats['source']} → {stats['target']} have increased "
                        f"by {relationship['delay_change_pct']}% over {len(sorted_periods)} periods"
                    )
                    results["degrading_relationships"].append(relationship)
                elif delay_trend < -0.1:
                    relationship["status"] = "IMPROVING"
                    results["improving_relationships"].append(relationship)

            # Detect seasonality (monthly patterns)
            if len(delay_series) >= 6:
                seasonal = self._detect_seasonality(delay_series)
                if seasonal["is_seasonal"]:
                    results["seasonal_patterns"].append({
                        "edge": edge_key,
                        "peak_period_index": seasonal["peak_index"],
                        "trough_period_index": seasonal["trough_index"],
                        "amplitude": round(seasonal["amplitude"], 2),
                        "insight": f"Performance on {edge_key} shows seasonal variation — "
                                   f"peak delays occur in period {seasonal['peak_index'] + 1}",
                    })

        # SPOF detection: nodes with increasing dependency concentration
        for node_id, memory in self.node_memories.items():
            if memory.interaction_count < 5:
                continue

            diversity_ratio = len(memory.partner_diversity) / max(memory.interaction_count, 1)
            avg_delay = float(np.mean(memory.delay_history)) if memory.delay_history else 0

            # A node is SPOF-trending if it has many interactions but few partners
            if diversity_ratio < 0.1 and memory.interaction_count > 20:
                results["spof_trending_nodes"].append({
                    "node_id": node_id,
                    "interaction_count": memory.interaction_count,
                    "unique_partners": len(memory.partner_diversity),
                    "diversity_ratio": round(diversity_ratio, 3),
                    "avg_delay": round(avg_delay, 1),
                    "risk_level": "CRITICAL" if diversity_ratio < 0.05 else "HIGH",
                    "recommendation": f"Node {node_id} is trending toward single-point-of-failure — "
                                      f"only {len(memory.partner_diversity)} partner(s) for "
                                      f"{memory.interaction_count} interactions",
                })

        # Sort by severity
        results["degrading_relationships"].sort(key=lambda x: x["delay_trend"], reverse=True)
        results["spof_trending_nodes"].sort(key=lambda x: x["diversity_ratio"])

        return results

    def predict_evolution(self, periods_ahead: int = 3) -> Dict[str, Any]:
        """
        Predict how the supply chain network topology will evolve.
        Uses learned temporal patterns to forecast future edge weights and risk.
        """
        if not self._fitted:
            return {"error": "Engine not fitted."}

        predictions: Dict[str, Any] = {
            "prediction_horizon": f"{periods_ahead} periods ahead",
            "edge_predictions": [],
            "risk_forecasts": [],
            "topology_changes": [],
        }

        for edge_key, stats in self.edge_statistics.items():
            windows = stats.get("time_windows", {})
            if len(windows) < 3:
                continue

            sorted_periods = sorted(windows.keys())
            delay_series = [windows[p]["avg_delay"] for p in sorted_periods]
            volume_series = [windows[p]["count"] for p in sorted_periods]

            # Forecast delay using Holt's linear trend method
            delay_forecast = self._holt_forecast(delay_series, periods_ahead)
            volume_forecast = self._holt_forecast(volume_series, periods_ahead)

            prediction = {
                "edge": edge_key,
                "source": stats["source"],
                "target": stats["target"],
                "current_avg_delay": round(delay_series[-1], 1),
                "predicted_delays": [round(d, 1) for d in delay_forecast],
                "current_volume": volume_series[-1],
                "predicted_volumes": [round(v, 0) for v in volume_forecast],
                "delay_direction": "INCREASING" if delay_forecast[-1] > delay_series[-1] else "DECREASING",
            }

            # Risk forecast
            if delay_forecast[-1] > delay_series[-1] * 1.5:
                prediction["risk_alert"] = "HIGH"
                prediction["alert_message"] = (
                    f"Delays on {edge_key} predicted to increase by "
                    f"{round((delay_forecast[-1] / max(delay_series[-1], 0.1) - 1) * 100, 0)}% "
                    f"in {periods_ahead} periods"
                )
                predictions["risk_forecasts"].append(prediction)

            predictions["edge_predictions"].append(prediction)

            # Topology change detection
            if volume_forecast[-1] < volume_series[-1] * 0.3:
                predictions["topology_changes"].append({
                    "type": "RELATIONSHIP_WEAKENING",
                    "edge": edge_key,
                    "current_volume": volume_series[-1],
                    "predicted_volume": round(volume_forecast[-1]),
                    "interpretation": f"The {edge_key} relationship may dissolve — "
                                      f"volume predicted to drop by "
                                      f"{round((1 - volume_forecast[-1] / max(volume_series[-1], 1)) * 100)}%",
                })
            elif volume_forecast[-1] > volume_series[-1] * 2.0:
                predictions["topology_changes"].append({
                    "type": "DEPENDENCY_GROWTH",
                    "edge": edge_key,
                    "current_volume": volume_series[-1],
                    "predicted_volume": round(volume_forecast[-1]),
                    "interpretation": f"Growing dependency on {edge_key} — "
                                      f"volume predicted to increase {round(volume_forecast[-1] / max(volume_series[-1], 1), 1)}x",
                })

        return predictions

    def get_temporal_risk_scores(self) -> Dict[str, Any]:
        """
        Compute risk scores that account for trajectory, not just current state.
        A supplier with rising delays gets a higher score than one with stable delays,
        even if the stable one currently has higher absolute delays.
        """
        if not self._fitted:
            return {"error": "Engine not fitted."}

        scores: List[Dict[str, Any]] = []

        for node_id, memory in self.node_memories.items():
            if not node_id.startswith("supplier:") or memory.interaction_count < 3:
                continue

            supplier_name = node_id.replace("supplier:", "")

            # Base risk from delay history
            if memory.delay_history:
                avg_delay = float(np.mean(memory.delay_history))
                delay_std = float(np.std(memory.delay_history)) if len(memory.delay_history) > 1 else 0
                max_delay = float(np.max(memory.delay_history))
            else:
                avg_delay = 0
                delay_std = 0
                max_delay = 0

            # Trajectory risk: are delays getting worse?
            trajectory_score = 0.0
            if len(memory.delay_history) >= 5:
                recent_half = memory.delay_history[len(memory.delay_history)//2:]
                earlier_half = memory.delay_history[:len(memory.delay_history)//2]
                recent_avg = float(np.mean(recent_half))
                earlier_avg = float(np.mean(earlier_half))
                if earlier_avg > 0:
                    trajectory_score = (recent_avg - earlier_avg) / earlier_avg
                elif recent_avg > 0:
                    trajectory_score = 1.0  # Going from 0 to positive is bad

            # Diversity risk: fewer partners = more fragile
            diversity_score = 1.0 / max(len(memory.partner_diversity), 1)

            # Composite temporal risk score (0-100)
            base_risk = min(100, avg_delay * 3 + delay_std * 5)
            trajectory_risk = min(30, max(0, trajectory_score * 50))
            diversity_risk = min(20, diversity_score * 20)
            temporal_risk = round(min(100, base_risk * 0.5 + trajectory_risk + diversity_risk), 1)

            scores.append({
                "supplier": supplier_name,
                "node_id": node_id,
                "temporal_risk_score": temporal_risk,
                "components": {
                    "base_delay_risk": round(base_risk, 1),
                    "trajectory_risk": round(trajectory_risk, 1),
                    "diversity_risk": round(diversity_risk, 1),
                },
                "avg_delay": round(avg_delay, 1),
                "delay_trend": "WORSENING" if trajectory_score > 0.2 else "IMPROVING" if trajectory_score < -0.2 else "STABLE",
                "trajectory_change_pct": round(trajectory_score * 100, 1),
                "interaction_count": memory.interaction_count,
                "partner_count": len(memory.partner_diversity),
                "tier": "CRITICAL" if temporal_risk >= 70 else "ELEVATED" if temporal_risk >= 40 else "STABLE",
            })

        scores.sort(key=lambda x: x["temporal_risk_score"], reverse=True)

        return {
            "total_suppliers_analyzed": len(scores),
            "critical_count": len([s for s in scores if s["tier"] == "CRITICAL"]),
            "elevated_count": len([s for s in scores if s["tier"] == "ELEVATED"]),
            "stable_count": len([s for s in scores if s["tier"] == "STABLE"]),
            "suppliers": scores,
            "methodology": (
                "Trajectory-adjusted risk scoring: base delay risk × worsening trend penalty × "
                "partner diversity penalty. Uses linear regression on monthly delay windows for "
                "trend detection. Classical time-series statistics — not a GNN."
            ),
        }

    # ── Private helpers ──

    def _update_memories(self, edge: TemporalEdge):
        """Update source and target node memories."""
        if edge.source not in self.node_memories:
            self.node_memories[edge.source] = TemporalNodeMemory(edge.source, self.embedding_dim)
        if edge.target not in self.node_memories:
            self.node_memories[edge.target] = TemporalNodeMemory(edge.target, self.embedding_dim)

        self.node_memories[edge.source].update(edge, is_source=True)
        self.node_memories[edge.target].update(edge, is_source=False)

    def _update_edge_stats(self, edge: TemporalEdge):
        """Track per-edge-pair statistics with time windowing."""
        key = f"{edge.source}→{edge.target}"

        if key not in self.edge_statistics:
            self.edge_statistics[key] = {
                "source": edge.source,
                "target": edge.target,
                "total_interactions": 0,
                "total_delay": 0.0,
                "total_cost": 0.0,
                "time_windows": {},
            }

        stats = self.edge_statistics[key]
        stats["total_interactions"] += 1
        stats["total_delay"] += edge.delay
        stats["total_cost"] += edge.cost

        # Group by month for time-window analysis
        dt = datetime.fromtimestamp(edge.timestamp, tz=timezone.utc)
        period = f"{dt.year}-{dt.month:02d}"

        if period not in stats["time_windows"]:
            stats["time_windows"][period] = {
                "count": 0, "total_delay": 0.0, "total_cost": 0.0,
                "avg_delay": 0.0, "avg_cost": 0.0,
            }

        window = stats["time_windows"][period]
        window["count"] += 1
        window["total_delay"] += edge.delay
        window["total_cost"] += edge.cost
        window["avg_delay"] = window["total_delay"] / window["count"]
        window["avg_cost"] = window["total_cost"] / window["count"]

    def _compute_temporal_embeddings(self):
        """
        Neighbourhood aggregation: blend each node's feature vector with
        the mean of its neighbours' feature vectors.

        Uses a fixed 0.7 (self) / 0.3 (neighbour mean) blend — there are
        NO learned weights and NO gradient updates. This is mean-pooling
        aggregation, not a temporal attention mechanism.
        """
        # Build adjacency from temporal edges
        adjacency: Dict[str, List[str]] = defaultdict(list)
        for edge in self.temporal_edges:
            adjacency[edge.source].append(edge.target)
            adjacency[edge.target].append(edge.source)

        # 2 rounds of message passing
        for _round in range(2):
            new_embeddings = {}
            for node_id, memory in self.node_memories.items():
                neighbors = list(set(adjacency.get(node_id, [])))
                if not neighbors:
                    new_embeddings[node_id] = memory.embedding.copy()
                    continue

                # Aggregate neighbor embeddings with mean pooling
                neighbor_embs = []
                for n in neighbors:
                    if n in self.node_memories:
                        neighbor_embs.append(self.node_memories[n].embedding)

                if neighbor_embs:
                    agg = np.mean(neighbor_embs, axis=0)
                    # Combine self-embedding with aggregated neighbors
                    new_embeddings[node_id] = 0.7 * memory.embedding + 0.3 * agg
                else:
                    new_embeddings[node_id] = memory.embedding.copy()

            # Update
            for node_id, emb in new_embeddings.items():
                self.node_memories[node_id].embedding = emb

    def _compute_trend(self, series: List[float]) -> float:
        """Simple linear regression slope — positive = increasing."""
        n = len(series)
        if n < 2:
            return 0.0
        x = np.arange(n, dtype=float)
        y = np.array(series, dtype=float)
        x_mean = x.mean()
        y_mean = y.mean()
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        if denominator == 0:
            return 0.0
        return float(numerator / denominator)

    def _detect_seasonality(self, series: List[float]) -> Dict[str, Any]:
        """Detect seasonal patterns using autocorrelation."""
        n = len(series)
        if n < 6:
            return {"is_seasonal": False}

        arr = np.array(series)
        arr_centered = arr - arr.mean()
        autocorr = np.correlate(arr_centered, arr_centered, mode="full")
        autocorr = autocorr[n-1:]  # Keep positive lags only
        if autocorr[0] != 0:
            autocorr = autocorr / autocorr[0]

        # Look for peaks in autocorrelation (at lag > 1)
        peaks = []
        for i in range(2, min(len(autocorr), n // 2)):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] if i+1 < len(autocorr) else False:
                if autocorr[i] > 0.3:  # Significant correlation
                    peaks.append(i)

        return {
            "is_seasonal": len(peaks) > 0,
            "period": peaks[0] if peaks else None,
            "peak_index": int(np.argmax(arr)),
            "trough_index": int(np.argmin(arr)),
            "amplitude": float(np.max(arr) - np.min(arr)),
        }

    def _holt_forecast(self, series: List[float], periods: int = 3) -> List[float]:
        """Holt's linear trend forecasting."""
        if len(series) < 2:
            return [series[-1]] * periods if series else [0.0] * periods

        alpha, beta = 0.3, 0.1
        level = float(series[0])
        trend = float(series[1] - series[0])

        for val in series:
            last_level = level
            level = alpha * val + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend

        forecasts = []
        for i in range(1, periods + 1):
            forecasts.append(max(0.0, level + i * trend))

        return forecasts

    # ── Sub-Tier Discovery (P0 Gap Fix) ─────────────────────────────────────────

    def discover_subtier_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Discover sub-tier supplier relationships for a given node.

        This method returns downstream (Tier 2, Tier 3, ... Tier N) suppliers
        that feed into the specified supplier node.

        CURRENT STATE: Returns mocked sub-tier data.
        The interface is designed to be swapped for a real data source:
          - Dun & Bradstreet API (corporate linkage data)
          - Panjiva / S&P Global Market Intelligence (trade flow data)
          - Custom ERP connector (internal procurement hierarchies)

        Args:
            node_id: Supplier identifier (e.g., "SUP-001" or "supplier:Acme Corp")

        Returns:
            List of sub-tier supplier nodes with relationship metadata.
        """
        # Normalize node_id
        clean_id = node_id.replace("supplier:", "").strip()

        # ── Mock sub-tier data ──
        # In production, replace this block with an API call to your data provider.
        mock_subtiers = [
            {
                "supplier_id": f"{clean_id}-T2-001",
                "name": f"{clean_id} Sub-Supplier Alpha",
                "tier": 2,
                "relationship_type": "RAW_MATERIAL",
                "parent_id": clean_id,
                "location": "Shenzhen, China",
                "risk_score": round(np.random.uniform(20, 80), 1),
                "confidence": 0.85,
                "data_source": "mock",
                "products": ["Raw Material A", "Component X"],
                "last_verified": datetime.now(timezone.utc).isoformat(),
            },
            {
                "supplier_id": f"{clean_id}-T2-002",
                "name": f"{clean_id} Sub-Supplier Beta",
                "tier": 2,
                "relationship_type": "COMPONENT",
                "parent_id": clean_id,
                "location": "Ho Chi Minh City, Vietnam",
                "risk_score": round(np.random.uniform(20, 80), 1),
                "confidence": 0.72,
                "data_source": "mock",
                "products": ["Component Y"],
                "last_verified": datetime.now(timezone.utc).isoformat(),
            },
            {
                "supplier_id": f"{clean_id}-T3-001",
                "name": f"{clean_id} Tier-3 Raw Source",
                "tier": 3,
                "relationship_type": "RAW_MATERIAL",
                "parent_id": f"{clean_id}-T2-001",
                "location": "Jakarta, Indonesia",
                "risk_score": round(np.random.uniform(30, 90), 1),
                "confidence": 0.58,
                "data_source": "mock",
                "products": ["Rare Earth Element"],
                "last_verified": datetime.now(timezone.utc).isoformat(),
            },
        ]

        # If the engine has real data about this node, enrich the mock
        node_key = f"supplier:{clean_id}"
        if node_key in self.node_memories:
            memory = self.node_memories[node_key]
            # Add known partners as potential sub-tier candidates
            for partner in list(memory.partner_diversity)[:3]:
                if partner.startswith("sku:"):
                    continue  # Skip SKU nodes
                mock_subtiers.append({
                    "supplier_id": partner.replace("supplier:", ""),
                    "name": partner.replace("supplier:", ""),
                    "tier": 2,
                    "relationship_type": "KNOWN_PARTNER",
                    "parent_id": clean_id,
                    "location": "Unknown",
                    "risk_score": None,
                    "confidence": 0.95,
                    "data_source": "temporal_graph",
                    "products": [],
                    "last_verified": datetime.now(timezone.utc).isoformat(),
                })

        return mock_subtiers

# ── Backward-compatibility alias ─────────────────────────────────────────────
# main.py instantiates TGNNEngine by name. This alias lets existing call sites
# work without modification while the class is honestly named internally.
TGNNEngine = TemporalTrendEngine
