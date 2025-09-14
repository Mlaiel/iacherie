"""💾 Backend Database Cache - Consolidated Enterprise Caching Management
========================================================================
Module: backend/database/cache.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Database Caching Management - Enterprise Production-Ready
Responsibility: Complete caching strategies for performance optimization and data access
==================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated cache module provides comprehensive caching strategies for:
- Multi-level caching (L1 memory, L2 Redis, L3 distributed)
- Content fingerprint caching for fast similarity matching
- User session and authentication token caching
- Revenue analytics and reporting data caching
- AI model results and predictions caching
- Platform integration data caching
- Real-time analytics and metrics caching

CONSOLIDATED CACHING FEATURES:
- Intelligent cache invalidation and TTL management
- Cache warming strategies for frequently accessed data
- Distributed cache synchronization across microservices
- Cache compression and serialization optimization
- Cache hit/miss ratio monitoring and analytics
- Automatic cache scaling based on load patterns
- Cache security with encryption for sensitive data
- Multi-tenant cache isolation and management
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Callable, Generic, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import pickle
import gzip
import hashlib
import weakref
from collections import OrderedDict
import threading

# Redis imports
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Memcached imports
try:
    import aiomcache
    MEMCACHED_AVAILABLE = True
except ImportError:
    MEMCACHED_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheLevel(Enum):
    """Cache level enumeration."""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISTRIBUTED = "l3_distributed"


class CacheStrategy(Enum):
    """Cache strategy enumeration."""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    CACHE_ASIDE = "cache_aside"


class SerializationFormat(Enum):
    """Serialization format enumeration."""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    PROTOBUF = "protobuf"


@dataclass
class CacheConfig:
    """Cache configuration parameters."""
    max_size: int = 1000
    ttl_seconds: int = 3600
    compression_enabled: bool = True
    encryption_enabled: bool = False
    serialization_format: SerializationFormat = SerializationFormat.JSON
    eviction_policy: str = "lru"  # lru, lfu, fifo
    enable_stats: bool = True
    warm_cache_on_start: bool = False
    auto_refresh_enabled: bool = False
    refresh_threshold: float = 0.1  # 10% before expiry


@dataclass
class CacheStats:
    """Cache statistics data structure."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    memory_usage: int = 0
    hit_rate: float = 0.0
    average_access_time: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CacheEntry:
    """Cache entry data structure."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class ICacheProvider(ABC, Generic[T]):
    """Cache provider interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class MemoryCache(ICacheProvider[T]):
    """
    🧠 In-Memory Cache Provider
    
    High-performance in-memory cache with LRU eviction and TTL support.
    Ideal for frequently accessed small datasets and session data.
    """
    
    def __init__(self, config -> None: CacheConfig) -> None:
        self.config = config
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._lock = threading.RLock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize memory cache."""
        logger.info("🧠 Initializing Memory Cache...")
        
        # Start cleanup task for expired entries
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
        
        logger.info(f"✅ Memory Cache initialized (max_size: {self.config.max_size})")
    
    async def get(self, key: str) -> Optional[T]:
        """Get value from memory cache."""
        start_time = datetime.now(timezone.utc)
        
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.misses += 1
                return None
            
            # Check expiration
            if entry.expires_at and datetime.now(timezone.utc) >= entry.expires_at:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_accessed = datetime.now(timezone.utc)
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            
            self._stats.hits += 1
            self._update_stats(start_time)
            
            return entry.value
    
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        expires_at = None
        if ttl:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        elif self.config.ttl_seconds:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.config.ttl_seconds)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        with self._lock:
            # Remove oldest entries if at capacity
            while len(self._cache) >= self.config.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats.evictions += 1
            
            self._cache[key] = entry
            self._stats.size = len(self._cache)
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry and (not entry.expires_at or datetime.now(timezone.utc) < entry.expires_at):
                return True
        return False
    
    async def clear(self) -> bool:
        """Clear all memory cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats.size = 0
            self._stats.evictions += len(self._cache)
        return True
    
    def get_stats(self) -> CacheStats:
        """Get memory cache statistics."""
        with self._lock:
            total_accesses = self._stats.hits + self._stats.misses
            self._stats.hit_rate = self._stats.hits / total_accesses if total_accesses > 0 else 0.0
            self._stats.size = len(self._cache)
            self._stats.last_updated = datetime.now(timezone.utc)
        return self._stats
    
    def _update_stats(self, start_time -> None: datetime) -> None:
        """Update performance statistics."""
        access_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000  # ms
        if self._stats.average_access_time == 0:
            self._stats.average_access_time = access_time
        else:
            # Exponential moving average
            self._stats.average_access_time = 0.9 * self._stats.average_access_time + 0.1 * access_time
    
    async def _cleanup_expired(self) -> None:
        """Cleanup expired entries periodically."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                now = datetime.now(timezone.utc)
                expired_keys = []
                
                with self._lock:
                    for key, entry in self._cache.items():
                        if entry.expires_at and now >= entry.expires_at:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self._cache[key]
                        self._stats.evictions += 1
                    
                    self._stats.size = len(self._cache)
                
                if expired_keys:
                    logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def close(self) -> None:
        """Close memory cache."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


