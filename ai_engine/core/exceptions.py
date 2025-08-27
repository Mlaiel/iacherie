"""
Core Exceptions Module

Advanced exception hierarchy for industrial-grade AI content processing system.
Provides comprehensive error handling for multi-format content creators platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for systematic classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    PROCESSING = "processing"
    NETWORK = "network"
    STORAGE = "storage"
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"


class BaseAIException(Exception):
    """
    Base exception class for all AI Core exceptions
    
    Provides standardized error handling with:
    - Error tracking and correlation
    - Detailed context capture
    - Monitoring integration
    - Security-safe error messages
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.PROCESSING,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        retry_after: Optional[int] = None,
        correlation_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.user_message = user_message or "An error occurred during processing"
        self.retry_after = retry_after
        self.correlation_id = correlation_id
        self.timestamp = datetime.utcnow()
        self.traceback_str = traceback.format_exc()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/monitoring"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "retry_after": self.retry_after,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback_str
        }
        
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ContentGenerationError(BaseAIException):
    """Base exception for content generation pipeline errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            **kwargs
        )


class ModelConnectionError(ContentGenerationError):
    """
    Exception raised when AI model connection or loading fails
    
    Common scenarios:
    - Model server unavailable
    - GPU memory exhaustion
    - Model file corruption
    - Network connectivity issues
    """
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "model_name": model_name,
            "model_version": model_version,
            "endpoint": endpoint
        })
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.EXTERNAL_SERVICE,
            context=context,
            user_message="AI processing service temporarily unavailable",
            retry_after=30,
            **kwargs
        )


class ContentValidationError(ContentGenerationError):
    """
    Exception raised when content validation fails
    
    Handles validation of:
    - Multi-format content (audio, video, image, text)
    - Content quality standards
    - Copyright compliance
    - Platform-specific requirements
    """
    
    def __init__(
        self,
        message: str,
        validation_errors: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        field_name: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "validation_errors": validation_errors or [],
            "content_type": content_type,
            "field_name": field_name
        })
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            context=context,
            user_message="Content validation failed. Please check your input.",
            **kwargs
        )


class RateLimitError(ContentGenerationError):
    """
    Exception raised when API rate limits are exceeded
    
    Provides intelligent rate limiting for:
    - AI model inference requests
    - External API calls (Spotify, social platforms)
    - Content processing quotas
    """
    
    def __init__(
        self,
        message: str,
        limit_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit_threshold: Optional[int] = None,
        reset_time: Optional[datetime] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "limit_type": limit_type,
            "current_usage": current_usage,
            "limit_threshold": limit_threshold,
            "reset_time": reset_time.isoformat() if reset_time else None
        })
        
        retry_after = None
        if reset_time:
            retry_after = int((reset_time - datetime.utcnow()).total_seconds())
            
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            context=context,
            user_message="Processing quota exceeded. Please try again later.",
            retry_after=retry_after,
            **kwargs
        )


class ConfigurationError(ContentGenerationError):
    """
    Exception raised when system configuration is invalid
    
    Covers configuration issues for:
    - AI model settings
    - Environment variables
    - Service integrations
    - Security parameters
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "config_key": config_key,
            "expected_type": expected_type,
            "actual_value": str(actual_value) if actual_value is not None else None
        })
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            context=context,
            user_message="System configuration error. Please contact support.",
            **kwargs
        )


class QualityCheckError(ContentGenerationError):
    """
    Exception raised when content quality checks fail
    
    Enforces quality standards for:
    - Content authenticity verification
    - Brand safety compliance
    - Professional content standards
    - Platform optimization requirements
    """
    
    def __init__(
        self,
        message: str,
        quality_score: Optional[float] = None,
        minimum_threshold: Optional[float] = None,
        failed_checks: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "quality_score": quality_score,
            "minimum_threshold": minimum_threshold,
            "failed_checks": failed_checks or [],
            "content_type": content_type
        })
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            user_message="Content quality does not meet platform standards.",
            **kwargs
        )


