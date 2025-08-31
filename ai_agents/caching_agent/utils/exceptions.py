"""Caching Agent Exception Classes

Custom exception hierarchy for the caching agent system,
providing detailed error handling and debugging capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

ATTENTION: Ce code fait partie de la propriété intellectuelle de Fahed Mlaiel.
Toute reproduction, distribution, ou utilisation non autorisée est strictement interdite.
Contact: mlaiel@live.de
"""from typing import Any, Dict, List, Optional


class CachingAgentError(Exception):
    """Base exception class for all caching agent errors."""    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CACHE_ERROR"
        self.details = details or {}
        
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "exception_type": self.__class__.__name__
        }


class CacheConfigurationError(CachingAgentError):
    """Exception raised for cache configuration issues."""    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_value: Optional[Any] = None):
        super().__init__(message, "CONFIG_ERROR", {
            "config_key": config_key,
            "config_value": config_value
        })


class CacheStorageError(CachingAgentError):
    """Exception raised for cache storage issues."""    
    def __init__(self, message: str, storage_type: Optional[str] = None,
                 operation: Optional[str] = None, key: Optional[str] = None):
        super().__init__(message, "STORAGE_ERROR", {
            "storage_type": storage_type,
            "operation": operation,
            "key": key
        })


class CacheConnectionError(CacheStorageError):
    """Exception raised for cache connection issues."""    
    def __init__(self, message: str, storage_type: str, 
                 connection_string: Optional[str] = None):
        super().__init__(message, storage_type, "connection")
        self.details["connection_string"] = connection_string
        self.error_code = "CONNECTION_ERROR"


class CacheSerializationError(CachingAgentError):
    """Exception raised for cache serialization/deserialization issues."""    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 serialization_format: Optional[str] = None):
        super().__init__(message, "SERIALIZATION_ERROR", {
            "data_type": data_type,
            "serialization_format": serialization_format
        })


class CacheCompressionError(CachingAgentError):
    """Exception raised for cache compression/decompression issues."""    
    def __init__(self, message: str, compression_type: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message, "COMPRESSION_ERROR", {
            "compression_type": compression_type,
            "operation": operation
        })


class CacheEncryptionError(CachingAgentError):
    """Exception raised for cache encryption/decryption issues."""    
    def __init__(self, message: str, operation: Optional[str] = None,
                 key_id: Optional[str] = None):
        super().__init__(message, "ENCRYPTION_ERROR", {
            "operation": operation,
            "key_id": key_id
        })


class CacheCapacityError(CachingAgentError):
    """Exception raised when cache capacity limits are exceeded."""    
    def __init__(self, message: str, current_size: Optional[int] = None,
                 max_size: Optional[int] = None, storage_level: Optional[str] = None):
        super().__init__(message, "CAPACITY_ERROR", {
            "current_size": current_size,
            "max_size": max_size,
            "storage_level": storage_level
        })


class CacheEvictionError(CachingAgentError):
    """Exception raised during cache eviction processes."""    
    def __init__(self, message: str, eviction_strategy: Optional[str] = None,
                 failed_keys: Optional[List[str]] = None):
        super().__init__(message, "EVICTION_ERROR", {
            "eviction_strategy": eviction_strategy,
            "failed_keys": failed_keys or []
        })


class CacheInvalidationError(CachingAgentError):
    """Exception raised during cache invalidation processes."""    
    def __init__(self, message: str, invalidation_strategy: Optional[str] = None,
                 failed_keys: Optional[List[str]] = None):
        super().__init__(message, "INVALIDATION_ERROR", {
            "invalidation_strategy": invalidation_strategy,
            "failed_keys": failed_keys or []
        })


class CacheConsistencyError(CachingAgentError):
    """Exception raised when cache consistency issues are detected."""    
    def __init__(self, message: str, inconsistent_keys: Optional[List[str]] = None,
                 storage_levels: Optional[List[str]] = None):
        super().__init__(message, "CONSISTENCY_ERROR", {
            "inconsistent_keys": inconsistent_keys or [],
            "storage_levels": storage_levels or []
        })


class CacheCoordinationError(CachingAgentError):
    """Exception raised for distributed cache coordination issues."""    
    def __init__(self, message: str, node_id: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message, "COORDINATION_ERROR", {
            "node_id": node_id,
            "operation": operation
        })


class CacheOptimizationError(CachingAgentError):
    """Exception raised during cache optimization processes."""    
    def __init__(self, message: str, optimization_type: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None):
        super().__init__(message, "OPTIMIZATION_ERROR", {
            "optimization_type": optimization_type,
            "parameters": parameters or {}
        })


class CacheAnalyticsError(CachingAgentError):
    """Exception raised during cache analytics operations."""    
    def __init__(self, message: str, metric_type: Optional[str] = None,
                 time_range: Optional[str] = None):
        super().__init__(message, "ANALYTICS_ERROR", {
            "metric_type": metric_type,
            "time_range": time_range
        })


