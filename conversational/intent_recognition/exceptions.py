"""Exception Classes for Intent Recognition System

Custom exception hierarchy for intent recognition components with detailed
error handling, recovery suggestions, and logging integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime


class IntentRecognitionError(Exception):
    """
    Base exception class for intent recognition system
    
    Provides structured error handling with context information,
    recovery suggestions, and integration with monitoring systems.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.suggestions = suggestions or []
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        
        # Log error automatically
        self._log_error()
    
    def _log_error(self) -> None:
        """
Log error with appropriate level based on severity"""
        logger = logging.getLogger(__name__)
        
        error_details = {
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'recoverable': self.recoverable,
            'timestamp': self.timestamp.isoformat()
        }
        
        if self.recoverable:
            logger.warning(f"Recoverable error: {error_details}")
        else:
            logger.error(f"Non-recoverable error: {error_details}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'suggestions': self.suggestions,
            'recoverable': self.recoverable,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        """
Human-readable error message"""
        base_message = f"[{self.error_code}] {self.message}"
        
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            base_message += f" (Context: {context_str})"
        
        if self.suggestions:
            suggestions_str = "; ".join(self.suggestions)
            base_message += f" | Suggestions: {suggestions_str}"
        
        return base_message


class ClassificationError(IntentRecognitionError):
    """
    Exception raised during intent classification process
    
    Covers errors in model inference, preprocessing, postprocessing,
    and result formatting.
    """
    
    def __init__(
        self,
        message: str,
        input_text: Optional[str] = None,
        model_name: Optional[str] = None,
        processing_stage: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'input_text': input_text[:100] if input_text else None,  # Truncate for logging
            'model_name': model_name,
            'processing_stage': processing_stage
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check input text format and encoding",
                "Verify model is properly loaded",
                "Try reducing input text length",
                "Use fallback classification if available"
            ]
        
        super().__init__(
            message=message,
            error_code="CLASSIFICATION_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class ModelLoadError(IntentRecognitionError):
    """
    Exception raised when model loading fails
    
    Covers errors in model initialization, weight loading,
    tokenizer setup, and model validation.
    """
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'model_name': model_name,
            'model_path': model_path
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check model file exists and is accessible",
                "Verify model format compatibility",
                "Check available memory and disk space",
                "Try downloading model again",
                "Use alternative model if available"
            ]
        
        super().__init__(
            message=message,
            error_code="MODEL_LOAD_ERROR",
            context=context,
            suggestions=suggestions,
            recoverable=False,  # Model load errors typically require intervention
            **kwargs
        )


class ConfigurationError(IntentRecognitionError):
    """
    Exception raised for configuration-related issues
    
    Covers invalid settings, missing required parameters,
    environment setup issues, and validation failures.
    """
    
    def __init__(
        self,
        message: str,
        config_section: Optional[str] = None,
        invalid_keys: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'config_section': config_section,
            'invalid_keys': invalid_keys
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check configuration file syntax",
                "Verify all required parameters are set",
                "Check environment variable values",
                "Review configuration documentation",
                "Use default configuration as starting point"
            ]
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=context,
            suggestions=suggestions,
            recoverable=False,  # Config errors typically require correction
            **kwargs
        )


