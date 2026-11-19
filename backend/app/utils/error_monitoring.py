"""
NEXUS — Error Monitoring and Metrics
=====================================
Utilities for error tracking, metrics collection, and alerting.
"""

import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nexus.error_monitoring")

# Import errors at runtime to avoid circular imports
def get_timeout_error():
    """Get TimeoutError class to avoid circular import."""
    from app.core.errors import TimeoutError
    return TimeoutError


# ── Error Severity Levels ──────────────────────────────────────────────────────

class ErrorSeverity(str, Enum):
    """Error severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Error Metrics Data Structures ──────────────────────────────────────────────

@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_id: str
    error_type: str
    error_code: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "endpoint": self.endpoint,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "stack_trace": self.stack_trace,
            "metadata": self.metadata,
        }


@dataclass
class ErrorMetrics:
    """Aggregated error metrics."""
    total_errors: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    errors_by_code: Dict[str, int] = field(default_factory=dict)
    errors_by_severity: Dict[str, int] = field(default_factory=dict)
    errors_by_endpoint: Dict[str, int] = field(default_factory=dict)
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_rate_per_minute: float = 0.0
    last_error_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_errors": self.total_errors,
            "errors_by_type": self.errors_by_type,
            "errors_by_code": self.errors_by_code,
            "errors_by_severity": self.errors_by_severity,
            "errors_by_endpoint": self.errors_by_endpoint,
            "recent_error_count": len(self.recent_errors),
            "error_rate_per_minute": self.error_rate_per_minute,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
        }


# ── Error Monitor Class ───────────────────────────────────────────────────────

class ErrorMonitor:
    """
    Central error monitoring and metrics collection.

    Tracks errors, calculates metrics, and provides alerting capabilities.
    """

    def __init__(self, alert_thresholds: Optional[Dict[str, int]] = None):
        self.metrics = ErrorMetrics()
        self.alert_thresholds = alert_thresholds or {
            "critical_per_minute": 5,
            "high_per_minute": 10,
            "total_per_minute": 20,
        }
        self.alert_callbacks: List[callable] = []
        self._recent_errors: deque = deque(maxlen=1000)
        self._error_history: List[ErrorRecord] = []

    def record_error(
        self,
        error_type: str,
        error_code: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        endpoint: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record an error occurrence.

        Returns the error_id for tracking.
        """
        error_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        error_record = ErrorRecord(
            error_id=error_id,
            error_type=error_type,
            error_code=error_code,
            message=message,
            severity=severity,
            timestamp=timestamp,
            endpoint=endpoint,
            user_id=user_id,
            request_id=request_id,
            stack_trace=stack_trace,
            metadata=metadata or {},
        )

        # Update metrics
        self.metrics.total_errors += 1
        self.metrics.errors_by_type[error_type] = self.metrics.errors_by_type.get(error_type, 0) + 1
        self.metrics.errors_by_code[error_code] = self.metrics.errors_by_code.get(error_code, 0) + 1
        self.metrics.errors_by_severity[severity.value] = self.metrics.errors_by_severity.get(severity.value, 0) + 1

        if endpoint:
            self.metrics.errors_by_endpoint[endpoint] = self.metrics.errors_by_endpoint.get(endpoint, 0) + 1

        self.metrics.last_error_time = timestamp

        # Store in recent errors
        self._recent_errors.append(error_record)
        self._error_history.append(error_record)

        # Update error rate
        self._update_error_rate()

        # Check for alerts
        self._check_alerts(error_record)

        # Log the error
        log_level = logging.CRITICAL if severity == ErrorSeverity.CRITICAL else logging.ERROR
        logger.log(
            log_level,
            "[NEXUS] Error recorded: %s (%s) - %s [%s]",
            error_type, error_code, message, severity.value
        )

        return error_id

    def _update_error_rate(self):
        """Calculate error rate per minute."""
        if not self._recent_errors:
            self.metrics.error_rate_per_minute = 0.0
            return

        now = datetime.now(timezone.utc)
        one_minute_ago = now - timedelta(minutes=1)

        recent_count = sum(
            1 for error in self._recent_errors
            if error.timestamp >= one_minute_ago
        )

        self.metrics.error_rate_per_minute = float(recent_count)

    def _check_alerts(self, error_record: ErrorRecord):
        """Check if error conditions trigger alerts."""
        if error_record.severity == ErrorSeverity.CRITICAL:
            critical_count = self._count_errors_in_last_minute(ErrorSeverity.CRITICAL)
            if critical_count >= self.alert_thresholds.get("critical_per_minute", 5):
                self._trigger_alert("critical_threshold", error_record)

        if error_record.severity == ErrorSeverity.HIGH:
            high_count = self._count_errors_in_last_minute(ErrorSeverity.HIGH)
            if high_count >= self.alert_thresholds.get("high_per_minute", 10):
                self._trigger_alert("high_threshold", error_record)

        if self.metrics.error_rate_per_minute >= self.alert_thresholds.get("total_per_minute", 20):
            self._trigger_alert("total_threshold", error_record)

    def _count_errors_in_last_minute(self, severity: ErrorSeverity) -> int:
        """Count errors of given severity in the last minute."""
        now = datetime.now(timezone.utc)
        one_minute_ago = now - timedelta(minutes=1)

        return sum(
            1 for error in self._recent_errors
            if error.severity == severity and error.timestamp >= one_minute_ago
        )

    def _trigger_alert(self, alert_type: str, error_record: ErrorRecord):
        """Trigger alert callbacks."""
        alert_data = {
            "alert_type": alert_type,
            "error": error_record.to_dict(),
            "metrics": self.metrics.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error("[NEXUS] Alert callback failed: %s", e, exc_info=True)

    def add_alert_callback(self, callback: callable):
        """Add a callback function for alerts."""
        self.alert_callbacks.append(callback)
        logger.info("[NEXUS] Alert callback registered")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current error metrics."""
        self._update_error_rate()
        return self.metrics.to_dict()

    def get_recent_errors(
        self,
        limit: int = 100,
        severity: Optional[ErrorSeverity] = None,
        error_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent errors with optional filtering."""
        errors = list(self._recent_errors)

        if severity:
            errors = [e for e in errors if e.severity == severity]

        if error_type:
            errors = [e for e in errors if e.error_type == error_type]

        # Sort by timestamp descending
        errors.sort(key=lambda x: x.timestamp, reverse=True)

        return [e.to_dict() for e in errors[:limit]]

    def get_error_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get error summary for the specified time period."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        period_errors = [
            e for e in self._error_history
            if e.timestamp >= cutoff_time
        ]

        if not period_errors:
            return {
                "period_minutes": minutes,
                "total_errors": 0,
                "error_rate_per_minute": 0.0,
                "top_error_types": [],
                "top_error_codes": [],
                "top_endpoints": [],
            }

        # Calculate statistics
        type_counts = defaultdict(int)
        code_counts = defaultdict(int)
        endpoint_counts = defaultdict(int)

        for error in period_errors:
            type_counts[error.error_type] += 1
            code_counts[error.error_code] += 1
            if error.endpoint:
                endpoint_counts[error.endpoint] += 1

        return {
            "period_minutes": minutes,
            "total_errors": len(period_errors),
            "error_rate_per_minute": len(period_errors) / minutes,
            "top_error_types": sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_error_codes": sorted(code_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_endpoints": sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        }

    def clear_old_errors(self, hours: int = 24):
        """Clear errors older than specified hours."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        original_count = len(self._error_history)
        self._error_history = [
            e for e in self._error_history
            if e.timestamp >= cutoff_time
        ]

        cleared_count = original_count - len(self._error_history)
        logger.info("[NEXUS] Cleared %d old errors (older than %d hours)", cleared_count, hours)


# ── Global Error Monitor Instance ──────────────────────────────────────────────

error_monitor = ErrorMonitor()


# ── Middleware Integration ─────────────────────────────────────────────────────

class ErrorMonitoringMiddleware:
    """Middleware for automatic error monitoring."""

    def __init__(self, monitor: ErrorMonitor):
        self.monitor = monitor

    async def __call__(self, request, call_next):
        """Process request and monitor any errors."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        user_id = getattr(request.state, "user", {}).get("id") if hasattr(request.state, "user") else None
        endpoint = f"{request.method} {request.url.path}"

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Determine error details
            error_type = type(e).__name__
            error_code = getattr(e, "error_code", "internal_error")
            message = str(e)

            # Determine severity
            severity = ErrorSeverity.MEDIUM
            if hasattr(e, "http_status"):
                if e.http_status >= 500:
                    severity = ErrorSeverity.HIGH
                elif e.http_status >= 400:
                    severity = ErrorSeverity.MEDIUM
            else:
                severity = ErrorSeverity.HIGH

            # Record the error
            self.monitor.record_error(
                error_type=error_type,
                error_code=error_code,
                message=message,
                severity=severity,
                endpoint=endpoint,
                user_id=str(user_id) if user_id else None,
                request_id=request_id,
                stack_trace=traceback_str(e),
            )

            # Re-raise the exception
            raise


