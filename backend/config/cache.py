"""Cache Configuration Module - Consolidated Cache Configs
========================================================

Consolidates all cache-related configurations from:
- config/cache/ (12 files) 

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Optional, List, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json

# ===== CACHE STRATEGIES =====

class CacheStrategy(str, Enum):
    """Cache strategy types"""
    CACHE_ASIDE = "cache_aside"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    REFRESH_AHEAD = "refresh_ahead"

class EvictionPolicy(str, Enum):
    """Cache eviction policies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    RANDOM = "random"

class ConsistencyLevel(str, Enum):
    """Cache consistency levels"""
    STRONG = "strong"
    EVENTUAL = "eventual"
    WEAK = "weak"

# ===== CACHE METRICS =====

class MetricType(str, Enum):
    """Cache metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AggregationMethod(str, Enum):
    """Metric aggregation methods"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    cpu_usage: float = 0.0

@dataclass
class MetricDefinition:
    """Definition for a cache metric"""
    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    aggregation_method: AggregationMethod = AggregationMethod.AVERAGE

@dataclass
class AlertRule:
    """Alert rule for cache metrics"""
    name: str
    metric_name: str
    threshold: float
    comparison: str  # >, <, >=, <=, ==, !=
    severity: AlertSeverity
    description: str
    enabled: bool = True

# ===== COMPRESSION =====

class CompressionAlgorithm(str, Enum):
    """Compression algorithms for cache data"""
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    SNAPPY = "snappy"
    NONE = "none"

class CompressionLevel(int, Enum):
    """Compression levels"""
    FASTEST = 1
    FAST = 3
    BALANCED = 6
    BEST = 9

@dataclass
class CompressionProfile:
    """Compression profile for specific content types"""
    name: str
    algorithm: CompressionAlgorithm
    level: CompressionLevel
    threshold_bytes: int = 1024
    content_types: List[str] = field(default_factory=list)

# ===== CACHE INVALIDATION =====

class InvalidationStrategy(str, Enum):
    """Cache invalidation strategies"""
    TTL_BASED = "ttl_based"
    EVENT_BASED = "event_based"
    MANUAL = "manual"
    DEPENDENCY_BASED = "dependency_based"

class InvalidationScope(str, Enum):
    """Invalidation scope"""
    SINGLE_KEY = "single_key"
    PATTERN = "pattern"
    TAG_BASED = "tag_based"
    GLOBAL = "global"

@dataclass
class InvalidationRule:
    """Cache invalidation rule"""
    name: str
    pattern: str
    strategy: InvalidationStrategy
    scope: InvalidationScope
    priority: int = 0
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)

# ===== CACHE WARMING =====

class WarmingStrategy(str, Enum):
    """Cache warming strategies"""
    PRELOAD = "preload"
    LAZY_LOAD = "lazy_load"
    BACKGROUND_REFRESH = "background_refresh"
    PREDICTIVE = "predictive"

class WarmingTrigger(str, Enum):
    """Cache warming triggers"""
    STARTUP = "startup"
    SCHEDULED = "scheduled"
    THRESHOLD = "threshold"
    EVENT = "event"

