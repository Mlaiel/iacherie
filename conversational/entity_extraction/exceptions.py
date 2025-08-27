"""
Entity Extraction Exceptions - IA Influencer Agent

Custom exception classes for robust error handling in entity extraction module
with specific error types for different failure scenarios.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

from typing import Dict, Any, Optional, List
import logging


class EntityExtractionError(Exception):
    """Base exception for entity extraction errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "ENTITY_EXTRACTION_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error': self.error_code,
            'message': self.message,
            'details': self.details,
            'type': self.__class__.__name__
        }


class ModelLoadError(EntityExtractionError):
    """Raised when ML models fail to load"""
    
    def __init__(self, model_name: str, reason: str = None):
        message = f"Failed to load model '{model_name}'"
        if reason:
            message += f": {reason}"
        
        details = {
            'model_name': model_name,
            'reason': reason
        }
        
        super().__init__(message, "MODEL_LOAD_ERROR", details)


class ModelInferenceError(EntityExtractionError):
    """Raised when model inference fails"""
    
    def __init__(self, model_name: str, input_data: Any = None, reason: str = None):
        message = f"Model inference failed for '{model_name}'"
        if reason:
            message += f": {reason}"
        
        details = {
            'model_name': model_name,
            'input_type': type(input_data).__name__ if input_data else None,
            'reason': reason
        }
        
        super().__init__(message, "MODEL_INFERENCE_ERROR", details)


class InvalidInputError(EntityExtractionError):
    """Raised when input data is invalid"""
    
    def __init__(self, input_type: str, validation_errors: List[str] = None):
        message = f"Invalid input data for {input_type}"
        if validation_errors:
            message += f": {', '.join(validation_errors)}"
        
        details = {
            'input_type': input_type,
            'validation_errors': validation_errors or []
        }
        
        super().__init__(message, "INVALID_INPUT_ERROR", details)


class APIConnectionError(EntityExtractionError):
    """Raised when external API connections fail"""
    
    def __init__(self, api_name: str, endpoint: str = None, status_code: int = None, reason: str = None):
        message = f"Failed to connect to {api_name} API"
        if status_code:
            message += f" (HTTP {status_code})"
        if reason:
            message += f": {reason}"
        
        details = {
            'api_name': api_name,
            'endpoint': endpoint,
            'status_code': status_code,
            'reason': reason
        }
        
        super().__init__(message, "API_CONNECTION_ERROR", details)


class RateLimitError(EntityExtractionError):
    """Raised when API rate limits are exceeded"""
    
    def __init__(self, api_name: str, retry_after: int = None):
        message = f"Rate limit exceeded for {api_name} API"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        
        details = {
            'api_name': api_name,
            'retry_after': retry_after
        }
        
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class DataProcessingError(EntityExtractionError):
    """Raised when data processing fails"""
    
    def __init__(self, operation: str, data_type: str = None, reason: str = None):
        message = f"Data processing failed for operation '{operation}'"
        if data_type:
            message += f" on {data_type} data"
        if reason:
            message += f": {reason}"
        
        details = {
            'operation': operation,
            'data_type': data_type,
            'reason': reason
        }
        
        super().__init__(message, "DATA_PROCESSING_ERROR", details)


class ConfigurationError(EntityExtractionError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, config_key: str = None, reason: str = None):
        message = "Configuration error"
        if config_key:
            message += f" for key '{config_key}'"
        if reason:
            message += f": {reason}"
        
        details = {
            'config_key': config_key,
            'reason': reason
        }
        
        super().__init__(message, "CONFIGURATION_ERROR", details)


class ResourceNotFoundError(EntityExtractionError):
    """Raised when required resources are not found"""
    
    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"Required {resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id
        }
        
        super().__init__(message, "RESOURCE_NOT_FOUND_ERROR", details)


class TimeoutError(EntityExtractionError):
    """Raised when operations timeout"""
    
    def __init__(self, operation: str, timeout_seconds: float):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        
        details = {
            'operation': operation,
            'timeout_seconds': timeout_seconds
        }
        
        super().__init__(message, "TIMEOUT_ERROR", details)


