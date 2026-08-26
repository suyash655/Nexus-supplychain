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

# ── Demo graph data (used when no analysis has been run yet) ──
_DEMO_GRAPH_VISUALIZATION = {
    "nodes": [
        {"id": "supplier:Apex Materials",  "type": "supplier",  "name": "Apex Materials",  "shipments": 187, "avg_delay": 8.3,  "total_cost": 892000},
        {"id": "supplier:GlobalTech Co",   "type": "supplier",  "name": "GlobalTech Co",   "shipments": 142, "avg_delay": 6.9,  "total_cost": 654000},
        {"id": "supplier:SteelMax Inc",    "type": "supplier",  "name": "SteelMax Inc",    "shipments": 98,  "avg_delay": 5.2,  "total_cost": 521000},
        {"id": "supplier:ProLogix Asia",   "type": "supplier",  "name": "ProLogix Asia",   "shipments": 221, "avg_delay": 4.8,  "total_cost": 780000},
        {"id": "supplier:NorthStar Parts", "type": "supplier",  "name": "NorthStar Parts", "shipments": 167, "avg_delay": 4.1,  "total_cost": 445000},
        {"id": "supplier:Delta Logistics", "type": "supplier",  "name": "Delta Logistics", "shipments": 312, "avg_delay": 2.8,  "total_cost": 356000},
        {"id": "supplier:QuickShip Pro",   "type": "supplier",  "name": "QuickShip Pro",   "shipments": 445, "avg_delay": 1.2,  "total_cost": 178000},
        {"id": "sku:SKU-A001", "type": "sku", "name": "SKU-A001", "volume": 234},
        {"id": "sku:SKU-B002", "type": "sku", "name": "SKU-B002", "volume": 189},
        {"id": "sku:SKU-C003", "type": "sku", "name": "SKU-C003", "volume": 156},
        {"id": "sku:SKU-D004", "type": "sku", "name": "SKU-D004", "volume": 201},
        {"id": "sku:SKU-E005", "type": "sku", "name": "SKU-E005", "volume": 143},
        {"id": "warehouse:WH-Mumbai",    "type": "warehouse", "name": "WH-Mumbai",    "throughput": 412},
        {"id": "warehouse:WH-Singapore", "type": "warehouse", "name": "WH-Singapore", "throughput": 298},
        {"id": "warehouse:WH-Frankfurt", "type": "warehouse", "name": "WH-Frankfurt", "throughput": 187},
        {"id": "region:Asia-Pacific", "type": "region", "name": "Asia-Pacific", "activity": 523},
        {"id": "region:Europe",       "type": "region", "name": "Europe",       "activity": 289},
        {"id": "region:Americas",     "type": "region", "name": "Americas",     "activity": 198},
    ],
    "edges": [
        {"source": "supplier:Apex Materials",  "target": "sku:SKU-A001", "weight": 1.8, "edge_type": "supply"},
        {"source": "supplier:Apex Materials",  "target": "sku:SKU-B002", "weight": 1.5, "edge_type": "supply"},
        {"source": "supplier:GlobalTech Co",   "target": "sku:SKU-B002", "weight": 1.4, "edge_type": "supply"},
        {"source": "supplier:GlobalTech Co",   "target": "sku:SKU-C003", "weight": 1.2, "edge_type": "supply"},
        {"source": "supplier:SteelMax Inc",    "target": "sku:SKU-C003", "weight": 1.1, "edge_type": "supply"},
        {"source": "supplier:SteelMax Inc",    "target": "sku:SKU-D004", "weight": 0.9, "edge_type": "supply"},
        {"source": "supplier:ProLogix Asia",   "target": "sku:SKU-A001", "weight": 1.0, "edge_type": "supply"},
        {"source": "supplier:ProLogix Asia",   "target": "sku:SKU-E005", "weight": 1.3, "edge_type": "supply"},
        {"source": "supplier:NorthStar Parts", "target": "sku:SKU-D004", "weight": 0.8, "edge_type": "supply"},
        {"source": "supplier:Delta Logistics", "target": "sku:SKU-E005", "weight": 0.6, "edge_type": "supply"},
        {"source": "supplier:QuickShip Pro",   "target": "sku:SKU-A001", "weight": 0.4, "edge_type": "supply"},
        {"source": "sku:SKU-A001", "target": "warehouse:WH-Mumbai",    "weight": 1.2, "edge_type": "storage"},
        {"source": "sku:SKU-B002", "target": "warehouse:WH-Singapore", "weight": 1.0, "edge_type": "storage"},
        {"source": "sku:SKU-C003", "target": "warehouse:WH-Frankfurt", "weight": 0.9, "edge_type": "storage"},
        {"source": "sku:SKU-D004", "target": "warehouse:WH-Mumbai",    "weight": 0.8, "edge_type": "storage"},
        {"source": "sku:SKU-E005", "target": "warehouse:WH-Singapore", "weight": 1.1, "edge_type": "storage"},
        {"source": "warehouse:WH-Mumbai",    "target": "region:Asia-Pacific", "weight": 1.5, "edge_type": "distribution"},
        {"source": "warehouse:WH-Singapore", "target": "region:Asia-Pacific", "weight": 1.2, "edge_type": "distribution"},
        {"source": "warehouse:WH-Frankfurt", "target": "region:Europe",       "weight": 1.3, "edge_type": "distribution"},
        {"source": "warehouse:WH-Mumbai",    "target": "region:Americas",     "weight": 0.7, "edge_type": "distribution"},
    ],
}


