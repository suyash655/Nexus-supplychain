from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session  # type: ignore

from app.models.auth import User, RefreshToken  # type: ignore
from app.core.config import settings  # type: ignore
from .utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    generate_refresh_token,
    verify_refresh_token_hash,
)

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "manager": ["read", "write", "export", "manage_team", "configure_connectors", "connectors:read", "connectors:write", "connectors:execute", "ibp:*", "reports:*"],
    "analyst": ["read", "write", "export", "run_analysis", "copilot", "connectors:read", "connectors:execute", "ibp:read", "ibp:execute", "reports:read"],
    "viewer": ["read", "connectors:read", "ibp:read", "reports:read"],
}


def check_permission(user_role: str, required: str) -> bool:
    """Check if a role has a specific permission."""
    perms = ROLE_PERMISSIONS.get(user_role, [])
    if "*" in perms or required in perms:
        return True
    namespace = required.split(":", 1)[0]
    return f"{namespace}:*" in perms


def user_has_permission(user: Dict[str, Any], required: str) -> bool:
    """Check role permissions plus user-specific permission grants."""
    role = user.get("role", "viewer")
    explicit = set(user.get("permissions") or [])
    return check_permission(role, required) or required in explicit or "*" in explicit


def require_permission(user: Dict[str, Any], required: str) -> None:
    """Raise a FastAPI 403 if the decoded user lacks a permission."""
    if not user_has_permission(user, required):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail=f"Missing permission: {required}")


def _issue_token_pair(db: Session, user: User) -> Dict[str, Any]:
    """
    Create a new access + refresh token pair for a user.
    The raw refresh token is returned to the caller once; only its hash is persisted.

    NOTE: This function calls db.flush(), NOT db.commit().  The caller is
    responsible for committing the enclosing transaction.  This allows the new
    token creation to be atomic with any preceding revocation.
    """
    access_token = create_access_token(
        {"sub": user.email, "role": user.role, "uid": user.id}
    )

    raw_refresh, refresh_hash = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + settings.refresh_token_lifetime

    db_token = RefreshToken(
        token_hash=refresh_hash,
        user_id=user.id,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(db_token)
    db.flush()  # assign PK but don't commit — caller owns the transaction

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
    }


class AuthService:
    """Handles user registration, login, token refresh, and logout."""

    @staticmethod
    def register(
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: str = "",
        role: str = "analyst",
    ) -> Dict[str, Any]:
        """Register a new user and return an initial token pair."""
        existing = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing:
            return {"error": "User with this email or username already exists"}

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
        )
        db.add(user)
        db.flush()  # assign user.id before token creation

        tokens = _issue_token_pair(db, user)
        db.commit()  # single commit: user + refresh token

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            **tokens,
        }

    @staticmethod
    def login(db: Session, email: str, password: str) -> Dict[str, Any]:
        """Authenticate and return a new access + refresh token pair."""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return {"error": "Invalid credentials"}

        if not user.is_active:
            return {"error": "Account is deactivated"}

        user.last_login = datetime.now(timezone.utc)

        tokens = _issue_token_pair(db, user)
        db.commit()  # single commit: last_login update + refresh token

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name,
            },
            **tokens,
        }

    @staticmethod
    def refresh(db: Session, raw_refresh_token: str) -> Dict[str, Any]:
        """
        Exchange a valid refresh token for a new access + refresh token pair
        (token rotation — the old refresh token is revoked on use).

        Race-condition fix: we use SELECT ... FOR UPDATE to obtain an exclusive
        row-level lock on the matched refresh token.  If two concurrent requests
        present the same token, only one will acquire the lock; the other blocks
        until the first commits (at which point revoked=True and the second
        request correctly fails with 'Invalid or expired refresh token').

        The revocation and new-token creation happen in a single db.commit(),
        making the entire operation atomic.
        """
        # Lock-aware query: FOR UPDATE prevents concurrent readers from
        # both matching the same un-revoked token.
        candidates = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.revoked == False,  # noqa: E712
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
            .with_for_update()  # row-level lock
            .all()
        )

        matched: Optional[RefreshToken] = None
        for candidate in candidates:
            if verify_refresh_token_hash(raw_refresh_token, candidate.token_hash):
                matched = candidate
                break

        if not matched:
            return {"error": "Invalid or expired refresh token"}

        # Revoke the used token (rotation — prevents reuse)
        matched.revoked = True
        # Do NOT commit yet — new token creation below is part of the same tx

        user = db.query(User).filter(User.id == matched.user_id).first()
        if not user or not user.is_active:
            db.commit()  # persist revocation even if user is gone
            return {"error": "User not found or deactivated"}

        tokens = _issue_token_pair(db, user)
        db.commit()  # atomic: revoke old + persist new in one transaction

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            **tokens,
        }

    @staticmethod
    def logout(db: Session, raw_refresh_token: str) -> Dict[str, Any]:
        """
        Revoke a specific refresh token (single-device logout).
        The short-lived access token expires naturally.
        """
        candidates = (
            db.query(RefreshToken)
            .filter(RefreshToken.revoked == False)  # noqa: E712
            .all()
        )

        for candidate in candidates:
            if verify_refresh_token_hash(raw_refresh_token, candidate.token_hash):
                candidate.revoked = True
                db.commit()
                return {"message": "Logged out successfully"}

        # Treat unknown tokens as already-logged-out (idempotent)
        return {"message": "Logged out successfully"}

    @staticmethod
    def logout_all(db: Session, user_id: int) -> Dict[str, Any]:
        """Revoke ALL refresh tokens for a user (logout from all devices)."""
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,  # noqa: E712
        ).update({"revoked": True})
        db.commit()
        return {"message": "Logged out from all devices"}

    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """Get user from a JWT access token."""
        payload = decode_token(token)
        if not payload:
            return None
        email = payload.get("sub")
        if not email:
            return None
        return db.query(User).filter(User.email == email).first()
