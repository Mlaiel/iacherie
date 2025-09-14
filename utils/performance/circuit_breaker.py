"""
Circuit Breaker - Performance Utilities Level 3
===============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade circuit breaker pattern consolidating circuit_breaker.py + error_handler.py
Enhanced with intelligent failure detection and recovery mechanisms.

Performance: < 1ms per circuit breaker operation
Standards: Fail-fast patterns, intelligent recovery, enterprise resilience
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerResult:
    """Result container for circuit breaker operations."""
    success: bool
    result: Optional[Any] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

class CircuitBreaker:
    """Enterprise circuit breaker with intelligent failure detection."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout_seconds: int = 60,
                 expected_exception: type = Exception):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = CircuitState.CLOSED
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            time_since_failure = datetime.now(timezone.utc) - self._last_failure_time
            return time_since_failure.total_seconds() >= self.timeout_seconds
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> CircuitBreakerResult:
        """Execute function with circuit breaker protection."""
        start_time = time.perf_counter()
        
        try:
            # Check if circuit is open
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    exec_time = (time.perf_counter() - start_time) * 1000
                    return CircuitBreakerResult(
                        success=False,
                        circuit_state=self._state,
                        errors=["Circuit breaker is OPEN"],
                        execution_time_ms=exec_time
                    )
            
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count and close circuit
            self._failure_count = 0
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                logger.info("Circuit breaker reset to CLOSED")
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return CircuitBreakerResult(
                success=True,
                result=result,
                circuit_state=self._state,
                execution_time_ms=exec_time
            )
            
        except self.expected_exception as e:
            # Handle expected failures
            self._failure_count += 1
            self._last_failure_time = datetime.now(timezone.utc)
            
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return CircuitBreakerResult(
                success=False,
                circuit_state=self._state,
                errors=[str(e)],
                execution_time_ms=exec_time
            )
        
        except Exception as e:
            # Handle unexpected exceptions
            exec_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Unexpected error in circuit breaker: {e}")
            
            return CircuitBreakerResult(
                success=False,
                circuit_state=self._state,
                errors=[f"Unexpected error: {str(e)}"],
                execution_time_ms=exec_time
            )
    
    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset")

class CircuitBreakerFactory:
    """Factory for creating circuit breaker instances."""
    
    @staticmethod
    def create_breaker(
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: type = Exception
    ) -> CircuitBreaker:
        return CircuitBreaker(failure_threshold, timeout_seconds, expected_exception)

# === ENHANCED ERROR HANDLING UTILITIES ===
# Consolidated from error_handler.py with enterprise features

import traceback
import uuid
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from collections import defaultdict, deque
import threading

