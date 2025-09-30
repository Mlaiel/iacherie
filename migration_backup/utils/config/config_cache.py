"""
Configuration Cache Manager
==========================

High-performance configuration caching with multi-level cache, TTL management,
and intelligent cache warming strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import threading
from typing import Any, Dict, Optional, Callable, List, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import pickle
import logging

logger = logging.getLogger(__name__)

class CacheEntry:
    """Cache entry with metadata."""
    
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 1
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl else None
        
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
        
    def touch(self) -> None:
        """Update access time and count."""
        self.last_accessed = time.time()
        self.access_count += 1

class LRUCache:
    """LRU (Least Recently Used) cache implementation."""
    
    def __init__(self, max_size: int, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    return None
                    
                entry.touch()
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return entry.value
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache."""
        with self.lock:
            effective_ttl = ttl or self.default_ttl
            entry = CacheEntry(value, effective_ttl)
            
            if key in self.cache:
                # Update existing entry
                self.cache[key] = entry
                self.cache.move_to_end(key)
            else:
                # Add new entry
                self.cache[key] = entry
                
                # Evict oldest if necessary
                if len(self.cache) > self.max_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
            
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)
            
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self.cache[key]
                
            return len(expired_keys)

class LFUCache:
    """LFU (Least Frequently Used) cache implementation."""
    
    def __init__(self, max_size: int, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.frequencies: Dict[str, int] = {}
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    del self.frequencies[key]
                    return None
                    
                entry.touch()
                self.frequencies[key] = entry.access_count
                return entry.value
            return None
            
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache."""
        with self.lock:
            effective_ttl = ttl or self.default_ttl
            entry = CacheEntry(value, effective_ttl)
            
            if key in self.cache:
                # Update existing entry
                self.cache[key] = entry
                self.frequencies[key] = entry.access_count
            else:
                # Add new entry
                if len(self.cache) >= self.max_size:
                    # Evict least frequently used
                    lfu_key = min(self.frequencies.items(), key=lambda x: x[1])[0]
                    del self.cache[lfu_key]
                    del self.frequencies[lfu_key]
                    
                self.cache[key] = entry
                self.frequencies[key] = entry.access_count
                
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.frequencies[key]
                return True
            return False
            
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.frequencies.clear()
            
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)

class ConfigurationCache:
    """
    Enterprise configuration cache with multiple cache levels and strategies.
    
    Features:
    - L1 cache: LRU cache for hot configuration values
    - L2 cache: LFU cache for frequently accessed values
    - Intelligent cache warming
    - Cache statistics and monitoring
    - Thread-safe operations
    - Configurable TTL per cache level
    """
    
    def __init__(self, l1_size: int = 1000, l2_size: int = 5000,
                 l1_ttl: float = 300, l2_ttl: float = 3600):
        self.l1_cache = LRUCache(l1_size, l1_ttl)
        self.l2_cache = LFUCache(l2_size, l2_ttl)
        
        # Cache statistics
        self.stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'total_requests': 0,
            'cache_sets': 0,
            'cache_deletes': 0,
            'warming_operations': 0
        }
        
        # Cache warming
        self.warm_cache_keys: List[str] = []
        self.warming_enabled = True
        
        # Background cleanup
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with fallback strategy.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        self.stats['total_requests'] += 1
        
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats['l1_hits'] += 1
            return value
            
        self.stats['l1_misses'] += 1
        
        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            self.stats['l2_hits'] += 1
            # Promote to L1 cache
            self.l1_cache.set(key, value)
            return value
            
        self.stats['l2_misses'] += 1
        return default
        
    def set(self, key: str, value: Any, ttl: Optional[float] = None,
            cache_level: str = 'both') -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            cache_level: 'l1', 'l2', or 'both'
        """
        self.stats['cache_sets'] += 1
        
        if cache_level in ['l1', 'both']:
            self.l1_cache.set(key, value, ttl)
            
        if cache_level in ['l2', 'both']:
            self.l2_cache.set(key, value, ttl)
            
    def delete(self, key: str) -> bool:
        """Delete value from all cache levels."""
        self.stats['cache_deletes'] += 1
        
        l1_deleted = self.l1_cache.delete(key)
        l2_deleted = self.l2_cache.delete(key)
        
        return l1_deleted or l2_deleted
        
    def clear(self) -> None:
        """Clear all cache levels."""
        self.l1_cache.clear()
        self.l2_cache.clear()
        
        # Reset statistics
        for key in self.stats:
            self.stats[key] = 0
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = self.stats['l1_hits'] + self.stats['l2_hits']
        total_misses = self.stats['l1_misses'] + self.stats['l2_misses']
        total_requests = self.stats['total_requests']
        
        hit_rate = total_hits / max(total_requests, 1)
        l1_hit_rate = self.stats['l1_hits'] / max(total_requests, 1)
        l2_hit_rate = self.stats['l2_hits'] / max(total_requests, 1)
        
        return {
            **self.stats,
            'total_hits': total_hits,
            'total_misses': total_misses,
            'hit_rate': hit_rate,
            'l1_hit_rate': l1_hit_rate,
            'l2_hit_rate': l2_hit_rate,
            'l1_size': self.l1_cache.size(),
            'l2_size': self.l2_cache.size(),
            'memory_usage_estimate': self._estimate_memory_usage()
        }
        
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        try:
            # Rough estimation using pickle size
            l1_size = sum(len(pickle.dumps(entry.value)) for entry in self.l1_cache.cache.values())
            l2_size = sum(len(pickle.dumps(entry.value)) for entry in self.l2_cache.cache.values())
            return l1_size + l2_size
        except Exception:
            return 0
            
    def warm_cache(self, config_getter: Callable[[str], Any], 
                   keys: Optional[List[str]] = None) -> int:
        """
        Warm cache with frequently accessed configuration values.
        
        Args:
            config_getter: Function to get configuration values
            keys: Optional list of keys to warm (uses warm_cache_keys if None)
            
        Returns:
            Number of keys warmed
        """
        if not self.warming_enabled:
            return 0
            
        keys_to_warm = keys or self.warm_cache_keys
        warmed_count = 0
        
        for key in keys_to_warm:
            try:
                value = config_getter(key)
                if value is not None:
                    self.set(key, value)
                    warmed_count += 1
            except Exception as e:
                logger.warning(f"Failed to warm cache for key {key}: {e}")
                
        self.stats['warming_operations'] += 1
        logger.info(f"Cache warming completed: {warmed_count}/{len(keys_to_warm)} keys warmed")
        
        return warmed_count
        
    def add_warm_keys(self, keys: List[str]) -> None:
        """Add keys to the warm cache list."""
        self.warm_cache_keys.extend(keys)
        
    def remove_warm_keys(self, keys: List[str]) -> None:
        """Remove keys from the warm cache list."""
        for key in keys:
            if key in self.warm_cache_keys:
                self.warm_cache_keys.remove(key)
                
    def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired cache entries."""
        current_time = time.time()
        
        # Only run cleanup if enough time has passed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return {'l1_removed': 0, 'l2_removed': 0}
            
        l1_removed = self.l1_cache.cleanup_expired()
        l2_removed = self.l2_cache.cleanup_expired()
        
        self.last_cleanup = current_time
        
        if l1_removed > 0 or l2_removed > 0:
            logger.info(f"Cache cleanup: removed {l1_removed} L1 entries, {l2_removed} L2 entries")
            
        return {'l1_removed': l1_removed, 'l2_removed': l2_removed}
        
    def get_cache_key(self, config_path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate cache key for configuration path and parameters.
        
        Args:
            config_path: Configuration path
            params: Optional parameters to include in key
            
        Returns:
            Generated cache key
        """
        if params:
            # Create deterministic hash of parameters
            param_str = str(sorted(params.items()))
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"{config_path}:{param_hash}"
        else:
            return config_path
            
    def enable_warming(self, enabled: bool = True) -> None:
        """Enable or disable cache warming."""
        self.warming_enabled = enabled
        
    def set_cleanup_interval(self, seconds: int) -> None:
        """Set cleanup interval in seconds."""
        self.cleanup_interval = max(60, seconds)  # Minimum 1 minute
        
    def get_top_keys(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed keys."""
        # Combine access counts from both caches
        all_keys = {}
        
        # Get L1 access counts
        for key, entry in self.l1_cache.cache.items():
            all_keys[key] = entry.access_count
            
        # Add L2 access counts
        for key, entry in self.l2_cache.cache.items():
            if key in all_keys:
                all_keys[key] += entry.access_count
            else:
                all_keys[key] = entry.access_count
                
        # Sort by access count and return top keys
        sorted_keys = sorted(all_keys.items(), key=lambda x: x[1], reverse=True)
        return sorted_keys[:limit]