"""{{service_name}} Cache Service Template for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Backend Senior Role: Enterprise cache service with comprehensive caching strategies
"""

import logging
import asyncio
import json
import pickle
import hashlib
import time
from typing import Dict, Any, List, Optional, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, asdict
import zlib
from concurrent.futures import ThreadPoolExecutor

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import aioredis

from core.config import get_settings
from utils.exceptions import ServiceError
from utils.serialization import JSONEncoder

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class CacheError(ServiceError):
    """Cache service specific error"""
    pass


class CacheBackend(str, Enum):
    """Supported cache backends"""
    REDIS = "redis"
    MEMORY = "memory"
    HYBRID = "hybrid"


class CacheStrategy(str, Enum):
    """Cache strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"


class SerializationMethod(str, Enum):
    """Serialization methods"""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    COMPRESSED_JSON = "compressed_json"
    COMPRESSED_PICKLE = "compressed_pickle"


@dataclass
class CacheConfig:
    """Cache configuration"""
    backend: CacheBackend = CacheBackend.REDIS
    strategy: CacheStrategy = CacheStrategy.LRU
    serialization: SerializationMethod = SerializationMethod.JSON
    default_ttl: int = 3600  # 1 hour
    max_memory: int = 100 * 1024 * 1024  # 100MB
    compression_threshold: int = 1024  # Compress if larger than 1KB
    key_prefix: str = "ainflue"
    namespace_separator: str = ":"
    enable_stats: bool = True
    
    # Redis specific
    redis_url: Optional[str] = None
    redis_pool_size: int = 10
    redis_db: int = 0
    
    # Memory cache specific
    memory_max_items: int = 10000


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_size: int = 0
    
    @property
    def hit_ratio(self) -> float:
        """Calculate hit ratio"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'hit_ratio': self.hit_ratio
        }


