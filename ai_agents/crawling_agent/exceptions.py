"""
Crawling Agent Exceptions - Specialized Error Handling & Recovery

Advanced exception handling system with categorized errors, recovery strategies,
and detailed error context for debugging and monitoring.

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

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import traceback
import json


class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ErrorCategory(Enum):
    """Categories of errors for better organization"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    PARSING = "parsing"
    RATE_LIMITING = "rate_limiting"
    CONTENT_PROCESSING = "content_processing"
    SIMILARITY_DETECTION = "similarity_detection"
    SURVEILLANCE = "surveillance"
    PLATFORM_API = "platform_api"
    DATABASE = "database"
    STORAGE = "storage"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY_IMMEDIATE = "retry_immediate"
    RETRY_EXPONENTIAL_BACKOFF = "retry_exponential_backoff"
    RETRY_AFTER_DELAY = "retry_after_delay"
    SKIP_AND_CONTINUE = "skip_and_continue"
    FALLBACK_METHOD = "fallback_method"
    ABORT_OPERATION = "abort_operation"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    SWITCH_PROXY = "switch_proxy"
    USE_CACHE = "use_cache"


class CrawlingAgentException(Exception):
    """
    Base exception class for all crawling agent errors
    
    Provides comprehensive error context and recovery information
    """
    
    def __init__(self, 
                 message: str,
                 error_code: str = "GENERAL_ERROR",
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.NETWORK,
                 recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.recovery_strategy = recovery_strategy
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        self.traceback_info = traceback.format_exc() if original_exception else None
        
        # Generate unique error ID for tracking
        self.error_id = f"{category.value}_{error_code}_{int(self.timestamp.timestamp())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/monitoring"""
        return {
            "error_id": self.error_id,
            "message": self.message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "recovery_strategy": self.recovery_strategy.value,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "traceback": self.traceback_info
        }
    
    def to_json(self) -> str:
        """Convert exception to JSON string"""
        return json.dumps(self.to_dict(), default=str, indent=2)


class CrawlingError(CrawlingAgentException):
    """Generic crawling operation errors"""
    
    def __init__(self, message: str, url: str = "", **kwargs):
        super().__init__(
            message,
            error_code="CRAWLING_ERROR",
            category=ErrorCategory.NETWORK,
            context={"url": url},
            **kwargs
        )


class NetworkError(CrawlingAgentException):
    """Network connectivity and communication errors"""
    
    def __init__(self, message: str, url: str = "", status_code: int = 0, **kwargs):
        super().__init__(
            message,
            error_code="NETWORK_ERROR", 
            category=ErrorCategory.NETWORK,
            recovery_strategy=RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
            context={"url": url, "status_code": status_code},
            **kwargs
        )


class TimeoutError(CrawlingAgentException):
    """Request timeout errors"""
    
    def __init__(self, message: str, timeout_seconds: int = 0, **kwargs):
        super().__init__(
            message,
            error_code="TIMEOUT_ERROR",
            category=ErrorCategory.NETWORK,
            recovery_strategy=RecoveryStrategy.RETRY_AFTER_DELAY,
            context={"timeout_seconds": timeout_seconds},
            **kwargs
        )


class AuthenticationError(CrawlingAgentException):
    """API authentication failures"""
    
    def __init__(self, message: str, platform: str = "", api_key_hash: str = "", **kwargs):
        super().__init__(
            message,
            error_code="AUTH_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            recovery_strategy=RecoveryStrategy.ESCALATE_TO_HUMAN,
            context={"platform": platform, "api_key_hash": api_key_hash},
            **kwargs
        )


class AuthorizationError(CrawlingAgentException):
    """API authorization/permission errors"""
    
    def __init__(self, message: str, platform: str = "", required_permission: str = "", **kwargs):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHORIZATION,
            recovery_strategy=RecoveryStrategy.ESCALATE_TO_HUMAN,
            context={"platform": platform, "required_permission": required_permission},
            **kwargs
        )


class RateLimitError(CrawlingAgentException):
    """Rate limiting errors from APIs or servers"""
    
    def __init__(self, message: str, platform: str = "", limit_reset_time: int = 0, **kwargs):
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            category=ErrorCategory.RATE_LIMITING,
            recovery_strategy=RecoveryStrategy.RETRY_AFTER_DELAY,
            context={"platform": platform, "reset_time": limit_reset_time},
            **kwargs
        )


