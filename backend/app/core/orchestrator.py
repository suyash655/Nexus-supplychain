"""
NEXUS — Analysis Pipeline Orchestrator
========================================
Extracted from main.py to isolate the heavy ML/Graph analysis pipeline
from the API request lifecycle. Each engine runs in its own try/except
so a single engine failure never crashes the full pipeline.
"""

import logging
import threading
import traceback
from datetime import datetime, timezone
from typing import Any, Optional, Dict

import pandas as pd  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.database import SessionLocal  # type: ignore
from app.models import SupplyData, AnalysisResult, WorldEvent  # type: ignore

logger = logging.getLogger("nexus.pipeline")

# ── Concurrency guard ──
_analysis_lock = threading.Lock()


def is_analyzing() -> bool:
    """Return True if a pipeline run is currently in progress."""
    return _analysis_lock.locked()


import os as _os
_MAX_ANALYSIS_ROWS: int = int(_os.getenv("MAX_ANALYSIS_ROWS", "100000"))

# ── Engine kwargs helper (for upload router) ──
# This is defined here to avoid circular import with main.py
_engine_kwargs_cache: Dict[str, Any] = {}

def set_engine_kwargs(**kwargs) -> None:
    """Set engine kwargs from main.py during startup."""
    global _engine_kwargs_cache
    _engine_kwargs_cache = kwargs

def _get_engine_kwargs() -> Dict[str, Any]:
    """Return current engine singletons as kwargs for the analysis orchestrator."""
    return _engine_kwargs_cache


