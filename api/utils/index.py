"""Utilities Index - IA Influencer Agent Platform
Main entry point for utility functions and helpers

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""# File and media utilities
from .files import (
    FileManager,
    MediaUploadHandler,
    ContentProcessor,
    FileValidator,
    StorageManager
)

# Common utility functions
from .helpers import (
    generate_unique_id,
    format_datetime,
    sanitize_filename,
    validate_email,
    hash_content,
    compress_data,
    decompress_data
)

# Data processing utilities
from .data_processing import (
    DataTransformer,
    DataValidator,
    DataNormalizer,
    DataAggregator,
    DataExporter
)

# Security utilities
from .security_utils import (
    PasswordManager,
    TokenGenerator,
    EncryptionHelper,
    SecurityValidator,
    AuditLogger
)

# Performance utilities
from .performance import (
    CacheManager,
    RateLimiter,
    PerformanceMonitor,
    ResourceOptimizer,
    MemoryManager
)

# API utilities
from .api_helpers import (
    ResponseFormatter,
    RequestValidator,
    PaginationHelper,
    ErrorHandler,
    APILogger
)

# Content utilities
from .content_helpers import (
    ContentAnalyzer,
    MetadataExtractor,
    ThumbnailGenerator,
    ContentConverter,
    QualityAssessor
)


def get_file_manager():
    """Get file management utilities"""    return FileManager()


def get_security_utils():
    """Get security utility collection"""    return {
        'password_manager': PasswordManager(),
        'token_generator': TokenGenerator(),
        'encryption_helper': EncryptionHelper(),
        'security_validator': SecurityValidator(),
        'audit_logger': AuditLogger()
    }


def get_performance_utils():
    """Get performance utility collection"""    return {
        'cache_manager': CacheManager(),
        'rate_limiter': RateLimiter(),
        'performance_monitor': PerformanceMonitor(),
        'resource_optimizer': ResourceOptimizer(),
        'memory_manager': MemoryManager()
    }


def get_api_utils():
    """Get API utility collection"""    return {
        'response_formatter': ResponseFormatter(),
        'request_validator': RequestValidator(),
        'pagination_helper': PaginationHelper(),
        'error_handler': ErrorHandler(),
        'api_logger': APILogger()
    }


def get_content_utils():
    """Get content utility collection"""    return {
        'content_analyzer': ContentAnalyzer(),
        'metadata_extractor': MetadataExtractor(),
        'thumbnail_generator': ThumbnailGenerator(),
        'content_converter': ContentConverter(),
        'quality_assessor': QualityAssessor()
    }


def get_data_utils():
    """Get data processing utility collection"""    return {
        'transformer': DataTransformer(),
        'validator': DataValidator(),
        'normalizer': DataNormalizer(),
        'aggregator': DataAggregator(),
        'exporter': DataExporter()
    }


def get_all_utilities():
    """Get all utility collections organized by category"""    return {
        'file_manager': get_file_manager(),
        'security': get_security_utils(),
        'performance': get_performance_utils(),
        'api': get_api_utils(),
        'content': get_content_utils(),
        'data': get_data_utils()
    }


__all__ = [
    # File Utilities
    'FileManager',
    'MediaUploadHandler',
    'ContentProcessor',
    'FileValidator',
    'StorageManager',
    
    # Helper Functions
    'generate_unique_id',
    'format_datetime',
    'sanitize_filename',
    'validate_email',
    'hash_content',
    'compress_data',
    'decompress_data',
    
    # Data Processing
    'DataTransformer',
    'DataValidator',
    'DataNormalizer',
    'DataAggregator',
    'DataExporter',
    
    # Security Utilities
    'PasswordManager',
    'TokenGenerator',
    'EncryptionHelper',
    'SecurityValidator',
    'AuditLogger',
    
    # Performance Utilities
    'CacheManager',
    'RateLimiter',
    'PerformanceMonitor',
    'ResourceOptimizer',
    'MemoryManager',
    
    # API Utilities
    'ResponseFormatter',
    'RequestValidator',
    'PaginationHelper',
    'ErrorHandler',
    'APILogger',
    
    # Content Utilities
    'ContentAnalyzer',
    'MetadataExtractor',
    'ThumbnailGenerator',
    'ContentConverter',
    'QualityAssessor',
    
    # Utility Collections
    'get_file_manager',
    'get_security_utils',
    'get_performance_utils',
    'get_api_utils',
    'get_content_utils',
    'get_data_utils',
    'get_all_utilities'
]
