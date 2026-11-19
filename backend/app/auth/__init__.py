"""
NEXUS — Authentication & Authorization
========================================
JWT-based auth with RBAC. Enterprise-grade security layer.
"""

from app.models.auth import APIKey, AuditLog, RefreshToken, User  # type: ignore

from .service import ROLE_PERMISSIONS, AuthService, check_permission
from .utils import (
    create_access_token,
    decode_token,
    generate_api_key,
    generate_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token_hash,
)

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
