"""Cache Manager Module

Advanced multi-layer caching system for database optimization with Redis integration,
intelligent cache strategies, and automatic cache invalidation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Set, Callable
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    READ_THROUGH = "read_through"


class CacheLevel(Enum):
    """Cache levels for multi-tier caching"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    strategy: CacheStrategy = CacheStrategy.LRU
    ttl_seconds: int = 3600
    max_size: int = 10000
    eviction_policy: str = "lru"
    compression_enabled: bool = True
    serialization_format: str = "json"
    invalidation_pattern: Optional[str] = None
    warm_up_enabled: bool = False
    metrics_enabled: bool = True
    
    # Redis specific settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Performance settings
    batch_size: int = 1000
    concurrent_operations: int = 10
    timeout_seconds: int = 5


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    write_count: int = 0
    read_count: int = 0
    total_size: int = 0
    memory_usage: int = 0
    avg_response_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total_requests = self.hit_count + self.miss_count
        return self.hit_count / total_requests if total_requests > 0 else 0.0
    
    @property
    def miss_ratio(self) -> float:
        """Calculate cache miss ratio"""
        return 1.0 - self.hit_ratio


class CacheEntry:
    """Cache entry with metadata"""
    
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl = ttl
        self.expires_at = self.created_at + timedelta(seconds=ttl) if ttl else None
        self.size = self._calculate_size()
    
    def _calculate_size(self) -> int:
        """Calculate entry size in bytes"""
        try:
            return len(json.dumps(self.value).encode('utf-8'))
        except (TypeError, ValueError):
            return len(str(self.value).encode('utf-8'))
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def access(self) -> None:
        """Mark entry as accessed"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class MemoryCache:
    """In-memory cache with LRU/LFU eviction"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []  # For LRU
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                await self._remove(key)
                return None
            
            entry.access()
            if self.config.strategy == CacheStrategy.LRU:
                self._access_order.remove(key)
                self._access_order.append(key)
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in memory cache"""
        async with self._lock:
            entry = CacheEntry(key, value, ttl or self.config.ttl_seconds)
            
            # Check if eviction is needed
            if len(self._cache) >= self.config.max_size:
                await self._evict()
            
            self._cache[key] = entry
            if key not in self._access_order:
                self._access_order.append(key)
    
    async def delete(self, key: str) -> bool:
        """Delete key from memory cache"""
        async with self._lock:
            return await self._remove(key)
    
    async def _remove(self, key: str) -> bool:
        """Remove key from cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False
    
    async def _evict(self) -> None:
        """Evict entries based on strategy"""
        if not self._cache:
            return
        
        if self.config.strategy == CacheStrategy.LRU:
            # Remove least recently used
            if self._access_order:
                key_to_evict = self._access_order[0]
                await self._remove(key_to_evict)
        
        elif self.config.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            min_access_count = min(entry.access_count for entry in self._cache.values())
            key_to_evict = next(
                key for key, entry in self._cache.items()
                if entry.access_count == min_access_count
            )
            await self._remove(key_to_evict)
    
    def get_size(self) -> int:
        """Get current cache size"""
        return len(self._cache)
    
    def get_memory_usage(self) -> int:
        """Get memory usage in bytes"""
        return sum(entry.size for entry in self._cache.values())


