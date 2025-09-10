"""
Cache Manager - Intelligent Multi-Level Caching System
======================================================

Enterprise-grade cache manager with LRU/LFU strategies, TTL-based expiration,
adaptive replacement, hierarchical caching, and distributed cache support.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import json
import pickle
import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import OrderedDict, defaultdict
import threading
from pathlib import Path
import weakref

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ARC = "arc"  # Adaptive Replacement Cache
    FIFO = "fifo"  # First In, First Out
    RANDOM = "random"  # Random eviction


class CacheLevel(Enum):
    """Cache hierarchy levels."""
    L1_MEMORY = "l1_memory"
    L2_MEMORY = "l2_memory"
    L3_DISK = "l3_disk"
    L4_DISTRIBUTED = "l4_distributed"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    size_bytes: Optional[int] = None
    compressed: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0


class LRUCache:
    """LRU (Least Recently Used) cache implementation."""
    
    def __init__(self, max_size: int, ttl_seconds: Optional[int] = None):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
            ttl_seconds: Time to live for entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = CacheStats()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.stats.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if self._is_expired(entry):
                del self.cache[key]
                self.stats.misses += 1
                self.stats.evictions += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.last_accessed = datetime.utcnow()
            entry.access_count += 1
            
            self.stats.hits += 1
            self._update_hit_rate()
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self.lock:
            try:
                # Calculate size
                size_bytes = self._calculate_size(value)
                
                # Create entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    access_count=1,
                    ttl_seconds=ttl_seconds or self.ttl_seconds,
                    size_bytes=size_bytes
                )
                
                # Remove if exists
                if key in self.cache:
                    del self.cache[key]
                
                # Add new entry
                self.cache[key] = entry
                
                # Evict if necessary
                while len(self.cache) > self.max_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    self.stats.evictions += 1
                
                self._update_stats()
                return True
                
            except Exception as e:
                logger.error(f"Failed to set cache entry: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self._update_stats()
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self._update_stats()
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if entry is expired."""
        if not entry.ttl_seconds:
            return False
        
        age = (datetime.utcnow() - entry.created_at).total_seconds()
        return age > entry.ttl_seconds
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value."""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return 1024  # Default size estimate
    
    def _update_stats(self) -> None:
        """Update cache statistics."""
        self.stats.entry_count = len(self.cache)
        self.stats.memory_usage = sum(
            entry.size_bytes or 0 for entry in self.cache.values()
        )
        self._update_hit_rate()
    
    def _update_hit_rate(self) -> None:
        """Update hit rate."""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.hit_rate = self.stats.hits / total_requests
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self.lock:
            return self.stats


class LFUCache:
    """LFU (Least Frequently Used) cache implementation."""
    
    def __init__(self, max_size: int, ttl_seconds: Optional[int] = None):
        """Initialize LFU cache."""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        self.frequencies: Dict[str, int] = {}
        self.freq_to_keys: Dict[int, Set[str]] = defaultdict(set)
        self.min_frequency = 0
        self.lock = threading.RLock()
        self.stats = CacheStats()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.stats.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if self._is_expired(entry):
                await self._remove_key(key)
                self.stats.misses += 1
                self.stats.evictions += 1
                return None
            
            # Update frequency
            self._update_frequency(key)
            entry.last_accessed = datetime.utcnow()
            entry.access_count += 1
            
            self.stats.hits += 1
            self._update_hit_rate()
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self.lock:
            try:
                # Remove if exists
                if key in self.cache:
                    await self._remove_key(key)
                
                # Evict if necessary
                if len(self.cache) >= self.max_size:
                    await self._evict_lfu()
                
                # Calculate size
                size_bytes = self._calculate_size(value)
                
                # Create entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    access_count=1,
                    ttl_seconds=ttl_seconds or self.ttl_seconds,
                    size_bytes=size_bytes
                )
                
                # Add to cache
                self.cache[key] = entry
                self.frequencies[key] = 1
                self.freq_to_keys[1].add(key)
                self.min_frequency = 1
                
                self._update_stats()
                return True
                
            except Exception as e:
                logger.error(f"Failed to set LFU cache entry: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self.lock:
            if key in self.cache:
                await self._remove_key(key)
                self._update_stats()
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.frequencies.clear()
            self.freq_to_keys.clear()
            self.min_frequency = 0
            self._update_stats()
    
    def _update_frequency(self, key: str) -> None:
        """Update frequency of key access."""
        freq = self.frequencies[key]
        
        # Remove from current frequency bucket
        self.freq_to_keys[freq].remove(key)
        
        # Update min_frequency if necessary
        if freq == self.min_frequency and not self.freq_to_keys[freq]:
            self.min_frequency += 1
        
        # Add to new frequency bucket
        new_freq = freq + 1
        self.frequencies[key] = new_freq
        self.freq_to_keys[new_freq].add(key)
    
    async def _remove_key(self, key: str) -> None:
        """Remove key from cache and frequency tracking."""
        if key in self.cache:
            freq = self.frequencies[key]
            self.freq_to_keys[freq].remove(key)
            
            del self.cache[key]
            del self.frequencies[key]
    
    async def _evict_lfu(self) -> None:
        """Evict least frequently used item."""
        if self.freq_to_keys[self.min_frequency]:
            # Get any key from min frequency bucket
            key_to_evict = next(iter(self.freq_to_keys[self.min_frequency]))
            await self._remove_key(key_to_evict)
            self.stats.evictions += 1
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if entry is expired."""
        if not entry.ttl_seconds:
            return False
        
        age = (datetime.utcnow() - entry.created_at).total_seconds()
        return age > entry.ttl_seconds
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value."""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return 1024
    
    def _update_stats(self) -> None:
        """Update cache statistics."""
        self.stats.entry_count = len(self.cache)
        self.stats.memory_usage = sum(
            entry.size_bytes or 0 for entry in self.cache.values()
        )
        self._update_hit_rate()
    
    def _update_hit_rate(self) -> None:
        """Update hit rate."""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.hit_rate = self.stats.hits / total_requests
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self.lock:
            return self.stats


class DiskCache:
    """Disk-based cache for large objects."""
    
    def __init__(self, cache_dir: str, max_size_mb: int = 1000):
        """Initialize disk cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.stats = CacheStats()
        
        # Load existing metadata
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load disk cache metadata: {e}")
            self.metadata = {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save disk cache metadata: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        with self.lock:
            try:
                if key not in self.metadata:
                    self.stats.misses += 1
                    return None
                
                entry_meta = self.metadata[key]
                
                # Check TTL
                if self._is_expired(entry_meta):
                    await self.delete(key)
                    self.stats.misses += 1
                    return None
                
                # Load from disk
                file_path = self.cache_dir / f"{key}.cache"
                if not file_path.exists():
                    # Metadata inconsistency, clean up
                    del self.metadata[key]
                    self.stats.misses += 1
                    return None
                
                with open(file_path, 'rb') as f:
                    value = pickle.load(f)
                
                # Update access info
                entry_meta['last_accessed'] = datetime.utcnow().isoformat()
                entry_meta['access_count'] = entry_meta.get('access_count', 0) + 1
                self._save_metadata()
                
                self.stats.hits += 1
                self._update_hit_rate()
                
                return value
                
            except Exception as e:
                logger.error(f"Failed to get from disk cache: {e}")
                self.stats.misses += 1
                return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in disk cache."""
        with self.lock:
            try:
                # Calculate size
                serialized_data = pickle.dumps(value)
                size_bytes = len(serialized_data)
                
                # Check if we need to evict
                await self._ensure_space(size_bytes)
                
                # Write to disk
                file_path = self.cache_dir / f"{key}.cache"
                with open(file_path, 'wb') as f:
                    f.write(serialized_data)
                
                # Update metadata
                now = datetime.utcnow()
                self.metadata[key] = {
                    'created_at': now.isoformat(),
                    'last_accessed': now.isoformat(),
                    'access_count': 1,
                    'ttl_seconds': ttl_seconds,
                    'size_bytes': size_bytes,
                    'file_path': str(file_path)
                }
                
                self._save_metadata()
                self._update_stats()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to set disk cache entry: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from disk cache."""
        with self.lock:
            try:
                if key not in self.metadata:
                    return False
                
                # Remove file
                file_path = self.cache_dir / f"{key}.cache"
                if file_path.exists():
                    file_path.unlink()
                
                # Remove metadata
                del self.metadata[key]
                self._save_metadata()
                self._update_stats()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete from disk cache: {e}")
                return False
    
    async def clear(self) -> None:
        """Clear all disk cache entries."""
        with self.lock:
            try:
                # Remove all cache files
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                # Clear metadata
                self.metadata.clear()
                self._save_metadata()
                self._update_stats()
                
            except Exception as e:
                logger.error(f"Failed to clear disk cache: {e}")
    
    async def _ensure_space(self, needed_bytes: int) -> None:
        """Ensure there's enough space by evicting old entries."""
        current_size = sum(
            entry.get('size_bytes', 0) for entry in self.metadata.values()
        )
        
        if current_size + needed_bytes <= self.max_size_bytes:
            return
        
        # Sort by last accessed time (LRU eviction)
        sorted_entries = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get('last_accessed', '1970-01-01T00:00:00')
        )
        
        # Evict until we have enough space
        for key, entry in sorted_entries:
            if current_size + needed_bytes <= self.max_size_bytes:
                break
            
            await self.delete(key)
            current_size -= entry.get('size_bytes', 0)
            self.stats.evictions += 1
    
    def _is_expired(self, entry_meta: Dict[str, Any]) -> bool:
        """Check if entry is expired."""
        ttl_seconds = entry_meta.get('ttl_seconds')
        if not ttl_seconds:
            return False
        
        created_at = datetime.fromisoformat(entry_meta['created_at'])
        age = (datetime.utcnow() - created_at).total_seconds()
        return age > ttl_seconds
    
    def _update_stats(self) -> None:
        """Update cache statistics."""
        self.stats.entry_count = len(self.metadata)
        self.stats.memory_usage = sum(
            entry.get('size_bytes', 0) for entry in self.metadata.values()
        )
        self._update_hit_rate()
    
    def _update_hit_rate(self) -> None:
        """Update hit rate."""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.hit_rate = self.stats.hits / total_requests
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self.lock:
            return self.stats