class CacheItem(Generic[T]):
    """Cache item wrapper"""
    
    def __init__(
        self,
        value: T,
        ttl: Optional[int] = None,
        created_at: Optional[datetime] = None,
        access_count: int = 0,
        last_accessed: Optional[datetime] = None
    ):
        self.value = value
        self.ttl = ttl
        self.created_at = created_at or datetime.utcnow()
        self.access_count = access_count
        self.last_accessed = last_accessed or datetime.utcnow()
    
    @property
    def is_expired(self) -> bool:
        """Check if item is expired"""
        if self.ttl is None:
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl)
        return datetime.utcnow() > expiry_time
    
    def access(self):
        """Mark item as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'value': self.value,
            'ttl': self.ttl,
            'created_at': self.created_at.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheItem':
        """Create from dictionary"""
        return cls(
            value=data['value'],
            ttl=data['ttl'],
            created_at=datetime.fromisoformat(data['created_at']),
            access_count=data['access_count'],
            last_accessed=datetime.fromisoformat(data['last_accessed'])
        )


class Serializer:
    """Data serialization utilities"""
    
    @staticmethod
    def serialize(
        data: Any,
        method: SerializationMethod = SerializationMethod.JSON,
        compress: bool = False
    ) -> bytes:
        """Serialize data to bytes"""
        try:
            if method == SerializationMethod.JSON:
                serialized = json.dumps(data, cls=JSONEncoder).encode('utf-8')
            elif method == SerializationMethod.PICKLE:
                serialized = pickle.dumps(data)
            elif method == SerializationMethod.COMPRESSED_JSON:
                json_data = json.dumps(data, cls=JSONEncoder).encode('utf-8')
                serialized = zlib.compress(json_data)
            elif method == SerializationMethod.COMPRESSED_PICKLE:
                pickle_data = pickle.dumps(data)
                serialized = zlib.compress(pickle_data)
            elif method == SerializationMethod.MSGPACK:
                try:
                    import msgpack
                    serialized = msgpack.packb(data)
                except ImportError:
                    logger.warning("msgpack not available, falling back to JSON")
                    serialized = json.dumps(data, cls=JSONEncoder).encode('utf-8')
            else:
                raise CacheError(f"Unsupported serialization method: {method}")
            
            # Apply compression if requested and beneficial
            if compress and len(serialized) > 1024:
                compressed = zlib.compress(serialized)
                if len(compressed) < len(serialized) * 0.9:  # At least 10% reduction
                    return b'compressed:' + compressed
            
            return serialized
            
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            raise CacheError(f"Serialization failed: {str(e)}")
    
    @staticmethod
    def deserialize(
        data: bytes,
        method: SerializationMethod = SerializationMethod.JSON
    ) -> Any:
        """Deserialize bytes to data"""
        try:
            # Check for compression
            if data.startswith(b'compressed:'):
                data = zlib.decompress(data[11:])  # Remove 'compressed:' prefix
            
            if method == SerializationMethod.JSON:
                return json.loads(data.decode('utf-8'))
            elif method == SerializationMethod.PICKLE:
                return pickle.loads(data)
            elif method == SerializationMethod.COMPRESSED_JSON:
                decompressed = zlib.decompress(data)
                return json.loads(decompressed.decode('utf-8'))
            elif method == SerializationMethod.COMPRESSED_PICKLE:
                decompressed = zlib.decompress(data)
                return pickle.loads(decompressed)
            elif method == SerializationMethod.MSGPACK:
                try:
                    import msgpack
                    return msgpack.unpackb(data)
                except ImportError:
                    logger.warning("msgpack not available, falling back to JSON")
                    return json.loads(data.decode('utf-8'))
            else:
                raise CacheError(f"Unsupported serialization method: {method}")
                
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            raise CacheError(f"Deserialization failed: {str(e)}")


class MemoryCache:
    """In-memory cache implementation with LRU/LFU strategies"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, CacheItem] = {}
        self._access_order: List[str] = []  # For LRU
        self._lock = asyncio.Lock()
        self._stats = CacheStats()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            item = self._cache[key]
            
            # Check expiration
            if item.is_expired:
                await self._delete_key(key)
                self._stats.misses += 1
                return None
            
            # Update access tracking
            item.access()
            self._update_access_order(key)
            
            self._stats.hits += 1
            return item.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        async with self._lock:
            try:
                # Create cache item
                item = CacheItem(value, ttl or self.config.default_ttl)
                
                # Check memory limits
                await self._ensure_capacity()
                
                # Store item
                self._cache[key] = item
                self._update_access_order(key)
                
                self._stats.sets += 1
                self._stats.total_size += len(str(value))
                
                return True
                
            except Exception as e:
                logger.error(f"Memory cache set failed: {e}")
                self._stats.errors += 1
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        async with self._lock:
            return await self._delete_key(key)
    
    async def clear(self) -> bool:
        """Clear entire cache"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._stats.total_size = 0
            return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        async with self._lock:
            if key not in self._cache:
                return False
            
            item = self._cache[key]
            if item.is_expired:
                await self._delete_key(key)
                return False
            
            return True
    
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self._stats
    
    async def _delete_key(self, key: str) -> bool:
        """Internal delete method"""
        if key in self._cache:
            item = self._cache[key]
            self._stats.total_size -= len(str(item.value))
            del self._cache[key]
            
            if key in self._access_order:
                self._access_order.remove(key)
            
            self._stats.deletes += 1
            return True
        
        return False
    
    def _update_access_order(self, key: str):
        """Update access order for LRU"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    async def _ensure_capacity(self):
        """Ensure cache doesn't exceed capacity"""
        # Check item count limit
        while len(self._cache) >= self.config.memory_max_items:
            await self._evict_item()
        
        # Check memory limit
        while self._stats.total_size > self.config.max_memory:
            await self._evict_item()
    
    async def _evict_item(self):
        """Evict item based on strategy"""
        if not self._cache:
            return
        
        if self.config.strategy == CacheStrategy.LRU:
            # Remove least recently used
            if self._access_order:
                lru_key = self._access_order[0]
                await self._delete_key(lru_key)
        
        elif self.config.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            lfu_key = min(self._cache.keys(), 
                         key=lambda k: self._cache[k].access_count)
            await self._delete_key(lfu_key)
        
        elif self.config.strategy == CacheStrategy.TTL:
            # Remove expired items first, then oldest
            expired_keys = [k for k, v in self._cache.items() if v.is_expired]
            if expired_keys:
                await self._delete_key(expired_keys[0])
            else:
                oldest_key = min(self._cache.keys(),
                               key=lambda k: self._cache[k].created_at)
                await self._delete_key(oldest_key)


