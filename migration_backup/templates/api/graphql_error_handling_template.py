"""GraphQL Error Handling Template for Ainflue Platform
Enterprise-grade GraphQL error handling with comprehensive monitoring

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
"""

import logging
import traceback
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

from graphql import GraphQLError, GraphQLResolveInfo
from graphql.error import format_error, GraphQLSyntaxError, GraphQLValidationError
from graphql.execution.middleware import Middleware

from core.config import get_settings
from core.auth import get_current_user
from core.logging import log_error_event
from utils.exceptions import (
    AuthenticationException, 
    AuthorizationException,
    ValidationException,
    BusinessLogicException,
    RateLimitException
)
from monitoring.api_metrics import ErrorMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


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
    RATE_LIMIT = "rate_limit"
    INTERNAL = "internal"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    CONFIGURATION = "configuration"


@dataclass
class ErrorContext:
    """Error context information"""
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    operation_name: Optional[str] = None
    field_path: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "operation_name": self.operation_name,
            "field_path": self.field_path,
            "variables": self.variables,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id
        }


@dataclass
class GraphQLErrorInfo:
    """Comprehensive GraphQL error information"""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    code: str
    details: Optional[Dict[str, Any]] = None
    context: Optional[ErrorContext] = None
    original_exception: Optional[Exception] = None
    stack_trace: Optional[str] = None
    suggestions: Optional[List[str]] = None
    
    def to_graphql_error(self) -> GraphQLError:
        """Convert to GraphQL error"""
        extensions = {
            "code": self.code,
            "category": self.category.value,
            "severity": self.severity.value
        }
        
        if self.details:
            extensions["details"] = self.details
        
        if self.suggestions:
            extensions["suggestions"] = self.suggestions
        
        # Don't expose sensitive information in production
        if settings.ENVIRONMENT != "production" and self.stack_trace:
            extensions["stack_trace"] = self.stack_trace
        
        return GraphQLError(
            message=self.message,
            extensions=extensions
        )


class ErrorClassifier:
    """Classifies errors and determines appropriate responses"""
    
    def __init__(self):
        self.error_mappings = {
            AuthenticationException: {
                "category": ErrorCategory.AUTHENTICATION,
                "severity": ErrorSeverity.MEDIUM,
                "code": "AUTHENTICATION_REQUIRED"
            },
            AuthorizationException: {
                "category": ErrorCategory.AUTHORIZATION,
                "severity": ErrorSeverity.MEDIUM,
                "code": "INSUFFICIENT_PERMISSIONS"
            },
            ValidationException: {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.LOW,
                "code": "VALIDATION_ERROR"
            },
            BusinessLogicException: {
                "category": ErrorCategory.BUSINESS_LOGIC,
                "severity": ErrorSeverity.MEDIUM,
                "code": "BUSINESS_RULE_VIOLATION"
            },
            RateLimitException: {
                "category": ErrorCategory.RATE_LIMIT,
                "severity": ErrorSeverity.MEDIUM,
                "code": "RATE_LIMIT_EXCEEDED"
            },
            GraphQLSyntaxError: {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.LOW,
                "code": "SYNTAX_ERROR"
            },
            GraphQLValidationError: {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.LOW,
                "code": "VALIDATION_ERROR"
            }
        }
        
        self.database_error_patterns = [
            "connection", "timeout", "deadlock", "constraint", "integrity"
        ]
        
        self.network_error_patterns = [
            "network", "connection refused", "timeout", "unreachable"
        ]
    
    def classify_error(self, error: Exception, context: ErrorContext) -> GraphQLErrorInfo:
        """Classify error and create error info"""
        
        # Check for direct mappings
        error_type = type(error)
        if error_type in self.error_mappings:
            mapping = self.error_mappings[error_type]
            return GraphQLErrorInfo(
                message=str(error),
                category=mapping["category"],
                severity=mapping["severity"],
                code=mapping["code"],
                context=context,
                original_exception=error,
                stack_trace=traceback.format_exc(),
                suggestions=self._get_error_suggestions(error, mapping["category"])
            )
        
        # Pattern-based classification
        error_str = str(error).lower()
        
        # Database errors
        if any(pattern in error_str for pattern in self.database_error_patterns):
            return GraphQLErrorInfo(
                message="Database operation failed",
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.HIGH,
                code="DATABASE_ERROR",
                details={"original_error": str(error)},
                context=context,
                original_exception=error,
                stack_trace=traceback.format_exc(),
                suggestions=["Check database connection", "Retry the operation"]
            )
        
        # Network errors
        if any(pattern in error_str for pattern in self.network_error_patterns):
            return GraphQLErrorInfo(
                message="Network operation failed",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                code="NETWORK_ERROR",
                details={"original_error": str(error)},
                context=context,
                original_exception=error,
                suggestions=["Check network connectivity", "Retry the operation"]
            )
        
        # Default to internal error
        return GraphQLErrorInfo(
            message="An internal error occurred" if settings.ENVIRONMENT == "production" else str(error),
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            code="INTERNAL_ERROR",
            details={"original_error": str(error)} if settings.ENVIRONMENT != "production" else None,
            context=context,
            original_exception=error,
            stack_trace=traceback.format_exc() if settings.ENVIRONMENT != "production" else None,
            suggestions=["Contact support if the problem persists"]
        )
    
    def _get_error_suggestions(self, error: Exception, category: ErrorCategory) -> List[str]:
        """Get helpful suggestions for error resolution"""
        suggestions = []
        
        if category == ErrorCategory.AUTHENTICATION:
            suggestions = [
                "Check if you are logged in",
                "Verify your authentication token",
                "Login again if token expired"
            ]
        elif category == ErrorCategory.AUTHORIZATION:
            suggestions = [
                "Check if you have the required permissions",
                "Contact an administrator if you need access",
                "Verify you're accessing the correct resource"
            ]
        elif category == ErrorCategory.VALIDATION:
            suggestions = [
                "Check the input data format",
                "Verify all required fields are provided",
                "Review the API documentation"
            ]
        elif category == ErrorCategory.RATE_LIMIT:
            suggestions = [
                "Wait before making another request",
                "Consider using pagination for large data sets",
                "Contact support for higher rate limits"
            ]
        
        return suggestions


