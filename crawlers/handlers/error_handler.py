"""
Error Handler Module
===================

Professional error handling system for crawler operations and platform integrations.
Manages exceptions, error recovery, logging, and alerting with enterprise-grade reliability.

Error Categories Supported:
- Platform API Errors (Rate limits, Authentication, Service unavailable)
- Network Errors (Timeout, Connection, DNS)
- Content Processing Errors (Invalid format, Corrupted data)
- Security Errors (Authentication, Authorization, Validation)
- System Errors (Database, Redis, Storage)
- Business Logic Errors (Invalid operations, Constraint violations)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""

import asyncio
import logging
import json
import uuid
import traceback
from typing import Dict, List, Optional, Any, Union, Type, Callable, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import re
from functools import wraps
import aiohttp
import asyncpg
import aioredis
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from backend.core.exceptions import (
    CrawlerError,
    PlatformError,
    NetworkError,
    ContentProcessingError,
    SecurityError,
    SystemError,
    BusinessLogicError,
    RateLimitError,
    AuthenticationError,
    ValidationError as CustomValidationError
)
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.database.models import ErrorLog, User, SystemAlert
from backend.database.session import async_session
from backend.utils.notification_utils import NotificationManager
from backend.utils.monitoring_utils import MetricsCollector
from backend.utils.alert_utils import AlertManager

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class ErrorCategory(Enum):
    """Error categories for classification."""
    PLATFORM_API = "platform.api"
    NETWORK = "network"
    CONTENT_PROCESSING = "content.processing"
    SECURITY = "security"
    DATABASE = "database"
    REDIS = "redis"
    STORAGE = "storage"
    BUSINESS_LOGIC = "business.logic"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate.limit"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorAction(Enum):
    """Possible error handling actions."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    ALERT = "alert"


@dataclass
class ErrorContext:
    """Error context information."""
    
    error_id: str
    timestamp: datetime
    user_id: Optional[int] = None
    content_id: Optional[int] = None
    platform: Optional[str] = None
    operation: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ErrorDetails:
    """Comprehensive error details."""
    
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception_type: str
    stack_trace: str
    context: ErrorContext
    metadata: Dict[str, Any]
    suggested_action: ErrorAction
    retry_count: int = 0
    max_retries: int = 3
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'error_id': self.error_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'exception_type': self.exception_type,
            'stack_trace': self.stack_trace,
            'context': self.context.to_dict(),
            'metadata': self.metadata,
            'suggested_action': self.suggested_action.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'resolved': self.resolved,
            'resolution_notes': self.resolution_notes
        }