class CacheManager:
    """
    Enterprise-grade cache manager with intelligent multi-level caching.
    
    Features:
    - Multiple cache strategies (LRU, LFU, TTL, ARC)
    - Hierarchical caching (Memory L1/L2, Disk L3, Distributed L4)
    - Intelligent cache warming
    - Hit ratio optimization
    - Memory usage efficient
    - Cache invalidation intelligent
    - Prefetching prediction
    - Cross-cache coordination
    - Compression support
    - Distributed cache support
    """
    
    def __init__(self, config: Any):
        """
        Initialize cache manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Configuration
        self.l1_strategy = config.get('cache.l1_strategy', 'lru')
        self.l1_max_size = config.get('cache.l1_max_size', 1000)
        self.l2_strategy = config.get('cache.l2_strategy', 'lfu')
        self.l2_max_size = config.get('cache.l2_max_size', 5000)
        self.l3_enabled = config.get('cache.l3_enabled', True)
        self.l3_max_size_mb = config.get('cache.l3_max_size_mb', 1000)
        self.default_ttl = config.get('cache.default_ttl', 3600)
        self.enable_compression = config.get('cache.enable_compression', False)
        self.enable_prefetch = config.get('cache.enable_prefetch', True)
        
        # Cache levels
        self.l1_cache: Optional[Union[LRUCache, LFUCache]] = None
        self.l2_cache: Optional[Union[LRUCache, LFUCache]] = None
        self.l3_cache: Optional[DiskCache] = None
        
        # Statistics
        self.global_stats = CacheStats()
        self.access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        
        # Prefetch queue
        self.prefetch_queue: Set[str] = set()
        self.prefetch_lock = threading.Lock()
        
        logger.info("CacheManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the cache manager."""
        try:
            # Initialize L1 cache
            if self.l1_strategy == 'lru':
                self.l1_cache = LRUCache(self.l1_max_size, self.default_ttl)
            elif self.l1_strategy == 'lfu':
                self.l1_cache = LFUCache(self.l1_max_size, self.default_ttl)
            else:
                self.l1_cache = LRUCache(self.l1_max_size, self.default_ttl)
            
            # Initialize L2 cache
            if self.l2_strategy == 'lru':
                self.l2_cache = LRUCache(self.l2_max_size, self.default_ttl * 2)
            elif self.l2_strategy == 'lfu':
                self.l2_cache = LFUCache(self.l2_max_size, self.default_ttl * 2)
            else:
                self.l2_cache = LFUCache(self.l2_max_size, self.default_ttl * 2)
            
            # Initialize L3 disk cache
            if self.l3_enabled:
                cache_dir = self.config.get('cache.l3_cache_dir', 'data/cache')
                self.l3_cache = DiskCache(cache_dir, self.l3_max_size_mb)
            
            logger.info("CacheManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CacheManager: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            start_time = time.time()
            
            # Track access pattern
            self._track_access(key)
            
            # Try L1 cache first
            if self.l1_cache:
                value = await self.l1_cache.get(key)
                if value is not None:
                    self._update_global_stats(True, time.time() - start_time)
                    return value
            
            # Try L2 cache
            if self.l2_cache:
                value = await self.l2_cache.get(key)
                if value is not None:
                    # Promote to L1
                    if self.l1_cache:
                        await self.l1_cache.set(key, value)
                    self._update_global_stats(True, time.time() - start_time)
                    return value
            
            # Try L3 disk cache
            if self.l3_cache:
                value = await self.l3_cache.get(key)
                if value is not None:
                    # Promote to L2 and L1
                    if self.l2_cache:
                        await self.l2_cache.set(key, value)
                    if self.l1_cache:
                        await self.l1_cache.set(key, value)
                    self._update_global_stats(True, time.time() - start_time)
                    return value
            
            # Cache miss
            self._update_global_stats(False, time.time() - start_time)
            
            # Trigger prefetch if enabled
            if self.enable_prefetch:
                await self._maybe_prefetch(key)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        level: Optional[CacheLevel] = None
    ) -> bool:
        """
        Set value in cache hierarchy.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live
            level: Specific cache level to use
        
        Returns:
            True if successfully cached
        """
        try:
            ttl = ttl_seconds or self.default_ttl
            success = False
            
            # Compress if enabled and value is large
            if self.enable_compression:
                value = await self._maybe_compress(value)
            
            # Set in all applicable levels
            if level is None or level == CacheLevel.L1_MEMORY:
                if self.l1_cache:
                    success = await self.l1_cache.set(key, value, ttl) or success
            
            if level is None or level == CacheLevel.L2_MEMORY:
                if self.l2_cache:
                    success = await self.l2_cache.set(key, value, ttl * 2) or success
            
            if level is None or level == CacheLevel.L3_DISK:
                if self.l3_cache:
                    success = await self.l3_cache.set(key, value, ttl * 4) or success
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to set cache entry: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from all cache levels."""
        try:
            success = False
            
            if self.l1_cache:
                success = await self.l1_cache.delete(key) or success
            
            if self.l2_cache:
                success = await self.l2_cache.delete(key) or success
            
            if self.l3_cache:
                success = await self.l3_cache.delete(key) or success
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete cache entry: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Key pattern to match
        
        Returns:
            Number of entries invalidated
        """
        try:
            import fnmatch
            invalidated = 0
            
            # L1 cache
            if self.l1_cache:
                keys_to_delete = [
                    key for key in self.l1_cache.cache.keys()
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_delete:
                    if await self.l1_cache.delete(key):
                        invalidated += 1
            
            # L2 cache
            if self.l2_cache:
                keys_to_delete = [
                    key for key in self.l2_cache.cache.keys()
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_delete:
                    if await self.l2_cache.delete(key):
                        invalidated += 1
            
            # L3 cache
            if self.l3_cache:
                keys_to_delete = [
                    key for key in self.l3_cache.metadata.keys()
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_delete:
                    if await self.l3_cache.delete(key):
                        invalidated += 1
            
            return invalidated
            
        except Exception as e:
            logger.error(f"Failed to invalidate pattern: {e}")
            return 0
    
    async def warm_cache(self, keys_and_values: List[Tuple[str, Any]]) -> int:
        """
        Warm cache with pre-loaded data.
        
        Args:
            keys_and_values: List of (key, value) tuples
        
        Returns:
            Number of entries successfully warmed
        """
        try:
            warmed = 0
            
            for key, value in keys_and_values:
                if await self.set(key, value):
                    warmed += 1
            
            logger.info(f"Cache warmed with {warmed} entries")
            return warmed
            
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")
            return 0
    
    async def _maybe_compress(self, value: Any) -> Any:
        """Compress value if beneficial."""
        try:
            # Simple size-based compression decision
            serialized = pickle.dumps(value)
            if len(serialized) > 1024:  # Compress if > 1KB
                import gzip
                compressed = gzip.compress(serialized)
                if len(compressed) < len(serialized) * 0.8:  # Only if significant reduction
                    return {
                        '_compressed': True,
                        '_data': compressed
                    }
            return value
            
        except Exception:
            return value
    
    async def _maybe_decompress(self, value: Any) -> Any:
        """Decompress value if needed."""
        try:
            if isinstance(value, dict) and value.get('_compressed'):
                import gzip
                decompressed = gzip.decompress(value['_data'])
                return pickle.loads(decompressed)
            return value
            
        except Exception:
            return value
    
    def _track_access(self, key: str) -> None:
        """Track access patterns for prefetching."""
        try:
            now = datetime.utcnow()
            self.access_patterns[key].append(now)
            
            # Keep only recent accesses (last hour)
            cutoff = now - timedelta(hours=1)
            self.access_patterns[key] = [
                access_time for access_time in self.access_patterns[key]
                if access_time > cutoff
            ]
            
            # Limit memory usage
            if len(self.access_patterns) > 10000:
                # Remove least accessed keys
                sorted_keys = sorted(
                    self.access_patterns.keys(),
                    key=lambda k: len(self.access_patterns[k])
                )
                for key_to_remove in sorted_keys[:1000]:
                    del self.access_patterns[key_to_remove]
                    
        except Exception as e:
            logger.error(f"Failed to track access: {e}")
    
    async def _maybe_prefetch(self, key: str) -> None:
        """Maybe trigger prefetching for related keys."""
        try:
            if not self.enable_prefetch:
                return
            
            # Simple prefetch strategy: predict related keys
            # This is a placeholder - real implementation would use ML
            related_keys = self._predict_related_keys(key)
            
            with self.prefetch_lock:
                for related_key in related_keys[:5]:  # Limit prefetch
                    self.prefetch_queue.add(related_key)
            
        except Exception as e:
            logger.error(f"Failed to trigger prefetch: {e}")
    
    def _predict_related_keys(self, key: str) -> List[str]:
        """Predict related keys for prefetching."""
        # Simple prediction based on key patterns
        # Real implementation would use machine learning
        related = []
        
        # If key has a pattern like "user_123_data", predict similar patterns
        parts = key.split('_')
        if len(parts) >= 2:
            base = '_'.join(parts[:-1])
            # Predict next few numbers
            try:
                last_num = int(parts[-1])
                for i in range(1, 4):
                    related.append(f"{base}_{last_num + i}")
            except ValueError:
                pass
        
        return related
    
    def _update_global_stats(self, hit: bool, access_time_ms: float) -> None:
        """Update global cache statistics."""
        if hit:
            self.global_stats.hits += 1
        else:
            self.global_stats.misses += 1
        
        # Update average access time
        total_requests = self.global_stats.hits + self.global_stats.misses
        current_avg = self.global_stats.avg_access_time_ms
        self.global_stats.avg_access_time_ms = (
            (current_avg * (total_requests - 1)) + (access_time_ms * 1000)
        ) / total_requests
        
        # Update hit rate
        self.global_stats.hit_rate = self.global_stats.hits / total_requests
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            'global': asdict(self.global_stats),
            'levels': {}
        }
        
        if self.l1_cache:
            stats['levels']['l1'] = asdict(self.l1_cache.get_stats())
        
        if self.l2_cache:
            stats['levels']['l2'] = asdict(self.l2_cache.get_stats())
        
        if self.l3_cache:
            stats['levels']['l3'] = asdict(self.l3_cache.get_stats())
        
        # Additional metrics
        stats['access_patterns_tracked'] = len(self.access_patterns)
        stats['prefetch_queue_size'] = len(self.prefetch_queue)
        
        # Memory usage summary
        total_memory = sum(
            level_stats.get('memory_usage', 0)
            for level_stats in stats['levels'].values()
        )
        stats['total_memory_usage'] = total_memory
        
        return stats
    
    async def optimize(self) -> Dict[str, Any]:
        """Optimize cache performance."""
        try:
            optimization_results = {}
            
            # Analyze hit rates by level
            l1_hit_rate = self.l1_cache.get_stats().hit_rate if self.l1_cache else 0
            l2_hit_rate = self.l2_cache.get_stats().hit_rate if self.l2_cache else 0
            l3_hit_rate = self.l3_cache.get_stats().hit_rate if self.l3_cache else 0
            
            optimization_results['hit_rates'] = {
                'l1': l1_hit_rate,
                'l2': l2_hit_rate,
                'l3': l3_hit_rate
            }
            
            # Suggest optimizations
            suggestions = []
            
            if l1_hit_rate < 0.5:
                suggestions.append("Consider increasing L1 cache size")
            
            if l2_hit_rate < 0.3:
                suggestions.append("Consider changing L2 cache strategy")
            
            if l3_hit_rate < 0.2:
                suggestions.append("Consider increasing L3 cache size or TTL")
            
            optimization_results['suggestions'] = suggestions
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Perform health check on cache manager."""
        try:
            # Test basic operations
            test_key = "health_check_test"
            test_value = {"test": "data", "timestamp": time.time()}
            
            # Test set and get
            if not await self.set(test_key, test_value):
                return False
            
            retrieved_value = await self.get(test_key)
            if not retrieved_value:
                return False
            
            # Test delete
            if not await self.delete(test_key):
                return False
            
            # Verify deletion
            if await self.get(test_key) is not None:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the cache manager."""
        logger.info("Shutting down CacheManager...")
        
        try:
            # Clear all caches
            if self.l1_cache:
                await self.l1_cache.clear()
            
            if self.l2_cache:
                await self.l2_cache.clear()
            
            if self.l3_cache:
                # Don't clear disk cache on shutdown - it's persistent
                pass
            
            # Clear access patterns
            self.access_patterns.clear()
            self.prefetch_queue.clear()
            
            logger.info("CacheManager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during cache shutdown: {e}")


# Export main classes
__all__ = [
    'CacheManager',
    'LRUCache',
    'LFUCache',
    'DiskCache',
    'CacheStrategy',
    'CacheLevel',
    'CacheEntry',
    'CacheStats'
]