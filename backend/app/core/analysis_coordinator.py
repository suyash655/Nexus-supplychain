"""
NEXUS — Progressive Analysis Coordinator
========================================
A resilient, logically-flowing analysis system with:
- Progressive analysis stages (quick → comprehensive)
- Dependency management between stages
- Progress tracking and status updates
- Retry logic with graceful degradation
- Smart sampling for representative results
"""

import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.analysis_coordinator")


class AnalysisStage(Enum):
    """Analysis stages in logical dependency order"""
    VALIDATION = "validation"
    BASIC_STATS = "basic_stats"
    SAMPLE_ML = "sample_ml"
    FULL_ML = "full_ml"
    GRAPH = "graph"
    XAI = "xai"
    EXECUTIVE = "executive"
    MONTE_CARLO = "monte_carlo"
    KPI = "kpi"


@dataclass
class StageResult:
    """Result of an analysis stage"""
    stage: AnalysisStage
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0


@dataclass
class AnalysisProgress:
    """Overall analysis progress tracking"""
    upload_id: str
    total_stages: int = 0
    completed_stages: int = 0
    current_stage: Optional[AnalysisStage] = None
    stage_results: Dict[AnalysisStage, StageResult] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed, partial


class AnalysisCoordinator:
    """
    Coordinates progressive analysis with dependency management and resilience.
    
    Analysis Flow:
    1. VALIDATION → Check data quality and basic validation
    2. BASIC_STATS → Compute basic statistics (instant)
    3. SAMPLE_ML → ML analysis on sample (fast, representative)
    4. FULL_ML → Full ML analysis (comprehensive)
    5. GRAPH → Graph analysis (depends on ML results)
    6. XAI → Explainable AI (depends on ML + Graph)
    7. EXECUTIVE → Executive summary (depends on all previous)
    8. MONTE_CARLO → Monte Carlo simulation (independent)
    9. KPI → KPI computation (depends on ML results)
    """
    
    # Dependency graph: stage -> list of stages it depends on
    DEPENDENCIES = {
        AnalysisStage.VALIDATION: [],
        AnalysisStage.BASIC_STATS: [AnalysisStage.VALIDATION],
        AnalysisStage.SAMPLE_ML: [AnalysisStage.BASIC_STATS],
        AnalysisStage.FULL_ML: [AnalysisStage.SAMPLE_ML],
        AnalysisStage.GRAPH: [AnalysisStage.FULL_ML],
        AnalysisStage.XAI: [AnalysisStage.GRAPH, AnalysisStage.FULL_ML],
        AnalysisStage.EXECUTIVE: [AnalysisStage.XAI, AnalysisStage.KPI],
        AnalysisStage.MONTE_CARLO: [AnalysisStage.BASIC_STATS],
        AnalysisStage.KPI: [AnalysisStage.FULL_ML],
    }
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self):
        self._progress: Dict[str, AnalysisProgress] = {}
        self._lock = threading.Lock()
        self._active_analyses: Dict[str, bool] = {}
    
    def start_analysis(self, upload_id: str, df, engines: Dict[str, Any]) -> str:
        """Start progressive analysis for an upload"""
        with self._lock:
            if upload_id in self._active_analyses:
                logger.warning(f"[NEXUS] Analysis already running for {upload_id}")
                return upload_id
            
            self._active_analyses[upload_id] = True
            progress = AnalysisProgress(
                upload_id=upload_id,
                total_stages=len(AnalysisStage),
                start_time=datetime.now(timezone.utc),
                status="running"
            )
            self._progress[upload_id] = progress
        
        # Run analysis in background thread
        thread = threading.Thread(
            target=self._run_progressive_analysis,
            args=(upload_id, df, engines),
            daemon=True
        )
        thread.start()
        
        return upload_id
    
    def _run_progressive_analysis(self, upload_id: str, df, engines: Dict[str, Any]):
        """Execute progressive analysis stages"""
        progress = self._get_progress(upload_id)
        
        try:
            for stage in AnalysisStage:
                progress.current_stage = stage
                progress.status = "running"
                
                # Check dependencies
                if not self._check_dependencies(stage, progress):
                    logger.warning(f"[NEXUS] Skipping {stage.value} - dependencies not met")
                    self._record_stage_result(
                        upload_id, stage, 
                        success=False, 
                        error="Dependencies not met"
                    )
                    continue
                
                # Execute stage with retry logic
                result = self._execute_stage_with_retry(
                    stage, df, engines, upload_id
                )
                
                self._record_stage_result(upload_id, stage, result)
                progress.completed_stages += 1
                
                if not result.success:
                    logger.error(f"[NEXUS] Stage {stage.value} failed after retries")
            
            # Determine final status
            success_count = sum(
                1 for r in progress.stage_results.values() if r.success
            )
            
            if success_count == progress.total_stages:
                progress.status = "completed"
            elif success_count > 0:
                progress.status = "partial"
            else:
                progress.status = "failed"
                
        except Exception as e:
            logger.exception(f"[NEXUS] Fatal error in analysis for {upload_id}")
            progress.status = "failed"
        finally:
            progress.end_time = datetime.now(timezone.utc)
            progress.current_stage = None
            with self._lock:
                self._active_analyses.pop(upload_id, None)
    
    def _check_dependencies(self, stage: AnalysisStage, progress: AnalysisProgress) -> bool:
        """Check if all dependencies for a stage have completed successfully"""
        dependencies = self.DEPENDENCIES.get(stage, [])
        
        for dep_stage in dependencies:
            dep_result = progress.stage_results.get(dep_stage)
            if not dep_result or not dep_result.success:
                return False
        
        return True
    
    def _execute_stage_with_retry(
        self, 
        stage: AnalysisStage, 
        df, 
        engines: Dict[str, Any],
        upload_id: str
    ) -> StageResult:
        """Execute a stage with retry logic and timeout"""
        import signal
        
        result = StageResult(stage=stage, success=False, start_time=datetime.now(timezone.utc))
        
        # Set stage-specific timeouts (in seconds)
        stage_timeouts = {
            AnalysisStage.VALIDATION: 30,
            AnalysisStage.BASIC_STATS: 60,
            AnalysisStage.SAMPLE_ML: 300,  # 5 minutes for sample ML
            AnalysisStage.FULL_ML: 600,    # 10 minutes for full ML
            AnalysisStage.GRAPH: 300,      # 5 minutes for graph
            AnalysisStage.XAI: 300,        # 5 minutes for XAI
            AnalysisStage.EXECUTIVE: 180,  # 3 minutes for executive
            AnalysisStage.MONTE_CARLO: 300, # 5 minutes for Monte Carlo
            AnalysisStage.KPI: 120,        # 2 minutes for KPI
        }
        
        timeout = stage_timeouts.get(stage, 300)  # Default 5 minutes
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"[NEXUS] Executing {stage.value} (attempt {attempt + 1}, timeout={timeout}s)")
                
                # Execute with timeout using threading
                import threading
                stage_result = [None]
                stage_exception = [None]
                
                def execute_with_timeout():
                    try:
                        stage_result[0] = self._execute_stage(stage, df, engines, upload_id)
                    except Exception as e:
                        stage_exception[0] = e
                
                thread = threading.Thread(target=execute_with_timeout)
                thread.daemon = True
                thread.start()
                thread.join(timeout=timeout)
                
                if thread.is_alive():
                    raise TimeoutError(f"Stage {stage.value} timed out after {timeout}s")
                
                if stage_exception[0]:
                    raise stage_exception[0]
                
                if not stage_result[0]:
                    raise ValueError(f"Stage {stage.value} returned no result")
                
                result.success = True
                result.data = stage_result[0]
                result.end_time = datetime.now(timezone.utc)
                result.retry_count = attempt
                
                logger.info(f"[NEXUS] ✓ {stage.value} completed successfully")
                return result
                
            except TimeoutError as e:
                result.retry_count = attempt + 1
                logger.error(f"[NEXUS] ✗ {stage.value} attempt {attempt + 1} timed out: {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    result.success = False
                    result.error = f"Stage timed out after {timeout}s"
                    result.end_time = datetime.now(timezone.utc)
                    return result
                    
            except Exception as e:
                result.retry_count = attempt + 1
                logger.error(f"[NEXUS] ✗ {stage.value} attempt {attempt + 1} failed: {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))  # Exponential backoff
        
        result.success = False
        result.error = f"Failed after {self.MAX_RETRIES} attempts"
        result.end_time = datetime.now(timezone.utc)
        return result
    
    def _execute_stage(
        self, 
        stage: AnalysisStage, 
        df, 
        engines: Dict[str, Any],
        upload_id: str
    ) -> Dict:
        """Execute a single analysis stage"""
        handlers = {
            AnalysisStage.VALIDATION: self._stage_validation,
            AnalysisStage.BASIC_STATS: self._stage_basic_stats,
            AnalysisStage.SAMPLE_ML: self._stage_sample_ml,
            AnalysisStage.FULL_ML: self._stage_full_ml,
            AnalysisStage.GRAPH: self._stage_graph,
            AnalysisStage.XAI: self._stage_xai,
            AnalysisStage.EXECUTIVE: self._stage_executive,
            AnalysisStage.MONTE_CARLO: self._stage_monte_carlo,
            AnalysisStage.KPI: self._stage_kpi,
        }
        
        handler = handlers.get(stage)
        if not handler:
            raise ValueError(f"No handler for stage {stage}")
        
        return handler(df, engines, upload_id)
    
    def _stage_validation(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 1: Data validation"""
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "validation_passed": True
        }
    
    def _stage_basic_stats(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 2: Basic statistics (instant)"""
        numeric_cols = df.select_dtypes(include=['number']).columns
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                "mean": float(df[col].mean()) if not df[col].empty else None,
                "median": float(df[col].median()) if not df[col].empty else None,
                "std": float(df[col].std()) if not df[col].empty else None,
                "min": float(df[col].min()) if not df[col].empty else None,
                "max": float(df[col].max()) if not df[col].empty else None,
            }
        
        return {
            "numeric_stats": stats,
            "categorical_counts": {
                col: df[col].value_counts().head(10).to_dict()
                for col in df.select_dtypes(include=['object']).columns
            }
        }
    
    def _stage_sample_ml(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 3: ML analysis on sample (fast, representative)"""
        ml_analyzer = engines.get("ml_analyzer")
        if not ml_analyzer:
            raise ValueError("ML analyzer not available")
        
        # Use representative sample (max 10,000 rows)
        sample_size = min(len(df), 10000)
        if len(df) > sample_size:
            sample_df = df.sample(n=sample_size, random_state=42)
        else:
            sample_df = df
        
        logger.info(f"[NEXUS] Running ML analysis on {len(sample_df)} sample rows")
        return ml_analyzer.full_analysis(sample_df)
    
    def _stage_full_ml(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 4: Full ML analysis (comprehensive)"""
        ml_analyzer = engines.get("ml_analyzer")
        if not ml_analyzer:
            raise ValueError("ML analyzer not available")
        
        # Use configurable max rows for full analysis
        max_rows = int(os.getenv("MAX_ANALYSIS_ROWS", "100000"))
        analysis_df = df.head(max_rows) if len(df) > max_rows else df
        
        logger.info(f"[NEXUS] Running full ML analysis on {len(analysis_df)} rows")
        return ml_analyzer.full_analysis(analysis_df)
    
    def _stage_graph(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 5: Graph analysis (depends on ML results)"""
        graph_engine = engines.get("graph_engine")
        if not graph_engine:
            raise ValueError("Graph engine not available")
        
        progress = self._get_progress(upload_id)
        ml_results = progress.stage_results.get(AnalysisStage.FULL_ML)
        
        if not ml_results or not ml_results.success:
            raise ValueError("ML analysis required for graph analysis")
        
        return {
            "summary": graph_engine.build_from_data(df),
            "centrality": graph_engine.get_centrality_scores(),
            "critical_paths": graph_engine.find_critical_paths(),
            "visualization": graph_engine.get_nodes_and_edges(),
            "resilience": graph_engine.get_resilience_metrics(),
            "deep_tier": graph_engine.deep_tier_inference(df),
        }
    
    def _stage_xai(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 6: XAI analysis (depends on ML + Graph)"""
        xai_engine = engines.get("xai_engine")
        graph_engine = engines.get("graph_engine")
        
        if not xai_engine:
            raise ValueError("XAI engine not available")
        
        progress = self._get_progress(upload_id)
        ml_results = progress.stage_results.get(AnalysisStage.FULL_ML)
        
        if not ml_results or not ml_results.success:
            raise ValueError("ML analysis required for XAI")
        
        ml_data = ml_results.data or {}
        
        return {
            "importance": xai_engine.compute_feature_importance(df),
            "counterfactuals": xai_engine.generate_counterfactuals(
                df, ml_data.get("risk_scores", []), graph_engine
            ),
        }
    
    def _stage_executive(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 7: Executive summary (depends on all previous)"""
        ai_copilot = engines.get("ai_copilot")
        if not ai_copilot:
            raise ValueError("AI copilot not available")
        
        progress = self._get_progress(upload_id)
        ml_results = progress.stage_results.get(AnalysisStage.FULL_ML)
        
        if not ml_results or not ml_results.success:
            raise ValueError("ML analysis required for executive summary")
        
        ml_data = ml_results.data or {}
        
        # Simplified executive summary without world events for now
        try:
            exec_res = ai_copilot.generate_executive_summary(
                ml_data.get("summary", {}),
                ml_data.get("risk_scores", []),
                ml_data.get("anomalies", {}),
            )
            return {"executive_summary": exec_res}
        except Exception as e:
            logger.warning(f"[NEXUS] Executive summary generation failed: {e}")
            return {"executive_summary": "Executive summary generation failed"}
    
    def _stage_monte_carlo(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 8: Monte Carlo simulation (independent)"""
        monte_carlo_engine = engines.get("monte_carlo_engine")
        if not monte_carlo_engine:
            raise ValueError("Monte Carlo engine not available")
        
        monte_carlo_engine.fit(df)
        return {"monte_carlo_fitted": True}
    
    def _stage_kpi(self, df, engines: Dict[str, Any], upload_id: str) -> Dict:
        """Stage 9: KPI computation (depends on ML results)"""
        kpi_engine = engines.get("kpi_engine_instance")
        if not kpi_engine:
            raise ValueError("KPI engine not available")
        
        progress = self._get_progress(upload_id)
        ml_results = progress.stage_results.get(AnalysisStage.FULL_ML)
        
        if not ml_results or not ml_results.success:
            raise ValueError("ML analysis required for KPI computation")
        
        ml_data = ml_results.data or {}
        
        return kpi_engine.compute_all_kpis(
            df,
            risk_scores=ml_data.get("risk_scores", []),
            anomalies=ml_data.get("anomalies", {}),
        )
    
    def _record_stage_result(self, upload_id: str, stage: AnalysisStage, result: StageResult):
        """Record the result of a stage and persist to DB."""
        with self._lock:
            progress = self._progress.get(upload_id)
            if progress:
                progress.stage_results[stage] = result

        # Persist completed stage results to analysis_results table
        # so the dashboard can read them immediately as each stage finishes.
        if result.success and result.data:
            self._save_stage_to_db(stage, result.data, upload_id)

    def _save_stage_to_db(
        self, stage: AnalysisStage, data: Dict, upload_id: str
    ):
        """Persist a completed stage result to the analysis_results DB table."""
        try:
            from app.core.database import SessionLocal  # type: ignore
            from app.core.orchestrator import save_analysis_result  # type: ignore

            # Map stage → analysis_type key used by dashboard routes
            stage_to_key = {
                AnalysisStage.FULL_ML:      "ml",
                AnalysisStage.SAMPLE_ML:    "ml",        # overwritten by FULL_ML later
                AnalysisStage.GRAPH:        "graph",
                AnalysisStage.XAI:          "xai",
                AnalysisStage.KPI:          "kpis",
                AnalysisStage.MONTE_CARLO:  "monte_carlo",
                AnalysisStage.BASIC_STATS:  "basic_stats",
            }
            key = stage_to_key.get(stage)
            if not key:
                return

            # For EXECUTIVE, save the inner executive_summary dict
            if stage == AnalysisStage.EXECUTIVE:
                exec_inner = data.get("executive_summary", data)
                db = SessionLocal()
                try:
                    save_analysis_result(db, "executive", exec_inner)
                finally:
                    db.close()
                return

            db = SessionLocal()
            try:
                save_analysis_result(db, key, data)
                logger.info("[NEXUS] Saved %s results to DB (upload=%s)", key, upload_id)
            finally:
                db.close()

        except Exception as e:
            logger.error("[NEXUS] Failed to persist %s to DB: %s", stage.value, e)
    
    def _get_progress(self, upload_id: str) -> Optional[AnalysisProgress]:
        """Get progress for an upload"""
        with self._lock:
            return self._progress.get(upload_id)
    
    def get_progress(self, upload_id: str) -> Optional[Dict]:
        """Get progress info for API response"""
        progress = self._get_progress(upload_id)
        if not progress:
            return None
        
        return {
            "upload_id": progress.upload_id,
            "status": progress.status,
            "total_stages": progress.total_stages,
            "completed_stages": progress.completed_stages,
            "current_stage": progress.current_stage.value if progress.current_stage else None,
            "progress_percentage": (progress.completed_stages / progress.total_stages) * 100,
            "start_time": progress.start_time.isoformat() if progress.start_time else None,
            "end_time": progress.end_time.isoformat() if progress.end_time else None,
            "stage_results": {
                stage.value: {
                    "success": result.success,
                    "error": result.error,
                    "duration_seconds": (
                        (result.end_time - result.start_time).total_seconds() 
                        if result.start_time and result.end_time else None
                    )
                }
                for stage, result in progress.stage_results.items()
            }
        }
    
    def cancel_analysis(self, upload_id: str) -> bool:
        """Cancel an ongoing analysis"""
        with self._lock:
            if upload_id in self._active_analyses:
                progress = self._progress.get(upload_id)
                if progress:
                    progress.status = "cancelled"
                self._active_analyses.pop(upload_id, None)
                return True
        return False


# Global coordinator instance
coordinator = AnalysisCoordinator()