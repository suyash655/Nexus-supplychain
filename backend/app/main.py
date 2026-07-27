"""
NEXUS — Main API Server
========================
Thin entry point: initialises FastAPI, registers routers, and manages
engine singletons via the lifespan context manager.

Engine initialisation is deferred to lifespan (not module-level) so that:
  - A single failing engine does not crash the whole server on startup
  - Each failure is logged with the engine name and the actual exception
  - The app starts in degraded mode and continues serving healthy endpoints
  - Unit tests can import this module without triggering heavy __init__ calls
"""

import logging
import math
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from fastapi.exceptions import RequestValidationError  # type: ignore
from starlette.exceptions import HTTPException as StarletteHTTPException  # type: ignore
from slowapi import _rate_limit_exceeded_handler  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore
from dotenv import load_dotenv  # type: ignore
import numpy as np  # type: ignore
from fastapi.encoders import ENCODERS_BY_TYPE

ENCODERS_BY_TYPE[np.integer] = int
ENCODERS_BY_TYPE[np.floating] = float
ENCODERS_BY_TYPE[np.ndarray] = lambda x: x.tolist()

load_dotenv()

from app.core.database import engine  # type: ignore
from app.models import Base  # type: ignore
from app.core.config import settings  # type: ignore
from app.core.errors import (  # type: ignore
    NexusError,
    nexus_error_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.middleware.audit import AuditMiddleware  # type: ignore

# ── Crash loudly if running in production with the default secret ──
settings.validate()


# ============================================================
# Structured JSON Logging
# ============================================================

class JSONFormatter(logging.Formatter):
    """Format all logs as structured JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Include request_id if it was injected into the log record
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
            
        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)
            
        # Extract extra kwargs passed to logger
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                           "funcName", "levelname", "levelno", "lineno", "module",
                           "msecs", "message", "msg", "name", "pathname", "process",
                           "processName", "relativeCreated", "stack_info", "thread",
                           "threadName", "taskName", "request_id"]:
                log_obj[key] = value

        return json.dumps(log_obj, default=str)

# Apply structured logging globally
_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler], force=True)

logger = logging.getLogger("nexus.startup")


# ============================================================
# Safe JSON Response (NaN / Inf → null)
# ============================================================

class SafeJSONResponse(JSONResponse):
    """JSONResponse that silently converts NaN/Inf to null."""

    def render(self, content) -> bytes:
        return json.dumps(
            self._sanitize(content),
            ensure_ascii=False,
            allow_nan=False,
            default=self._default_serializer,
        ).encode("utf-8")

    @classmethod
    def _sanitize(cls, obj):
        if isinstance(obj, float):
            return None if (math.isnan(obj) or math.isinf(obj)) else obj
        if isinstance(obj, (np.floating,)):
            v = float(obj)
            return None if (math.isnan(v) or math.isinf(v)) else v
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return cls._sanitize(obj.tolist())
        if isinstance(obj, dict):
            return {key: cls._sanitize(value) for key, value in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [cls._sanitize(value) for value in obj]
        return obj

    @staticmethod
    def _default_serializer(obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            v = float(obj)
            return None if (math.isnan(v) or math.isinf(v)) else v
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)


# ============================================================
# Engine container
# ============================================================

class AppEngines:
    """
    Holds all engine singletons.  Populated during lifespan startup.

    Attributes default to None so that any router importing this object
    before lifespan completes (e.g. in tests) gets a clear AttributeError
    rather than a stale import-time instance.
    """
    ml_analyzer = None
    graph_engine = None
    ai_copilot = None
    xai_engine = None
    causal_engine = None
    quality_engine = None
    monte_carlo_engine = None
    kpi_engine_instance = None
    data_scheduler = None
    tgnn_engine_instance = None
    sop_engine = None
    response_planning_engine = None

    # Tracks which engines failed to initialise
    failed_engines: list = []


engines = AppEngines()


def _init_engine(name: str, factory):
    """
    Call `factory()` and return the result.
    On any exception: log the engine name + full error and return None.
    The app continues starting — degraded but alive.
    """
    try:
        instance = factory()
        logger.info("[NEXUS] ✓ %s initialised", name)
        return instance
    except Exception as exc:
        logger.error(
            "[NEXUS] ✗ %s failed to initialise: %s — "
            "endpoints depending on this engine will return errors.",
            name, exc, exc_info=True,
        )
        engines.failed_engines.append({"engine": name, "error": str(exc)})
        return None


# ============================================================
# Lifespan: startup + shutdown in one place
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Replaces deprecated @app.on_event("startup") / ("shutdown").
    All engine initialisation happens here so failures are isolated,
    logged, and never prevent the server from binding its port.
    """
    # ── Create DB tables ──
    # Import all models to ensure they're registered with Base.metadata
    from app.connectors import ConnectorConfig, DataLineage  # type: ignore
    from app.pipeline import PipelineRun, MetricDefinition  # type: ignore
    
    Base.metadata.create_all(bind=engine)
    logger.info("[NEXUS] Database tables verified/created")

    # ── openpyxl check ──
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        logger.warning(
            "[NEXUS] openpyxl not installed — Excel (.xlsx) upload will fail. "
            "Install with: pip install openpyxl"
        )

    # ── Initialise engines one by one ──
    # Each is wrapped independently: a bad ESG config cannot kill ML startup.
    from app.engines.analyzer import SupplyChainAnalyzer  # type: ignore
    from app.engines.graph_engine import SupplyChainGraph  # type: ignore
    from app.engines.ai_copilot import AICopilot  # type: ignore
    from app.engines.xai_engine import XAIEngine  # type: ignore
    from app.causal import CausalGenomeEngine  # type: ignore
    from app.pipeline import DataQualityEngine  # type: ignore
    from app.engines.monte_carlo import MonteCarloEngine  # type: ignore
    from app.engines.kpi_engine import KPIEngine  # type: ignore
    from app.engines.scheduler import DataScheduler  # type: ignore
    from app.engines.tgnn_engine import TGNNEngine  # type: ignore

    engines.ml_analyzer       = _init_engine("SupplyChainAnalyzer",  SupplyChainAnalyzer)
    engines.graph_engine      = _init_engine("SupplyChainGraph",      SupplyChainGraph)
    engines.ai_copilot        = _init_engine("AICopilot",             AICopilot)
    engines.xai_engine        = _init_engine("XAIEngine",             XAIEngine)
    engines.causal_engine     = _init_engine("CausalGenomeEngine",    CausalGenomeEngine)
    engines.quality_engine    = _init_engine("DataQualityEngine",     DataQualityEngine)
    engines.monte_carlo_engine= _init_engine("MonteCarloEngine",      MonteCarloEngine)
    engines.kpi_engine_instance=_init_engine("KPIEngine",             KPIEngine)
    engines.tgnn_engine_instance=_init_engine("TGNNEngine",           TGNNEngine)

    # SAP IBP Engines
    from app.engines.sop_engine import SOPEngine  # type: ignore
    from app.engines.response_planning import ResponsePlanningEngine  # type: ignore
    engines.sop_engine = _init_engine("SOPEngine", SOPEngine)
    engines.response_planning_engine = _init_engine("ResponsePlanningEngine", ResponsePlanningEngine)

    # Initialize API Gateway
    from app.core.api_gateway import api_gateway  # type: ignore
    try:
        api_gateway.initialize()
        logger.info("[NEXUS] ✓ API Gateway initialized")
    except Exception as exc:
        logger.error("[NEXUS] ✗ API Gateway failed to initialize: %s", exc)

    # Scheduler last — it starts background threads
    engines.data_scheduler    = _init_engine("DataScheduler",         DataScheduler)
    if engines.data_scheduler:
        try:
            engines.data_scheduler.start()
            logger.info("[NEXUS] ✓ DataScheduler started")
        except Exception as exc:
            logger.error("[NEXUS] ✗ DataScheduler failed to start: %s", exc, exc_info=True)

    # Set engine kwargs for orchestrator (avoid circular import)
    set_engine_kwargs(
        ml_analyzer=engines.ml_analyzer,
        graph_engine=engines.graph_engine,
        ai_copilot=engines.ai_copilot,
        xai_engine=engines.xai_engine,
        monte_carlo_engine=engines.monte_carlo_engine,
        kpi_engine_instance=engines.kpi_engine_instance,
    )

    if engines.failed_engines:
        logger.warning(
            "[NEXUS] Server started in DEGRADED MODE — %d engine(s) failed: %s",
            len(engines.failed_engines),
            [e["engine"] for e in engines.failed_engines],
        )
    else:
        logger.info("[NEXUS] All engines initialised successfully — server ready")

    yield  # ── app is running ──

    # ── Shutdown ──
    if engines.data_scheduler:
        try:
            engines.data_scheduler.stop()
            logger.info("[NEXUS] DataScheduler stopped")
        except Exception as exc:
            logger.error("[NEXUS] Error stopping DataScheduler: %s", exc)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="NEXUS — Autonomous Data Intelligence Platform",
    description=(
        "Enterprise-grade supply chain intelligence with risk propagation, "
        "multi-source connectors, and AI autonomy."
    ),
    version=settings.APP_VERSION,
    default_response_class=SafeJSONResponse,
    lifespan=lifespan,
)