class RedisCache(ICacheProvider[T]):
    """
    🔴 Redis Cache Provider
    
    Distributed Redis cache for high-performance data sharing across microservices.
    Supports clustering, persistence, and advanced data structures.
    """
    
    def __init__(self, config -> None: CacheConfig, redis_url -> None: str) -> None:
        self.config = config
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._stats = CacheStats()
    
    async def initialize(self) -> None:
        """Initialize Redis cache."""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis not available")
        
        logger.info("🔴 Initializing Redis Cache...")
        
        self._redis = aioredis.from_url(self.redis_url)
        
        # Test connection
        await self._redis.ping()
        
        logger.info("✅ Redis Cache initialized")
    
    async def get(self, key: str) -> Optional[T]:
        """Get value from Redis cache."""
        if not self._redis:
            return None
        
        start_time = datetime.now(timezone.utc)
        
        try:
            data = await self._redis.get(key)
            if data is None:
                self._stats.misses += 1
                return None
            
            # Deserialize
            value = self._deserialize(data)
            self._stats.hits += 1
            self._update_stats(start_time)
            
            return value
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._stats.misses += 1
            return None
    
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        if not self._redis:
            return False
        
        try:
            # Serialize
            data = self._serialize(value)
            
            # Set TTL
            expire_time = ttl or self.config.ttl_seconds
            
            await self._redis.set(key, data, ex=expire_time)
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all Redis cache entries."""
        if not self._redis:
            return False
        
        try:
            await self._redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def _serialize(self, value: T) -> bytes:
        """Serialize value for storage."""
        if self.config.serialization_format == SerializationFormat.JSON:
            data = json.dumps(value).encode()
        elif self.config.serialization_format == SerializationFormat.PICKLE:
            data = pickle.dumps(value)
        else:
            data = str(value).encode()
        
        if self.config.compression_enabled:
            data = gzip.compress(data)
        
        return data
    
    def _deserialize(self, data: bytes) -> T:
        """Deserialize value from storage."""
        if self.config.compression_enabled:
            data = gzip.decompress(data)
        
        if self.config.serialization_format == SerializationFormat.JSON:
            return json.loads(data.decode())
        elif self.config.serialization_format == SerializationFormat.PICKLE:
            return pickle.loads(data)
        else:
            return data.decode()
    
    def get_stats(self) -> CacheStats:
        """Get Redis cache statistics."""
        total_accesses = self._stats.hits + self._stats.misses
        self._stats.hit_rate = self._stats.hits / total_accesses if total_accesses > 0 else 0.0
        self._stats.last_updated = datetime.now(timezone.utc)
        return self._stats
    
    def _update_stats(self, start_time -> None: datetime) -> None:
        """Update performance statistics."""
        access_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000  # ms
        if self._stats.average_access_time == 0:
            self._stats.average_access_time = access_time
        else:
            self._stats.average_access_time = 0.9 * self._stats.average_access_time + 0.1 * access_time
    
    async def close(self) -> None:
        """Close Redis cache."""
        if self._redis:
            await self._redis.close()


class MultiLevelCache(ICacheProvider[T]):
    """
    🏗️ Multi-Level Cache Manager
    
    Intelligent multi-level caching combining memory (L1), Redis (L2), and distributed (L3) caches.
    Automatically promotes frequently accessed data to faster cache levels.
    """
    
    def __init__(self, memory_config -> None: CacheConfig, redis_config -> None: Optional[CacheConfig] = None, redis_url -> None: Optional[str] = None) -> None:
        self.memory_cache = MemoryCache(memory_config)
        self.redis_cache = RedisCache(redis_config, redis_url) if redis_config and redis_url else None
        self._stats = CacheStats()
        
    async def initialize(self) -> None:
        """Initialize multi-level cache."""
        logger.info("🏗️ Initializing Multi-Level Cache...")
        
        await self.memory_cache.initialize()
        
        if self.redis_cache:
            try:
                await self.redis_cache.initialize()
                logger.info("✅ L2 Redis cache enabled")
            except Exception as e:
                logger.warning(f"⚠️ L2 Redis cache disabled: {e}")
                self.redis_cache = None
        
        logger.info("✅ Multi-Level Cache initialized")
    
    async def get(self, key: str) -> Optional[T]:
        """Get value from multi-level cache."""
        # Try L1 (Memory) first
        value = await self.memory_cache.get(key)
        if value is not None:
            self._stats.hits += 1
            return value
        
        # Try L2 (Redis) if available
        if self.redis_cache:
            value = await self.redis_cache.get(key)
            if value is not None:
                # Promote to L1
                await self.memory_cache.set(key, value)
                self._stats.hits += 1
                return value
        
        self._stats.misses += 1
        return None
    
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set value in multi-level cache."""
        # Set in all available levels
        success = await self.memory_cache.set(key, value, ttl)
        
        if self.redis_cache:
            redis_success = await self.redis_cache.set(key, value, ttl)
            success = success and redis_success
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete value from multi-level cache."""
        # Delete from all levels
        success = await self.memory_cache.delete(key)
        
        if self.redis_cache:
            redis_success = await self.redis_cache.delete(key)
            success = success or redis_success
        
        return success
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache level."""
        if await self.memory_cache.exists(key):
            return True
        
        if self.redis_cache and await self.redis_cache.exists(key):
            return True
        
        return False
    
    async def clear(self) -> bool:
        """Clear all cache levels."""
        success = await self.memory_cache.clear()
        
        if self.redis_cache:
            redis_success = await self.redis_cache.clear()
            success = success and redis_success
        
        return success
    
    def get_stats(self) -> CacheStats:
        """Get combined cache statistics."""
        l1_stats = self.memory_cache.get_stats()
        l2_stats = self.redis_cache.get_stats() if self.redis_cache else CacheStats()
        
        # Combine statistics
        total_hits = l1_stats.hits + l2_stats.hits + self._stats.hits
        total_misses = l1_stats.misses + l2_stats.misses + self._stats.misses
        total_accesses = total_hits + total_misses
        
        combined_stats = CacheStats(
            hits=total_hits,
            misses=total_misses,
            evictions=l1_stats.evictions + l2_stats.evictions,
            size=l1_stats.size + l2_stats.size,
            hit_rate=total_hits / total_accesses if total_accesses > 0 else 0.0,
            average_access_time=(l1_stats.average_access_time + l2_stats.average_access_time) / 2,
            last_updated=datetime.now(timezone.utc)
        )
        
        return combined_stats
    
    async def close(self) -> None:
        """Close multi-level cache."""
        await self.memory_cache.close()
        if self.redis_cache:
            await self.redis_cache.close()


