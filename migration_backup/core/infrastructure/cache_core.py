"""Ainflue Core Cache - Enterprise Caching System
============================================

Advanced caching management providing Redis-based distributed caching,
memory caching, cache invalidation strategies, and performance optimization
for the Ainflue platform core engine.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import pickle
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
import hashlib

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)

class CacheType(str, Enum):
    """Cache storage types"""
    REDIS = "redis"
    MEMORY = "memory"
    HYBRID = "hybrid"

class CacheStrategy(str, Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out

@dataclass
class CacheConfig:
    """Cache configuration"""
    cache_type: CacheType = CacheType.REDIS
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    max_memory_items: int = 10000
    default_ttl: int = 3600  # 1 hour
    max_ttl: int = 86400  # 24 hours
    strategy: CacheStrategy = CacheStrategy.LRU
    compression: bool = True
    serialization: str = "json"  # json, pickle
    cluster_mode: bool = False
    connection_timeout: int = 5
    retry_attempts: int = 3

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    memory_usage_bytes: int = 0
    items_count: int = 0
    avg_access_time: float = 0.0
    hit_ratio: float = 0.0
    uptime_seconds: int = 0
    last_health_check: float = field(default_factory=time.time)

class CacheCore:
    """Enterprise cache core management system"""
    
    def __init__(self, config: Optional[CacheConfig] = None, level: str = "enterprise"):
        """Initialize cache core"""
        self.config = config or CacheConfig()
        self.level = level
        self.metrics = CacheMetrics()
        self.start_time = time.time()
        
        # Cache backends
        self.redis_client: Optional[Any] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_access_times: Dict[str, float] = {}
        self.memory_access_counts: Dict[str, int] = {}
        
        # Health monitoring
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Cache invalidation
        self.invalidation_patterns: Dict[str, List[str]] = {}
        self.cache_dependencies: Dict[str, List[str]] = {}
    
    async def initialize(self) -> bool:
        """Initialize cache system"""
        try:
            logger.info(f"🚀 Initializing cache core - Type: {self.config.cache_type.value}")
            
            if self.config.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                await self._initialize_redis()
            
            logger.info("✅ Cache core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache initialization failed: {str(e)}")
            return False
    
    async def _initialize_redis(self) -> bool:
        """Initialize Redis connection"""
        try:
            if redis:
                connection_kwargs = {
                    "host": self.config.redis_host,
                    "port": self.config.redis_port,
                    "db": self.config.redis_db,
                    "decode_responses": True,
                    "socket_timeout": self.config.connection_timeout,
                    "retry_on_timeout": True
                }
                
                if self.config.redis_password:
                    connection_kwargs["password"] = self.config.redis_password
                
                if self.config.redis_ssl:
                    connection_kwargs["ssl"] = True
                
                self.redis_client = redis.Redis(**connection_kwargs)
                
                # Test connection
                await self.redis_client.ping()
                logger.info("✅ Redis connection established")
                return True
            else:
                logger.warning("⚠️ Redis not available, using memory cache only")
                return True
                
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            if self.config.cache_type == CacheType.REDIS:
                raise
            return False
    
    async def start(self) -> bool:
        """Start cache core"""
        try:
            if not hasattr(self, '_initialized'):
                await self.initialize()
                self._initialized = True
            
            # Start health monitoring
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            logger.info("🚀 Cache core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache core start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop cache core"""
        try:
            logger.info("🛑 Stopping cache core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel health monitoring
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("✅ Cache core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache core stop failed: {str(e)}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        start_time = time.time()
        
        try:
            # Try Redis first (if available and configured)
            if self.redis_client and self.config.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                value = await self._get_from_redis(key)
                if value is not None:
                    self.metrics.hits += 1
                    self._update_access_time(start_time)
                    return value
            
            # Try memory cache
            if self.config.cache_type in [CacheType.MEMORY, CacheType.HYBRID]:
                value = self._get_from_memory(key)
                if value is not None:
                    self.metrics.hits += 1
                    self._update_access_time(start_time)
                    return value
            
            self.metrics.misses += 1
            self._update_access_time(start_time)
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            self.metrics.misses += 1
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.config.default_ttl
            ttl = min(ttl, self.config.max_ttl)
            
            # Store in Redis (if available and configured)
            if self.redis_client and self.config.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                await self._set_in_redis(key, value, ttl)
            
            # Store in memory cache
            if self.config.cache_type in [CacheType.MEMORY, CacheType.HYBRID]:
                self._set_in_memory(key, value, ttl)
            
            self.metrics.sets += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            deleted = False
            
            # Delete from Redis
            if self.redis_client and self.config.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                result = await self.redis_client.delete(key)
                deleted = deleted or bool(result)
            
            # Delete from memory cache
            if self.config.cache_type in [CacheType.MEMORY, CacheType.HYBRID]:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    self.memory_access_times.pop(key, None)
                    self.memory_access_counts.pop(key, None)
                    deleted = True
            
            if deleted:
                self.metrics.deletes += 1
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            # Clear Redis
            if self.redis_client and self.config.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                await self.redis_client.flushdb()
            
            # Clear memory cache
            if self.config.cache_type in [CacheType.MEMORY, CacheType.HYBRID]:
                self.memory_cache.clear()
                self.memory_access_times.clear()
                self.memory_access_counts.clear()
            
            logger.info("🧹 Cache cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    async def _get_from_redis(self, key: str) -> Any:
        """Get value from Redis"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            return self._deserialize(value)
            
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in Redis"""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = self._serialize(value)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    def _get_from_memory(self, key: str) -> Any:
        """Get value from memory cache"""
        if key not in self.memory_cache:
            return None
        
        cache_item = self.memory_cache[key]
        
        # Check TTL
        if time.time() > cache_item["expires_at"]:
            del self.memory_cache[key]
            self.memory_access_times.pop(key, None)
            self.memory_access_counts.pop(key, None)
            self.metrics.evictions += 1
            return None
        
        # Update access statistics
        self.memory_access_times[key] = time.time()
        self.memory_access_counts[key] = self.memory_access_counts.get(key, 0) + 1
        
        return cache_item["value"]
    
    def _set_in_memory(self, key: str, value: Any, ttl: int):
        """Set value in memory cache"""
        # Check memory limits
        if len(self.memory_cache) >= self.config.max_memory_items:
            self._evict_memory_items()
        
        expires_at = time.time() + ttl
        self.memory_cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time()
        }
        
        self.memory_access_times[key] = time.time()
        self.memory_access_counts[key] = 1
    
    def _evict_memory_items(self):
        """Evict items from memory cache based on strategy"""
        if not self.memory_cache:
            return
        
        items_to_remove = max(1, len(self.memory_cache) // 10)  # Remove 10%
        
        if self.config.strategy == CacheStrategy.LRU:
            # Remove least recently used
            sorted_keys = sorted(
                self.memory_access_times.keys(),
                key=lambda k: self.memory_access_times[k]
            )
        elif self.config.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            sorted_keys = sorted(
                self.memory_access_counts.keys(),
                key=lambda k: self.memory_access_counts[k]
            )
        elif self.config.strategy == CacheStrategy.FIFO:
            # Remove oldest items
            sorted_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]["created_at"]
            )
        else:  # TTL
            # Remove items expiring soonest
            sorted_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]["expires_at"]
            )
        
        for key in sorted_keys[:items_to_remove]:
            self.memory_cache.pop(key, None)
            self.memory_access_times.pop(key, None)
            self.memory_access_counts.pop(key, None)
            self.metrics.evictions += 1
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        if self.config.serialization == "json":
            return json.dumps(value, default=str)
        elif self.config.serialization == "pickle":
            return pickle.dumps(value).hex()
        else:
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            if self.config.serialization == "json":
                return json.loads(value)
            elif self.config.serialization == "pickle":
                return pickle.loads(bytes.fromhex(value))
            else:
                return value
        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            return value
    
    def _update_access_time(self, start_time: float):
        """Update average access time metric"""
        access_time = time.time() - start_time
        total_operations = self.metrics.hits + self.metrics.misses
        
        if total_operations > 0:
            self.metrics.avg_access_time = (
                (self.metrics.avg_access_time * (total_operations - 1) + access_time) /
                total_operations
            )
    
    async def health_check(self) -> bool:
        """Perform cache health check"""
        try:
            # Test Redis if available
            if self.redis_client and self.config.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                await self.redis_client.ping()
            
            # Update metrics
            total_operations = self.metrics.hits + self.metrics.misses
            if total_operations > 0:
                self.metrics.hit_ratio = self.metrics.hits / total_operations
            
            self.metrics.items_count = len(self.memory_cache)
            self.metrics.uptime_seconds = int(time.time() - self.start_time)
            self.metrics.last_health_check = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache health monitor error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_metrics(self) -> CacheMetrics:
        """Get current cache metrics"""
        return self.metrics
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get cache status summary"""
        return {
            "cache_type": self.config.cache_type.value,
            "strategy": self.config.strategy.value,
            "uptime_seconds": int(time.time() - self.start_time),
            "hits": self.metrics.hits,
            "misses": self.metrics.misses,
            "hit_ratio": round(self.metrics.hit_ratio * 100, 2),
            "items_count": self.metrics.items_count,
            "memory_items": len(self.memory_cache),
            "evictions": self.metrics.evictions,
            "avg_access_time_ms": round(self.metrics.avg_access_time * 1000, 2)
        }

# Module exports
__all__ = [
    "CacheCore", "CacheConfig", "CacheMetrics", 
    "CacheType", "CacheStrategy"
]