# ── Global exception handlers ──
# Order matters: most-specific first.
app.add_exception_handler(NexusError, nexus_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

# ── Rate-limit error handler (slowapi) ──
app.state.limiter = __import__("app.features.auth.router", fromlist=["limiter"]).limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Request Logging Middleware ──
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.perf_counter()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        status_code = 500
        raise exc
    finally:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        user_id = "unauthenticated"
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(request.state.user.get("id", "unknown"))
            
        access_logger = logging.getLogger("nexus.access")
        access_logger.info(
            f"{request.method} {request.url.path} {status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
            }
        )
        
    response.headers["X-Request-ID"] = request_id
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ============================================================
# Orchestrator helper — called by upload router
# ============================================================

from app.core.orchestrator import set_engine_kwargs  # type: ignore


# ============================================================
# Register Routers
# ============================================================

from app.features.upload.router import router as upload_router  # type: ignore
from app.features.analytics.router import router as analytics_router  # type: ignore
from app.routers.ml import router as ml_router  # type: ignore
from app.routers.graph import router as graph_router  # type: ignore
from app.routers.copilot import router as copilot_router  # type: ignore
from app.features.auth.router import router as auth_router  # type: ignore
from app.features.mitigation.router import router as mitigation_router  # type: ignore
from app.routers.events import router as events_router  # type: ignore
from app.routers.health import router as health_router  # type: ignore
# from app.routers.rag import router as rag_router  # type: ignore
from app.routers.suppliers import router as suppliers_router  # type: ignore
from app.routers.analysis import router as analysis_router  # type: ignore
from app.routers.remaining import (  # type: ignore
    connectors_router,
    pipeline_router,
    causal_router,
    scheduler_router,
    system_router,
)
from app.features.xai.router import xai_router  # type: ignore
from app.features.export.router import export_router  # type: ignore
from app.routers.sop import router as sop_router  # type: ignore
from app.routers.response_planning import router as response_planning_router  # type: ignore
from app.routers.graphql import router as graphql_router  # type: ignore
from app.routers.websocket import router as websocket_router  # type: ignore
from app.routers.data_management import router as data_management_router  # type: ignore
from app.routers.advanced_analytics import router as advanced_analytics_router  # type: ignore
from app.routers.batch_operations import router as batch_operations_router  # type: ignore
from app.routers.export_reporting import router as export_reporting_router  # type: ignore
from app.routers.monitoring import router as monitoring_router  # type: ignore
from app.routers.control_tower import router as control_tower_router  # type: ignore
from app.features.planning.inventory.router import router as inventory_optimization_router  # type: ignore
from app.routers.analytics_reporting import router as analytics_reporting_router  # type: ignore
from app.routers.connectors import router as enterprise_connectors_router  # type: ignore
from app.routers.ibp_orchestrator import router as ibp_orchestrator_router  # type: ignore