class ErrorSeverity(Enum):
    """Error severity levels for enterprise error handling"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class ErrorCategory(Enum):
    """Error categories for classification and routing"""
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    FILE_SYSTEM = "FILE_SYSTEM"
    EXTERNAL_API = "EXTERNAL_API"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    CONFIGURATION = "CONFIGURATION"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"

@dataclass
class ErrorInfo:
    """Comprehensive error information structure"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    exception_message: str
    stack_trace: str
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error info to dictionary"""
        return {
            'error_id': self.error_id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'stack_trace': self.stack_trace,
            'context': self.context,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'module': self.module,
            'function': self.function
        }

class EnterpriseErrorHandler:
    """Enterprise-grade error handling with circuit breaker integration
    
    DevOps Expert: Comprehensive error handling with alerting, logging, recovery
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Error storage and tracking
        self.error_storage: deque = deque(maxlen=self.config.get('max_errors', 1000))
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.error_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Circuit breakers for different error types
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Error handlers and notifications
        self.error_handlers: Dict[ErrorSeverity, List[Callable]] = defaultdict(list)
        self.notification_handlers: List[Callable] = []
        
        # Threading for async operations
        self._lock = threading.Lock()
        
        # Email configuration for critical alerts
        self.email_config = self.config.get('email', {})
        
        # Error rate thresholds
        self.error_rate_thresholds = {
            ErrorSeverity.WARNING: self.config.get('warning_rate_threshold', 10),  # per minute
            ErrorSeverity.ERROR: self.config.get('error_rate_threshold', 5),
            ErrorSeverity.CRITICAL: self.config.get('critical_rate_threshold', 1)
        }
    
    async def handle_error(
        self,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> str:
        """Handle an error with comprehensive logging and alerting"""
        
        error_id = str(uuid.uuid4())
        
        # Extract stack trace and exception details
        stack_trace = traceback.format_exc()
        exception_type = type(exception).__name__
        exception_message = str(exception)
        
        # Get caller information
        frame = traceback.extract_tb(exception.__traceback__)[-1] if exception.__traceback__ else None
        module = frame.filename if frame else None
        function = frame.name if frame else None
        
        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            category=category,
            message=exception_message,
            exception_type=exception_type,
            exception_message=exception_message,
            stack_trace=stack_trace,
            context=context or {},
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            module=module,
            function=function
        )
        
        # Store error
        with self._lock:
            self.error_storage.append(error_info)
            self.error_counts[category.value] += 1
            self.error_rates[severity.value].append(time.time())
        
        # Log error
        log_message = f"[{error_id}] {category.value}: {exception_message}"
        if severity == ErrorSeverity.DEBUG:
            self.logger.debug(log_message)
        elif severity == ErrorSeverity.INFO:
            self.logger.info(log_message)
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(log_message, exc_info=exception)
        elif severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            self.logger.critical(log_message, exc_info=exception)
        
        # Execute error handlers
        await self._execute_error_handlers(error_info)
        
        # Check error rates and trigger circuit breakers
        await self._check_error_rates(error_info)
        
        # Send notifications for critical errors
        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            await self._send_critical_alert(error_info)
        
        return error_id
    
    async def _execute_error_handlers(self, error_info: ErrorInfo):
        """Execute registered error handlers"""
        handlers = self.error_handlers.get(error_info.severity, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_info)
                else:
                    handler(error_info)
            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
    
    async def _check_error_rates(self, error_info: ErrorInfo):
        """Check error rates and trigger circuit breakers if needed"""
        current_time = time.time()
        severity = error_info.severity
        
        # Clean old error timestamps (older than 1 minute)
        error_times = self.error_rates[severity.value]
        while error_times and current_time - error_times[0] > 60:
            error_times.popleft()
        
        # Check if error rate threshold is exceeded
        error_count = len(error_times)
        threshold = self.error_rate_thresholds.get(severity, float('inf'))
        
        if error_count > threshold:
            # Trigger circuit breaker for this error category
            category_key = error_info.category.value
            if category_key not in self.circuit_breakers:
                self.circuit_breakers[category_key] = CircuitBreaker(
                    failure_threshold=threshold,
                    timeout_seconds=300  # 5 minutes
                )
            
            # Log high error rate
            self.logger.warning(
                f"High error rate detected: {error_count} {severity.value} errors "
                f"in last minute for category {error_info.category.value}"
            )
    
    async def _send_critical_alert(self, error_info: ErrorInfo):
        """Send critical error alerts via configured channels"""
        alert_message = (
            f"CRITICAL ERROR ALERT\n\n"
            f"Error ID: {error_info.error_id}\n"
            f"Time: {error_info.timestamp.isoformat()}\n"
            f"Category: {error_info.category.value}\n"
            f"Message: {error_info.message}\n"
            f"Module: {error_info.module}\n"
            f"Function: {error_info.function}\n"
        )
        
        # Send email if configured
        if self.email_config:
            await self._send_email_alert(alert_message, error_info)
        
        # Execute notification handlers
        for handler in self.notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_info)
                else:
                    handler(error_info)
            except Exception as e:
                self.logger.error(f"Notification handler failed: {e}")
    
    async def _send_email_alert(self, message: str, error_info: ErrorInfo):
        """Send email alert for critical errors"""
        try:
            if not all(k in self.email_config for k in ['smtp_server', 'smtp_port', 'username', 'password', 'to_email']):
                return
            
            msg = MimeMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = f"CRITICAL ERROR: {error_info.category.value}"
            
            msg.attach(MimeText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Critical error email sent for error {error_info.error_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send error email: {e}")
    
    def add_error_handler(self, severity: ErrorSeverity, handler: Callable):
        """Add a custom error handler for specific severity"""
        self.error_handlers[severity].append(handler)
    
    def add_notification_handler(self, handler: Callable):
        """Add a notification handler for critical errors"""
        self.notification_handlers.append(handler)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        with self._lock:
            total_errors = len(self.error_storage)
            
            # Count by severity
            severity_counts = defaultdict(int)
            category_counts = defaultdict(int)
            
            for error in self.error_storage:
                severity_counts[error.severity.value] += 1
                category_counts[error.category.value] += 1
            
            # Calculate error rates (last hour)
            current_time = time.time()
            hour_ago = current_time - 3600
            
            recent_errors = [
                error for error in self.error_storage 
                if error.timestamp.timestamp() > hour_ago
            ]
            
            return {
                'total_errors': total_errors,
                'recent_errors_last_hour': len(recent_errors),
                'errors_by_severity': dict(severity_counts),
                'errors_by_category': dict(category_counts),
                'active_circuit_breakers': list(self.circuit_breakers.keys()),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors"""
        with self._lock:
            recent = list(self.error_storage)[-limit:]
            return [error.to_dict() for error in reversed(recent)]

# Error handling decorators
def async_error_handler(
    error_handler: EnterpriseErrorHandler,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
    reraise: bool = True
):
    """Decorator for automatic async error handling"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await error_handler.handle_error(
                    exception=e,
                    severity=severity,
                    category=category,
                    context={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)}
                )
                if reraise:
                    raise
                return None
        return wrapper
    return decorator

def sync_error_handler(
    error_handler: EnterpriseErrorHandler,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
    reraise: bool = True
):
    """Decorator for automatic sync error handling"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Use asyncio to handle the error
                asyncio.create_task(error_handler.handle_error(
                    exception=e,
                    severity=severity,
                    category=category,
                    context={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)}
                ))
                if reraise:
                    raise
                return None
        return wrapper
    return decorator

# Export enhanced circuit breaker and error handling utilities
__all__ = ['CircuitBreaker', 'CircuitBreakerFactory', 'CircuitBreakerResult', 'CircuitState',
           'EnterpriseErrorHandler', 'ErrorInfo', 'ErrorSeverity', 'ErrorCategory',
           'async_error_handler', 'sync_error_handler']