class ErrorClassifier:
    """Professional error classification system."""
    
    def __init__(self):
        self.classification_rules = self._load_classification_rules()
    
    def _load_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load error classification rules."""
        return {
            # Platform API Errors
            'platform_api': {
                'patterns': [
                    r'youtube.*api.*error',
                    r'instagram.*api.*error',
                    r'tiktok.*api.*error',
                    r'twitter.*api.*error',
                    r'api.*rate.*limit',
                    r'api.*quota.*exceeded',
                    r'unauthorized.*api',
                    r'forbidden.*api'
                ],
                'category': ErrorCategory.PLATFORM_API,
                'severity_mapping': {
                    'rate.limit': ErrorSeverity.MEDIUM,
                    'quota.exceeded': ErrorSeverity.HIGH,
                    'unauthorized': ErrorSeverity.HIGH,
                    'forbidden': ErrorSeverity.HIGH,
                    'default': ErrorSeverity.MEDIUM
                }
            },
            
            # Network Errors
            'network': {
                'patterns': [
                    r'connection.*timeout',
                    r'connection.*refused',
                    r'dns.*resolution.*failed',
                    r'ssl.*certificate.*error',
                    r'network.*unreachable',
                    r'socket.*timeout'
                ],
                'category': ErrorCategory.NETWORK,
                'severity_mapping': {
                    'timeout': ErrorSeverity.MEDIUM,
                    'refused': ErrorSeverity.HIGH,
                    'dns': ErrorSeverity.HIGH,
                    'ssl': ErrorSeverity.HIGH,
                    'default': ErrorSeverity.MEDIUM
                }
            },
            
            # Content Processing Errors
            'content_processing': {
                'patterns': [
                    r'invalid.*content.*format',
                    r'corrupted.*file',
                    r'unsupported.*content.*type',
                    r'fingerprint.*generation.*failed',
                    r'content.*validation.*failed'
                ],
                'category': ErrorCategory.CONTENT_PROCESSING,
                'severity_mapping': {
                    'invalid.format': ErrorSeverity.LOW,
                    'corrupted': ErrorSeverity.MEDIUM,
                    'unsupported': ErrorSeverity.LOW,
                    'default': ErrorSeverity.MEDIUM
                }
            },
            
            # Security Errors
            'security': {
                'patterns': [
                    r'authentication.*failed',
                    r'authorization.*denied',
                    r'security.*validation.*failed',
                    r'malware.*detected',
                    r'suspicious.*activity'
                ],
                'category': ErrorCategory.SECURITY,
                'severity_mapping': {
                    'malware': ErrorSeverity.CRITICAL,
                    'suspicious': ErrorSeverity.HIGH,
                    'authentication': ErrorSeverity.HIGH,
                    'authorization': ErrorSeverity.HIGH,
                    'default': ErrorSeverity.HIGH
                }
            },
            
            # Database Errors
            'database': {
                'patterns': [
                    r'database.*connection.*failed',
                    r'postgresql.*error',
                    r'constraint.*violation',
                    r'deadlock.*detected',
                    r'transaction.*rollback'
                ],
                'category': ErrorCategory.DATABASE,
                'severity_mapping': {
                    'connection.failed': ErrorSeverity.CRITICAL,
                    'deadlock': ErrorSeverity.HIGH,
                    'constraint.violation': ErrorSeverity.MEDIUM,
                    'default': ErrorSeverity.HIGH
                }
            }
        }
    
    def classify_error(
        self, 
        exception: Exception, 
        context: Optional[ErrorContext] = None
    ) -> Tuple[ErrorCategory, ErrorSeverity, ErrorAction]:
        """
        Classify error and determine appropriate handling.
        
        Args:
            exception: The exception to classify
            context: Error context information
            
        Returns:
            Tuple of (category, severity, suggested_action)
        """
        try:
            error_message = str(exception).lower()
            exception_type = type(exception).__name__
            
            # Direct exception type mapping
            category, severity = self._classify_by_exception_type(exception)
            
            if category == ErrorCategory.UNKNOWN:
                # Pattern-based classification
                category, severity = self._classify_by_patterns(error_message)
            
            # Determine suggested action
            action = self._determine_action(category, severity, exception)
            
            return category, severity, action
            
        except Exception as e:
            logger.error(f"Error classification failed: {e}")
            return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM, ErrorAction.RETRY
    
    def _classify_by_exception_type(self, exception: Exception) -> Tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by exception type."""
        type_mapping = {
            # Platform errors
            aiohttp.ClientResponseError: (ErrorCategory.PLATFORM_API, ErrorSeverity.MEDIUM),
            aiohttp.ClientTimeout: (ErrorCategory.NETWORK, ErrorSeverity.MEDIUM),
            aiohttp.ClientConnectionError: (ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            
            # Database errors
            asyncpg.PostgresError: (ErrorCategory.DATABASE, ErrorSeverity.HIGH),
            SQLAlchemyError: (ErrorCategory.DATABASE, ErrorSeverity.HIGH),
            
            # Redis errors
            aioredis.RedisError: (ErrorCategory.REDIS, ErrorSeverity.HIGH),
            aioredis.ConnectionError: (ErrorCategory.REDIS, ErrorSeverity.CRITICAL),
            
            # Custom errors
            PlatformError: (ErrorCategory.PLATFORM_API, ErrorSeverity.MEDIUM),
            NetworkError: (ErrorCategory.NETWORK, ErrorSeverity.MEDIUM),
            ContentProcessingError: (ErrorCategory.CONTENT_PROCESSING, ErrorSeverity.MEDIUM),
            SecurityError: (ErrorCategory.SECURITY, ErrorSeverity.HIGH),
            SystemError: (ErrorCategory.SYSTEM, ErrorSeverity.HIGH),
            BusinessLogicError: (ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.MEDIUM),
            RateLimitError: (ErrorCategory.RATE_LIMIT, ErrorSeverity.MEDIUM),
            AuthenticationError: (ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH),
            CustomValidationError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
            ValidationError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
            
            # Standard errors
            ValueError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
            TypeError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
            KeyError: (ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.MEDIUM),
            AttributeError: (ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.MEDIUM),
            FileNotFoundError: (ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM),
            PermissionError: (ErrorCategory.SECURITY, ErrorSeverity.HIGH),
            TimeoutError: (ErrorCategory.NETWORK, ErrorSeverity.MEDIUM)
        }
        
        exception_type = type(exception)
        
        # Check direct mapping
        if exception_type in type_mapping:
            return type_mapping[exception_type]
        
        # Check inheritance
        for error_type, (category, severity) in type_mapping.items():
            if isinstance(exception, error_type):
                return category, severity
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def _classify_by_patterns(self, error_message: str) -> Tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by message patterns."""
        for rule_name, rule_config in self.classification_rules.items():
            patterns = rule_config['patterns']
            
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    category = rule_config['category']
                    severity_mapping = rule_config['severity_mapping']
                    
                    # Determine severity based on specific patterns
                    severity = severity_mapping.get('default', ErrorSeverity.MEDIUM)
                    for severity_key, severity_value in severity_mapping.items():
                        if severity_key != 'default' and re.search(severity_key, error_message, re.IGNORECASE):
                            severity = severity_value
                            break
                    
                    return category, severity
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def _determine_action(
        self, 
        category: ErrorCategory, 
        severity: ErrorSeverity, 
        exception: Exception
    ) -> ErrorAction:
        """Determine suggested action based on error characteristics."""
        # Critical and emergency errors
        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.EMERGENCY]:
            return ErrorAction.ESCALATE
        
        # Category-specific actions
        action_mapping = {
            ErrorCategory.RATE_LIMIT: ErrorAction.RETRY,
            ErrorCategory.NETWORK: ErrorAction.RETRY,
            ErrorCategory.PLATFORM_API: ErrorAction.RETRY,
            ErrorCategory.CONTENT_PROCESSING: ErrorAction.SKIP,
            ErrorCategory.VALIDATION: ErrorAction.SKIP,
            ErrorCategory.SECURITY: ErrorAction.ALERT,
            ErrorCategory.DATABASE: ErrorAction.RETRY,
            ErrorCategory.REDIS: ErrorAction.RETRY,
            ErrorCategory.AUTHENTICATION: ErrorAction.ALERT,
            ErrorCategory.AUTHORIZATION: ErrorAction.ALERT,
            ErrorCategory.BUSINESS_LOGIC: ErrorAction.SKIP,
            ErrorCategory.SYSTEM: ErrorAction.RETRY
        }
        
        return action_mapping.get(category, ErrorAction.RETRY)


class ErrorRecoveryManager:
    """Professional error recovery and retry management."""
    
    def __init__(self):
        self.recovery_strategies = self._load_recovery_strategies()
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
    
    def _load_recovery_strategies(self) -> Dict[ErrorCategory, Dict[str, Any]]:
        """Load recovery strategies for different error categories."""
        return {
            ErrorCategory.RATE_LIMIT: {
                'max_retries': 5,
                'base_delay': 60,  # 1 minute
                'exponential_backoff': True,
                'jitter': True,
                'fallback_enabled': False
            },
            ErrorCategory.NETWORK: {
                'max_retries': 3,
                'base_delay': 2,
                'exponential_backoff': True,
                'jitter': True,
                'fallback_enabled': True
            },
            ErrorCategory.PLATFORM_API: {
                'max_retries': 3,
                'base_delay': 5,
                'exponential_backoff': True,
                'jitter': True,
                'fallback_enabled': True
            },
            ErrorCategory.DATABASE: {
                'max_retries': 3,
                'base_delay': 1,
                'exponential_backoff': True,
                'jitter': False,
                'fallback_enabled': False
            },
            ErrorCategory.CONTENT_PROCESSING: {
                'max_retries': 1,
                'base_delay': 0,
                'exponential_backoff': False,
                'jitter': False,
                'fallback_enabled': True
            }
        }
    
    async def execute_with_recovery(
        self,
        operation: Callable[[], Coroutine[Any, Any, Any]],
        context: ErrorContext,
        max_retries: Optional[int] = None
    ) -> Any:
        """
        Execute operation with automatic error recovery.
        
        Args:
            operation: Async operation to execute
            context: Error context information
            max_retries: Override default max retries
            
        Returns:
            Operation result
        """
        attempt = 0
        last_error = None
        
        while attempt <= (max_retries or 3):
            try:
                result = await operation()
                
                # Log successful recovery if this was a retry
                if attempt > 0:
                    logger.info(f"Operation recovered after {attempt} retries: {context.operation}")
                
                return result
                
            except Exception as e:
                last_error = e
                attempt += 1
                
                # Classify error
                classifier = ErrorClassifier()
                category, severity, action = classifier.classify_error(e, context)
                
                # Check if should retry
                if attempt > (max_retries or 3) or action not in [ErrorAction.RETRY, ErrorAction.FALLBACK]:
                    break
                
                # Calculate delay
                delay = await self._calculate_retry_delay(category, attempt)
                
                logger.warning(
                    f"Operation failed (attempt {attempt}), retrying in {delay}s: {e}"
                )
                
                # Wait before retry
                if delay > 0:
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        if last_error:
            logger.error(f"Operation failed after {attempt} attempts: {last_error}")
            raise last_error
    
    async def _calculate_retry_delay(self, category: ErrorCategory, attempt: int) -> float:
        """Calculate retry delay based on category and attempt number."""
        strategy = self.recovery_strategies.get(category, {})
        
        base_delay = strategy.get('base_delay', 2)
        exponential_backoff = strategy.get('exponential_backoff', True)
        jitter = strategy.get('jitter', True)
        
        if exponential_backoff:
            delay = base_delay * (2 ** (attempt - 1))
        else:
            delay = base_delay
        
        # Add jitter to prevent thundering herd
        if jitter:
            import random
            delay += random.uniform(0, delay * 0.1)  # Up to 10% jitter
        
        # Cap maximum delay
        max_delay = 300  # 5 minutes
        return min(delay, max_delay)
    
    async def attempt_fallback(
        self,
        primary_operation: Callable[[], Coroutine[Any, Any, Any]],
        fallback_operation: Callable[[], Coroutine[Any, Any, Any]],
        context: ErrorContext
    ) -> Any:
        """
        Attempt primary operation with fallback.
        
        Args:
            primary_operation: Primary async operation
            fallback_operation: Fallback async operation
            context: Error context
            
        Returns:
            Operation result
        """
        try:
            return await primary_operation()
        except Exception as e:
            logger.warning(f"Primary operation failed, attempting fallback: {e}")
            
            try:
                result = await fallback_operation()
                logger.info(f"Fallback operation succeeded: {context.operation}")
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback operation also failed: {fallback_error}")
                raise e  # Raise original error


class ErrorAggregator:
    """Error aggregation and analysis system."""
    
    def __init__(self):
        self.error_cache: Dict[str, List[ErrorDetails]] = {}
        self.aggregation_window = timedelta(minutes=5)
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,  # Alert immediately
            ErrorSeverity.HIGH: 3,      # Alert after 3 in window
            ErrorSeverity.MEDIUM: 10,   # Alert after 10 in window
            ErrorSeverity.LOW: 50       # Alert after 50 in window
        }
    
    async def add_error(self, error_details: ErrorDetails):
        """Add error to aggregation system."""
        try:
            # Create aggregation key
            key = f"{error_details.category.value}:{error_details.exception_type}"
            
            if key not in self.error_cache:
                self.error_cache[key] = []
            
            # Add error to cache
            self.error_cache[key].append(error_details)
            
            # Clean old errors
            await self._clean_old_errors(key)
            
            # Check for alert conditions
            await self._check_alert_conditions(key, error_details)
            
        except Exception as e:
            logger.error(f"Error aggregation failed: {e}")
    
    async def _clean_old_errors(self, key: str):
        """Remove errors outside aggregation window."""
        try:
            cutoff_time = datetime.utcnow() - self.aggregation_window
            self.error_cache[key] = [
                error for error in self.error_cache[key]
                if error.context.timestamp > cutoff_time
            ]
        except Exception as e:
            logger.warning(f"Error cache cleanup failed: {e}")
    
    async def _check_alert_conditions(self, key: str, latest_error: ErrorDetails):
        """Check if alert conditions are met."""
        try:
            errors_in_window = self.error_cache[key]
            error_count = len(errors_in_window)
            
            # Get threshold for this severity
            threshold = self.alert_thresholds.get(latest_error.severity, 10)
            
            if error_count >= threshold:
                await self._trigger_error_alert(key, errors_in_window)
        
        except Exception as e:
            logger.error(f"Alert condition check failed: {e}")
    
    async def _trigger_error_alert(self, key: str, errors: List[ErrorDetails]):
        """Trigger alert for error pattern."""
        try:
            alert_data = {
                'error_pattern': key,
                'error_count': len(errors),
                'severity': max(error.severity for error in errors).name,
                'time_window': self.aggregation_window.total_seconds(),
                'first_occurrence': min(error.context.timestamp for error in errors),
                'last_occurrence': max(error.context.timestamp for error in errors),
                'affected_users': len(set(e.context.user_id for e in errors if e.context.user_id)),
                'affected_platforms': list(set(e.context.platform for e in errors if e.context.platform))
            }
            
            logger.critical(f"Error pattern alert: {json.dumps(alert_data, default=str)}")
            
            # TODO: Send to alerting system
            # await alert_manager.send_error_pattern_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Error alert triggering failed: {e}")


class ErrorHandler:
    """Main error handler orchestrating all error management operations."""
    
    def __init__(
        self,
        notification_manager: Optional[NotificationManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        alert_manager: Optional[AlertManager] = None
    ):
        self.classifier = ErrorClassifier()
        self.recovery_manager = ErrorRecoveryManager()
        self.aggregator = ErrorAggregator()
        self.notification_manager = notification_manager
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        logger.info("Error Handler initialized successfully")
    
    async def handle_error(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        operation: Optional[str] = None
    ) -> ErrorDetails:
        """
        Main entry point for error handling.
        
        Args:
            exception: The exception to handle
            context: Error context information
            operation: Operation that failed
            
        Returns:
            Error details
        """
        try:
            # Create error context if not provided
            if context is None:
                context = ErrorContext(
                    error_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    operation=operation
                )
            
            # Classify error
            category, severity, action = self.classifier.classify_error(exception, context)
            
            # Create error details
            error_details = ErrorDetails(
                error_id=context.error_id,
                category=category,
                severity=severity,
                message=str(exception),
                exception_type=type(exception).__name__,
                stack_trace=traceback.format_exc(),
                context=context,
                metadata=self._extract_error_metadata(exception),
                suggested_action=action
            )
            
            # Log error
            await self._log_error(error_details)
            
            # Add to aggregation
            await self.aggregator.add_error(error_details)
            
            # Update metrics
            if self.metrics_collector:
                await self.metrics_collector.increment_error_count(
                    category.value, severity.value
                )
            
            # Send notifications for high severity errors
            if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.EMERGENCY]:
                await self._send_critical_notification(error_details)
            
            logger.error(
                f"Error handled: {error_details.error_id} "
                f"[{category.value}] [{severity.name}] {error_details.message}"
            )
            
            return error_details
            
        except Exception as e:
            logger.critical(f"Error handler itself failed: {e}")
            # Create minimal error details
            return ErrorDetails(
                error_id=str(uuid.uuid4()),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                message=f"Error handler failure: {e}",
                exception_type=type(e).__name__,
                stack_trace=traceback.format_exc(),
                context=context or ErrorContext(
                    error_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow()
                ),
                metadata={},
                suggested_action=ErrorAction.ESCALATE
            )
    
    def _extract_error_metadata(self, exception: Exception) -> Dict[str, Any]:
        """Extract metadata from exception."""
        metadata = {}
        
        try:
            # HTTP response errors
            if isinstance(exception, aiohttp.ClientResponseError):
                metadata.update({
                    'status_code': exception.status,
                    'response_headers': dict(exception.headers) if exception.headers else {},
                    'request_url': str(exception.request_info.url) if exception.request_info else None
                })
            
            # Database errors
            elif isinstance(exception, (asyncpg.PostgresError, SQLAlchemyError)):
                metadata.update({
                    'error_code': getattr(exception, 'sqlstate', None),
                    'error_detail': getattr(exception, 'detail', None)
                })
            
            # Validation errors
            elif isinstance(exception, ValidationError):
                metadata.update({
                    'validation_errors': exception.errors() if hasattr(exception, 'errors') else []
                })
            
            # Custom application errors
            elif hasattr(exception, 'error_code'):
                metadata['error_code'] = exception.error_code
            
            if hasattr(exception, 'details'):
                metadata['error_details'] = exception.details
            
        except Exception as e:
            logger.warning(f"Error metadata extraction failed: {e}")
        
        return metadata
    
    async def _log_error(self, error_details: ErrorDetails):
        """Log error to database and file system."""
        try:
            # Log to database
            async with async_session() as session:
                error_log = ErrorLog(
                    error_id=error_details.error_id,
                    category=error_details.category.value,
                    severity=error_details.severity.value,
                    message=error_details.message,
                    exception_type=error_details.exception_type,
                    stack_trace=error_details.stack_trace,
                    context=error_details.context.to_dict(),
                    metadata=error_details.metadata,
                    suggested_action=error_details.suggested_action.value,
                    retry_count=error_details.retry_count,
                    user_id=error_details.context.user_id,
                    created_at=error_details.context.timestamp
                )
                
                session.add(error_log)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Error logging to database failed: {e}")
    
    async def _send_critical_notification(self, error_details: ErrorDetails):
        """Send notification for critical errors."""
        try:
            if self.notification_manager:
                await self.notification_manager.send_critical_error_alert(error_details)
            
            if self.alert_manager:
                await self.alert_manager.send_error_alert(error_details)
                
        except Exception as e:
            logger.warning(f"Critical error notification failed: {e}")
    
    def error_handler_decorator(
        self,
        operation: Optional[str] = None,
        context_factory: Optional[Callable[[], ErrorContext]] = None
    ):
        """Decorator for automatic error handling."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    context = context_factory() if context_factory else None
                    await self.handle_error(e, context, operation or func.__name__)
                    raise  # Re-raise after handling
            return wrapper
        return decorator
    
    async def get_error_statistics(self, 
                                 time_range: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        try:
            cutoff_time = datetime.utcnow() - time_range
            
            async with async_session() as session:
                # TODO: Implement database queries for error statistics
                # This would include counts by category, severity, trends, etc.
                pass
            
            return {
                'time_range_hours': time_range.total_seconds() / 3600,
                'total_errors': 0,  # Placeholder
                'by_category': {},  # Placeholder
                'by_severity': {},  # Placeholder
                'top_error_types': [],  # Placeholder
                'error_rate_trend': []  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error statistics collection failed: {e}")
            return {}


# Utility functions
def create_error_context(
    user_id: Optional[int] = None,
    content_id: Optional[int] = None,
    platform: Optional[str] = None,
    operation: Optional[str] = None,
    **kwargs
) -> ErrorContext:
    """Create error context with provided information."""
    return ErrorContext(
        error_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        user_id=user_id,
        content_id=content_id,
        platform=platform,
        operation=operation,
        **kwargs
    )


# Factory function
def create_error_handler(
    notification_manager: Optional[NotificationManager] = None,
    metrics_collector: Optional[MetricsCollector] = None,
    alert_manager: Optional[AlertManager] = None
) -> ErrorHandler:
    """Create and return an ErrorHandler instance."""
    return ErrorHandler(
        notification_manager=notification_manager,
        metrics_collector=metrics_collector,
        alert_manager=alert_manager
    )