app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(graph_router)
app.include_router(copilot_router)
app.include_router(auth_router)
app.include_router(mitigation_router)
app.include_router(events_router)
app.include_router(health_router)
# app.include_router(rag_router)
app.include_router(suppliers_router)
app.include_router(analysis_router)
app.include_router(enterprise_connectors_router)
app.include_router(xai_router)
app.include_router(export_router)
app.include_router(pipeline_router)
app.include_router(causal_router)
app.include_router(scheduler_router)
app.include_router(system_router)
app.include_router(sop_router)
app.include_router(response_planning_router)
app.include_router(graphql_router)
app.include_router(websocket_router)
app.include_router(data_management_router)
app.include_router(advanced_analytics_router)
app.include_router(batch_operations_router)
app.include_router(export_reporting_router)
app.include_router(monitoring_router)
app.include_router(control_tower_router)
app.include_router(inventory_optimization_router)
app.include_router(analytics_reporting_router)
app.include_router(ibp_orchestrator_router)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
async def root():
    """Welcome message, API status, and degraded engine report."""
    response = {
        "status": "online",
        "message": "NEXUS 3.0 API is running",
        "docs": "/docs",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if engines.failed_engines:
        response["degraded"] = True
        response["failed_engines"] = [e["engine"] for e in engines.failed_engines]
    return response


if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)
