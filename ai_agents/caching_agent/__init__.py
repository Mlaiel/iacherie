"""Caching Agent Module for IA-Influencer-Agent

This module provides a comprehensive, enterprise-grade caching system
designed specifically for the IA-Influencer-Agent platform.

Features:
- Multi-layer caching (L1-L4: Memory, Redis, Database, S3/CDN)
- Intelligent cache strategies (LRU, TTL, Adaptive, Geographic, Content-aware)
- Advanced invalidation mechanisms
- Performance analytics and monitoring
- Distributed cache coordination
- AI-driven optimization
- Comprehensive security features

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

ATTENTION: Ce code fait partie de la propriété intellectuelle de Fahed Mlaiel.
Toute reproduction, distribution, ou utilisation non autorisée est strictement interdite.
Contact: mlaiel@live.de

License: Proprietary - All rights reserved
Warning: Unauthorized copying, distribution, or use is prohibited by law.
"""
# Core cache manager
from .manager import CachingManager, CacheConfig, CachePriority

# Cache strategies
from .strategies import (
    CacheStrategy,
    LRUStrategy,
    TTLStrategy,
    AdaptiveStrategy,
    GeographicStrategy,
    ContentAwareStrategy
)

# Storage implementations
from .storage import (
    CacheStorage,
    MemoryStorage,
    RedisStorage,
    DatabaseStorage,
    HybridStorage,
    StorageLevel,
    CompressionType
)

# Invalidation system
from .invalidation import (
    InvalidationEngine,
    InvalidationStrategy,
    TTLInvalidationStrategy,
    TagBasedInvalidationStrategy,
    TimeBasedInvalidationStrategy,
    EventDrivenInvalidationStrategy
)

# Analytics and monitoring
from .analytics import (
    CacheAnalytics,
    PerformanceMetrics,
    CacheReport
)

# Distributed coordination
from .coordinator import (
    CacheCoordinator,
    NodeInfo,
    ConsistentHashRing
)

# AI optimization
from .optimizer import (
    CacheOptimizer,
    OptimizationRecommendation,
    ModelType
)

# Module organization
from .index import (
    get_cache_manager,
    get_strategy_by_name,
    get_storage_by_level,
    create_caching_system
)

# Configuration and utilities
from .config import (
    DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG,
    HIGH_PERFORMANCE_CONFIG,
    AUDIO_PROCESSING_CONFIG,
    SEO_OPTIMIZATION_CONFIG,
    COLLABORATION_CONFIG,
    SECURITY_ENHANCED_CONFIG,
    CONFIGURATION_TEMPLATES,
    get_config_for_environment,
    create_custom_config,
    get_ttl_for_content_type,
    get_priority_for_content_type
)

# Exception classes
from .exceptions import (
    CachingAgentError,
    CacheConfigurationError,
    CacheStorageError,
    CacheConnectionError,
    CacheSerializationError,
    CacheCompressionError,
    CacheEncryptionError,
    CacheCapacityError,
    CacheEvictionError,
    CacheInvalidationError,
    CacheConsistencyError,
    CacheCoordinationError,
    CacheOptimizationError,
    CacheAnalyticsError,
    CacheSecurityError,
    CacheValidationError,
    CacheTimeoutError,
    CacheLockError,
    CacheStrategyError,
    CacheMaintenanceError,
    CacheVersionError,
    CacheMonitoringError,
    categorize_exception,
    is_retryable_exception,
    get_exception_severity
)

# Utility classes and functions
from .utils import (
    CacheKey,
    SerializationManager,
    CompressionManager,
    TimingUtilities,
    SizeUtilities,
    HashUtilities,
    ValidationUtilities,
    AsyncUtilities,
    ThreadUtilities,
    ThreadSafeCounter,
    PerformanceTimer,
    ConfigurationValidator,
    serialization_manager,
    compression_manager,
    timing_utils,
    size_utils,
    hash_utils,
    validation_utils,
    async_utils,
    thread_utils,
    config_validator
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

# Export all public classes and functions
__all__ = [
    # Core components
    'CachingManager',
    'CacheConfig',
    'CachePriority',
    
    # Strategies
    'CacheStrategy',
    'LRUStrategy',
    'TTLStrategy',
    'AdaptiveStrategy',
    'GeographicStrategy',
    'ContentAwareStrategy',
    
    # Storage
    'CacheStorage',
    'MemoryStorage',
    'RedisStorage',
    'DatabaseStorage',
    'HybridStorage',
    'StorageLevel',
    'CompressionType',
    
    # Invalidation
    'InvalidationEngine',
    'InvalidationStrategy',
    'TTLInvalidationStrategy',
    'TagBasedInvalidationStrategy',
    'TimeBasedInvalidationStrategy',
    'EventDrivenInvalidationStrategy',
    
    # Analytics
    'CacheAnalytics',
    'PerformanceMetrics',
    'CacheReport',
    
    # Coordination
    'CacheCoordinator',
    'NodeInfo',
    'ConsistentHashRing',
    
    # Optimization
    'CacheOptimizer',
    'OptimizationRecommendation',
    'ModelType',
    
    # Factory functions
    'get_cache_manager',
    'get_strategy_by_name',
    'get_storage_by_level',
    'create_caching_system',
    
    # Configuration
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG',
    'HIGH_PERFORMANCE_CONFIG',
    'AUDIO_PROCESSING_CONFIG',
    'SEO_OPTIMIZATION_CONFIG',
    'COLLABORATION_CONFIG',
    'SECURITY_ENHANCED_CONFIG',
    'CONFIGURATION_TEMPLATES',
    'get_config_for_environment',
    'create_custom_config',
    'get_ttl_for_content_type',
    'get_priority_for_content_type',
    
    # Exceptions
    'CachingAgentError',
    'CacheConfigurationError',
    'CacheStorageError',
    'CacheConnectionError',
    'CacheSerializationError',
    'CacheCompressionError',
    'CacheEncryptionError',
    'CacheCapacityError',
    'CacheEvictionError',
    'CacheInvalidationError',
    'CacheConsistencyError',
    'CacheCoordinationError',
    'CacheOptimizationError',
    'CacheAnalyticsError',
    'CacheSecurityError',
    'CacheValidationError',
    'CacheTimeoutError',
    'CacheLockError',
    'CacheStrategyError',
    'CacheMaintenanceError',
    'CacheVersionError',
    'CacheMonitoringError',
    'categorize_exception',
    'is_retryable_exception',
    'get_exception_severity',
    
    # Utilities
    'CacheKey',
    'SerializationManager',
    'CompressionManager',
    'TimingUtilities',
    'SizeUtilities',
    'HashUtilities',
    'ValidationUtilities',
    'AsyncUtilities',
    'ThreadUtilities',
    'ThreadSafeCounter',
    'PerformanceTimer',
    'ConfigurationValidator',
    'serialization_manager',
    'compression_manager',
    'timing_utils',
    'size_utils',
    'hash_utils',
    'validation_utils',
    'async_utils',
    'thread_utils',
    'config_validator'
]