class CacheError(EntityExtractionError):
    """Raised when cache operations fail"""
    
    def __init__(self, operation: str, cache_key: str = None, reason: str = None):
        message = f"Cache {operation} failed"
        if cache_key:
            message += f" for key '{cache_key}'"
        if reason:
            message += f": {reason}"
        
        details = {
            'operation': operation,
            'cache_key': cache_key,
            'reason': reason
        }
        
        super().__init__(message, "CACHE_ERROR", details)


class ValidationError(EntityExtractionError):
    """Raised when data validation fails"""
    
    def __init__(self, field_name: str, expected_type: str = None, actual_value: Any = None):
        message = f"Validation failed for field '{field_name}'"
        if expected_type:
            message += f": expected {expected_type}"
            if actual_value is not None:
                message += f", got {type(actual_value).__name__}"
        
        details = {
            'field_name': field_name,
            'expected_type': expected_type,
            'actual_type': type(actual_value).__name__ if actual_value is not None else None,
            'actual_value': str(actual_value) if actual_value is not None else None
        }
        
        super().__init__(message, "VALIDATION_ERROR", details)


class SecurityError(EntityExtractionError):
    """Raised when security violations are detected"""
    
    def __init__(self, violation_type: str, details_msg: str = None):
        message = f"Security violation detected: {violation_type}"
        if details_msg:
            message += f" - {details_msg}"
        
        details = {
            'violation_type': violation_type,
            'details': details_msg
        }
        
        super().__init__(message, "SECURITY_ERROR", details)


class MemoryError(EntityExtractionError):
    """Raised when memory limits are exceeded"""
    
    def __init__(self, operation: str, memory_usage_mb: float = None):
        message = f"Memory limit exceeded during operation '{operation}'"
        if memory_usage_mb:
            message += f" (using {memory_usage_mb:.1f} MB)"
        
        details = {
            'operation': operation,
            'memory_usage_mb': memory_usage_mb
        }
        
        super().__init__(message, "MEMORY_ERROR", details)


class DependencyError(EntityExtractionError):
    """Raised when required dependencies are missing or incompatible"""
    
    def __init__(self, dependency_name: str, required_version: str = None, actual_version: str = None):
        message = f"Dependency error: {dependency_name}"
        if required_version:
            message += f" (required: {required_version}"
            if actual_version:
                message += f", found: {actual_version}"
            message += ")"
        
        details = {
            'dependency_name': dependency_name,
            'required_version': required_version,
            'actual_version': actual_version
        }
        
        super().__init__(message, "DEPENDENCY_ERROR", details)


class DataQualityError(EntityExtractionError):
    """Raised when data quality is insufficient for processing"""
    
    def __init__(self, quality_issue: str, quality_score: float = None, threshold: float = None):
        message = f"Data quality issue: {quality_issue}"
        if quality_score is not None and threshold is not None:
            message += f" (score: {quality_score:.3f}, threshold: {threshold:.3f})"
        
        details = {
            'quality_issue': quality_issue,
            'quality_score': quality_score,
            'threshold': threshold
        }
        
        super().__init__(message, "DATA_QUALITY_ERROR", details)


class ConcurrencyError(EntityExtractionError):
    """Raised when concurrency-related issues occur"""
    
    def __init__(self, operation: str, concurrent_operations: int = None):
        message = f"Concurrency error in operation '{operation}'"
        if concurrent_operations:
            message += f" (active operations: {concurrent_operations})"
        
        details = {
            'operation': operation,
            'concurrent_operations': concurrent_operations
        }
        
        super().__init__(message, "CONCURRENCY_ERROR", details)