class ValidationError(CrawlingAgentException):
    """Data validation and format errors"""
    
    def __init__(self, message: str, field_name: str = "", invalid_value: str = "", **kwargs):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            recovery_strategy=RecoveryStrategy.SKIP_AND_CONTINUE,
            context={"field_name": field_name, "invalid_value": invalid_value},
            **kwargs
        )


class ParsingError(CrawlingAgentException):
    """HTML, JSON, or other content parsing errors"""
    
    def __init__(self, message: str, content_type: str = "", parser_used: str = "", **kwargs):
        super().__init__(
            message,
            error_code="PARSING_ERROR",
            category=ErrorCategory.PARSING,
            recovery_strategy=RecoveryStrategy.FALLBACK_METHOD,
            context={"content_type": content_type, "parser_used": parser_used},
            **kwargs
        )


class ContentProcessingError(CrawlingAgentException):
    """Content analysis and processing errors"""
    
    def __init__(self, message: str, content_id: str = "", processing_stage: str = "", **kwargs):
        super().__init__(
            message,
            error_code="CONTENT_PROCESSING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            recovery_strategy=RecoveryStrategy.FALLBACK_METHOD,
            context={"content_id": content_id, "processing_stage": processing_stage},
            **kwargs
        )


class SimilarityDetectionError(CrawlingAgentException):
    """Content similarity detection and comparison errors"""
    
    def __init__(self, message: str, content_id1: str = "", content_id2: str = "", **kwargs):
        super().__init__(
            message,
            error_code="SIMILARITY_ERROR",
            category=ErrorCategory.SIMILARITY_DETECTION,
            recovery_strategy=RecoveryStrategy.FALLBACK_METHOD,
            context={"content_id1": content_id1, "content_id2": content_id2},
            **kwargs
        )


class SurveillanceError(CrawlingAgentException):
    """Surveillance and monitoring system errors"""
    
    def __init__(self, message: str, target_id: str = "", surveillance_type: str = "", **kwargs):
        super().__init__(
            message,
            error_code="SURVEILLANCE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SURVEILLANCE,
            recovery_strategy=RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
            context={"target_id": target_id, "surveillance_type": surveillance_type},
            **kwargs
        )


class PlatformAPIError(CrawlingAgentException):
    """Platform-specific API errors"""
    
    def __init__(self, message: str, platform: str = "", api_endpoint: str = "", 
                 api_response_code: int = 0, **kwargs):
        super().__init__(
            message,
            error_code="PLATFORM_API_ERROR",
            category=ErrorCategory.PLATFORM_API,
            recovery_strategy=RecoveryStrategy.FALLBACK_METHOD,
            context={
                "platform": platform, 
                "api_endpoint": api_endpoint,
                "api_response_code": api_response_code
            },
            **kwargs
        )


class DatabaseError(CrawlingAgentException):
    """Database connection and operation errors"""
    
    def __init__(self, message: str, operation: str = "", table: str = "", **kwargs):
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            recovery_strategy=RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF,
            context={"operation": operation, "table": table},
            **kwargs
        )


class StorageError(CrawlingAgentException):
    """File storage and retrieval errors"""
    
    def __init__(self, message: str, storage_backend: str = "", file_path: str = "", **kwargs):
        super().__init__(
            message,
            error_code="STORAGE_ERROR",
            category=ErrorCategory.STORAGE,
            recovery_strategy=RecoveryStrategy.FALLBACK_METHOD,
            context={"storage_backend": storage_backend, "file_path": file_path},
            **kwargs
        )


class ConfigurationError(CrawlingAgentException):
    """Configuration and setup errors"""
    
    def __init__(self, message: str, config_key: str = "", config_value: str = "", **kwargs):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIGURATION,
            recovery_strategy=RecoveryStrategy.ABORT_OPERATION,
            context={"config_key": config_key, "config_value": config_value},
            **kwargs
        )


class SecurityError(CrawlingAgentException):
    """Security and encryption errors"""
    
    def __init__(self, message: str, security_context: str = "", **kwargs):
        super().__init__(
            message,
            error_code="SECURITY_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            recovery_strategy=RecoveryStrategy.ESCALATE_TO_HUMAN,
            context={"security_context": security_context},
            **kwargs
        )


class ResourceExhaustionError(CrawlingAgentException):
    """System resource exhaustion errors"""
    
    def __init__(self, message: str, resource_type: str = "", usage_percent: float = 0, **kwargs):
        super().__init__(
            message,
            error_code="RESOURCE_EXHAUSTION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.RESOURCE_EXHAUSTION,
            recovery_strategy=RecoveryStrategy.RETRY_AFTER_DELAY,
            context={"resource_type": resource_type, "usage_percent": usage_percent},
            **kwargs
        )


