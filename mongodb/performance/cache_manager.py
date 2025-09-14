"""MongoDB Cache Manager
======================

Multi-level caching system for MongoDB operations with intelligent cache invalidation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import time
import asyncio
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import redis
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache level enumeration."""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: Any
    timestamp: float
    ttl: int  # Time to live in seconds
    access_count: int = 0
    last_accessed: float = 0
    size_bytes: int = 0
    tags: List[str] = None

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []
        if self.last_accessed == 0:
            self.last_accessed = self.timestamp

@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    hit_ratio: float = 0.0
    memory_usage_bytes: int = 0
    redis_usage_bytes: int = 0
    disk_usage_bytes: int = 0

class CacheManager:
    """Advanced multi-level cache manager for MongoDB operations."""
    
    def __init__(self, 
                 memory_limit_mb -> None: int = 100,
                 redis_config -> None: Optional[Dict[str, Any]] = None,
                 disk_cache_dir -> None: Optional[str] = None,
                 default_ttl -> None: int = 3600) -> None:
        """Initialize cache manager.
        
        Args:
            memory_limit_mb: Memory cache limit in MB
            redis_config: Redis configuration dictionary
            disk_cache_dir: Directory for disk cache
            default_ttl: Default TTL in seconds
        """
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.default_ttl = default_ttl
        
        # Memory cache
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._memory_usage = 0
        
        # Redis cache
        self._redis_client = None
        if redis_config:
            try:
                self._redis_client = redis.Redis(**redis_config)
                self._redis_client.ping()
                logger.info("Redis cache connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
        
        # Disk cache
        self._disk_cache_dir = disk_cache_dir
        if disk_cache_dir:
            import os
            os.makedirs(disk_cache_dir, exist_ok=True)
        
        # Statistics
        self._stats = CacheStats()
        
        # Background cleanup
        self._cleanup_executor = ThreadPoolExecutor(max_workers=1)
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
        
        # Cache invalidation callbacks
        self._invalidation_callbacks: Dict[str, List[Callable]] = {}
        
    def get(self, key: str, collection_name: str = None) -> Optional[Any]:
        """Get value from cache with multi-level lookup.
        
        Args:
            key: Cache key
            collection_name: Collection name for tagging
            
        Returns:
            Cached value or None if not found
        """
        self._stats.total_requests += 1
        
        # Try memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if self._is_valid(entry):
                entry.access_count += 1
                entry.last_accessed = time.time()
                self._stats.hits += 1
                logger.debug(f"Cache HIT (memory): {key}")
                return entry.data
            else:
                # Expired entry
                del self._memory_cache[key]
                self._memory_usage -= entry.size_bytes
        
        # Try Redis cache
        if self._redis_client:
            try:
                redis_data = self._redis_client.get(f"cache:{key}")
                if redis_data:
                    entry_dict = json.loads(redis_data)
                    entry = CacheEntry(**entry_dict)
                    if self._is_valid(entry):
                        # Promote to memory cache
                        self._set_memory_cache(key, entry)
                        self._stats.hits += 1
                        logger.debug(f"Cache HIT (redis): {key}")
                        return entry.data
                    else:
                        # Expired entry
                        self._redis_client.delete(f"cache:{key}")
            except Exception as e:
                logger.warning(f"Redis cache read error: {e}")
        
        # Try disk cache
        if self._disk_cache_dir:
            try:
                cache_file = self._get_disk_cache_path(key)
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        entry_dict = json.load(f)
                    entry = CacheEntry(**entry_dict)
                    if self._is_valid(entry):
                        # Promote to memory and Redis
                        self._set_memory_cache(key, entry)
                        if self._redis_client:
                            self._set_redis_cache(key, entry)
                        self._stats.hits += 1
                        logger.debug(f"Cache HIT (disk): {key}")
                        return entry.data
                    else:
                        # Expired entry
                        cache_file.unlink()
            except Exception as e:
                logger.warning(f"Disk cache read error: {e}")
        
        # Cache miss
        self._stats.misses += 1
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            tags: List[str] = None, collection_name: str = None) -> bool:
        """Set value in cache with multi-level storage.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Cache tags for invalidation
            collection_name: Collection name for tagging
            
        Returns:
            True if successfully cached
        """
        if ttl is None:
            ttl = self.default_ttl
        
        if tags is None:
            tags = []
        
        if collection_name:
            tags.append(f"collection:{collection_name}")
        
        # Create cache entry
        timestamp = time.time()
        data_size = self._calculate_size(value)
        
        entry = CacheEntry(
            data=value,
            timestamp=timestamp,
            ttl=ttl,
            size_bytes=data_size,
            tags=tags
        )
        
        # Set in memory cache
        self._set_memory_cache(key, entry)
        
        # Set in Redis cache
        if self._redis_client:
            self._set_redis_cache(key, entry)
        
        # Set in disk cache
        if self._disk_cache_dir:
            self._set_disk_cache(key, entry)
        
        logger.debug(f"Cache SET: {key} (size: {data_size} bytes, ttl: {ttl}s)")
        return True
    
    def invalidate(self, key: str) -> bool:
        """Invalidate specific cache entry.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if entry was found and invalidated
        """
        found = False
        
        # Remove from memory
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            self._memory_usage -= entry.size_bytes
            del self._memory_cache[key]
            found = True
        
        # Remove from Redis
        if self._redis_client:
            try:
                result = self._redis_client.delete(f"cache:{key}")
                if result > 0:
                    found = True
            except Exception as e:
                logger.warning(f"Redis invalidation error: {e}")
        
        # Remove from disk
        if self._disk_cache_dir:
            try:
                cache_file = self._get_disk_cache_path(key)
                if cache_file.exists():
                    cache_file.unlink()
                    found = True
            except Exception as e:
                logger.warning(f"Disk cache invalidation error: {e}")
        
        if found:
            logger.debug(f"Cache INVALIDATE: {key}")
            
            # Execute invalidation callbacks
            if key in self._invalidation_callbacks:
                for callback in self._invalidation_callbacks[key]:
                    try:
                        callback(key)
                    except Exception as e:
                        logger.error(f"Invalidation callback error: {e}")
        
        return found
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with specific tag.
        
        Args:
            tag: Tag to invalidate
            
        Returns:
            Number of entries invalidated
        """
        invalidated = 0
        
        # Find keys with tag in memory cache
        keys_to_invalidate = []
        for key, entry in self._memory_cache.items():
            if tag in entry.tags:
                keys_to_invalidate.append(key)
        
        # Invalidate found keys
        for key in keys_to_invalidate:
            if self.invalidate(key):
                invalidated += 1
        
        # For Redis and disk, we'd need to scan all keys (expensive operation)
        # In production, consider using Redis tag-based invalidation patterns
        
        logger.info(f"Cache INVALIDATE BY TAG '{tag}': {invalidated} entries")
        return invalidated
    
    def invalidate_collection(self, collection_name: str) -> int:
        """Invalidate all cache entries for a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Number of entries invalidated
        """
        return self.invalidate_by_tag(f"collection:{collection_name}")
    
    def clear(self, level: Optional[CacheLevel] = None) -> bool:
        """Clear cache at specific level or all levels.
        
        Args:
            level: Cache level to clear, or None for all levels
            
        Returns:
            True if successful
        """
        if level is None or level == CacheLevel.MEMORY:
            self._memory_cache.clear()
            self._memory_usage = 0
            logger.info("Memory cache cleared")
        
        if level is None or level == CacheLevel.REDIS:
            if self._redis_client:
                try:
                    # Delete all cache keys
                    keys = self._redis_client.keys("cache:*")
                    if keys:
                        self._redis_client.delete(*keys)
                    logger.info("Redis cache cleared")
                except Exception as e:
                    logger.error(f"Redis clear error: {e}")
                    return False
        
        if level is None or level == CacheLevel.DISK:
            if self._disk_cache_dir:
                try:
                    import shutil
                    from pathlib import Path
                    
                    cache_dir = Path(self._disk_cache_dir)
                    if cache_dir.exists():
                        shutil.rmtree(cache_dir)
                        cache_dir.mkdir(exist_ok=True)
                    logger.info("Disk cache cleared")
                except Exception as e:
                    logger.error(f"Disk cache clear error: {e}")
                    return False
        
        return True
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics.
        
        Returns:
            Cache statistics
        """
        # Update hit ratio
        if self._stats.total_requests > 0:
            self._stats.hit_ratio = self._stats.hits / self._stats.total_requests
        
        # Update memory usage
        self._stats.memory_usage_bytes = self._memory_usage
        
        # Update Redis usage
        if self._redis_client:
            try:
                info = self._redis_client.info()
                self._stats.redis_usage_bytes = info.get('used_memory', 0)
            except Exception:
                pass
        
        # Update disk usage
        if self._disk_cache_dir:
            try:
                from pathlib import Path
                cache_dir = Path(self._disk_cache_dir)
                if cache_dir.exists():
                    disk_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                    self._stats.disk_usage_bytes = disk_size
            except Exception:
                pass
        
        return self._stats
    
    def warmup_collection(self, collection: Collection, queries: List[Dict[str, Any]],
                         ttl: Optional[int] = None) -> int:
        """Warm up cache with common queries for a collection.
        
        Args:
            collection: MongoDB collection
            queries: List of queries to pre-cache
            ttl: Cache TTL for warmed entries
            
        Returns:
            Number of entries cached
        """
        cached = 0
        collection_name = collection.name
        
        for query in queries:
            try:
                # Execute query
                results = list(collection.find(query))
                
                # Generate cache key
                cache_key = self._generate_cache_key(collection_name, "find", query)
                
                # Cache results
                if self.set(cache_key, results, ttl=ttl, collection_name=collection_name):
                    cached += 1
                    
            except Exception as e:
                logger.error(f"Cache warmup error for query {query}: {e}")
        
        logger.info(f"Cache warmup complete: {cached} entries cached for '{collection_name}'")
        return cached
    
    def register_invalidation_callback(self, key: str, callback: Callable) -> None:
        """Register callback for cache invalidation events.
        
        Args:
            key: Cache key to monitor
            callback: Callback function to execute on invalidation
        """
        if key not in self._invalidation_callbacks:
            self._invalidation_callbacks[key] = []
        self._invalidation_callbacks[key].append(callback)
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries.
        
        Returns:
            Number of entries cleaned up
        """
        current_time = time.time()
        
        # Skip if cleanup ran recently
        if current_time - self._last_cleanup < self._cleanup_interval:
            return 0
        
        self._last_cleanup = current_time
        cleaned = 0
        
        # Clean memory cache
        expired_keys = []
        for key, entry in self._memory_cache.items():
            if not self._is_valid(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            entry = self._memory_cache[key]
            self._memory_usage -= entry.size_bytes
            del self._memory_cache[key]
            cleaned += 1
            self._stats.evictions += 1
        
        logger.debug(f"Cache cleanup: {cleaned} expired entries removed")
        return cleaned
    
    def _set_memory_cache(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in memory cache with eviction."""
        # Check if we need to evict entries
        while (self._memory_usage + entry.size_bytes > self.memory_limit_bytes 
               and self._memory_cache):
            self._evict_lru_entry()
        
        # Set new entry
        self._memory_cache[key] = entry
        self._memory_usage += entry.size_bytes
        return True
    
    def _set_redis_cache(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in Redis cache."""
        try:
            # Convert entry to JSON
            entry_dict = asdict(entry)
            redis_data = json.dumps(entry_dict, default=str)
            
            # Set with TTL
            self._redis_client.setex(f"cache:{key}", entry.ttl, redis_data)
            return True
        except Exception as e:
            logger.warning(f"Redis cache set error: {e}")
            return False
    
    def _set_disk_cache(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in disk cache."""
        try:
            cache_file = self._get_disk_cache_path(key)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            entry_dict = asdict(entry)
            with open(cache_file, 'w') as f:
                json.dump(entry_dict, f, default=str)
            return True
        except Exception as e:
            logger.warning(f"Disk cache set error: {e}")
            return False
    
    def _evict_lru_entry(self) -> None:
        """Evict least recently used entry from memory."""
        if not self._memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(self._memory_cache.keys(),
                     key=lambda k: self._memory_cache[k].last_accessed)
        
        # Remove LRU entry
        entry = self._memory_cache[lru_key]
        self._memory_usage -= entry.size_bytes
        del self._memory_cache[lru_key]
        self._stats.evictions += 1
        
        logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def _is_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid."""
        current_time = time.time()
        return (current_time - entry.timestamp) < entry.ttl
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        try:
            import sys
            if hasattr(value, '__sizeof__'):
                return sys.getsizeof(value)
            else:
                # Fallback: use JSON string length
                return len(json.dumps(value, default=str).encode('utf-8'))
        except Exception:
            return 1024  # Default size estimate
    
    def _get_disk_cache_path(self, key -> None: str) -> None:
        """Get disk cache file path for key."""
        from pathlib import Path
        
        # Create subdirectories based on key hash for better distribution
        key_hash = hashlib.md5(key.encode()).hexdigest()
        subdir = key_hash[:2]
        filename = f"{key_hash}.json"
        
        return Path(self._disk_cache_dir) / subdir / filename
    
    def _generate_cache_key(self, collection_name: str, operation: str,
                          query: Dict[str, Any], **kwargs) -> str:
        """Generate cache key for query."""
        key_data = {
            'collection': collection_name,
            'operation': operation,
            'query': query,
            **kwargs
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

# Cache decorators
def cached_query(ttl -> None: int = 3600, tags -> None: List[str] = None) -> None:
    """Decorator to cache MongoDB query results.
    
    Args:
        ttl: Cache TTL in seconds
        tags: Cache tags for invalidation
    """
    def decorator(func) -> None:
        def wrapper(*args, **kwargs) -> None:
            # Generate cache key from function arguments
            cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # Try to get from cache
            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl=ttl, tags=tags)
            
            return result
        return wrapper
    return decorator

# Global cache manager instance
_default_cache_manager: Optional[CacheManager] = None

def get_cache_manager(**kwargs) -> CacheManager:
    """Get or create default cache manager instance."""
    global _default_cache_manager
    if _default_cache_manager is None:
        _default_cache_manager = CacheManager(**kwargs)
    return _default_cache_manager

__all__ = [
    'CacheManager', 'CacheEntry', 'CacheStats', 'CacheLevel',
    'cached_query', 'get_cache_manager'
]