class CacheManager:
    """Advanced multi-layer cache manager"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.memory_cache = MemoryCache(config)
        self.redis_client: Optional[redis.Redis] = None
        self.metrics = CacheMetrics()
        self.metrics_collector = MetricsCollector()
        self._invalidation_patterns: Set[str] = set()
        self._warm_up_tasks: List[Callable] = []
        
        # Initialize Redis connection
        asyncio.create_task(self._initialize_redis())
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True,
                socket_timeout=self.config.timeout_seconds
            )
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache (multi-level)"""
        start_time = time.time()
        
        try:
            # Try L1 cache (memory)
            value = await self.memory_cache.get(key)
            if value is not None:
                self._update_metrics(hit=True, level=CacheLevel.L1_MEMORY)
                return value
            
            # Try L2 cache (Redis)
            if self.redis_client:
                value = await self._get_from_redis(key)
                if value is not None:
                    # Store in L1 for faster access
                    await self.memory_cache.set(key, value)
                    self._update_metrics(hit=True, level=CacheLevel.L2_REDIS)
                    return value
            
            # Cache miss
            self._update_metrics(hit=False)
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
        
        finally:
            response_time = time.time() - start_time
            self._update_response_time(response_time)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache (multi-level)"""
        try:
            effective_ttl = ttl or self.config.ttl_seconds
            
            # Set in L1 cache (memory)
            await self.memory_cache.set(key, value, effective_ttl)
            
            # Set in L2 cache (Redis)
            if self.redis_client:
                await self._set_in_redis(key, value, effective_ttl)
            
            self.metrics.write_count += 1
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        try:
            deleted = False
            
            # Delete from L1 cache
            if await self.memory_cache.delete(key):
                deleted = True
            
            # Delete from L2 cache
            if self.redis_client:
                if await self.redis_client.delete(key):
                    deleted = True
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        try:
            deleted_count = 0
            
            if self.redis_client:
                # Get all keys matching pattern
                keys = await self.redis_client.keys(pattern)
                if keys:
                    # Delete in batches
                    for i in range(0, len(keys), self.config.batch_size):
                        batch = keys[i:i + self.config.batch_size]
                        deleted_count += await self.redis_client.delete(*batch)
            
            # Also invalidate from memory cache
            memory_keys = [k for k in self.memory_cache._cache.keys() if self._match_pattern(k, pattern)]
            for key in memory_keys:
                await self.memory_cache.delete(key)
                deleted_count += 1
            
            logger.info(f"Invalidated {deleted_count} cache entries for pattern: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return 0
    
    async def warm_up(self) -> None:
        """Warm up cache with predefined data"""
        if not self.config.warm_up_enabled or not self._warm_up_tasks:
            return
        
        try:
            logger.info("Starting cache warm-up process")
            
            with ThreadPoolExecutor(max_workers=self.config.concurrent_operations) as executor:
                warm_up_futures = [
                    asyncio.get_event_loop().run_in_executor(executor, task)
                    for task in self._warm_up_tasks
                ]
                await asyncio.gather(*warm_up_futures, return_exceptions=True)
            
            logger.info("Cache warm-up completed")
            
        except Exception as e:
            logger.error(f"Cache warm-up error: {e}")
    
    def add_warm_up_task(self, task: Callable) -> None:
        """Add a warm-up task"""
        self._warm_up_tasks.append(task)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "hit_ratio": self.metrics.hit_ratio,
            "miss_ratio": self.metrics.miss_ratio,
            "total_hits": self.metrics.hit_count,
            "total_misses": self.metrics.miss_count,
            "total_writes": self.metrics.write_count,
            "eviction_count": self.metrics.eviction_count,
            "avg_response_time": self.metrics.avg_response_time,
            "memory_cache_size": self.memory_cache.get_size(),
            "memory_usage": self.memory_cache.get_memory_usage(),
            "last_updated": self.metrics.last_updated.isoformat(),
        }
        
        # Add Redis stats if available
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
                stats["redis_memory_usage"] = redis_info.get("used_memory", 0)
                stats["redis_peak_memory"] = redis_info.get("used_memory_peak", 0)
            except Exception as e:
                logger.warning(f"Could not get Redis stats: {e}")
        
        return stats
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # Deserialize value
            if self.config.serialization_format == "json":
                return json.loads(value)
            return value
            
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis cache"""
        try:
            # Serialize value
            if self.config.serialization_format == "json":
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
            
            await self.redis_client.setex(key, ttl, serialized_value)
            
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
    
    def _update_metrics(self, hit: bool, level: Optional[CacheLevel] = None) -> None:
        """Update cache metrics"""
        if hit:
            self.metrics.hit_count += 1
        else:
            self.metrics.miss_count += 1
        
        self.metrics.read_count += 1
        self.metrics.last_updated = datetime.now()
        
        # Send metrics to collector if enabled
        if self.config.metrics_enabled:
            self.metrics_collector.counter(
                "cache_requests_total",
                1,
                {"result": "hit" if hit else "miss", "level": level.value if level else "unknown"}
            )
    
    def _update_response_time(self, response_time: float) -> None:
        """Update average response time"""
        total_requests = self.metrics.hit_count + self.metrics.miss_count
        if total_requests == 1:
            self.metrics.avg_response_time = response_time
        else:
            # Calculate running average
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (total_requests - 1) + response_time) / total_requests
            )
        
        # Send metrics to collector
        if self.config.metrics_enabled:
            self.metrics_collector.histogram(
                "cache_response_time_seconds",
                response_time
            )
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple wildcard support)"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    async def close(self) -> None:
        """Close cache connections"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")


# Cache decorators for easy integration
def cached(
    key_pattern: str = None,
    ttl: int = 3600,
    cache_manager: CacheManager = None
):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if cache_manager is None:
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_pattern:
                cache_key = key_pattern.format(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_invalidate(
    pattern: str,
    cache_manager: CacheManager = None
):
    """Decorator for cache invalidation after function execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if cache_manager:
                invalidation_pattern = pattern.format(*args, **kwargs)
                await cache_manager.invalidate_pattern(invalidation_pattern)
            
            return result
        
        return wrapper
    return decorator
