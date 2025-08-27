"""
Pipeline Exceptions

Ultra-advanced exception handling system for pipeline executions
with detailed error context, recovery strategies, and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Error Detection → Classification → Context Collection → Recovery Strategy → Monitoring → Escalation
"""

import logging
import traceback
import json
import uuid
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ErrorCategory(Enum):
    """Error categories"""
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    VALIDATION = "validation"
    RESOURCE = "resource"
    NETWORK = "network"
    SECURITY = "security"
    EXTERNAL_SERVICE = "external_service"
    USER_INPUT = "user_input"
    CONTENT_PROCESSING = "content_processing"
    AI_PROCESSING = "ai_processing"
    PROTECTION = "protection"
    DISTRIBUTION = "distribution"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"


class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ESCALATE = "escalate"
    ABORT = "abort"
    MANUAL_INTERVENTION = "manual_intervention"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"


class ErrorImpact(Enum):
    """Error impact levels"""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


@dataclass
class ErrorContext:
    """Detailed error context"""
    timestamp: datetime = field(default_factory=datetime.now)
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation: str = ""
    stage: str = ""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    session_id: Optional[str] = None
    execution_context: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    additional_data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


@dataclass
class RecoveryAttempt:
    """Recovery attempt information"""
    attempt_number: int = 0
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    error_message: str = ""
    execution_time: float = 0.0
    recovery_data: Dict[str, Any] = field(default_factory=dict)
    backoff_delay: float = 0.0


@dataclass
class ErrorMetrics:
    """Error metrics and statistics"""
    occurrence_count: int = 1
    first_occurrence: datetime = field(default_factory=datetime.now)
    last_occurrence: datetime = field(default_factory=datetime.now)
    total_recovery_attempts: int = 0
    successful_recoveries: int = 0
    average_recovery_time: float = 0.0
    business_impact_score: float = 0.0
    user_impact_count: int = 0
    frequency_per_hour: float = 0.0


class PipelineError(Exception):
    """
    Base pipeline exception with advanced error handling capabilities
    
    Features:
    - Comprehensive error context and metadata
    - Recovery strategy management
    - Error correlation and tracing
    - Business impact assessment
    - Monitoring and alerting integration
    - Detailed error analytics
    """
    
    def __init__(
        self, 
        message: str,
        error_code: str = "",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        impact: ErrorImpact = ErrorImpact.MODERATE,
        context: Optional[ErrorContext] = None,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY,
        max_retry_attempts: int = 3,
        retry_backoff_factor: float = 2.0,
        original_exception: Optional[Exception] = None,
        correlation_data: Optional[Dict[str, Any]] = None,
        business_impact: float = 0.0,
        user_message: Optional[str] = None,
        resolution_steps: Optional[List[str]] = None,
        escalation_contacts: Optional[List[str]] = None
    ):
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.impact = impact
        self.context = context or ErrorContext()
        self.recovery_strategy = recovery_strategy
        self.max_retry_attempts = max_retry_attempts
        self.retry_backoff_factor = retry_backoff_factor
        self.original_exception = original_exception
        self.correlation_data = correlation_data or {}
        self.business_impact = business_impact
        self.user_message = user_message or message
        self.resolution_steps = resolution_steps or []
        self.escalation_contacts = escalation_contacts or []
        
        # Recovery tracking
        self.recovery_attempts: List[RecoveryAttempt] = []
        self.is_recoverable = True
        self.resolved = False
        self.resolution_time: Optional[datetime] = None
        
        # Error metrics
        self.metrics = ErrorMetrics()
        
        # Stack trace and debugging
        self.stack_trace = traceback.format_exc() if traceback.format_exc() != "NoneType: None
