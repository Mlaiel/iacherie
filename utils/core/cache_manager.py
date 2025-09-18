"""
Cache Manager - Core Utilities Level 1
=====================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade cache management utility for Creator Economy platform.
Provides multi-level caching with Redis integration, memory cache,
intelligent invalidation, and performance monitoring.

Performance: < 1ms for memory cache, < 5ms for Redis operations
Standards: 100% async, type hints, enterprise patterns
"""

import asyncio
import json
import hashlib
import logging
import pickle
import time
import weakref
from typing import (
    Any, Dict, List, Optional, Union, Callable, Tuple, 
    AsyncIterator, TypeVar, Generic, Set
)
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import threading
from collections import OrderedDict

# Optional dependencies with enterprise fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    lz4 = None
    LZ4_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class CacheResult(Generic[T]):
    """Enterprise result container for cache operations."""
    success: bool
    data: Optional[T] = None
    hit: bool = False
    source: Optional[str] = None  # 'memory', 'redis', 'miss'
    ttl_remaining: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CacheConfig:
    """Enterprise cache configuration."""
    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_max_connections: int = 100
    
    # Memory cache configuration
    memory_max_size: int = 1000  # Maximum number of items
    memory_ttl_default: int = 3600  # Default TTL in seconds
    
    # Performance configuration
    compression_threshold: int = 1024  # Compress data larger than this
    enable_compression: bool = True
    enable_metrics: bool = True
    
    # Creator Economy specific
    creator_content_ttl: int = 7200  # 2 hours for creator content
    analytics_ttl: int = 1800  # 30 minutes for analytics
    cdn_ttl: int = 86400  # 24 hours for CDN cache

@dataclass
class CacheEntry:
    """Internal cache entry with metadata."""
    data: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: int = 0
    compressed: bool = False

