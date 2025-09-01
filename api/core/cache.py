"""Enterprise-grade caching system for IA Influencer Agent.
Professional multi-level caching with intelligent invalidation strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Optional, Dict, List, Union, Callable, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import asyncio
import hashlib
import json
import pickle
import time
import threading
from contextlib import asynccontextmanager


T = TypeVar('T')


class CacheStrategy(Enum):
    """
Cache invalidation strategies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


class CacheLevel(Enum):
    """Cache hierarchy levels."""

    L1_MEMORY = 1  # In-memory cache
    L2_REDIS = 2   # Redis distributed cache
    L3_DATABASE = 3  # Database cache


@dataclass
class CacheEntry:
    """
Cache entry with comprehensive metadata."""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: List[str] = None
    size_bytes: int = 0
    version: int = 1
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        
        # Calculate approximate size
        if self.size_bytes == 0:
            try:
                self.size_bytes = len(pickle.dumps(self.value))
            except:
                self.size_bytes = len(str(self.value).encode('utf-8'))
    
    @property
    def is_expired(self) -> bool:
        """
Check if cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now(timezone.utc) > expiry_time
    
    @property
    def age_seconds(self) -> float:
        """
Get age of cache entry in seconds."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    def touch(self):
        """
Update access timestamp and count."""
        self.accessed_at = datetime.now(timezone.utc)
        self.access_count += 1


class ICacheProvider(ABC):
    """
Interface for cache provider implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
Get value from cache."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
Delete value from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
Clear all cache entries."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
Get cache statistics."""
        pass


class InMemoryCache(ICacheProvider):
    """
High-performance in-memory cache implementation."""
    
    def __init__(
        self,
        max_size: int = 10000,
        default_ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.LRU
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with LRU tracking."""
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            # Update access info
            entry.touch()
            self._stats["hits"] += 1
            
            return entry.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set value with eviction strategy."""
        with self._lock:
            # Use default TTL if not specified
            ttl = ttl_seconds or self.default_ttl
            
            # Create cache entry
            now = datetime.now(timezone.utc)
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                accessed_at=now,
                ttl_seconds=ttl,
                tags=tags or []
            )
            
            # Check if we need to evict
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_entries(1)
            
            self._cache[key] = entry
            self._stats["sets"] += 1
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            if entry.is_expired:
                del self._cache[key]
                return False
            
            return True
    
    async def clear(self) -> bool:
        """
Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """
Get comprehensive cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_ratio = self._stats["hits"] / total_requests if total_requests > 0 else 0
            
            total_size = sum(entry.size_bytes for entry in self._cache.values())
            
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_ratio": hit_ratio,
                "total_size_bytes": total_size,
                "average_entry_size": total_size / len(self._cache) if self._cache else 0
            }
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries by tags."""
        invalidated = 0
        with self._lock:
            keys_to_delete = []
            
            for key, entry in self._cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cache[key]
                invalidated += 1
        
        return invalidated
    
    async def _evict_entries(self, count: int):
        """
Evict entries based on strategy."""
        if not self._cache:
            return
        
        entries_to_evict = []
        
        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].accessed_at
            )
            entries_to_evict = sorted_entries[:count]
        
        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].access_count
            )
            entries_to_evict = sorted_entries[:count]
        
        elif self.strategy == CacheStrategy.FIFO:
            # Evict first in, first out
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].created_at
            )
            entries_to_evict = sorted_entries[:count]
        
        # Remove evicted entries
        for key, _ in entries_to_evict:
            if key in self._cache:
                del self._cache[key]
                self._stats["evictions"] += 1


class MultiLevelCache:
    """Professional multi-level caching system."""
    
    def __init__(self):
        self._providers: Dict[CacheLevel, ICacheProvider] = {}
        self._lock = threading.RLock()
    
    def add_provider(self, level: CacheLevel, provider: ICacheProvider):
        """
Add cache provider at specific level."""
        with self._lock:
            self._providers[level] = provider
    
    async def get(self, key: str) -> Optional[Any]:
        """
Get value from multi-level cache hierarchy."""
        # Try each level in order (L1 -> L2 -> L3)
        for level in sorted(self._providers.keys(), key=lambda x: x.value):
            provider = self._providers[level]
            value = await provider.get(key)
            
            if value is not None:
                # Populate higher levels (cache promotion)
                await self._promote_to_higher_levels(key, value, level)
                return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
        levels: Optional[List[CacheLevel]] = None
    ) -> bool:
        """
