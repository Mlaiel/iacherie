"""Comprehensive Exception Handling for Ainflue SDK

Enterprise-grade exception hierarchy with multi-expert design:
- Backend Senior: Robust error handling architecture
- Sécurité: Security-aware exception design
- DevOps: Monitoring and logging integration
- Lead Dev IA: Intelligent error recovery

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime


class AinflueSdkException(Exception):
    """Base exception class for all Ainflue SDK errors
    
    Designed with enterprise requirements:
    - Structured error information
    - Monitoring integration
    - Security-aware logging
    - Multi-language support
    """
    
    def __init__(
        self,
        message -> None: str,
        error_code -> None: Optional[str] = None,
        context -> None: Optional[Dict[str, Any]] = None,
        inner_exception -> None: Optional[Exception] = None,
        severity -> None: str = "ERROR"
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.inner_exception = inner_exception
        self.severity = severity
        self.timestamp = datetime.utcnow()
        self.logger = logging.getLogger(__name__)
        
        # Log the exception for monitoring (DevOps expertise)
        self._log_exception()
    
    def _log_exception(self) -> None:
        """Log exception for monitoring and debugging"""
        log_data = {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'context': self._sanitize_context()
        }
        
        if self.severity == "CRITICAL":
            self.logger.critical(f"SDK Critical Error: {json.dumps(log_data)}")
        elif self.severity == "ERROR":
            self.logger.error(f"SDK Error: {json.dumps(log_data)}")
        elif self.severity == "WARNING":
            self.logger.warning(f"SDK Warning: {json.dumps(log_data)}")
        else:
            self.logger.info(f"SDK Info: {json.dumps(log_data)}")
    
    def _sanitize_context(self) -> Dict[str, Any]:
        """Sanitize context data for security (Sécurité expertise)"""
        sanitized = {}
        sensitive_keys = ['password', 'api_key', 'token', 'secret', 'auth', 'credential']
        
        for key, value in self.context.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = str(value)[:100]  # Limit length
        
        return sanitized
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'context': self._sanitize_context(),
            'inner_exception': str(self.inner_exception) if self.inner_exception else None
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# Authentication & Authorization Exceptions
class AuthenticationError(AinflueSdkException):
    """Authentication failed - invalid credentials or tokens"""
    
    def __init__(self, message -> None: str = "Authentication failed", **kwargs) -> None:
        super().__init__(message, error_code="AUTH_FAILED", severity="ERROR", **kwargs)


class AuthorizationError(AinflueSdkException):
    """Authorization failed - insufficient permissions"""
    
    def __init__(self, message -> None: str = "Insufficient permissions", **kwargs) -> None:
        super().__init__(message, error_code="AUTH_INSUFFICIENT", severity="ERROR", **kwargs)


class TokenExpiredError(AuthenticationError):
    """Access token has expired"""
    
    def __init__(self, message -> None: str = "Access token expired", **kwargs) -> None:
        super().__init__(message, error_code="TOKEN_EXPIRED", **kwargs)


class TokenInvalidError(AuthenticationError):
    """Access token is invalid or malformed"""
    
    def __init__(self, message -> None: str = "Invalid access token", **kwargs) -> None:
        super().__init__(message, error_code="TOKEN_INVALID", **kwargs)


# API & Network Exceptions
class APIError(AinflueSdkException):
    """API request failed"""
    
    def __init__(
        self,
        message -> None: str,
        status_code -> None: Optional[int] = None,
        response_data -> None: Optional[Dict] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        if status_code:
            context['status_code'] = status_code
        if response_data:
            context['response_data'] = response_data
            
        super().__init__(
            message,
            error_code=f"API_ERROR_{status_code}" if status_code else "API_ERROR",
            context=context,
            **kwargs
        )
        self.status_code = status_code
        self.response_data = response_data


class NetworkError(AinflueSdkException):
    """Network connectivity issues"""
    
    def __init__(self, message -> None: str = "Network connection failed", **kwargs) -> None:
        super().__init__(message, error_code="NETWORK_ERROR", severity="ERROR", **kwargs)


class TimeoutError(NetworkError):
    """Request timeout exceeded"""
    
    def __init__(self, message -> None: str = "Request timeout", timeout_duration -> None: Optional[float] = None, **kwargs) -> None:
        context = kwargs.pop('context', {})
        if timeout_duration:
            context['timeout_duration'] = timeout_duration
        super().__init__(message, error_code="TIMEOUT", context=context, **kwargs)


class RateLimitError(APIError):
    """Rate limit exceeded"""
    
    def __init__(
        self,
        message -> None: str = "Rate limit exceeded",
        retry_after -> None: Optional[int] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        if retry_after:
            context['retry_after'] = retry_after
        super().__init__(message, error_code="RATE_LIMIT", context=context, **kwargs)


# Validation & Data Exceptions
class ValidationError(AinflueSdkException):
    """Request validation failed"""
    
    def __init__(
        self,
        message -> None: str,
        field_errors -> None: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        if field_errors:
            context['field_errors'] = field_errors
        super().__init__(message, error_code="VALIDATION_ERROR", context=context, **kwargs)
        self.field_errors = field_errors or {}


class DataError(AinflueSdkException):
    """Data processing or format error"""
    
    def __init__(self, message -> None: str = "Data processing error", **kwargs) -> None:
        super().__init__(message, error_code="DATA_ERROR", **kwargs)


class SerializationError(DataError):
    """JSON/Data serialization failed"""
    
    def __init__(self, message -> None: str = "Serialization failed", **kwargs) -> None:
        super().__init__(message, error_code="SERIALIZATION_ERROR", **kwargs)


# Content & AI Processing Exceptions
class ContentProcessingError(AinflueSdkException):
    """Content analysis or processing failed"""
    
    def __init__(
        self,
        message -> None: str,
        content_type -> None: Optional[str] = None,
        processing_stage -> None: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        if content_type:
            context['content_type'] = content_type
        if processing_stage:
            context['processing_stage'] = processing_stage
        super().__init__(message, error_code="CONTENT_PROCESSING_ERROR", context=context, **kwargs)


class AIProcessingError(AinflueSdkException):
    """AI model or processing error"""
    
    def __init__(
        self,
        message -> None: str,
        model_name -> None: Optional[str] = None,
        ai_provider -> None: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        if model_name:
            context['model_name'] = model_name
        if ai_provider:
            context['ai_provider'] = ai_provider
        super().__init__(message, error_code="AI_PROCESSING_ERROR", context=context, **kwargs)


class ModelNotAvailableError(AIProcessingError):
    """AI model is not available or loaded"""
    
    def __init__(self, message -> None: str = "AI model not available", **kwargs) -> None:
        super().__init__(message, error_code="MODEL_UNAVAILABLE", **kwargs)


# Configuration & Setup Exceptions
class ConfigurationError(AinflueSdkException):
    """SDK configuration error"""
    
    def __init__(self, message -> None: str = "Configuration error", **kwargs) -> None:
        super().__init__(message, error_code="CONFIG_ERROR", severity="CRITICAL", **kwargs)


class InitializationError(ConfigurationError):
    """SDK initialization failed"""
    
    def __init__(self, message -> None: str = "SDK initialization failed", **kwargs) -> None:
        super().__init__(message, error_code="INIT_ERROR", **kwargs)


# Business Logic Exceptions
class BusinessLogicError(AinflueSdkException):
    """Business rule or logic violation"""
    
    def __init__(self, message -> None: str, rule_name -> None: Optional[str] = None, **kwargs) -> None:
        context = kwargs.pop('context', {})
        if rule_name:
            context['rule_name'] = rule_name
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", context=context, **kwargs)


class QuotaExceededError(BusinessLogicError):
    """Usage quota exceeded"""
    
    def __init__(
        self,
        message -> None: str = "Usage quota exceeded",
        quota_type -> None: Optional[str] = None,
        current_usage -> None: Optional[int] = None,
        quota_limit -> None: Optional[int] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        context.update({
            'quota_type': quota_type,
            'current_usage': current_usage,
            'quota_limit': quota_limit
        })
        super().__init__(message, error_code="QUOTA_EXCEEDED", context=context, **kwargs)


class ResourceNotFoundError(AinflueSdkException):
    """Requested resource not found"""
    
    def __init__(
        self,
        message -> None: str = "Resource not found",
        resource_type -> None: Optional[str] = None,
        resource_id -> None: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.pop('context', {})
        if resource_type:
            context['resource_type'] = resource_type
        if resource_id:
            context['resource_id'] = resource_id
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", context=context, **kwargs)


# Utility functions for exception handling
def handle_api_response_error(response_data: Dict[str, Any], status_code: int) -> AinflueSdkException:
    """Convert API error response to appropriate exception"""
    
    error_code = response_data.get('error_code', 'UNKNOWN_ERROR')
    message = response_data.get('message', 'Unknown error occurred')
    
    # Map error codes to specific exceptions
    error_mapping = {
        'AUTH_FAILED': AuthenticationError,
        'TOKEN_EXPIRED': TokenExpiredError,
        'TOKEN_INVALID': TokenInvalidError,
        'AUTH_INSUFFICIENT': AuthorizationError,
        'RATE_LIMIT': RateLimitError,
        'VALIDATION_ERROR': ValidationError,
        'QUOTA_EXCEEDED': QuotaExceededError,
        'RESOURCE_NOT_FOUND': ResourceNotFoundError,
        'CONTENT_PROCESSING_ERROR': ContentProcessingError,
        'AI_PROCESSING_ERROR': AIProcessingError
    }
    
    exception_class = error_mapping.get(error_code, APIError)
    
    return exception_class(
        message=message,
        status_code=status_code,
        response_data=response_data,
        context={'api_response': True}
    )


def is_retryable_error(exception: Exception) -> bool:
    """Determine if an error is retryable"""
    
    retryable_errors = (
        NetworkError,
        TimeoutError,
        APIError
    )
    
    if isinstance(exception, retryable_errors):
        # Don't retry authentication or authorization errors
        if isinstance(exception, (AuthenticationError, AuthorizationError)):
            return False
        
        # Don't retry validation errors
        if isinstance(exception, ValidationError):
            return False
        
        # Check status codes for API errors
        if isinstance(exception, APIError) and exception.status_code:
            # Retry server errors (5xx) and some client errors
            return exception.status_code >= 500 or exception.status_code in [408, 429]
        
        return True
    
    return False


# Export all exception classes
__all__ = [
    # Base exception
    'AinflueSdkException',
    
    # Authentication & Authorization
    'AuthenticationError',
    'AuthorizationError', 
    'TokenExpiredError',
    'TokenInvalidError',
    
    # API & Network
    'APIError',
    'NetworkError',
    'TimeoutError',
    'RateLimitError',
    
    # Validation & Data
    'ValidationError',
    'DataError',
    'SerializationError',
    
    # Content & AI Processing
    'ContentProcessingError',
    'AIProcessingError',
    'ModelNotAvailableError',
    
    # Configuration & Setup
    'ConfigurationError',
    'InitializationError',
    
    # Business Logic
    'BusinessLogicError',
    'QuotaExceededError',
    'ResourceNotFoundError',
    
    # Utility functions
    'handle_api_response_error',
    'is_retryable_error'
]