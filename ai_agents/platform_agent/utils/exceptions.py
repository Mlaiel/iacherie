"""Platform Agent Exceptions - Enterprise Error Handling

Comprehensive exception hierarchy for robust error handling and debugging
in all Platform Agent components with detailed error reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import traceback
from datetime import datetime


class ErrorSeverity(Enum):
    """
Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""

    PLATFORM_API = "platform_api"
    AUTHENTICATION = "authentication"
    CONTENT_PROCESSING = "content_processing"
    DATABASE = "database"
    NETWORK = "network"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    AI_PROCESSING = "ai_processing"
    FILE_OPERATIONS = "file_operations"
    SYNCHRONIZATION = "synchronization"
    RATE_LIMITING = "rate_limiting"
    OPTIMIZATION = "optimization"
    DISTRIBUTION = "distribution"
    MONITORING = "monitoring"


class PlatformAgentBaseException(Exception):
    """Base exception for all Platform Agent errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.PLATFORM_API,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        recoverable: bool = True,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.recoverable = recoverable
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()
        
    def _generate_user_message(self) -> str:
        """
Generate user-friendly error message"""
        return f"An error occurred in {self.category.value}. Please try again."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "retry_after": self.retry_after,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback if self.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
        }
    
    def __str__(self) -> str:
        try:
            logger.info(f"Executing __str__")
            
            # Implementation for __str__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__str__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__str__ failed: {e}")
            raise
class PlatformConnectionException(PlatformAgentBaseException):
    """Base exception for platform connection errors"""
    
    def __init__(self, platform: str, message: str, **kwargs):
        self.platform = platform
        super().__init__(
            message,
            category=ErrorCategory.PLATFORM_API,
            details={"platform": platform},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
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
    def _generate_user_message(self) -> str:
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
        return f"Unable to connect to {self.platform}. Please check your internet connection and try again."


class PlatformAuthenticationException(PlatformConnectionException):
    """Authentication failed with platform"""
    
    def __init__(self, platform: str, message: str = "Authentication failed", **kwargs):
        super().__init__(
            platform,
            message,
            error_code="PLATFORM_AUTH_FAILED",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
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
class PlatformRateLimitException(PlatformConnectionException):
    """Platform rate limit exceeded"""
    
    def __init__(self, platform: str, retry_after: int = 60, **kwargs):
        super().__init__(
            platform,
            f"Rate limit exceeded for {platform}",
            error_code="RATE_LIMIT_EXCEEDED",
            category=ErrorCategory.RATE_LIMITING,
            severity=ErrorSeverity.MEDIUM,
            retry_after=retry_after,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return f"Too many requests to {self.platform}. Please wait {self.retry_after} seconds before trying again."


class PlatformAPIException(PlatformConnectionException):
    """General platform API error"""
    
    def __init__(self, platform: str, api_error: str, status_code: Optional[int] = None, **kwargs):
        self.status_code = status_code
        super().__init__(
            platform,
            f"API error from {platform}: {api_error}",
            error_code="PLATFORM_API_ERROR",
            details={"api_error": api_error, "status_code": status_code},
            **kwargs
        )


class PlatformUnavailableException(PlatformConnectionException):
    """Platform is temporarily unavailable"""
    
    def __init__(self, platform: str, **kwargs):
        super().__init__(
            platform,
            f"{platform} is currently unavailable",
            error_code="PLATFORM_UNAVAILABLE",
            severity=ErrorSeverity.HIGH,
            retry_after=300,  # 5 minutes
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return f"{self.platform} is currently unavailable. Please try again later."


# Content Processing Exceptions
class ContentProcessingException(PlatformAgentBaseException):
    """Base exception for content processing errors"""
    
    def __init__(self, message: str, content_type: Optional[str] = None, **kwargs):
        self.content_type = content_type
        super().__init__(
            message,
            category=ErrorCategory.CONTENT_PROCESSING,
            details={"content_type": content_type},
            **kwargs
        )


class ContentValidationException(ContentProcessingException):
    """Content validation failed"""
    
    def __init__(self, validation_errors: List[str], **kwargs):
        self.validation_errors = validation_errors
        super().__init__(
            f"Content validation failed: {', '.join(validation_errors)}",
            error_code="CONTENT_VALIDATION_FAILED",
            details={"validation_errors": validation_errors},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "The content doesn't meet platform requirements. Please check and try again."


class ContentFormatException(ContentProcessingException):
    """Unsupported or invalid content format"""
    
    def __init__(self, format_type: str, supported_formats: Optional[List[str]] = None, **kwargs):
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
        self.supported_formats = supported_formats or []
        super().__init__(
            f"Unsupported content format: {format_type}",
            error_code="UNSUPPORTED_FORMAT",
            details={"format": format_type, "supported_formats": self.supported_formats},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        if self.supported_formats:
            return f"Format '{self.format_type}' is not supported. Supported formats: {', '.join(self.supported_formats)}"
        return f"Format '{self.format_type}' is not supported."


class ContentSizeException(ContentProcessingException):
    """Content exceeds size limits"""
    
    def __init__(self, actual_size: int, max_size: int, **kwargs):
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
        self.max_size = max_size
        super().__init__(
            f"Content size {actual_size} exceeds maximum {max_size}",
            error_code="CONTENT_TOO_LARGE",
            details={"actual_size": actual_size, "max_size": max_size},
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
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            details={"actual_size": actual_size, "max_size": max_size},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return f"File is too large. Maximum size is {self.max_size // (1024*1024)} MB."


# AI Processing Exceptions
class AIProcessingException(PlatformAgentBaseException):
    """Base exception for AI processing errors"""
    
    def __init__(self, message: str, model_name: Optional[str] = None, **kwargs):
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
    def __init__(self, message: str, model_name: Optional[str] = None, **kwargs):
        self.model_name = model_name
        super().__init__(
            message,
            category=ErrorCategory.AI_PROCESSING,
            details={"model_name": model_name},
            **kwargs
        )


class AIModelLoadException(AIProcessingException):
    """AI model failed to load"""
    
    def __init__(self, model_name: str, **kwargs):
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
        super().__init__(
            f"Failed to load AI model: {model_name}",
            model_name=model_name,
            error_code="AI_MODEL_LOAD_FAILED",
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "AI processing is temporarily unavailable. Please try again later."


class AIProcessingTimeoutException(AIProcessingException):
    """AI processing timed out"""
    
    def __init__(self, timeout_seconds: int, **kwargs):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"AI processing timed out after {timeout_seconds} seconds",
            error_code="AI_PROCESSING_TIMEOUT",
            details={"timeout_seconds": timeout_seconds},
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
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            f"AI processing timed out after {timeout_seconds} seconds",
            error_code="AI_PROCESSING_TIMEOUT",
            details={"timeout_seconds": timeout_seconds},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "AI processing is taking longer than expected. Please try again with a smaller file."


class AIResourceException(AIProcessingException):
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
class AIResourceException(AIProcessingException):
    """Insufficient resources for AI processing"""
    
    def __init__(self, resource_type: str, required: str, available: str, **kwargs):
        super().__init__(
            f"Insufficient {resource_type}: required {required}, available {available}",
            error_code="INSUFFICIENT_AI_RESOURCES",
            severity=ErrorSeverity.HIGH,
            details={"resource_type": resource_type, "required": required, "available": available},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
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
            raise
    def _generate_user_message(self) -> str:
        return "AI processing resources are currently limited. Please try again later."


# Database Exceptions
class DatabaseException(PlatformAgentBaseException):
    """Base exception for database errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            **kwargs
        )


