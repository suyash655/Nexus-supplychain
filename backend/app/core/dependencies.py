"""
NEXUS — Shared FastAPI Dependencies
=====================================
Centralized auth guard + DB session to remove duplication across routers.
"""

import os
from typing import Optional

from fastapi import Depends, HTTPException, Header  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.database import SessionLocal  # type: ignore
from app.auth.utils import decode_token  # type: ignore


# ── Database dependency ──

def get_db():
    """Yield a DB session, auto-close when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_for_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """
    Yield a DB session configured for a specific tenant via RLS.
    We check for Postgres vs SQLite since SQLite does not support this RLS.

    Security note: PostgreSQL's SET LOCAL is a configuration command, not a
    DML statement, so the wire protocol does not support bind parameters for
    its value.  The safe mitigation is strict UUID validation — a valid UUID
    contains only hex digits and hyphens, making SQL injection structurally
    impossible through this value.
    """
    import uuid
    from sqlalchemy import text
    from app.core.config import settings

    # ── Input validation: reject anything that is not a well-formed UUID ──
    # This must happen before the value is used in any SQL context.
    try:
        # uuid.UUID() normalises and validates; we re-serialise to a canonical
        # lowercase string so the value passed to Postgres is always safe.
        safe_tenant_id = str(uuid.UUID(tenant_id))
    except (ValueError, AttributeError):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Invalid tenant_id: must be a valid UUID (e.g. 550e8400-e29b-41d4-a716-446655440000)",
        )

    if not settings.is_sqlite:
        # SET LOCAL is a Postgres configuration command; bind params are not
        # supported by the protocol for this statement type.  safe_tenant_id
        # is guaranteed to match ^[0-9a-f-]{36}$ at this point.
        db.execute(text(f"SET LOCAL app.current_tenant_id = '{safe_tenant_id}'"))

    yield db


# ── Auth dependency ──

_ALLOW_DEMO = os.getenv("ALLOW_DEMO", "true").lower() == "true"


async def require_auth(authorization: Optional[str] = Header(None)) -> dict:
    """
    Extract and validate JWT from Authorization header.
    Returns the decoded token payload (sub, role, uid).

    Demo mode (ALLOW_DEMO=true): activated only when NO Authorization header
    is present at all, or when the header contains a known empty placeholder
    (undefined/null from some frontend stacks).  It is NOT activated by any
    specific token value — there is no magic bypass string.

    Production: set ALLOW_DEMO=false in your environment to disable entirely.
    """
    if not authorization:
        if _ALLOW_DEMO:
            return {"sub": "demo@nexus.ai", "role": "viewer", "uid": 0, "demo": True}
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    # Support "Bearer <token>" or raw token
    token = authorization
    if authorization.lower().startswith("bearer "):
        token = authorization[7:]

    if not token or token == "undefined" or token == "null":
        if _ALLOW_DEMO:
            return {"sub": "demo@nexus.ai", "role": "viewer", "uid": 0, "demo": True}
        raise HTTPException(status_code=401, detail="Invalid token")

    # Real JWT validation — no magic token bypass exists beyond this point
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


async def get_current_user(user: dict = Depends(require_auth)) -> dict:
    """Compatibility alias for routers that use the older dependency name."""
    return user


async def require_admin(user: dict = Depends(require_auth)) -> dict:
    """Require admin role for sensitive operations."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

