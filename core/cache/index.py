"""Cache Module Index for IA Influencer Agent Platform
Central entry point for all caching components with factory patterns and global instances

Business Logic Integration:
- Creator content caching with tenant isolation
- AI processing result caching for faster analysis
- Revenue tracking and analytics caching
- Content protection and fingerprint caching
- Platform API response caching with intelligent invalidation
- Multi-tier caching strategy (Memory -> Redis -> Vector)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
      Microservices Architect + Audio Processing Expert + DevOps Engineer + IA Prompt Engineer
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, Union
from datetime import datetime

# Core cache imports
from .cache_manager import (
    CacheManager,
    CacheConfig,
    CacheBackend,
    CacheStrategy,
    create_cache_manager,
    get_cache_manager
)

from .redis_cache import (
    RedisCache,
    RedisConfig,
    RedisClusterConfig,
    SerializerType,
    CompressionType,
    EncryptionMode,
    create_redis_cache,
    get_redis_cache
)

from .memory_cache import (
    EnterpriseMemoryCache,
    CacheConfig as MemoryCacheConfig,
    EvictionPolicy,
    CacheNamespace,
    CachePriority,
    CompressionType as MemoryCompressionType,
    CacheMetrics,
    CreatorContentCache,
    AIProcessingCache,
    RevenueAnalyticsCache,
    create_memory_cache,
    create_creator_cache,
    create_ai_cache,
    create_revenue_cache,
    get_memory_cache,
    get_creator_cache,
    get_ai_cache,
    get_revenue_cache
)

from .vector_cache import (
    VectorCache,
    FAISSCache,
    VectorCacheConfig,
    ContentType,
    SimilarityMetric,
    IndexType,
    VectorEntry,
    SimilarityResult,
    VectorCacheAnalytics,
    create_vector_cache,
    create_faiss_cache,
    get_vector_cache,
    get_faiss_cache,
    cache_audio_fingerprint,
    search_similar_audio,
    detect_audio_violations
)

from .content_cache import (
    ContentCache,
    MediaCache,
    ContentType as ContentContentType,
    ProcessingStatus,
    ContentPriority,
    ProtectionLevel,
    MonetizationStatus,
    ContentMetadata,
    ProcessingResult
)

from .analytics_cache import (
    AnalyticsCache,
    MetricType,
    AggregationType,
    TimeWindow,
    AnalyticsMetric,
    RevenueMetric,
    CreatorMetric,
    create_analytics_cache,
    get_analytics_cache
)

from .cache_utils import (
    CacheUtils,
    cache_key,
    invalidate_pattern,
    batch_get,
    batch_set,
    cache_aside,
    write_through,
    write_behind,
    circuit_breaker
)

logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Global cache instances for IA Influencer Agent platform
_global_cache_instances = {
    'cache_manager': None,
    'redis_cache': None,
    'memory_cache': None,
    'vector_cache': None,
    'content_cache': None,
    'analytics_cache': None,
    'creator_cache': None,
    'ai_cache': None,
    'revenue_cache': None
}

class CacheFactory:
    """
    Factory class for creating and managing cache instances
    Provides centralized configuration and instance management
    """
    
    @staticmethod
    def create_enterprise_cache_stack(
        redis_config: Optional[RedisConfig] = None,
        memory_config: Optional[MemoryCacheConfig] = None,
        vector_config: Optional[VectorCacheConfig] = None,
        enable_analytics: bool = True,
        enable_content_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Create complete enterprise cache stack for IA Influencer Agent
        
        Returns dictionary with all cache instances configured for production use
        """
        
        # Default configurations optimized for IA Influencer Agent
        if redis_config is None:
            redis_config = RedisConfig(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD'),
                ssl=os.getenv('REDIS_SSL', 'false').lower() == 'true',
                pool_size=20,
                retry_attempts=3,
                timeout=30.0,
                enable_compression=True,
                compression_type=CompressionType.ZLIB,
                enable_encryption=True,
                encryption_mode=EncryptionMode.AES_256_GCM,
                multi_tenant=True,
                tenant_isolation=True
            )
        
        if memory_config is None:
            memory_config = MemoryCacheConfig(
                max_size=10000,
                max_memory_bytes=500 * 1024 * 1024,  # 500MB
                eviction_policy=EvictionPolicy.ADAPTIVE,
                enable_compression=True,
                compression_type=MemoryCompressionType.ZLIB,
                creator_isolation=True,
                namespace_isolation=True,
                priority_based_eviction=True,
                revenue_aware_caching=True
            )
        
        if vector_config is None:
            vector_config = VectorCacheConfig(
                dimension=512,
                max_vectors=100000,
                similarity_threshold=0.8,
                metric=SimilarityMetric.COSINE,
                index_type=IndexType.HNSW,
                enable_persistence=True
            )
        
        # Create cache instances
        cache_stack = {}
        
        # Redis cache - Foundation layer
        cache_stack['redis'] = RedisCache(redis_config)
        
        # Memory cache - High-speed layer
        cache_stack['memory'] = EnterpriseMemoryCache(memory_config)
        
        # Vector cache - AI similarity search
        try:
            cache_stack['vector'] = FAISSCache(vector_config)
        except ImportError:
            logger.warning("FAISS not available, using standard vector cache")
            cache_stack['vector'] = VectorCache(vector_config)
        
        # Specialized caches
        cache_stack['creator'] = CreatorContentCache(max_size=5000)
        cache_stack['ai_processing'] = AIProcessingCache(max_size=2000)
        cache_stack['revenue'] = RevenueAnalyticsCache(max_size=1000)
        
        # Content cache for multimedia
        if enable_content_cache:
            cache_stack['content'] = ContentCache(
                redis_config=redis_config,
                vector_cache=cache_stack['vector'],
                max_file_size=100 * 1024 * 1024,  # 100MB
                chunk_size=1024 * 1024  # 1MB chunks
            )
        
        # Analytics cache for metrics
        if enable_analytics:
            cache_stack['analytics'] = AnalyticsCache(
                redis_cache=cache_stack['redis'],
                memory_cache=cache_stack['memory']
            )
        
        # Cache manager - Orchestration layer
        cache_manager_config = CacheConfig(
            strategy=CacheStrategy.MULTI_TIER,
            default_ttl=3600,
            enable_metrics=True,
            enable_circuit_breaker=True,
            enable_batch_operations=True
        )
        
        cache_stack['manager'] = CacheManager(
            config=cache_manager_config,
            redis_cache=cache_stack['redis'],
            memory_cache=cache_stack['memory'],
            vector_cache=cache_stack['vector']
        )
        
        logger.info("Enterprise cache stack created successfully")
        return cache_stack
    
    @staticmethod
    async def initialize_cache_stack(cache_stack: Dict[str, Any]) -> bool:
        """Initialize all caches in the stack"""
        try:
            # Initialize Redis connection
            if 'redis' in cache_stack:
                await cache_stack['redis'].connect()
            
            # Initialize content cache
            if 'content' in cache_stack:
                await cache_stack['content'].initialize()
            
            # Initialize analytics cache  
            if 'analytics' in cache_stack:
                await cache_stack['analytics'].initialize()
            
            # Initialize cache manager
            if 'manager' in cache_stack:
                await cache_stack['manager'].initialize()
            
            logger.info("Cache stack initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cache stack: {e}")
            return False
    
    @staticmethod
    async def shutdown_cache_stack(cache_stack: Dict[str, Any]) -> bool:
        """Gracefully shutdown all caches"""
        try:
            # Shutdown in reverse order
            shutdown_order = ['manager', 'analytics', 'content', 'revenue', 
                            'ai_processing', 'creator', 'vector', 'memory', 'redis']
            
            for cache_name in shutdown_order:
                if cache_name in cache_stack:
                    cache_instance = cache_stack[cache_name]
                    
                    if hasattr(cache_instance, 'close'):
                        if asyncio.iscoroutinefunction(cache_instance.close):
                            await cache_instance.close()
                        else:
                            cache_instance.close()
                    
                    logger.debug(f"Shutdown {cache_name} cache")
            
            logger.info("Cache stack shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during cache stack shutdown: {e}")
            return False

