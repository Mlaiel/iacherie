"""
Database Cache Management - IA Influencer Agent Platform
Enterprise-grade caching layer with multiple backends and intelligent strategies

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

import asyncio
import redis
import memcache
import pickle
import json
import zlib
import hashlib
from typing import Optional, Any, Dict, List, Union, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging
from contextlib import asynccontextmanager

from ..core.config import get_settings
from ..core.logging import get_logger
from .connection import DatabaseConnection

logger = get_logger(__name__)
settings = get_settings()

T = TypeVar('T')


class CacheLevel(Enum):
    """Cache level enumeration for multi-tier caching"""
    L1_MEMORY = "l1_memory"        # In-process memory cache
    L2_REDIS = "l2_redis"          # Redis distributed cache
    L3_DATABASE = "l3_database"    # Database query result cache


class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"                    # Time-to-live expiration
    LRU = "lru"                    # Least recently used
    LFU = "lfu"                    # Least frequently used
    WRITE_THROUGH = "write_through"  # Write to cache and storage
    WRITE_BEHIND = "write_behind"    # Async write to storage
    REFRESH_AHEAD = "refresh_ahead"  # Pre-refresh before expiry


@dataclass
class CacheConfig:
    """Cache configuration parameters"""
    default_ttl: int = 3600        # Default TTL in seconds
    max_memory_size: int = 1000    # Max items in memory cache
    compression_threshold: int = 1024  # Compress data above this size
    serialization_format: str = "pickle"  # pickle, json, msgpack
    key_prefix: str = "ia_agent"
    enable_compression: bool = True
    enable_encryption: bool = False
    stats_collection: bool = True


@dataclass
class CacheStats:
    """Cache statistics and metrics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    total_keys: int = 0
    hit_rate: float = 0.0
    avg_access_time: float = 0.0
    last_reset: datetime = None


class CacheSerializer:
    """Cache data serialization handler"""
    
    @staticmethod
    def serialize(data: Any, format: str = "pickle", compress: bool = True) -> bytes:
        """Serialize data with optional compression"""



        try:
            if format == "pickle":
                serialized = pickle.dumps(data)
            elif format == "json":
                serialized = json.dumps(data, default=str).encode('utf-8')
            else:
                raise ValueError(f"Unsupported serialization format: {format}")
            
            if compress and len(serialized) > 1024:
                serialized = zlib.compress(serialized)
                return b"compressed:" + serialized
            
            return serialized
            
        except Exception as e:
            logger.error(f"Cache serialization error: {e}")
            raise
    
    @staticmethod
    def deserialize(data: bytes, format: str = "pickle") -> Any:
        """Deserialize data with decompression support"""



        try:
            # Check if data is compressed
            if data.startswith(b"compressed:"):
                data = zlib.decompress(data[11:])  # Remove "compressed:" prefix
            
            if format == "pickle":
                return pickle.loads(data)
            elif format == "json":
                return json.loads(data.decode('utf-8'))
            else:
                raise ValueError(f"Unsupported serialization format: {format}")
                
        except Exception as e:
            logger.error(f"Cache deserialization error: {e}")
            raise