def _load_dataframe(max_rows: int = _MAX_ANALYSIS_ROWS) -> pd.DataFrame:
    """
    Load the most recent `max_rows` supply records into a DataFrame.
    ORDER BY id DESC + LIMIT keeps RAM bounded regardless of table size.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(SupplyData)
            .order_by(SupplyData.id.desc())
            .limit(max_rows)
            .all()
        )
        if not rows:
            return pd.DataFrame()

        data = [
            {
                "id": r.id,
                "supplier": r.supplier,
                "sku": r.sku,
                "warehouse": r.warehouse,
                "region": r.region,
                "shipment_id": r.shipment_id,
                "order_date": r.order_date,
                "delivery_date": r.delivery_date,
                "delay_days": r.delay_days,
                "cost": r.cost,
                "quantity": r.quantity,
                "category": r.category,
                "quality_score": r.quality_score,
            }
            for r in rows
        ]
        df = pd.DataFrame(data)
        return df.iloc[::-1].reset_index(drop=True)
    except Exception:
        logger.exception("[NEXUS] Failed to load dataframe from database")
        return pd.DataFrame()
    finally:
        db.close()


def save_analysis_result(db: Session, analysis_type: str, result: Any) -> None:
    """Upsert analysis result into the database."""
    try:
        existing = db.query(AnalysisResult).filter(
            AnalysisResult.analysis_type == analysis_type
        ).first()
        if existing:
            existing.result_json = result
            existing.created_at = datetime.now(timezone.utc)
        else:
            db.add(AnalysisResult(analysis_type=analysis_type, result_json=result))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("[NEXUS] Failed to save analysis result: %s", analysis_type)


def get_analysis_result(db: Session, analysis_type: str, default: Any = None) -> Any:
    """Helper to retrieve latest analysis from DB."""
    res = db.query(AnalysisResult).filter(
        AnalysisResult.analysis_type == analysis_type
    ).first()
    return res.result_json if res else default


def run_full_analysis(
    *,
    ml_analyzer,
    graph_engine,
    ai_copilot,
    xai_engine,
    monte_carlo_engine,
    kpi_engine_instance,
) -> None:
    """
    Run the full multi-engine analysis pipeline.

    Protected by a threading.Lock — if a run is already in progress the call
    returns immediately instead of stacking concurrent heavy jobs.

    Engines that failed to initialise (None) are skipped with a warning log
    rather than raising AttributeError.

    Each engine stage has its own try/except with structured logging so a
    failure in one stage (e.g. ESG) does NOT prevent the others completing.
    """
    acquired = _analysis_lock.acquire(blocking=False)
    if not acquired:
        logger.warning("[NEXUS] Analysis already running — skipping duplicate trigger")
        return

    db = SessionLocal()
    start_time = datetime.now(timezone.utc)
    logger.info("[NEXUS] ► Analysis pipeline started at %s", start_time.isoformat())

    try:
        df = _load_dataframe()
        if df.empty:
            logger.warning("[NEXUS] No data to analyse — pipeline aborted")
            return

        logger.info("[NEXUS]   Loaded %d rows for analysis", len(df))

        # ── 1. ML Analysis ──
        ml_res: dict = {}
        if ml_analyzer is None:
            logger.warning("[NEXUS] ⚠ ML engine not available — skipping ML stage")
        else:
            try:
                ml_res = ml_analyzer.full_analysis(df)
                save_analysis_result(db, "ml", ml_res)
                logger.info("[NEXUS] ✓ ML analysis complete")
            except Exception:
                logger.exception("[NEXUS] ✗ ML analysis failed")

        # ── 2. Graph Analysis ──
        if graph_engine is None:
            logger.warning("[NEXUS] ⚠ Graph engine not available — skipping graph stage")
        else:
            try:
                graph_res = {
                    "summary": graph_engine.build_from_data(df),
                    "centrality": graph_engine.get_centrality_scores(),
                    "critical_paths": graph_engine.find_critical_paths(),
                    "visualization": graph_engine.get_nodes_and_edges(),
                    "resilience": graph_engine.get_resilience_metrics(),
                    "deep_tier": graph_engine.deep_tier_inference(df),
                }
                save_analysis_result(db, "graph", graph_res)
                logger.info("[NEXUS] ✓ Graph analysis complete")
            except Exception:
                logger.exception("[NEXUS] ✗ Graph analysis failed")

        # ── 3. XAI Analysis ──
        if xai_engine is None:
            logger.warning("[NEXUS] ⚠ XAI engine not available — skipping XAI stage")
        else:
            try:
                xai_res = {
                    "importance": xai_engine.compute_feature_importance(df),
                    "counterfactuals": xai_engine.generate_counterfactuals(
                        df, ml_res.get("risk_scores", []), graph_engine
                    ),
                }
                save_analysis_result(db, "xai", xai_res)
                logger.info("[NEXUS] ✓ XAI analysis complete")
            except Exception:
                logger.exception("[NEXUS] ✗ XAI analysis failed")

        # ── 4. AI Executive Summary ──
        if ai_copilot is None:
            logger.warning("[NEXUS] ⚠ AI Copilot not available — skipping executive summary")
        else:
            try:
                world_events = db.query(WorldEvent).filter(
                    WorldEvent.status == "ACTIVE"
                ).all()
                we_data = [
                    {
                        "title": e.title,
                        "description": e.description,
                        "severity": e.severity,
                        "region": e.region,
                    }
                    for e in world_events
                ]
                exec_res = ai_copilot.generate_executive_summary(
                    ml_res.get("summary", {}),
                    ml_res.get("risk_scores", []),
                    ml_res.get("anomalies", {}),
                )
                we_impact = ai_copilot.analyze_world_events(
                    we_data, ml_res.get("risk_scores", [])
                )
                save_analysis_result(db, "executive", exec_res)
                save_analysis_result(db, "world_event_impact", we_impact)
                logger.info("[NEXUS] ✓ Executive summary complete")
            except Exception:
                logger.exception("[NEXUS] ✗ Executive summary failed")

        # ── 5. Monte Carlo ──
        if monte_carlo_engine is None:
            logger.warning("[NEXUS] ⚠ Monte Carlo engine not available — skipping")
        else:
            try:
                monte_carlo_engine.fit(df)
                logger.info("[NEXUS] ✓ Monte Carlo engine fitted")
            except Exception:
                logger.exception("[NEXUS] ✗ Monte Carlo fitting failed")

        # ── 7. KPI Computation ──
        if kpi_engine_instance is None:
            logger.warning("[NEXUS] ⚠ KPI engine not available — skipping")
        else:
            try:
                kpi_res = kpi_engine_instance.compute_all_kpis(
                    df,
                    risk_scores=ml_res.get("risk_scores", []),
                    anomalies=ml_res.get("anomalies", {}),
                )
                save_analysis_result(db, "kpis", kpi_res)
                logger.info("[NEXUS] ✓ KPI computation complete")
            except Exception:
                logger.exception("[NEXUS] ✗ KPI computation failed")

        # ── 8. Agentic Mitigation Trigger ──
        try:
            from agent.mitigation_graph import trigger_mitigation, CRITICAL_THRESHOLD
            for score_data in ml_res.get("risk_scores", []):
                supplier = score_data.get("supplier")
                score = score_data.get("risk_score", 0)
                if score >= CRITICAL_THRESHOLD:
                    # Pass the graph_res if it was created successfully, else None
                    g_data = graph_res.get("visualization") if 'graph_res' in locals() else None
                    trigger_mitigation(
                        supplier=supplier,
                        risk_score=score,
                        risk_data=score_data,
                        graph_data=g_data,
                        sku=None
                    )
            logger.info("[NEXUS] ✓ Agentic mitigation triggers evaluated")
        except Exception:
            logger.exception("[NEXUS] ✗ Agentic mitigation trigger failed")

    except Exception:
        logger.exception("[NEXUS] ✗ Analysis pipeline fatal error")
    finally:
        db.close()
        _analysis_lock.release()
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info("[NEXUS] ◄ Pipeline finished in %.1fs", elapsed)

