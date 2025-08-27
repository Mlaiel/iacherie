"""
Caching Agent Index - Module Organization and Exports

Central index file providing organized access to all caching agent components
with clear categorization and professional module structure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action.
"""

# Core Management Components
from .manager import CachingManager, CacheConfig, CacheStats, CacheEntry

# Storage Layer Components
from .storage import (
    CacheStorage,
    MemoryStorage,
    RedisStorage,
    DatabaseStorage,
    HybridStorage,
    StorageLevel,
    StorageConfig,
    StorageMetrics,
    CompressionType
)

# Strategy Components
from .strategies import (
    CacheStrategy,
    LRUStrategy,
    TTLStrategy,
    AdaptiveStrategy,
    GeographicStrategy,
    ContentAwareStrategy,
    AccessPattern,
    EvictionCandidate,
    EvictionReason
)

# Invalidation Components
from .invalidation import (
    InvalidationEngine,
    InvalidationStrategy,
    TTLInvalidationStrategy,
    TagBasedInvalidation,
    TimeBasedInvalidation,
    EventDrivenInvalidation,
    InvalidationEvent,
    InvalidationRule,
    InvalidationTrigger,
    InvalidationPriority
)

# Analytics Components
from .analytics import (
    CacheAnalytics,
    CacheMetric,
    PerformanceReport,
    AlertRule,
    MetricType,
    AnalyticsPeriod
)

# Coordination Components
from .coordinator import (
    DistributedCacheCoordinator,
    CacheNode,
    ConsistencyHash,
    CoordinationMessage,
    NodeStatus,
    CoordinationEvent
)

# Optimization Components
from .optimizer import (
    CacheOptimizer,
    OptimizationRecommendation,
    OptimizationResult,
    CachePrediction,
    OptimizationType,
    OptimizationPriority
)

# Version and Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Multi-Layer Caching System for IA-Influencer-Agent Platform"

# Module Categories for Better Organization
CORE_COMPONENTS = [
    "CachingManager",
    "CacheConfig", 
    "CacheStats",
    "CacheEntry"
]

STORAGE_COMPONENTS = [
    "CacheStorage",
    "MemoryStorage",
    "RedisStorage",
    "DatabaseStorage", 
    "HybridStorage",
    "StorageLevel",
    "StorageConfig"
]

STRATEGY_COMPONENTS = [
    "CacheStrategy",
    "LRUStrategy",
    "TTLStrategy",
    "AdaptiveStrategy",
    "GeographicStrategy",
    "ContentAwareStrategy"
]

INVALIDATION_COMPONENTS = [
    "InvalidationEngine",
    "InvalidationStrategy",
    "TTLInvalidationStrategy",
    "TagBasedInvalidation",
    "TimeBasedInvalidation",
    "EventDrivenInvalidation"
]

ANALYTICS_COMPONENTS = [
    "CacheAnalytics",
    "PerformanceReport",
    "CacheMetric",
    "AlertRule"
]

COORDINATION_COMPONENTS = [
    "DistributedCacheCoordinator",
    "CacheNode",
    "ConsistencyHash",
    "CoordinationMessage"
]

OPTIMIZATION_COMPONENTS = [
    "CacheOptimizer",
    "OptimizationRecommendation",
    "OptimizationResult",
    "CachePrediction"
]

# Complete exports list
__all__ = (
    CORE_COMPONENTS +
    STORAGE_COMPONENTS + 
    STRATEGY_COMPONENTS +
    INVALIDATION_COMPONENTS +
    ANALYTICS_COMPONENTS +
    COORDINATION_COMPONENTS +
    OPTIMIZATION_COMPONENTS + [
        # Enums and utility classes
        "StorageLevel",
        "CompressionType", 
        "EvictionReason",
        "InvalidationTrigger",
        "InvalidationPriority",
        "NodeStatus",
        "CoordinationEvent",
        "MetricType",
        "AnalyticsPeriod",
        "OptimizationType",
        "OptimizationPriority"
    ]
)

def get_component_info() -> dict:
    """
    Get comprehensive information about all caching agent components.
    
    Returns:
        Dictionary containing component categories and descriptions
    """
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "core": {
                "description": "Main cache management and configuration components",
                "classes": CORE_COMPONENTS
            },
            "storage": {
                "description": "Multi-layer storage implementations and configurations",
                "classes": STORAGE_COMPONENTS
            },
            "strategies": {
                "description": "Intelligent caching and eviction strategies",
                "classes": STRATEGY_COMPONENTS
            },
            "invalidation": {
                "description": "Advanced cache invalidation mechanisms",
                "classes": INVALIDATION_COMPONENTS
            },
            "analytics": {
                "description": "Performance monitoring and analytics systems",
                "classes": ANALYTICS_COMPONENTS
            },
            "coordination": {
                "description": "Distributed cache coordination and synchronization",
                "classes": COORDINATION_COMPONENTS
            },
            "optimization": {
                "description": "AI-driven cache performance optimization",
                "classes": OPTIMIZATION_COMPONENTS
            }
        },
        "total_components": len(__all__),
        "supported_features": [
            "Multi-layer cache hierarchy (L1-L4)",
            "Intelligent eviction strategies",
            "Distributed coordination", 
            "Real-time analytics",
            "AI-driven optimization",
            "Event-driven invalidation",
            "Geographic awareness",
            "Content-type optimization",
            "Performance forecasting",
            "Automated tuning"
        ]
    }

def create_caching_manager(config: dict = None) -> CachingManager:
    """
    Factory function to create a configured CachingManager instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured CachingManager instance
    """
    if config is None:
        config = {}
        
    cache_config = CacheConfig(
        max_memory_size=config.get('max_memory_size', 1024*1024*1024),  # 1GB default
        redis_url=config.get('redis_url', 'redis://localhost:6379'),
        database_url=config.get('database_url', ''),
        s3_bucket=config.get('s3_bucket', ''),
        enable_analytics=config.get('enable_analytics', True),
        enable_distributed_coordination=config.get('enable_coordination', True),
        compression_threshold=config.get('compression_threshold', 1024),
        default_ttl=config.get('default_ttl', 3600)
    )
    
    return CachingManager(config=cache_config)

# Module initialization logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Caching Agent v{__version__} initialized - {len(__all__)} components loaded")