class CacheBackend(ABC):
    """Abstract cache backend interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all keys"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend with LRU eviction"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, datetime] = {}
        self.access_counts: Dict[str, int] = {}
        self.stats = CacheStats(last_reset=datetime.utcnow())
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        async with self._lock:
            if key in self.cache:
                self.access_times[key] = datetime.utcnow()
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                self.stats.hits += 1
                return self.cache[key]
            else:
                self.stats.misses += 1
                return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache with LRU eviction"""
        async with self._lock:
            try:
                # Check if we need to evict items
                if len(self.cache) >= self.config.max_memory_size and key not in self.cache:
                    await self._evict_lru()
                
                self.cache[key] = value
                self.access_times[key] = datetime.utcnow()
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                return True
                
            except Exception as e:
                logger.error(f"Memory cache set error: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from memory cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
                del self.access_counts[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache"""



        return key in self.cache
    
    async def clear(self) -> bool:
        """Clear memory cache"""
        async with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.access_counts.clear()
            self.stats = CacheStats(last_reset=datetime.utcnow())
            return True
    
    async def get_stats(self) -> CacheStats:
        """Get memory cache statistics"""
        self.stats.total_keys = len(self.cache)
        self.stats.hit_rate = (
            self.stats.hits / (self.stats.hits + self.stats.misses)
            if (self.stats.hits + self.stats.misses) > 0 else 0.0
        )
        return self.stats
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # Remove from all structures
        del self.cache[lru_key]
        del self.access_times[lru_key]
        del self.access_counts[lru_key]
        
        self.stats.evictions += 1


class RedisCache(CacheBackend):
    """Redis distributed cache backend"""
    
    def __init__(self, config: CacheConfig, connection: redis.Redis):
        self.config = config
        self.redis = connection
        self.serializer = CacheSerializer()
        self.stats = CacheStats(last_reset=datetime.utcnow())
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""



        return f"{self.config.key_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""



        try:
            redis_key = self._make_key(key)
            data = await self.redis.get(redis_key)
            
            if data:
                self.stats.hits += 1
                return self.serializer.deserialize(
                    data, self.config.serialization_format
                )
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            self.stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""



        try:
            redis_key = self._make_key(key)
            serialized_value = self.serializer.serialize(
                value, 
                self.config.serialization_format,
                self.config.enable_compression
            )
            
            ttl = ttl or self.config.default_ttl
            
            result = await self.redis.setex(redis_key, ttl, serialized_value)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""



        try:
            redis_key = self._make_key(key)
            result = await self.redis.delete(redis_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""



        try:
            redis_key = self._make_key(key)
            return bool(await self.redis.exists(redis_key))
            
        except Exception as e:
            logger.error(f"Redis cache exists error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear Redis cache (pattern-based)"""



        try:
            pattern = f"{self.config.key_prefix}:*"
            cursor = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
            
            self.stats = CacheStats(last_reset=datetime.utcnow())
            return True
            
        except Exception as e:
            logger.error(f"Redis cache clear error: {e}")
            return False
    
    async def get_stats(self) -> CacheStats:
        """Get Redis cache statistics"""



        try:
            info = await self.redis.info()
            self.stats.memory_usage = info.get('used_memory', 0)
            
            # Count keys with our prefix
            pattern = f"{self.config.key_prefix}:*"
            cursor = 0
            key_count = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                key_count += len(keys)
                if cursor == 0:
                    break
            
            self.stats.total_keys = key_count
            self.stats.hit_rate = (
                self.stats.hits / (self.stats.hits + self.stats.misses)
                if (self.stats.hits + self.stats.misses) > 0 else 0.0
            )
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return self.stats


class DatabaseCache:
    """
    Multi-tier cache manager with intelligent caching strategies
    Supports L1 (memory) -> L2 (Redis) -> L3 (Database) hierarchy
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.l1_cache: Optional[MemoryCache] = None
        self.l2_cache: Optional[RedisCache] = None
        self.db_connection: Optional[DatabaseConnection] = None
        self.cache_strategies: Dict[str, CacheStrategy] = {}
        self.key_patterns: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache backends"""
        if self._initialized:
            return
        
        try:
            # Initialize L1 memory cache
            self.l1_cache = MemoryCache(self.config)
            logger.info("L1 memory cache initialized")
            
            # Initialize L2 Redis cache
            db_connection = await DatabaseConnection.get_instance()
            redis_conn = db_connection.connections.get('redis_primary')
            
            if redis_conn:
                self.l2_cache = RedisCache(self.config, redis_conn)
                logger.info("L2 Redis cache initialized")
            
            self.db_connection = db_connection
            self._initialized = True
            
            logger.info("Database cache system initialized successfully")
            
        except Exception as e:
            logger.error(f"Cache initialization error: {e}")
            raise
    
    def register_key_pattern(self, 
                           pattern: str, 
                           strategy: CacheStrategy = CacheStrategy.TTL,
                           ttl: Optional[int] = None,
                           levels: List[CacheLevel] = None):
        """Register caching strategy for key patterns"""
        self.key_patterns[pattern] = {
            'strategy': strategy,
            'ttl': ttl or self.config.default_ttl,
            'levels': levels or [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        }
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value with multi-tier cache lookup"""



        try:
            pattern_config = self._get_pattern_config(key)
            levels = pattern_config.get('levels', [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS])
            
            # Try L1 cache first
            if CacheLevel.L1_MEMORY in levels and self.l1_cache:
                value = await self.l1_cache.get(key)
                if value is not None:
                    logger.debug(f"Cache L1 hit: {key}")
                    return value
            
            # Try L2 cache
            if CacheLevel.L2_REDIS in levels and self.l2_cache:
                value = await self.l2_cache.get(key)
                if value is not None:
                    logger.debug(f"Cache L2 hit: {key}")
                    
                    # Populate L1 cache
                    if CacheLevel.L1_MEMORY in levels and self.l1_cache:
                        await self.l1_cache.set(key, value, pattern_config.get('ttl'))
                    
                    return value
            
            # Cache miss
            logger.debug(f"Cache miss: {key}")
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(self, 
                 key: str, 
                 value: Any, 
                 ttl: Optional[int] = None,
                 levels: Optional[List[CacheLevel]] = None) -> bool:
        """Set value in specified cache levels"""



        try:
            pattern_config = self._get_pattern_config(key)
            cache_levels = levels or pattern_config.get('levels', [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS])
            cache_ttl = ttl or pattern_config.get('ttl', self.config.default_ttl)
            
            success = True
            
            # Set in L1 cache
            if CacheLevel.L1_MEMORY in cache_levels and self.l1_cache:
                l1_success = await self.l1_cache.set(key, value, cache_ttl)
                success = success and l1_success
            
            # Set in L2 cache
            if CacheLevel.L2_REDIS in cache_levels and self.l2_cache:
                l2_success = await self.l2_cache.set(key, value, cache_ttl)
                success = success and l2_success
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""



        try:
            success = True
            
            if self.l1_cache:
                l1_success = await self.l1_cache.delete(key)
                success = success and l1_success
            
            if self.l2_cache:
                l2_success = await self.l2_cache.delete(key)
                success = success and l2_success
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> bool:
        """Clear cache keys matching pattern"""



        try:
            # For simplicity, clear entire cache
            # In production, implement pattern-based clearing
            success = True
            
            if self.l1_cache:
                l1_success = await self.l1_cache.clear()
                success = success and l1_success
            
            if self.l2_cache:
                l2_success = await self.l2_cache.clear()
                success = success and l2_success
            
            return success
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False
    
    async def get_combined_stats(self) -> Dict[str, CacheStats]:
        """Get statistics from all cache levels"""
        stats = {}
        
        try:
            if self.l1_cache:
                stats['l1_memory'] = await self.l1_cache.get_stats()
            
            if self.l2_cache:
                stats['l2_redis'] = await self.l2_cache.get_stats()
            
            return stats
            
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}
    
    def _get_pattern_config(self, key: str) -> Dict[str, Any]:
        """Get configuration for key pattern"""
        for pattern, config in self.key_patterns.items():
            if pattern in key or key.startswith(pattern):
                return config
        
        # Return default configuration
        return {
            'strategy': CacheStrategy.TTL,
            'ttl': self.config.default_ttl,
            'levels': [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        }


class QueryCache:
    """Database query result caching with intelligent invalidation"""
    
    def __init__(self, database_cache: DatabaseCache):
        self.cache = database_cache
        self.query_dependencies: Dict[str, List[str]] = {}  # query -> [table1, table2, ...]
        self.table_queries: Dict[str, List[str]] = {}       # table -> [query1, query2, ...]
    
    async def get_query_result(self, 
                              query_hash: str, 
                              tables: List[str],
                              default: Any = None) -> Any:
        """Get cached query result"""
        cache_key = f"query:{query_hash}"
        
        # Register query dependencies
        self.query_dependencies[query_hash] = tables
        for table in tables:
            if table not in self.table_queries:
                self.table_queries[table] = []
            if query_hash not in self.table_queries[table]:
                self.table_queries[table].append(query_hash)
        
        return await self.cache.get(cache_key, default)
    
    async def cache_query_result(self, 
                               query_hash: str, 
                               result: Any,
                               ttl: Optional[int] = None) -> bool:
        """Cache query result"""
        cache_key = f"query:{query_hash}"
        return await self.cache.set(cache_key, result, ttl)
    
    async def invalidate_table_queries(self, table_name: str) -> bool:
        """Invalidate all queries that depend on a table"""
        if table_name not in self.table_queries:
            return True
        
        success = True
        for query_hash in self.table_queries[table_name]:
            cache_key = f"query:{query_hash}"
            query_success = await self.cache.delete(cache_key)
            success = success and query_success
        
        # Clear tracking
        del self.table_queries[table_name]
        
        return success


class ResultSetCache:
    """Cache for paginated result sets and aggregations"""
    
    def __init__(self, database_cache: DatabaseCache):
        self.cache = database_cache
    
    async def get_result_set(self, 
                           key: str, 
                           page: int = 1, 
                           page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Get cached result set page"""
        cache_key = f"resultset:{key}:p{page}:s{page_size}"
        return await self.cache.get(cache_key)
    
    async def cache_result_set(self, 
                             key: str, 
                             page: int, 
                             page_size: int,
                             data: Dict[str, Any],
                             ttl: Optional[int] = None) -> bool:
        """Cache result set page"""
        cache_key = f"resultset:{key}:p{page}:s{page_size}"
        return await self.cache.set(cache_key, data, ttl)
    
    async def invalidate_result_set(self, key: str) -> bool:
        """Invalidate all pages of a result set"""
        pattern = f"resultset:{key}:*"
        return await self.cache.clear_pattern(pattern)


# Global cache instance
_cache_instance: Optional[DatabaseCache] = None


async def get_cache() -> DatabaseCache:
    """Get global cache instance"""
    global _cache_instance
    
    if _cache_instance is None:
        config = CacheConfig(
            default_ttl=settings.CACHE_DEFAULT_TTL,
            max_memory_size=settings.CACHE_MAX_MEMORY_SIZE,
            compression_threshold=settings.CACHE_COMPRESSION_THRESHOLD,
            key_prefix=settings.CACHE_KEY_PREFIX
        )
        
        _cache_instance = DatabaseCache(config)
        await _cache_instance.initialize()
        
        # Register common cache patterns
        _cache_instance.register_key_pattern(
            "user:", 
            CacheStrategy.TTL, 
            ttl=1800,  # 30 minutes
            levels=[CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        )
        
        _cache_instance.register_key_pattern(
            "content:", 
            CacheStrategy.TTL, 
            ttl=3600,  # 1 hour
            levels=[CacheLevel.L2_REDIS]
        )
        
        _cache_instance.register_key_pattern(
            "analytics:", 
            CacheStrategy.TTL, 
            ttl=300,   # 5 minutes
            levels=[CacheLevel.L1_MEMORY]
        )
    
    return _cache_instance


# Convenience functions
async def cache_get(key: str, default: Any = None) -> Any:
    """Get value from cache"""
    cache = await get_cache()
    return await cache.get(key, default)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache"""
    cache = await get_cache()
    return await cache.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    """Delete key from cache"""
    cache = await get_cache()
    return await cache.delete(key)
