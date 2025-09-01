# -*- coding: utf-8 -*-
"""IA Influencer Agent - Advanced Business Exception Management

This module provides comprehensive exception handling for the notification system,
ensuring robust error management and detailed error reporting for business operations.
All exceptions include detailed context, business impact assessment, and recovery guidance.

LEGAL WARNING:
This code is protected by copyright and proprietary rights. 
Any unauthorized reproduction, distribution, or commercial use is strictly prohibited.
Violations will be prosecuted to the full extent of the law.
Developed by Mlaiel for IA Influencer Agent Platform.

Architecture Pattern: Exception Hierarchy with Business Context
Processing Level: Industrial-Grade Error Management
Creation Pattern: Enterprise Exception Handling
Business Logic Integration: Complete Error Tracking and Recovery
"""

import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """
Error severity levels for business operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class ErrorCategory(Enum):
    """Categorization of business errors."""

    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    BUSINESS_RULE = "business_rule"
    TECHNICAL = "technical"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    USER_ERROR = "user_error"
    SYSTEM_ERROR = "system_error"
    DATA_ERROR = "data_error"


@dataclass
class ErrorContext:
    """Comprehensive error context for business operations."""
    error_id: str
    timestamp: datetime
    user_id: Optional[str] = None
    creator_type: Optional[str] = None
    notification_id: Optional[str] = None
    workflow_id: Optional[str] = None
    business_context: Optional[Dict[str, Any]] = None
    technical_context: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    environment: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class BusinessImpact:
    """
Assessment of business impact for errors."""
    revenue_impact: float  # Estimated revenue impact in USD
    user_affected_count: int  # Number of users affected
    service_disruption: bool  # Whether service is disrupted
    data_integrity_risk: bool  # Whether data integrity is at risk
    compliance_risk: bool  # Whether compliance is at risk
    reputation_impact: str  # Description of reputation impact
    recovery_time_estimate: int  # Estimated recovery time in minutes


class NotificationBusinessException(Exception):
    """
    Base exception class for all notification business errors.
    
    This class provides comprehensive error handling with business context,
    impact assessment, and recovery guidance for enterprise operations.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.TECHNICAL,
        context: Optional[ErrorContext] = None,
        business_impact: Optional[BusinessImpact] = None,
        recoverable: bool = True,
        recovery_actions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or self._create_default_context()
        self.business_impact = business_impact
        self.recoverable = recoverable
        self.recovery_actions = recovery_actions or []
        self.occurred_at = datetime.utcnow()
    
    def _create_default_context(self) -> ErrorContext:
        """
Create default error context."""
        return ErrorContext(
            error_id=f"ERR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.utcnow(),
            stack_trace=traceback.format_exc()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging and monitoring."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "occurred_at": self.occurred_at.isoformat(),
            "context": {
                "error_id": self.context.error_id,
                "timestamp": self.context.timestamp.isoformat(),
                "user_id": self.context.user_id,
                "creator_type": self.context.creator_type,
                "notification_id": self.context.notification_id,
                "workflow_id": self.context.workflow_id,
                "business_context": self.context.business_context,
                "technical_context": self.context.technical_context,
                "environment": self.context.environment,
                "session_id": self.context.session_id
            },
            "business_impact": {
                "revenue_impact": self.business_impact.revenue_impact if self.business_impact else 0,
                "user_affected_count": self.business_impact.user_affected_count if self.business_impact else 0,
                "service_disruption": self.business_impact.service_disruption if self.business_impact else False,
                "data_integrity_risk": self.business_impact.data_integrity_risk if self.business_impact else False,
                "compliance_risk": self.business_impact.compliance_risk if self.business_impact else False,
                "reputation_impact": self.business_impact.reputation_impact if self.business_impact else "none",
                "recovery_time_estimate": self.business_impact.recovery_time_estimate if self.business_impact else 0
            },
            "recoverable": self.recoverable,
            "recovery_actions": self.recovery_actions,
            "stack_trace": self.context.stack_trace
        }
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly error message."""
        return self.message
    
    def get_technical_details(self) -> Dict[str, Any]:
        """