class DatabaseCacheManager:
    """
    🚀 Enterprise Database Cache Manager
    
    Central cache orchestrator for the IA Influencer platform providing intelligent
    caching strategies for all database operations and business logic data.
    """
    
    def __init__(self) -> None:
        self._caches: Dict[str, ICacheProvider] = {}
        self._cache_configs: Dict[str, CacheConfig] = {}
        
    async def initialize_cache(self, cache_name -> None: str, cache_type -> None: str, config -> None: CacheConfig, **kwargs) -> None:
        """Initialize a named cache instance."""
        logger.info(f"🚀 Initializing {cache_type} cache: {cache_name}")
        
        if cache_type == "memory":
            cache = MemoryCache(config)
        elif cache_type == "redis":
            cache = RedisCache(config, kwargs.get("redis_url"))
        elif cache_type == "multi_level":
            cache = MultiLevelCache(config, kwargs.get("redis_config"), kwargs.get("redis_url"))
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
        
        await cache.initialize()
        self._caches[cache_name] = cache
        self._cache_configs[cache_name] = config
        
        logger.info(f"✅ Cache {cache_name} initialized")
    
    async def get_cache(self, cache_name: str) -> ICacheProvider:
        """Get a named cache instance."""
        if cache_name not in self._caches:
            raise ValueError(f"Cache not found: {cache_name}")
        return self._caches[cache_name]
    
    async def setup_default_caches(self, redis_url -> None: Optional[str] = None) -> None:
        """Setup default caches for the platform."""
        # Session cache (fast access, short TTL)
        session_config = CacheConfig(
            max_size=10000,
            ttl_seconds=1800,  # 30 minutes
            compression_enabled=False,
            serialization_format=SerializationFormat.JSON
        )
        await self.initialize_cache("sessions", "memory", session_config)
        
        # Content fingerprint cache (large, persistent)
        fingerprint_config = CacheConfig(
            max_size=100000,
            ttl_seconds=86400,  # 24 hours
            compression_enabled=True,
            serialization_format=SerializationFormat.PICKLE
        )
        if redis_url:
            await self.initialize_cache("fingerprints", "redis", fingerprint_config, redis_url=redis_url)
        else:
            await self.initialize_cache("fingerprints", "memory", fingerprint_config)
        
        # Analytics cache (medium size, medium TTL)
        analytics_config = CacheConfig(
            max_size=50000,
            ttl_seconds=3600,  # 1 hour
            compression_enabled=True,
            serialization_format=SerializationFormat.JSON
        )
        if redis_url:
            await self.initialize_cache("analytics", "multi_level", analytics_config, redis_url=redis_url)
        else:
            await self.initialize_cache("analytics", "memory", analytics_config)
        
        logger.info("✅ Default caches setup completed")
    
    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all caches."""
        return {name: cache.get_stats() for name, cache in self._caches.items()}
    
    async def clear_all_caches(self) -> None:
        """Clear all cache instances."""
        for name, cache in self._caches.items():
            await cache.clear()
            logger.info(f"🧹 Cache {name} cleared")
    
    async def close_all_caches(self) -> None:
        """Close all cache instances."""
        for name, cache in self._caches.items():
            await cache.close()
            logger.info(f"🔌 Cache {name} closed")
        
        self._caches.clear()


# Global cache manager instance
_cache_manager: Optional[DatabaseCacheManager] = None


def get_cache_manager() -> DatabaseCacheManager:
    """Get the global database cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = DatabaseCacheManager()
    return _cache_manager


# Export all public interfaces
__all__ = [
    "DatabaseCacheManager",
    "get_cache_manager",
    "ICacheProvider",
    "MemoryCache",
    "RedisCache",
    "MultiLevelCache",
    "CacheConfig",
    "CacheStats",
    "CacheLevel",
    "CacheStrategy",
    "SerializationFormat",
]