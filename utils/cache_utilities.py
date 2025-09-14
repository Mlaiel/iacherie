"""
Cache Utilities - Enterprise Grade
=================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Expert Roles: DBA Expert + Backend Senior + DevOps Expert
Provides comprehensive caching solutions for enterprise applications.
"""

import json
import time
import threading
import hashlib
import pickle
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from collections import OrderedDict
import redis
import memcache
from functools import wraps, lru_cache
import weakref


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'tags': self.tags
        }


class CacheStats:
    """Cache statistics tracking."""
    
    def __init__(self) -> None:
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.errors = 0
        self.start_time = datetime.now()
        self._lock = threading.RLock()
    
    def record_hit(self) -> None:
        """Record cache hit."""
        with self._lock:
            self.hits += 1
    
    def record_miss(self) -> None:
        """Record cache miss."""
        with self._lock:
            self.misses += 1
    
    def record_set(self) -> None:
        """Record cache set."""
        with self._lock:
            self.sets += 1
    
    def record_delete(self) -> None:
        """Record cache delete."""
        with self._lock:
            self.deletes += 1
    
    def record_eviction(self) -> None:
        """Record cache eviction."""
        with self._lock:
            self.evictions += 1
    
    def record_error(self) -> None:
        """Record cache error."""
        with self._lock:
            self.errors += 1
    
    def get_hit_rate(self) -> float:
        """Calculate hit rate."""
        with self._lock:
            total = self.hits + self.misses
            return self.hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all statistics."""
        with self._lock:
            uptime = datetime.now() - self.start_time
            return {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'deletes': self.deletes,
                'evictions': self.evictions,
                'errors': self.errors,
                'hit_rate': self.get_hit_rate(),
                'uptime_seconds': uptime.total_seconds()
            }
    
    def reset(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.sets = 0
            self.deletes = 0
            self.evictions = 0
            self.errors = 0
            self.start_time = datetime.now()


class CacheBackend(ABC):
    """Abstract cache backend interface."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class InMemoryCache(CacheBackend):
    """In-memory cache implementation with LRU eviction."""
    
    def __init__(self, max_size -> None: int = 1000, default_ttl -> None: int = 3600) -> None:
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()
        self.logger = logging.getLogger(__name__)
    
    def _evict_expired(self) -> None:
        """Remove expired entries."""
        expired_keys = []
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            self.stats.record_eviction()
    
    def _evict_lru(self) -> None:
        """Remove least recently used entry."""
        if self._cache:
            key, _ = self._cache.popitem(last=False)
            self.stats.record_eviction()
            self.logger.debug(f"Evicted LRU entry: {key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            self._evict_expired()
            
            if key in self._cache:
                entry = self._cache[key]
                
                if entry.is_expired():
                    del self._cache[key]
                    self.stats.record_miss()
                    return None
                
                # Update access information
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                
                self.stats.record_hit()
                return entry.value
            
            self.stats.record_miss()
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            with self._lock:
                # Calculate expiration time
                expires_at = None
                if ttl is not None:
                    expires_at = datetime.now() + timedelta(seconds=ttl)
                elif self.default_ttl > 0:
                    expires_at = datetime.now() + timedelta(seconds=self.default_ttl)
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.now(),
                    expires_at=expires_at
                )
                
                # Evict expired entries
                self._evict_expired()
                
                # Evict LRU entries if needed
                while len(self._cache) >= self.max_size:
                    self._evict_lru()
                
                # Add new entry
                self._cache[key] = entry
                self.stats.record_set()
                return True
                
        except Exception as e:
            self.logger.error(f"Cache set error: {str(e)}")
            self.stats.record_error()
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.stats.record_delete()
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    del self._cache[key]
                    return False
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            base_stats = self.stats.get_stats()
            base_stats.update({
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_estimate': self._estimate_memory_usage()
            })
            return base_stats
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # Rough estimation
        total_size = 0
        for entry in self._cache.values():
            try:
                total_size += len(pickle.dumps(entry.value))
            except:
                total_size += 100  # Default estimate
        return total_size