Get technical details for debugging."""
        return {
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context.technical_context,
            "stack_trace": self.context.stack_trace
        }


# Validation Exceptions

class NotificationValidationError(NotificationBusinessException):
    """Exception raised for notification validation errors."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Any = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="NOTIFICATION_VALIDATION_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule
    
    def get_user_friendly_message(self) -> str:
        if self.field_name:
            return f"Invalid {self.field_name}: {self.message}"
        return f"Validation Error: {self.message}"


class InvalidNotificationTypeError(NotificationValidationError):
    """Exception raised for invalid notification types."""
    
    def __init__(self, notification_type: str, valid_types: List[str], **kwargs):
        message = f"Invalid notification type '{notification_type}'. Valid types are: {', '.join(valid_types)}"
        super().__init__(
            message=message,
            field_name="notification_type",
            field_value=notification_type,
            validation_rule="notification_type_enum",
            **kwargs
        )
        self.notification_type = notification_type
        self.valid_types = valid_types


class InvalidRecipientError(NotificationValidationError):
    """Exception raised for invalid recipients."""
    
    def __init__(self, recipient: str, reason: str, **kwargs):
        message = f"Invalid recipient '{recipient}': {reason}"
        super().__init__(
            message=message,
            field_name="recipient",
            field_value=recipient,
            validation_rule="recipient_validation",
            **kwargs
        )
        self.recipient = recipient
        self.reason = reason


class InvalidPriorityError(NotificationValidationError):
    """Exception raised for invalid priority values."""
    
    def __init__(self, priority: str, valid_priorities: List[str], **kwargs):
        message = f"Invalid priority '{priority}'. Valid priorities are: {', '.join(valid_priorities)}"
        super().__init__(
            message=message,
            field_name="priority",
            field_value=priority,
            validation_rule="priority_enum",
            **kwargs
        )
        self.priority = priority
        self.valid_priorities = valid_priorities


# Configuration Exceptions

class NotificationConfigurationError(NotificationBusinessException):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="NOTIFICATION_CONFIGURATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )
        self.config_key = config_key


class MissingConfigurationError(NotificationConfigurationError):
    """Exception raised for missing configuration values."""
    
    def __init__(self, config_key: str, **kwargs):
        message = f"Missing required configuration: {config_key}"
        super().__init__(
            message=message,
            config_key=config_key,
            error_code="MISSING_CONFIGURATION_ERROR",
            **kwargs
        )


class InvalidConfigurationError(NotificationConfigurationError):
    """Exception raised for invalid configuration values."""
    
    def __init__(self, config_key: str, config_value: Any, reason: str, **kwargs):
        message = f"Invalid configuration '{config_key}' = '{config_value}': {reason}"
        super().__init__(
            message=message,
            config_key=config_key,
            error_code="INVALID_CONFIGURATION_ERROR",
            **kwargs
        )
        self.config_value = config_value
        self.reason = reason


# Business Rule Exceptions

class BusinessRuleViolationError(NotificationBusinessException):
    """Exception raised for business rule violations."""
    
    def __init__(
        self,
        message: str,
        rule_name: str,
        rule_description: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_RULE,
            **kwargs
        )
        self.rule_name = rule_name
        self.rule_description = rule_description


