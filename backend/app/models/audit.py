"""Compatibility module for audit/governance models."""

from app.models.auth import AuditLog, ComplianceReport, DataMaskingPolicy, PermissionGrant, Role

__all__ = ["AuditLog", "ComplianceReport", "DataMaskingPolicy", "PermissionGrant", "Role"]