class DatabaseConnectionException(DatabaseException):
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
        )


class DatabaseConnectionException(DatabaseException):
    """
Database connection failed"""
    
    def __init__(self, **kwargs):
        super().__init__(
            "Database connection failed",
            error_code="DATABASE_CONNECTION_FAILED",
            severity=ErrorSeverity.CRITICAL,
            recoverable=False,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "Database is temporarily unavailable. Please try again later."


class DatabaseIntegrityException(DatabaseException):
    """Database integrity constraint violation"""
    
    def __init__(self, constraint: str, **kwargs):
        self.constraint = constraint
        super().__init__(
            f"Database integrity constraint violated: {constraint}",
            error_code="DATABASE_INTEGRITY_ERROR",
            details={"constraint": constraint},
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
            logger.error(f"__init__ failed: {e}")
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
            raise
            **kwargs
        )


# Synchronization Exceptions
class SynchronizationException(PlatformAgentBaseException):
    """Base exception for synchronization errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SYNCHRONIZATION,
            **kwargs
        )


class SyncConflictException(SynchronizationException):
    """
Synchronization conflict detected"""
    
    def __init__(self, conflict_type: str, conflicting_data: Dict[str, Any], **kwargs):
        self.conflict_type = conflict_type
        self.conflicting_data = conflicting_data
        super().__init__(
            f"Synchronization conflict: {conflict_type}",
            error_code="SYNC_CONFLICT",
            details={"conflict_type": conflict_type, "conflicting_data": conflicting_data},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "A synchronization conflict occurred. Please refresh and try again."


class SyncLockException(SynchronizationException):
    """Unable to acquire synchronization lock"""
    
    def __init__(self, resource: str, timeout: int, **kwargs):
        super().__init__(
            f"Unable to acquire lock for {resource} within {timeout} seconds",
            error_code="SYNC_LOCK_TIMEOUT",
            details={"resource": resource, "timeout": timeout},
            **kwargs
        )


# Configuration Exceptions
class ConfigurationException(PlatformAgentBaseException):
    """Configuration error"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        self.config_key = config_key
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            recoverable=False,
            details={"config_key": config_key},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "System configuration error. Please contact support."


class MissingConfigurationException(ConfigurationException):
    """Required configuration is missing"""
    
    def __init__(self, config_key: str, **kwargs):
        super().__init__(
            f"Missing required configuration: {config_key}",
            config_key=config_key,
            error_code="MISSING_CONFIGURATION",
            **kwargs
        )


# Security Exceptions
class SecurityException(PlatformAgentBaseException):
    """Base exception for security-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthenticationException(SecurityException):
    """
Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message,
            error_code="AUTHENTICATION_FAILED",
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "Authentication failed. Please check your credentials and try again."


class AuthorizationException(SecurityException):
    """Authorization/permission denied"""
    
    def __init__(self, resource: str, action: str, **kwargs):
        self.resource = resource
        self.action = action
        super().__init__(
            f"Access denied to {action} on {resource}",
            error_code="ACCESS_DENIED",
            details={"resource": resource, "action": action},
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "You don't have permission to perform this action."


class EncryptionException(SecurityException):
    """Encryption/decryption error"""
    
    def __init__(self, operation: str, **kwargs):
        super().__init__(
            f"Encryption {operation} failed",
            error_code="ENCRYPTION_ERROR",
            details={"operation": operation},
            **kwargs
        )


# File Operation Exceptions
class FileOperationException(PlatformAgentBaseException):
    """File operation error"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        self.file_path = file_path
        super().__init__(
            message,
            category=ErrorCategory.FILE_OPERATIONS,
            details={"file_path": file_path},
            **kwargs
        )


class FileNotFoundException(FileOperationException):
    """File not found"""
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(
            f"File not found: {file_path}",
            file_path=file_path,
            error_code="FILE_NOT_FOUND",
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "The requested file could not be found."


class FilePermissionException(FileOperationException):
    """File permission error"""
    
    def __init__(self, file_path: str, operation: str, **kwargs):
        super().__init__(
            f"Permission denied for {operation} on {file_path}",
            file_path=file_path,
            error_code="FILE_PERMISSION_DENIED",
            details={"operation": operation},
            **kwargs
        )


# Optimization Exceptions
class OptimizationException(PlatformAgentBaseException):
    """Content optimization error"""
    
    def __init__(self, message: str, optimization_type: Optional[str] = None, **kwargs):
        self.optimization_type = optimization_type
        super().__init__(
            message,
            category=ErrorCategory.OPTIMIZATION,
            details={"optimization_type": optimization_type},
            **kwargs
        )


class OptimizationTimeoutException(OptimizationException):
    """Optimization process timed out"""
    
    def __init__(self, timeout_seconds: int, **kwargs):
        super().__init__(
            f"Optimization timed out after {timeout_seconds} seconds",
            error_code="OPTIMIZATION_TIMEOUT",
            details={"timeout_seconds": timeout_seconds},
            **kwargs
        )


# Distribution Exceptions
class DistributionException(PlatformAgentBaseException):
    """Content distribution error"""
    
    def __init__(self, message: str, platforms: Optional[List[str]] = None, **kwargs):
        self.platforms = platforms or []
        super().__init__(
            message,
            category=ErrorCategory.DISTRIBUTION,
            details={"platforms": self.platforms},
            **kwargs
        )


class PartialDistributionException(DistributionException):
    """Content distributed to some platforms but not others"""
    
    def __init__(self, successful_platforms: List[str], failed_platforms: List[str], **kwargs):
        self.successful_platforms = successful_platforms
        self.failed_platforms = failed_platforms
        super().__init__(
            f"Partial distribution success: {len(successful_platforms)} succeeded, {len(failed_platforms)} failed",
            error_code="PARTIAL_DISTRIBUTION",
            details={
                "successful_platforms": successful_platforms,
                "failed_platforms": failed_platforms
            },
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return f"Content published to {len(self.successful_platforms)} platforms. {len(self.failed_platforms)} platforms failed."


# Network Exceptions
class NetworkException(PlatformAgentBaseException):
    """Network-related error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class NetworkTimeoutException(NetworkException):
    """
Network request timed out"""
    
    def __init__(self, timeout_seconds: int, **kwargs):
        super().__init__(
            f"Network request timed out after {timeout_seconds} seconds",
            error_code="NETWORK_TIMEOUT",
            retry_after=30,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "Network request timed out. Please check your internet connection and try again."


class NetworkConnectivityException(NetworkException):
    """No network connectivity"""
    
    def __init__(self, **kwargs):
        super().__init__(
            "No network connectivity",
            error_code="NO_NETWORK_CONNECTIVITY",
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "No internet connection. Please check your network settings and try again."


# Exception Registry for serialization
EXCEPTION_REGISTRY = {
    cls.__name__: cls for cls in [
        PlatformAgentBaseException,
        PlatformConnectionException,
        PlatformAuthenticationException,
        PlatformRateLimitException,
        PlatformAPIException,
        PlatformUnavailableException,
        ContentProcessingException,
        ContentValidationException,
        ContentFormatException,
        ContentSizeException,
        AIProcessingException,
        AIModelLoadException,
        AIProcessingTimeoutException,
        AIResourceException,
        DatabaseException,
        DatabaseConnectionException,
        DatabaseIntegrityException,
        SynchronizationException,
        SyncConflictException,
        SyncLockException,
        ConfigurationException,
        MissingConfigurationException,
        SecurityException,
        AuthenticationException,
        AuthorizationException,
        EncryptionException,
        FileOperationException,
        FileNotFoundException,
        FilePermissionException,
        OptimizationException,
        OptimizationTimeoutException,
        DistributionException,
        PartialDistributionException,
        NetworkException,
        NetworkTimeoutException,
        NetworkConnectivityException
    ]
}


def create_exception_from_dict(error_dict: Dict[str, Any]) -> PlatformAgentBaseException:
    """Create exception instance from dictionary"""
    error_code = error_dict.get("error_code", "PlatformAgentBaseException")
    exception_class = EXCEPTION_REGISTRY.get(error_code, PlatformAgentBaseException)
    
    return exception_class(
        message=error_dict.get("message", "Unknown error"),
        error_code=error_code,
        severity=ErrorSeverity(error_dict.get("severity", "medium")),
        category=ErrorCategory(error_dict.get("category", "platform_api")),
        details=error_dict.get("details", {}),
        user_message=error_dict.get("user_message"),
        recoverable=error_dict.get("recoverable", True),
        retry_after=error_dict.get("retry_after")
    )
