"""
NEXUS — Authentication & Authorization
========================================
JWT-based auth with RBAC. Enterprise-grade security layer.
"""

from app.models.auth import User, APIKey, AuditLog, RefreshToken  # type: ignore
from .utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    generate_api_key,
    generate_refresh_token,
    verify_refresh_token_hash,
)
from .service import AuthService, check_permission, ROLE_PERMISSIONS

__all__ = [
    "User",
    "APIKey",
    "AuditLog",
    "RefreshToken",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "generate_api_key",
    "generate_refresh_token",
    "verify_refresh_token_hash",
    "AuthService",
    "check_permission",
    "ROLE_PERMISSIONS",
]