class ErrorAggregator:
    """Aggregates and analyzes error patterns"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_patterns: Dict[str, List[str]] = {}
        self.metrics = ErrorMetrics()
    
    def record_error(self, error_info: GraphQLErrorInfo):
        """Record error for pattern analysis"""
        
        # Count by category and code
        key = f"{error_info.category.value}:{error_info.code}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Track patterns
        if error_info.context:
            pattern_key = error_info.category.value
            if pattern_key not in self.error_patterns:
                self.error_patterns[pattern_key] = []
            
            self.error_patterns[pattern_key].append(error_info.message)
        
        # Record metrics
        self.metrics.record_error(
            category=error_info.category.value,
            code=error_info.code,
            severity=error_info.severity.value,
            user_id=error_info.context.user_id if error_info.context else None
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts,
            "top_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def detect_error_spike(self, threshold: int = 10) -> Optional[Dict[str, Any]]:
        """Detect error spikes that might indicate issues"""
        recent_errors = self.metrics.get_recent_error_count(minutes=5)
        
        if recent_errors > threshold:
            return {
                "spike_detected": True,
                "error_count": recent_errors,
                "threshold": threshold,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return None


class GraphQLErrorHandler(Middleware):
    """Comprehensive GraphQL error handling middleware"""
    
    def __init__(self):
        self.classifier = ErrorClassifier()
        self.aggregator = ErrorAggregator()
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,  # Alert immediately
            ErrorSeverity.HIGH: 5,      # Alert after 5 errors
            ErrorSeverity.MEDIUM: 20,   # Alert after 20 errors
        }
    
    async def resolve(self, next, root, info: GraphQLResolveInfo, **args):
        """Middleware resolver with comprehensive error handling"""
        
        # Build error context
        context = await self._build_error_context(info)
        
        try:
            # Execute resolver
            result = await next(root, info, **args)
            return result
            
        except Exception as error:
            # Classify and handle error
            error_info = self.classifier.classify_error(error, context)
            
            # Record error
            self.aggregator.record_error(error_info)
            
            # Log error
            await self._log_error(error_info)
            
            # Send alerts if needed
            await self._check_and_send_alerts(error_info)
            
            # Return formatted GraphQL error
            raise error_info.to_graphql_error()
    
    async def _build_error_context(self, info: GraphQLResolveInfo) -> ErrorContext:
        """Build error context from request info"""
        request = info.context.get("request")
        
        context = ErrorContext(
            operation_name=info.operation.name.value if info.operation.name else None,
            field_path=".".join(info.path.as_list()) if info.path else None,
            variables=info.variable_values,
            request_id=getattr(request, "request_id", None) if request else None,
            trace_id=getattr(request, "trace_id", None) if request else None
        )
        
        if request:
            context.ip_address = self._get_client_ip(request)
            context.user_agent = request.headers.get("user-agent")
            
            # Get user ID if authenticated
            try:
                user = await get_current_user(request)
                if user:
                    context.user_id = str(user.id)
            except:
                pass  # Ignore authentication errors here
        
        return context
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return getattr(request.client, "host", "unknown")
    
    async def _log_error(self, error_info: GraphQLErrorInfo):
        """Log error with appropriate level"""
        
        log_data = {
            "message": error_info.message,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "code": error_info.code,
            "context": error_info.context.to_dict() if error_info.context else None,
            "details": error_info.details
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical("Critical GraphQL error", extra=log_data)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error("High severity GraphQL error", extra=log_data)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning("Medium severity GraphQL error", extra=log_data)
        else:
            logger.info("Low severity GraphQL error", extra=log_data)
        
        # Log to centralized error tracking
        log_error_event(
            event_type="graphql_error",
            severity=error_info.severity.value,
            details=log_data
        )
    
    async def _check_and_send_alerts(self, error_info: GraphQLErrorInfo):
        """Check if alerts should be sent for this error"""
        
        severity = error_info.severity
        threshold = self.alert_thresholds.get(severity)
        
        if threshold:
            # Get recent error count for this type
            error_key = f"{error_info.category.value}:{error_info.code}"
            recent_count = self.aggregator.error_counts.get(error_key, 0)
            
            if recent_count >= threshold:
                await self._send_error_alert(error_info, recent_count)
        
        # Check for error spikes
        spike_info = self.aggregator.detect_error_spike()
        if spike_info:
            await self._send_spike_alert(spike_info)
    
    async def _send_error_alert(self, error_info: GraphQLErrorInfo, count: int):
        """Send error alert"""
        alert_data = {
            "type": "error_threshold_exceeded",
            "error_category": error_info.category.value,
            "error_code": error_info.code,
            "error_count": count,
            "severity": error_info.severity.value,
            "message": error_info.message,
            "context": error_info.context.to_dict() if error_info.context else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # This would typically send to alerting system (Slack, PagerDuty, etc.)
        logger.critical(f"ERROR ALERT: {alert_data}")
    
    async def _send_spike_alert(self, spike_info: Dict[str, Any]):
        """Send error spike alert"""
        alert_data = {
            "type": "error_spike_detected",
            **spike_info
        }
        
        logger.critical(f"ERROR SPIKE ALERT: {alert_data}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.aggregator.get_error_summary()


# Custom error formatter
def format_graphql_error(error: GraphQLError) -> Dict[str, Any]:
    """Custom error formatter for GraphQL responses"""
    
    formatted_error = format_error(error)
    
    # Add custom error information
    if hasattr(error, 'extensions') and error.extensions:
        formatted_error["extensions"] = error.extensions
    
    # Remove stack trace in production
    if settings.ENVIRONMENT == "production":
        formatted_error.pop("locations", None)
        if "extensions" in formatted_error:
            formatted_error["extensions"].pop("stack_trace", None)
    
    return formatted_error


# Error reporting utilities
class ErrorReporter:
    """Reports errors to external monitoring services"""
    
    def __init__(self):
        self.metrics = ErrorMetrics()
    
    async def report_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Report error to monitoring services"""
        
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to error tracking service (Sentry, Rollbar, etc.)
        # This would typically use the configured error tracking service
        logger.error("Error reported to monitoring", extra=error_data)
        
        # Record metrics
        self.metrics.record_reported_error(
            error_type=type(error).__name__,
            context=context
        )


# Global instances
error_handler = GraphQLErrorHandler()
error_reporter = ErrorReporter()


# Export for template system
__all__ = [
    "GraphQLErrorHandler",
    "ErrorClassifier",
    "ErrorAggregator",
    "ErrorReporter",
    "GraphQLErrorInfo",
    "ErrorContext",
    "ErrorCategory",
    "ErrorSeverity",
    "format_graphql_error",
    "error_handler",
    "error_reporter"
]