"""
Performance Cache Engine - Industrial Redis-Based Optimization

High-performance caching system with Redis integration, intelligent cache
strategies, and advanced performance optimization for payment operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import json
import hashlib
import pickle
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass, field
import time

import redis.asyncio as aioredis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from .config import PaymentConfig
from .exceptions import PaymentProcessingError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheLevel(str, Enum):
    """Cache level priorities"""
    L1_MEMORY = "l1_memory"      # In-process memory cache
    L2_REDIS = "l2_redis"        # Redis distributed cache
    L3_DATABASE = "l3_database"   # Database query cache


class CacheStrategy(str, Enum):
    """Caching strategies"""
    WRITE_THROUGH = "write_through"      # Write to cache and storage
    WRITE_BACK = "write_back"            # Write to cache, delayed storage
    WRITE_AROUND = "write_around"        # Write to storage, bypass cache
    READ_THROUGH = "read_through"        # Read from cache, fallback to storage
    CACHE_ASIDE = "cache_aside"          # Manual cache management


class CacheEvictionPolicy(str, Enum):
    """Cache eviction policies"""
    LRU = "lru"          # Least Recently Used
    LFU = "lfu"          # Least Frequently Used
    FIFO = "fifo"        # First In, First Out
    TTL = "ttl"          # Time To Live based
    RANDOM = "random"    # Random eviction


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_count: int = 0
    miss_count: int = 0
    write_count: int = 0
    eviction_count: int = 0
    error_count: int = 0
    total_latency: float = 0.0
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_reads = self.hit_count + self.miss_count
        return self.hit_count / total_reads if total_reads > 0 else 0.0
    
    @property
    def avg_latency(self) -> float:
        """Calculate average operation latency"""
        total_ops = self.hit_count + self.miss_count + self.write_count
        return self.total_latency / total_ops if total_ops > 0 else 0.0


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 1
    ttl: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)
    
    def touch(self):
        """Update access metadata"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1


class MemoryCache(Generic[T]):
    """In-memory L1 cache with LRU eviction"""
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300,  # 5 minutes
        eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.LRU
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []  # For LRU tracking
        self.metrics = CacheMetrics()
    
    async def get(self, key: str) -> Optional[T]:
        """Get value from memory cache"""
        start_time = time.time()
        
        try:
            if key in self._cache:
                entry = self._cache[key]
                
                # Check expiration
                if entry.is_expired():
                    await self.delete(key)
                    self.metrics.miss_count += 1
                    return None
                
                # Update access metadata
                entry.touch()
                self._update_access_order(key)
                
                self.metrics.hit_count += 1
                self.metrics.total_latency += time.time() - start_time
                return entry.value
            
            self.metrics.miss_count += 1
            self.metrics.total_latency += time.time() - start_time
            return None
            
        except Exception as e:
            logger.error(f"Memory cache get error for key {key}: {str(e)}")
            self.metrics.error_count += 1
            return None
    
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache"""
        start_time = time.time()
        
        try:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict()
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.default_ttl
            )
            
            self._cache[key] = entry
            self._update_access_order(key)
            
            self.metrics.write_count += 1
            self.metrics.total_latency += time.time() - start_time
            return True
            
        except Exception as e:
            logger.error(f"Memory cache set error for key {key}: {str(e)}")
            self.metrics.error_count += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        try:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
        except Exception as e:
            logger.error(f"Memory cache delete error for key {key}: {str(e)}")
            return False
    
    async def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._access_order.clear()
    
    def _update_access_order(self, key: str):
        """Update LRU access order"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    async def _evict(self):
        """Evict entries based on policy"""
        if not self._cache:
            return
        
        if self.eviction_policy == CacheEvictionPolicy.LRU:
            # Remove least recently used
            lru_key = self._access_order[0]
            await self.delete(lru_key)
        
        elif self.eviction_policy == CacheEvictionPolicy.LFU:
            # Remove least frequently used
            lfu_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
            await self.delete(lfu_key)
        
        elif self.eviction_policy == CacheEvictionPolicy.TTL:
            # Remove oldest entry by creation time
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            await self.delete(oldest_key)
        
        else:  # FIFO or RANDOM
            # Remove first inserted (FIFO behavior)
            first_key = next(iter(self._cache))
            await self.delete(first_key)
        
        self.metrics.eviction_count += 1