class GlobalCacheManager:
    """
    Global cache manager for singleton instances
    Provides application-wide cache access patterns
    """
    
    @staticmethod
    async def initialize_global_caches(
        redis_config: Optional[RedisConfig] = None,
        memory_config: Optional[MemoryCacheConfig] = None,
        vector_config: Optional[VectorCacheConfig] = None
    ) -> bool:
        """
Initialize global cache instances"""
        
        global _global_cache_instances
        
        try:
            # Create enterprise cache stack
            cache_stack = CacheFactory.create_enterprise_cache_stack(
                redis_config=redis_config,
                memory_config=memory_config,
                vector_config=vector_config
            )
            
            # Initialize all caches
            success = await CacheFactory.initialize_cache_stack(cache_stack)
            
            if success:
                # Store global references
                _global_cache_instances.update(cache_stack)
                _global_cache_instances['cache_manager'] = cache_stack['manager']
                
                logger.info("Global caches initialized successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize global caches: {e}")
            return False
    
    @staticmethod
    def get_cache_manager() -> Optional[CacheManager]:
        """Get global cache manager instance"""
        return _global_cache_instances.get('cache_manager')
    
    @staticmethod
    def get_redis_cache() -> Optional[RedisCache]:
        """
Get global Redis cache instance"""
        return _global_cache_instances.get('redis')
    
    @staticmethod
    def get_memory_cache() -> Optional[EnterpriseMemoryCache]:
        """
Get global memory cache instance"""
        return _global_cache_instances.get('memory')
    
    @staticmethod
    def get_vector_cache() -> Optional[Union[VectorCache, FAISSCache]]:
        """
Get global vector cache instance"""
        return _global_cache_instances.get('vector')
    
    @staticmethod
    def get_content_cache() -> Optional[ContentCache]:
        """
Get global content cache instance"""
        return _global_cache_instances.get('content')
    
    @staticmethod
    def get_analytics_cache() -> Optional[AnalyticsCache]:
        """
Get global analytics cache instance"""
        return _global_cache_instances.get('analytics')
    
    @staticmethod
    def get_creator_cache() -> Optional[CreatorContentCache]:
        """
Get global creator cache instance"""
        return _global_cache_instances.get('creator')
    
    @staticmethod
    def get_ai_cache() -> Optional[AIProcessingCache]:
        """
Get global AI processing cache instance"""
        return _global_cache_instances.get('ai_processing')
    
    @staticmethod
    def get_revenue_cache() -> Optional[RevenueAnalyticsCache]:
        """
Get global revenue cache instance"""
        return _global_cache_instances.get('revenue')
    
    @staticmethod
    async def shutdown_global_caches() -> bool:
        """
Shutdown all global cache instances"""
        global _global_cache_instances
        
        success = await CacheFactory.shutdown_cache_stack(_global_cache_instances)
        
        # Clear global references
        _global_cache_instances = {key: None for key in _global_cache_instances}
        
        return success

