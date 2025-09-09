"""Ainflue Platform Utils Package
Enterprise-grade utility modules for AI-powered content protection and monetization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Core Performance & Monitoring
from .performance_monitor import PerformanceMonitor, RateLimiter, CircuitBreaker
from .notification_service import NotificationService
from .metrics_collector import MetricsCollector, get_global_collector, record_counter, record_gauge, record_timer
from .health_checker import HealthChecker, HealthStatus, get_global_health_checker, health_check

# Data Processing
from .data_validator import DataValidator, ValidationResult, ValidationError, get_global_validator, validate_data
from .data_transformer import DataTransformer, get_global_transformer, transform_data

# Security & Encryption
from .encryption_utilities import (
    EncryptionUtilities, PasswordUtilities, 
    get_encryption_utils, get_password_utils,
    encrypt_data, decrypt_data, hash_password, verify_password
)

# Module exports
__all__ = [
    # Performance & Monitoring
    "PerformanceMonitor",
    "RateLimiter", 
    "CircuitBreaker",
    "NotificationService",
    "MetricsCollector",
    "get_global_collector",
    "record_counter",
    "record_gauge", 
    "record_timer",
    "HealthChecker",
    "HealthStatus",
    "get_global_health_checker",
    "health_check",
    
    # Data Processing
    "DataValidator",
    "ValidationResult",
    "ValidationError", 
    "get_global_validator",
    "validate_data",
    "DataTransformer",
    "get_global_transformer",
    "transform_data",
    
    # Security & Encryption
    "EncryptionUtilities",
    "PasswordUtilities",
    "get_encryption_utils",
    "get_password_utils",
    "encrypt_data",
    "decrypt_data",
    "hash_password",
    "verify_password",
]

# Version info
VERSION_INFO = {
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "description": "Enterprise-grade utilities for Ainflue AI Platform",
    "modules": {
        "core": [
            "PerformanceMonitor", "RateLimiter", "CircuitBreaker", "NotificationService",
            "MetricsCollector", "HealthChecker"
        ],
        "data_processing": [
            "DataValidator", "DataTransformer"
        ],
        "security": [
            "EncryptionUtilities", "PasswordUtilities"
        ],
        "planned": 164,
        "implemented": 10,
        "coverage": "6%"
    }
}