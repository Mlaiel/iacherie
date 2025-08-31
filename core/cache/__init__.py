"""Core Cache Module for IA Influencer Agent Platform
Enterprise-grade, multi-backend caching system for content creators

Business Logic: Creator Upload → AI Processing → Cache Layer → SEO → Distribution → Monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Contact: mlaiel@live.de
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Processing Expert + DevOps Engineer + IA Prompt Engineer

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED ⚠️
Copyright (C) 2024 Fahed Mlaiel. All rights reserved.
This software is protected by copyright law and international treaties.
Unauthorized reproduction, distribution, or use is strictly prohibited.
Violations may result in severe civil and criminal penalties.

For licensing inquiries: mlaiel@live.de
"""# Import everything from the main index module for enhanced functionality
from .index import *

# Maintain backward compatibility with existing imports
from .cache_manager import CacheManager, CacheConfig, CacheBackend, CachePolicy, CacheMetadata
from .redis_cache import RedisCache, RedisClusterCache, RedisConfig, RedisMetrics
from .memory_cache import MemoryCache, LRUCache, EvictionPolicy, MemoryStats
from .vector_cache import VectorCache, FAISSCache, VectorCacheConfig, SimilarityResult
from .content_cache import ContentCache, MediaCache, ContentMetadata, ContentType
from .analytics_cache import AnalyticsCache, MetricsCache, AnalyticsData, MetricsSnapshot
from .cache_utils import (
    GlobalCacheConfig, CacheProfiler, CacheMetricsCollector, CacheError,
    CacheConnectionError, CacheTimeoutError, CacheSerializationError,
    build_cache_key, serialize_cache_value, deserialize_cache_value,
    calculate_cache_efficiency, get_cache_recommendations
)

# Legacy imports that may be used by existing code
try:
    from .session_cache import SessionCache, AuthCache, SessionData, AuthenticationData
    from .platform_cache import PlatformCache, APIResponseCache, PlatformData, APIMetrics
    from .fingerprint_cache import FingerprintCache, SimilarityCache, FingerprintData, MatchResult
    from .revenue_cache import RevenueCache, MonetizationCache, RevenueEntry, RevenueAnalytics, EarningsData
    from .cache_strategies import (
        CacheStrategy, CacheStrategyManager, EvictionStrategy, PrefetchStrategy, 
        InvalidationStrategy, WarmupStrategy, DistributionStrategy
    )
    from .cache_decorators import (
        cached, memoize, cache_invalidate, cache_warmup, cache_warm_up,
        register_cache_instance, cache_key_builder, cache_timeout
    )
    from .cache_monitoring import (
        CacheMonitor, CacheMetrics, MetricCollector, AlertManager, 
        CacheHealthStatus, PerformanceTracker, UsageAnalyzer
    )
except ImportError:
    # These modules may not exist yet but are planned for future implementation
    pass

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (C) 2024 Fahed Mlaiel. All rights reserved."

# Export all public components (enhanced list from index.py plus legacy compatibility)
__all__ = [
    # Enhanced exports from index.py
    'CacheManager', 'RedisCache', 'EnterpriseMemoryCache', 'VectorCache', 'FAISSCache',
    'ContentCache', 'MediaCache', 'AnalyticsCache',
    'CreatorContentCache', 'AIProcessingCache', 'RevenueAnalyticsCache',
    'CacheFactory', 'GlobalCacheManager',
    'cache_creator_content', 'cache_ai_processing_result', 'cache_revenue_metrics',
    'search_similar_content', 'get_creator_analytics', 'invalidate_creator_cache',
    'health_check', 'get_cache_metrics',
    
    # Legacy compatibility exports
    "CacheConfig", 
    "CacheBackend",
    "CachePolicy",
    "CacheMetadata",
    "RedisClusterCache",
    "RedisConfig",
    "RedisMetrics",
    "MemoryCache", 
    "LRUCache",
    "EvictionPolicy",
    "MemoryStats",
    "VectorCacheConfig",
    "SimilarityResult",
    "ContentMetadata",
    "ContentType",
    "MetricsCache",
    "AnalyticsData",
    "MetricsSnapshot",
    "GlobalCacheConfig",
    "CacheProfiler", 
    "CacheMetricsCollector",
    "CacheError",
    "CacheConnectionError",
    "CacheTimeoutError", 
    "CacheSerializationError",
    "build_cache_key",
    "serialize_cache_value",
    "deserialize_cache_value",
    "calculate_cache_efficiency",
    "get_cache_recommendations"
]

# Module metadata for introspection (enhanced)
__module_info__ = {
    "name": "IA Influencer Agent Core Cache",
    "description": "Enterprise caching system for multi-format content creators",
    "business_logic": "Creator Upload → AI Processing → Cache Layer → SEO → Distribution → Monetization",
    "supported_formats": ["audio", "video", "image", "text", "metadata", "podcast", "music", "livestream"],
    "cache_backends": ["redis", "redis_cluster", "memory", "vector", "hybrid", "faiss"],
    "specializations": [
        "Multi-tenant isolation",
        "AI-powered similarity search", 
        "Revenue-aware caching",
        "Real-time analytics",
        "Content fingerprinting",
        "Platform API caching",
        "Content protection",
        "Monetization tracking",
        "Creator collaboration"
    ],
    "team_expertise": [
        "Lead Dev IA", "Backend Senior", "ML Engineer", "DBA", 
        "Security Expert", "Microservices Architect", "Audio Processing Expert",
        "DevOps Engineer", "IA Prompt Engineer"
    ],
    "version": __version__,
    "enhanced_features": [
        "Enterprise memory cache with compression",
        "Multi-tier caching strategy",
        "Business logic aware eviction",
        "Real-time health monitoring",
        "Advanced analytics and metrics",
        "Content-aware caching policies"
    ]
}
