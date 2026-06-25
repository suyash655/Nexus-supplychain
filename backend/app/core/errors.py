"""
NEXUS — Centralized Error Handling
===================================
Defines:
  - ErrorCode literals — derived from actual error categories in this app.
  - ErrorEnvelope — the single, consistent JSON shape returned on every error.
  - NexusError  — typed base exception with an HTTP status + error code baked in.
  - Subclasses for each logical error category (NotFoundError, AuthError, etc.)

Error code rationale (derived from actual usage in this codebase):
  - validation_error   → Pydantic / FastAPI request schema failures (422), or manual
                         field-level checks (e.g. empty question in /copilot/ask).
  - auth_error         → Bad/expired JWT, wrong password, revoked token.
  - not_found          → DB record or file (data frame) not present.
  - engine_unavailable → A specific engine was None (failed to init at startup).
  - no_data            → Engines are running but no supply data has been uploaded yet.
  - internal_error     → Everything else (bugs, unexpected engine failures).
"""

from __future__ import annotations

import uuid
import logging
from typing import Literal, Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("nexus.errors")

# ── Error code literals ──────────────────────────────────────────────────────

ErrorCode = Literal[
    "validation_error",
    "auth_error",
    "not_found",
    "engine_unavailable",
    "no_data",
    "internal_error",
]


# ── Envelope builder ─────────────────────────────────────────────────────────

def error_envelope(
    code: ErrorCode,
    message: str,
    request_id: Optional[str] = None,
    detail: Optional[object] = None,
) -> dict:
    """Return the canonical error response body."""
    body: dict = {
        "status": "error",
        "code": code,
        "message": message,
        "request_id": request_id or str(uuid.uuid4()),
    }
    if detail is not None:
        body["detail"] = detail
    return body


def error_response(
    status_code: int,
    code: ErrorCode,
    message: str,
    request_id: Optional[str] = None,
    detail: Optional[object] = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_envelope(code, message, request_id, detail),
    )


# ── Typed exception hierarchy ─────────────────────────────────────────────────

class NexusError(Exception):
    """Base class for all application-level errors."""

    http_status: int = 500
    error_code: ErrorCode = "internal_error"

    def __init__(self, message: str, detail: Optional[object] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class ValidationError(NexusError):
    http_status = 422
    error_code = "validation_error"


class AuthError(NexusError):
    http_status = 401
    error_code = "auth_error"


class NotFoundError(NexusError):
    http_status = 404
    error_code = "not_found"


class EngineUnavailableError(NexusError):
    http_status = 503
    error_code = "engine_unavailable"


class NoDataError(NexusError):
    http_status = 400
    error_code = "no_data"


# ── FastAPI exception handlers (register these on the `app` object) ───────────

def _get_request_id(request: Request) -> str:
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))


async def nexus_error_handler(request: Request, exc: NexusError) -> JSONResponse:
    """Handler for our own typed NexusError subclasses."""
    return error_response(
        status_code=exc.http_status,
        code=exc.error_code,
        message=exc.message,
        request_id=_get_request_id(request),
        detail=exc.detail,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Convert legacy HTTPException (raised by existing routers) to the envelope."""
    # Map HTTP status → error code
    if exc.status_code == 401 or exc.status_code == 403:
        code: ErrorCode = "auth_error"
    elif exc.status_code == 404:
        code = "not_found"
    elif exc.status_code in (400, 422):
        code = "validation_error"
    elif exc.status_code == 503:
        code = "engine_unavailable"
    else:
        code = "internal_error"

    return error_response(
        status_code=exc.status_code,
        code=code,
        message=str(exc.detail),
        request_id=_get_request_id(request),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert Pydantic/FastAPI schema validation errors to the envelope."""
    # Build a concise summary of which fields failed
    field_errors = [
        {"field": " → ".join(str(loc) for loc in e["loc"]), "msg": e["msg"]}
        for e in exc.errors()
    ]
    return error_response(
        status_code=422,
        code="validation_error",
        message="Request validation failed.",
        request_id=_get_request_id(request),
        detail=field_errors,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all for any unhandled exception.
    Logs the full traceback server-side; returns only a safe envelope to the client.
    """
    rid = _get_request_id(request)
    logger.error(
        "[NEXUS] Unhandled exception on %s %s (request_id=%s)",
        request.method,
        request.url.path,
        rid,
        exc_info=exc,
    )
    return error_response(
        status_code=500,
        code="internal_error",
        message="An unexpected error occurred. Please try again or contact support.",
        request_id=rid,
    )
