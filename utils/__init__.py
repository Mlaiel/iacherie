"""
Utils Module - Enterprise-Grade Utility Functions
=================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive utility functions supporting the entire
Ainflue platform ecosystem across all expert domains.

Total Implementations: 18 utility modules covering all 9 expert roles
"""

# Core Infrastructure Utilities (DevOps Expert)
from .performance_monitor import PerformanceMonitor
from .circuit_breaker import CircuitBreaker
from .rate_limiter import RateLimiter
from .notification_service import NotificationService
from .metrics_collector import MetricsCollector
from .health_checker import HealthChecker

# Security Utilities (Security Expert)
from .encryption_utilities import EncryptionUtilities
from .auth_utilities import AuthUtilities

# Database Utilities (DBA Expert)
from .database_utilities import DatabaseUtilities
from .query_builder import QueryBuilder

# AI/ML Utilities (ML Engineer + Lead Dev IA)
from .model_utilities import ModelUtilities
from .ai_orchestrator import AIOrchestrator

# Media Processing (Audio Engineer)
from .audio_utilities import AudioUtilities
from .media_processor import MediaProcessor

# API & Network (Microservices Expert)
from .api_validator import APIValidator
from .rest_client import RestClient

# AI Prompt Engineering (IA Prompt Engineer)
from .prompt_optimizer import PromptOptimizer
from .ai_config import AIConfig

# NEW CRITICAL UTILITIES - January 2025 Implementation
from .data_validator import DataValidator, ValidationResult
from .data_transformer import DataTransformer, TransformationResult
from .input_sanitizer import InputSanitizer, SanitizationResult
from .error_handler import ErrorHandler, ErrorRecord, ErrorSeverity, ErrorCategory

# ADDITIONAL ENTERPRISE UTILITIES - January 2025 Phase 2 Implementation
from .file_utilities import FileUtilities, FileMetadata, FileOperationResult
from .file_validator import FileValidator, FileValidationReport, ValidationLevel
from .test_utilities import TestUtilities, TestResult, TestSuite, PerformanceBenchmark
from .datetime_utilities import DateTimeUtilities, DateTimeRange, BusinessHours
from .video_utilities import VideoUtilities, VideoMetadata, VideoProcessingResult
from .password_utilities import PasswordUtilities, PasswordAnalysis, PasswordPolicy
from .logging_utilities import StructuredLogger, LogContext, LogLevel
from .cache_utilities import CacheUtilities, InMemoryCache, RedisCache

# Expert role coverage verification
EXPERT_ROLES_IMPLEMENTED = {
    'Lead Dev IA': ['AIOrchestrator', 'ModelUtilities', 'DataTransformer', 'DataValidator'],
    'Backend Senior': ['DatabaseUtilities', 'APIValidator', 'RestClient', 'DataTransformer', 'CacheUtilities'],
    'ML Engineer': ['ModelUtilities', 'AIOrchestrator', 'DataTransformer'],
    'DBA': ['DatabaseUtilities', 'QueryBuilder', 'CacheUtilities', 'InMemoryCache', 'RedisCache'],
    'Security': ['EncryptionUtilities', 'AuthUtilities', 'InputSanitizer', 'DataValidator'],
    'Microservices': ['APIValidator', 'RestClient', 'ErrorHandler', 'CacheUtilities'],
    'Audio Engineer': ['AudioUtilities', 'MediaProcessor'],
    'DevOps': ['PerformanceMonitor', 'MetricsCollector', 'HealthChecker', 'CircuitBreaker', 'RateLimiter', 'NotificationService', 'ErrorHandler', 'StructuredLogger'],
    'IA Prompt Engineer': ['PromptOptimizer', 'AIConfig']
}

# NEW IMPLEMENTATIONS COUNT
NEW_UTILITIES_IMPLEMENTED = {
    'data_validator.py': 'Data validation with security checks',
    'data_transformer.py': 'Enterprise data transformation pipeline',
    'input_sanitizer.py': 'Security-focused input sanitization',
    'error_handler.py': 'Comprehensive error management system',
    'logging_utilities.py': 'Structured enterprise logging',
    'cache_utilities.py': 'Multi-backend caching system'
}

__all__ = [
    # Core Infrastructure (DevOps)
    'PerformanceMonitor', 'CircuitBreaker', 'RateLimiter', 'NotificationService',
    'MetricsCollector', 'HealthChecker',
    
    # Security Expert
    'EncryptionUtilities', 'AuthUtilities',
    
    # Database Expert (DBA)
    'DatabaseUtilities', 'QueryBuilder',
    
    # AI/ML Expert (Lead Dev IA + ML Engineer)
    'ModelUtilities', 'AIOrchestrator',
    
    # Media Expert (Audio Engineer)
    'AudioUtilities', 'MediaProcessor',
    
    # API/Network Expert (Microservices)
    'APIValidator', 'RestClient',
    
    # AI Prompt Expert (IA Prompt Engineer)
    'PromptOptimizer', 'AIConfig',
    
    # Expert role tracking
    'EXPERT_ROLES_IMPLEMENTED'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production Ready"
__implementation_coverage__ = "100% - All 9 Expert Roles Covered"