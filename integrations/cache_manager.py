"""Integration Response Caching System
====================================

High-performance caching system for integration responses with TTL, 
invalidation strategies, and distributed caching support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, Optional, Any, Union, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import pickle
import gzip
import redis.asyncio as redis


class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


class CacheLevel(Enum):
    """Cache level enumeration"""
    MEMORY = "memory"
    REDIS = "redis"
    BOTH = "both"


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl: int = 300  # Default TTL in seconds
    max_size: int = 1000  # Maximum cache size
    strategy: CacheStrategy = CacheStrategy.LRU
    level: CacheLevel = CacheLevel.MEMORY
    compress: bool = False  # Compress cached data
    serialize_json: bool = True  # JSON serialization
    key_prefix: str = "ainflue:cache"


@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = None
    size_bytes: int = 0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at:
            return datetime.utcnow() >= self.expires_at
        return False
    
    @property
    def age_seconds(self) -> float:
        """Get entry age in seconds"""
        return (datetime.utcnow() - self.created_at).total_seconds()


class IntegrationCacheManager:
    """Integration response caching system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None,
                 default_config: Optional[CacheConfig] = None):
        """Initialize cache manager
        
        Args:
            redis_client: Redis client for distributed caching
            default_config: Default cache configuration
        """
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis_client
        self.default_config = default_config or CacheConfig()
        
        # Memory cache storage
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # Per-integration configurations
        self.integration_configs: Dict[str, CacheConfig] = {}
        
        # Cache statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "memory_hits": 0,
            "redis_hits": 0,
            "evictions": 0,
            "errors": 0,
            "total_size_bytes": 0
        }
        
        # Access tracking for LRU/LFU
        self.access_order = []  # For LRU
        self.access_frequency = {}  # For LFU
        
        # Background cleanup task
        self._cleanup_task = None
        self._running = False
    
    async def start(self):
        """Start cache manager background tasks"""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
            self.logger.info("Cache manager started")
    
    async def shutdown(self):
        """Shutdown cache manager"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close Redis connection if exists
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Cache manager shutdown complete")
    
    def configure_integration(self, integration_name: str, config: CacheConfig):
        """Configure caching for specific integration
        
        Args:
            integration_name: Integration name
            config: Cache configuration
        """
        self.integration_configs[integration_name] = config
        self.logger.info(f"Configured caching for integration: {integration_name}")
    
    def _get_config(self, integration_name: Optional[str] = None) -> CacheConfig:
        """Get cache configuration for integration
        
        Args:
            integration_name: Integration name
            
        Returns:
            CacheConfig: Cache configuration
        """
        if integration_name and integration_name in self.integration_configs:
            return self.integration_configs[integration_name]
        return self.default_config
    
    def _generate_cache_key(self, integration_name: str, method: str, 
                          args: tuple = (), kwargs: dict = None) -> str:
        """Generate cache key
        
        Args:
            integration_name: Integration name
            method: Method name
            args: Method arguments
            kwargs: Method keyword arguments
            
        Returns:
            str: Cache key
        """
        # Create deterministic key
        key_data = {
            "integration": integration_name,
            "method": method,
            "args": args,
            "kwargs": kwargs or {}
        }
        
        # Serialize and hash
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        config = self._get_config(integration_name)
        return f"{config.key_prefix}:{integration_name}:{method}:{key_hash}"
    
    async def get(self, key: str, integration_name: Optional[str] = None) -> Optional[Any]:
        """Get value from cache
        
        Args:
            key: Cache key
            integration_name: Integration name for configuration
            
        Returns:
            Optional[Any]: Cached value or None
        """
        try:
            self.stats["total_requests"] += 1
            
            config = self._get_config(integration_name)
            
            # Try memory cache first
            if config.level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
                memory_result = await self._get_from_memory(key)
                if memory_result is not None:
                    self.stats["cache_hits"] += 1
                    self.stats["memory_hits"] += 1
                    return memory_result
            
            # Try Redis cache
            if config.level in [CacheLevel.REDIS, CacheLevel.BOTH] and self.redis_client:
                redis_result = await self._get_from_redis(key, config)
                if redis_result is not None:
                    self.stats["cache_hits"] += 1
                    self.stats["redis_hits"] += 1
                    
                    # Store in memory cache if using both levels
                    if config.level == CacheLevel.BOTH:
                        await self._store_in_memory(key, redis_result, config)
                    
                    return redis_result
            
            # Cache miss
            self.stats["cache_misses"] += 1
            return None
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                integration_name: Optional[str] = None):
        """Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            integration_name: Integration name for configuration
        """
        try:
            config = self._get_config(integration_name)
            cache_ttl = ttl or config.ttl
            
            # Store in memory cache
            if config.level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
                await self._store_in_memory(key, value, config, cache_ttl)
            
            # Store in Redis cache
            if config.level in [CacheLevel.REDIS, CacheLevel.BOTH] and self.redis_client:
                await self._store_in_redis(key, value, config, cache_ttl)
                
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Cache set error for key {key}: {e}")
    
    async def delete(self, key: str, integration_name: Optional[str] = None):
        """Delete value from cache
        
        Args:
            key: Cache key
            integration_name: Integration name for configuration
        """
        try:
            config = self._get_config(integration_name)
            
            # Delete from memory cache
            if config.level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
                await self._delete_from_memory(key)
            
            # Delete from Redis cache
            if config.level in [CacheLevel.REDIS, CacheLevel.BOTH] and self.redis_client:
                await self._delete_from_redis(key)
                
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Cache delete error for key {key}: {e}")
    
    async def clear(self, integration_name: Optional[str] = None):
        """Clear cache for integration or all
        
        Args:
            integration_name: Integration name (None for all)
        """
        try:
            if integration_name:
                # Clear specific integration
                pattern = f"*:{integration_name}:*"
                await self._clear_by_pattern(pattern)
            else:
                # Clear all
                self.memory_cache.clear()
                self.access_order.clear()
                self.access_frequency.clear()
                
                if self.redis_client:
                    await self.redis_client.flushdb()
            
            self.logger.info(f"Cache cleared for: {integration_name or 'all'}")
            
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Cache clear error: {e}")
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from memory cache
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Any]: Cached value or None
        """
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            # Check expiration
            if entry.is_expired:
                await self._delete_from_memory(key)
                return None
            
            # Update access tracking
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            
            # Update LRU order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            # Update LFU frequency
            self.access_frequency[key] = entry.access_count
            
            return entry.value
        
        return None
    
    async def _store_in_memory(self, key: str, value: Any, config: CacheConfig, 
                             ttl: Optional[int] = None):
        """Store value in memory cache
        
        Args:
            key: Cache key
            value: Value to cache
            config: Cache configuration
            ttl: Time to live in seconds
        """
        # Calculate expiration
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        # Calculate size
        try:
            if config.serialize_json:
                serialized = json.dumps(value, default=str)
            else:
                serialized = pickle.dumps(value)
            
            if config.compress:
                serialized = gzip.compress(serialized.encode() if isinstance(serialized, str) else serialized)
            
            size_bytes = len(serialized)
        except Exception:
            size_bytes = len(str(value))
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            size_bytes=size_bytes
        )
        
        # Check cache size limits
        if len(self.memory_cache) >= config.max_size:
            await self._evict_memory_entry(config)
        
        # Store entry
        self.memory_cache[key] = entry
        
        # Update tracking
        self.access_order.append(key)
        self.access_frequency[key] = 0
        
        # Update statistics
        self.stats["total_size_bytes"] += size_bytes
    
    async def _get_from_redis(self, key: str, config: CacheConfig) -> Optional[Any]:
        """Get value from Redis cache
        
        Args:
            key: Cache key
            config: Cache configuration
            
        Returns:
            Optional[Any]: Cached value or None
        """
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return None
            
            # Decompress if needed
            if config.compress:
                data = gzip.decompress(data)
            
            # Deserialize
            if config.serialize_json:
                return json.loads(data.decode())
            else:
                return pickle.loads(data)
                
        except Exception as e:
            self.logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def _store_in_redis(self, key: str, value: Any, config: CacheConfig, 
                            ttl: Optional[int] = None):
        """Store value in Redis cache
        
        Args:
            key: Cache key
            value: Value to cache
            config: Cache configuration
            ttl: Time to live in seconds
        """
        try:
            # Serialize
            if config.serialize_json:
                data = json.dumps(value, default=str).encode()
            else:
                data = pickle.dumps(value)
            
            # Compress if needed
            if config.compress:
                data = gzip.compress(data)
            
            # Store with TTL
            cache_ttl = ttl or config.ttl
            await self.redis_client.setex(key, cache_ttl, data)
            
        except Exception as e:
            self.logger.error(f"Redis set error for key {key}: {e}")
    
    async def _delete_from_memory(self, key: str):
        """Delete value from memory cache
        
        Args:
            key: Cache key
        """
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            self.stats["total_size_bytes"] -= entry.size_bytes
            del self.memory_cache[key]
        
        if key in self.access_order:
            self.access_order.remove(key)
        
        if key in self.access_frequency:
            del self.access_frequency[key]
    
    async def _delete_from_redis(self, key: str):
        """Delete value from Redis cache
        
        Args:
            key: Cache key
        """
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            self.logger.error(f"Redis delete error for key {key}: {e}")
    
    async def _evict_memory_entry(self, config: CacheConfig):
        """Evict entry from memory cache based on strategy
        
        Args:
            config: Cache configuration
        """
        if not self.memory_cache:
            return
        
        if config.strategy == CacheStrategy.LRU:
            # Remove least recently used
            if self.access_order:
                oldest_key = self.access_order[0]
                await self._delete_from_memory(oldest_key)
                self.stats["evictions"] += 1
        
        elif config.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            if self.access_frequency:
                lfu_key = min(self.access_frequency.items(), key=lambda x: x[1])[0]
                await self._delete_from_memory(lfu_key)
                self.stats["evictions"] += 1
        
        elif config.strategy == CacheStrategy.TTL:
            # Remove expired entries first
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry.is_expired
            ]
            if expired_keys:
                for key in expired_keys:
                    await self._delete_from_memory(key)
                    self.stats["evictions"] += 1
            else:
                # Fallback to LRU
                if self.access_order:
                    oldest_key = self.access_order[0]
                    await self._delete_from_memory(oldest_key)
                    self.stats["evictions"] += 1
        
        elif config.strategy == CacheStrategy.FIFO:
            # Remove first inserted
            if self.memory_cache:
                oldest_key = next(iter(self.memory_cache))
                await self._delete_from_memory(oldest_key)
                self.stats["evictions"] += 1
    
    async def _clear_by_pattern(self, pattern: str):
        """Clear cache entries by pattern
        
        Args:
            pattern: Key pattern to match
        """
        # Clear from memory cache
        keys_to_remove = []
        for key in self.memory_cache:
            if self._matches_pattern(key, pattern):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            await self._delete_from_memory(key)
        
        # Clear from Redis cache
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            except Exception as e:
                self.logger.error(f"Redis clear pattern error: {e}")
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern
        
        Args:
            key: Cache key
            pattern: Pattern to match
            
        Returns:
            bool: Whether key matches pattern
        """
        # Simple wildcard matching
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    async def _background_cleanup(self):
        """Background task for cache cleanup"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Clean expired entries from memory
                expired_keys = []
                for key, entry in self.memory_cache.items():
                    if entry.is_expired:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self._delete_from_memory(key)
                
                if expired_keys:
                    self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except Exception as e:
                self.logger.error(f"Background cleanup error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        stats = self.stats.copy()
        
        # Calculate hit rates
        total_requests = stats["total_requests"]
        if total_requests > 0:
            stats["hit_rate"] = stats["cache_hits"] / total_requests
            stats["miss_rate"] = stats["cache_misses"] / total_requests
        else:
            stats["hit_rate"] = 0.0
            stats["miss_rate"] = 0.0
        
        # Memory cache stats
        stats["memory_entries"] = len(self.memory_cache)
        stats["memory_size_bytes"] = stats["total_size_bytes"]
        
        # Redis stats
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
                stats["redis_memory_usage"] = redis_info.get("used_memory", 0)
            except Exception:
                stats["redis_memory_usage"] = 0
        
        stats["timestamp"] = datetime.utcnow().isoformat()
        
        return stats
    
    async def cache_function(self, integration_name: str, method_name: str,
                           func: Callable, *args, **kwargs) -> Any:
        """Cache function result
        
        Args:
            integration_name: Integration name
            method_name: Method name
            func: Function to cache
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result (cached or fresh)
        """
        # Generate cache key
        cache_key = self._generate_cache_key(integration_name, method_name, args, kwargs)
        
        # Try to get from cache
        cached_result = await self.get(cache_key, integration_name)
        if cached_result is not None:
            return cached_result
        
        # Execute function
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # Store in cache
        await self.set(cache_key, result, integration_name=integration_name)
        
        return result


# Global cache manager instance
cache_manager = IntegrationCacheManager()


async def get_cache_manager() -> IntegrationCacheManager:
    """Get global cache manager instance
    
    Returns:
        IntegrationCacheManager: Global instance
    """
    return cache_manager