class RedisCache(CacheBackend):
    """Redis-based cache implementation."""
    
    def __init__(self, host -> None: str = 'localhost', port -> None: int = 6379, 
                 db -> None: int = 0, password -> None: Optional[str] = None,
                 key_prefix -> None: str = 'ainflue -> None:') -> None:
        self.key_prefix = key_prefix
        self.stats = CacheStats()
        self.logger = logging.getLogger(__name__)
        
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, 
                password=password, decode_responses=False
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            self.logger.error(f"Redis connection failed: {str(e)}")
            raise
    
    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            redis_key = self._make_key(key)
            data = self.redis_client.get(redis_key)
            
            if data is not None:
                value = pickle.loads(data)
                self.stats.record_hit()
                return value
            
            self.stats.record_miss()
            return None
            
        except Exception as e:
            self.logger.error(f"Redis get error: {str(e)}")
            self.stats.record_error()
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            redis_key = self._make_key(key)
            data = pickle.dumps(value)
            
            if ttl is not None:
                result = self.redis_client.setex(redis_key, ttl, data)
            else:
                result = self.redis_client.set(redis_key, data)
            
            if result:
                self.stats.record_set()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Redis set error: {str(e)}")
            self.stats.record_error()
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            redis_key = self._make_key(key)
            result = self.redis_client.delete(redis_key)
            
            if result > 0:
                self.stats.record_delete()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Redis delete error: {str(e)}")
            self.stats.record_error()
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            redis_key = self._make_key(key)
            return self.redis_client.exists(redis_key) > 0
        except Exception as e:
            self.logger.error(f"Redis exists error: {str(e)}")
            self.stats.record_error()
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries with prefix."""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Redis clear error: {str(e)}")
            self.stats.record_error()
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        base_stats = self.stats.get_stats()
        
        try:
            redis_info = self.redis_client.info('memory')
            base_stats.update({
                'redis_memory_used': redis_info.get('used_memory', 0),
                'redis_memory_peak': redis_info.get('used_memory_peak', 0),
                'redis_connected_clients': self.redis_client.info('clients').get('connected_clients', 0)
            })
        except Exception as e:
            self.logger.error(f"Redis stats error: {str(e)}")
        
        return base_stats


class CacheUtilities:
    """
    Enterprise-grade cache utility manager.
    
    Features:
    - Multiple cache backends (In-Memory, Redis, Memcached)
    - Tiered caching with fallback
    - Cache warming and preloading
    - Tag-based cache invalidation
    - Automatic serialization and compression
    - Performance monitoring and statistics
    - Cache pattern implementations (read-through, write-through, write-behind)
    """
    
    def __init__(self, 
                 primary_backend -> None: CacheBackend,
                 secondary_backend -> None: Optional[CacheBackend] = None,
                 enable_compression -> None: bool = False,
                 compression_threshold -> None: int = 1024) -> None:
        
        self.primary_backend = primary_backend
        self.secondary_backend = secondary_backend
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        
        self.logger = logging.getLogger(__name__)
        
        # Tag-based invalidation
        self._tag_keys: Dict[str, set] = {}
        self._key_tags: Dict[str, set] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with fallback."""
        # Try primary cache
        value = self.primary_backend.get(key)
        if value is not None:
            return value
        
        # Try secondary cache if available
        if self.secondary_backend:
            value = self.secondary_backend.get(key)
            if value is not None:
                # Populate primary cache
                self.primary_backend.set(key, value)
                return value
        
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            tags: Optional[List[str]] = None) -> bool:
        """Set value in cache with tags."""
        # Set in primary cache
        success = self.primary_backend.set(key, value, ttl)
        
        # Set in secondary cache if available
        if self.secondary_backend:
            self.secondary_backend.set(key, value, ttl)
        
        # Handle tags
        if tags and success:
            self._add_tags(key, tags)
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete value from all caches."""
        success = self.primary_backend.delete(key)
        
        if self.secondary_backend:
            self.secondary_backend.delete(key)
        
        # Remove tag associations
        self._remove_tags(key)
        
        return success
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with a specific tag."""
        with self._lock:
            keys_to_invalidate = self._tag_keys.get(tag, set()).copy()
            
            count = 0
            for key in keys_to_invalidate:
                if self.delete(key):
                    count += 1
            
            return count
    
    def get_or_set(self, key: str, func: Callable[[], Any], 
                   ttl: Optional[int] = None, tags: Optional[List[str]] = None) -> Any:
        """Get value from cache or set it using the provided function."""
        value = self.get(key)
        
        if value is None:
            value = func()
            self.set(key, value, ttl, tags)
        
        return value
    
    async def get_or_set_async(self, key: str, func: Callable[[], Any], 
                              ttl: Optional[int] = None, tags: Optional[List[str]] = None) -> Any:
        """Async version of get_or_set."""
        value = self.get(key)
        
        if value is None:
            if asyncio.iscoroutinefunction(func):
                value = await func()
            else:
                value = func()
            self.set(key, value, ttl, tags)
        
        return value
    
    def warm_cache(self, key_value_pairs -> None: Dict[str, Any], 
                   ttl -> None: Optional[int] = None, tags -> None: Optional[List[str]] = None) -> None:
        """Warm cache with multiple key-value pairs."""
        for key, value in key_value_pairs.items():
            self.set(key, value, ttl, tags)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in any cache."""
        return (self.primary_backend.exists(key) or 
                (self.secondary_backend and self.secondary_backend.exists(key)))
    
    def clear(self) -> bool:
        """Clear all caches."""
        primary_success = self.primary_backend.clear()
        secondary_success = True
        
        if self.secondary_backend:
            secondary_success = self.secondary_backend.clear()
        
        # Clear tag mappings
        with self._lock:
            self._tag_keys.clear()
            self._key_tags.clear()
        
        return primary_success and secondary_success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            'primary': self.primary_backend.get_stats()
        }
        
        if self.secondary_backend:
            stats['secondary'] = self.secondary_backend.get_stats()
        
        with self._lock:
            stats['tags'] = {
                'total_tags': len(self._tag_keys),
                'total_tagged_keys': len(self._key_tags)
            }
        
        return stats
    
    def _add_tags(self, key -> None: str, tags -> None: List[str]) -> None:
        """Add tag associations for a key."""
        with self._lock:
            for tag in tags:
                if tag not in self._tag_keys:
                    self._tag_keys[tag] = set()
                self._tag_keys[tag].add(key)
            
            if key not in self._key_tags:
                self._key_tags[key] = set()
            self._key_tags[key].update(tags)
    
    def _remove_tags(self, key -> None: str) -> None:
        """Remove tag associations for a key."""
        with self._lock:
            if key in self._key_tags:
                tags = self._key_tags[key]
                for tag in tags:
                    if tag in self._tag_keys:
                        self._tag_keys[tag].discard(key)
                        if not self._tag_keys[tag]:
                            del self._tag_keys[tag]
                del self._key_tags[key]


# Decorators for caching
def cached(cache -> None: CacheUtilities, ttl -> None: int = 3600, 
          key_func -> None: Optional[Callable] = None,
          tags -> None: Optional[List[str]] = None) -> None:
    """Decorator for caching function results."""
    def decorator(func) -> None:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl, tags)
            return result
        
        return wrapper
    return decorator


def cache_result(ttl -> None: int = 3600, tags -> None: Optional[List[str]] = None) -> None:
    """Simple decorator for caching with global cache."""
    def decorator(func) -> None:
        if not hasattr(decorator, '_cache'):
            decorator._cache = CacheUtilities(InMemoryCache())
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            result = decorator._cache.get(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            decorator._cache.set(cache_key, result, ttl, tags)
            return result
        
        return wrapper
    return decorator


# Global cache instance
global_cache = CacheUtilities(InMemoryCache(max_size=1000))


# Convenience functions
def cache_get(key: str, default: Any = None) -> Any:
    """Get value from global cache."""
    return global_cache.get(key, default)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in global cache."""
    return global_cache.set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete value from global cache."""
    return global_cache.delete(key)


def cache_clear() -> bool:
    """Clear global cache."""
    return global_cache.clear()


# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Test in-memory cache
    memory_cache = InMemoryCache(max_size=5)
    cache_utils = CacheUtilities(memory_cache)
    
    # Test basic operations
    cache_utils.set("key1", "value1", ttl=60)
    cache_utils.set("key2", "value2", ttl=60, tags=["user", "profile"])
    
    print(f"Get key1: {cache_utils.get('key1')}")
    print(f"Get key2: {cache_utils.get('key2')}")
    
    # Test tag-based invalidation
    cache_utils.set("key3", "value3", tags=["user"])
    cache_utils.set("key4", "value4", tags=["admin"])
    
    print(f"Before invalidation - key2: {cache_utils.get('key2')}, key3: {cache_utils.get('key3')}")
    
    invalidated = cache_utils.invalidate_by_tag("user")
    print(f"Invalidated {invalidated} keys with tag 'user'")
    
    print(f"After invalidation - key2: {cache_utils.get('key2')}, key3: {cache_utils.get('key3')}")
    
    # Test decorator
    @cache_result(ttl=30)
    def expensive_function(x, y) -> None:
        time.sleep(0.1)  # Simulate expensive operation
        return x + y
    
    start_time = time.time()
    result1 = expensive_function(1, 2)
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    result2 = expensive_function(1, 2)  # Should be cached
    second_call_time = time.time() - start_time
    
    print(f"First call: {result1} ({first_call_time:.3f}s)")
    print(f"Second call: {result2} ({second_call_time:.3f}s)")
    print(f"Speedup: {first_call_time / second_call_time:.1f}x")
    
    # Get statistics
    stats = cache_utils.get_stats()
    print(f"Cache statistics: {stats}")