def _rebuild_graph(graph_res) -> SupplyChainGraph:
    """
    Rebuild a SupplyChainGraph from cached visualization data.
    WARNING: This is a lossy round-trip. Internal metadata such as
    `_cost_samples` is lost after serialization.
    """
    g = SupplyChainGraph()
    nodes = graph_res.get("visualization", {}).get("nodes", [])
    edges = graph_res.get("visualization", {}).get("edges", [])
    g._built = True
    for n in nodes:
        g.G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in edges:
        g.G.add_edge(e["source"], e["target"], **{k: v for k, v in e.items() if k not in ("source", "target")})
    return g


@router.get("/demo")
def graph_demo(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """
    Return demo/fallback graph visualization data.
    Used by the frontend when no real graph analysis is available yet.
    """
    return _DEMO_GRAPH_VISUALIZATION


@router.get("/status")
def graph_status(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """
    Return whether real graph data is available.
    Allows the frontend to poll until analysis completes.
    """
    from app.core.orchestrator import is_analyzing  # type: ignore
    graph_res = get_analysis_result(db, "graph")
    has_real_data = graph_res is not None and len(graph_res.get("visualization", {}).get("nodes", [])) > 0
    return {
        "has_real_data": has_real_data,
        "is_analyzing": is_analyzing(),
        "node_count": len(graph_res.get("visualization", {}).get("nodes", [])) if graph_res else 0,
    }


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
    df = _load_dataframe()
    if df.empty:
        return {"error": "No data available for deep-tier inference"}
    return g.deep_tier_inference(df)


# ── Temporal Trend Engine (legacy TGNNEngine alias) ──

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


# ── Scenario History (Failure Simulations) ──

@router.post("/simulate-failure")
def simulate_failure(
    body: Dict[str, str],
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """
    Simulate failure of a specific node, returning a diff of network centrality 
    and cascading effects. Stores the run in the database.
    """
    node_id = body.get("node_id")
    if not node_id:
        raise HTTPException(status_code=400, detail="node_id is required")

    graph_res = get_analysis_result(db, "graph")
    if not graph_res:
        raise HTTPException(status_code=400, detail="No graph analysis available")

    g = _rebuild_graph(graph_res)
    result = g.simulate_failure(node_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    from app.models.supply import ScenarioRun
    import uuid
    run_id = str(uuid.uuid4())
    run = ScenarioRun(
        run_id=run_id,
        node_id=result["node_id"],
        node_name=result["node_name"],
        node_type=result["node_type"],
        pre_betweenness=result["pre_betweenness"],
        post_betweenness=result["post_betweenness"],
        pre_pagerank=result["pre_pagerank"],
        post_pagerank=result["post_pagerank"],
        newly_critical_nodes=result["newly_critical_nodes"],
        unreachable_skus=result["unreachable_skus"],
        affected_regions=result["affected_regions"],
        cascade_result=result["cascade_result"],
        total_affected=result["total_affected"],
        risk_assessment=result["risk_assessment"],
        created_by="system",
    )
    db.add(run)
    db.commit()

    return {"run_id": run_id, "diff": result}


@router.get("/scenario-runs")
def list_scenario_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Get a history of simulated failure scenarios."""
    from app.models.supply import ScenarioRun
    graph_res = get_analysis_result(db, "graph")
    current_node_ids = {
        node.get("id")
        for node in (graph_res or {}).get("visualization", {}).get("nodes", [])
        if node.get("id")
    }

    q = db.query(ScenarioRun).order_by(ScenarioRun.created_at.desc())
    if current_node_ids:
        q = q.filter(ScenarioRun.node_id.in_(current_node_ids))
    total = q.count()
    runs = q.offset(skip).limit(limit).all()

    return {
        "total": total,
        "runs": [
            {
                "id": r.id,
                "run_id": r.run_id,
                "node_id": r.node_id,
                "node_name": r.node_name,
                "node_type": r.node_type,
                "total_affected": r.total_affected,
                "risk_assessment": r.risk_assessment,
                "newly_critical_nodes": r.newly_critical_nodes,
                "unreachable_skus": r.unreachable_skus,
                "affected_regions": r.affected_regions,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "created_by": r.created_by,
            }
            for r in runs
        ]
    }

