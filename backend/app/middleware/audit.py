"""HTTP audit middleware for compliance-grade request trails."""

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.utils import mask_sensitive_data
from app.core.database import SessionLocal
from app.models.auth import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """Persist request audit records without blocking the response path heavily."""

    async def dispatch(self, request: Request, call_next: Callable):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)

        if request.url.path not in {"/health", "/docs", "/openapi.json"}:
            db = SessionLocal()
            try:
                user = getattr(request.state, "user", None) or {}
                db.add(AuditLog(
                    user_id=user.get("uid") or user.get("id"),
                    action=f"{request.method} {request.url.path}",
                    resource=request.url.path,
                    details=mask_sensitive_data({
                        "method": request.method,
                        "path": request.url.path,
                        "query": dict(request.query_params),
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "request_id": getattr(request.state, "request_id", None),
                    }),
                    ip_address=request.client.host if request.client else None,
                ))
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        return response