class RedisCache:
    """Redis cache implementation"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._redis: Optional[redis.Redis] = None
        self._stats = CacheStats()
        self._serializer = Serializer()
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            if self.config.redis_url:
                self._redis = redis.from_url(
                    self.config.redis_url,
                    db=self.config.redis_db,
                    max_connections=self.config.redis_pool_size
                )
            else:
                # Use default connection
                self._redis = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=self.config.redis_db,
                    max_connections=self.config.redis_pool_size
                )
            
            # Test connection
            await self._redis.ping()
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise CacheError(f"Redis initialization failed: {str(e)}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            prefixed_key = self._get_prefixed_key(key)
            data = await self._redis.get(prefixed_key)
            
            if data is None:
                self._stats.misses += 1
                return None
            
            # Deserialize
            value = self._serializer.deserialize(data, self.config.serialization)
            
            self._stats.hits += 1
            return value
            
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
            self._stats.errors += 1
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in Redis"""
        try:
            prefixed_key = self._get_prefixed_key(key)
            
            # Serialize
            compress = len(str(value)) > self.config.compression_threshold
            serialized = self._serializer.serialize(
                value, 
                self.config.serialization,
                compress
            )
            
            # Set with TTL
            ttl_seconds = ttl or self.config.default_ttl
            result = await self._redis.setex(prefixed_key, ttl_seconds, serialized)
            
            if result:
                self._stats.sets += 1
                self._stats.total_size += len(serialized)
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis set failed: {e}")
            self._stats.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis"""
        try:
            prefixed_key = self._get_prefixed_key(key)
            result = await self._redis.delete(prefixed_key)
            
            if result:
                self._stats.deletes += 1
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis delete failed: {e}")
            self._stats.errors += 1
            return False
    
    async def clear(self) -> bool:
        """Clear cache (with prefix)"""
        try:
            pattern = f"{self.config.key_prefix}*"
            keys = await self._redis.keys(pattern)
            
            if keys:
                result = await self._redis.delete(*keys)
                return bool(result)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis clear failed: {e}")
            self._stats.errors += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            prefixed_key = self._get_prefixed_key(key)
            result = await self._redis.exists(prefixed_key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis exists failed: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value"""
        try:
            prefixed_key = self._get_prefixed_key(key)
            result = await self._redis.incrby(prefixed_key, amount)
            return int(result)
            
        except Exception as e:
            logger.error(f"Redis increment failed: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for existing key"""
        try:
            prefixed_key = self._get_prefixed_key(key)
            result = await self._redis.expire(prefixed_key, ttl)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis expire failed: {e}")
            return False
    
    async def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self._stats
    
    def _get_prefixed_key(self, key: str) -> str:
        """Get key with prefix"""
        return f"{self.config.key_prefix}{self.config.namespace_separator}{key}"


class {{service_name}}CacheService:
    """{{service_description}}
    
    Enterprise cache service providing:
    - Multiple backend support (Redis, Memory, Hybrid)
    - Advanced serialization with compression
    - Cache strategies (LRU, LFU, TTL)
    - Statistics and monitoring
    - Distributed caching support
    - Pattern-based invalidation
    - Namespace management
    - Performance optimization
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._memory_cache: Optional[MemoryCache] = None
        self._redis_cache: Optional[RedisCache] = None
        self._initialized = False
        
        # Namespace management
        self._namespaces: Dict[str, CacheConfig] = {}
        
        # Background task for cleanup
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize cache service"""
        try:
            if self.config.backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
                self._redis_cache = RedisCache(self.config)
                await self._redis_cache.initialize()
            
            if self.config.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
                self._memory_cache = MemoryCache(self.config)
            
            # Start background cleanup task
            if self._memory_cache:
                self._cleanup_task = asyncio.create_task(self._cleanup_expired())
            
            self._initialized = True
            logger.info(f"Cache service initialized with backend: {self.config.backend}")
            
        except Exception as e:
            logger.error(f"Cache service initialization failed: {e}")
            raise CacheError(f"Initialization failed: {str(e)}")
    
    async def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """Get value from cache"""
        if not self._initialized:
            await self.initialize()
        
        try:
            full_key = self._build_key(key, namespace)
            
            # Try memory cache first (if hybrid)
            if self.config.backend == CacheBackend.HYBRID and self._memory_cache:
                value = await self._memory_cache.get(full_key)
                if value is not None:
                    return value
            
            # Try primary cache
            cache = self._get_primary_cache()
            if cache:
                value = await cache.get(full_key)
                
                # Store in memory cache for hybrid mode
                if (value is not None and 
                    self.config.backend == CacheBackend.HYBRID and 
                    self._memory_cache):
                    await self._memory_cache.set(full_key, value)
                
                return value if value is not None else default
            
            return default
            
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: Optional[str] = None
    ) -> bool:
        """Set value in cache"""
        if not self._initialized:
            await self.initialize()
        
        try:
            full_key = self._build_key(key, namespace)
            ttl = ttl or self.config.default_ttl
            
            success = True
            
            # Set in primary cache
            cache = self._get_primary_cache()
            if cache:
                success = await cache.set(full_key, value, ttl)
            
            # Set in memory cache for hybrid mode
            if (self.config.backend == CacheBackend.HYBRID and 
                self._memory_cache and success):
                await self._memory_cache.set(full_key, value, ttl)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(
        self,
        key: str,
        namespace: Optional[str] = None
    ) -> bool:
        """Delete value from cache"""
        if not self._initialized:
            await self.initialize()
        
        try:
            full_key = self._build_key(key, namespace)
            
            success = True
            
            # Delete from all caches
            if self._redis_cache:
                success = await self._redis_cache.delete(full_key) and success
            
            if self._memory_cache:
                success = await self._memory_cache.delete(full_key) and success
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def clear(self, namespace: Optional[str] = None) -> bool:
        """Clear cache or namespace"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if namespace:
                # Clear specific namespace
                pattern = f"{namespace}*"
                return await self._clear_pattern(pattern)
            else:
                # Clear all caches
                success = True
                
                if self._redis_cache:
                    success = await self._redis_cache.clear() and success
                
                if self._memory_cache:
                    success = await self._memory_cache.clear() and success
                
                return success
                
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    async def exists(
        self,
        key: str,
        namespace: Optional[str] = None
    ) -> bool:
        """Check if key exists in cache"""
        if not self._initialized:
            await self.initialize()
        
        try:
            full_key = self._build_key(key, namespace)
            
            # Check memory cache first
            if self._memory_cache:
                if await self._memory_cache.exists(full_key):
                    return True
            
            # Check Redis cache
            if self._redis_cache:
                return await self._redis_cache.exists(full_key)
            
            return False
            
        except Exception as e:
            logger.error(f"Cache exists failed for key {key}: {e}")
            return False
    
    async def get_many(
        self,
        keys: List[str],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        
        for key in keys:
            value = await self.get(key, namespace)
            if value is not None:
                result[key] = value
        
        return result
    
    async def set_many(
        self,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
        namespace: Optional[str] = None
    ) -> bool:
        """Set multiple values in cache"""
        success = True
        
        for key, value in data.items():
            result = await self.set(key, value, ttl, namespace)
            success = success and result
        
        return success
    
    async def increment(
        self,
        key: str,
        amount: int = 1,
        namespace: Optional[str] = None
    ) -> Optional[int]:
        """Increment a numeric value"""
        if not self._initialized:
            await self.initialize()
        
        if self._redis_cache:
            full_key = self._build_key(key, namespace)
            return await self._redis_cache.increment(full_key, amount)
        
        # Fallback for memory cache
        current = await self.get(key, namespace) or 0
        new_value = current + amount
        await self.set(key, new_value, namespace=namespace)
        return new_value
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'backend': self.config.backend.value,
            'initialized': self._initialized
        }
        
        if self._redis_cache:
            redis_stats = await self._redis_cache.get_stats()
            stats['redis'] = redis_stats.to_dict()
        
        if self._memory_cache:
            memory_stats = await self._memory_cache.get_stats()
            stats['memory'] = memory_stats.to_dict()
        
        return stats
    
    async def create_namespace(
        self,
        namespace: str,
        config: Optional[CacheConfig] = None
    ) -> bool:
        """Create a cache namespace with specific configuration"""
        try:
            namespace_config = config or self.config
            self._namespaces[namespace] = namespace_config
            
            logger.info(f"Created cache namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create namespace {namespace}: {e}")
            return False
    
    def _build_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Build full cache key with namespace"""
        if namespace:
            return f"{namespace}{self.config.namespace_separator}{key}"
        return key
    
    def _get_primary_cache(self) -> Optional[Union[RedisCache, MemoryCache]]:
        """Get primary cache based on backend configuration"""
        if self.config.backend == CacheBackend.REDIS:
            return self._redis_cache
        elif self.config.backend == CacheBackend.MEMORY:
            return self._memory_cache
        elif self.config.backend == CacheBackend.HYBRID:
            return self._redis_cache or self._memory_cache
        
        return None
    
    async def _clear_pattern(self, pattern: str) -> bool:
        """Clear keys matching pattern"""
        # This would need implementation based on backend
        # For now, return True
        return True
    
    async def _cleanup_expired(self):
        """Background task to cleanup expired items"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                if self._memory_cache:
                    # Cleanup expired items in memory cache
                    expired_keys = []
                    for key, item in self._memory_cache._cache.items():
                        if item.is_expired:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        await self._memory_cache.delete(key)
                
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
    
    async def shutdown(self):
        """Shutdown cache service"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        if self._redis_cache and self._redis_cache._redis:
            await self._redis_cache._redis.close()
        
        logger.info("Cache service shutdown completed")


# Decorator for caching function results
def cache_result(
    ttl: int = 3600,
    namespace: Optional[str] = None,
    key_prefix: Optional[str] = None
):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cache_service = get_cache_service()  # Implement this
            cached_result = await cache_service.get(cache_key, namespace)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl, namespace)
            
            return result
        
        return wrapper
    return decorator


# Factory function
def create_cache_service(config: Optional[CacheConfig] = None) -> {{service_name}}CacheService:
    """Create cache service instance"""
    if config is None:
        config = CacheConfig(
            backend=CacheBackend.REDIS,
            redis_url=getattr(settings, 'REDIS_URL', None),
            default_ttl=getattr(settings, 'CACHE_DEFAULT_TTL', 3600)
        )
    
    return {{service_name}}CacheService(config)


# Export service class
__all__ = [
    'CacheError',
    'CacheBackend',
    'CacheStrategy',
    'SerializationMethod',
    'CacheConfig',
    'CacheStats',
    'CacheItem',
    'Serializer',
    'MemoryCache',
    'RedisCache',
    '{{service_name}}CacheService',
    'cache_result',
    'create_cache_service'
]