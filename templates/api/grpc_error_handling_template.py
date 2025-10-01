"""gRPC Error Handling Template for iacherie Platform

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Version: 1.0.0
"""

import grpc
import time
import json
import uuid
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable, Union, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import Future
import threading
from functools import wraps
import asyncio
import contextlib

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    SYSTEM = "system"
    RATE_LIMITING = "rate_limiting"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"

@dataclass
class ErrorDetails:
    """Detailed error information"""
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    grpc_code: grpc.StatusCode = grpc.StatusCode.UNKNOWN
    error_message: str = ""
    error_details: str = ""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.SYSTEM
    service_name: str = ""
    method_name: str = ""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0
    context_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['grpc_code'] = self.grpc_code.name
        data['severity'] = self.severity.value
        data['category'] = self.category.value
        return data

class GRPCErrorHandler:
    """Enhanced gRPC error handler with comprehensive error management"""
    
    def __init__(
        self,
        service_name: str,
        enable_detailed_errors: bool = True,
        enable_error_logging: bool = True,
        enable_metrics: bool = True,
        error_callback: Optional[Callable[[ErrorDetails], None]] = None
    ):
        self.service_name = service_name
        self.enable_detailed_errors = enable_detailed_errors
        self.enable_error_logging = enable_error_logging
        self.enable_metrics = enable_metrics
        self.error_callback = error_callback
        
        # Error statistics
        self.error_counts: Dict[str, int] = {}
        self.error_by_category: Dict[ErrorCategory, int] = {}
        self.error_by_severity: Dict[ErrorSeverity, int] = {}
        self.total_errors = 0
        self._lock = threading.Lock()
        
        # Rate limiting for error logging
        self.error_rate_limit: Dict[str, float] = {}
        self.rate_limit_window = 60  # seconds
        self.max_errors_per_window = 10
        
        logger.info(f"gRPC Error Handler initialized for service: {service_name}")
    
    def _should_log_error(self, error_key: str) -> bool:
        """Check if error should be logged based on rate limiting"""
        current_time = time.time()
        
        with self._lock:
            if error_key not in self.error_rate_limit:
                self.error_rate_limit[error_key] = current_time
                return True
            
            time_since_last = current_time - self.error_rate_limit[error_key]
            if time_since_last > self.rate_limit_window:
                self.error_rate_limit[error_key] = current_time
                return True
            
            # Check error count in current window
            error_count = self.error_counts.get(error_key, 0)
            if error_count < self.max_errors_per_window:
                return True
            
            return False
    
    def _update_error_metrics(self, error_details: ErrorDetails):
        """Update error metrics and statistics"""
        if not self.enable_metrics:
            return
        
        with self._lock:
            # Update total errors
            self.total_errors += 1
            
            # Update error counts by type
            error_key = f"{error_details.grpc_code.name}:{error_details.method_name}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            # Update category counts
            category = error_details.category
            self.error_by_category[category] = self.error_by_category.get(category, 0) + 1
            
            # Update severity counts
            severity = error_details.severity
            self.error_by_severity[severity] = self.error_by_severity.get(severity, 0) + 1
    
    def _log_error(self, error_details: ErrorDetails):
        """Log error with appropriate level"""
        if not self.enable_error_logging:
            return
        
        error_key = f"{error_details.grpc_code.name}:{error_details.method_name}"
        
        if not self._should_log_error(error_key):
            return
        
        log_data = {
            'error_id': error_details.error_id,
            'service': error_details.service_name,
            'method': error_details.method_name,
            'grpc_code': error_details.grpc_code.name,
            'message': error_details.error_message,
            'category': error_details.category.value,
            'severity': error_details.severity.value,
            'user_id': error_details.user_id,
            'request_id': error_details.request_id,
            'client_ip': error_details.client_ip,
            'retry_count': error_details.retry_count
        }
        
        # Log based on severity
        if error_details.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical gRPC error: {json.dumps(log_data)}")
        elif error_details.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity gRPC error: {json.dumps(log_data)}")
        elif error_details.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity gRPC error: {json.dumps(log_data)}")
        else:
            logger.info(f"Low severity gRPC error: {json.dumps(log_data)}")
        
        # Log stack trace for critical errors
        if error_details.severity == ErrorSeverity.CRITICAL and error_details.stack_trace:
            logger.critical(f"Stack trace for error {error_details.error_id}: {error_details.stack_trace}")
    
    def handle_exception(
        self,
        exception: Exception,
        context: grpc.ServicerContext,
        method_name: str,
        **kwargs
    ) -> ErrorDetails:
        """Handle exception and convert to gRPC error"""
        
        # Extract context information
        user_id = kwargs.get('user_id')
        request_id = kwargs.get('request_id')
        client_ip = self._get_client_ip(context)
        
        # Determine gRPC status code and error details
        grpc_code, error_message, severity, category = self._classify_exception(exception)
        
        # Create error details
        error_details = ErrorDetails(
            grpc_code=grpc_code,
            error_message=error_message,
            error_details=str(exception),
            severity=severity,
            category=category,
            service_name=self.service_name,
            method_name=method_name,
            user_id=user_id,
            request_id=request_id,
            client_ip=client_ip,
            context_data=kwargs
        )
        
        # Add stack trace for critical errors
        if severity == ErrorSeverity.CRITICAL:
            error_details.stack_trace = traceback.format_exc()
        
        # Update metrics
        self._update_error_metrics(error_details)
        
        # Log error
        self._log_error(error_details)
        
        # Call error callback if provided
        if self.error_callback:
            try:
                self.error_callback(error_details)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
        
        # Set gRPC error status
        self._set_grpc_error(context, error_details)
        
        return error_details
    
    def _classify_exception(self, exception: Exception) -> tuple:
        """Classify exception to determine gRPC code, message, severity, and category"""
        
        # Authentication errors
        if isinstance(exception, (PermissionError, ValueError)) and "auth" in str(exception).lower():
            return (
                grpc.StatusCode.UNAUTHENTICATED,
                "Authentication failed",
                ErrorSeverity.MEDIUM,
                ErrorCategory.AUTHENTICATION
            )
        
        # Authorization errors
        if isinstance(exception, PermissionError):
            return (
                grpc.StatusCode.PERMISSION_DENIED,
                "Permission denied",
                ErrorSeverity.MEDIUM,
                ErrorCategory.AUTHORIZATION
            )
        
        # Validation errors
        if isinstance(exception, ValueError):
            return (
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid input parameters",
                ErrorSeverity.LOW,
                ErrorCategory.VALIDATION
            )
        
        # Timeout errors
        if isinstance(exception, asyncio.TimeoutError) or "timeout" in str(exception).lower():
            return (
                grpc.StatusCode.DEADLINE_EXCEEDED,
                "Request timeout",
                ErrorSeverity.MEDIUM,
                ErrorCategory.TIMEOUT
            )
        
        # Resource exhausted
        if "resource" in str(exception).lower() or "limit" in str(exception).lower():
            return (
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                "Resource limit exceeded",
                ErrorSeverity.HIGH,
                ErrorCategory.RESOURCE_EXHAUSTED
            )
        
        # Network errors
        if isinstance(exception, ConnectionError) or "network" in str(exception).lower():
            return (
                grpc.StatusCode.UNAVAILABLE,
                "Service temporarily unavailable",
                ErrorSeverity.HIGH,
                ErrorCategory.NETWORK
            )
        
        # Database errors
        if "database" in str(exception).lower() or "sql" in str(exception).lower():
            return (
                grpc.StatusCode.INTERNAL,
                "Database error",
                ErrorSeverity.HIGH,
                ErrorCategory.DATABASE
            )
        
        # Rate limiting
        if "rate" in str(exception).lower() or "throttle" in str(exception).lower():
            return (
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                "Rate limit exceeded",
                ErrorSeverity.MEDIUM,
                ErrorCategory.RATE_LIMITING
            )
        
        # Not found
        if isinstance(exception, (FileNotFoundError, KeyError)) or "not found" in str(exception).lower():
            return (
                grpc.StatusCode.NOT_FOUND,
                "Resource not found",
                ErrorSeverity.LOW,
                ErrorCategory.BUSINESS_LOGIC
            )
        
        # Already exists
        if "already exists" in str(exception).lower() or "duplicate" in str(exception).lower():
            return (
                grpc.StatusCode.ALREADY_EXISTS,
                "Resource already exists",
                ErrorSeverity.LOW,
                ErrorCategory.BUSINESS_LOGIC
            )
        
        # Default: Internal error
        return (
            grpc.StatusCode.INTERNAL,
            "Internal server error",
            ErrorSeverity.CRITICAL,
            ErrorCategory.SYSTEM
        )
    
    def _get_client_ip(self, context: grpc.ServicerContext) -> Optional[str]:
        """Extract client IP from gRPC context"""
        try:
            peer = context.peer()
            if peer and peer.startswith('ipv4:'):
                return peer.split(':')[1]
            elif peer and peer.startswith('ipv6:'):
                return peer.split(':')[1]
        except Exception:
            pass
        return None
    
    def _set_grpc_error(self, context: grpc.ServicerContext, error_details: ErrorDetails):
        """Set gRPC error status with details"""
        
        # Prepare error message
        if self.enable_detailed_errors:
            error_message = f"{error_details.error_message} (Error ID: {error_details.error_id})"
        else:
            error_message = error_details.error_message
        
        # Set status
        context.set_code(error_details.grpc_code)
        context.set_details(error_message)
        
        # Add custom headers if needed
        context.send_initial_metadata([
            ('error-id', error_details.error_id),
            ('error-category', error_details.category.value),
            ('error-severity', error_details.severity.value)
        ])
    
    def create_business_error(
        self,
        message: str,
        grpc_code: grpc.StatusCode = grpc.StatusCode.FAILED_PRECONDITION,
        severity: ErrorSeverity = ErrorSeverity.LOW,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        **context_data
    ) -> ErrorDetails:
        """Create business logic error"""
        
        return ErrorDetails(
            grpc_code=grpc_code,
            error_message=message,
            error_details=message,
            severity=severity,
            category=category,
            service_name=self.service_name,
            context_data=context_data
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            return {
                'total_errors': self.total_errors,
                'error_counts': dict(self.error_counts),
                'errors_by_category': {k.value: v for k, v in self.error_by_category.items()},
                'errors_by_severity': {k.value: v for k, v in self.error_by_severity.items()},
                'service_name': self.service_name
            }
    
    def reset_statistics(self):
        """Reset error statistics"""
        with self._lock:
            self.error_counts.clear()
            self.error_by_category.clear()
            self.error_by_severity.clear()
            self.total_errors = 0
            self.error_rate_limit.clear()

# Retry mechanism for gRPC clients
class RetryConfig:
    """Configuration for retry mechanism"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_status_codes: Optional[List[grpc.StatusCode]] = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        
        # Default retryable status codes
        if retryable_status_codes is None:
            self.retryable_status_codes = [
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                grpc.StatusCode.ABORTED
            ]
        else:
            self.retryable_status_codes = retryable_status_codes

def with_retry(retry_config: RetryConfig):
    """Decorator for adding retry mechanism to gRPC calls"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except grpc.RpcError as e:
                    last_exception = e
                    
                    # Check if error is retryable
                    if e.code() not in retry_config.retryable_status_codes:
                        raise e
                    
                    # Don't retry on last attempt
                    if attempt == retry_config.max_retries:
                        break
                    
                    # Calculate delay
                    delay = retry_config.base_delay * (retry_config.exponential_base ** attempt)
                    delay = min(delay, retry_config.max_delay)
                    
                    # Add jitter
                    if retry_config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.info(f"Retrying gRPC call after {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_retries})")
                    time.sleep(delay)
                
                except Exception as e:
                    # Non-gRPC exceptions are not retryable
                    raise e
            
            # Re-raise last exception if all retries failed
            raise last_exception
        
        return wrapper
    return decorator

# Error handling interceptors
class ErrorHandlingInterceptor(grpc.ServerInterceptor):
    """Server interceptor for error handling"""
    
    def __init__(self, error_handler: GRPCErrorHandler):
        self.error_handler = error_handler
    
    def intercept_service(self, continuation, handler_call_details):
        """Intercept service calls"""
        def new_behavior(request, context):
            try:
                return continuation(request, context)
            except Exception as e:
                method_name = handler_call_details.method.split('/')[-1]
                self.error_handler.handle_exception(e, context, method_name)
                # The error handler sets the gRPC status, so we don't need to return anything
                return None
        
        return new_behavior

class ClientErrorInterceptor(grpc.UnaryUnaryClientInterceptor):
    """Client interceptor for error handling and logging"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept client calls"""
        try:
            response = continuation(client_call_details, request)
            return response
            
        except grpc.RpcError as e:
            # Log client-side error
            logger.error(f"gRPC call failed: {client_call_details.method}, "
                        f"Status: {e.code()}, Details: {e.details()}")
            
            # Re-raise the error
            raise e

# Circuit breaker for gRPC calls
class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for gRPC calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self._lock = threading.Lock()
    
    @contextlib.contextmanager
    def call(self):
        """Context manager for circuit breaker calls"""
        if not self._can_call():
            raise grpc.RpcError(grpc.StatusCode.UNAVAILABLE, "Circuit breaker is open")
        
        try:
            yield
            self._on_success()
        except Exception as e:
            self._on_failure()
            raise e
    
    def _can_call(self) -> bool:
        """Check if call can be made"""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    return True
                return False
            else:  # HALF_OPEN
                return True
    
    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN

# Error recovery strategies
class ErrorRecoveryStrategy:
    """Base class for error recovery strategies"""
    
    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        """Retry function with exponential backoff"""
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                delay = min(base_delay * (2 ** attempt), max_delay)
                time.sleep(delay)
    
    @staticmethod
    def fallback_on_error(primary_func: Callable, fallback_func: Callable):
        """Execute fallback function on error"""
        try:
            return primary_func()
        except Exception:
            return fallback_func()

# Configuration template
GRPC_ERROR_HANDLING_CONFIG = {
    "error_handler": {
        "enable_detailed_errors": True,
        "enable_error_logging": True,
        "enable_metrics": True,
        "rate_limit_window": 60,
        "max_errors_per_window": 10
    },
    "retry": {
        "max_retries": 3,
        "base_delay": 1.0,
        "max_delay": 60.0,
        "exponential_base": 2.0,
        "jitter": True,
        "retryable_status_codes": [
            "UNAVAILABLE",
            "DEADLINE_EXCEEDED",
            "RESOURCE_EXHAUSTED",
            "ABORTED"
        ]
    },
    "circuit_breaker": {
        "failure_threshold": 5,
        "timeout": 60.0,
        "success_threshold": 3
    }
}

if __name__ == "__main__":
    # Example usage
    error_handler = GRPCErrorHandler("test_service")
    
    # Simulate handling exceptions
    try:
        raise ValueError("Invalid input parameter")
    except Exception as e:
        error_details = error_handler.handle_exception(
            e, 
            None,  # Mock context
            "TestMethod",
            user_id="user123",
            request_id="req456"
        )
        print(f"Handled error: {error_details.error_id}")
    
    # Print statistics
    stats = error_handler.get_error_statistics()
    print("Error Statistics:", json.dumps(stats, indent=2))