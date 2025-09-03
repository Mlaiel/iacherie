"""❌ IP Protection Service Exceptions - Professional Error Handling
================================================================

Professional exception classes for the IP Protection Service providing
comprehensive error handling and debugging capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

class IPProtectionException(Exception):
    """Base exception for IP Protection Service"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "IP_PROTECTION_ERROR"
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class DetectionError(IPProtectionException):
    """Exception for plagiarism detection errors"""
    
    def __init__(
        self, 
        message: str, 
        content_id: Optional[str] = None,
        detection_stage: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if content_id:
            details['content_id'] = content_id
        if detection_stage:
            details['detection_stage'] = detection_stage
        
        super().__init__(
            message, 
            error_code="DETECTION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class MonitoringError(IPProtectionException):
    """Exception for monitoring system errors"""
    
    def __init__(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        platform: Optional[str] = None,
        monitoring_stage: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if session_id:
            details['session_id'] = session_id
        if platform:
            details['platform'] = platform
        if monitoring_stage:
            details['monitoring_stage'] = monitoring_stage
        
        super().__init__(
            message, 
            error_code="MONITORING_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class EnforcementError(IPProtectionException):
    """Exception for enforcement and DMCA system errors"""
    
    def __init__(
        self, 
        message: str, 
        violation_id: Optional[str] = None,
        dmca_id: Optional[str] = None,
        platform: Optional[str] = None,
        enforcement_stage: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if violation_id:
            details['violation_id'] = violation_id
        if dmca_id:
            details['dmca_id'] = dmca_id
        if platform:
            details['platform'] = platform
        if enforcement_stage:
            details['enforcement_stage'] = enforcement_stage
        
        super().__init__(
            message, 
            error_code="ENFORCEMENT_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class ValidationError(IPProtectionException):
    """Exception for data validation errors"""
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        validation_rules: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if invalid_value is not None:
            details['invalid_value'] = str(invalid_value)
        if validation_rules:
            details['validation_rules'] = validation_rules
        
        super().__init__(
            message, 
            error_code="VALIDATION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class ConfigurationError(IPProtectionException):
    """Exception for configuration errors"""
    
    def __init__(
        self, 
        message: str, 
        config_section: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_section:
            details['config_section'] = config_section
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(
            message, 
            error_code="CONFIGURATION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class AuthenticationError(IPProtectionException):
    """Exception for authentication errors"""
    
    def __init__(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        auth_method: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if auth_method:
            details['auth_method'] = auth_method
        
        super().__init__(
            message, 
            error_code="AUTHENTICATION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class AuthorizationError(IPProtectionException):
    """Exception for authorization errors"""
    
    def __init__(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if required_permission:
            details['required_permission'] = required_permission
        if resource:
            details['resource'] = resource
        
        super().__init__(
            message, 
            error_code="AUTHORIZATION_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class RateLimitError(IPProtectionException):
    """Exception for rate limiting errors"""
    
    def __init__(
        self, 
        message: str, 
        limit_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit_value: Optional[int] = None,
        reset_time: Optional[datetime] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if limit_type:
            details['limit_type'] = limit_type
        if current_usage is not None:
            details['current_usage'] = current_usage
        if limit_value is not None:
            details['limit_value'] = limit_value
        if reset_time:
            details['reset_time'] = reset_time.isoformat()
        
        super().__init__(
            message, 
            error_code="RATE_LIMIT_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class ResourceError(IPProtectionException):
    """Exception for resource-related errors"""
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message, 
            error_code="RESOURCE_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class DatabaseError(IPProtectionException):
    """Exception for database-related errors"""
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        table: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table
        if query:
            details['query'] = query[:500] if query else None  # Truncate for safety
        
        super().__init__(
            message, 
            error_code="DATABASE_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class APIError(IPProtectionException):
    """Exception for external API errors"""
    
    def __init__(
        self, 
        message: str, 
        api_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if api_name:
            details['api_name'] = api_name
        if endpoint:
            details['endpoint'] = endpoint
        if status_code:
            details['status_code'] = status_code
        if response_body:
            details['response_body'] = response_body[:1000]  # Truncate for safety
        
        super().__init__(
            message, 
            error_code="API_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class LegalError(IPProtectionException):
    """Exception for legal system errors"""
    
    def __init__(
        self, 
        message: str, 
        jurisdiction: Optional[str] = None,
        legal_document_type: Optional[str] = None,
        compliance_issue: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if jurisdiction:
            details['jurisdiction'] = jurisdiction
        if legal_document_type:
            details['legal_document_type'] = legal_document_type
        if compliance_issue:
            details['compliance_issue'] = compliance_issue
        
        super().__init__(
            message, 
            error_code="LEGAL_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

class AIModelError(IPProtectionException):
    """Exception for AI/ML model errors"""
    
    def __init__(
        self, 
        message: str, 
        model_name: Optional[str] = None,
        model_operation: Optional[str] = None,
        input_data_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if model_name:
            details['model_name'] = model_name
        if model_operation:
            details['model_operation'] = model_operation
        if input_data_type:
            details['input_data_type'] = input_data_type
        
        super().__init__(
            message, 
            error_code="AI_MODEL_ERROR",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )

# Error handling utilities
def handle_exception(func):
    """Decorator for standardized exception handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IPProtectionException:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            # Convert generic exceptions to IPProtectionException
            raise IPProtectionException(
                f"Unexpected error in {func.__name__}: {str(e)}",
                details={"function": func.__name__, "args": str(args)[:500]}
            ) from e
    return wrapper

async def ahandle_exception(func):
    """Async decorator for standardized exception handling"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IPProtectionException:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            # Convert generic exceptions to IPProtectionException
            raise IPProtectionException(
                f"Unexpected error in {func.__name__}: {str(e)}",
                details={"function": func.__name__, "args": str(args)[:500]}
            ) from e
    return wrapper

def log_exception(logger, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Log exception with full context"""
    if isinstance(exception, IPProtectionException):
        log_data = exception.to_dict()
        if context:
            log_data['context'] = context
        logger.error(f"IP Protection Error: {exception.message}", extra=log_data)
    else:
        logger.error(f"Unexpected error: {str(exception)}", extra={
            "exception_type": type(exception).__name__,
            "context": context or {}
        })

# Export all exception classes
__all__ = [
    # Base exception
    "IPProtectionException",
    
    # Specific exceptions
    "DetectionError",
    "MonitoringError", 
    "EnforcementError",
    "ValidationError",
    "ConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ResourceError",
    "DatabaseError",
    "APIError",
    "LegalError",
    "AIModelError",
    
    # Utilities
    "handle_exception",
    "ahandle_exception",
    "log_exception"
]