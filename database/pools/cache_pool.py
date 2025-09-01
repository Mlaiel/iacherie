"""Advanced Cache Connection Pool - IA Influencer Agent + Content Protection Platform

Enterprise cache pool implementation for high-performance data caching,
session management, real-time operations, and distributed cache coordination.

Cache Features:
- Multi-level caching (L1: Local, L2: Redis, L3: Distributed)
- Intelligent cache invalidation and warming
- Real-time data synchronization
- Session and user state management
- Content fingerprint caching
- Analytics data caching
- Geographic cache distribution

Performance Optimizations:
- Connection pooling and load balancing
- Automatic failover and recovery
- Cache partitioning and sharding
- Compression and serialization
- TTL management and memory optimization
- Cache hit ratio monitoring

Business Logic Caching:
- User authentication and permissions
- Content metadata and fingerprints
- Search results and recommendations
- Revenue calculations and reports
- Protection alerts and notifications
- Analytics dashboards data

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import pickle
import json
import zlib
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
from functools import wraps
import weakref
import threading
from collections import defaultdict, OrderedDict

try:
    import aioredis
    from aioredis.sentinel import Sentinel
    from aioredis.cluster import RedisCluster
    import msgpack
    import lz4.frame
    from cachetools import TTLCache, LRUCache
except ImportError as e:
    logging.warning(f"Cache dependency missing: {e}")

from .manager import IConnectionPool, PoolConfig, DatabaseConnectionInfo, ConnectionState

logger = logging.getLogger(__name__)

T = TypeVar('T')

# =============== CACHE CONFIGURATION ===============

class CacheLevel(str, Enum):
    """Cache levels for multi-tier caching"""

    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISTRIBUTED = "l3_distributed"

class CacheStrategy(str, Enum):
    """Cache strategies"""

    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"
    CACHE_ASIDE = "cache_aside"

class SerializationMethod(str, Enum):
    """Serialization methods for cache data"""

    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    COMPRESSED_PICKLE = "compressed_pickle"

class EvictionPolicy(str, Enum):
    """Cache eviction policies"""

    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    RANDOM = "random"

@dataclass
class CacheConfig(PoolConfig):
    """Advanced cache configuration"""
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_sentinel_hosts: List[Tuple[str, int]] = field(default_factory=list)
    redis_master_name: str = "mymaster"
    redis_cluster_nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Cache levels and strategies
    enable_l1_cache: bool = True
    enable_l2_cache: bool = True
    enable_l3_cache: bool = False
    default_strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    
    # Serialization settings
    serialization_method: SerializationMethod = SerializationMethod.MSGPACK
    compression_enabled: bool = True
    compression_threshold: int = 1024  # bytes
    
    # Performance settings
    max_connections: int = 50
    connection_pool_size: int = 20
    socket_keepalive: bool = True
    socket_timeout: int = 5
    
    # L1 Cache (Memory) settings
    l1_max_size: int = 10000
    l1_ttl_seconds: int = 300
    l1_eviction_policy: EvictionPolicy = EvictionPolicy.TTL
    
    # L2 Cache (Redis) settings
    l2_default_ttl: int = 3600
    l2_max_memory_policy: str = "allkeys-lru"
    l2_key_prefix: str = "ia_influencer"
    
    # Cache patterns
    cache_patterns: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "user_session": {"ttl": 1800, "level": CacheLevel.L2_REDIS},
        "content_metadata": {"ttl": 3600, "level": CacheLevel.L2_REDIS},
        "fingerprint_data": {"ttl": 86400, "level": CacheLevel.L2_REDIS},
        "analytics_data": {"ttl": 300, "level": CacheLevel.L1_MEMORY},
        "search_results": {"ttl": 600, "level": CacheLevel.L2_REDIS},
        "revenue_calculations": {"ttl": 1800, "level": CacheLevel.L2_REDIS}
    })

@dataclass
class CacheItem:
    """Cache item with metadata"""
    key: str
    value: Any
    ttl: int
    created_at: float
    accessed_at: float
    access_count: int = 0
    size_bytes: int = 0
    level: CacheLevel = CacheLevel.L2_REDIS
    
    def is_expired(self) -> bool:
        """
Check if cache item is expired"""
        if self.ttl <= 0:
            return False
        return time.time() - self.created_at > self.ttl
    
    def update_access(self) -> None:
        """
