"""
Exception Handling and Error Management for Copyright Enforcement
Professional error handling, custom exceptions, and error recovery
"""

import logging
import traceback
from typing import Dict, List, Optional, Any, Union, Type, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import sys
from abc import ABC, abstractmethod
from collections import defaultdict


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NETWORK = "network"
    PLATFORM_API = "platform_api"
    DATABASE = "database"
    CONTENT_ANALYSIS = "content_analysis"
    LEGAL_DOCUMENT = "legal_document"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"
    RATE_LIMITING = "rate_limiting"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    ABORT = "abort"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorContext:
    """Context information for errors"""
    operation: str
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    platform: Optional[str] = None
    endpoint: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'operation': self.operation,
            'user_id': self.user_id,
            'case_id': self.case_id,
            'platform': self.platform,
            'endpoint': self.endpoint,
            'request_data': self.request_data,
            'response_data': self.response_data,
            'metadata': self.metadata
        }


class BaseEnforcementException(Exception, ABC):
    """Base exception for all enforcement-related errors"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        recovery_strategy: Optional[RecoveryStrategy] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context
        self.cause = cause
        self.recovery_strategy = recovery_strategy
        self.error_code = error_code or self._generate_error_code()
        self.timestamp = datetime.utcnow()
        self.traceback_info = traceback.format_exc() if sys.exc_info()[0] else None
    
    def _generate_error_code(self) -> str:
        """Generate unique error code"""
        return f"{self.category.value.upper()}_{self.__class__.__name__.upper()}_{int(self.timestamp.timestamp())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'recovery_strategy': self.recovery_strategy.value if self.recovery_strategy else None,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context.to_dict() if self.context else None,
            'cause': str(self.cause) if self.cause else None,
            'traceback': self.traceback_info
        }
    
    def to_json(self) -> str:
        """Convert exception to JSON"""
        return json.dumps(self.to_dict(), indent=2)
    
    @abstractmethod
    def get_user_message(self) -> str:
        """Get user-friendly error message"""
        pass


class AuthenticationError(BaseEnforcementException):
    """Authentication-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
    
    def get_user_message(self) -> str:
        return "Authentication failed. Please check your credentials and try again."


class AuthorizationError(BaseEnforcementException):
    """Authorization-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
    
    def get_user_message(self) -> str:
        return "Access denied. You don't have permission to perform this operation."


class ValidationError(BaseEnforcementException):
    """Data validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
        self.field = field
    
    def get_user_message(self) -> str:
        if self.field:
            return f"Invalid value for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class NetworkError(BaseEnforcementException):
    """Network-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
    
    def get_user_message(self) -> str:
        return "Network error occurred. Please check your connection and try again."


class PlatformAPIError(BaseEnforcementException):
    """Platform API-related errors"""
    
    def __init__(
        self,
        message: str,
        platform: str,
        status_code: Optional[int] = None,
        api_error_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.PLATFORM_API,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.platform = platform
        self.status_code = status_code
        self.api_error_code = api_error_code
    
    def get_user_message(self) -> str:
        return f"Error communicating with {self.platform}. Please try again later."


class DatabaseError(BaseEnforcementException):
    """Database-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
    
    def get_user_message(self) -> str:
        return "Database error occurred. Please try again later."


class ContentAnalysisError(BaseEnforcementException):
    """Content analysis errors"""
    
    def __init__(self, message: str, content_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONTENT_ANALYSIS,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            **kwargs
        )
        self.content_type = content_type
    
    def get_user_message(self) -> str:
        return "Content analysis failed. The content may be corrupted or in an unsupported format."