class DistributionError(ContentGenerationError):
    """
    Exception raised when content distribution fails
    
    Handles distribution to:
    - Social media platforms
    - Music streaming services
    - Content delivery networks
    - Collaboration platforms
    """
    
    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        distribution_id: Optional[str] = None,
        failed_platforms: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "platform": platform,
            "distribution_id": distribution_id,
            "failed_platforms": failed_platforms or []
        })
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.EXTERNAL_SERVICE,
            context=context,
            user_message="Content distribution failed. Retrying automatically.",
            retry_after=60,
            **kwargs
        )


class OptimizationError(ContentGenerationError):
    """
    Exception raised when content optimization fails
    
    Covers optimization failures for:
    - SEO enhancement
    - Performance optimization
    - Format conversion
    - Quality enhancement
    """
    
    def __init__(
        self,
        message: str,
        optimization_type: Optional[str] = None,
        original_format: Optional[str] = None,
        target_format: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "optimization_type": optimization_type,
            "original_format": original_format,
            "target_format": target_format
        })
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PROCESSING,
            context=context,
            user_message="Content optimization failed. Using original version.",
            **kwargs
        )


class ProtectionError(ContentGenerationError):
    """
    Exception raised when content protection mechanisms fail
    
    Critical for:
    - Rights management
    - Fingerprinting technology
    - Copyright detection
    - Legal compliance
    """
    
    def __init__(
        self,
        message: str,
        protection_type: Optional[str] = None,
        content_id: Optional[str] = None,
        violation_detected: Optional[bool] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "protection_type": protection_type,
            "content_id": content_id,
            "violation_detected": violation_detected
        })
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            user_message="Content protection system error. Please contact support immediately.",
            **kwargs
        )


class CollaborationError(ContentGenerationError):
    """
    Exception raised when collaboration features fail
    
    Manages errors in:
    - Creator matching algorithms
    - Collaboration invitations
    - Shared project management
    - Revenue sharing calculations
    """
    
    def __init__(
        self,
        message: str,
        collaboration_id: Optional[str] = None,
        creator_ids: Optional[List[str]] = None,
        collaboration_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "collaboration_id": collaboration_id,
            "creator_ids": creator_ids or [],
            "collaboration_type": collaboration_type
        })
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            user_message="Collaboration feature temporarily unavailable.",
            **kwargs
        )


class MonetizationError(ContentGenerationError):
    """
    Exception raised when monetization processes fail
    
    Critical for:
    - Revenue calculation
    - Payment processing
    - Rights royalty distribution
    - Analytics reporting
    """
    
    def __init__(
        self,
        message: str,
        transaction_id: Optional[str] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        payment_method: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method
        })
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            user_message="Monetization error. Please contact support for assistance.",
            **kwargs
        )


class AuthenticationError(BaseAIException):
    """Exception raised for authentication failures"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            user_message="Authentication required. Please log in.",
            **kwargs
        )


class AuthorizationError(BaseAIException):
    """Exception raised for authorization failures"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHORIZATION,
            user_message="You don't have permission to perform this action.",
            **kwargs
        )


class ResourceNotFoundError(BaseAIException):
    """Raised when requested resource cannot be found"""
    
    def __init__(
        self,
        message: str = "Requested resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            user_message="Requested resource not found.",
            **kwargs
        )


# AI Model specific exceptions
class AIModelError(BaseAIException):
    """Base exception for all AI model related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PROCESSING,
            user_message="AI model operation failed.",
            **kwargs
        )


class ModelError(AIModelError):
    """General model operation error"""
    pass


class ValidationError(AIModelError):
    """Data validation error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            user_message="Input data validation failed.",
            **kwargs
        )


class ProcessingError(AIModelError):
    """Model processing error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PROCESSING,
            user_message="Processing operation failed.",
            **kwargs
        )


class TimeoutError(AIModelError):
    """Operation timeout error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            user_message="Operation timed out.",
            **kwargs
        )


class PerformanceError(AIModelError):
    """Performance monitoring and analysis error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            user_message="Performance monitoring error occurred.",
            **kwargs
        )


class MonitoringError(AIModelError):
    """Monitoring system error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            user_message="Monitoring system error occurred.",
            **kwargs
        )


class ContentProcessingError(AIModelError):
    """Content processing and analysis error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PROCESSING,
            user_message="Content processing error occurred.",
            **kwargs
        )


class BusinessMetricsError(AIModelError):
    """Business metrics collection and analysis error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Business metrics error occurred.",
            **kwargs
        )


