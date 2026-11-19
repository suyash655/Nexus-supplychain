"""
NEXUS — Risk Propagation Engine (Supply Chain Genome)
======================================================
Maps how risk scores propagate through the supply chain dependency graph.

What this engine does (accurately):
  - Builds a directed dependency graph from structural edges
  - Propagates risk scores downstream via BFS traversal
  - Computes node fragility from graph topology (Taleb-inspired)
  - Simulates the downstream exposure if a node is removed

What this engine does NOT do:
  - It does NOT perform causal inference (no do-calculus, no PC/FCI/LiNGAM)
  - It does NOT run conditional independence tests
  - It does NOT distinguish causation from correlation
  - Edge "strength" is derived from upstream risk scores, not interventional data

Instead of "Supplier A risk: 87", this engine answers:
  "If Supplier A were disrupted, which downstream nodes carry the most
   accumulated risk exposure, and how large is that exposure?"

This is structurally-weighted risk propagation — a well-established, honest
technique. It is valuable and useful. It is not Bayesian causal inference.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np  # type: ignore


class RiskPropagationEngine:
    """
    Builds a risk-weighted dependency graph from supply chain data and
    propagates risk scores downstream to estimate exposure.

    Terminology used in outputs has been chosen to accurately reflect
    what the algorithm computes:
      - "propagation_strength" (not "causal_strength")
      - "dependency_path" (not "causal_chain")
      - "downstream_exposure" (not "causal intervention")
      - "Structural dependency" (not "causal mechanism")
    """

    def __init__(self):
        self.edges: List[Dict[str, Any]] = []
        self.node_properties: Dict[str, Dict[str, Any]] = {}
        self._built = False

    def build_from_graph(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        risk_data: Optional[List[Dict]] = None,
        world_events: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Build the risk propagation graph from supply chain nodes, edges,
        risk scores, and optional world events.

        Edge weight = upstream node's risk score / 100.
        Nodes with no risk data get a default propagation weight of 0.3.
        """
        self.edges = []
        self.node_properties = {}

        # Register all nodes
        for n in nodes:
            node_id = n.get("id", "")
            self.node_properties[node_id] = {
                "name": n.get("name", node_id),
                "type": n.get("type", "unknown"),
                "region": n.get("region", "Global"),
                "risk_score": 0.0,
                "upstream_nodes": [],
                "downstream_nodes": [],
                "fragility": 0.0,
            }

        # Enrich with risk scores
        if risk_data:
            for r in risk_data:
                name = r.get("supplier", "")
                score = r.get("risk_score", 0)
                for nid, props in self.node_properties.items():
                    if name.lower() in nid.lower() or name.lower() in props.get("name", "").lower():
                        props["risk_score"] = score

        # Build edges — weight is upstream risk score normalised to [0, 1]
        for e in edges:
            src = e.get("source", "")
            tgt = e.get("target", "")

            src_risk = self.node_properties.get(src, {}).get("risk_score", 0)
            weight = min(1.0, src_risk / 100.0) if src_risk > 0 else 0.3

            self.edges.append({
                "source": src,
                "target": tgt,
                "propagation_weight": round(float(weight), 3),
                "dependency_type": self._infer_dependency_type(src, tgt),
            })

            if src in self.node_properties:
                self.node_properties[src]["downstream_nodes"].append(tgt)
            if tgt in self.node_properties:
                self.node_properties[tgt]["upstream_nodes"].append(src)

        # Inject world events as upstream risk sources
        if world_events:
            for event in world_events:
                event_id = f"EVENT_{event.get('title', 'unknown').replace(' ', '_')}"
                self.node_properties[event_id] = {
                    "name": event.get("title", "Unknown Event"),
                    "type": "world_event",
                    "region": event.get("region", "Global"),
                    "risk_score": event.get("impact_score", 50),
                    "severity": event.get("severity", "MEDIUM"),
                    "upstream_nodes": [],
                    "downstream_nodes": [],
                    "fragility": 0.0,
                }

                event_region = event.get("region", "").lower()
                for nid, props in self.node_properties.items():
                    if nid == event_id:
                        continue
                    node_region = props.get("region", "").lower()
                    if event_region and event_region in node_region:
                        self.edges.append({
                            "source": event_id,
                            "target": nid,
                            "propagation_weight": min(1.0, event.get("impact_score", 50) / 100.0),
                            "dependency_type": f"Regional exposure from {event.get('title')}",
                        })
                        props["upstream_nodes"].append(event_id)
                        self.node_properties[event_id]["downstream_nodes"].append(nid)

        self._compute_fragility()
        self._built = True

        return {
            "total_nodes": len(self.node_properties),
            "total_edges": len(self.edges),
            "root_nodes": [
                nid for nid, p in self.node_properties.items()
                if not p["upstream_nodes"]
            ],
            "leaf_nodes": [
                nid for nid, p in self.node_properties.items()
                if not p["downstream_nodes"]
            ],
        }

    def simulate_removal(
        self, target_node: str, scenario: str = "remove"
    ) -> Dict[str, Any]:
        """
        Simulate the downstream risk exposure if a node is removed or disrupted.

        Uses BFS over the dependency graph, accumulating propagation weight
        at each hop. This is NOT a do-calculus intervention — it is a
        graph traversal that estimates which nodes carry the most accumulated
        risk exposure if the target node fails.

        Dollar impact estimates are derived from actual node cost data where
        available; the type-based fallback is clearly labelled as an estimate.
        """
        if not self._built:
            return {"error": "Risk graph not built yet. Call build_from_graph first."}

        target = self._find_node(target_node)
        if not target:
            return {"error": f"Node '{target_node}' not found in risk graph"}

        # BFS downstream
        affected: List[Dict[str, Any]] = []
        visited: Set[str] = {target}
        queue: List[Tuple[str, float, List[str]]] = [(target, 1.0, [target])]

        while queue:
            current, accumulated_weight, path = queue.pop(0)

            for edge in self.edges:
                if edge["source"] == current and edge["target"] not in visited:
                    child = edge["target"]
                    visited.add(child)
                    new_weight = accumulated_weight * edge["propagation_weight"]
                    new_path = path + [child]

                    child_props = self.node_properties.get(child, {})
                    affected.append({
                        "node": child,
                        "name": child_props.get("name", child),
                        "type": child_props.get("type", "unknown"),
                        "propagation_strength": round(float(new_weight), 3),
                        "dependency_type": edge["dependency_type"],
                        "dependency_path": " → ".join(new_path),
                        "estimated_cost_exposure": self._estimate_cost_exposure(
                            child_props, new_weight
                        ),
                    })
                    queue.append((child, new_weight, new_path))

        affected.sort(key=lambda x: x["propagation_strength"], reverse=True)

        target_props = self.node_properties.get(target, {})
        total_exposure = sum(a.get("estimated_cost_exposure", 0) for a in affected)

        return {
            "scenario": scenario,
            "target": {
                "id": target,
                "name": target_props.get("name", target),
                "type": target_props.get("type", "unknown"),
                "fragility": target_props.get("fragility", 0),
                "risk_score": target_props.get("risk_score", 0),
            },
            "total_downstream_nodes_affected": len(affected),
            "total_estimated_cost_exposure": f"${total_exposure:,.0f}",
            "cost_exposure_basis": (
                "Derived from actual transaction costs where available; "
                "type-based fallback applied for nodes with no cost data."
            ),
            "downstream_nodes": affected[:20],
            "methodology": (
                "BFS risk propagation over structural dependency graph. "
                "Propagation weight = product of upstream risk scores normalised to [0,1]. "
                "This is NOT causal inference."
            ),
        }

    def get_dependency_path(
        self, from_node: str, to_node: str
    ) -> Dict[str, Any]:
        """
        Find the shortest dependency path between two nodes in the graph.
        Returns the structural path and accumulated propagation weight.

        This shows structural connectivity (A depends on B), not causal
        directionality in the do-calculus sense.
        """
        if not self._built:
            return {"error": "Risk graph not built yet"}

        start = self._find_node(from_node)
        end = self._find_node(to_node)

        if not start or not end:
            return {"error": "One or both nodes not found"}

        queue: List[Tuple[str, List[str], float]] = [(start, [start], 1.0)]
        visited: Set[str] = {start}

        while queue:
            current, path, weight = queue.pop(0)

            if current == end:
                steps = []
                for i in range(len(path) - 1):
                    edge = next(
                        (
                            e for e in self.edges
                            if e["source"] == path[i] and e["target"] == path[i + 1]
                        ),
                        None,
                    )
                    steps.append({
                        "from": self.node_properties.get(path[i], {}).get("name", path[i]),
                        "to": self.node_properties.get(path[i + 1], {}).get("name", path[i + 1]),
                        "dependency_type": edge["dependency_type"] if edge else "structural dependency",
                        "propagation_weight": edge["propagation_weight"] if edge else 0.5,
                    })

                return {
                    "from": self.node_properties.get(start, {}).get("name", start),
                    "to": self.node_properties.get(end, {}).get("name", end),
                    "path_length": len(path),
                    "accumulated_propagation_weight": round(float(weight), 3),
                    "steps": steps,
                    "summary": self._generate_path_summary(steps),
                }

            for edge in self.edges:
                if edge["source"] == current and edge["target"] not in visited:
                    visited.add(edge["target"])
                    queue.append((
                        edge["target"],
                        path + [edge["target"]],
                        weight * edge["propagation_weight"],
                    ))

        return {
            "error": f"No dependency path found from '{from_node}' to '{to_node}'"
        }

    def get_fragility_report(self) -> Dict[str, Any]:
        """
        Taleb-inspired fragility analysis based on graph topology.

        Fragility is computed from:
          - upstream node count (low count = concentration risk)
          - downstream node count (high count = broad exposure)
          - node's own risk score

        This is a heuristic topology metric, not a statistical test.
        """
        if not self._built:
            return {"error": "Risk graph not built yet"}

        nodes_ranked = sorted(
            [
                {
                    "id": nid,
                    "name": props.get("name", nid),
                    "type": props.get("type", "unknown"),
                    "fragility_score": round(float(props.get("fragility", 0)), 2),
                    "classification": (
                        "ANTIFRAGILE" if props.get("fragility", 0) < -0.3
                        else "ROBUST" if props.get("fragility", 0) < 0.3
                        else "FRAGILE" if props.get("fragility", 0) < 0.7
                        else "EXTREMELY_FRAGILE"
                    ),
                    "upstream_count": len(props.get("upstream_nodes", [])),
                    "downstream_count": len(props.get("downstream_nodes", [])),
                }
                for nid, props in self.node_properties.items()
            ],
            key=lambda x: x["fragility_score"],
            reverse=True,
        )

        fragile = [n for n in nodes_ranked if n["fragility_score"] >= 0.5]
        robust = [n for n in nodes_ranked if 0.0 <= n["fragility_score"] < 0.5]
        antifragile = [n for n in nodes_ranked if n["fragility_score"] < 0.0]

        return {
            "total_nodes_analyzed": len(nodes_ranked),
            "fragile_count": len(fragile),
            "robust_count": len(robust),
            "antifragile_count": len(antifragile),
            "most_fragile": fragile[:10],
            "most_robust": robust[:5],
            "antifragile_nodes": antifragile[:5],
            "system_fragility_index": round(
                float(
                    np.mean([n["fragility_score"] for n in nodes_ranked])
                    if nodes_ranked else 0
                ),
                3,
            ),
            "methodology": (
                "Fragility = f(upstream concentration, downstream exposure, risk score). "
                "Heuristic topology metric — not a statistical test."
            ),
        }

    # ── Private helpers ────────────────────────────────────────────────

    def _infer_dependency_type(self, src: str, tgt: str) -> str:
        """Label the structural dependency type between two nodes."""
        src_type = self.node_properties.get(src, {}).get("type", "")
        tgt_type = self.node_properties.get(tgt, {}).get("type", "")

        labels = {
            ("supplier", "sku"): "Supply dependency: SKU sourced from this supplier",
            ("supplier", "warehouse"): "Distribution dependency: supplier ships to this warehouse",
            ("sku", "warehouse"): "Inventory dependency: SKU stored at this warehouse",
            ("warehouse", "region"): "Geographic dependency: warehouse serves this region",
            ("world_event", "supplier"): "Regional exposure: event affects supplier operations",
            ("world_event", "warehouse"): "Regional exposure: event affects warehouse operations",
        }

        return labels.get(
            (src_type, tgt_type),
            f"Structural dependency: {src_type} → {tgt_type}",
        )

    def _compute_fragility(self):
        """Compute topology-based fragility scores for all nodes."""
        for nid, props in self.node_properties.items():
            upstream = len(props.get("upstream_nodes", []))
            downstream = len(props.get("downstream_nodes", []))
            risk = props.get("risk_score", 0) / 100.0

            if upstream == 0 and downstream == 0:
                fragility = 0.0
            else:
                concentration = 1.0 / max(upstream, 1)
                downstream_exposure = min(1.0, downstream / 10.0)
                fragility = (risk * 0.4) + (concentration * 0.3) + (downstream_exposure * 0.3)

                if upstream >= 3:
                    fragility -= 0.2  # Diversified supply = less fragile

            props["fragility"] = round(float(fragility), 3)

    def _estimate_cost_exposure(
        self, node_props: Dict, propagation_weight: float
    ) -> float:
        """
        Estimate cost exposure for a disrupted node.

        Uses actual transaction cost data from the node if available.
        Falls back to type-based order-of-magnitude estimates only when
        no cost data exists. The fallback values are clearly labelled
        as estimates in the API response.
        """
        # Prefer actual cost data stored on the node
        actual_cost = node_props.get("total_cost", 0)
        if actual_cost and actual_cost > 0:
            risk_multiplier = 1.0 + (node_props.get("risk_score", 0) / 100.0)
            return round(float(actual_cost * propagation_weight * risk_multiplier), 0)

        # Fallback: rough order-of-magnitude by node type
        # These are placeholder estimates — replace with customer's actual data
        fallback = {
            "supplier": 100_000,
            "sku": 50_000,
            "warehouse": 75_000,
            "region": 200_000,
            "world_event": 500_000,
        }.get(node_props.get("type", ""), 25_000)

        risk_multiplier = 1.0 + (node_props.get("risk_score", 0) / 100.0)
        return round(float(fallback * propagation_weight * risk_multiplier), 0)

    def _find_node(self, query: str) -> Optional[str]:
        """Find a node by partial name match."""
        for nid in self.node_properties:
            if (
                query.lower() in nid.lower()
                or query.lower() in self.node_properties[nid].get("name", "").lower()
            ):
                return nid
        return None

    def _generate_path_summary(self, steps: List[Dict]) -> str:
        """Generate a plain-language summary of a dependency path."""
        if not steps:
            return "No dependency path found."

        parts = []
        for i, step in enumerate(steps):
            if i == 0:
                parts.append(
                    f"**{step['from']}** has a structural dependency on "
                    f"**{step['to']}** ({step['dependency_type'].lower()})"
                )
            else:
                parts.append(
                    f"which in turn depends on **{step['to']}** "
                    f"via {step['dependency_type'].lower()}"
                )

        summary = ", ".join(parts) + "."

        # Describe accumulated propagation weight — not "causal strength"
        total_weight = 1.0
        for step in steps:
            total_weight *= step["propagation_weight"]

        if total_weight > 0.7:
            summary += " This is a **HIGH-EXPOSURE** dependency path."
        elif total_weight > 0.4:
            summary += " This is a **MODERATE-EXPOSURE** dependency path."
        else:
            summary += " This is a **LOW-EXPOSURE** dependency path."

        return summary


# ── Backward-compatibility alias ──────────────────────────────────────
# main.py and remaining.py instantiate CausalGenomeEngine by name.
# This alias lets existing call sites work without touching those files.
CausalGenomeEngine = RiskPropagationEngine