def traceback_str(exception: Exception) -> str:
    """Get formatted traceback string from exception."""
    import traceback
    return "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))


# ── Metrics Endpoint Handler ──────────────────────────────────────────────────

def get_error_metrics() -> Dict[str, Any]:
    """Get current error metrics for API endpoint."""
    return error_monitor.get_metrics()


def get_error_summary(minutes: int = 60) -> Dict[str, Any]:
    """Get error summary for API endpoint."""
    return error_monitor.get_error_summary(minutes)


def get_recent_errors(
    limit: int = 100,
    severity: Optional[str] = None,
    error_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Get recent errors for API endpoint."""
    severity_enum = ErrorSeverity(severity) if severity else None
    errors = error_monitor.get_recent_errors(limit, severity_enum, error_type)

    return {
        "errors": errors,
        "count": len(errors),
        "limit": limit,
    }


# ── Alert Callback Examples ───────────────────────────────────────────────────

def log_alert_callback(alert_data: Dict[str, Any]):
    """Simple alert callback that logs alerts."""
    logger.critical(
        "[NEXUS] ALERT TRIGGERED: %s - Error: %s (%s)",
        alert_data["alert_type"],
        alert_data["error"]["error_type"],
        alert_data["error"]["error_code"]
    )


def email_alert_callback(alert_data: Dict[str, Any]):
    """Alert callback that sends email (placeholder)."""
    # In production, integrate with email service
    logger.info("[NEXUS] Email alert would be sent for: %s", alert_data["alert_type"])


# Register default alert callbacks
error_monitor.add_alert_callback(log_alert_callback)