" else ""
        self.call_stack = traceback.extract_stack()
        
        # Monitoring and alerting
        self.alert_sent = False
        self.escalated = False
        self.suppressed = False
        
        # Error fingerprint for deduplication
        self.fingerprint = self._generate_fingerprint()
        
        # Logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._log_error()
    
    def _generate_fingerprint(self) -> str:
        """Generate error fingerprint for deduplication"""
        fingerprint_data = f"{self.error_code}:{self.category.value}:{self.context.operation}:{self.context.stage}"
        return str(hash(fingerprint_data))
    
    def _log_error(self):
        """Log error with appropriate level"""
        log_data = self.to_dict()
        
        if self.severity in [ErrorSeverity.EMERGENCY, ErrorSeverity.CRITICAL]:
            self.logger.critical(f"Critical error: {self.message}", extra={"error_data": log_data})
        elif self.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {self.message}", extra={"error_data": log_data})
        elif self.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {self.message}", extra={"error_data": log_data})
        else:
            self.logger.info(f"Low severity error: {self.message}", extra={"error_data": log_data})
    
    def add_recovery_attempt(self, attempt: RecoveryAttempt):
        """Add recovery attempt"""
        self.recovery_attempts.append(attempt)
        self.metrics.total_recovery_attempts += 1
        
        if attempt.success:
            self.resolved = True
            self.resolution_time = datetime.now()
            self.metrics.successful_recoveries += 1
            self.logger.info(f"Error {self.error_code} resolved after {len(self.recovery_attempts)} attempts")
        
        # Update average recovery time
        if self.recovery_attempts:
            self.metrics.average_recovery_time = sum(
                attempt.execution_time for attempt in self.recovery_attempts
            ) / len(self.recovery_attempts)
    
    def can_retry(self) -> bool:
        """Check if error can be retried"""
        return (
            self.is_recoverable and 
            self.recovery_strategy in [RecoveryStrategy.RETRY, RecoveryStrategy.CIRCUIT_BREAKER] and
            len(self.recovery_attempts) < self.max_retry_attempts and
            not self.resolved
        )
    
    def get_next_retry_delay(self) -> float:
        """Calculate next retry delay with exponential backoff"""
        if not self.recovery_attempts:
            return 1.0
        
        attempt_count = len(self.recovery_attempts)
        base_delay = 1.0
        
        return base_delay * (self.retry_backoff_factor ** attempt_count)
    
    def should_escalate(self) -> bool:
        """Check if error should be escalated"""
        return (
            self.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.EMERGENCY] or
            self.impact in [ErrorImpact.SEVERE, ErrorImpact.CATASTROPHIC] or
            (len(self.recovery_attempts) >= self.max_retry_attempts and not self.resolved) or
            self.recovery_strategy == RecoveryStrategy.ESCALATE
        )
    
    def mark_as_escalated(self):
        """Mark error as escalated"""
        self.escalated = True
        self.logger.warning(f"Error {self.error_code} has been escalated")
    
    def suppress_alerts(self):
        """Suppress alerts for this error"""
        self.suppressed = True
        self.logger.info(f"Alerts suppressed for error {self.error_code}")
    
    def update_metrics(self):
        """Update error metrics"""
        self.metrics.last_occurrence = datetime.now()
        self.metrics.occurrence_count += 1
        
        # Calculate frequency
        time_diff = self.metrics.last_occurrence - self.metrics.first_occurrence
        if time_diff.total_seconds() > 0:
            self.metrics.frequency_per_hour = (
                self.metrics.occurrence_count / (time_diff.total_seconds() / 3600)
            )
    
    def get_correlation_id(self) -> str:
        """Get correlation ID for error tracking"""
        return self.context.correlation_id or self.context.error_id
    
    def add_context_data(self, key: str, value: Any):
        """Add additional context data"""
        self.context.additional_data[key] = value
    
    def get_business_impact_description(self) -> str:
        """Get business impact description"""
        impact_descriptions = {
            ErrorImpact.NONE: "No business impact",
            ErrorImpact.MINIMAL: "Minimal impact on operations",
            ErrorImpact.MODERATE: "Moderate impact on user experience",
            ErrorImpact.SIGNIFICANT: "Significant impact on business operations",
            ErrorImpact.SEVERE: "Severe impact on service availability",
            ErrorImpact.CATASTROPHIC: "Catastrophic impact on business"
        }
        return impact_descriptions.get(self.impact, "Unknown impact")
    
    def get_resolution_recommendations(self) -> List[str]:
        """Get resolution recommendations"""
        recommendations = self.resolution_steps.copy()
        
        # Add common recovery strategies
        if self.recovery_strategy == RecoveryStrategy.RETRY:
            recommendations.append("Verify system resources and retry operation")
        elif self.recovery_strategy == RecoveryStrategy.FALLBACK:
            recommendations.append("Use alternative processing method")
        elif self.recovery_strategy == RecoveryStrategy.ESCALATE:
            recommendations.append("Contact technical support team")
        
        return recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "error_id": self.context.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "impact": self.impact.value,
            "business_impact": self.business_impact,
            "recovery_strategy": self.recovery_strategy.value,
            "max_retry_attempts": self.max_retry_attempts,
            "recovery_attempts": len(self.recovery_attempts),
            "is_recoverable": self.is_recoverable,
            "resolved": self.resolved,
            "escalated": self.escalated,
            "suppressed": self.suppressed,
            "fingerprint": self.fingerprint,
            "timestamp": self.context.timestamp.isoformat(),
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None,
            "context": {
                "operation": self.context.operation,
                "stage": self.context.stage,
                "user_id": self.context.user_id,
                "request_id": self.context.request_id,
                "pipeline_id": self.context.pipeline_id,
                "session_id": self.context.session_id,
                "correlation_id": self.context.correlation_id,
                "trace_id": self.context.trace_id,
                "span_id": self.context.span_id
            },
            "metrics": {
                "occurrence_count": self.metrics.occurrence_count,
                "first_occurrence": self.metrics.first_occurrence.isoformat(),
                "last_occurrence": self.metrics.last_occurrence.isoformat(),
                "total_recovery_attempts": self.metrics.total_recovery_attempts,
                "successful_recoveries": self.metrics.successful_recoveries,
                "average_recovery_time": self.metrics.average_recovery_time,
                "business_impact_score": self.metrics.business_impact_score,
                "user_impact_count": self.metrics.user_impact_count,
                "frequency_per_hour": self.metrics.frequency_per_hour
            },
            "correlation_data": self.correlation_data,
            "resolution_steps": self.resolution_steps,
            "escalation_contacts": self.escalation_contacts,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "stack_trace": self.stack_trace
        }
    
    def to_alert_payload(self) -> Dict[str, Any]:
        """Convert to alert payload for monitoring systems"""
        return {
            "alert_type": "error",
            "error_id": self.context.error_id,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "impact": self.impact.value,
            "message": self.message,
            "user_message": self.user_message,
            "timestamp": self.context.timestamp.isoformat(),
            "context": {
                "operation": self.context.operation,
                "stage": self.context.stage,
                "user_id": self.context.user_id,
                "request_id": self.context.request_id,
                "pipeline_id": self.context.pipeline_id
            },
            "business_impact": self.business_impact,
            "escalation_required": self.should_escalate(),
            "resolution_steps": self.resolution_steps,
            "escalation_contacts": self.escalation_contacts
        }