class ValidationError(IntentRecognitionError):
    """
    Exception raised for input validation failures
    
    Covers text format validation, length restrictions,
    language detection issues, and content filtering.
    """
    
    def __init__(
        self,
        message: str,
        validation_type: Optional[str] = None,
        input_value: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'validation_type': validation_type,
            'input_value': str(input_value)[:50] if input_value else None,  # Truncate for security
            'constraints': constraints
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check input text format and encoding",
                "Verify text length is within limits",
                "Remove or escape special characters",
                "Use supported language text",
                "Try shorter input text"
            ]
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class ProcessingTimeoutError(IntentRecognitionError):
    """
    Exception raised when processing exceeds timeout limits
    
    Covers classification timeouts, queue timeouts,
    and batch processing timeouts.
    """
    
    def __init__(
        self,
        message: str,
        timeout_ms: Optional[int] = None,
        actual_time_ms: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'timeout_ms': timeout_ms,
            'actual_time_ms': actual_time_ms,
            'operation': operation
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Increase timeout limit for complex requests",
                "Use batch processing for multiple items",
                "Reduce input text complexity",
                "Check system resource availability",
                "Use async processing for long operations"
            ]
        
        super().__init__(
            message=message,
            error_code="PROCESSING_TIMEOUT_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class CacheError(IntentRecognitionError):
    """
    Exception raised for caching system issues
    
    Covers cache store/retrieve failures, cache corruption,
    and cache eviction problems.
    """
    
    def __init__(
        self,
        message: str,
        cache_operation: Optional[str] = None,
        cache_key: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'cache_operation': cache_operation,
            'cache_key': cache_key
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check cache service availability",
                "Verify cache storage capacity",
                "Clear cache if corrupted",
                "Use fallback processing without cache",
                "Check cache configuration settings"
            ]
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class RateLimitError(IntentRecognitionError):
    """
    Exception raised when rate limits are exceeded
    
    Covers per-user limits, per-IP limits, global limits,
    and burst limit violations.
    """
    
    def __init__(
        self,
        message: str,
        limit_type: Optional[str] = None,
        current_rate: Optional[float] = None,
        limit_value: Optional[float] = None,
        reset_time: Optional[datetime] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'limit_type': limit_type,
            'current_rate': current_rate,
            'limit_value': limit_value,
            'reset_time': reset_time.isoformat() if reset_time else None
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                f"Wait until {reset_time.strftime('%H:%M:%S')} before retrying" if reset_time else "Wait before retrying",
                "Use batch processing to reduce request count",
                "Implement exponential backoff for retries",
                "Contact support for rate limit increase",
                "Cache results to reduce duplicate requests"
            ]
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class ResourceError(IntentRecognitionError):
    """
    Exception raised for resource-related issues
    
    Covers memory limitations, disk space issues,
    GPU availability, and system resource constraints.
    """
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        current_usage: Optional[float] = None,
        available: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'resource_type': resource_type,
            'current_usage': current_usage,
            'available': available
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Free up system resources",
                "Use lighter model variants",
                "Process data in smaller batches",
                "Scale up infrastructure resources",
                "Implement resource monitoring and alerts"
            ]
        
        super().__init__(
            message=message,
            error_code="RESOURCE_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


class IntegrationError(IntentRecognitionError):
    """
    Exception raised for external integration failures
    
    Covers API connection issues, authentication failures,
    service unavailability, and data format mismatches.
    """
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'service_name': service_name,
            'endpoint': endpoint,
            'status_code': status_code
        })
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check service availability and status",
                "Verify authentication credentials",
                "Review API endpoint configuration",
                "Implement retry logic with backoff",
                "Use fallback service if available"
            ]
        
        super().__init__(
            message=message,
            error_code="INTEGRATION_ERROR",
            context=context,
            suggestions=suggestions,
            **kwargs
        )


# Exception hierarchy mapping for error handling
EXCEPTION_HIERARCHY = {
    'IntentRecognitionError': IntentRecognitionError,
    'ClassificationError': ClassificationError,
    'ModelLoadError': ModelLoadError,
    'ConfigurationError': ConfigurationError,
    'ValidationError': ValidationError,
    'ProcessingTimeoutError': ProcessingTimeoutError,
    'CacheError': CacheError,
    'RateLimitError': RateLimitError,
    'ResourceError': ResourceError,
    'IntegrationError': IntegrationError
}


def create_error_response(
    exception: IntentRecognitionError,
        try:
            logger.info(f"Executing create_error_response")
            
            # Implementation for create_error_response
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"create_error_response completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"create_error_response failed: {e}")
            raise
def handle_exception(
    func_name: str,
    exception: Exception,
    context: Optional[Dict[str, Any]] = None
) -> IntentRecognitionError:
    """
    Convert generic exceptions to structured intent recognition errors
    
    Args:
        func_name: Name of function where exception occurred
        exception: The original exception
        context: Additional context information
        
    Returns:
        Structured intent recognition error
    """
    context = context or {}
    context['function'] = func_name
    context['original_exception_type'] = exception.__class__.__name__
    
    # Map common exceptions to specific error types
    if isinstance(exception, FileNotFoundError):
        return ModelLoadError(
            message=f"Required file not found: {str(exception)}",
            context=context
        )
    elif isinstance(exception, MemoryError):
        return ResourceError(
            message=f"Insufficient memory: {str(exception)}",
            resource_type="memory",
            context=context
        )
    elif isinstance(exception, TimeoutError):
        return ProcessingTimeoutError(
            message=f"Operation timed out: {str(exception)}",
            context=context
        )
    elif isinstance(exception, ValueError):
        return ValidationError(
            message=f"Invalid value: {str(exception)}",
            context=context
        )
    elif isinstance(exception, KeyError):
        return ConfigurationError(
            message=f"Missing configuration key: {str(exception)}",
            context=context
        )
    else:
        # Generic error for unknown exceptions
        return IntentRecognitionError(
            message=f"Unexpected error in {func_name}: {str(exception)}",
            context=context,
            recoverable=False
        )


class MonetizationIntentError(IntentRecognitionError):
    """Monetization intent processing error"""
    pass


class CollaborationIntentError(IntentRecognitionError):
    """
Collaboration intent processing error"""
    pass