class CacheSecurityError(CachingAgentError):
    """Exception raised for cache security violations."""    
    def __init__(self, message: str, security_level: Optional[str] = None,
                 violation_type: Optional[str] = None):
        super().__init__(message, "SECURITY_ERROR", {
            "security_level": security_level,
            "violation_type": violation_type
        })


class CacheValidationError(CachingAgentError):
    """Exception raised for cache data validation issues."""    
    def __init__(self, message: str, validation_type: Optional[str] = None,
                 invalid_fields: Optional[List[str]] = None):
        super().__init__(message, "VALIDATION_ERROR", {
            "validation_type": validation_type,
            "invalid_fields": invalid_fields or []
        })


class CacheTimeoutError(CachingAgentError):
    """Exception raised for cache operation timeouts."""    
    def __init__(self, message: str, operation: Optional[str] = None,
                 timeout_duration: Optional[float] = None):
        super().__init__(message, "TIMEOUT_ERROR", {
            "operation": operation,
            "timeout_duration": timeout_duration
        })


class CacheLockError(CachingAgentError):
    """Exception raised for cache locking issues."""    
    def __init__(self, message: str, lock_key: Optional[str] = None,
                 lock_owner: Optional[str] = None):
        super().__init__(message, "LOCK_ERROR", {
            "lock_key": lock_key,
            "lock_owner": lock_owner
        })


class CacheStrategyError(CachingAgentError):
    """Exception raised for cache strategy issues."""    
    def __init__(self, message: str, strategy_type: Optional[str] = None,
                 strategy_config: Optional[Dict[str, Any]] = None):
        super().__init__(message, "STRATEGY_ERROR", {
            "strategy_type": strategy_type,
            "strategy_config": strategy_config or {}
        })


class CacheMaintenanceError(CachingAgentError):
    """Exception raised during cache maintenance operations."""    
    def __init__(self, message: str, maintenance_type: Optional[str] = None,
                 affected_keys: Optional[List[str]] = None):
        super().__init__(message, "MAINTENANCE_ERROR", {
            "maintenance_type": maintenance_type,
            "affected_keys": affected_keys or []
        })


class CacheVersionError(CachingAgentError):
    """Exception raised for cache version compatibility issues."""    
    def __init__(self, message: str, current_version: Optional[str] = None,
                 required_version: Optional[str] = None):
        super().__init__(message, "VERSION_ERROR", {
            "current_version": current_version,
            "required_version": required_version
        })


class CacheMonitoringError(CachingAgentError):
    """Exception raised for cache monitoring issues."""    
    def __init__(self, message: str, monitor_type: Optional[str] = None,
                 metric_name: Optional[str] = None):
        super().__init__(message, "MONITORING_ERROR", {
            "monitor_type": monitor_type,
            "metric_name": metric_name
        })


# Exception mapping for error categorization
EXCEPTION_CATEGORIES = {
    "configuration": [CacheConfigurationError],
    "storage": [CacheStorageError, CacheConnectionError, CacheCapacityError],
    "data_processing": [CacheSerializationError, CacheCompressionError, 
                       CacheEncryptionError, CacheValidationError],
    "eviction": [CacheEvictionError, CacheInvalidationError],
    "consistency": [CacheConsistencyError, CacheCoordinationError],
    "optimization": [CacheOptimizationError, CacheAnalyticsError],
    "security": [CacheSecurityError],
    "performance": [CacheTimeoutError, CacheLockError],
    "strategy": [CacheStrategyError],
    "maintenance": [CacheMaintenanceError, CacheVersionError],
    "monitoring": [CacheMonitoringError]
}


def categorize_exception(exception: Exception) -> Optional[str]:
    """    Categorize an exception into a specific category.
    
    Args:
        exception: Exception to categorize
        
    Returns:
        Category name or None if not categorized
    """    exception_type = type(exception)
    
    for category, exception_types in EXCEPTION_CATEGORIES.items():
        if exception_type in exception_types:
            return category
    
    return None


def is_retryable_exception(exception: Exception) -> bool:
    """    Check if an exception is retryable.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if the exception is retryable
    """    retryable_types = {
        CacheConnectionError,
        CacheTimeoutError,
        CacheLockError,
        CacheCoordinationError,
        CacheCapacityError  # May be retryable after eviction
    }
    
    return type(exception) in retryable_types


def get_exception_severity(exception: Exception) -> str:
    """    Get the severity level of an exception.
    
    Args:
        exception: Exception to evaluate
        
    Returns:
        Severity level (CRITICAL, HIGH, MEDIUM, LOW)
    """    critical_types = {
        CacheSecurityError,
        CacheConsistencyError,
        CacheConnectionError
    }
    
    high_types = {
        CacheStorageError,
        CacheConfigurationError,
        CacheCoordinationError
    }
    
    medium_types = {
        CacheCapacityError,
        CacheEvictionError,
        CacheInvalidationError,
        CacheOptimizationError
    }
    
    exception_type = type(exception)
    
    if exception_type in critical_types:
        return "CRITICAL"
    elif exception_type in high_types:
        return "HIGH"
    elif exception_type in medium_types:
        return "MEDIUM"
    else:
        return "LOW"
