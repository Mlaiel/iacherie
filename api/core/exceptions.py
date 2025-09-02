"""Enterprise-grade exception handling system for IA Influencer Agent.
Professional error hierarchy with comprehensive business logic coverage.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status
from enum import Enum


class ErrorCode(str, Enum):
    """
Professional error codes for business logic categorization."""
    
    # Authentication & Authorization
    AUTHENTICATION_FAILED = "AUTH_001"
    INVALID_CREDENTIALS = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    INSUFFICIENT_PRIVILEGES = "AUTH_004"
    USER_NOT_FOUND = "AUTH_005"
    
    # Business Logic
    CONTENT_NOT_FOUND = "BIZ_001"
    INVALID_CONTENT_TYPE = "BIZ_002"
    UPLOAD_SIZE_EXCEEDED = "BIZ_003"
    CONTENT_ALREADY_PROTECTED = "BIZ_004"
    FINGERPRINT_GENERATION_FAILED = "BIZ_005"
    
    # External Services
    SPOTIFY_API_ERROR = "EXT_001"
    YOUTUBE_API_ERROR = "EXT_002"
    STORAGE_SERVICE_ERROR = "EXT_003"
    ML_SERVICE_UNAVAILABLE = "EXT_004"
    PAYMENT_GATEWAY_ERROR = "EXT_005"
    
    # Database & Infrastructure
    DATABASE_CONNECTION_ERROR = "DB_001"
    REDIS_CONNECTION_ERROR = "DB_002"
    QUERY_TIMEOUT = "DB_003"
    TRANSACTION_FAILED = "DB_004"
    
    # System & Infrastructure
    INTERNAL_SERVER_ERROR = "SYS_001"
    SERVICE_UNAVAILABLE = "SYS_002"
    RATE_LIMIT_EXCEEDED = "SYS_003"
    MAINTENANCE_MODE = "SYS_004"


class BaseApplicationException(Exception):
    """Base exception class for all application-specific errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert exception to dictionary for API responses."""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details
            }
        }


class AuthenticationException(BaseApplicationException):
    """Authentication and authorization related errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(BaseApplicationException):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def __init__(
        self,
        message: str = "Insufficient privileges",
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )


class BusinessLogicException(BaseApplicationException):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ContentNotFoundException(BusinessLogicException):
    """
Content not found error."""
    
    def __init__(
        self,
        content_id: Union[str, int],
        content_type: str = "content"
    ):
        super().__init__(
            message=f"{content_type.title()} not found",
            error_code=ErrorCode.CONTENT_NOT_FOUND,
            details={"content_id": str(content_id), "content_type": content_type}
        )


class ExternalServiceException(BaseApplicationException):
    """External service integration errors."""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{service_name} service error: {message}",
            error_code=error_code,
            details=details or {"service": service_name},
            status_code=status.HTTP_502_BAD_GATEWAY
        )


class DatabaseException(BaseApplicationException):
    """Database operation errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.DATABASE_CONNECTION_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ValidationException(BusinessLogicException):
    """
Input validation errors."""
    
    def __init__(
        self,
        field: str,
        message: str,
        value: Any = None
    ):
        details = {"field": field}
        if value is not None:
            details["provided_value"] = str(value)
            
        super().__init__(
            message=f"Validation error for {field}: {message}",
            error_code=ErrorCode.INVALID_CONTENT_TYPE,
            details=details
        )


class RateLimitException(BaseApplicationException):
    """Rate limiting errors."""
    
    def __init__(
        self,
        limit: int,
        window: int,
        retry_after: Optional[int] = None
    ):
        details = {
            "limit": limit,
            "window_seconds": window
        }
        if retry_after:
            details["retry_after_seconds"] = retry_after
            
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window} seconds",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details=details,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ContentProtectionException(BusinessLogicException):
    """Content protection specific errors."""
    
    def __init__(
        self,
        message: str,
        content_id: Optional[Union[str, int]] = None,
        protection_type: Optional[str] = None
    ):
        details = {}
        if content_id:
            details["content_id"] = str(content_id)
        if protection_type:
            details["protection_type"] = protection_type
            
        super().__init__(
            message=message,
            error_code=ErrorCode.CONTENT_ALREADY_PROTECTED,
            details=details
        )


class FingerprintException(BaseApplicationException):
    """Fingerprint generation and matching errors."""
    
    def __init__(
        self,
        message: str,
        content_type: str,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = {"content_type": content_type}
        if details:
            error_details.update(details)
            
        super().__init__(
            message=message,
            error_code=ErrorCode.FINGERPRINT_GENERATION_FAILED,
            details=error_details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def convert_to_http_exception(exc: BaseApplicationException) -> HTTPException:
    """Convert application exception to FastAPI HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.to_dict()
    )


def get_error_message(error_code: ErrorCode, default_message: str = "An error occurred") -> str:
    """Get user-friendly error message based on error code."""
    error_messages = {
        ErrorCode.AUTHENTICATION_FAILED: "Authentication credentials are invalid or missing",
        ErrorCode.INVALID_CREDENTIALS: "The provided credentials are incorrect",
        ErrorCode.TOKEN_EXPIRED: "Your session has expired, please log in again",
        ErrorCode.INSUFFICIENT_PRIVILEGES: "You don't have permission to perform this action",
        ErrorCode.USER_NOT_FOUND: "User account not found",
        
        ErrorCode.CONTENT_NOT_FOUND: "The requested content could not be found",
        ErrorCode.INVALID_CONTENT_TYPE: "The content type is not supported",
        ErrorCode.UPLOAD_SIZE_EXCEEDED: "The uploaded file exceeds the maximum size limit",
        ErrorCode.CONTENT_ALREADY_PROTECTED: "This content is already under protection",
        ErrorCode.FINGERPRINT_GENERATION_FAILED: "Failed to generate content fingerprint",
        
        ErrorCode.SPOTIFY_API_ERROR: "Spotify service is temporarily unavailable",
        ErrorCode.YOUTUBE_API_ERROR: "YouTube service is temporarily unavailable",
        ErrorCode.STORAGE_SERVICE_ERROR: "File storage service is temporarily unavailable",
        ErrorCode.ML_SERVICE_UNAVAILABLE: "AI processing service is temporarily unavailable",
        ErrorCode.PAYMENT_GATEWAY_ERROR: "Payment processing is temporarily unavailable",
        
        ErrorCode.DATABASE_CONNECTION_ERROR: "Database service is temporarily unavailable",
        ErrorCode.REDIS_CONNECTION_ERROR: "Cache service is temporarily unavailable",
        ErrorCode.QUERY_TIMEOUT: "The operation took too long to complete",
        ErrorCode.TRANSACTION_FAILED: "Database transaction failed",
        
        ErrorCode.INTERNAL_SERVER_ERROR: "An internal server error occurred",
        ErrorCode.SERVICE_UNAVAILABLE: "The service is temporarily unavailable",
        ErrorCode.RATE_LIMIT_EXCEEDED: "Too many requests, please try again later",
        ErrorCode.MAINTENANCE_MODE: "The service is under maintenance",
    }
    
    return error_messages.get(error_code, default_message)