Set value in specified cache levels."""
        target_levels = levels or list(self._providers.keys())
        success = True
        
        for level in target_levels:
            if level in self._providers:
                result = await self._providers[level].set(key, value, ttl_seconds, tags)
                success = success and result
        
        return success
    
    async def delete(self, key: str, levels: Optional[List[CacheLevel]] = None) -> bool:
        """
Delete from specified levels."""
        target_levels = levels or list(self._providers.keys())
        success = True
        
        for level in target_levels:
            if level in self._providers:
                result = await self._providers[level].delete(key)
                success = success and result
        
        return success
    
    async def invalidate_by_tags(
        self,
        tags: List[str],
        levels: Optional[List[CacheLevel]] = None
    ) -> Dict[CacheLevel, int]:
        """
Invalidate by tags across levels."""
        target_levels = levels or list(self._providers.keys())
        results = {}
        
        for level in target_levels:
            if level in self._providers:
                provider = self._providers[level]
                if hasattr(provider, 'invalidate_by_tags'):
                    count = await provider.invalidate_by_tags(tags)
                    results[level] = count
        
        return results
    
    async def get_stats(self) -> Dict[CacheLevel, Dict[str, Any]]:
        """
Get statistics from all levels."""
        stats = {}
        for level, provider in self._providers.items():
            stats[level] = await provider.get_stats()
        return stats
    
    async def _promote_to_higher_levels(
        self,
        key: str,
        value: Any,
        current_level: CacheLevel
    ):
        """
Promote cache entry to higher (faster) levels."""
        for level in self._providers.keys():
            if level.value < current_level.value:
                await self._providers[level].set(key, value)


class CacheManager:
    """
Professional cache management with intelligent strategies."""
    
    def __init__(self, cache: Union[ICacheProvider, MultiLevelCache]):
        self.cache = cache
        self._key_generators: Dict[str, Callable] = {}
    
    def register_key_generator(self, prefix: str, generator: Callable[..., str]):
        """
Register key generation strategy for prefix."""
        self._key_generators[prefix] = generator
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
Generate cache key using registered strategies."""
        if prefix in self._key_generators:
            return self._key_generators[prefix](*args, **kwargs)
        
        # Default key generation
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Any:
        """Get from cache or set using factory function."""
        value = await self.cache.get(key)
        
        if value is not None:
            return value
        
        # Generate value using factory
        value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
        
        # Store in cache
        await self.cache.set(key, value, ttl_seconds, tags)
        
        return value
    
    @asynccontextmanager
    async def cache_context(self, prefix: str, ttl_seconds: Optional[int] = None):
        """
Context manager for scoped caching."""
        context_keys = []
        
        original_set = self.cache.set
        
        async def tracked_set(key: str, value: Any, ttl: Optional[int] = None, tags: Optional[List[str]] = None):
            full_key = f"{prefix}:{key}"
            context_keys.append(full_key)
            return await original_set(full_key, value, ttl or ttl_seconds, tags)
        
        self.cache.set = tracked_set
        
        try:
            yield self
        finally:
            self.cache.set = original_set
            # Cleanup context keys if needed
            # This could be extended with automatic cleanup


# Default cache key generators
def user_cache_key(user_id: str, resource: str, *args) -> str:
    """Generate user-specific cache key."""
    parts = ["user", str(user_id), resource]
    parts.extend(str(arg) for arg in args)
    return ":".join(parts)


def content_cache_key(content_id: str, operation: str, *args) -> str:
    """Generate content-specific cache key."""
    parts = ["content", str(content_id), operation]
    parts.extend(str(arg) for arg in args)
    return ":".join(parts)


def fingerprint_cache_key(content_type: str, hash_value: str) -> str:
    """Generate fingerprint cache key."""
    return f"fingerprint:{content_type}:{hash_value}"


# Global cache instances
_memory_cache = InMemoryCache(max_size=50000, default_ttl=3600)
_multi_level_cache = MultiLevelCache()
_multi_level_cache.add_provider(CacheLevel.L1_MEMORY, _memory_cache)

_cache_manager = CacheManager(_multi_level_cache)

# Register default key generators
_cache_manager.register_key_generator("user", user_cache_key)
_cache_manager.register_key_generator("content", content_cache_key)
_cache_manager.register_key_generator("fingerprint", fingerprint_cache_key)


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    return _cache_manager


def get_memory_cache() -> InMemoryCache:
    """
Get global memory cache instance."""
    return _memory_cache


def get_multi_level_cache() -> MultiLevelCache:
    """
Get global multi-level cache instance."""
    return _multi_level_cache
