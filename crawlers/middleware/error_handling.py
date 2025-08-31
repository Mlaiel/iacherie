"""Error Handling Middleware Module
===============================

Enterprise-grade error handling middleware for crawler pipeline.
Implements comprehensive error management, recovery, and reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Error Handling:
- Multi-format content processing error recovery
- Creator workflow continuity assurance
- AI protection system failure handling
- Monetization transaction error management
- Cross-platform distribution error mitigation
"""
import asyncio
import json
import time
import traceback
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
import threading
from collections import defaultdict

from pydantic import BaseModel, Field
import redis

from ...config.settings import get_settings
from ...utils.cache import CacheManager

settings = get_settings()
logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class ErrorCategory(str, Enum):
    """Error categories"""    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    PROCESSING = "processing"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    SECURITY = "security"
    RATE_LIMITING = "rate_limiting"
    CONTENT_PROCESSING = "content_processing"
    FINGERPRINTING = "fingerprinting"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    PLATFORM_INTEGRATION = "platform_integration"


class RecoveryAction(str, Enum):
    """Recovery actions"""    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ESCALATE = "escalate"
    TERMINATE = "terminate"
    QUARANTINE = "quarantine"
    ROLLBACK = "rollback"
    ALTERNATIVE_PROCESSING = "alternative_processing"


class BusinessImpact(str, Enum):
    """Business impact levels"""    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"


class ErrorInfo(BaseModel):
    """Enhanced error information model"""    error_id: str = Field(description="Unique error identifier")
    error_type: str = Field(description="Type of error")
    error_message: str = Field(description="Error message")
    severity: ErrorSeverity = Field(description="Error severity")
    category: ErrorCategory = Field(description="Error category")
    business_impact: BusinessImpact = Field(description="Business impact level")
    timestamp: datetime = Field(description="Error timestamp")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    content_id: Optional[str] = Field(None, description="Content ID if applicable")
    request_id: Optional[str] = Field(None, description="Request ID if applicable")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")
    upstream_errors: List[str] = Field(default_factory=list, description="Related upstream errors")
    recovery_attempts: int = Field(default=0, description="Number of recovery attempts")


class RecoveryStrategy(BaseModel):
    """Enhanced error recovery strategy"""    strategy_id: str = Field(description="Strategy identifier")
    error_types: List[str] = Field(description="Applicable error types")
    error_categories: List[ErrorCategory] = Field(description="Applicable error categories")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Retry delay in seconds")
    exponential_backoff: bool = Field(default=True, description="Use exponential backoff")
    backoff_multiplier: float = Field(default=2.0, description="Backoff multiplier")
    jitter: bool = Field(default=True, description="Add jitter to retry delays")
    circuit_breaker_threshold: int = Field(default=5, description="Circuit breaker threshold")
    recovery_timeout: int = Field(default=30, description="Recovery timeout in seconds")
    fallback_strategies: List[str] = Field(default_factory=list, description="Fallback strategies")
    business_continuity: bool = Field(default=True, description="Enable business continuity")


@dataclass
class CircuitBreakerState:
    """Circuit breaker state management"""    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    reset_timeout: int = 60
    lock: threading.RLock = None
    
    def __post_init__(self):
        if self.lock is None:
            self.lock = threading.RLock()


