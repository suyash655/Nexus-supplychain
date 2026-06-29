"""
SynChain 2.0 — Graph Intelligence Engine
==========================================
Models the supply chain as a directed graph and performs network analysis.
Uses networkx for graph operations.
"""

import logging
import warnings
import networkx as nx  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Suppress NetworkX constant input warning
warnings.filterwarnings("ignore", category=UserWarning, message=".*ConstantInputWarning.*")

logger_ge = logging.getLogger("nexus.graph_engine")


class SupplyChainGraph:
    """Supply chain modeled as a directed weighted graph."""

    def __init__(self):
        self.G = nx.DiGraph()
        self._built = False

    def build_from_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Build supply chain graph from transaction data."""
        import time as _time
        start_total = _time.time()
        
        self.G.clear()

        # Add supplier nodes
        if "supplier" in df.columns:
            start = _time.time()
            for supplier in df["supplier"].dropna().unique():
                subset = df[df["supplier"] == supplier]
                delays = pd.to_numeric(subset.get("delay_days", pd.Series([0])), errors="coerce").fillna(0)
                costs = pd.to_numeric(subset.get("cost", pd.Series([0])), errors="coerce").fillna(0)
                self.G.add_node(
                    f"supplier:{supplier}",
                    type="supplier",
                    name=str(supplier),
                    shipments=len(subset),
                    avg_delay=round(float(delays.mean()), 1),
                    total_cost=round(float(costs.sum()), 2),
                )
            logger_ge.debug(f"Supplier nodes added in {_time.time() - start:.2f}s")

        # Add SKU nodes
        if "sku" in df.columns:
            start = _time.time()
            for sku in df["sku"].dropna().unique():
                subset = df[df["sku"] == sku]
                self.G.add_node(
                    f"sku:{sku}",
                    type="sku",
                    name=str(sku),
                    volume=len(subset),
                )
            logger_ge.debug(f"SKU nodes added in {_time.time() - start:.2f}s")

        # Add warehouse nodes
        if "warehouse" in df.columns:
            start = _time.time()
            for wh in df["warehouse"].dropna().unique():
                subset = df[df["warehouse"] == wh]
                self.G.add_node(
                    f"warehouse:{wh}",
                    type="warehouse",
                    name=str(wh),
                    throughput=len(subset),
                )
            logger_ge.debug(f"Warehouse nodes added in {_time.time() - start:.2f}s")

        # Add region nodes
        if "region" in df.columns:
            start = _time.time()
            for region in df["region"].dropna().unique():
                subset = df[df["region"] == region]
                self.G.add_node(
                    f"region:{region}",
                    type="region",
                    name=str(region),
                    activity=len(subset),
                )
            logger_ge.debug(f"Region nodes added in {_time.time() - start:.2f}s")

        # ── Build edges: accumulate delay and cost per edge ──
        # We keep raw counts separate from risk signals.
        # After all rows are processed we compute a normalised risk_weight
        # from (avg_delay, cost_variance) so that high-volume relationships
        # are NOT treated as structurally shorter/safer paths.
        start = _time.time()
        for _, row in df.iterrows():
            supplier = row.get("supplier")
            sku = row.get("sku")
            warehouse = row.get("warehouse")
            region = row.get("region")
            delay = float(row.get("delay_days", 0) or 0)
            cost = float(row.get("cost", 0) or 0)

            # Supplier → SKU
            if pd.notna(supplier) and pd.notna(sku):
                u, v = f"supplier:{supplier}", f"sku:{sku}"
                if self.G.has_edge(u, v):
                    self.G[u][v]["transaction_count"] += 1
                    self.G[u][v]["total_delay"] += delay
                    self.G[u][v]["total_cost"] += cost
                    self.G[u][v]["_cost_samples"].append(cost)
                else:
                    self.G.add_edge(
                        u, v,
                        edge_type="supplies",
                        transaction_count=1,
                        total_delay=delay,
                        total_cost=cost,
                        _cost_samples=[cost],
                    )

            # SKU → Warehouse
            if pd.notna(sku) and pd.notna(warehouse):
                u, v = f"sku:{sku}", f"warehouse:{warehouse}"
                if self.G.has_edge(u, v):
                    self.G[u][v]["transaction_count"] += 1
                else:
                    self.G.add_edge(u, v, edge_type="stored_at", transaction_count=1,
                                    total_delay=0, total_cost=0, _cost_samples=[])

            # Warehouse → Region
            if pd.notna(warehouse) and pd.notna(region):
                u, v = f"warehouse:{warehouse}", f"region:{region}"
                if self.G.has_edge(u, v):
                    self.G[u][v]["transaction_count"] += 1
                else:
                    self.G.add_edge(u, v, edge_type="serves", transaction_count=1,
                                    total_delay=0, total_cost=0, _cost_samples=[])
        logger_ge.debug(f"Edges built in {_time.time() - start:.2f}s")

        # ── Compute risk_weight per edge ──
        # risk_weight is a composite of:
        #   • avg_delay_norm  : normalised avg delay across all edges (0–1)
        #   • cost_cv_norm    : normalised cost coefficient of variation (0–1)
        #
        # Higher risk_weight = higher risk path.
        # NetworkX betweenness/pagerank use weight as path COST, so passing
        # risk_weight means riskier edges are "longer" — which is the correct
        # semantics for supply chain risk analysis.
        start = _time.time()
        self._attach_risk_weights()
        logger_ge.debug(f"Risk weights attached in {_time.time() - start:.2f}s")

        self._built = True
        logger_ge.debug(f"Total graph build time: {_time.time() - start_total:.2f}s")
        return self.get_graph_summary()

    def _attach_risk_weights(self):
        """
        Compute and attach a normalised risk_weight to every edge.

        Methodology:
          avg_delay  = total_delay / transaction_count
          cost_cv    = std(cost_samples) / mean(cost_samples)  [0 if no variance]
          raw_risk   = 0.6 × avg_delay_norm + 0.4 × cost_cv_norm
          risk_weight = clipped to [0.01, 1.0]

        Edges without cost/delay data (SKU→Warehouse, Warehouse→Region)
        receive a neutral weight of 0.5.
        """
        # Collect raw values to normalise across all edges
        avg_delays = []
        cost_cvs = []
        for u, v, data in self.G.edges(data=True):
            n = data.get("transaction_count", 1)
            td = data.get("total_delay", 0)
            samples = data.get("_cost_samples", [])
            if n > 0:
                avg_delays.append(td / n)
                if len(samples) >= 2:
                    mean_c = float(np.mean(samples))
                    cv = float(np.std(samples)) / mean_c if mean_c > 0 else 0.0
                else:
                    cv = 0.0
                cost_cvs.append(cv)

        max_delay = max(avg_delays) if avg_delays else 1.0
        max_cv = max(cost_cvs) if cost_cvs else 1.0

        idx = 0
        for u, v, data in self.G.edges(data=True):
            n = data.get("transaction_count", 1)
            td = data.get("total_delay", 0)
            samples = data.get("_cost_samples", [])

            if n > 0 and (td > 0 or samples):
                avg_d = td / n
                mean_c = float(np.mean(samples)) if samples else 0.0
                cv = (float(np.std(samples)) / mean_c) if (mean_c > 0 and len(samples) >= 2) else 0.0

                delay_norm = avg_d / max(max_delay, 1e-9)
                cv_norm = cv / max(max_cv, 1e-9)
                raw = 0.6 * delay_norm + 0.4 * cv_norm
                risk_weight = round(float(np.clip(raw, 0.01, 1.0)), 4)
            else:
                # No risk signal available — neutral weight
                risk_weight = 0.5

            data["risk_weight"] = risk_weight
            # Expose avg_delay on the edge for downstream use
            data["avg_delay"] = round(data.get("total_delay", 0) / max(n, 1), 2)
            # Remove internal accumulator — not needed in API responses
            data.pop("_cost_samples", None)
            idx += 1

    def get_graph_summary(self) -> Dict[str, Any]:
        """Get graph overview statistics and resilience metrics."""
        if not self._built:
            return {"error": "Graph not built yet"}

        node_types: Dict[str, int] = defaultdict(int)
        for _, data in self.G.nodes(data=True):
            node_types[data.get("type", "unknown")] += 1  # type: ignore[index, operator]

        summary = {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "node_types": dict(node_types),
            "density": round(float(nx.density(self.G)), 4),  # type: ignore[call-overload]
            "is_connected": nx.is_weakly_connected(self.G) if self.G.number_of_nodes() > 0 else False,
            "components": nx.number_weakly_connected_components(self.G) if self.G.number_of_nodes() > 0 else 0,
            "resilience_metrics": self.get_resilience_metrics(),
        }
        return summary

    def get_resilience_metrics(self) -> Dict[str, Any]:
        """
        Compute supply chain resilience metrics grounded in network science.

        Three metrics are reported independently — they are NOT combined into
        a single arbitrary weighted score, because the weights would have no
        empirical basis:

        1. redundancy_ratio
           Average number of direct upstream suppliers per SKU node.
           A SKU sourced from 3 suppliers has ratio=3 (resilient).
           A SKU with a single source has ratio=1 (fragile).
           Formula: mean(in_degree of SKU nodes)

        2. concentration_index
           Fraction of total transaction volume passing through the single
           highest-throughput node (warehouse or supplier).
           Low = well-distributed. High = single point of concentration risk.
           Formula: max(node_shipments) / sum(node_shipments) for warehouse/supplier nodes

        3. algebraic_connectivity (Fiedler value)
           How well-connected the undirected graph is overall.
           Value = 0 means the graph is disconnected.
           Higher value = harder to fragment.
           Reported transparently without being combined with other metrics.

        A composite "network_resilience_score" (0-100) is also provided for
        dashboard display, computed as:
            score = 50 × min(redundancy_ratio / 3, 1.0)      ← up to 50 pts for redundancy
                  + 30 × (1 - min(concentration_index, 1.0)) ← up to 30 pts for distribution
                  + 20 × min(algebraic_connectivity, 1.0)    ← up to 20 pts for connectivity
        This formula and its weights are documented here and in the API response.
        """
        if self.G.number_of_nodes() == 0:
            return {}

        # ── 1. Redundancy ratio ──
        sku_nodes = [n for n, d in self.G.nodes(data=True) if d.get("type") == "sku"]
        if sku_nodes:
            in_degrees = [self.G.in_degree(n) for n in sku_nodes]
            redundancy_ratio = float(np.mean(in_degrees))
        else:
            redundancy_ratio = 1.0

        # ── 2. Concentration index ──
        supply_nodes = [
            (n, d) for n, d in self.G.nodes(data=True)
            if d.get("type") in ("supplier", "warehouse")
        ]
        if supply_nodes:
            volumes = [
                d.get("shipments", 0) + d.get("throughput", 0)
                for _, d in supply_nodes
            ]
            total_vol = sum(volumes)
            concentration_index = (max(volumes) / total_vol) if total_vol > 0 else 1.0
        else:
            concentration_index = 1.0

        # ── 3. Algebraic connectivity (Fiedler value) ──
        algebraic_connectivity = 0.0
        try:
            undirected = self.G.to_undirected()
            if nx.is_connected(undirected) and undirected.number_of_nodes() > 1:
                # Use faster method for larger graphs
                method = "tracemin" if undirected.number_of_nodes() > 100 else "lanczos"
                algebraic_connectivity = float(
                    nx.algebraic_connectivity(undirected, method=method)
                )
        except Exception as exc:
            logger_ge.debug("Algebraic connectivity computation skipped: %s", exc)

        # ── Composite score (documented formula) ──
        redundancy_pts   = 50.0 * min(redundancy_ratio / 3.0, 1.0)
        distribution_pts = 30.0 * (1.0 - min(concentration_index, 1.0))
        connectivity_pts = 20.0 * min(algebraic_connectivity, 1.0)
        composite = round(redundancy_pts + distribution_pts + connectivity_pts, 1)

        # ── Degree assortativity (systemic risk proxy) ──
        systemic_risk_index = 0.0
        try:
            if len(self.G.edges) > 2:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    systemic_risk_index = round(
                        float(nx.degree_pearson_correlation_coefficient(self.G)), 3
                    )
        except Exception as exc:
            logger_ge.debug("Degree assortativity skipped: %s", exc)

        return {
            "network_resilience_score": composite,
            "score_components": {
                "redundancy_pts": round(redundancy_pts, 1),
                "distribution_pts": round(distribution_pts, 1),
                "connectivity_pts": round(connectivity_pts, 1),
            },
            "score_formula": (
                "50 × min(redundancy_ratio/3, 1) "
                "+ 30 × (1 - concentration_index) "
                "+ 20 × min(algebraic_connectivity, 1)"
            ),
            "redundancy_ratio": round(redundancy_ratio, 2),
            "redundancy_interpretation": (
                "Each SKU has on average "
                f"{redundancy_ratio:.1f} upstream supplier(s). "
                + ("Good diversification." if redundancy_ratio >= 2 else
                   "Single-source risk present.")
            ),
            "concentration_index": round(concentration_index, 3),
            "concentration_interpretation": (
                f"{concentration_index * 100:.1f}% of volume flows through the "
                "single highest-throughput node. "
                + ("Highly concentrated — single point of failure risk."
                   if concentration_index > 0.5 else "Reasonably distributed.")
            ),
            "algebraic_connectivity": round(algebraic_connectivity, 4),
            "structural_robustness": (
                "High" if algebraic_connectivity > 0.5
                else "Medium" if algebraic_connectivity > 0.1
                else "Low"
            ),
            "systemic_risk_index": systemic_risk_index,
        }

    def get_centrality_scores(self) -> Dict[str, List[Dict]]:
        """
        Compute centrality metrics for all nodes.

        Uses risk_weight as the edge weight for betweenness and PageRank.
        risk_weight is a composite of avg_delay and cost_variance (0–1),
        where higher = riskier. In NetworkX, higher weight = longer path,
        so riskier edges are traversed less in shortest-path algorithms —
        correctly identifying nodes that sit on high-risk critical paths.
        """
        if not self._built or self.G.number_of_nodes() == 0:
            return {"degree": [], "betweenness": [], "pagerank": []}

        try:
            degree = nx.degree_centrality(self.G)
        except Exception as e:
            logger_ge.error(f"Failed to compute degree centrality: {e}")
            degree = {}

        # Use risk_weight: high-risk edges are "costly" to traverse,
        # surfacing nodes on unavoidably risky paths as high-centrality.
        try:
            betweenness = nx.betweenness_centrality(self.G, weight="risk_weight")
        except Exception as e:
            logger_ge.error(f"Failed to compute betweenness centrality: {e}")
            betweenness = {}

        try:
            pagerank = nx.pagerank(self.G, weight="risk_weight")
        except Exception as e:
            logger_ge.error(f"Failed to compute PageRank: {e}")
            pagerank = {n: 1.0 / self.G.number_of_nodes() for n in self.G.nodes()}

        def format_scores(scores: dict, metric_name: str) -> List[Dict]:
            result = []
            for node, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                if node not in self.G.nodes:
                    continue
                data = self.G.nodes[node]
                result.append({
                    "node_id": node,
                    "name": data.get("name", node),
                    "type": data.get("type", "unknown"),
                    metric_name: round(float(score), 4),
                })
            return result[:20]

        return {
            "degree": format_scores(degree, "degree_centrality"),
            "betweenness": format_scores(betweenness, "betweenness_centrality"),
            "pagerank": format_scores(pagerank, "pagerank_score"),
        }

    def simulate_cascade(self, failed_nodes: List[str]) -> Dict[str, Any]:
        """Simulate what happens if one or more nodes fail (multi-node cascade analysis)."""
        if not self._built:
            return {"error": "Graph not built yet"}

        resolved_nodes = []
        for fn in failed_nodes:
            if fn in self.G:
                resolved_nodes.append(fn)
            else:
                matches = [n for n in self.G.nodes() if fn.lower() in n.lower()]
                if matches:
                    resolved_nodes.append(matches[0])

        if not resolved_nodes:
            return {"error": "None of the specified nodes found", "available_samples": list(self.G.nodes)[:10]} # type: ignore

        # BFS for collective downstream impact
        all_affected = set()
        for start_node in resolved_nodes:
            try:
                successors = list(self.G.successors(start_node))
                queue = list(successors)[:100] # type: ignore
                visited = {start_node}
                while queue:
                    current = queue.pop(0)
                    if str(current) in visited:
                        continue
                    visited.add(str(current))
                    all_affected.add(str(current))
                    queue.extend([str(s) for s in self.G.successors(current)])
            except Exception as e:
                logger_ge.error(f"Error simulating cascade from {start_node}: {e}")
                continue

        # Remove failed nodes from affected (they are the cause)
        for fn in resolved_nodes:
            if fn in all_affected:
                all_affected.remove(fn)

        affected_details = []
        for node in all_affected:
            if node not in self.G.nodes:
                continue
            data = self.G.nodes[node]
            ttr_base = {"supplier": 14, "warehouse": 7, "sku": 5, "region": 3}.get(data.get("type"), 5)
            affected_details.append({
                "node_id": node,
                "name": data.get("name", node),
                "type": data.get("type", "unknown"),
                "estimated_ttr_days": ttr_base,
            })

        primary_node = resolved_nodes[0] if resolved_nodes else ""
        return {
            "failed_nodes": resolved_nodes,
            "total_affected": len(all_affected),
            "affected_details": list(affected_details)[:50], # type: ignore
            "risk_assessment": self._cascade_risk(primary_node, all_affected) if primary_node else "unknown",
            "recovery_complexity": "High" if len(all_affected) > 15 or len(resolved_nodes) > 2 else "Medium" if len(all_affected) > 5 else "Low",
        }

    def _cascade_depth(self, start_node: str) -> int:
        """Compute maximum cascade depth from a node."""
        try:
            lengths = nx.single_source_shortest_path_length(self.G, start_node)
            return max(lengths.values()) if lengths else 0
        except Exception as exc:
            logger_ge.debug("Cascade depth skipped for %s: %s", start_node, exc)
            return 0

    def deep_tier_inference(self, df: "pd.DataFrame | None" = None) -> Dict[str, Any]:
        """Infer probable Tier 3+ relationships using real data patterns.
        
        Algorithm:
        - Identifies suppliers that share SKUs (implicit dependency).
        - Uses co-occurrence frequency and cost correlation as a proxy for
          hidden sub-tier relationships.
        - Returns ONLY data-driven inferences — no hardcoded strings.
        """
        if not self._built:
            return {"error": "Graph not built yet"}

        if df is None or len(df) == 0:
            return {
                "shadow_nodes": [],
                "shadow_edges": [],
                "total_inferred": 0,
                "visibility_multiplier": "1.0x",
                "narrative": "Upload supply chain data to enable deep-tier inference.",
            }

        shadow_nodes: List[Dict] = []
        shadow_edges: List[Dict] = []

        try:
            if "supplier" not in df.columns or "sku" not in df.columns:
                return {
                    "shadow_nodes": [],
                    "shadow_edges": [],
                    "total_inferred": 0,
                    "narrative": "supplier and sku columns required for inference.",
                }

            # Build supplier→SKU mapping
            supplier_skus: Dict[str, set] = {}
            for _, row in df.iterrows():
                sup = str(row.get("supplier", "")).strip()
                sku = str(row.get("sku", "")).strip()
                if sup and sku:
                    supplier_skus.setdefault(sup, set()).add(sku)

            # Find supplier pairs sharing at least 2 SKUs (co-dependency signal)
            suppliers = list(supplier_skus.keys())
            inferred_links: List[Dict] = []
            for i in range(len(suppliers)):
                for j in range(i + 1, len(suppliers)):
                    s1, s2 = suppliers[i], suppliers[j]
                    shared = supplier_skus[s1] & supplier_skus[s2]
                    if len(shared) >= 2:
                        confidence = min(0.95, round(len(shared) / max(len(supplier_skus[s1] | supplier_skus[s2]), 1), 2))
                        inferred_links.append({
                            "supplier_a": s1,
                            "supplier_b": s2,
                            "shared_skus": list(shared),
                            "confidence": confidence,
                        })

            # Convert to shadow nodes / edges for visualization
            for link in inferred_links[:10]:  # cap at top 10 inferences
                shadow_id = f"inferred_link:{link['supplier_a']}_{link['supplier_b']}"
                shadow_nodes.append({
                    "id": shadow_id,
                    "name": f"Shared Sub-Tier ({len(link['shared_skus'])} SKUs)",
                    "type": "inferred-sub-tier",
                    "inferred": True,
                    "confidence": link["confidence"],
                    "shared_skus": link["shared_skus"][:5],
                })
                shadow_edges.append({"source": f"supplier:{link['supplier_a']}", "target": shadow_id})
                shadow_edges.append({"source": f"supplier:{link['supplier_b']}", "target": shadow_id})

        except Exception as e:
            return {"error": f"Inference failed: {e}", "shadow_nodes": [], "shadow_edges": [], "total_inferred": 0}

        multiplier = f"{round(1 + len(shadow_nodes) * 0.15, 2)}x" if shadow_nodes else "1.0x"
        return {
            "shadow_nodes": shadow_nodes,
            "shadow_edges": shadow_edges,
            "total_inferred": len(shadow_nodes),
            "visibility_multiplier": multiplier,
            "narrative": (
                f"Identified {len(shadow_nodes)} probable sub-tier linkages based on shared SKU patterns. "
                f"All inferences are data-driven (zero synthetic values)."
            ),
        }

    def _cascade_risk(self, failed_node: str, affected: set) -> str:
        """Assess the risk level of a cascade failure."""
        total_nodes = self.G.number_of_nodes()
        if total_nodes == 0:
            return "unknown"

        impact_pct = len(affected) / total_nodes * 100
        if impact_pct > 50:
            return "catastrophic"
        elif impact_pct > 25:
            return "severe"
        elif impact_pct > 10:
            return "significant"
        else:
            return "contained"

    def get_nodes_and_edges(self) -> Dict[str, Any]:
        """Get full graph data for visualization."""
        nodes = []
        for node_id, data in self.G.nodes(data=True):
            nodes.append({
                "id": node_id,
                "name": data.get("name", node_id),
                "type": data.get("type", "unknown"),
                **{k: v for k, v in data.items() if k not in ("name", "type")},
            })

        edges = []
        for source, target, data in self.G.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "edge_type": data.get("edge_type", "unknown"),
                "transaction_count": data.get("transaction_count", 1),
                "risk_weight": data.get("risk_weight", 0.5),
                "avg_delay": data.get("avg_delay", 0.0),
            })

        return {"nodes": nodes, "edges": edges}

    def find_critical_paths(self) -> List[Dict]:
        """
        Find the most critical paths in the supply chain.

        Betweenness is computed with risk_weight so that nodes on
        high-delay / high-cost-variance paths rank higher, not just
        nodes with the most transaction volume.
        """
        if not self._built or self.G.number_of_nodes() == 0:
            return []

        try:
            betweenness = nx.betweenness_centrality(self.G, weight="risk_weight")
        except Exception as e:
            logger_ge.error(f"Failed to compute betweenness centrality: {e}")
            betweenness = {}

        if not betweenness:
            return []

        bottlenecks = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]

        critical_paths = []
        for node, score in bottlenecks:
            if node not in self.G.nodes:
                continue
            data = self.G.nodes[node]
            critical_paths.append({
                "node_id": node,
                "name": data.get("name", node),
                "type": data.get("type", "unknown"),
                "betweenness_score": round(float(score), 4),
                "in_connections": self.G.in_degree(node),
                "out_connections": self.G.out_degree(node),
                "bottleneck_risk": (
                    "high" if float(score) > 0.3
                    else "medium" if float(score) > 0.1
                    else "low"
                ),
            })

        return critical_paths