Update access statistics"""
        self.accessed_at = time.time()
        self.access_count += 1

# =============== CACHE IMPLEMENTATIONS ===============

class L1MemoryCache:
    """
Level 1 memory cache implementation"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.max_size = config.l1_max_size
        self.ttl = config.l1_ttl_seconds
        
        # Use appropriate cache implementation based on eviction policy
        if config.l1_eviction_policy == EvictionPolicy.TTL:
            self._cache = TTLCache(maxsize=self.max_size, ttl=self.ttl)
        elif config.l1_eviction_policy == EvictionPolicy.LRU:
            self._cache = LRUCache(maxsize=self.max_size)
        else:
            self._cache = {}
        
        self._lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache"""
        with self._lock:
            try:
                value = self._cache.get(key)
                if value is not None:
                    self.stats["hits"] += 1
                    return value
                else:
                    self.stats["misses"] += 1
                    return None
            except Exception as e:
                logger.error(f"L1 cache get error: {e}")
                self.stats["misses"] += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in L1 cache"""
        with self._lock:
            try:
                if isinstance(self._cache, TTLCache) and ttl:
                    # TTLCache doesn't support per-item TTL, use default
                    pass
                
                # Track evictions
                old_size = len(self._cache)
                self._cache[key] = value
                new_size = len(self._cache)
                
                if new_size < old_size:
                    self.stats["evictions"] += 1
                
                self.stats["sets"] += 1
                return True
                
            except Exception as e:
                logger.error(f"L1 cache set error: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from L1 cache"""
        with self._lock:
            try:
                if key in self._cache:
                    del self._cache[key]
                    self.stats["deletes"] += 1
                    return True
                return False
            except Exception as e:
                logger.error(f"L1 cache delete error: {e}")
                return False
    
    def clear(self) -> None:
        """Clear all L1 cache"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
Get L1 cache statistics"""
        with self._lock:
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) if (self.stats["hits"] + self.stats["misses"]) > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                **self.stats
            }

