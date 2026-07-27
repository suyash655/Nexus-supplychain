"""
NEXUS — Auth Router
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request  # type: ignore
from pydantic import BaseModel, EmailStr, Field  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from slowapi import Limiter  # type: ignore
from slowapi.util import get_remote_address  # type: ignore
from typing import Optional

from app.core.database import SessionLocal  # type: ignore
from app.core.dependencies import require_auth  # type: ignore
from app.auth import AuthService, AuditLog  # type: ignore
from app.auth.utils import decode_token  # type: ignore

router = APIRouter(prefix="/auth", tags=["Auth"])

limiter = Limiter(key_func=get_remote_address)


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Fix #4: Pydantic models for registration input validation ──

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254, description="Valid email address")
    username: str = Field(..., min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field("", max_length=128)
    role: str = Field("analyst", pattern=r"^(admin|analyst|viewer)$")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class TokenFormRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, max_length=2048)


@router.post("/register")
@limiter.limit("5/minute")
def register_user(
    request: Request,
    body: RegisterRequest,
    db: Session = Depends(_get_db),
):
    """Register a new NEXUS user. Returns access_token + refresh_token."""
    result = AuthService.register(db, body.email, body.username, body.password, body.full_name, body.role)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    db.add(AuditLog(action="register", resource=f"user:{body.username}", details={"role": body.role}))
    db.commit()
    return result


# Fix #1: Rate-limit login AND refresh
@router.post("/login")
@limiter.limit("10/minute")
def login_user(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(_get_db),
):
    """Authenticate and get access_token + refresh_token pair."""
    result = AuthService.login(db, body.email, body.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    db.add(AuditLog(user_id=result["user"]["id"], action="login", resource="auth"))
    db.commit()
    return result


@router.post("/refresh")
@limiter.limit("5/minute")
def refresh_token(
    request: Request,
    body: TokenFormRequest,
    db: Session = Depends(_get_db),
):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    The submitted refresh token is immediately revoked (rotation).
    """
    result = AuthService.refresh(db, body.refresh_token)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@router.post("/logout")
def logout_user(
    body: TokenFormRequest,
    db: Session = Depends(_get_db),
):
    """
    Revoke the supplied refresh token (single-device logout).
    The short-lived access token will expire on its own within 60 minutes.
    """
    return AuthService.logout(db, body.refresh_token)


@router.post("/logout-all")
def logout_all_devices(
    db: Session = Depends(_get_db),
    user: dict = Depends(require_auth),
):
    """Revoke ALL refresh tokens for the current user (all-device logout)."""
    result = AuthService.logout_all(db, user["uid"])
    db.add(AuditLog(user_id=user["uid"], action="logout_all", resource="auth"))
    db.commit()
    return result


# Fix #3: Convert query-param JWT to header-only
@router.get("/me")
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(_get_db),
):
    """Get current user from Authorization: Bearer <token> header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization
    if authorization.lower().startswith("bearer "):
        token = authorization[7:]

    if not token or token in ("undefined", "null"):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = AuthService.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
    }