class RateLimitExceededError(BusinessRuleViolationError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(
        self,
        limit: int,
        current_count: int,
        window: str,
        user_id: Optional[str] = None,
        **kwargs
    ):
        message = f"Rate limit exceeded: {current_count}/{limit} in {window}"
        super().__init__(
            message=message,
            rule_name="rate_limit",
            rule_description=f"Maximum {limit} notifications per {window}",
            error_code="RATE_LIMIT_EXCEEDED_ERROR",
            **kwargs
        )
        self.limit = limit
        self.current_count = current_count
        self.window = window
        self.user_id = user_id


class QuotaExceededError(BusinessRuleViolationError):
    """Exception raised when quotas are exceeded."""
    
    def __init__(
        self,
        quota_type: str,
        quota_limit: int,
        current_usage: int,
        **kwargs
    ):
        message = f"Quota exceeded for {quota_type}: {current_usage}/{quota_limit}"
        super().__init__(
            message=message,
            rule_name=f"{quota_type}_quota",
            rule_description=f"Maximum {quota_limit} {quota_type} allowed",
            error_code="QUOTA_EXCEEDED_ERROR",
            **kwargs
        )
        self.quota_type = quota_type
        self.quota_limit = quota_limit
        self.current_usage = current_usage


# Technical Exceptions

class NotificationDeliveryError(NotificationBusinessException):
    """Exception raised for delivery-related errors."""
    
    def __init__(
        self,
        message: str,
        channel: str,
        notification_id: Optional[str] = None,
        provider_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="NOTIFICATION_DELIVERY_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.TECHNICAL,
            **kwargs
        )
        self.channel = channel
        self.notification_id = notification_id
        self.provider_error = provider_error


class ChannelUnavailableError(NotificationDeliveryError):
    """Exception raised when a delivery channel is unavailable."""
    
    def __init__(self, channel: str, reason: str, **kwargs):
        message = f"Channel '{channel}' is unavailable: {reason}"
        super().__init__(
            message=message,
            channel=channel,
            error_code="CHANNEL_UNAVAILABLE_ERROR",
            **kwargs
        )
        self.reason = reason


class ProviderError(NotificationDeliveryError):
    """Exception raised for third-party provider errors."""
    
    def __init__(
        self,
        provider: str,
        channel: str,
        provider_error_code: Optional[str] = None,
        provider_message: Optional[str] = None,
        **kwargs
    ):
        message = f"Provider '{provider}' error for channel '{channel}'"
        if provider_message:
            message += f": {provider_message}"
        
        super().__init__(
            message=message,
            channel=channel,
            provider_error=provider_message,
            error_code="PROVIDER_ERROR",
            **kwargs
        )
        self.provider = provider
        self.provider_error_code = provider_error_code


# Processing Exceptions

class NotificationProcessingError(NotificationBusinessException):
    """Exception raised for processing-related errors."""
    
    def __init__(
        self,
        message: str,
        processing_stage: Optional[str] = None,
        notification_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="NOTIFICATION_PROCESSING_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TECHNICAL,
            **kwargs
        )
        self.processing_stage = processing_stage
        self.notification_data = notification_data


class TemplateProcessingError(NotificationProcessingError):
    """Exception raised for template processing errors."""
    
    def __init__(
        self,
        template_name: str,
        template_error: str,
        template_variables: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Template processing error for '{template_name}': {template_error}"
        super().__init__(
            message=message,
            processing_stage="template_processing",
            error_code="TEMPLATE_PROCESSING_ERROR",
            **kwargs
        )
        self.template_name = template_name
        self.template_error = template_error
        self.template_variables = template_variables


class PersonalizationError(NotificationProcessingError):
    """Exception raised for personalization errors."""
    
    def __init__(
        self,
        personalization_type: str,
        reason: str,
        user_profile: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Personalization error for {personalization_type}: {reason}"
        super().__init__(
            message=message,
            processing_stage="personalization",
            error_code="PERSONALIZATION_ERROR",
            **kwargs
        )
        self.personalization_type = personalization_type
        self.reason = reason
        self.user_profile = user_profile


# Workflow Exceptions

class WorkflowExecutionError(NotificationBusinessException):
    """Exception raised for workflow execution errors."""
    
    def __init__(
        self,
        message: str,
        workflow_id: str,
        step_id: Optional[str] = None,
        step_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="WORKFLOW_EXECUTION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_RULE,
            **kwargs
        )
        self.workflow_id = workflow_id
        self.step_id = step_id
        self.step_error = step_error


class WorkflowTimeoutError(WorkflowExecutionError):
    """Exception raised when workflow execution times out."""
    
    def __init__(
        self,
        workflow_id: str,
        timeout_seconds: int,
        elapsed_seconds: int,
        **kwargs
    ):
        message = f"Workflow '{workflow_id}' timed out after {elapsed_seconds}s (limit: {timeout_seconds}s)"
        super().__init__(
            message=message,
            workflow_id=workflow_id,
            error_code="WORKFLOW_TIMEOUT_ERROR",
            **kwargs
        )
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds


class WorkflowStepError(WorkflowExecutionError):
    """Exception raised for workflow step errors."""
    
    def __init__(
        self,
        workflow_id: str,
        step_id: str,
        step_name: str,
        step_error: str,
        **kwargs
    ):
        message = f"Step '{step_name}' failed in workflow '{workflow_id}': {step_error}"
        super().__init__(
            message=message,
            workflow_id=workflow_id,
            step_id=step_id,
            step_error=step_error,
            error_code="WORKFLOW_STEP_ERROR",
            **kwargs
        )
        self.step_name = step_name


# Security Exceptions

class SecurityViolationError(NotificationBusinessException):
    """Exception raised for security violations."""
    
    def __init__(
        self,
        message: str,
        security_rule: str,
        violation_details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="SECURITY_VIOLATION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            recoverable=False,
            **kwargs
        )
        self.security_rule = security_rule
        self.violation_details = violation_details or {}


class UnauthorizedAccessError(SecurityViolationError):
    """Exception raised for unauthorized access attempts."""
    
    def __init__(
        self,
        resource: str,
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        message = f"Unauthorized access to resource '{resource}'"
        if required_permission:
            message += f" (requires permission: {required_permission})"
        
        super().__init__(
            message=message,
            security_rule="access_control",
            violation_details={
                "resource": resource,
                "user_id": user_id,
                "required_permission": required_permission
            },
            error_code="UNAUTHORIZED_ACCESS_ERROR",
            **kwargs
        )
        self.resource = resource
        self.user_id = user_id
        self.required_permission = required_permission


class DataIntegrityError(NotificationBusinessException):
    """Exception raised for data integrity violations."""
    
    def __init__(
        self,
        message: str,
        data_type: str,
        integrity_check: str,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="DATA_INTEGRITY_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.DATA_ERROR,
            **kwargs
        )
        self.data_type = data_type
        self.integrity_check = integrity_check


# Performance Exceptions

class PerformanceThresholdError(NotificationBusinessException):
    """Exception raised when performance thresholds are exceeded."""
    
    def __init__(
        self,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        threshold_type: str = "max",
        **kwargs
    ):
        message = f"Performance threshold exceeded for {metric_name}: {current_value} > {threshold_value}"
        super().__init__(
            message=message,
            error_code="PERFORMANCE_THRESHOLD_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            **kwargs
        )
        self.metric_name = metric_name
        self.current_value = current_value
        self.threshold_value = threshold_value
        self.threshold_type = threshold_type


class ResourceExhaustedError(PerformanceThresholdError):
    """Exception raised when system resources are exhausted."""
    
    def __init__(
        self,
        resource_type: str,
        current_usage: float,
        max_capacity: float,
        **kwargs
    ):
        message = f"Resource '{resource_type}' exhausted: {current_usage}/{max_capacity}"
        super().__init__(
            metric_name=resource_type,
            current_value=current_usage,
            threshold_value=max_capacity,
            threshold_type="capacity",
            error_code="RESOURCE_EXHAUSTED_ERROR",
            **kwargs
        )
        self.resource_type = resource_type


# Integration Exceptions

class ExternalServiceError(NotificationBusinessException):
    """Exception raised for external service errors."""
    
    def __init__(
        self,
        service_name: str,
        error_message: str,
        service_response: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"External service '{service_name}' error: {error_message}"
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.INTEGRATION,
            **kwargs
        )
        self.service_name = service_name
        self.service_response = service_response or {}


class DatabaseConnectionError(NotificationBusinessException):
    """Exception raised for database connection errors."""
    
    def __init__(
        self,
        database_name: str,
        connection_details: str,
        **kwargs
    ):
        message = f"Database connection error for '{database_name}': {connection_details}"
        super().__init__(
            message=message,
            error_code="DATABASE_CONNECTION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.TECHNICAL,
            **kwargs
        )
        self.database_name = database_name
        self.connection_details = connection_details


# Factory Functions for Common Errors

def create_validation_error(
    field_name: str,
    field_value: Any,
    rule: str,
    user_message: Optional[str] = None
) -> NotificationValidationError:
    """Create a standardized validation error."""
    message = user_message or f"Validation failed for field '{field_name}'"
    return NotificationValidationError(
        message=message,
        field_name=field_name,
        field_value=field_value,
        validation_rule=rule
    )


def create_business_rule_error(
    rule_name: str,
    violation_details: str,
    severity: ErrorSeverity = ErrorSeverity.HIGH
) -> BusinessRuleViolationError:
    """Create a standardized business rule violation error."""
    return BusinessRuleViolationError(
        message=f"Business rule violation: {violation_details}",
        rule_name=rule_name,
        severity=severity
    )


def create_processing_error(
    stage: str,
    error_details: str,
    notification_id: Optional[str] = None
) -> NotificationProcessingError:
    """Create a standardized processing error."""
    context = ErrorContext(
        error_id=f"PROC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
        timestamp=datetime.utcnow(),
        notification_id=notification_id,
        technical_context={"processing_stage": stage}
    )
    
    return NotificationProcessingError(
        message=f"Processing error in stage '{stage}': {error_details}",
        processing_stage=stage,
        context=context
    )


def create_delivery_error(
    channel: str,
    provider_error: str,
    notification_id: Optional[str] = None
) -> NotificationDeliveryError:
    """Create a standardized delivery error."""
    return NotificationDeliveryError(
        message=f"Delivery failed for channel '{channel}': {provider_error}",
        channel=channel,
        notification_id=notification_id,
        provider_error=provider_error
    )


# Error Handler Registry

class ErrorHandlerRegistry:
    """Registry for error handlers and recovery strategies."""
    
    def __init__(self):
        self._handlers = {}
        self._recovery_strategies = {}
    
    def register_handler(
        self,
        error_type: type,
        handler_func,
        priority: int = 100
    ):
        """
Register an error handler for a specific error type."""
        if error_type not in self._handlers:
            self._handlers[error_type] = []
        
        self._handlers[error_type].append({
            "handler": handler_func,
            "priority": priority
        })
        
        # Sort by priority (higher priority first)
        self._handlers[error_type].sort(key=lambda x: x["priority"], reverse=True)
    
    def register_recovery_strategy(
        self,
        error_code: str,
        strategy_func,
        conditions: Optional[Dict[str, Any]] = None
    ):
        """Register a recovery strategy for an error code."""
        self._recovery_strategies[error_code] = {
            "strategy": strategy_func,
            "conditions": conditions or {}
        }
    
    def handle_error(self, error: NotificationBusinessException) -> bool:
        """Handle an error using registered handlers."""
        error_type = type(error)
        
        if error_type in self._handlers:
            for handler_info in self._handlers[error_type]:
                try:
                    result = handler_info["handler"](error)
                    if result:
                        return True
                except Exception:
                    # Handler failed, try next one
                    continue
        
        return False
    
    def attempt_recovery(
        self,
        error: NotificationBusinessException,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Attempt to recover from an error using registered strategies."""
        if error.error_code in self._recovery_strategies:
            strategy_info = self._recovery_strategies[error.error_code]
            
            # Check if conditions are met
            conditions = strategy_info["conditions"]
            if conditions and context:
                for key, value in conditions.items():
                    if context.get(key) != value:
                        return False
            
            try:
                return strategy_info["strategy"](error, context)
            except Exception:
                return False
        
        return False


# Global error handler registry
error_handler_registry = ErrorHandlerRegistry()
