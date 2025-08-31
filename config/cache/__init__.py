"""Cache Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional enterprise-grade caching system with comprehensive configuration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
# Redis Configuration
from .redis_cache_config import (
    RedisCacheConfig,
    RedisConnectionConfig,
    RedisPoolConfig,
    RedisSentinelConfig,
    RedisClusterConfig,
    RedisMode,
    RedisCompressionType,
    DEVELOPMENT_CONFIG as REDIS_DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG as REDIS_PRODUCTION_CONFIG,
    TESTING_CONFIG as REDIS_TESTING_CONFIG
)

# Memcached Configuration
from .memcached_config import (
    MemcachedConfig,
    MemcachedServerConfig,
    MemcachedConnectionConfig,
    MemcachedFailureHandling,
    MemcachedPoolManager,
    MemcachedHashingAlgorithm,
    MemcachedBehavior,
    DEVELOPMENT_CONFIG as MEMCACHED_DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG as MEMCACHED_PRODUCTION_CONFIG,
    TESTING_CONFIG as MEMCACHED_TESTING_CONFIG
)

# Cache Strategies
from .cache_strategies_config import (
    CacheStrategiesConfig,
    BaseCacheStrategy,
    CacheAsideStrategy,
    WriteThroughStrategy,
    CacheKeyConfig,
    CacheMetrics,
    CacheStrategy,
    EvictionPolicy,
    ConsistencyLevel,
    CacheStrategyFactory,
    DEFAULT_CONFIG as STRATEGIES_DEFAULT_CONFIG,
    PRODUCTION_CONFIG as STRATEGIES_PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG as STRATEGIES_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as STRATEGIES_TESTING_CONFIG
)

# Cache Invalidation
from .cache_invalidation_config import (
    CacheInvalidationConfig,
    InvalidationRule,
    InvalidationExecutor,
    InvalidationStrategy,
    InvalidationEvent,
    InvalidationScope,
    InvalidationMetrics,
    DEFAULT_RULES,
    DEFAULT_CONFIG as INVALIDATION_DEFAULT_CONFIG,
    PRODUCTION_CONFIG as INVALIDATION_PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG as INVALIDATION_DEVELOPMENT_CONFIG
)

# Distributed Cache
from .distributed_cache_config import (
    DistributedCacheConfig,
    CacheNode,
    RegionConfig,
    DistributedCacheManager,
    DistributionStrategy,
    ReplicationMode,
    ConsistencyLevel as DistributedConsistencyLevel,
    FailoverPolicy,
    SINGLE_REGION_CONFIG,
    MULTI_REGION_CONFIG,
    HIGH_AVAILABILITY_CONFIG
)

# Cache Warming
from .cache_warming_config import (
    CacheWarmingConfig,
    WarmingRule,
    CacheWarmingEngine,
    AccessPattern,
    WarmingStrategy,
    WarmingTrigger,
    WarmingPriority,
    WarmingMetrics,
    DEFAULT_RULES as WARMING_DEFAULT_RULES,
    DEFAULT_CONFIG as WARMING_DEFAULT_CONFIG,
    PRODUCTION_CONFIG as WARMING_PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG as WARMING_DEVELOPMENT_CONFIG
)

# Cache Metrics
from .cache_metrics_config import (
    CacheMetricsConfig,
    MetricsCollector,
    MetricDefinition,
    AlertRule,
    MetricValue,
    MetricType,
    AggregationMethod,
    AlertSeverity,
    STANDARD_METRICS,
    STANDARD_ALERTS,
    DEFAULT_CONFIG as METRICS_DEFAULT_CONFIG,
    PRODUCTION_CONFIG as METRICS_PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG as METRICS_DEVELOPMENT_CONFIG
)

# Cache Compression
from .cache_compression_config import (
    CacheCompressionConfig,
    CompressionEngine,
    CompressionProfile,
    CompressionMetrics,
    CompressionAlgorithm,
    CompressionLevel,
    ContentType,
    TEXT_PROFILE,
    BINARY_PROFILE,
    LARGE_DATA_PROFILE,
    FAST_PROFILE,
    DEFAULT_CONFIG as COMPRESSION_DEFAULT_CONFIG,
    PRODUCTION_CONFIG as COMPRESSION_PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG as COMPRESSION_DEVELOPMENT_CONFIG
)

# Content Fingerprint Cache - NEW
from .content_fingerprint_cache_config import (
    ContentType as FingerprintContentType,
    FingerprintAlgorithm,
    CacheStorageMode,
    FingerprintCacheSettings,
    ContentFingerprintCacheConfig,
    FingerprintCacheManager,
    DEVELOPMENT_CONFIG as CONTENT_FINGERPRINT_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as CONTENT_FINGERPRINT_TESTING_CONFIG,
    PRODUCTION_CONFIG as CONTENT_FINGERPRINT_PRODUCTION_CONFIG
)

# ML Model Cache - NEW
from .ml_model_cache_config import (
    ModelType,
    ModelFormat,
    CacheStrategy as MLCacheStrategy,
    ModelCacheSettings,
    MLModelCacheConfig,
    MLModelCacheManager,
    DEVELOPMENT_CONFIG as ML_MODEL_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as ML_MODEL_TESTING_CONFIG,
    PRODUCTION_CONFIG as ML_MODEL_PRODUCTION_CONFIG
)

# Platform API Cache - NEW
from .platform_api_cache_config import (
    PlatformType,
    APIEndpointType,
    CacheDataType,
    RateLimitConfig,
    PlatformAPISettings,
    PlatformAPICacheConfig,
    PlatformAPICacheManager,
    DEVELOPMENT_CONFIG as PLATFORM_API_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as PLATFORM_API_TESTING_CONFIG,
    PRODUCTION_CONFIG as PLATFORM_API_PRODUCTION_CONFIG
)

# Multi-Tenant Cache - NEW
from .multi_tenant_cache_config import (
    TenantType,
    IsolationLevel,
    ResourceTier,
    TenantResourceLimits,
    TenantCacheSettings,
    MultiTenantCacheConfig,
    MultiTenantCacheManager,
    DEVELOPMENT_CONFIG as MULTI_TENANT_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as MULTI_TENANT_TESTING_CONFIG,
    PRODUCTION_CONFIG as MULTI_TENANT_PRODUCTION_CONFIG
)

# Content Vector Cache - NEW
from .content_vector_cache_config import (
    VectorType,
    SimilarityMetric,
    IndexType,
    VectorCacheSettings,
    ContentVectorCacheConfig,
    ContentVectorCacheManager,
    DEVELOPMENT_CONFIG as CONTENT_VECTOR_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as CONTENT_VECTOR_TESTING_CONFIG,
    PRODUCTION_CONFIG as CONTENT_VECTOR_PRODUCTION_CONFIG
)

# Revenue Cache - NEW
from .revenue_cache_config import (
    RevenueType,
    CurrencyCode,
    TimePeriod,
    PlatformProvider,
    RevenueCacheSettings,
    RevenueCacheConfig,
    RevenueCacheManager,
    DEVELOPMENT_CONFIG as REVENUE_DEVELOPMENT_CONFIG,
    TESTING_CONFIG as REVENUE_TESTING_CONFIG,
    PRODUCTION_CONFIG as REVENUE_PRODUCTION_CONFIG
)

# Cache Configuration Index and Utilities
from .index import (
    Environment,
    CacheType,
    CacheConfigurationBundle,
    CacheConfigurationFactory,
    CacheConfigurationManager,
    config_manager,
    get_default_config,
    setup_cache_config,
    ENTERPRISE_PRODUCTION_BUNDLE,
    SIMPLE_PRODUCTION_BUNDLE,
    DEVELOPMENT_BUNDLE,
    TESTING_BUNDLE
)

__all__ = [
    # Redis Configuration
    'RedisCacheConfig',
    'RedisConnectionConfig',
    'RedisPoolConfig',
    'RedisSentinelConfig',
    'RedisClusterConfig',
    'RedisMode',
    'RedisCompressionType',
    'REDIS_DEVELOPMENT_CONFIG',
    'REDIS_PRODUCTION_CONFIG',
    'REDIS_TESTING_CONFIG',
    
    # Memcached Configuration
    'MemcachedConfig',
    'MemcachedServerConfig',
    'MemcachedConnectionConfig',
    'MemcachedFailureHandling',
    'MemcachedPoolManager',
    'MemcachedHashingAlgorithm',
    'MemcachedBehavior',
    'MEMCACHED_DEVELOPMENT_CONFIG',
    'MEMCACHED_PRODUCTION_CONFIG',
    'MEMCACHED_TESTING_CONFIG',
    
    # Cache Strategies
    'CacheStrategiesConfig',
    'BaseCacheStrategy',
    'CacheAsideStrategy',
    'WriteThroughStrategy',
    'CacheKeyConfig',
    'CacheMetrics',
    'CacheStrategy',
    'EvictionPolicy',
    'ConsistencyLevel',
    'CacheStrategyFactory',
    'STRATEGIES_DEFAULT_CONFIG',
    'STRATEGIES_PRODUCTION_CONFIG',
    'STRATEGIES_DEVELOPMENT_CONFIG',
    'STRATEGIES_TESTING_CONFIG',
    
    # Cache Invalidation
    'CacheInvalidationConfig',
    'InvalidationRule',
    'InvalidationExecutor',
    'InvalidationStrategy',
    'InvalidationEvent',
    'InvalidationScope',
    'InvalidationMetrics',
    'DEFAULT_RULES',
    'INVALIDATION_DEFAULT_CONFIG',
    'INVALIDATION_PRODUCTION_CONFIG',
    'INVALIDATION_DEVELOPMENT_CONFIG',
    
    # Distributed Cache
    'DistributedCacheConfig',
    'CacheNode',
    'RegionConfig',
    'DistributedCacheManager',
    'DistributionStrategy',
    'ReplicationMode',
    'DistributedConsistencyLevel',
    'FailoverPolicy',
    'SINGLE_REGION_CONFIG',
    'MULTI_REGION_CONFIG',
    'HIGH_AVAILABILITY_CONFIG',
    
    # Cache Warming
    'CacheWarmingConfig',
    'WarmingRule',
    'CacheWarmingEngine',
    'AccessPattern',
    'WarmingStrategy',
    'WarmingTrigger',
    'WarmingPriority',
    'WarmingMetrics',
    'WARMING_DEFAULT_RULES',
    'WARMING_DEFAULT_CONFIG',
    'WARMING_PRODUCTION_CONFIG',
    'WARMING_DEVELOPMENT_CONFIG',
    
    # Cache Metrics
    'CacheMetricsConfig',
    'MetricsCollector',
    'MetricDefinition',
    'AlertRule',
    'MetricValue',
    'MetricType',
    'AggregationMethod',
    'AlertSeverity',
    'STANDARD_METRICS',
    'STANDARD_ALERTS',
    'METRICS_DEFAULT_CONFIG',
    'METRICS_PRODUCTION_CONFIG',
    'METRICS_DEVELOPMENT_CONFIG',
    
    # Cache Compression
    'CacheCompressionConfig',
    'CompressionEngine',
    'CompressionProfile',
    'CompressionMetrics',
    'CompressionAlgorithm',
    'CompressionLevel',
    'ContentType',
    'TEXT_PROFILE',
    'BINARY_PROFILE',
    'LARGE_DATA_PROFILE',
    'FAST_PROFILE',
    'COMPRESSION_DEFAULT_CONFIG',
    'COMPRESSION_PRODUCTION_CONFIG',
    'COMPRESSION_DEVELOPMENT_CONFIG',
    
    # Content Fingerprint Cache - NEW
    'FingerprintContentType',
    'FingerprintAlgorithm',
    'CacheStorageMode',
    'FingerprintCacheSettings',
    'ContentFingerprintCacheConfig',
    'FingerprintCacheManager',
    'CONTENT_FINGERPRINT_DEVELOPMENT_CONFIG',
    'CONTENT_FINGERPRINT_TESTING_CONFIG',
    'CONTENT_FINGERPRINT_PRODUCTION_CONFIG',
    
    # ML Model Cache - NEW
    'ModelType',
    'ModelFormat',
    'MLCacheStrategy',
    'ModelCacheSettings',
    'MLModelCacheConfig',
    'MLModelCacheManager',
    'ML_MODEL_DEVELOPMENT_CONFIG',
    'ML_MODEL_TESTING_CONFIG',
    'ML_MODEL_PRODUCTION_CONFIG',
    
    # Platform API Cache - NEW
    'PlatformType',
    'APIEndpointType',
    'CacheDataType',
    'RateLimitConfig',
    'PlatformAPISettings',
    'PlatformAPICacheConfig',
    'PlatformAPICacheManager',
    'PLATFORM_API_DEVELOPMENT_CONFIG',
    'PLATFORM_API_TESTING_CONFIG',
    'PLATFORM_API_PRODUCTION_CONFIG',
    
    # Multi-Tenant Cache - NEW
    'TenantType',
    'IsolationLevel',
    'ResourceTier',
    'TenantResourceLimits',
    'TenantCacheSettings',
    'MultiTenantCacheConfig',
    'MultiTenantCacheManager',
    'MULTI_TENANT_DEVELOPMENT_CONFIG',
    'MULTI_TENANT_TESTING_CONFIG',
    'MULTI_TENANT_PRODUCTION_CONFIG',
    
    # Content Vector Cache - NEW
    'VectorType',
    'SimilarityMetric',
    'IndexType',
    'VectorCacheSettings',
    'ContentVectorCacheConfig',
    'ContentVectorCacheManager',
    'CONTENT_VECTOR_DEVELOPMENT_CONFIG',
    'CONTENT_VECTOR_TESTING_CONFIG',
    'CONTENT_VECTOR_PRODUCTION_CONFIG',
    
    # Revenue Cache - NEW
    'RevenueType',
    'CurrencyCode',
    'TimePeriod',
    'PlatformProvider',
    'RevenueCacheSettings',
    'RevenueCacheConfig',
    'RevenueCacheManager',
    'REVENUE_DEVELOPMENT_CONFIG',
    'REVENUE_TESTING_CONFIG',
    'REVENUE_PRODUCTION_CONFIG',
    
    # Index and Utilities
    'Environment',
    'CacheType',
    'CacheConfigurationBundle',
    'CacheConfigurationFactory',
    'CacheConfigurationManager',
    'config_manager',
    'get_default_config',
    'setup_cache_config',
    'ENTERPRISE_PRODUCTION_BUNDLE',
    'SIMPLE_PRODUCTION_BUNDLE',
    'DEVELOPMENT_BUNDLE',
    'TESTING_BUNDLE'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'

# Module metadata
__title__ = 'IA-Influencer Agent Cache Configuration'
__description__ = 'Enterprise-grade caching configuration system for IA-Influencer Agent platform'
__url__ = 'https://github.com/Mlaiel/IA-influencer'
__license__ = 'Proprietary - Copyright Fahed Mlaiel'