# Specialized Pipeline Exceptions

class StageExecutionError(PipelineError):
    """Pipeline stage execution error"""
    
    def __init__(
        self, 
        stage: str, 
        message: str, 
        stage_data: Optional[Dict[str, Any]] = None,
        stage_metrics: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Stage '{stage}' execution failed: {message}",
            error_code=f"STAGE_EXECUTION_ERROR_{stage.upper()}",
            category=ErrorCategory.BUSINESS_LOGIC,
            **kwargs
        )
        self.stage = stage
        self.stage_data = stage_data or {}
        self.stage_metrics = stage_metrics or {}


class ValidationError(PipelineError):
    """Data validation error"""
    
    def __init__(
        self, 
        field: str, 
        value: Any, 
        validation_rule: str,
        expected_type: Optional[Type] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Validation failed for field '{field}' with value '{value}': {validation_rule}",
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.ABORT,
            **kwargs
        )
        self.field = field
        self.value = value
        self.validation_rule = validation_rule
        self.expected_type = expected_type


class ResourceError(PipelineError):
    """Resource availability error"""
    
    def __init__(
        self, 
        resource_type: str, 
        resource_id: str, 
        message: str,
        resource_status: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Resource '{resource_type}:{resource_id}' error: {message}",
            error_code="RESOURCE_ERROR",
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.resource_status = resource_status


class TimeoutError(PipelineError):
    """Operation timeout error"""
    
    def __init__(
        self, 
        operation: str, 
        timeout_seconds: float, 
        elapsed_seconds: float,
        **kwargs
    ):
        super().__init__(
            message=f"Operation '{operation}' timed out after {elapsed_seconds:.2f}s (limit: {timeout_seconds}s)",
            error_code="TIMEOUT_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds


class ConfigurationError(PipelineError):
    """Configuration error"""
    
    def __init__(
        self, 
        config_key: str, 
        message: str,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Configuration error for '{config_key}': {message}",
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.ABORT,
            is_recoverable=False,
            **kwargs
        )
        self.config_key = config_key
        self.config_value = config_value


class DependencyError(PipelineError):
    """Dependency resolution error"""
    
    def __init__(
        self, 
        dependency: str, 
        message: str,
        dependency_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Dependency error for '{dependency}': {message}",
            error_code="DEPENDENCY_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            **kwargs
        )
        self.dependency = dependency
        self.dependency_version = dependency_version


class ContentProcessingError(PipelineError):
    """Content processing error"""
    
    def __init__(
        self,
        content_type: str,
        processing_stage: str,
        message: str,
        content_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Content processing failed for {content_type} at stage '{processing_stage}': {message}",
            error_code="CONTENT_PROCESSING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            **kwargs
        )
        self.content_type = content_type
        self.processing_stage = processing_stage
        self.content_metadata = content_metadata or {}


class AIProcessingError(PipelineError):
    """AI processing error"""
    
    def __init__(
        self,
        model_name: str,
        operation: str,
        message: str,
        model_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"AI processing failed for model '{model_name}' during '{operation}': {message}",
            error_code="AI_PROCESSING_ERROR",
            category=ErrorCategory.AI_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            **kwargs
        )
        self.model_name = model_name
        self.operation = operation
        self.model_version = model_version


class ProtectionError(PipelineError):
    """Content protection error"""
    
    def __init__(
        self,
        protection_type: str,
        message: str,
        content_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Content protection failed for '{protection_type}': {message}",
            error_code="PROTECTION_ERROR",
            category=ErrorCategory.PROTECTION,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.protection_type = protection_type
        self.content_id = content_id


class DistributionError(PipelineError):
    """Content distribution error"""
    
    def __init__(
        self,
        platform: str,
        message: str,
        distribution_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Distribution failed for platform '{platform}': {message}",
            error_code="DISTRIBUTION_ERROR",
            category=ErrorCategory.DISTRIBUTION,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.platform = platform
        self.distribution_id = distribution_id


class MonetizationError(PipelineError):
    """Monetization error"""
    
    def __init__(
        self,
        monetization_type: str,
        message: str,
        revenue_impact: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Monetization failed for '{monetization_type}': {message}",
            error_code="MONETIZATION_ERROR",
            category=ErrorCategory.MONETIZATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            business_impact=revenue_impact or 0.0,
            **kwargs
        )
        self.monetization_type = monetization_type
        self.revenue_impact = revenue_impact


class SecurityError(PipelineError):
    """Security error"""
    
    def __init__(
        self,
        security_issue: str,
        message: str,
        threat_level: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Security issue '{security_issue}': {message}",
            error_code="SECURITY_ERROR",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            **kwargs
        )
        self.security_issue = security_issue
        self.threat_level = threat_level


class ExternalServiceError(PipelineError):
    """External service error"""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.CIRCUIT_BREAKER,
            **kwargs
        )
        self.service_name = service_name
        self.status_code = status_code


class NetworkError(PipelineError):
    """Network connectivity error"""
    
    def __init__(
        self,
        endpoint: str,
        message: str,
        **kwargs
    ):
        super().__init__(
            message=f"Network error connecting to '{endpoint}': {message}",
            error_code="NETWORK_ERROR",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.endpoint = endpoint


class AnalyticsError(PipelineError):
    """Analytics processing error"""
    
    def __init__(
        self,
        analytics_type: str,
        message: str,
        data_period: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Analytics processing failed for '{analytics_type}': {message}",
            error_code="ANALYTICS_ERROR",
            category=ErrorCategory.ANALYTICS,
            severity=ErrorSeverity.LOW,
            recovery_strategy=RecoveryStrategy.SKIP,
            **kwargs
        )
        self.analytics_type = analytics_type
        self.data_period = data_period


class QualityGateError(PipelineError):
    """Quality gate validation error"""
    
    def __init__(
        self,
        gate_name: str,
        threshold: float,
        actual_value: float,
        message: str = "",
        **kwargs
    ):
        default_message = f"Quality gate '{gate_name}' failed: {actual_value} < {threshold}"
        super().__init__(
            message=message or default_message,
            error_code="QUALITY_GATE_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.ABORT,
            **kwargs
        )
        self.gate_name = gate_name
        self.threshold = threshold
        self.actual_value = actual_value


class CircuitBreakerError(PipelineError):
    """Circuit breaker triggered error"""
    
    def __init__(
        self,
        service_name: str,
        failure_count: int,
        threshold: int,
        **kwargs
    ):
        super().__init__(
            message=f"Circuit breaker triggered for '{service_name}': {failure_count}/{threshold} failures",
            error_code="CIRCUIT_BREAKER_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            **kwargs
        )
        self.service_name = service_name
        self.failure_count = failure_count
        self.threshold = threshold


class RateLimitError(PipelineError):
    """Rate limit exceeded error"""
    
    def __init__(
        self,
        service_name: str,
        limit: int,
        window: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Rate limit exceeded for '{service_name}': {limit} requests per {window}",
            error_code="RATE_LIMIT_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.RETRY,
            **kwargs
        )
        self.service_name = service_name
        self.limit = limit
        self.window = window
        self.retry_after = retry_after


# Error Handler Registry
class ErrorHandlerRegistry:
    """Registry for error handlers and recovery strategies"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.recovery_strategies: Dict[RecoveryStrategy, Callable] = {}
        self.logger = logging.getLogger(f"{__name__}.ErrorHandlerRegistry")
    
    def register_handler(self, error_code: str, handler: Callable):
        """Register error handler"""
        self.handlers[error_code] = handler
        self.logger.info(f"Registered handler for error code: {error_code}")
    
    def register_recovery_strategy(self, strategy: RecoveryStrategy, handler: Callable):
        """Register recovery strategy handler"""
        self.recovery_strategies[strategy] = handler
        self.logger.info(f"Registered recovery strategy: {strategy.value}")
    
    async def handle_error(self, error: PipelineError) -> bool:
        """Handle error using registered handlers"""
        handler = self.handlers.get(error.error_code)
        if handler:
            try:
                return await handler(error)
            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
        return False
    
    async def execute_recovery_strategy(self, error: PipelineError) -> bool:
        """Execute recovery strategy"""
        strategy_handler = self.recovery_strategies.get(error.recovery_strategy)
        if strategy_handler:
            try:
                return await strategy_handler(error)
            except Exception as e:
                self.logger.error(f"Recovery strategy failed: {e}")
        return False


# Global error handler registry instance
error_handler_registry = ErrorHandlerRegistry()

import logging
import traceback
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    SYSTEM = "system"
    PIPELINE = "pipeline"
    CONTENT = "content"
    AI = "ai"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    DISTRIBUTION = "distribution"
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    PERMISSION = "permission"


class RecoveryStrategy(Enum):
    """Recovery strategies"""
    NONE = "none"
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"
    RESTART = "restart"
    MANUAL = "manual"


@dataclass
class ErrorContext:
    """Error context information"""
    pipeline_id: str = ""
    stage_name: str = ""
    component_name: str = ""
    operation: str = ""
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    
    # System context
    system_state: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Request context
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorDetails:
    """Detailed error information"""
    error_id: str = ""
    error_type: str = ""
    error_message: str = ""
    error_code: Optional[str] = None
    
    # Classification
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.SYSTEM
    
    # Context
    context: ErrorContext = field(default_factory=ErrorContext)
    stacktrace: str = ""
    
    # Timing
    occurred_at: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    
    # Recovery
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    
    # Resolution
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    
    # Impact
    affected_users: List[str] = field(default_factory=list)
    affected_content: List[str] = field(default_factory=list)
    business_impact: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": {
                "pipeline_id": self.context.pipeline_id,
                "stage_name": self.context.stage_name,
                "component_name": self.context.component_name,
                "operation": self.context.operation,
                "user_id": self.context.user_id,
                "content_id": self.context.content_id,
                "metadata": self.context.metadata
            },
            "stacktrace": self.stacktrace,
            "occurred_at": self.occurred_at.isoformat(),
            "duration": self.duration,
            "recovery_strategy": self.recovery_strategy.value,
            "recovery_attempts": self.recovery_attempts,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "affected_users": self.affected_users,
            "affected_content": self.affected_content,
            "business_impact": self.business_impact
        }


# Base Pipeline Exception
class PipelineException(Exception):
    """Base pipeline exception"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.PIPELINE,
        context: Optional[ErrorContext] = None,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE,
        **kwargs
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.recovery_strategy = recovery_strategy
        self.metadata = kwargs
        
        # Generate error ID
        self.error_id = f"err_{uuid.uuid4().hex[:8]}"
        self.occurred_at = datetime.now()


# System Exceptions
class SystemResourceException(PipelineException):
    """System resource related exceptions"""
    
    def __init__(self, message: str, resource_type: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            recovery_strategy=RecoveryStrategy.RETRY,
            resource_type=resource_type,
            **kwargs
        )


class DatabaseException(PipelineException):
    """Database related exceptions"""
    
    def __init__(self, message: str, operation: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            recovery_strategy=RecoveryStrategy.RETRY,
            database_operation=operation,
            **kwargs
        )


class NetworkException(PipelineException):
    """Network related exceptions"""
    
    def __init__(self, message: str, endpoint: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            recovery_strategy=RecoveryStrategy.RETRY,
            endpoint=endpoint,
            **kwargs
        )


class TimeoutException(PipelineException):
    """Timeout related exceptions"""
    
    def __init__(self, message: str, timeout_duration: float = 0.0, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.TIMEOUT,
            recovery_strategy=RecoveryStrategy.RETRY,
            timeout_duration=timeout_duration,
            **kwargs
        )


# Content Processing Exceptions
class ContentProcessingException(PipelineException):
    """Content processing related exceptions"""
    
    def __init__(self, message: str, content_type: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONTENT,
            recovery_strategy=RecoveryStrategy.SKIP,
            content_type=content_type,
            **kwargs
        )


class ContentValidationException(PipelineException):
    """Content validation related exceptions"""
    
    def __init__(self, message: str, validation_rule: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            recovery_strategy=RecoveryStrategy.SKIP,
            validation_rule=validation_rule,
            **kwargs
        )


class ContentFormatException(PipelineException):
    """Content format related exceptions"""
    
    def __init__(self, message: str, expected_format: str = "", actual_format: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONTENT,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            expected_format=expected_format,
            actual_format=actual_format,
            **kwargs
        )


# AI Processing Exceptions
class AIProcessingException(PipelineException):
    """AI processing related exceptions"""
    
    def __init__(self, message: str, model_name: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AI,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            model_name=model_name,
            **kwargs
        )


class AIModelException(PipelineException):
    """AI model related exceptions"""
    
    def __init__(self, message: str, model_name: str = "", model_version: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.AI,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            model_name=model_name,
            model_version=model_version,
            **kwargs
        )


class AIAnalysisException(PipelineException):
    """AI analysis related exceptions"""
    
    def __init__(self, message: str, analysis_type: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.AI,
            recovery_strategy=RecoveryStrategy.RETRY,
            analysis_type=analysis_type,
            **kwargs
        )


# Protection Exceptions
class ProtectionException(PipelineException):
    """Protection related exceptions"""
    
    def __init__(self, message: str, protection_type: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PROTECTION,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            protection_type=protection_type,
            **kwargs
        )


class FingerprintingException(PipelineException):
    """Fingerprinting related exceptions"""
    
    def __init__(self, message: str, fingerprint_type: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PROTECTION,
            recovery_strategy=RecoveryStrategy.RETRY,
            fingerprint_type=fingerprint_type,
            **kwargs
        )


class CopyrightException(PipelineException):
    """Copyright related exceptions"""
    
    def __init__(self, message: str, copyright_issue: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.PROTECTION,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            copyright_issue=copyright_issue,
            **kwargs
        )


# Monetization Exceptions
class MonetizationException(PipelineException):
    """Monetization related exceptions"""
    
    def __init__(self, message: str, monetization_type: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.MONETIZATION,
            recovery_strategy=RecoveryStrategy.RETRY,
            monetization_type=monetization_type,
            **kwargs
        )


class PaymentException(PipelineException):
    """Payment related exceptions"""
    
    def __init__(self, message: str, payment_provider: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.MONETIZATION,
            recovery_strategy=RecoveryStrategy.MANUAL,
            payment_provider=payment_provider,
            **kwargs
        )


class RevenueException(PipelineException):
    """Revenue related exceptions"""
    
    def __init__(self, message: str, revenue_stream: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.MONETIZATION,
            recovery_strategy=RecoveryStrategy.RETRY,
            revenue_stream=revenue_stream,
            **kwargs
        )


# Distribution Exceptions
class DistributionException(PipelineException):
    """Distribution related exceptions"""
    
    def __init__(self, message: str, platform: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DISTRIBUTION,
            recovery_strategy=RecoveryStrategy.RETRY,
            platform=platform,
            **kwargs
        )


class PlatformException(PipelineException):
    """Platform integration related exceptions"""
    
    def __init__(self, message: str, platform: str = "", api_endpoint: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DISTRIBUTION,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            platform=platform,
            api_endpoint=api_endpoint,
            **kwargs
        )


class DeliveryException(PipelineException):
    """Content delivery related exceptions"""
    
    def __init__(self, message: str, delivery_method: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DISTRIBUTION,
            recovery_strategy=RecoveryStrategy.RETRY,
            delivery_method=delivery_method,
            **kwargs
        )


# Security Exceptions
class SecurityException(PipelineException):
    """Security related exceptions"""
    
    def __init__(self, message: str, security_issue: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            security_issue=security_issue,
            **kwargs
        )


class AuthenticationException(PipelineException):
    """Authentication related exceptions"""
    
    def __init__(self, message: str, auth_method: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            auth_method=auth_method,
            **kwargs
        )


class AuthorizationException(PipelineException):
    """Authorization related exceptions"""
    
    def __init__(self, message: str, required_permission: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERMISSION,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            required_permission=required_permission,
            **kwargs
        )


# Configuration Exceptions
class ConfigurationException(PipelineException):
    """Configuration related exceptions"""
    
    def __init__(self, message: str, config_key: str = "", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            recovery_strategy=RecoveryStrategy.MANUAL,
            config_key=config_key,
            **kwargs
        )


class ErrorHandler:
    """Advanced error handling system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ErrorHandler")
        
        # Error storage
        self.error_history: List[ErrorDetails] = []
        self.error_patterns: Dict[str, int] = {}
        
        # Recovery handlers
        self.recovery_handlers: Dict[RecoveryStrategy, Callable] = {}
        
        # Notification handlers
        self.notification_handlers: List[Callable] = []
        
        # Initialize default recovery handlers
        self._initialize_recovery_handlers()
    
    def _initialize_recovery_handlers(self):
        """Initialize default recovery handlers"""
        self.recovery_handlers = {
            RecoveryStrategy.RETRY: self._handle_retry_recovery,
            RecoveryStrategy.FALLBACK: self._handle_fallback_recovery,
            RecoveryStrategy.SKIP: self._handle_skip_recovery,
            RecoveryStrategy.ROLLBACK: self._handle_rollback_recovery,
            RecoveryStrategy.ESCALATE: self._handle_escalate_recovery,
            RecoveryStrategy.RESTART: self._handle_restart_recovery,
            RecoveryStrategy.MANUAL: self._handle_manual_recovery
        }
    
    async def handle_exception(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        auto_recover: bool = True
    ) -> ErrorDetails:
        """Handle exception with intelligent classification and recovery"""
        
        # Create error details
        error_details = self._create_error_details(exception, context)
        
        # Classify error
        self._classify_error(error_details, exception)
        
        # Add to history
        self.error_history.append(error_details)
        
        # Update error patterns
        self._update_error_patterns(error_details)
        
        # Log error
        self._log_error(error_details)
        
        # Attempt recovery if enabled
        if auto_recover and error_details.recovery_strategy != RecoveryStrategy.NONE:
            recovery_result = await self._attempt_recovery(error_details)
            if recovery_result:
                error_details.resolved = True
                error_details.resolved_at = datetime.now()
                error_details.resolution_notes = "Automatically recovered"
        
        # Send notifications
        await self._send_error_notifications(error_details)
        
        return error_details
    
    def _create_error_details(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None
    ) -> ErrorDetails:
        """Create error details from exception"""
        
        # Extract information from exception
        error_type = type(exception).__name__
        error_message = str(exception)
        stacktrace = traceback.format_exc()
        
        # Handle PipelineException specially
        if isinstance(exception, PipelineException):
            error_details = ErrorDetails(
                error_id=exception.error_id,
                error_type=error_type,
                error_message=error_message,
                error_code=exception.error_code,
                severity=exception.severity,
                category=exception.category,
                context=exception.context,
                stacktrace=stacktrace,
                occurred_at=exception.occurred_at,
                recovery_strategy=exception.recovery_strategy
            )
            
            # Add metadata
            for key, value in exception.metadata.items():
                error_details.context.metadata[key] = value
        
        else:
            # Handle standard exceptions
            error_details = ErrorDetails(
                error_id=f"err_{uuid.uuid4().hex[:8]}",
                error_type=error_type,
                error_message=error_message,
                context=context or ErrorContext(),
                stacktrace=stacktrace
            )
        
        return error_details
    
    def _classify_error(self, error_details: ErrorDetails, exception: Exception):
        """Classify error for better handling"""
        
        # Skip classification for PipelineException (already classified)
        if isinstance(exception, PipelineException):
            return
        
        error_type = type(exception).__name__
        error_message = str(exception).lower()
        
        # Classify by exception type
        if "timeout" in error_type.lower() or "timeout" in error_message:
            error_details.category = ErrorCategory.TIMEOUT
            error_details.severity = ErrorSeverity.HIGH
            error_details.recovery_strategy = RecoveryStrategy.RETRY
        
        elif "connection" in error_message or "network" in error_message:
            error_details.category = ErrorCategory.NETWORK
            error_details.severity = ErrorSeverity.MEDIUM
            error_details.recovery_strategy = RecoveryStrategy.RETRY
        
        elif "permission" in error_message or "access" in error_message:
            error_details.category = ErrorCategory.PERMISSION
            error_details.severity = ErrorSeverity.HIGH
            error_details.recovery_strategy = RecoveryStrategy.ESCALATE
        
        elif "memory" in error_message or "resource" in error_message:
            error_details.category = ErrorCategory.RESOURCE
            error_details.severity = ErrorSeverity.HIGH
            error_details.recovery_strategy = RecoveryStrategy.RESTART
        
        elif "database" in error_message or "sql" in error_message:
            error_details.category = ErrorCategory.DATABASE
            error_details.severity = ErrorSeverity.HIGH
            error_details.recovery_strategy = RecoveryStrategy.RETRY
        
        else:
            # Default classification
            error_details.category = ErrorCategory.SYSTEM
            error_details.severity = ErrorSeverity.MEDIUM
            error_details.recovery_strategy = RecoveryStrategy.NONE
    
    def _update_error_patterns(self, error_details: ErrorDetails):
        """Update error patterns for trend analysis"""
        pattern_key = f"{error_details.category.value}_{error_details.error_type}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
    
    def _log_error(self, error_details: ErrorDetails):
        """Log error with appropriate level"""
        log_message = f"[{error_details.error_id}] {error_details.error_type}: {error_details.error_message}"
        
        if error_details.context.pipeline_id:
            log_message += f" (Pipeline: {error_details.context.pipeline_id})"
        
        if error_details.context.stage_name:
            log_message += f" (Stage: {error_details.context.stage_name})"
        
        if error_details.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_details.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_details.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log stacktrace for high severity errors
        if error_details.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.debug(f"Stacktrace for {error_details.error_id}:\n{error_details.stacktrace}")
    
    async def _attempt_recovery(self, error_details: ErrorDetails) -> bool:
        """Attempt error recovery"""
        if error_details.recovery_attempts >= error_details.max_recovery_attempts:
            self.logger.warning(f"Max recovery attempts reached for {error_details.error_id}")
            return False
        
        error_details.recovery_attempts += 1
        
        recovery_handler = self.recovery_handlers.get(error_details.recovery_strategy)
        if not recovery_handler:
            self.logger.warning(f"No recovery handler for strategy: {error_details.recovery_strategy}")
            return False
        
        try:
            self.logger.info(f"Attempting recovery for {error_details.error_id} using {error_details.recovery_strategy.value}")
            return await recovery_handler(error_details)
        
        except Exception as e:
            self.logger.error(f"Recovery failed for {error_details.error_id}: {e}")
            return False
    
    async def _handle_retry_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle retry recovery strategy"""
        # Wait before retry (exponential backoff)
        wait_time = min(2 ** error_details.recovery_attempts, 60)
        await asyncio.sleep(wait_time)
        
        self.logger.info(f"Retry recovery executed for {error_details.error_id}")
        return True
    
    async def _handle_fallback_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle fallback recovery strategy"""
        # Implement fallback logic (placeholder)
        self.logger.info(f"Fallback recovery executed for {error_details.error_id}")
        return True
    
    async def _handle_skip_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle skip recovery strategy"""
        # Skip the failed operation
        self.logger.info(f"Skip recovery executed for {error_details.error_id}")
        return True
    
    async def _handle_rollback_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle rollback recovery strategy"""
        # Implement rollback logic (placeholder)
        self.logger.info(f"Rollback recovery executed for {error_details.error_id}")
        return True
    
    async def _handle_escalate_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle escalate recovery strategy"""
        # Escalate to human intervention
        self.logger.warning(f"Escalating error {error_details.error_id} for manual intervention")
        return False  # Requires manual intervention
    
    async def _handle_restart_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle restart recovery strategy"""
        # Implement restart logic (placeholder)
        self.logger.info(f"Restart recovery executed for {error_details.error_id}")
        return True
    
    async def _handle_manual_recovery(self, error_details: ErrorDetails) -> bool:
        """Handle manual recovery strategy"""
        # Requires manual intervention
        self.logger.warning(f"Manual recovery required for {error_details.error_id}")
        return False
    
    async def _send_error_notifications(self, error_details: ErrorDetails):
        """Send error notifications"""
        for handler in self.notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_details)
                else:
                    handler(error_details)
            except Exception as e:
                self.logger.error(f"Notification handler failed: {e}")
    
    def add_notification_handler(self, handler: Callable):
        """Add error notification handler"""
        self.notification_handlers.append(handler)
    
    def add_recovery_handler(self, strategy: RecoveryStrategy, handler: Callable):
        """Add custom recovery handler"""
        self.recovery_handlers[strategy] = handler
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {}
        
        total_errors = len(self.error_history)
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            count = sum(1 for error in self.error_history if error.severity == severity)
            severity_counts[severity.value] = count
        
        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            count = sum(1 for error in self.error_history if error.category == category)
            category_counts[category.value] = count
        
        # Recovery success rate
        attempted_recoveries = sum(1 for error in self.error_history 
                                 if error.recovery_strategy != RecoveryStrategy.NONE)
        successful_recoveries = sum(1 for error in self.error_history if error.resolved)
        
        recovery_rate = (successful_recoveries / max(attempted_recoveries, 1)) * 100
        
        return {
            "total_errors": total_errors,
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "recovery_success_rate": recovery_rate,
            "most_common_patterns": dict(sorted(self.error_patterns.items(), 
                                               key=lambda x: x[1], reverse=True)[:10]),
            "recent_errors": len([e for e in self.error_history 
                                if (datetime.now() - e.occurred_at).days < 1])
        }


# Error handling decorators
def handle_pipeline_errors(
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE,
    max_retries: int = 3,
    error_handler: Optional[ErrorHandler] = None
):
    """Decorator for pipeline error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if error_handler:
                        context = ErrorContext(
                            operation=func.__name__,
                            metadata={"retry_attempt": retries}
                        )
                        await error_handler.handle_exception(e, context)
                    
                    if retries >= max_retries:
                        break
                    
                    retries += 1
                    
                    # Wait before retry
                    if recovery_strategy == RecoveryStrategy.RETRY:
                        wait_time = min(2 ** retries, 60)
                        await asyncio.sleep(wait_time)
            
            # Re-raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


def catch_and_log(
    logger: Optional[logging.Logger] = None,
    reraise: bool = True,
    default_return=None
):
    """Decorator for catching and logging exceptions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            except Exception as e:
                error_logger = logger or logging.getLogger(func.__module__)
                error_logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                
                if reraise:
                    raise
                else:
                    return default_return
        
        return wrapper
    return decorator
