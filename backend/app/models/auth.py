from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Index, Text  # type: ignore
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


class Role(Base):
    """Fine-grained RBAC role definition."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, default=lambda: [])
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class PermissionGrant(Base):
    """Direct user permission grants/denials for field-level overrides."""
    __tablename__ = "permission_grants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    permission = Column(String, index=True, nullable=False)
    effect = Column(String, default="allow")  # allow, deny
    resource = Column(String, nullable=True)
    field_scope = Column(JSON, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)


class DataMaskingPolicy(Base):
    """Field-level data masking and encryption policy."""
    __tablename__ = "data_masking_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String, unique=True, index=True)
    resource = Column(String, index=True)
    field_name = Column(String, index=True)
    classification = Column(String, default="internal")
    mask_strategy = Column(String, default="partial")  # partial, full, hash, none
    encrypt_at_rest = Column(Boolean, default=False)
    allowed_roles = Column(JSON, default=lambda: ["admin"])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)


class ComplianceReport(Base):
    """Generated compliance evidence package."""
    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    framework = Column(String, index=True)  # SOC2, GDPR, HIPAA, ISO27001
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    status = Column(String, default="generated")
    summary = Column(JSON, nullable=True)
    generated_by = Column(Integer, nullable=True)
    generated_at = Column(DateTime, default=_utcnow)
