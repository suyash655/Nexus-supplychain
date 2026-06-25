"""
NEXUS — Graph Router
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Query, Depends, HTTPException  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.dependencies import get_db, require_auth  # type: ignore
from app.core.orchestrator import get_analysis_result, _load_dataframe  # type: ignore
from app.engines.graph_engine import SupplyChainGraph  # type: ignore

router = APIRouter(prefix="/graph", tags=["Graph"])


def _rebuild_graph(graph_res) -> SupplyChainGraph:
    """Rebuild a SupplyChainGraph from cached visualization data."""
    g = SupplyChainGraph()
    nodes = graph_res.get("visualization", {}).get("nodes", [])
    edges = graph_res.get("visualization", {}).get("edges", [])
    g._built = True
    for n in nodes:
        g.G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in edges:
        g.G.add_edge(e["source"], e["target"], **{k: v for k, v in e.items() if k not in ("source", "target")})
    return g


@router.get("/summary")
def graph_summary(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get graph overview statistics."""
    graph_res = get_analysis_result(db, "graph")
    if graph_res:
        return graph_res["summary"]
    return {"total_nodes": 0, "total_edges": 0}


@router.get("/resilience")
def graph_resilience(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get advanced resilience metrics."""
    graph_res = get_analysis_result(db, "graph")
    if graph_res:
        return graph_res.get("resilience", {})
    return {}


@router.get("/centrality")
def graph_centrality(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get node centrality scores."""
    graph_res = get_analysis_result(db, "graph")
    if graph_res:
        return graph_res["centrality"]
    return {"degree": [], "betweenness": [], "pagerank": []}


@router.get("/critical-paths")
def critical_paths(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Get critical bottleneck nodes."""
    graph_res = get_analysis_result(db, "graph")
    data = graph_res["critical_paths"] if graph_res else []
    return {
        "data": data[skip : skip + limit],
        "total": len(data),
        "skip": skip,
        "limit": limit,
    }


@router.get("/visualization")
def graph_visualization(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get full graph data for frontend visualization."""
    graph_res = get_analysis_result(db, "graph")
    if graph_res:
        return graph_res["visualization"]
    return {"nodes": [], "edges": []}


@router.get("/simulate")
def graph_simulation(
    node_id: Optional[str] = None,
    node_ids: Optional[str] = None,
    db: Session = Depends(get_db), user: dict = Depends(require_auth),
):
    """Simulate supply chain disruption (Digital Twin)."""
    graph_res = get_analysis_result(db, "graph")
    if not graph_res:
        return {"error": "No analysis available"}

    targets = []
    if node_ids:
        targets = node_ids.split(",")
    elif node_id:
        targets = [node_id]

    if not targets:
        return {"error": "No target nodes provided"}

    g = _rebuild_graph(graph_res)
    return g.simulate_cascade(targets)


@router.get("/deep-inference")
def deep_inference(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Reveal hidden Tier 3-5 suppliers (Shadow Nodes)."""
    graph_res = get_analysis_result(db, "graph")
    if not graph_res:
        return {"error": "Graph not built yet"}

    g = _rebuild_graph(graph_res)
    return g.deep_tier_inference()


# ── Temporal Graph (T-GNN) ──

@router.get("/temporal-analysis")
def temporal_analysis(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Analyze how supply chain relationships evolve over time."""
    from app.main import engines  # type: ignore
    tgnn = engines.tgnn_engine_instance
    if not tgnn:
        raise HTTPException(status_code=503, detail="Temporal trend engine unavailable.")
    if not tgnn._fitted:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available.")
        fit_result = tgnn.fit(df)
        if "error" in fit_result:
            raise HTTPException(status_code=400, detail=fit_result["error"])
    return tgnn.analyze_temporal_patterns()


@router.get("/predict-evolution")
def predict_evolution(periods: int = Query(3, ge=1, le=12), db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Predict future supply chain network topology changes."""
    from app.main import engines  # type: ignore
    tgnn = engines.tgnn_engine_instance
    if not tgnn:
        raise HTTPException(status_code=503, detail="Temporal trend engine unavailable.")
    if not tgnn._fitted:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available.")
        tgnn.fit(df)
    return tgnn.predict_evolution(periods)


@router.get("/temporal-risk")
def temporal_risk_scores(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Get trajectory-aware risk scores."""
    from app.main import engines  # type: ignore
    tgnn = engines.tgnn_engine_instance
    if not tgnn:
        raise HTTPException(status_code=503, detail="Temporal trend engine unavailable.")
    if not tgnn._fitted:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available.")
        tgnn.fit(df)
    return tgnn.get_temporal_risk_scores()


# ── Monte Carlo ──

@router.post("/simulate-monte-carlo")
def monte_carlo_simulation(
    node_ids: List[str] = Query(..., alias="nodes"),
    severity: float = Query(0.5, ge=0.0, le=1.0),
    num_trials: int = Query(1000, ge=100, le=10000),
    db: Session = Depends(get_db), user: dict = Depends(require_auth),
):
    """Run Monte Carlo probabilistic disruption simulation."""
    from app.main import engines  # type: ignore
    mc = engines.monte_carlo_engine
    if not mc:
        raise HTTPException(status_code=503, detail="Monte Carlo engine unavailable.")
    if not mc._fitted:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No supply chain data available.")
        mc.fit(df)
    return mc.simulate_disruption(
        target_suppliers=node_ids,
        disruption_severity=severity,
        num_trials=num_trials,
    )


@router.post("/compare-scenarios")
def compare_scenarios(
    scenarios: List[Dict[str, Any]],
    num_trials: int = Query(1000, ge=100, le=10000),
    db: Session = Depends(get_db), user: dict = Depends(require_auth),
):
    """Compare multiple what-if disruption scenarios side by side."""
    from app.main import engines  # type: ignore
    mc = engines.monte_carlo_engine
    if not mc:
        raise HTTPException(status_code=503, detail="Monte Carlo engine unavailable.")
    if not mc._fitted:
        df = _load_dataframe()
        if df.empty:
            raise HTTPException(status_code=400, detail="No supply chain data available.")
        mc.fit(df)
    return mc.compare_scenarios(scenarios, num_trials)