class EntityNotFoundError(EntityExtractionError):
    """Raised when expected entities are not found"""
    
    def __init__(self, entity_type: str, search_criteria: Dict[str, Any] = None):
        message = f"No {entity_type} entities found"
        if search_criteria:
            criteria_str = ', '.join([f"{k}={v}" for k, v in search_criteria.items()])
            message += f" matching criteria: {criteria_str}"
        
        details = {
            'entity_type': entity_type,
            'search_criteria': search_criteria or {}
        }
        
        super().__init__(message, "ENTITY_NOT_FOUND_ERROR", details)


class ExtractionQualityError(EntityExtractionError):
    """Raised when extraction quality is below acceptable threshold"""
    
    def __init__(self, avg_confidence: float, min_threshold: float, entity_count: int = None):
        message = f"Extraction quality below threshold: {avg_confidence:.3f} < {min_threshold:.3f}"
        if entity_count:
            message += f" (extracted {entity_count} entities)"
        
        details = {
            'average_confidence': avg_confidence,
            'min_threshold': min_threshold,
            'entity_count': entity_count
        }
        
        super().__init__(message, "EXTRACTION_QUALITY_ERROR", details)


# Error handling utilities
class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def log_error(error: EntityExtractionError, context: str = None):
        """Log error with appropriate level and context"""
        log_message = f"EntityExtraction Error: {error.message}"
        if context:
            log_message = f"{context} - {log_message}"
        
        # Determine log level based on error type
        if isinstance(error, (SecurityError, DependencyError)):
            logging.critical(log_message, extra={'error_details': error.details})
        elif isinstance(error, (ModelLoadError, ConfigurationError)):
            logging.error(log_message, extra={'error_details': error.details})
        elif isinstance(error, (APIConnectionError, TimeoutError)):
            logging.warning(log_message, extra={'error_details': error.details})
        else:
            logging.info(log_message, extra={'error_details': error.details})
    
    @staticmethod
    def handle_and_reraise(func):
        """Decorator to handle exceptions and convert to EntityExtractionError"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except EntityExtractionError:
                # Re-raise our custom exceptions
                raise
            except ValueError as e:
                raise ValidationError("value_error", reason=str(e))
            except KeyError as e:
                raise ConfigurationError(str(e), "missing_key")
            except FileNotFoundError as e:
                raise ResourceNotFoundError("file", str(e))
            except ConnectionError as e:
                raise APIConnectionError("unknown", reason=str(e))
            except MemoryError as e:
                raise MemoryError("unknown", reason=str(e))
            except Exception as e:
                # Catch-all for unexpected errors
                raise EntityExtractionError(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    "UNEXPECTED_ERROR",
                    {'function': func.__name__, 'exception_type': type(e).__name__}
                )
        return wrapper
    
    @staticmethod
    def create_error_response(error: EntityExtractionError) -> Dict[str, Any]:
        """Create standardized error response for APIs"""
        return {
            'success': False,
            'error': error.to_dict(),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    @staticmethod
    def is_retryable_error(error: EntityExtractionError) -> bool:
        """Determine if an error is retryable"""
        retryable_types = (
            APIConnectionError,
            TimeoutError,
            CacheError,
            ConcurrencyError
        )
        return isinstance(error, retryable_types)


# Exception context manager
class EntityExtractionContext:
    """Context manager for entity extraction operations with error handling"""
    
    def __init__(self, operation_name: str, log_errors: bool = True):
        self.operation_name = operation_name
        self.log_errors = log_errors
        self.start_time = None
    
    def __enter__(self):
        self.start_time = __import__('time').time()
        logging.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = __import__('time').time() - self.start_time
        
        if exc_type is None:
            logging.debug(f"Operation completed successfully: {self.operation_name} ({duration:.3f}s)")
        elif issubclass(exc_type, EntityExtractionError):
            if self.log_errors:
                ErrorHandler.log_error(exc_val, self.operation_name)
            logging.debug(f"Operation failed: {self.operation_name} ({duration:.3f}s)")
        else:
            # Convert unexpected exceptions
            logging.error(f"Unexpected error in {self.operation_name}: {exc_val}")
            
        return False  # Don't suppress exceptions


# Global error handler instance
error_handler = ErrorHandler()
