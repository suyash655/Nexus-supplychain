"""
NEXUS — Error Recovery Utilities
==================================
Utilities for error recovery including retry logic, circuit breakers, 
and graceful degradation mechanisms.
"""

import logging
import asyncio
import time
from typing import Callable, Optional, Type, Any, Dict
from functools import wraps
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("nexus.error_recovery")


# ── Retry Decorator ───────────────────────────────────────────────────────────

class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[tuple] = None,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (Exception,)


def retry_with_backoff(config: RetryConfig):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        config: RetryConfig instance with retry parameters
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(
                            "[NEXUS] Function %s failed after %d attempts: %s",
                            func.__name__, config.max_attempts, str(e)
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    
                    # Add jitter to avoid thundering herd
                    if config.jitter:
                        import random
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(
                        "[NEXUS] Function %s failed (attempt %d/%d), retrying in %.2fs: %s",
                        func.__name__, attempt, config.max_attempts, delay, str(e)
                    )
                    
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(
                            "[NEXUS] Function %s failed after %d attempts: %s",
                            func.__name__, config.max_attempts, str(e)
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    
                    # Add jitter
                    if config.jitter:
                        import random
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(
                        "[NEXUS] Function %s failed (attempt %d/%d), retrying in %.2fs: %s",
                        func.__name__, attempt, config.max_attempts, delay, str(e)
                    )
                    
                    time.sleep(delay)
            
            if last_exception:
                raise last_exception
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ── Circuit Breaker Pattern ────────────────────────────────────────────────────

class CircuitBreakerState:
    """Circuit breaker state enumeration."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for preventing cascading failures.
    
    Opens the circuit when failure threshold is reached, then 
    transitions to half-open after timeout to test recovery.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.success_count = 0
        self.last_success_time: Optional[datetime] = None
    
    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        self.success_count += 1
        self.last_success_time = datetime.now(timezone.utc)
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # If we get enough successes in half-open state, close the circuit
            if self.success_count >= 2:
                self.state = CircuitBreakerState.CLOSED
                logger.info("[NEXUS] Circuit breaker closed after successful recovery")
    
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        self.success_count = 0
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Fail fast in half-open state
            self.state = CircuitBreakerState.OPEN
            logger.warning("[NEXUS] Circuit breaker opened again during recovery test")
        elif self.failure_count >= self.failure_threshold:
            # Open the circuit if threshold reached
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                "[NEXUS] Circuit breaker opened after %d failures",
                self.failure_count
            )
    
    def can_attempt(self) -> bool:
        """Check if a call should be attempted."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            if self.last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("[NEXUS] Circuit breaker transitioned to half-open")
                    return True
            return False
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
        }


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
):
    """
    Decorator for circuit breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        expected_exception: Exception type that counts as failure
    """
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            if not breaker.can_attempt():
                # Import at runtime to avoid circular imports
                from app.core.errors import ServiceUnavailableError  # type: ignore
                raise ServiceUnavailableError(
                    f"Circuit breaker is {breaker.state}. Service temporarily unavailable."
                )
            
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except expected_exception as e:
                breaker.record_failure()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            if not breaker.can_attempt():
                # Import at runtime to avoid circular imports
                from app.core.errors import ServiceUnavailableError  # type: ignore
                raise ServiceUnavailableError(
                    f"Circuit breaker is {breaker.state}. Service temporarily unavailable."
                )
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except expected_exception as e:
                breaker.record_failure()
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ── Graceful Degradation ───────────────────────────────────────────────────────

class FallbackHandler:
    """Handler for graceful degradation when services fail."""
    
    def __init__(self):
        self.fallback_functions: Dict[str, Callable] = {}
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """Register a fallback function for a service."""
        self.fallback_functions[service_name] = fallback_func
        logger.info("[NEXUS] Registered fallback for service: %s", service_name)
    
    def get_fallback(self, service_name: str) -> Optional[Callable]:
        """Get fallback function for a service."""
        return self.fallback_functions.get(service_name)


fallback_handler = FallbackHandler()


def with_fallback(service_name: str, default_return: Any = None):
    """
    Decorator for graceful degradation with fallback.
    
    Args:
        service_name: Name of the service (for fallback lookup)
        default_return: Default return value if no fallback available
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    "[NEXUS] Service %s failed, attempting fallback: %s",
                    service_name, str(e)
                )
                
                fallback_func = fallback_handler.get_fallback(service_name)
                if fallback_func:
                    try:
                        if asyncio.iscoroutinefunction(fallback_func):
                            return await fallback_func(*args, **kwargs)
                        else:
                            return fallback_func(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(
                            "[NEXUS] Fallback for service %s also failed: %s",
                            service_name, str(fallback_error)
                        )
                
                # Return default if no fallback or fallback failed
                logger.info("[NEXUS] Using default return for service %s", service_name)
                return default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    "[NEXUS] Service %s failed, attempting fallback: %s",
                    service_name, str(e)
                )
                
                fallback_func = fallback_handler.get_fallback(service_name)
                if fallback_func:
                    try:
                        return fallback_func(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(
                            "[NEXUS] Fallback for service %s also failed: %s",
                            service_name, str(fallback_error)
                        )
                
                logger.info("[NEXUS] Using default return for service %s", service_name)
                return default_return
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ── Bulkhead Pattern ──────────────────────────────────────────────────────────

class Bulkhead:
    """
    Bulkhead pattern for limiting concurrent operations.
    Prevents resource exhaustion by limiting concurrent calls.
    """
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
    
    async def __aenter__(self):
        await self.semaphore.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()


def bulkhead(max_concurrent: int = 10):
    """
    Decorator for bulkhead pattern.
    
    Args:
        max_concurrent: Maximum number of concurrent executions
    """
    bulkhead_instance = Bulkhead(max_concurrent)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            async with bulkhead_instance:
                return await func(*args, **kwargs)
        
        return async_wrapper
    
    return decorator


# ── Timeout Handler ────────────────────────────────────────────────────────────

async def with_timeout(coro, timeout_seconds: float, timeout_message: str = "Operation timed out"):
    """
    Execute a coroutine with a timeout.
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Timeout in seconds
        timeout_message: Message to use if timeout occurs
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        # Import at runtime to avoid circular imports
        from app.core.errors import TimeoutError as NexusTimeoutError  # type: ignore
        raise NexusTimeoutError(timeout_message)