class ErrorRecoveryManager:
    """Advanced error recovery management with business continuity"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        self.recovery_strategies = {}
        self.circuit_breakers = defaultdict(CircuitBreakerState)
        self.error_statistics = defaultdict(lambda: defaultdict(int))
        self.business_continuity_handlers = {}
        
        # Initialize default recovery strategies
        self._initialize_default_strategies()
        self._initialize_business_continuity_handlers()
    
    def _initialize_default_strategies(self):
        """Initialize default recovery strategies"""        # Network error strategy
        self.recovery_strategies["network"] = RecoveryStrategy(
            strategy_id="network_recovery",
            error_types=["ConnectionError", "TimeoutError", "HTTPError"],
            max_retries=3,
            retry_delay=2.0,
            exponential_backoff=True,
            recovery_timeout=30
        )
        
        # Database error strategy
        self.recovery_strategies["database"] = RecoveryStrategy(
            strategy_id="database_recovery",
            error_types=["DatabaseError", "OperationalError", "ConnectionError"],
            max_retries=2,
            retry_delay=5.0,
            exponential_backoff=True,
            recovery_timeout=60
        )
        
        # External service strategy
        self.recovery_strategies["external_service"] = RecoveryStrategy(
            strategy_id="external_service_recovery",
            error_types=["ServiceUnavailable", "APIError", "ThirdPartyError"],
            max_retries=2,
            retry_delay=3.0,
            exponential_backoff=True,
            recovery_timeout=45
        )
        
        # Processing error strategy
        self.recovery_strategies["processing"] = RecoveryStrategy(
            strategy_id="processing_recovery",
            error_types=["ProcessingError", "ValidationError", "TransformationError"],
            max_retries=1,
            retry_delay=1.0,
            exponential_backoff=False,
            recovery_timeout=15
        )
    
    async def handle_error_with_recovery(self, error: Exception, 
                                       context: Dict[str, Any],
                                       operation: Callable) -> Any:
        """Handle error with automatic recovery"""        error_type = type(error).__name__
        strategy = await self.get_recovery_strategy(error_type)
        
        if not strategy:
            # No recovery strategy, re-raise error
            raise error
        
        # Check circuit breaker
        if await self.is_circuit_breaker_open(error_type):
            logger.warning(f"Circuit breaker open for {error_type}, skipping recovery")
            raise error
        
        # Attempt recovery
        return await self.execute_recovery(error, strategy, context, operation)
    
    async def get_recovery_strategy(self, error_type: str) -> Optional[RecoveryStrategy]:
        """Get appropriate recovery strategy for error type"""        for category, strategy in self.recovery_strategies.items():
            if error_type in strategy.error_types:
                return strategy
        return None
    
    async def execute_recovery(self, error: Exception, 
                             strategy: RecoveryStrategy,
                             context: Dict[str, Any],
                             operation: Callable) -> Any:
        """Execute recovery strategy"""        attempt = 0
        last_error = error
        
        while attempt < strategy.max_retries:
            attempt += 1
            
            # Calculate delay with exponential backoff
            if strategy.exponential_backoff:
                delay = strategy.retry_delay * (2 ** (attempt - 1))
            else:
                delay = strategy.retry_delay
            
            logger.info(f"Recovery attempt {attempt}/{strategy.max_retries} for {type(error).__name__} after {delay}s")
            
            # Wait before retry
            await asyncio.sleep(delay)
            
            try:
                # Retry operation
                result = await operation()
                
                # Success - reset circuit breaker
                await self.reset_circuit_breaker(type(error).__name__)
                
                logger.info(f"Recovery successful after {attempt} attempts")
                return result
                
            except Exception as retry_error:
                last_error = retry_error
                logger.warning(f"Recovery attempt {attempt} failed: {retry_error}")
                
                # Track failure
                await self.track_recovery_failure(type(error).__name__)
        
        # All retries failed - update circuit breaker
        await self.update_circuit_breaker(type(error).__name__)
        
        logger.error(f"Recovery failed after {strategy.max_retries} attempts")
        raise last_error
    
    async def is_circuit_breaker_open(self, error_type: str) -> bool:
        """Check if circuit breaker is open for error type"""        cb_key = f"circuit_breaker:{error_type}"
        cb_data = await self.redis_client.get(cb_key)
        
        if not cb_data:
            return False
        
        cb_info = json.loads(cb_data)
        
        # Check if circuit breaker timeout has passed
        if time.time() > cb_info.get("opens_until", 0):
            await self.redis_client.delete(cb_key)
            return False
        
        return cb_info.get("state") == "open"
    
    async def track_recovery_failure(self, error_type: str):
        """Track recovery failure for circuit breaker logic"""        failure_key = f"recovery_failures:{error_type}"
        failures = await self.redis_client.incr(failure_key)
        await self.redis_client.expire(failure_key, 300)  # 5 minutes window
        
        return failures
    
    async def update_circuit_breaker(self, error_type: str):
        """Update circuit breaker state based on failures"""        failures = await self.track_recovery_failure(error_type)
        
        # Open circuit breaker if too many failures
        if failures >= 5:  # Threshold
            cb_key = f"circuit_breaker:{error_type}"
            cb_data = {
                "state": "open",
                "opened_at": time.time(),
                "opens_until": time.time() + 300,  # 5 minutes
                "failure_count": failures
            }
            
            await self.redis_client.set(cb_key, json.dumps(cb_data), ex=300)
            logger.warning(f"Circuit breaker opened for {error_type}")
    
    async def reset_circuit_breaker(self, error_type: str):
        """Reset circuit breaker after successful operation"""        cb_key = f"circuit_breaker:{error_type}"
        failure_key = f"recovery_failures:{error_type}"
        
        await self.redis_client.delete(cb_key)
        await self.redis_client.delete(failure_key)


class ErrorReporter:
    """Comprehensive error reporting and analytics"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        
    async def report_error(self, error_info: ErrorInfo):
        """Report error for monitoring and analytics"""        try:
            # Store detailed error information
            error_key = f"errors:{error_info.error_id}"
            error_data = {
                "error_type": error_info.error_type,
                "error_message": error_info.error_message,
                "severity": error_info.severity.value,
                "category": error_info.category.value,
                "timestamp": error_info.timestamp.isoformat(),
                "context": json.dumps(error_info.context),
                "stack_trace": error_info.stack_trace or "",
                "user_id": error_info.user_id or "",
                "request_id": error_info.request_id or ""
            }
            
            await self.redis_client.hmset(error_key, error_data)
            await self.redis_client.expire(error_key, 86400 * 7)  # Keep for 7 days
            
            # Update error statistics
            await self.update_error_statistics(error_info)
            
            # Add to error timeline
            timeline_key = f"error_timeline:{error_info.category.value}"
            await self.redis_client.zadd(timeline_key, {error_info.error_id: error_info.timestamp.timestamp()})
            await self.redis_client.expire(timeline_key, 86400 * 7)
            
            # Send alerts for critical errors
            if error_info.severity == ErrorSeverity.CRITICAL:
                await self.send_critical_error_alert(error_info)
            
        except Exception as e:
            logger.error(f"Error reporting failed: {e}")
    
    async def update_error_statistics(self, error_info: ErrorInfo):
        """Update error statistics for monitoring"""        now = time.time()
        hour_window = int(now // 3600)
        day_window = int(now // 86400)
        
        # Update hourly statistics
        await self.redis_client.incr(f"error_stats:hourly:{hour_window}:total")
        await self.redis_client.incr(f"error_stats:hourly:{hour_window}:{error_info.category.value}")
        await self.redis_client.incr(f"error_stats:hourly:{hour_window}:{error_info.severity.value}")
        
        # Update daily statistics
        await self.redis_client.incr(f"error_stats:daily:{day_window}:total")
        await self.redis_client.incr(f"error_stats:daily:{day_window}:{error_info.category.value}")
        await self.redis_client.incr(f"error_stats:daily:{day_window}:{error_info.severity.value}")
        
        # Set expiration
        await self.redis_client.expire(f"error_stats:hourly:{hour_window}:total", 86400 * 7)
        await self.redis_client.expire(f"error_stats:daily:{day_window}:total", 86400 * 30)
    
    async def send_critical_error_alert(self, error_info: ErrorInfo):
        """Send alert for critical errors"""        alert = {
            "type": "critical_error",
            "error_id": error_info.error_id,
            "error_type": error_info.error_type,
            "message": error_info.error_message,
            "severity": error_info.severity.value,
            "category": error_info.category.value,
            "timestamp": error_info.timestamp.isoformat(),
            "context": error_info.context
        }
        
        # Log critical error
        logger.critical(f"CRITICAL ERROR: {error_info.error_message}")
        
        # Store in critical alerts
        await self.redis_client.lpush("critical_errors", json.dumps(alert))
        await self.redis_client.ltrim("critical_errors", 0, 100)  # Keep last 100
    
    async def get_error_statistics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get error statistics for specified time range"""        try:
            now = time.time()
            
            if time_range == "1h":
                window = int(now // 3600)
                prefix = "error_stats:hourly"
                windows = [window]
            elif time_range == "24h":
                window = int(now // 3600)
                prefix = "error_stats:hourly"
                windows = [window - i for i in range(24)]
            elif time_range == "7d":
                window = int(now // 86400)
                prefix = "error_stats:daily"
                windows = [window - i for i in range(7)]
            else:
                return {"error": "Invalid time range"}
            
            # Collect statistics
            total_errors = 0
            category_stats = {}
            severity_stats = {}
            
            for w in windows:
                # Total errors
                total = await self.redis_client.get(f"{prefix}:{w}:total") or 0
                total_errors += int(total)
                
                # Category breakdown
                for category in ErrorCategory:
                    count = await self.redis_client.get(f"{prefix}:{w}:{category.value}") or 0
                    category_stats[category.value] = category_stats.get(category.value, 0) + int(count)
                
                # Severity breakdown
                for severity in ErrorSeverity:
                    count = await self.redis_client.get(f"{prefix}:{w}:{severity.value}") or 0
                    severity_stats[severity.value] = severity_stats.get(severity.value, 0) + int(count)
            
            return {
                "time_range": time_range,
                "total_errors": total_errors,
                "category_breakdown": category_stats,
                "severity_breakdown": severity_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error statistics retrieval error: {e}")
            return {"error": str(e)}


class ErrorHandlingMiddleware:
    """Main error handling middleware orchestrator"""    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        
        # Initialize components
        self.recovery_manager = ErrorRecoveryManager(self.redis_client)
        self.error_reporter = ErrorReporter(self.redis_client)
        
        # Error handling configuration
        self.error_handling_enabled = True
        self.auto_recovery_enabled = True
        self.detailed_logging = True
    
    async def handle_error(self, error: Exception, 
                         context: Dict[str, Any] = None,
                         operation: Callable = None) -> Any:
        """Main error handling method"""        try:
            # Create error information
            error_info = await self.create_error_info(error, context)
            
            # Report error
            await self.error_reporter.report_error(error_info)
            
            # Log error
            await self.log_error(error_info)
            
            # Attempt recovery if operation provided and auto-recovery enabled
            if operation and self.auto_recovery_enabled:
                try:
                    return await self.recovery_manager.handle_error_with_recovery(
                        error, context or {}, operation
                    )
                except Exception as recovery_error:
                    # Recovery failed, log and re-raise original error
                    logger.error(f"Error recovery failed: {recovery_error}")
                    raise error
            
            # No recovery attempted or available
            raise error
            
        except Exception as handling_error:
            # Error in error handling - log and re-raise original
            logger.critical(f"Error handling failed: {handling_error}")
            raise error
    
    async def create_error_info(self, error: Exception, 
                              context: Dict[str, Any] = None) -> ErrorInfo:
        """Create comprehensive error information"""        error_id = f"error_{int(time.time() * 1000)}"
        error_type = type(error).__name__
        error_message = str(error)
        
        # Determine severity
        severity = self.determine_error_severity(error_type, error_message)
        
        # Determine category
        category = self.determine_error_category(error_type, error_message)
        
        # Get stack trace
        stack_trace = None
        if self.detailed_logging:
            stack_trace = traceback.format_exc()
        
        return ErrorInfo(
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            category=category,
            timestamp=datetime.utcnow(),
            context=context or {},
            stack_trace=stack_trace,
            user_id=context.get("user_id") if context else None,
            request_id=context.get("request_id") if context else None
        )
    
    def determine_error_severity(self, error_type: str, error_message: str) -> ErrorSeverity:
        """Determine error severity based on type and message"""        critical_keywords = ["critical", "fatal", "security", "breach", "corruption"]
        high_keywords = ["timeout", "connection", "database", "service"]
        medium_keywords = ["validation", "permission", "rate limit"]
        
        error_text = (error_type + " " + error_message).lower()
        
        if any(keyword in error_text for keyword in critical_keywords):
            return ErrorSeverity.CRITICAL
        elif any(keyword in error_text for keyword in high_keywords):
            return ErrorSeverity.HIGH
        elif any(keyword in error_text for keyword in medium_keywords):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def determine_error_category(self, error_type: str, error_message: str) -> ErrorCategory:
        """Determine error category based on type and message"""        category_mapping = {
            "authentication": ["auth", "login", "token", "credential"],
            "authorization": ["permission", "access", "forbidden", "unauthorized"],
            "validation": ["validation", "invalid", "format", "schema"],
            "network": ["connection", "network", "timeout", "http"],
            "database": ["database", "sql", "query", "connection"],
            "security": ["security", "attack", "breach", "malicious"],
            "rate_limiting": ["rate", "limit", "throttle", "quota"],
            "system": ["memory", "disk", "cpu", "system"]
        }
        
        error_text = (error_type + " " + error_message).lower()
        
        for category, keywords in category_mapping.items():
            if any(keyword in error_text for keyword in keywords):
                return ErrorCategory(category)
        
        return ErrorCategory.PROCESSING  # Default category
    
    async def log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""        log_message = f"[{error_info.error_id}] {error_info.error_type}: {error_info.error_message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Log additional context if available
        if error_info.context and self.detailed_logging:
            logger.debug(f"Error context: {json.dumps(error_info.context, indent=2)}")
        
        # Log stack trace for high severity errors
        if error_info.stack_trace and error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.debug(f"Stack trace:\n{error_info.stack_trace}")
    
    @asynccontextmanager
    async def error_context(self, context: Dict[str, Any] = None):
        """Context manager for automatic error handling"""        try:
            yield
        except Exception as error:
            await self.handle_error(error, context)
    
    async def get_error_dashboard_data(self) -> Dict[str, Any]:
        """Get error data for monitoring dashboard"""        try:
            # Get error statistics
            hourly_stats = await self.error_reporter.get_error_statistics("24h")
            daily_stats = await self.error_reporter.get_error_statistics("7d")
            
            # Get recent critical errors
            critical_errors = await self.redis_client.lrange("critical_errors", 0, 10)
            recent_critical = [json.loads(error) for error in critical_errors]
            
            # Get circuit breaker status
            cb_keys = await self.redis_client.keys("circuit_breaker:*")
            circuit_breakers = {}
            for key in cb_keys:
                cb_data = await self.redis_client.get(key)
                if cb_data:
                    error_type = key.decode().split(":")[-1]
                    circuit_breakers[error_type] = json.loads(cb_data)
            
            return {
                "hourly_statistics": hourly_stats,
                "daily_statistics": daily_stats,
                "recent_critical_errors": recent_critical,
                "circuit_breakers": circuit_breakers,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error dashboard data retrieval error: {e}")
            return {"error": str(e)}


# Factory function for dependency injection
def get_error_handling_middleware() -> ErrorHandlingMiddleware:
    """Get error handling middleware instance"""    return ErrorHandlingMiddleware()


# Decorator for automatic error handling
def handle_errors(context: Dict[str, Any] = None, auto_recovery: bool = True):
    """Decorator for automatic error handling"""    def decorator(func):
        async def wrapper(*args, **kwargs):
            middleware = get_error_handling_middleware()
            
            # Create operation function for recovery
            async def operation():
                return await func(*args, **kwargs)
            
            try:
                return await func(*args, **kwargs)
            except Exception as error:
                # Add function context
                error_context = context or {}
                error_context.update({
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                })
                
                if auto_recovery:
                    return await middleware.handle_error(error, error_context, operation)
                else:
                    await middleware.handle_error(error, error_context)
        
        return wrapper
    return decorator


# Utility functions
async def report_error(error: Exception, context: Dict[str, Any] = None):
    """Convenience function for error reporting"""    middleware = get_error_handling_middleware()
    await middleware.handle_error(error, context)


async def get_error_statistics(time_range: str = "24h") -> Dict[str, Any]:
    """Convenience function for getting error statistics"""    middleware = get_error_handling_middleware()
    return await middleware.error_reporter.get_error_statistics(time_range)