class L2RedisCache:
    """Level 2 Redis cache implementation"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "connection_errors": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        try:
            if self.config.redis_cluster_nodes:
                # Redis Cluster
                self.redis_client = aioredis.RedisCluster.from_url(
                    f"redis://{self.config.redis_host}:{self.config.redis_port}",
                    password=self.config.redis_password,
                    max_connections=self.config.max_connections
                )
            elif self.config.redis_sentinel_hosts:
                # Redis Sentinel
                sentinel = Sentinel(self.config.redis_sentinel_hosts)
                self.redis_client = sentinel.master_for(
                    self.config.redis_master_name,
                    password=self.config.redis_password,
                    db=self.config.redis_db
                )
            else:
                # Single Redis instance
                self.redis_pool = aioredis.ConnectionPool.from_url(
                    f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
                    password=self.config.redis_password,
                    max_connections=self.config.max_connections,
                    socket_keepalive=self.config.socket_keepalive,
                    socket_timeout=self.config.socket_timeout
                )
                self.redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ L2 Redis cache initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ L2 Redis cache initialization failed: {e}")
            return False
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Redis storage"""
        try:
            if self.config.serialization_method == SerializationMethod.JSON:
                data = json.dumps(value).encode('utf-8')
            elif self.config.serialization_method == SerializationMethod.PICKLE:
                data = pickle.dumps(value)
            elif self.config.serialization_method == SerializationMethod.MSGPACK:
                data = msgpack.packb(value)
            elif self.config.serialization_method == SerializationMethod.COMPRESSED_PICKLE:
                data = zlib.compress(pickle.dumps(value))
            else:
                data = pickle.dumps(value)
            
            # Apply compression if enabled and above threshold
            if (self.config.compression_enabled and 
                len(data) > self.config.compression_threshold and
                self.config.serialization_method != SerializationMethod.COMPRESSED_PICKLE):
                try:
                    compressed = lz4.frame.compress(data)
                    if len(compressed) < len(data):
                        return b'lz4:' + compressed
                except:
                    pass
            
            return data
            
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from Redis storage"""
        try:
            # Check for compression
            if data.startswith(b'lz4:'):
                data = lz4.frame.decompress(data[4:])
            
            if self.config.serialization_method == SerializationMethod.JSON:
                return json.loads(data.decode('utf-8'))
            elif self.config.serialization_method == SerializationMethod.PICKLE:
                return pickle.loads(data)
            elif self.config.serialization_method == SerializationMethod.MSGPACK:
                return msgpack.unpackb(data, raw=False)
            elif self.config.serialization_method == SerializationMethod.COMPRESSED_PICKLE:
                return pickle.loads(zlib.decompress(data))
            else:
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def _get_cache_key(self, key: str) -> str:
        """Get full cache key with prefix"""
        return f"{self.config.l2_key_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            cache_key = self._get_cache_key(key)
            data = await self.redis_client.get(cache_key)
            
            if data is not None:
                value = self._deserialize_value(data)
                self.stats["hits"] += 1
                return value
            else:
                self.stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"L2 cache get error: {e}")
            self.stats["connection_errors"] += 1
            self.stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        try:
            cache_key = self._get_cache_key(key)
            serialized_value = self._serialize_value(value)
            
            if ttl:
                await self.redis_client.setex(cache_key, ttl, serialized_value)
            else:
                await self.redis_client.set(cache_key, serialized_value)
                if self.config.l2_default_ttl > 0:
                    await self.redis_client.expire(cache_key, self.config.l2_default_ttl)
            
            self.stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"L2 cache set error: {e}")
            self.stats["connection_errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            cache_key = self._get_cache_key(key)
            result = await self.redis_client.delete(cache_key)
            
            if result > 0:
                self.stats["deletes"] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"L2 cache delete error: {e}")
            self.stats["connection_errors"] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        try:
            cache_key = self._get_cache_key(key)
            return await self.redis_client.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"L2 cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment integer value in Redis cache"""
        try:
            cache_key = self._get_cache_key(key)
            return await self.redis_client.incrby(cache_key, amount)
        except Exception as e:
            logger.error(f"L2 cache increment error: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        try:
            cache_key = self._get_cache_key(key)
            return await self.redis_client.expire(cache_key, ttl) > 0
        except Exception as e:
            logger.error(f"L2 cache expire error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        try:
            cache_pattern = self._get_cache_key(pattern)
            keys = []
            async for key in self.redis_client.scan_iter(match=cache_pattern):
                keys.append(key)
            
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"L2 cache clear pattern error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        try:
            info = await self.redis_client.info('memory')
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) if (self.stats["hits"] + self.stats["misses"]) > 0 else 0
            
            return {
                "memory_used": info.get('used_memory', 0),
                "memory_used_human": info.get('used_memory_human', '0B'),
                "hit_rate": hit_rate,
                **self.stats
            }
        except Exception as e:
            logger.error(f"Failed to get L2 cache stats: {e}")
            return self.stats
    
    async def close(self) -> None:
        """Close Redis connections"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            if self.redis_pool:
                await self.redis_pool.disconnect()
        except Exception as e:
            logger.error(f"Error closing L2 cache: {e}")

# =============== ADVANCED CACHE CONNECTION POOL ===============

class AdvancedCacheConnectionPool(IConnectionPool):
    """Advanced multi-level cache connection pool"""
    
    def __init__(self, config: CacheConfig, connection_info: DatabaseConnectionInfo):
        self.config = config
        self.connection_info = connection_info
        self.state = ConnectionState.IDLE
        
        # Cache instances
        self.l1_cache: Optional[L1MemoryCache] = None
        self.l2_cache: Optional[L2RedisCache] = None
        
        # Cache warming and invalidation
        self._cache_warming_tasks: Dict[str, asyncio.Task] = {}
        self._invalidation_listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_deletes": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "last_health_check": None,
            "average_response_time": 0.0
        }
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._metrics_collection_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """Initialize cache layers"""
        try:
            # Initialize L1 memory cache
            if self.config.enable_l1_cache:
                self.l1_cache = L1MemoryCache(self.config)
                logger.info("✅ L1 memory cache initialized")
            
            # Initialize L2 Redis cache
            if self.config.enable_l2_cache:
                self.l2_cache = L2RedisCache(self.config)
                success = await self.l2_cache.initialize()
                if not success:
                    logger.error("Failed to initialize L2 Redis cache")
                    return False
            
            self.state = ConnectionState.ACTIVE
            
            # Start background tasks
            if self.config.enable_monitoring:
                self._health_check_task = asyncio.create_task(self._health_monitor())
                self._metrics_collection_task = asyncio.create_task(self._metrics_collector())
            
            logger.info(f"✅ Advanced cache pool initialized - L1: {self.config.enable_l1_cache}, L2: {self.config.enable_l2_cache}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Advanced cache pool initialization failed: {e}")
            self.state = ConnectionState.FAILED
            return False
    
    async def acquire(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Acquire cache instances"""
        if self.state != ConnectionState.ACTIVE:
            raise Exception("Cache pool not initialized")
        
        return {
            "l1_cache": self.l1_cache,
            "l2_cache": self.l2_cache,
            "pool": self
        }
    
    async def release(self, connection: Any) -> None:
        """Release cache instances (no-op)"""
        pass
    
    async def get(self, key: str, pattern: Optional[str] = None) -> Optional[Any]:
        """
Get value from cache with multi-level lookup"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Try L1 cache first
            if self.l1_cache and self.config.enable_l1_cache:
                value = self.l1_cache.get(key)
                if value is not None:
                    self.stats["cache_hits"] += 1
                    self.stats["l1_hits"] += 1
                    await self._update_response_time(start_time)
                    return value
            
            # Try L2 cache
            if self.l2_cache and self.config.enable_l2_cache:
                value = await self.l2_cache.get(key)
                if value is not None:
                    self.stats["cache_hits"] += 1
                    self.stats["l2_hits"] += 1
                    
                    # Populate L1 cache if enabled
                    if self.l1_cache and self.config.enable_l1_cache:
                        cache_config = self._get_cache_config(pattern)
                        self.l1_cache.set(key, value, cache_config.get("ttl"))
                    
                    await self._update_response_time(start_time)
                    return value
            
            # Cache miss
            self.stats["cache_misses"] += 1
            await self._update_response_time(start_time)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["cache_misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, pattern: Optional[str] = None) -> bool:
        """Set value in cache with multi-level storage"""
        start_time = time.time()
        self.stats["cache_sets"] += 1
        
        try:
            # Get cache configuration for pattern
            cache_config = self._get_cache_config(pattern)
            effective_ttl = ttl or cache_config.get("ttl", self.config.l2_default_ttl)
            cache_level = cache_config.get("level", CacheLevel.L2_REDIS)
            
            success = True
            
            # Set in L1 cache if enabled and appropriate
            if (self.l1_cache and self.config.enable_l1_cache and 
                cache_level in [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]):
                self.l1_cache.set(key, value, effective_ttl)
            
            # Set in L2 cache if enabled and appropriate
            if (self.l2_cache and self.config.enable_l2_cache and 
                cache_level in [CacheLevel.L2_REDIS, CacheLevel.L3_DISTRIBUTED]):
                success = await self.l2_cache.set(key, value, effective_ttl)
            
            await self._update_response_time(start_time)
            
            # Trigger cache warming if configured
            if pattern and pattern in self.config.cache_patterns:
                await self._trigger_cache_warming(pattern, key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache levels"""
        start_time = time.time()
        self.stats["cache_deletes"] += 1
        
        try:
            success = True
            
            # Delete from L1 cache
            if self.l1_cache and self.config.enable_l1_cache:
                self.l1_cache.delete(key)
            
            # Delete from L2 cache
            if self.l2_cache and self.config.enable_l2_cache:
                success = await self.l2_cache.delete(key)
            
            await self._update_response_time(start_time)
            
            # Trigger invalidation listeners
            await self._trigger_invalidation_listeners(key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache level"""
        try:
            # Check L1 cache
            if self.l1_cache and self.config.enable_l1_cache:
                if self.l1_cache.get(key) is not None:
                    return True
            
            # Check L2 cache
            if self.l2_cache and self.config.enable_l2_cache:
                return await self.l2_cache.exists(key)
            
            return False
            
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
        """Increment counter in cache"""
        try:
            # Use L2 cache for atomic increments
            if self.l2_cache and self.config.enable_l2_cache:
                result = await self.l2_cache.increment(key, amount)
                
                # Set TTL if specified
                if ttl and result is not None:
                    await self.l2_cache.expire(key, ttl)
                
                # Update L1 cache if enabled
                if self.l1_cache and self.config.enable_l1_cache and result is not None:
                    self.l1_cache.set(key, result, ttl)
                
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern from all cache levels"""
        try:
            cleared_count = 0
            
            # Clear from L2 cache (L1 doesn't support pattern clearing)
            if self.l2_cache and self.config.enable_l2_cache:
                cleared_count = await self.l2_cache.clear_pattern(pattern)
            
            # Clear entire L1 cache as fallback (pattern not supported)
            if self.l1_cache and self.config.enable_l1_cache:
                self.l1_cache.clear()
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def _get_cache_config(self, pattern: Optional[str]) -> Dict[str, Any]:
        """Get cache configuration for pattern"""
        if pattern and pattern in self.config.cache_patterns:
            return self.config.cache_patterns[pattern]
        return {"ttl": self.config.l2_default_ttl, "level": CacheLevel.L2_REDIS}
    
    async def _trigger_cache_warming(self, pattern: str, key: str) -> None:
        """Trigger cache warming for related keys"""
        try:
            # Implementation for cache warming logic
            # This can be extended based on specific business needs
            pass
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
    
    async def _trigger_invalidation_listeners(self, key: str) -> None:
        """Trigger registered invalidation listeners"""
        try:
            for pattern, listeners in self._invalidation_listeners.items():
                if pattern in key or pattern == "*":
                    for listener in listeners:
                        try:
                            await listener(key)
                        except Exception as e:
                            logger.error(f"Invalidation listener error: {e}")
        except Exception as e:
            logger.error(f"Invalidation trigger error: {e}")
    
    def register_invalidation_listener(self, pattern: str, callback: Callable[[str], None]) -> None:
        """Register cache invalidation listener"""
        self._invalidation_listeners[pattern].append(callback)
    
    async def _update_response_time(self, start_time: float) -> None:
        """
Update average response time"""
        response_time = (time.time() - start_time) * 1000  # ms
        total_requests = self.stats["total_requests"]
        
        if total_requests > 0:
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (total_requests - 1) + response_time) / total_requests
            )
    
    # =============== CACHE DECORATORS ===============
    
    def cached(self, ttl: int = 3600, pattern: Optional[str] = None, 
              key_func: Optional[Callable] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # Try to get from cache
                cached_result = await self.get(cache_key, pattern)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl, pattern)
                
                return result
            
            return wrapper
        return decorator
    
    def cache_invalidate(self, patterns: List[str]):
        """Decorator for cache invalidation on function execution"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                
                # Invalidate cache patterns
                for pattern in patterns:
                    await self.clear_pattern(pattern)
                
                return result
            
            return wrapper
        return decorator
    
    # =============== BUSINESS LOGIC CACHE METHODS ===============
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """
Cache user session data"""
        key = f"user_session:{user_id}"
        return await self.set(key, session_data, ttl, "user_session")
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data"""
        key = f"user_session:{user_id}"
        return await self.get(key, "user_session")
    
    async def cache_content_metadata(self, content_id: str, metadata: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache content metadata"""
        key = f"content_metadata:{content_id}"
        return await self.set(key, metadata, ttl, "content_metadata")
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get cached content metadata"""
        key = f"content_metadata:{content_id}"
        return await self.get(key, "content_metadata")
    
    async def cache_fingerprint_data(self, fingerprint_id: str, data: Any, ttl: int = 86400) -> bool:
        """Cache fingerprint data"""
        key = f"fingerprint_data:{fingerprint_id}"
        return await self.set(key, data, ttl, "fingerprint_data")
    
    async def get_fingerprint_data(self, fingerprint_id: str) -> Optional[Any]:
        """Get cached fingerprint data"""
        key = f"fingerprint_data:{fingerprint_id}"
        return await self.get(key, "fingerprint_data")
    
    async def cache_search_results(self, query_hash: str, results: List[Dict], ttl: int = 600) -> bool:
        """Cache search results"""
        key = f"search_results:{query_hash}"
        return await self.set(key, results, ttl, "search_results")
    
    async def get_search_results(self, query_hash: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        key = f"search_results:{query_hash}"
        return await self.get(key, "search_results")
    
    async def cache_revenue_calculation(self, calculation_id: str, result: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache revenue calculation result"""
        key = f"revenue_calculation:{calculation_id}"
        return await self.set(key, result, ttl, "revenue_calculations")
    
    async def get_revenue_calculation(self, calculation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached revenue calculation"""
        key = f"revenue_calculation:{calculation_id}"
        return await self.get(key, "revenue_calculations")
    
    async def increment_view_count(self, content_id: str, ttl: int = 86400) -> Optional[int]:
        """Increment content view counter"""
        key = f"view_count:{content_id}"
        return await self.increment(key, 1, ttl)
    
    async def increment_download_count(self, content_id: str, ttl: int = 86400) -> Optional[int]:
        """Increment content download counter"""
        key = f"download_count:{content_id}"
        return await self.increment(key, 1, ttl)
    
    # =============== HEALTH AND MONITORING ===============
    
    async def health_check(self) -> bool:
        """Check cache pool health"""
        try:
            # Test L1 cache
            l1_healthy = True
            if self.l1_cache and self.config.enable_l1_cache:
                try:
                    test_key = f"health_check_{int(time.time())}"
                    self.l1_cache.set(test_key, "test", 10)
                    self.l1_cache.delete(test_key)
                except Exception as e:
                    logger.warning(f"L1 cache health check failed: {e}")
                    l1_healthy = False
            
            # Test L2 cache
            l2_healthy = True
            if self.l2_cache and self.config.enable_l2_cache:
                try:
                    test_key = f"health_check_{int(time.time())}"
                    await self.l2_cache.set(test_key, "test", 10)
                    await self.l2_cache.delete(test_key)
                except Exception as e:
                    logger.warning(f"L2 cache health check failed: {e}")
                    l2_healthy = False
            
            self.stats["last_health_check"] = datetime.utcnow()
            
            # Consider healthy if at least one level is working
            return l1_healthy or l2_healthy
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def _health_monitor(self) -> None:
        """Background health monitoring"""
        while self.state == ConnectionState.ACTIVE:
            try:
                is_healthy = await self.health_check()
                if not is_healthy:
                    logger.warning("Cache pool health check failed")
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache health monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _metrics_collector(self) -> None:
        """Background metrics collection"""
        while self.state == ConnectionState.ACTIVE:
            try:
                # Collect metrics from cache levels
                await self._collect_metrics()
                await asyncio.sleep(60)  # Collect every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self) -> None:
        """Collect detailed metrics from all cache levels"""
        try:
            # Update hit rates and performance metrics
            total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
            if total_requests > 0:
                hit_rate = self.stats["cache_hits"] / total_requests
                self.stats["hit_rate"] = hit_rate
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache pool statistics"""
        pool_stats = {
            "l1_enabled": self.config.enable_l1_cache,
            "l2_enabled": self.config.enable_l2_cache,
            "serialization_method": self.config.serialization_method.value,
            "compression_enabled": self.config.compression_enabled,
            "state": self.state.value
        }
        
        # Add cache level specific stats
        if self.l1_cache:
            pool_stats["l1_stats"] = self.l1_cache.get_stats()
        
        if self.l2_cache:
            try:
                # This needs to be called in async context
                l2_stats = asyncio.create_task(self.l2_cache.get_stats())
                pool_stats["l2_stats"] = l2_stats
            except:
                pool_stats["l2_stats"] = {"error": "Unable to collect L2 stats"}
        
        pool_stats.update(self.stats)
        return pool_stats
    
    async def close(self) -> None:
        """Close cache pool"""
        try:
            self.state = ConnectionState.CLOSED
            
            # Cancel background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            if self._metrics_collection_task:
                self._metrics_collection_task.cancel()
                try:
                    await self._metrics_collection_task
                except asyncio.CancelledError:
                    pass
            
            # Close cache connections
            if self.l2_cache:
                await self.l2_cache.close()
            
            # Clear L1 cache
            if self.l1_cache:
                self.l1_cache.clear()
            
            logger.info("✅ Advanced cache pool closed")
            
        except Exception as e:
            logger.error(f"Error closing cache pool: {e}")

# =============== EXPORTS ===============

__all__ = [
    "AdvancedCacheConnectionPool",
    "CacheConfig",
    "CacheLevel",
    "CacheStrategy",
    "SerializationMethod",
    "EvictionPolicy",
    "CacheItem",
    "L1MemoryCache",
    "L2RedisCache"
]