class MemoryCache:
    """Thread-safe in-memory LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size_bytes': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from memory cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            # Check TTL
            now = datetime.now(timezone.utc)
            if entry.expires_at and now > entry.expires_at:
                self._cache.pop(key)
                self._stats['misses'] += 1
                self._stats['size_bytes'] -= entry.size_bytes
                return None
            
            # Update access info and move to end (LRU)
            entry.access_count += 1
            entry.last_accessed = now
            self._cache.move_to_end(key)
            self._stats['hits'] += 1
            return entry.data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set item in memory cache."""
        with self._lock:
            try:
                # Calculate size (approximate)
                size_bytes = len(pickle.dumps(value))
                
                # Create entry
                now = datetime.now(timezone.utc)
                expires_at = now + timedelta(seconds=ttl) if ttl else None
                entry = CacheEntry(
                    data=value,
                    created_at=now,
                    expires_at=expires_at,
                    size_bytes=size_bytes
                )
                
                # Remove existing entry if present
                if key in self._cache:
                    old_entry = self._cache[key]
                    self._stats['size_bytes'] -= old_entry.size_bytes
                
                # Add new entry
                self._cache[key] = entry
                self._cache.move_to_end(key)
                self._stats['size_bytes'] += size_bytes
                
                # Evict if necessary
                while len(self._cache) > self.max_size:
                    oldest_key = next(iter(self._cache))
                    oldest_entry = self._cache.pop(oldest_key)
                    self._stats['evictions'] += 1
                    self._stats['size_bytes'] -= oldest_entry.size_bytes
                
                return True
            except Exception as e:
                logger.error(f"Memory cache set error: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete item from memory cache."""
        with self._lock:
            entry = self._cache.pop(key, None)
            if entry:
                self._stats['size_bytes'] -= entry.size_bytes
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from memory cache."""
        with self._lock:
            self._cache.clear()
            self._stats['size_bytes'] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_operations = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_operations if total_operations > 0 else 0
            
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self._stats['evictions'],
                'size_items': len(self._cache),
                'size_bytes': self._stats['size_bytes'],
                'max_size': self.max_size
            }

class CacheManager:
    """
    Enterprise cache manager for Creator Economy platform.
    
    Provides multi-level caching with:
    - Memory cache for sub-millisecond access
    - Redis cache for distributed caching
    - Intelligent invalidation and TTL management
    - Performance monitoring and metrics
    - Creator-specific optimization
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.memory_cache = MemoryCache(self.config.memory_max_size)
        self.redis_client: Optional[redis.Redis] = None
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="cache-worker")
        
        # Performance monitoring
        self.metrics = {
            'total_operations': 0,
            'redis_operations': 0,
            'memory_operations': 0,
            'compression_operations': 0,
            'avg_response_time': 0.0
        }
        
        # Creator Economy specific caches
        self.creator_patterns = {
            'content': 'creator_content:',
            'analytics': 'creator_analytics:',
            'profile': 'creator_profile:',
            'earnings': 'creator_earnings:',
            'collaboration': 'creator_collab:'
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self) -> bool:
        """Initialize cache manager and connections."""
        try:
            # Initialize Redis connection if available
            if REDIS_AVAILABLE and self.config.redis_url:
                self.redis_client = redis.from_url(
                    self.config.redis_url,
                    db=self.config.redis_db,
                    max_connections=self.config.redis_max_connections,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test Redis connection
                await self.redis_client.ping()
                logger.info("Redis cache connection established")
            else:
                logger.warning("Redis not available, using memory cache only")
            
            logger.info("Cache manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Cache manager initialization failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close cache manager and cleanup resources."""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.executor.shutdown(wait=True)
            logger.info("Cache manager closed successfully")
            
        except Exception as e:
            logger.error(f"Cache manager close error: {e}")
    
    def _generate_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Generate standardized cache key."""
        if namespace:
            return f"{namespace}:{key}"
        return key
    
    def _compress_data(self, data: bytes) -> Tuple[bytes, bool]:
        """Compress data if beneficial."""
        if not self.config.enable_compression or len(data) < self.config.compression_threshold:
            return data, False
        
        if LZ4_AVAILABLE:
            try:
                compressed = lz4.frame.compress(data)
                if len(compressed) < len(data):
                    return compressed, True
            except Exception as e:
                logger.warning(f"Compression failed: {e}")
        
        return data, False
    
    def _decompress_data(self, data: bytes, compressed: bool) -> bytes:
        """Decompress data if compressed."""
        if not compressed or not LZ4_AVAILABLE:
            return data
        
        try:
            return lz4.frame.decompress(data)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return data
    
    async def _measure_performance(self, operation: Callable) -> Tuple[Any, float]:
        """Measure operation performance."""
        start_time = time.perf_counter()
        result = await operation()
        execution_time = (time.perf_counter() - start_time) * 1000
        
        # Update metrics
        self.metrics['total_operations'] += 1
        current_avg = self.metrics['avg_response_time']
        total_ops = self.metrics['total_operations']
        self.metrics['avg_response_time'] = (current_avg * (total_ops - 1) + execution_time) / total_ops
        
        return result, execution_time
    
    async def get(self, key: str, namespace: Optional[str] = None) -> CacheResult[Any]:
        """
        Get value from cache with multi-level lookup.
        
        Args:
            key: Cache key
            namespace: Optional namespace for key isolation
            
        Returns:
            CacheResult with data and metadata
        """
        async def _get_operation():
            full_key = self._generate_key(key, namespace)
            
            # Try memory cache first
            memory_value = self.memory_cache.get(full_key)
            if memory_value is not None:
                self.metrics['memory_operations'] += 1
                return CacheResult(
                    success=True,
                    data=memory_value,
                    hit=True,
                    source='memory'
                )
            
            # Try Redis cache
            if self.redis_client:
                try:
                    redis_data = await self.redis_client.get(full_key)
                    if redis_data:
                        # Get metadata
                        metadata_key = f"{full_key}:meta"
                        metadata_raw = await self.redis_client.get(metadata_key)
                        metadata = json.loads(metadata_raw) if metadata_raw else {}
                        
                        # Decompress if needed
                        compressed = metadata.get('compressed', False)
                        decompressed_data = self._decompress_data(redis_data, compressed)
                        
                        # Deserialize
                        value = pickle.loads(decompressed_data)
                        
                        # Store in memory cache for faster future access
                        memory_ttl = min(3600, metadata.get('ttl', 3600))
                        self.memory_cache.set(full_key, value, memory_ttl)
                        
                        # Get TTL remaining
                        ttl_remaining = await self.redis_client.ttl(full_key)
                        
                        self.metrics['redis_operations'] += 1
                        return CacheResult(
                            success=True,
                            data=value,
                            hit=True,
                            source='redis',
                            ttl_remaining=ttl_remaining if ttl_remaining > 0 else None,
                            metadata=metadata
                        )
                        
                except Exception as e:
                    logger.error(f"Redis get error for key {full_key}: {e}")
            
            # Cache miss
            return CacheResult(
                success=True,
                data=None,
                hit=False,
                source='miss'
            )
        
        result, execution_time = await self._measure_performance(_get_operation)
        result.execution_time_ms = execution_time
        return result
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> CacheResult[bool]:
        """
        Set value in cache with multi-level storage.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            namespace: Optional namespace for key isolation
            tags: Optional tags for invalidation groups
            
        Returns:
            CacheResult with operation status
        """
        async def _set_operation():
            full_key = self._generate_key(key, namespace)
            effective_ttl = ttl or self.config.memory_ttl_default
            
            # Serialize data
            try:
                serialized_data = pickle.dumps(value)
                compressed_data, is_compressed = self._compress_data(serialized_data)
                
                if is_compressed:
                    self.metrics['compression_operations'] += 1
                
            except Exception as e:
                return CacheResult(
                    success=False,
                    data=False,
                    errors=[f"Serialization failed: {e}"]
                )
            
            # Store in memory cache
            memory_success = self.memory_cache.set(full_key, value, effective_ttl)
            if memory_success:
                self.metrics['memory_operations'] += 1
            
            # Store in Redis cache
            redis_success = True
            if self.redis_client:
                try:
                    # Create metadata
                    metadata = {
                        'compressed': is_compressed,
                        'ttl': effective_ttl,
                        'tags': tags or [],
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'size_bytes': len(compressed_data)
                    }
                    
                    # Store data and metadata
                    async with self.redis_client.pipeline() as pipe:
                        pipe.set(full_key, compressed_data, ex=effective_ttl)
                        pipe.set(f"{full_key}:meta", json.dumps(metadata), ex=effective_ttl)
                        
                        # Add to tag sets for invalidation
                        if tags:
                            for tag in tags:
                                tag_key = f"tag:{tag}"
                                pipe.sadd(tag_key, full_key)
                                pipe.expire(tag_key, effective_ttl)
                        
                        await pipe.execute()
                    
                    self.metrics['redis_operations'] += 1
                    
                except Exception as e:
                    logger.error(f"Redis set error for key {full_key}: {e}")
                    redis_success = False
            
            return CacheResult(
                success=memory_success or redis_success,
                data=True,
                metadata={
                    'memory_success': memory_success,
                    'redis_success': redis_success,
                    'compressed': is_compressed,
                    'size_bytes': len(compressed_data)
                }
            )
        
        result, execution_time = await self._measure_performance(_set_operation)
        result.execution_time_ms = execution_time
        return result
    
    async def delete(self, key: str, namespace: Optional[str] = None) -> CacheResult[bool]:
        """Delete value from all cache levels."""
        async def _delete_operation():
            full_key = self._generate_key(key, namespace)
            
            # Delete from memory cache
            memory_deleted = self.memory_cache.delete(full_key)
            
            # Delete from Redis cache
            redis_deleted = False
            if self.redis_client:
                try:
                    deleted_count = await self.redis_client.delete(full_key, f"{full_key}:meta")
                    redis_deleted = deleted_count > 0
                except Exception as e:
                    logger.error(f"Redis delete error for key {full_key}: {e}")
            
            return CacheResult(
                success=memory_deleted or redis_deleted,
                data=memory_deleted or redis_deleted,
                metadata={
                    'memory_deleted': memory_deleted,
                    'redis_deleted': redis_deleted
                }
            )
        
        result, execution_time = await self._measure_performance(_delete_operation)
        result.execution_time_ms = execution_time
        return result
    
    async def invalidate_by_tags(self, tags: List[str]) -> CacheResult[int]:
        """Invalidate all cache entries with specified tags."""
        if not self.redis_client:
            return CacheResult(success=False, errors=["Redis not available for tag invalidation"])
        
        async def _invalidate_operation():
            total_deleted = 0
            
            try:
                for tag in tags:
                    tag_key = f"tag:{tag}"
                    
                    # Get all keys with this tag
                    keys = await self.redis_client.smembers(tag_key)
                    
                    if keys:
                        # Delete data and metadata keys
                        keys_to_delete = []
                        for key in keys:
                            key_str = key.decode() if isinstance(key, bytes) else key
                            keys_to_delete.extend([key_str, f"{key_str}:meta"])
                        
                        # Delete from Redis
                        deleted = await self.redis_client.delete(*keys_to_delete)
                        total_deleted += deleted
                        
                        # Delete from memory cache
                        for key in keys:
                            key_str = key.decode() if isinstance(key, bytes) else key
                            self.memory_cache.delete(key_str)
                    
                    # Delete tag set
                    await self.redis_client.delete(tag_key)
                
                return CacheResult(
                    success=True,
                    data=total_deleted,
                    metadata={'tags_processed': len(tags)}
                )
                
            except Exception as e:
                return CacheResult(
                    success=False,
                    data=0,
                    errors=[f"Tag invalidation failed: {e}"]
                )
        
        result, execution_time = await self._measure_performance(_invalidate_operation)
        result.execution_time_ms = execution_time
        return result
    
    async def clear_all(self) -> CacheResult[bool]:
        """Clear all cache entries."""
        async def _clear_operation():
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear Redis cache
            redis_cleared = True
            if self.redis_client:
                try:
                    await self.redis_client.flushdb()
                except Exception as e:
                    logger.error(f"Redis clear error: {e}")
                    redis_cleared = False
            
            return CacheResult(
                success=True,
                data=True,
                metadata={'redis_cleared': redis_cleared}
            )
        
        result, execution_time = await self._measure_performance(_clear_operation)
        result.execution_time_ms = execution_time
        return result
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        memory_stats = self.memory_cache.get_stats()
        
        redis_stats = {}
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info('memory')
                redis_stats = {
                    'memory_used': redis_info.get('used_memory', 0),
                    'memory_peak': redis_info.get('used_memory_peak', 0),
                    'connections': redis_info.get('connected_clients', 0)
                }
            except Exception as e:
                logger.error(f"Redis stats error: {e}")
        
        return {
            'memory_cache': memory_stats,
            'redis_cache': redis_stats,
            'performance_metrics': self.metrics.copy(),
            'configuration': {
                'memory_max_size': self.config.memory_max_size,
                'redis_available': self.redis_client is not None,
                'compression_enabled': self.config.enable_compression,
                'compression_threshold': self.config.compression_threshold
            }
        }
    
    # Creator Economy specific methods
    
    async def cache_creator_content(
        self, 
        creator_id: str, 
        content_id: str, 
        content_data: Any
    ) -> CacheResult[bool]:
        """Cache creator content with optimized TTL."""
        key = f"{creator_id}:{content_id}"
        return await self.set(
            key=key,
            value=content_data,
            ttl=self.config.creator_content_ttl,
            namespace=self.creator_patterns['content'],
            tags=[f"creator:{creator_id}", "content"]
        )
    
    async def cache_creator_analytics(
        self, 
        creator_id: str, 
        analytics_data: Any,
        period: str = "daily"
    ) -> CacheResult[bool]:
        """Cache creator analytics with shorter TTL."""
        key = f"{creator_id}:{period}"
        return await self.set(
            key=key,
            value=analytics_data,
            ttl=self.config.analytics_ttl,
            namespace=self.creator_patterns['analytics'],
            tags=[f"creator:{creator_id}", "analytics", f"period:{period}"]
        )
    
    async def invalidate_creator_cache(self, creator_id: str) -> CacheResult[int]:
        """Invalidate all cache entries for a specific creator."""
        return await self.invalidate_by_tags([f"creator:{creator_id}"])

# Factory for dependency injection
class CacheManagerFactory:
    """Factory for creating CacheManager instances."""
    
    @staticmethod
    def create(config: Optional[CacheConfig] = None) -> CacheManager:
        """Create a new CacheManager instance."""
        return CacheManager(config)
    
    @staticmethod
    def create_with_redis(redis_url: str, **kwargs) -> CacheManager:
        """Create CacheManager with Redis configuration."""
        config = CacheConfig(redis_url=redis_url, **kwargs)
        return CacheManager(config)
    
    @staticmethod
    def create_memory_only(**kwargs) -> CacheManager:
        """Create memory-only CacheManager."""
        config = CacheConfig(redis_url="", **kwargs)
        return CacheManager(config)

# Singleton instance for global use
_cache_manager_instance: Optional[CacheManager] = None

async def get_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
    """Get or create global cache manager instance."""
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager(config)
        await _cache_manager_instance.initialize()
    
    return _cache_manager_instance

__all__ = [
    'CacheManager',
    'CacheManagerFactory', 
    'CacheConfig',
    'CacheResult',
    'MemoryCache',
    'get_cache_manager'
]