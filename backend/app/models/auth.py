from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Index  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from app.models.base import Base, _utcnow  # type: ignore


class User(Base):
    """Platform user with role-based access."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="analyst")  # admin, manager, analyst, viewer
    team = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, default=lambda: [])  # granular permissions
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # ORM cascades — SQLAlchemy deletes children when a User is deleted
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    # AuditLog deliberately NOT cascade-deleted — see AuditLog docstring
    audit_logs = relationship("AuditLog", back_populates="user", passive_deletes=True)


class RefreshToken(Base):
    """
    Persisted refresh tokens — enables server-side revocation.
    A row is deleted (revoked) on logout or password change.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    # Store only the SHA-256 hash of the raw token, never the raw value.
    token_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="refresh_tokens")
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        # Needed by the nightly cleanup job: DELETE WHERE expires_at < now()
        # Without this index every cleanup scan is O(N) across all token rows.
        Index("ix_refresh_token_expires_at", "expires_at"),
        # Composite index for: WHERE user_id = ? AND revoked = false
        # Used by logout_all to bulk-revoke all of a user's tokens.
        Index("ix_refresh_token_user_revoked", "user_id", "revoked"),
    )


class APIKey(Base):
    """API keys for programmatic access and connector auth."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="api_keys")
    scopes = Column(JSON, default=lambda: ["read"])  # read, write, admin
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)


class AuditLog(Base):
    """
    Immutable audit trail for compliance.

    IMPORTANT: AuditLog uses ondelete='SET NULL' rather than CASCADE.
    Audit records must survive user deletion — regulatory compliance (SOC 2,
    GDPR Article 30) requires that the *action history* is preserved even
    when the actor's account is removed.  The user_id is set to NULL, but
    the action, resource, details, and timestamp remain intact.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String)  # login, upload, query, export, config_change
    resource = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    user = relationship("User", back_populates="audit_logs")
