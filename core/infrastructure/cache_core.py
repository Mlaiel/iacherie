"""Ainflue Core Cache - Enterprise Cache Management
=================================================

Core cache management system providing advanced caching orchestration,
distributed caching, cache invalidation, performance optimization, and
enterprise-grade cache operations for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
import time
from datetime import timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class CacheType(str, Enum):
    """Cache types"""
    MEMORY = "memory"
    REDIS = "redis"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"

class SerializationType(str, Enum):
    """Serialization types"""
    JSON = "json"
    PICKLE = "pickle"
    STRING = "string"
    BINARY = "binary"

@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    default_ttl: int = 3600  # 1 hour
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    compression_threshold: int = 1024  # Compress items > 1KB
    key_prefix: str = "ainflue:"

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    memory_usage: int = 0
    avg_get_time: float = 0.0
    avg_set_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None

class CacheEntry:
    """Cache entry with metadata"""
    
    def __init__(self, value: Any, ttl: Optional[int] = None, tags: List[str] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.tags = tags or []
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def access(self):
        """Mark entry as accessed"""
        self.access_count += 1
        self.last_accessed = time.time()

class CacheCore:
    """Enterprise cache core management system"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache core"""
        self.config = config or CacheConfig()
        self.metrics = CacheMetrics()
        
        # Cache storage
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.redis_client: Optional[redis.Redis] = None
        
        # Cache locks for thread safety
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        
        logger.info("🗃️ Cache Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize cache system"""
        try:
            logger.info("🔌 Initializing cache connections...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            logger.info("✅ Cache Core initialization completed")
            return True
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Cache Core initialization failed: {e}")
            return False
    
    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=False,  # Handle binary data
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            
            logger.info("✅ Redis cache connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed, using memory cache only: {e}")
            self.redis_client = None
    
    def _get_key(self, key: str) -> str:
        """Get prefixed cache key"""
        return f"{self.config.key_prefix}{key}"
    
    def _serialize_value(self, value: Any, serialization: SerializationType = SerializationType.PICKLE) -> bytes:
        """Serialize value for storage"""
        try:
            if serialization == SerializationType.JSON:
                return json.dumps(value).encode()
            elif serialization == SerializationType.PICKLE:
                return pickle.dumps(value)
            elif serialization == SerializationType.STRING:
                return str(value).encode()
            else:
                return bytes(value)
        except Exception as e:
            logger.error(f"❌ Serialization failed: {e}")
            raise
    
    def _deserialize_value(self, data: bytes, serialization: SerializationType = SerializationType.PICKLE) -> Any:
        """Deserialize value from storage"""
        try:
            if serialization == SerializationType.JSON:
                return json.loads(data.decode())
            elif serialization == SerializationType.PICKLE:
                return pickle.loads(data)
            elif serialization == SerializationType.STRING:
                return data.decode()
            else:
                return data
        except Exception as e:
            logger.error(f"❌ Deserialization failed: {e}")
            raise
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        start_time = time.time()
        
        try:
            # Try memory cache first
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if not entry.is_expired():
                    entry.access()
                    self.metrics.hits += 1
                    
                    # Update timing
                    get_time = time.time() - start_time
                    self._update_avg_time('get', get_time)
                    
                    return entry.value
                else:
                    # Remove expired entry
                    del self.memory_cache[key]
            
            # Try Redis cache
            if self.redis_client:
                prefixed_key = self._get_key(key)
                data = await self.redis_client.get(prefixed_key)
                
                if data:
                    value = self._deserialize_value(data)
                    
                    # Store in memory cache for faster access
                    self.memory_cache[key] = CacheEntry(value, self.config.default_ttl)
                    
                    self.metrics.hits += 1
                    
                    # Update timing
                    get_time = time.time() - start_time
                    self._update_avg_time('get', get_time)
                    
                    return value
            
            # Cache miss
            self.metrics.misses += 1
            return default
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Cache get failed for key '{key}': {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in cache"""
        start_time = time.time()
        
        try:
            ttl = ttl or self.config.default_ttl
            
            # Store in memory cache
            self.memory_cache[key] = CacheEntry(value, ttl, tags or [])
            
            # Store in Redis cache
            if self.redis_client:
                prefixed_key = self._get_key(key)
                serialized_value = self._serialize_value(value)
                
                await self.redis_client.setex(prefixed_key, ttl, serialized_value)
            
            self.metrics.sets += 1
            
            # Update timing
            set_time = time.time() - start_time
            self._update_avg_time('set', set_time)
            
            # Check memory usage and evict if necessary
            await self._check_memory_usage()
            
            return True
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Cache set failed for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove from Redis cache
            if self.redis_client:
                prefixed_key = self._get_key(key)
                await self.redis_client.delete(prefixed_key)
            
            self.metrics.deletes += 1
            return True
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Cache delete failed for key '{key}': {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear Redis cache (only our keys)
            if self.redis_client:
                pattern = f"{self.config.key_prefix}*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            
            logger.info("✅ Cache cleared")
            return True
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Cache clear failed: {e}")
            return False
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        invalidated = 0
        
        try:
            # Check memory cache
            keys_to_remove = []
            for key, entry in self.memory_cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                await self.delete(key)
                invalidated += 1
            
            logger.info(f"✅ Invalidated {invalidated} cache entries by tags: {tags}")
            return invalidated
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation by tags failed: {e}")
            return 0
    
    def _update_avg_time(self, operation: str, duration: float):
        """Update average operation time"""
        if operation == 'get':
            total_ops = self.metrics.hits + self.metrics.misses
            if total_ops > 0:
                self.metrics.avg_get_time = (
                    (self.metrics.avg_get_time * (total_ops - 1) + duration) / total_ops
                )
        elif operation == 'set':
            if self.metrics.sets > 0:
                self.metrics.avg_set_time = (
                    (self.metrics.avg_set_time * (self.metrics.sets - 1) + duration) / self.metrics.sets
                )
    
    async def _check_memory_usage(self):
        """Check memory usage and evict if necessary"""
        try:
            # Simple size estimation
            current_size = len(self.memory_cache) * 1000  # Rough estimate
            
            if current_size > self.config.max_memory_size:
                # Evict least recently used entries
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].last_accessed
                )
                
                # Remove 25% of entries
                to_remove = len(sorted_entries) // 4
                for i in range(to_remove):
                    key = sorted_entries[i][0]
                    del self.memory_cache[key]
                    self.metrics.evictions += 1
                
                logger.info(f"📊 Evicted {to_remove} cache entries due to memory pressure")
        
        except Exception as e:
            logger.error(f"❌ Memory check failed: {e}")
    
    async def health_check(self) -> bool:
        """Perform cache health check"""
        try:
            # Test memory cache
            test_key = "__health_check__"
            await self.set(test_key, "ok", 60)
            result = await self.get(test_key)
            await self.delete(test_key)
            
            if result != "ok":
                return False
            
            # Test Redis if available
            if self.redis_client:
                await self.redis_client.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache health check failed: {e}")
            return False
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics"""
        # Calculate hit rate
        total_requests = self.metrics.hits + self.metrics.misses
        hit_rate = (self.metrics.hits / total_requests * 100) if total_requests > 0 else 0
        
        logger.info(f"📊 Cache metrics - Hit rate: {hit_rate:.1f}%, Memory entries: {len(self.memory_cache)}")
        
        return self.metrics

# Global cache instance
cache_core = CacheCore()

# Convenience functions
async def cache_get(key: str, default: Any = None) -> Any:
    """Get value from cache"""
    return await cache_core.get(key, default)

async def cache_set(key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
    """Set value in cache"""
    return await cache_core.set(key, value, ttl, tags)

async def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    return await cache_core.delete(key)

async def cache_clear() -> bool:
    """Clear all cache"""
    return await cache_core.clear()

async def cache_health() -> bool:
    """Check cache health"""
    return await cache_core.health_check()

# Module exports
__all__ = [
    "CacheCore", "CacheConfig", "CacheMetrics", "CacheType", "SerializationType",
    "CacheEntry", "cache_core", "cache_get", "cache_set", "cache_delete",
    "cache_clear", "cache_health"
]