class HealthCheckError(AIModelError):
    """Health check system error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            user_message="Health check error occurred.",
            **kwargs
        )


class AlertingError(AIModelError):
    """Real-time alerting system error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            user_message="Alerting system error occurred.",
            **kwargs
        )


class ReportingError(AIModelError):
    """Reporting and analytics error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PROCESSING,
            user_message="Reporting system error occurred.",
            **kwargs
        )


class DataProcessingError(AIModelError):
    """Data processing and transformation error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PROCESSING,
            user_message="Data processing error occurred.",
            **kwargs
        )


class MetricsError(AIModelError):
    """Metrics collection and processing error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            user_message="Metrics system error occurred.",
            **kwargs
        )


class ModelNotFoundError(AIModelError):
    """Model not found error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            user_message="AI model not found.",
            **kwargs
        )


class ModelLoadError(AIModelError):
    """Model loading error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIGURATION,
            user_message="Failed to load AI model.",
            **kwargs
        )


class ModelInitializationError(AIModelError):
    """Model initialization error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIGURATION,
            user_message="Failed to initialize AI model.",
            **kwargs
        )


class AudioProcessingError(ProcessingError):
    """Audio-specific processing error"""
    pass


class VideoProcessingError(ProcessingError):
    """Video-specific processing error"""
    pass


class ImageProcessingError(ProcessingError):
    """Image-specific processing error"""
    pass


class TextProcessingError(ProcessingError):
    """Text-specific processing error"""
    pass


class MonitoringError(BaseAIException):
    """Monitoring system error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            user_message="System monitoring encountered an error.",
            **kwargs
        )


class AnomalyDetectionError(BaseAIException):
    """Anomaly detection system error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            user_message="Anomaly detection system encountered an error.",
            **kwargs
        )


class PersonalizationError(BaseAIException):
    """Personalization system error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PROCESSING,
            user_message="Personalization system encountered an error.",
            **kwargs
        )


class ModelConnectionError(BaseAIException):
    """Model connection error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.NETWORK,
            user_message="Model connection failed.",
            **kwargs
        )


# Exception registry for systematic error handling
EXCEPTION_REGISTRY = {
    "base": BaseAIException,
    "content_generation": ContentGenerationError,
    "model_connection": ModelConnectionError,
    "content_validation": ContentValidationError,
    "rate_limit": RateLimitError,
    "configuration": ConfigurationError,
    "quality_check": QualityCheckError,
    "distribution": DistributionError,
    "optimization": OptimizationError,
    "protection": ProtectionError,
    "collaboration": CollaborationError,
    "monetization": MonetizationError,
    "authentication": AuthenticationError,
    "authorization": AuthorizationError,
    "resource_not_found": ResourceNotFoundError,
    # AI Model exceptions
    "ai_model_error": AIModelError,
    "model_error": ModelError,
    "validation_error": ValidationError,
    "processing_error": ProcessingError,
    "timeout_error": TimeoutError,
    "model_not_found": ModelNotFoundError,
    "model_load_error": ModelLoadError,
    "model_initialization_error": ModelInitializationError,
    "audio_processing_error": AudioProcessingError,
    "video_processing_error": VideoProcessingError,
    "image_processing_error": ImageProcessingError,
    "text_processing_error": TextProcessingError,
    "monitoring_error": MonitoringError,
    "anomaly_detection_error": AnomalyDetectionError,
    "personalization_error": PersonalizationError,
    "model_connection_error": ModelConnectionError
}


class ComponentError(AIModelError):
    """Component-level error"""
    pass


class AIOrchestrationError(BaseAIException):
    """AI orchestration system error"""
    
    def __init__(self, message: str, component: str = None, context: Dict = None):
        super().__init__(
            message=message,
            error_code="AI_ORCHESTRATION_ERROR",
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.HIGH
        )
        self.component = component
        self.context = context or {}


def get_exception_by_code(error_code: str) -> type:
    """
    Get exception class by error code
    
    Args:
        error_code: The error code to look up
        
    Returns:
        Exception class or BaseAIException if not found
    """
    return EXCEPTION_REGISTRY.get(error_code.lower(), BaseAIException)