class WarmingPriority(int, Enum):
    """Cache warming priorities"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class WarmingRule:
    """Cache warming rule"""
    name: str
    strategy: WarmingStrategy
    trigger: WarmingTrigger
    priority: WarmingPriority
    key_patterns: List[str] = field(default_factory=list)
    schedule: Optional[str] = None  # Cron expression
    enabled: bool = True

# ===== MAIN CONFIGURATION CLASSES =====

@dataclass
class CacheKeyConfig:
    """Cache key configuration"""
    prefix: str = "ia_influencer"
    separator: str = ":"
    max_length: int = 250
    encoding: str = "utf-8"
    hash_long_keys: bool = True
    case_sensitive: bool = True

@dataclass
class CacheStrategiesConfig:
    """Cache strategies configuration"""
    default_strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    default_ttl: int = 3600  # 1 hour
    max_ttl: int = 86400  # 24 hours
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    key_config: CacheKeyConfig = field(default_factory=CacheKeyConfig)

@dataclass
class CacheMetricsConfig:
    """Cache metrics configuration"""
    enabled: bool = True
    collection_interval: int = 60  # seconds
    retention_period: int = 604800  # 7 days
    metrics: List[MetricDefinition] = field(default_factory=list)
    alerts: List[AlertRule] = field(default_factory=list)

@dataclass
class CacheCompressionConfig:
    """Cache compression configuration"""
    enabled: bool = False
    default_algorithm: CompressionAlgorithm = CompressionAlgorithm.LZ4
    default_level: CompressionLevel = CompressionLevel.BALANCED
    threshold_bytes: int = 1024
    profiles: List[CompressionProfile] = field(default_factory=list)

@dataclass
class CacheInvalidationConfig:
    """Cache invalidation configuration"""
    enabled: bool = True
    default_strategy: InvalidationStrategy = InvalidationStrategy.TTL_BASED
    batch_size: int = 100
    retry_attempts: int = 3
    rules: List[InvalidationRule] = field(default_factory=list)

@dataclass
class CacheWarmingConfig:
    """Cache warming configuration"""
    enabled: bool = True
    max_concurrent_jobs: int = 5
    timeout_seconds: int = 300
    default_strategy: WarmingStrategy = WarmingStrategy.LAZY_LOAD
    rules: List[WarmingRule] = field(default_factory=list)

# ===== SPECIALIZED CACHE CONFIGS =====

@dataclass
class ContentFingerprintCacheConfig:
    """Content fingerprint cache configuration"""
    enabled: bool = True
    ttl: int = 86400  # 24 hours
    max_fingerprints: int = 1000000  # 1M fingerprints
    compression_enabled: bool = True
    storage_mode: str = "memory_with_persistence"

@dataclass
class MLModelCacheConfig:
    """ML model cache configuration"""
    enabled: bool = True
    model_ttl: int = 3600  # 1 hour
    prediction_ttl: int = 300  # 5 minutes
    max_model_size: int = 1073741824  # 1GB
    warm_models_on_startup: bool = True

@dataclass
class PlatformAPICacheConfig:
    """Platform API cache configuration"""
    enabled: bool = True
    default_ttl: int = 600  # 10 minutes
    rate_limit_cache_ttl: int = 3600  # 1 hour
    max_cached_responses: int = 10000
    compress_responses: bool = True

@dataclass
class RevenueCacheConfig:
    """Revenue data cache configuration"""
    enabled: bool = True
    revenue_ttl: int = 300  # 5 minutes
    analytics_ttl: int = 3600  # 1 hour
    historical_data_ttl: int = 86400  # 24 hours
    cache_aggregations: bool = True

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_cache_config() -> Dict[str, Any]:
    """Get development cache configuration"""
    return {
        "strategies": CacheStrategiesConfig(
            default_ttl=300,  # 5 minutes
            max_ttl=3600     # 1 hour
        ),
        "metrics": CacheMetricsConfig(
            enabled=True,
            collection_interval=30
        ),
        "compression": CacheCompressionConfig(
            enabled=False
        ),
        "invalidation": CacheInvalidationConfig(
            enabled=True
        ),
        "warming": CacheWarmingConfig(
            enabled=False
        )
    }

def get_production_cache_config() -> Dict[str, Any]:
    """Get production cache configuration"""
    return {
        "strategies": CacheStrategiesConfig(
            default_ttl=3600,   # 1 hour
            max_ttl=86400      # 24 hours
        ),
        "metrics": CacheMetricsConfig(
            enabled=True,
            collection_interval=60
        ),
        "compression": CacheCompressionConfig(
            enabled=True,
            default_algorithm=CompressionAlgorithm.LZ4
        ),
        "invalidation": CacheInvalidationConfig(
            enabled=True
        ),
        "warming": CacheWarmingConfig(
            enabled=True,
            max_concurrent_jobs=10
        )
    }

def get_testing_cache_config() -> Dict[str, Any]:
    """Get testing cache configuration"""
    return {
        "strategies": CacheStrategiesConfig(
            default_ttl=60,    # 1 minute
            max_ttl=300       # 5 minutes
        ),
        "metrics": CacheMetricsConfig(
            enabled=False
        ),
        "compression": CacheCompressionConfig(
            enabled=False
        ),
        "invalidation": CacheInvalidationConfig(
            enabled=True
        ),
        "warming": CacheWarmingConfig(
            enabled=False
        )
    }

# ===== CACHE CONFIGURATION FACTORY =====

class CacheConfigurationFactory:
    """Factory for creating cache configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> Dict[str, Any]:
        """Create cache configuration for environment"""
        if environment.lower() == "production":
            return get_production_cache_config()
        elif environment.lower() == "testing":
            return get_testing_cache_config()
        else:
            return get_development_cache_config()
    
    @staticmethod
    def create_specialized_config(cache_type: str) -> Dict[str, Any]:
        """Create specialized cache configuration"""
        configs = {
            "fingerprint": ContentFingerprintCacheConfig(),
            "ml_model": MLModelCacheConfig(),
            "platform_api": PlatformAPICacheConfig(),
            "revenue": RevenueCacheConfig()
        }
        return configs.get(cache_type, {})

# Export all cache configurations
__all__ = [
    # Strategy Enums
    "CacheStrategy",
    "EvictionPolicy", 
    "ConsistencyLevel",
    
    # Metric Enums
    "MetricType",
    "AggregationMethod",
    "AlertSeverity",
    
    # Compression Enums
    "CompressionAlgorithm",
    "CompressionLevel",
    
    # Invalidation Enums
    "InvalidationStrategy",
    "InvalidationScope",
    
    # Warming Enums
    "WarmingStrategy",
    "WarmingTrigger",
    "WarmingPriority",
    
    # Configuration Classes
    "CacheKeyConfig",
    "CacheStrategiesConfig",
    "CacheMetricsConfig", 
    "CacheCompressionConfig",
    "CacheInvalidationConfig",
    "CacheWarmingConfig",
    
    # Specialized Cache Configs
    "ContentFingerprintCacheConfig",
    "MLModelCacheConfig",
    "PlatformAPICacheConfig",
    "RevenueCacheConfig",
    
    # Data Classes
    "CacheMetrics",
    "MetricDefinition",
    "AlertRule",
    "CompressionProfile",
    "InvalidationRule", 
    "WarmingRule",
    
    # Factory and Functions
    "CacheConfigurationFactory",
    "get_development_cache_config",
    "get_production_cache_config",
    "get_testing_cache_config"
]