# Convenience functions for IA Influencer Agent business logic

async def cache_creator_content(
    creator_id: str,
    content_id: str,
    content: Any,
    content_type: str = "audio",
    monetization_value: float = 0.0,
    ttl: Optional[int] = None
) -> bool:
    """Cache creator content with business metadata"""
    creator_cache = GlobalCacheManager.get_creator_cache()
    if creator_cache:
        return creator_cache.cache_content(
            content_id=content_id,
            creator_id=creator_id,
            content=content,
            content_type=content_type,
            monetization_value=monetization_value
        )
    return False

async def cache_ai_processing_result(
    creator_id: str,
    content_id: str,
    processing_result: Any,
    processing_cost: float,
    model_version: str = "v1.0"
) -> bool:
    """Cache AI processing result"""
    ai_cache = GlobalCacheManager.get_ai_cache()
    if ai_cache:
        return ai_cache.cache_ai_result(
            content_id=content_id,
            creator_id=creator_id,
            processing_result=processing_result,
            processing_cost=processing_cost,
            model_version=model_version
        )
    return False

async def cache_revenue_metrics(
    creator_id: str,
    metric_key: str,
    revenue_data: Any,
    revenue_impact: float
) -> bool:
    """
Cache revenue metrics"""
    revenue_cache = GlobalCacheManager.get_revenue_cache()
    if revenue_cache:
        return revenue_cache.cache_revenue_data(
            metric_key=metric_key,
            creator_id=creator_id,
            data=revenue_data,
            revenue_impact=revenue_impact
        )
    return False

