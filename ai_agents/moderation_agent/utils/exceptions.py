"""Moderation Agent Exceptions - Custom Exception Classes

Enterprise-grade exception handling for the ultra-advanced content moderation system.
Provides detailed error information and proper error categorization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class ModerationAgentException(Exception):
    """    Base exception class for Moderation Agent
    
    All moderation-specific exceptions inherit from this class.
    Provides structured error information and logging.
    """    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None, 
                 details: str = None):
        self.message = message
        self.error_code = error_code or "MODERATION_ERROR"
        self.context = context or {}
        self.details = details
        
        super().__init__(self.message)
        
        # Log the exception
        logger.error(f"ModerationAgentException: {self.error_code} - {self.message}", 
                    extra={'context': self.context, 'details': self.details})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""        return {
            'error': True,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'details': self.details
        }

class ModelLoadingError(ModerationAgentException):
    """    Exception raised when AI models fail to load
    
    This can occur due to missing model files, insufficient memory,
    or incompatible model versions.
    """    
    def __init__(self, model_name: str, reason: str, context: Dict[str, Any] = None):
        message = f"Failed to load model '{model_name}': {reason}"
        super().__init__(
            message=message,
            error_code="MODEL_LOADING_ERROR",
            context=context or {'model_name': model_name, 'reason': reason}
        )

class ContentProcessingError(ModerationAgentException):
    """    Exception raised during content processing
    
    Covers errors in text analysis, image processing, audio analysis,
    and video processing stages.
    """    
    def __init__(self, content_type: str, processing_stage: str, reason: str, 
                 content_id: str = None, context: Dict[str, Any] = None):
        message = f"Content processing failed for {content_type} at {processing_stage}: {reason}"
        error_context = {
            'content_type': content_type,
            'processing_stage': processing_stage,
            'reason': reason
        }
        if content_id:
            error_context['content_id'] = content_id
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="CONTENT_PROCESSING_ERROR",
            context=error_context
        )

class ViolationDetectionError(ModerationAgentException):
    """    Exception raised during violation detection
    
    Occurs when the violation detection process fails due to model errors,
    invalid input, or processing timeouts.
    """    
    def __init__(self, violation_type: str, detection_model: str, reason: str,
                 confidence_threshold: float = None, context: Dict[str, Any] = None):
        message = f"Violation detection failed for {violation_type} using {detection_model}: {reason}"
        error_context = {
            'violation_type': violation_type,
            'detection_model': detection_model,
            'reason': reason
        }
        if confidence_threshold is not None:
            error_context['confidence_threshold'] = confidence_threshold
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="VIOLATION_DETECTION_ERROR",
            context=error_context
        )

class ConfigurationError(ModerationAgentException):
    """    Exception raised for configuration-related errors
    
    Covers missing required configuration keys, invalid configuration values,
    and configuration validation failures.
    """    
    def __init__(self, config_key: str, reason: str, valid_values: List[Any] = None,
                 current_value: Any = None, context: Dict[str, Any] = None):
        message = f"Configuration error for '{config_key}': {reason}"
        error_context = {
            'config_key': config_key,
            'reason': reason
        }
        if valid_values is not None:
            error_context['valid_values'] = valid_values
        if current_value is not None:
            error_context['current_value'] = current_value
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=error_context
        )

class UnsupportedContentTypeError(ModerationAgentException):
    """    Exception raised for unsupported content types
    
    Occurs when trying to process content in a format that is not
    supported by the moderation agent.
    """    
    def __init__(self, content_type: str, supported_types: List[str] = None,
                 context: Dict[str, Any] = None):
        message = f"Unsupported content type: {content_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
        
        error_context = {'content_type': content_type}
        if supported_types:
            error_context['supported_types'] = supported_types
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_CONTENT_TYPE",
            context=error_context
        )

class ThresholdValidationError(ModerationAgentException):
    """    Exception raised for threshold validation errors
    
    Occurs when moderation thresholds are set to invalid values
    or when threshold logic conflicts arise.
    """    
    def __init__(self, threshold_name: str, threshold_value: float, 
                 min_value: float = None, max_value: float = None,
                 context: Dict[str, Any] = None):
        message = f"Invalid threshold value for '{threshold_name}': {threshold_value}"
        if min_value is not None and max_value is not None:
            message += f" (valid range: {min_value} - {max_value})"
        
        error_context = {
            'threshold_name': threshold_name,
            'threshold_value': threshold_value
        }
        if min_value is not None:
            error_context['min_value'] = min_value
        if max_value is not None:
            error_context['max_value'] = max_value
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="THRESHOLD_VALIDATION_ERROR",
            context=error_context
        )

class ContentTooLargeError(ModerationAgentException):
    """    Exception raised when content exceeds size limits
    
    Prevents processing of content that is too large for efficient
    or safe processing.
    """    
    def __init__(self, content_type: str, content_size: int, max_size: int,
                 size_unit: str = "bytes", context: Dict[str, Any] = None):
        message = f"Content too large: {content_size} {size_unit} exceeds limit of {max_size} {size_unit}"
        
        error_context = {
            'content_type': content_type,
            'content_size': content_size,
            'max_size': max_size,
            'size_unit': size_unit
        }
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="CONTENT_TOO_LARGE",
            context=error_context
        )

class ProcessingTimeoutError(ModerationAgentException):
    """    Exception raised when processing exceeds time limits
    
    Prevents long-running processes from blocking the system
    and ensures timely responses.
    """    
    def __init__(self, processing_stage: str, timeout_seconds: float,
                 elapsed_time: float = None, content_id: str = None,
                 context: Dict[str, Any] = None):
        message = f"Processing timeout in {processing_stage}: exceeded {timeout_seconds}s limit"
        if elapsed_time:
            message += f" (elapsed: {elapsed_time:.2f}s)"
        
        error_context = {
            'processing_stage': processing_stage,
            'timeout_seconds': timeout_seconds
        }
        if elapsed_time is not None:
            error_context['elapsed_time'] = elapsed_time
        if content_id:
            error_context['content_id'] = content_id
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="PROCESSING_TIMEOUT",
            context=error_context
        )

class InsufficientResourcesError(ModerationAgentException):
    """    Exception raised when system resources are insufficient
    
    Covers memory, disk space, GPU availability, and other
    resource-related constraints.
    """    
    def __init__(self, resource_type: str, required: str, available: str = None,
                 context: Dict[str, Any] = None):
        message = f"Insufficient {resource_type}: requires {required}"
        if available:
            message += f", available: {available}"
        
        error_context = {
            'resource_type': resource_type,
            'required': required
        }
        if available:
            error_context['available'] = available
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_RESOURCES",
            context=error_context
        )

class LiveStreamError(ModerationAgentException):
    """    Exception raised during live stream moderation
    
    Covers connection issues, streaming protocol errors,
    and real-time processing failures.
    """    
    def __init__(self, stream_id: str, error_type: str, reason: str,
                 stream_url: str = None, context: Dict[str, Any] = None):
        message = f"Live stream error ({error_type}) for stream {stream_id}: {reason}"
        
        error_context = {
            'stream_id': stream_id,
            'error_type': error_type,
            'reason': reason
        }
        if stream_url:
            error_context['stream_url'] = stream_url
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="LIVE_STREAM_ERROR",
            context=error_context
        )

class ComplianceViolationError(ModerationAgentException):
    """    Exception raised for compliance framework violations
    
    Covers GDPR, COPPA, and other regulatory compliance issues
    that prevent content processing.
    """    
    def __init__(self, compliance_framework: str, violation_type: str, 
                 requirement: str, context: Dict[str, Any] = None):
        message = f"Compliance violation ({compliance_framework}): {violation_type} - {requirement}"
        
        error_context = {
            'compliance_framework': compliance_framework,
            'violation_type': violation_type,
            'requirement': requirement
        }
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="COMPLIANCE_VIOLATION",
            context=error_context
        )

class ModelInferenceError(ModerationAgentException):
    """    Exception raised during model inference
    
    Covers prediction failures, invalid model outputs,
    and inference pipeline errors.
    """    
    def __init__(self, model_name: str, inference_stage: str, reason: str,
                 input_shape: tuple = None, context: Dict[str, Any] = None):
        message = f"Model inference failed for {model_name} at {inference_stage}: {reason}"
        
        error_context = {
            'model_name': model_name,
            'inference_stage': inference_stage,
            'reason': reason
        }
        if input_shape:
            error_context['input_shape'] = input_shape
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="MODEL_INFERENCE_ERROR",
            context=error_context
        )

class HumanReviewRequiredError(ModerationAgentException):
    """    Exception raised when human review is required
    
    Not technically an error, but an exception to interrupt
    automated processing when human intervention is needed.
    """    
    def __init__(self, content_id: str, violation_types: List[str], 
                 confidence_scores: List[float], severity_level: str,
                 context: Dict[str, Any] = None):
        message = f"Human review required for content {content_id} due to {severity_level} severity violations"
        
        error_context = {
            'content_id': content_id,
            'violation_types': violation_types,
            'confidence_scores': confidence_scores,
            'severity_level': severity_level,
            'review_required': True
        }
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="HUMAN_REVIEW_REQUIRED",
            context=error_context
        )

class DataPrivacyError(ModerationAgentException):
    """    Exception raised for data privacy violations
    
    Covers unauthorized access, data retention violations,
    and privacy policy breaches.
    """    
    def __init__(self, privacy_type: str, violation_description: str,
                 user_id: str = None, data_category: str = None,
                 context: Dict[str, Any] = None):
        message = f"Data privacy violation ({privacy_type}): {violation_description}"
        
        error_context = {
            'privacy_type': privacy_type,
            'violation_description': violation_description
        }
        if user_id:
            error_context['user_id'] = user_id
        if data_category:
            error_context['data_category'] = data_category
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="DATA_PRIVACY_ERROR",
            context=error_context
        )

class APIQuotaExceededError(ModerationAgentException):
    """    Exception raised when API quotas are exceeded
    
    Covers rate limiting, usage quotas, and service limitations
    from external APIs or internal resource limits.
    """    
    def __init__(self, api_name: str, quota_type: str, limit: int,
                 current_usage: int = None, reset_time: str = None,
                 context: Dict[str, Any] = None):
        message = f"API quota exceeded for {api_name}: {quota_type} limit of {limit} reached"
        if current_usage is not None:
            message += f" (current usage: {current_usage})"
        
        error_context = {
            'api_name': api_name,
            'quota_type': quota_type,
            'limit': limit
        }
        if current_usage is not None:
            error_context['current_usage'] = current_usage
        if reset_time:
            error_context['reset_time'] = reset_time
        if context:
            error_context.update(context)
        
        super().__init__(
            message=message,
            error_code="API_QUOTA_EXCEEDED",
            context=error_context
        )

# Exception factory for creating appropriate exceptions
class ModerationExceptionFactory:
    """    Factory class for creating appropriate moderation exceptions
    
    Provides a centralized way to create exceptions with consistent
    formatting and proper error categorization.
    """    
    @staticmethod
    def create_model_error(model_name: str, error_type: str, details: str,
                          context: Dict[str, Any] = None) -> ModerationAgentException:
        """Create model-related exception"""        if error_type == "loading":
            return ModelLoadingError(model_name, details, context)
        elif error_type == "inference":
            return ModelInferenceError(model_name, "prediction", details, context=context)
        else:
            return ModerationAgentException(
                message=f"Model error in {model_name}: {details}",
                error_code=f"MODEL_{error_type.upper()}_ERROR",
                context=context
            )
    
    @staticmethod
    def create_content_error(content_type: str, stage: str, reason: str,
                           content_id: str = None, context: Dict[str, Any] = None) -> ContentProcessingError:
        """Create content processing exception"""        return ContentProcessingError(content_type, stage, reason, content_id, context)
    
    @staticmethod
    def create_configuration_error(config_key: str, issue: str,
                                 context: Dict[str, Any] = None) -> ConfigurationError:
        """Create configuration exception"""        return ConfigurationError(config_key, issue, context=context)
    
    @staticmethod
    def create_resource_error(resource: str, requirement: str, 
                            availability: str = None, context: Dict[str, Any] = None) -> InsufficientResourcesError:
        """Create resource limitation exception"""        return InsufficientResourcesError(resource, requirement, availability, context)

# Error handler for graceful exception handling
def handle_moderation_exception(exception: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """    Handle moderation exceptions gracefully
    
    Args:
        exception: The exception to handle
        context: Additional context information
        
    Returns:
        Dictionary representation of the error for API responses
    """    if isinstance(exception, ModerationAgentException):
        error_dict = exception.to_dict()
        if context:
            error_dict['context'].update(context)
        return error_dict
    else:
        # Handle unexpected exceptions
        logger.error(f"Unexpected exception: {type(exception).__name__}: {str(exception)}")
        return {
            'error': True,
            'error_code': 'UNEXPECTED_ERROR',
            'message': str(exception),
            'context': context or {},
            'exception_type': type(exception).__name__
        }