class LegalDocumentError(BaseEnforcementException):
    """Legal document generation errors"""
    
    def __init__(self, message: str, document_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.LEGAL_DOCUMENT,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
        self.document_type = document_type
    
    def get_user_message(self) -> str:
        return "Error generating legal document. Please contact support for assistance."


class NotificationError(BaseEnforcementException):
    """Notification delivery errors"""
    
    def __init__(self, message: str, channel: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NOTIFICATION,
            severity=ErrorSeverity.LOW,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.channel = channel
    
    def get_user_message(self) -> str:
        return "Notification delivery failed. You may not receive updates for this operation."


class IntegrationError(BaseEnforcementException):
    """External integration errors"""
    
    def __init__(
        self,
        message: str,
        service: str,
        integration_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.INTEGRATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            **kwargs
        )
        self.service = service
        self.integration_type = integration_type
    
    def get_user_message(self) -> str:
        return f"Integration with {self.service} failed. Some features may not be available."


class ConfigurationError(BaseEnforcementException):
    """Configuration-related errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
        self.config_key = config_key
    
    def get_user_message(self) -> str:
        return "Configuration error. Please contact your system administrator."


class RateLimitError(BaseEnforcementException):
    """Rate limiting errors"""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.RATE_LIMITING,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.retry_after = retry_after
    
    def get_user_message(self) -> str:
        if self.retry_after:
            return f"Rate limit exceeded. Please wait {self.retry_after} seconds before trying again."
        return "Rate limit exceeded. Please try again later."


class TimeoutError(BaseEnforcementException):
    """Timeout errors"""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.timeout_duration = timeout_duration
    
    def get_user_message(self) -> str:
        return "Operation timed out. Please try again."


class ResourceExhaustionError(BaseEnforcementException):
    """Resource exhaustion errors"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RESOURCE_EXHAUSTION,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            **kwargs
        )
        self.resource_type = resource_type
    
    def get_user_message(self) -> str:
        return "System resources exhausted. Please try again later or contact support."


class DataCorruptionError(BaseEnforcementException):
    """Data corruption errors"""
    
    def __init__(self, message: str, data_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATA_CORRUPTION,
            severity=ErrorSeverity.CRITICAL,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
        self.data_type = data_type
    
    def get_user_message(self) -> str:
        return "Data corruption detected. Please contact support immediately."


class BusinessLogicError(BaseEnforcementException):
    """Business logic errors"""
    
    def __init__(self, message: str, rule_name: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            **kwargs
        )
        self.rule_name = rule_name
    
    def get_user_message(self) -> str:
        return f"Business rule violation: {self.message}"


class ExternalServiceError(BaseEnforcementException):
    """External service errors"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        service_status: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.service_name = service_name
        self.service_status = service_status
    
    def get_user_message(self) -> str:
        return f"External service {self.service_name} is unavailable. Please try again later."


@dataclass
class ErrorSummary:
    """Summary of error occurrence"""
    error_code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    count: int = 1
    first_occurrence: datetime = field(default_factory=datetime.utcnow)
    last_occurrence: datetime = field(default_factory=datetime.utcnow)
    affected_operations: Set[str] = field(default_factory=set)
    recovery_attempts: int = 0
    resolved: bool = False


class ErrorTracker:
    """Track and analyze error patterns"""
    
    def __init__(self):
        self.error_summaries: Dict[str, ErrorSummary] = {}
        self.error_history: List[BaseEnforcementException] = []
        self.max_history_size = 1000
        
    def track_error(self, error: BaseEnforcementException):
        """Track an error occurrence"""
        try:
            # Add to history
            self.error_history.append(error)
            
            # Maintain history size
            if len(self.error_history) > self.max_history_size:
                self.error_history = self.error_history[-self.max_history_size:]
            
            # Update summary
            if error.error_code in self.error_summaries:
                summary = self.error_summaries[error.error_code]
                summary.count += 1
                summary.last_occurrence = error.timestamp
                if error.context:
                    summary.affected_operations.add(error.context.operation)
            else:
                affected_operations = set()
                if error.context:
                    affected_operations.add(error.context.operation)
                
                self.error_summaries[error.error_code] = ErrorSummary(
                    error_code=error.error_code,
                    message=error.message,
                    category=error.category,
                    severity=error.severity,
                    first_occurrence=error.timestamp,
                    last_occurrence=error.timestamp,
                    affected_operations=affected_operations
                )
            
            logger.error(f"Error tracked: {error.error_code} - {error.message}")
            
        except Exception as e:
            logger.error(f"Error tracking failed: {e}")
    
    def get_error_stats(self, category: Optional[ErrorCategory] = None) -> Dict[str, Any]:
        """Get error statistics"""
        try:
            filtered_summaries = self.error_summaries.values()
            
            if category:
                filtered_summaries = [s for s in filtered_summaries if s.category == category]
            
            total_errors = sum(s.count for s in filtered_summaries)
            critical_errors = sum(s.count for s in filtered_summaries if s.severity == ErrorSeverity.CRITICAL)
            high_errors = sum(s.count for s in filtered_summaries if s.severity == ErrorSeverity.HIGH)
            
            # Most frequent errors
            most_frequent = sorted(filtered_summaries, key=lambda s: s.count, reverse=True)[:10]
            
            # Recent errors
            recent_errors = sorted(
                [e for e in self.error_history if not category or e.category == category],
                key=lambda e: e.timestamp,
                reverse=True
            )[:20]
            
            return {
                'total_errors': total_errors,
                'unique_error_types': len(filtered_summaries),
                'critical_errors': critical_errors,
                'high_severity_errors': high_errors,
                'most_frequent_errors': [
                    {
                        'error_code': s.error_code,
                        'message': s.message,
                        'count': s.count,
                        'category': s.category.value,
                        'severity': s.severity.value
                    }
                    for s in most_frequent
                ],
                'recent_errors': [
                    {
                        'error_code': e.error_code,
                        'message': e.message,
                        'timestamp': e.timestamp.isoformat(),
                        'category': e.category.value,
                        'severity': e.severity.value
                    }
                    for e in recent_errors
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_error_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get error trends over time"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
            
            # Group by hour
            hourly_counts = defaultdict(int)
            category_counts = defaultdict(int)
            severity_counts = defaultdict(int)
            
            for error in recent_errors:
                hour_key = error.timestamp.strftime('%Y-%m-%d %H:00')
                hourly_counts[hour_key] += 1
                category_counts[error.category.value] += 1
                severity_counts[error.severity.value] += 1
            
            return {
                'time_period_hours': hours,
                'total_errors': len(recent_errors),
                'hourly_distribution': dict(hourly_counts),
                'category_distribution': dict(category_counts),
                'severity_distribution': dict(severity_counts)
            }
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {}
    
    def clear_resolved_errors(self):
        """Clear resolved errors from tracking"""
        try:
            resolved_codes = [code for code, summary in self.error_summaries.items() if summary.resolved]
            
            for code in resolved_codes:
                del self.error_summaries[code]
            
            logger.info(f"Cleared {len(resolved_codes)} resolved errors from tracking")
            
        except Exception as e:
            logger.error(f"Error clearing resolved errors: {e}")


class ErrorHandler:
    """Centralized error handling and recovery"""
    
    def __init__(self, error_tracker: Optional[ErrorTracker] = None):
        self.error_tracker = error_tracker or ErrorTracker()
        self.recovery_handlers: Dict[ErrorCategory, Callable] = {}
        self.notification_handlers: List[Callable] = []
        
    def register_recovery_handler(self, category: ErrorCategory, handler: Callable):
        """Register error recovery handler"""
        self.recovery_handlers[category] = handler
        logger.info(f"Registered recovery handler for category {category.value}")
    
    def register_notification_handler(self, handler: Callable):
        """Register error notification handler"""
        self.notification_handlers.append(handler)
        logger.info("Registered error notification handler")
    
    async def handle_error(
        self,
        error: BaseEnforcementException,
        context: Optional[ErrorContext] = None
    ) -> Optional[Any]:
        """Handle error with recovery and notification"""
        try:
            # Update context if provided
            if context and not error.context:
                error.context = context
            
            # Track error
            self.error_tracker.track_error(error)
            
            # Log error
            logger.error(
                f"Handling error {error.error_code}: {error.message}",
                extra={
                    'error_code': error.error_code,
                    'category': error.category.value,
                    'severity': error.severity.value,
                    'context': error.context.to_dict() if error.context else None
                }
            )
            
            # Attempt recovery based on strategy
            recovery_result = None
            if error.recovery_strategy:
                recovery_result = await self._attempt_recovery(error)
            
            # Send notifications for high severity errors
            if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                await self._send_notifications(error)
            
            return recovery_result
            
        except Exception as e:
            logger.error(f"Error handling failed: {e}")
            return None
    
    async def _attempt_recovery(self, error: BaseEnforcementException) -> Optional[Any]:
        """Attempt error recovery based on strategy"""
        try:
            if error.recovery_strategy == RecoveryStrategy.RETRY:
                return await self._retry_operation(error)
            
            elif error.recovery_strategy == RecoveryStrategy.FALLBACK:
                return await self._fallback_operation(error)
            
            elif error.recovery_strategy == RecoveryStrategy.ESCALATE:
                return await self._escalate_error(error)
            
            elif error.recovery_strategy == RecoveryStrategy.MANUAL_INTERVENTION:
                return await self._request_manual_intervention(error)
            
            # Category-specific recovery
            if error.category in self.recovery_handlers:
                handler = self.recovery_handlers[error.category]
                return await handler(error)
            
            return None
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return None
    
    async def _retry_operation(self, error: BaseEnforcementException) -> Optional[Any]:
        """Implement retry logic"""
        # This would be implemented based on specific operation context
        logger.info(f"Retry recovery attempted for error {error.error_code}")
        return None
    
    async def _fallback_operation(self, error: BaseEnforcementException) -> Optional[Any]:
        """Implement fallback logic"""
        logger.info(f"Fallback recovery attempted for error {error.error_code}")
        return None
    
    async def _escalate_error(self, error: BaseEnforcementException) -> Optional[Any]:
        """Escalate error to higher level"""
        logger.warning(f"Error escalated: {error.error_code}")
        return None
    
    async def _request_manual_intervention(self, error: BaseEnforcementException) -> Optional[Any]:
        """Request manual intervention"""
        logger.critical(f"Manual intervention required for error {error.error_code}")
        return None
    
    async def _send_notifications(self, error: BaseEnforcementException):
        """Send error notifications"""
        try:
            for handler in self.notification_handlers:
                await handler(error)
                
        except Exception as e:
            logger.error(f"Error notification failed: {e}")


# Global instances
error_tracker = ErrorTracker()
error_handler = ErrorHandler(error_tracker)


def get_error_tracker() -> ErrorTracker:
    """Get global error tracker instance"""
    return error_tracker


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    return error_handler


__all__ = [
    'BaseEnforcementException',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'NetworkError',
    'PlatformAPIError',
    'DatabaseError',
    'ContentAnalysisError',
    'LegalDocumentError',
    'NotificationError',
    'IntegrationError',
    'ConfigurationError',
    'RateLimitError',
    'TimeoutError',
    'ResourceExhaustionError',
    'DataCorruptionError',
    'BusinessLogicError',
    'ExternalServiceError',
    'ErrorContext',
    'ErrorSummary',
    'ErrorTracker',
    'ErrorHandler',
    'ErrorSeverity',
    'ErrorCategory',
    'RecoveryStrategy',
    'get_error_tracker',
    'get_error_handler'
]