async def search_similar_content(
    query_vector: list,
    content_type: Optional[str] = None,
    creator_id: Optional[str] = None,
    top_k: int = 10
) -> list:
    """
Search for similar content using vector cache"""
    vector_cache = GlobalCacheManager.get_vector_cache()
    if vector_cache:
        return await vector_cache.search_similar(
            query_vector=query_vector,
            top_k=top_k,
            content_type=ContentType(content_type) if content_type else None,
            creator_id=creator_id
        )
    return []

async def get_creator_analytics(creator_id: str) -> Dict[str, Any]:
    """
Get comprehensive analytics for a creator"""
    analytics = {}
    
    # Get creator cache stats
    creator_cache = GlobalCacheManager.get_creator_cache()
    if creator_cache:
        analytics['content_stats'] = creator_cache.get_creator_stats(creator_id)
    
    # Get vector cache stats
    vector_cache = GlobalCacheManager.get_vector_cache()
    if vector_cache and hasattr(vector_cache, 'get_creator_vectors'):
        creator_vectors = await vector_cache.get_creator_vectors(creator_id)
        analytics['vector_stats'] = {
            'total_vectors': len(creator_vectors),
            'avg_similarity_score': sum(v.last_similarity_score or 0 for v in creator_vectors) / len(creator_vectors) if creator_vectors else 0
        }
    
    # Get revenue analytics
    revenue_cache = GlobalCacheManager.get_revenue_cache()
    if revenue_cache:
        analytics['revenue_stats'] = revenue_cache.get_creator_stats(creator_id)
    
    return analytics

async def invalidate_creator_cache(creator_id: str) -> bool:
    """
Invalidate all cache entries for a creator"""
    success = True
    
    # Clear from all specialized caches
    caches = [
        GlobalCacheManager.get_creator_cache(),
        GlobalCacheManager.get_ai_cache(),
        GlobalCacheManager.get_revenue_cache()
    ]
    
    for cache in caches:
        if cache and hasattr(cache, 'clear_creator_cache'):
            try:
                cache.clear_creator_cache(creator_id)
            except Exception as e:
                logger.error(f"Failed to clear creator cache: {e}")
                success = False
    
    # Clear from vector cache
    vector_cache = GlobalCacheManager.get_vector_cache()
    if vector_cache and hasattr(vector_cache, 'remove_creator_vectors'):
        try:
            await vector_cache.remove_creator_vectors(creator_id)
        except Exception as e:
            logger.error(f"Failed to clear vector cache: {e}")
            success = False
    
    return success

# Health check functions

async def health_check() -> Dict[str, Any]:
    """Comprehensive health check for all cache components"""
    health_status = {
        'overall': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }
    
    # Check cache manager
    cache_manager = GlobalCacheManager.get_cache_manager()
    if cache_manager:
        health_status['components']['cache_manager'] = await cache_manager.health_check()
    
    # Check Redis cache
    redis_cache = GlobalCacheManager.get_redis_cache()
    if redis_cache:
        health_status['components']['redis'] = await redis_cache.health_check()
    
    # Check memory cache
    memory_cache = GlobalCacheManager.get_memory_cache()
    if memory_cache:
        health_status['components']['memory'] = memory_cache._health_status
    
    # Check vector cache
    vector_cache = GlobalCacheManager.get_vector_cache()
    if vector_cache:
        health_status['components']['vector'] = {'status': 'healthy', 'vectors': len(vector_cache._vectors)}
    
    # Determine overall health
    component_statuses = [comp.get('status', 'unknown') for comp in health_status['components'].values()]
    if any(status in ['critical', 'error'] for status in component_statuses):
        health_status['overall'] = 'critical'
    elif any(status == 'warning' for status in component_statuses):
        health_status['overall'] = 'warning'
    
    return health_status