class ProxyError(CrawlingAgentException):
    """Proxy connection and configuration errors"""
    
    def __init__(self, message: str, proxy_url: str = "", proxy_type: str = "", **kwargs):
        super().__init__(
            message,
            error_code="PROXY_ERROR",
            category=ErrorCategory.NETWORK,
            recovery_strategy=RecoveryStrategy.SWITCH_PROXY,
            context={"proxy_url": proxy_url, "proxy_type": proxy_type},
            **kwargs
        )


class AlertError(CrawlingAgentException):
    """Alert system and notification errors"""
    
    def __init__(self, message: str, alert_type: str = "", recipient: str = "", **kwargs):
        super().__init__(
            message,
            error_code="ALERT_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SURVEILLANCE,
            recovery_strategy=RecoveryStrategy.FALLBACK_METHOD,
            context={"alert_type": alert_type, "recipient": recipient},
            **kwargs
        )


class CacheError(CrawlingAgentException):
    """Caching system errors"""
    
    def __init__(self, message: str, cache_key: str = "", cache_backend: str = "", **kwargs):
        super().__init__(
            message,
            error_code="CACHE_ERROR",
            category=ErrorCategory.STORAGE,
            recovery_strategy=RecoveryStrategy.USE_CACHE,
            context={"cache_key": cache_key, "cache_backend": cache_backend},
            **kwargs
        )


class ContentViolationError(CrawlingAgentException):
    """Content policy violation detection errors"""
    
    def __init__(self, message: str, content_id: str = "", violation_type: str = "", 
                 similarity_score: float = 0, **kwargs):
        super().__init__(
            message,
            error_code="CONTENT_VIOLATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SURVEILLANCE,
            recovery_strategy=RecoveryStrategy.ESCALATE_TO_HUMAN,
            context={
                "content_id": content_id,
                "violation_type": violation_type,
                "similarity_score": similarity_score
            },
            **kwargs
        )


# Exception mapping for common HTTP status codes
HTTP_STATUS_EXCEPTIONS = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: CrawlingError,
    408: TimeoutError,
    429: RateLimitError,
    500: NetworkError,
    502: NetworkError,
    503: NetworkError,
    504: TimeoutError
}


def create_exception_from_http_status(status_code: int, message: str, **kwargs) -> CrawlingAgentException:
    """
    Create appropriate exception based on HTTP status code
    """
    exception_class = HTTP_STATUS_EXCEPTIONS.get(status_code, NetworkError)
    return exception_class(message, **kwargs)


def handle_exception_with_recovery(exception: CrawlingAgentException, 
                                 recovery_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Handle exception based on its recovery strategy
    
    Returns recovery action details
    """
    recovery_context = recovery_context or {}
    
    recovery_action = {
        "action": exception.recovery_strategy.value,
        "error_id": exception.error_id,
        "timestamp": datetime.now().isoformat(),
        "context": recovery_context
    }
    
    if exception.recovery_strategy == RecoveryStrategy.RETRY_EXPONENTIAL_BACKOFF:
        retry_count = recovery_context.get("retry_count", 0)
        recovery_action["delay_seconds"] = min(2 ** retry_count, 300)  # Max 5 minutes
        recovery_action["max_retries"] = 5
    
    elif exception.recovery_strategy == RecoveryStrategy.RETRY_AFTER_DELAY:
        recovery_action["delay_seconds"] = 60  # 1 minute default
    
    elif exception.recovery_strategy == RecoveryStrategy.SWITCH_PROXY:
        recovery_action["switch_proxy"] = True
        recovery_action["blacklist_current"] = True
    
    elif exception.recovery_strategy == RecoveryStrategy.ESCALATE_TO_HUMAN:
        recovery_action["alert_administrators"] = True
        recovery_action["priority"] = "high"
    
    return recovery_action


# Export all exception classes
__all__ = [
    'ErrorSeverity',
    'ErrorCategory', 
    'RecoveryStrategy',
    'CrawlingAgentException',
    'CrawlingError',
    'NetworkError',
    'TimeoutError',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError',
    'ValidationError',
    'ParsingError',
    'ContentProcessingError',
    'SimilarityDetectionError',
    'SurveillanceError',
    'PlatformAPIError',
    'DatabaseError',
    'StorageError',
    'ConfigurationError',
    'SecurityError',
    'ResourceExhaustionError',
    'ProxyError',
    'AlertError',
    'CacheError',
    'ContentViolationError',
    'create_exception_from_http_status',
    'handle_exception_with_recovery'
]