class RedisCache:
    """Redis-based L2 distributed cache"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,  # 1 hour
        key_prefix: str = "payment:",
        serializer: str = "json"  # json, pickle
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.serializer = serializer
        self.redis_client: Optional[aioredis.Redis] = None
        self.metrics = CacheMetrics()
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # We handle encoding ourselves
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache connected successfully")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
            raise PaymentProcessingError(f"Cache connection failed: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.redis_client:
            await self.connect()
        
        start_time = time.time()
        cache_key = f"{self.key_prefix}{key}"
        
        try:
            raw_value = await self.redis_client.get(cache_key)
            
            if raw_value is None:
                self.metrics.miss_count += 1
                self.metrics.total_latency += time.time() - start_time
                return None
            
            # Deserialize value
            value = self._deserialize(raw_value)
            
            self.metrics.hit_count += 1
            self.metrics.total_latency += time.time() - start_time
            return value
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(f"Redis get error for key {key}: {str(e)}")
            self.metrics.error_count += 1
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set value in Redis cache"""
        if not self.redis_client:
            await self.connect()
        
        start_time = time.time()
        cache_key = f"{self.key_prefix}{key}"
        ttl = ttl or self.default_ttl
        
        try:
            # Serialize value
            serialized_value = self._serialize(value)
            
            # Set value with TTL
            result = await self.redis_client.setex(cache_key, ttl, serialized_value)
            
            # Add to tag sets if provided
            if tags:
                for tag in tags:
                    await self.redis_client.sadd(f"{self.key_prefix}tag:{tag}", key)
                    await self.redis_client.expire(f"{self.key_prefix}tag:{tag}", ttl)
            
            self.metrics.write_count += 1
            self.metrics.total_latency += time.time() - start_time
            return bool(result)
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(f"Redis set error for key {key}: {str(e)}")
            self.metrics.error_count += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        if not self.redis_client:
            return False
        
        cache_key = f"{self.key_prefix}{key}"
        
        try:
            result = await self.redis_client.delete(cache_key)
            return result > 0
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False
    
    async def delete_by_tag(self, tag: str) -> int:
        """Delete all cached values with specific tag"""
        if not self.redis_client:
            return 0
        
        try:
            tag_key = f"{self.key_prefix}tag:{tag}"
            
            # Get all keys with this tag
            keys = await self.redis_client.smembers(tag_key)
            
            if not keys:
                return 0
            
            # Delete all keys
            cache_keys = [f"{self.key_prefix}{key.decode()}" for key in keys]
            deleted_count = await self.redis_client.delete(*cache_keys)
            
            # Clean up tag set
            await self.redis_client.delete(tag_key)
            
            return deleted_count
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(f"Redis delete by tag error for tag {tag}: {str(e)}")
            return 0
    
    async def clear_all(self) -> bool:
        """Clear all cache entries with our prefix"""
        if not self.redis_client:
            return False
        
        try:
            # Get all keys with our prefix
            pattern = f"{self.key_prefix}*"
            keys = []
            
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis_client.delete(*keys)
            
            return True
            
        except (RedisError, RedisConnectionError) as e:
            logger.error(f"Redis clear all error: {str(e)}")
            return False
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            if self.serializer == "json":
                # Handle Decimal serialization
                json_str = json.dumps(
                    value,
                    default=self._json_serializer,
                    ensure_ascii=False
                )
                return json_str.encode('utf-8')
            else:  # pickle
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization error: {str(e)}")
            raise
    
    def _deserialize(self, raw_value: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            if self.serializer == "json":
                json_str = raw_value.decode('utf-8')
                return json.loads(json_str, object_hook=self._json_deserializer)
            else:  # pickle
                return pickle.loads(raw_value)
        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            raise
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for complex types"""
        if isinstance(obj, Decimal):
            return {"__decimal__": str(obj)}
        elif isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        elif hasattr(obj, '__dict__'):
            return {"__object__": obj.__dict__}
        raise TypeError(f"Object {obj} is not JSON serializable")
    
    def _json_deserializer(self, obj: Dict[str, Any]) -> Any:
        """Custom JSON deserializer for complex types"""
        if "__decimal__" in obj:
            return Decimal(obj["__decimal__"])
        elif "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
        elif "__object__" in obj:
            return obj["__object__"]
        return obj


class PerformanceCache:
    """
    Multi-level performance cache system with intelligent routing.
    
    Implements L1 (memory) + L2 (Redis) caching with automatic
    promotion/demotion and cache warming strategies.
    """
    
    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        redis_url: Optional[str] = None,
        enable_l1: bool = True,
        enable_l2: bool = True
    ):
        self.config = config or PaymentConfig()
        
        # Initialize cache levels
        self.l1_cache = MemoryCache(max_size=1000) if enable_l1 else None
        self.l2_cache = RedisCache(
            redis_url or "redis://localhost:6379"
        ) if enable_l2 else None
        
        # Cache strategy settings
        self.strategy = CacheStrategy.READ_THROUGH
        self.l1_promotion_threshold = 3  # Promote to L1 after 3 L2 hits
        self.l2_hit_counts: Dict[str, int] = {}
        
        # Performance monitoring
        self.total_metrics = CacheMetrics()
        
        # Cache warming queues
        self.warming_queue: asyncio.Queue = asyncio.Queue()
        self.warming_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize cache system"""
        if self.l2_cache:
            await self.l2_cache.connect()
        
        # Start cache warming background task
        if not self.warming_task:
            self.warming_task = asyncio.create_task(self._cache_warming_worker())
        
        logger.info("Performance cache system initialized")
    
    async def shutdown(self):
        """Shutdown cache system"""
        if self.warming_task:
            self.warming_task.cancel()
            try:
                await self.warming_task
            except asyncio.CancelledError:
                pass
        
        if self.l2_cache:
            await self.l2_cache.disconnect()
        
        logger.info("Performance cache system shutdown")
    
    async def get(self, key: str, fetch_func: Optional[Callable] = None) -> Optional[Any]:
        """
        Get value from multi-level cache with read-through strategy.
        
        Args:
            key: Cache key
            fetch_func: Function to fetch data if not in cache
            
        Returns:
            Cached or fetched value
        """
        start_time = time.time()
        
        try:
            # Try L1 cache first
            if self.l1_cache:
                value = await self.l1_cache.get(key)
                if value is not None:
                    logger.debug(f"L1 cache hit for key: {key}")
                    self._update_total_metrics("hit", time.time() - start_time)
                    return value
            
            # Try L2 cache
            if self.l2_cache:
                value = await self.l2_cache.get(key)
                if value is not None:
                    logger.debug(f"L2 cache hit for key: {key}")
                    
                    # Track L2 hits for L1 promotion
                    self.l2_hit_counts[key] = self.l2_hit_counts.get(key, 0) + 1
                    
                    # Promote to L1 if threshold reached
                    if (self.l1_cache and 
                        self.l2_hit_counts[key] >= self.l1_promotion_threshold):
                        await self.l1_cache.set(key, value)
                        logger.debug(f"Promoted key to L1 cache: {key}")
                    
                    self._update_total_metrics("hit", time.time() - start_time)
                    return value
            
            # Cache miss - try to fetch from source
            if fetch_func:
                logger.debug(f"Cache miss - fetching from source: {key}")
                value = await fetch_func()
                if value is not None:
                    await self.set(key, value)
                    self._update_total_metrics("miss_fetch", time.time() - start_time)
                    return value
            
            self._update_total_metrics("miss", time.time() - start_time)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            self._update_total_metrics("error", time.time() - start_time)
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        level: Optional[CacheLevel] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Set value in multi-level cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            level: Specific cache level to set
            tags: Cache tags for invalidation
            
        Returns:
            Success status
        """
        start_time = time.time()
        success = False
        
        try:
            if level == CacheLevel.L1_MEMORY or level is None:
                if self.l1_cache:
                    success = await self.l1_cache.set(key, value, ttl) or success
            
            if level == CacheLevel.L2_REDIS or level is None:
                if self.l2_cache:
                    success = await self.l2_cache.set(key, value, ttl, tags) or success
            
            if success:
                self._update_total_metrics("write", time.time() - start_time)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            self._update_total_metrics("error", time.time() - start_time)
            return False
    
    async def delete(self, key: str, level: Optional[CacheLevel] = None) -> bool:
        """Delete value from cache"""
        success = False
        
        try:
            if level == CacheLevel.L1_MEMORY or level is None:
                if self.l1_cache:
                    success = await self.l1_cache.delete(key) or success
            
            if level == CacheLevel.L2_REDIS or level is None:
                if self.l2_cache:
                    success = await self.l2_cache.delete(key) or success
            
            # Clean up promotion tracking
            if key in self.l2_hit_counts:
                del self.l2_hit_counts[key]
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with specific tag"""
        total_deleted = 0
        
        if self.l2_cache:
            deleted = await self.l2_cache.delete_by_tag(tag)
            total_deleted += deleted
        
        # For L1 cache, we'd need to track tags separately
        # This is a simplified implementation
        
        return total_deleted
    
    async def warm_cache(self, key: str, fetch_func: Callable, ttl: Optional[int] = None):
        """Add cache warming request to queue"""
        try:
            await self.warming_queue.put({
                "key": key,
                "fetch_func": fetch_func,
                "ttl": ttl
            })
        except Exception as e:
            logger.error(f"Cache warming queue error: {str(e)}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics"""
        metrics = {
            "total": self.total_metrics.__dict__,
            "l1": None,
            "l2": None
        }
        
        if self.l1_cache:
            metrics["l1"] = self.l1_cache.metrics.__dict__
        
        if self.l2_cache:
            metrics["l2"] = self.l2_cache.metrics.__dict__
        
        return metrics
    
    def _update_total_metrics(self, operation: str, latency: float):
        """Update total cache metrics"""
        if operation == "hit":
            self.total_metrics.hit_count += 1
        elif operation in ("miss", "miss_fetch"):
            self.total_metrics.miss_count += 1
        elif operation == "write":
            self.total_metrics.write_count += 1
        elif operation == "error":
            self.total_metrics.error_count += 1
        
        self.total_metrics.total_latency += latency
    
    async def _cache_warming_worker(self):
        """Background worker for cache warming"""
        logger.info("Cache warming worker started")
        
        try:
            while True:
                try:
                    # Wait for warming request
                    request = await asyncio.wait_for(
                        self.warming_queue.get(),
                        timeout=60.0  # 1 minute timeout
                    )
                    
                    key = request["key"]
                    fetch_func = request["fetch_func"]
                    ttl = request.get("ttl")
                    
                    # Fetch and cache data
                    try:
                        value = await fetch_func()
                        if value is not None:
                            await self.set(key, value, ttl)
                            logger.debug(f"Cache warmed for key: {key}")
                    except Exception as e:
                        logger.error(f"Cache warming fetch error for {key}: {str(e)}")
                    
                    # Mark task done
                    self.warming_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # No warming requests - continue loop
                    continue
                    
        except asyncio.CancelledError:
            logger.info("Cache warming worker stopped")
            raise
        except Exception as e:
            logger.error(f"Cache warming worker error: {str(e)}")


# Utility functions for cache key generation
def generate_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate consistent cache key from arguments"""
    # Create key components
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
        else:
            key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float)):
            key_parts.append(f"{key}:{value}")
        else:
            value_hash = hashlib.md5(str(value).encode()).hexdigest()[:8]
            key_parts.append(f"{key}:{value_hash}")
    
    return ":".join(key_parts)


def cache_key_for_transaction(transaction_id: str) -> str:
    """Generate cache key for transaction data"""
    return generate_cache_key("transaction", transaction_id)


def cache_key_for_user_payments(user_id: str, limit: int = 10) -> str:
    """Generate cache key for user payment history"""
    return generate_cache_key("user_payments", user_id, limit=limit)


def cache_key_for_revenue_stats(creator_id: str, period: str) -> str:
    """Generate cache key for revenue statistics"""
    return generate_cache_key("revenue_stats", creator_id, period)