async def get_cache_metrics() -> Dict[str, Any]:
    """
Get comprehensive metrics from all cache components"""
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }
    
    # Cache manager metrics
    cache_manager = GlobalCacheManager.get_cache_manager()
    if cache_manager:
        metrics['components']['cache_manager'] = await cache_manager.get_comprehensive_stats()
    
    # Redis metrics
    redis_cache = GlobalCacheManager.get_redis_cache()
    if redis_cache:
        metrics['components']['redis'] = await redis_cache.get_comprehensive_stats()
    
    # Memory cache metrics
    memory_cache = GlobalCacheManager.get_memory_cache()
    if memory_cache:
        metrics['components']['memory'] = memory_cache.get_comprehensive_stats()
    
    # Vector cache metrics
    vector_cache = GlobalCacheManager.get_vector_cache()
    if vector_cache:
        metrics['components']['vector'] = vector_cache.get_comprehensive_stats()
    
    # Specialized cache metrics
    for cache_name, cache_instance in [
        ('creator', GlobalCacheManager.get_creator_cache()),
        ('ai_processing', GlobalCacheManager.get_ai_cache()),
        ('revenue', GlobalCacheManager.get_revenue_cache())
    ]:
        if cache_instance:
            metrics['components'][cache_name] = cache_instance.get_comprehensive_stats()
    
    return metrics

# Export all public APIs
__all__ = [
    # Core classes
    'CacheManager', 'RedisCache', 'EnterpriseMemoryCache', 'VectorCache', 'FAISSCache',
    'ContentCache', 'MediaCache', 'AnalyticsCache',
    
    # Specialized caches
    'CreatorContentCache', 'AIProcessingCache', 'RevenueAnalyticsCache',
    
    # Configuration classes
    'CacheConfig', 'RedisConfig', 'MemoryCacheConfig', 'VectorCacheConfig',
    
    # Enums
    'CacheBackend', 'CacheStrategy', 'EvictionPolicy', 'CacheNamespace', 'CachePriority',
    'ContentType', 'ProcessingStatus', 'SerializerType', 'CompressionType', 'EncryptionMode',
    'SimilarityMetric', 'IndexType', 'MetricType', 'AggregationType', 'TimeWindow',
    
    # Data classes
    'VectorEntry', 'SimilarityResult', 'ContentMetadata', 'ProcessingResult',
    'AnalyticsMetric', 'RevenueMetric', 'CreatorMetric',
    
    # Factory and management
    'CacheFactory', 'GlobalCacheManager',
    
    # Convenience functions
    'cache_creator_content', 'cache_ai_processing_result', 'cache_revenue_metrics',
    'search_similar_content', 'get_creator_analytics', 'invalidate_creator_cache',
    
    # Utility functions
    'cache_key', 'invalidate_pattern', 'batch_get', 'batch_set',
    'cache_aside', 'write_through', 'write_behind', 'circuit_breaker',
    
    # Health and monitoring
    'health_check', 'get_cache_metrics',
    
    # Factory functions
    'create_cache_manager', 'create_redis_cache', 'create_memory_cache',
    'create_vector_cache', 'create_faiss_cache', 'create_analytics_cache',
    
    # Global getters
    'get_cache_manager', 'get_redis_cache', 'get_memory_cache', 'get_vector_cache',
    'get_analytics_cache', 'get_creator_cache', 'get_ai_cache', 'get_revenue_cache',
    
    # Business logic helpers
    'cache_audio_fingerprint', 'search_similar_audio', 'detect_audio_violations'
]

# Module metadata
__title__ = "IA Influencer Agent Cache Module"
__description__ = "Enterprise-grade caching system for multimedia content creators"
__url__ = "https://github.com/Mlaiel/IA-influencer"
__version_info__ = (1, 0, 0)
__version__ = ".".join(map(str, __version_info__))
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "All rights reserved"
__copyright__ = "Copyright 2025 Fahed Mlaiel"
