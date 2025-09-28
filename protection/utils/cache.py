#!/usr/bin/env python3
"""
💾 Cache Utilities - Protection Utils Module
===========================================

Caching utilities for the protection system.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Utils Module
"""

import time
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import json
import hashlib
import asyncio

class CrawlerCache:
    """In-memory cache for crawler operations"""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache with default TTL"""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        
    def _generate_key(self, key: Union[str, dict]) -> str:
        """Generate cache key"""
        if isinstance(key, dict):
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def set(self, key: Union[str, dict], value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value"""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl
        expire_time = time.time() + ttl
        
        self._cache[cache_key] = {
            'value': value,
            'expire_time': expire_time,
            'created_at': time.time()
        }
    
    def get(self, key: Union[str, dict]) -> Optional[Any]:
        """Get cache value"""
        cache_key = self._generate_key(key)
        
        if cache_key not in self._cache:
            return None
            
        entry = self._cache[cache_key]
        
        # Check if expired
        if time.time() > entry['expire_time']:
            del self._cache[cache_key]
            return None
            
        return entry['value']
    
    def delete(self, key: Union[str, dict]) -> bool:
        """Delete cache entry"""
        cache_key = self._generate_key(key)
        
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time > entry['expire_time']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self._cache)
        expired_count = 0
        current_time = time.time()
        
        for entry in self._cache.values():
            if current_time > entry['expire_time']:
                expired_count += 1
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_count,
            'expired_entries': expired_count,
            'cache_size_kb': len(str(self._cache)) / 1024
        }

class AsyncCrawlerCache(CrawlerCache):
    """Async version of crawler cache"""
    
    async def async_set(self, key: Union[str, dict], value: Any, ttl: Optional[int] = None) -> None:
        """Async set cache value"""
        await asyncio.sleep(0)  # Yield control
        self.set(key, value, ttl)
    
    async def async_get(self, key: Union[str, dict]) -> Optional[Any]:
        """Async get cache value"""
        await asyncio.sleep(0)  # Yield control
        return self.get(key)
    
    async def async_delete(self, key: Union[str, dict]) -> bool:
        """Async delete cache entry"""
        await asyncio.sleep(0)  # Yield control
        return self.delete(key)
    
    async def async_cleanup_expired(self) -> int:
        """Async cleanup expired entries"""
        await asyncio.sleep(0)  # Yield control
        return self.cleanup_expired()

class DistributedCache:
    """Distributed cache interface for enterprise environments"""
    
    def __init__(self, redis_client=None, fallback_cache=None):
        """Initialize distributed cache"""
        self.redis_client = redis_client
        self.fallback_cache = fallback_cache or CrawlerCache()
        
    def set(self, key: Union[str, dict], value: Any, ttl: Optional[int] = None) -> None:
        """Set value in distributed cache"""
        if self.redis_client:
            try:
                cache_key = self._generate_key(key)
                serialized_value = json.dumps(value)
                ttl = ttl or 3600
                self.redis_client.setex(cache_key, ttl, serialized_value)
                return
            except Exception:
                pass  # Fall back to local cache
        
        # Use fallback cache
        self.fallback_cache.set(key, value, ttl)
    
    def get(self, key: Union[str, dict]) -> Optional[Any]:
        """Get value from distributed cache"""
        if self.redis_client:
            try:
                cache_key = self._generate_key(key)
                value = self.redis_client.get(cache_key)
                if value:
                    return json.loads(value.decode())
            except Exception:
                pass  # Fall back to local cache
        
        # Use fallback cache
        return self.fallback_cache.get(key)
    
    def _generate_key(self, key: Union[str, dict]) -> str:
        """Generate cache key"""
        if isinstance(key, dict):
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)
        return f"crawler_cache:{hashlib.md5(key_str.encode()).hexdigest()}"

# Global cache instance
crawler_cache = CrawlerCache()

# Convenience functions
def cache_set(key: Union[str, dict], value: Any, ttl: Optional[int] = None) -> None:
    """Set cache value using global cache"""
    crawler_cache.set(key, value, ttl)

def cache_get(key: Union[str, dict]) -> Optional[Any]:
    """Get cache value using global cache"""
    return crawler_cache.get(key)

def cache_delete(key: Union[str, dict]) -> bool:
    """Delete cache entry using global cache"""
    return crawler_cache.delete(key)

def cache_clear() -> None:
    """Clear all cache entries using global cache"""
    crawler_cache.clear()

def cache_cleanup() -> int:
    """Cleanup expired entries using global cache"""
    return crawler_cache.cleanup_expired()

def cache_stats() -> Dict[str, Any]:
    """Get cache statistics using global cache"""
    return crawler_cache.get_stats()

# Aliases for backward compatibility
Cache = CrawlerCache
AsyncCache = AsyncCrawlerCache
DistCache = DistributedCache