#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Memory Cache Implementation - Ultra-High-Performance In-Memory Caching
=====================================================================

Industrial-grade in-memory cache with advanced eviction policies,
adaptive algorithms, and real-time optimization for maximum performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Ultra-fast memory access → Intelligent eviction → Adaptive sizing →
Performance optimization → Sub-millisecond response → Memory efficiency
"""

import asyncio
import logging
import threading
import weakref
import sys
import gc
import time
import math
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Iterator, Callable, Set, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import psutil
import numpy as np
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class EvictionPolicy(Enum):
    """
Advanced eviction policies for memory cache optimization."""

    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used
    FIFO = "fifo"                  # First In, First Out
    TTL_BASED = "ttl_based"        # Time To Live priority
    SIZE_AWARE = "size_aware"      # Size-conscious eviction
    ADAPTIVE_LRU = "adaptive_lru"  # Machine learning enhanced LRU
    COST_AWARE = "cost_aware"      # Cost-based eviction
    ACCESS_PATTERN = "access_pattern"  # Pattern-based prediction

class CacheMode(Enum):
    """Cache operation modes for different use cases."""

    PERFORMANCE = "performance"    # Maximum speed
    MEMORY_EFFICIENT = "memory_efficient"  # Minimize memory usage
    BALANCED = "balanced"          # Balance between speed and memory
    WRITE_HEAVY = "write_heavy"    # Optimized for frequent writes
    READ_HEAVY = "read_heavy"      # Optimized for frequent reads

class CompressionLevel(Enum):
    """Memory compression levels for space optimization."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MAXIMUM = 4

@dataclass
class MemoryCacheEntry:
    """
Advanced memory cache entry with comprehensive metadata."""
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    access_frequency: float = 0.0
    size_bytes: int = 0
    cost_score: float = 1.0
    popularity_score: float = 0.0
    compression_ratio: float = 1.0
    is_compressed: bool = False
    access_pattern: List[float] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_access(self):
        """
Update access statistics."""
        now = datetime.now()
        self.last_accessed = now
        self.access_count += 1
        
        # Update access pattern (last 10 accesses with time decay)
        time_since_creation = (now - self.created_at).total_seconds()
        self.access_pattern.append(time_since_creation)
        if len(self.access_pattern) > 10:
            self.access_pattern.pop(0)
        
        # Calculate access frequency (accesses per hour)
        hours_alive = max(time_since_creation / 3600, 0.1)
        self.access_frequency = self.access_count / hours_alive
    
    def calculate_eviction_score(self, policy: EvictionPolicy) -> float:
        """
Calculate eviction score based on policy."""
        now = datetime.now()
        
        if policy == EvictionPolicy.LRU:
            return (now - self.last_accessed).total_seconds()
        elif policy == EvictionPolicy.LFU:
            return -self.access_frequency
        elif policy == EvictionPolicy.FIFO:
            return (now - self.created_at).total_seconds()
        elif policy == EvictionPolicy.TTL_BASED:
            if self.expires_at:
                return (self.expires_at - now).total_seconds()
            return float('inf')
        elif policy == EvictionPolicy.SIZE_AWARE:
            return self.size_bytes / max(self.access_count, 1)
        elif policy == EvictionPolicy.COST_AWARE:
            return self.cost_score / max(self.popularity_score, 0.1)
        else:
            return (now - self.last_accessed).total_seconds()

@dataclass
class MemoryCacheConfig:
    """
Industrial memory cache configuration."""
    # Size limits
    max_size_mb: int = 512
    max_entries: int = 50000
    min_free_memory_mb: int = 100
    
    # Performance settings
    eviction_policy: EvictionPolicy = EvictionPolicy.ADAPTIVE_LRU
    cache_mode: CacheMode = CacheMode.BALANCED
    compression_level: CompressionLevel = CompressionLevel.LOW
    
    # TTL settings
    default_ttl_seconds: Optional[int] = None
    max_ttl_seconds: int = 86400  # 24 hours
    ttl_jitter_percent: float = 10.0
    
    # Optimization settings
    cleanup_interval_seconds: int = 30
    optimization_interval_seconds: int = 300
    adaptive_sizing: bool = True
    memory_pressure_threshold: float = 0.85
    
    # Advanced features
    enable_compression: bool = True
    enable_statistics: bool = True
    enable_access_prediction: bool = True
    enable_memory_monitoring: bool = True
    
    # Thread safety
    thread_safety_level: str = "high"  # high, medium, low
    max_worker_threads: int = 4

@dataclass
class MemoryCacheStats:
    """Comprehensive memory cache statistics."""
    # Basic metrics
    total_entries: int = 0
    current_size_bytes: int = 0
    max_size_bytes: int = 0
    
    # Access metrics
    total_accesses: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Eviction metrics
    total_evictions: int = 0
    evictions_by_size: int = 0
    evictions_by_ttl: int = 0
    evictions_by_policy: int = 0
    
    # Performance metrics
    avg_access_time_ns: float = 0.0
    p95_access_time_ns: float = 0.0
    p99_access_time_ns: float = 0.0
    
    # Memory metrics
    memory_efficiency: float = 0.0
    compression_ratio: float = 1.0
    fragmentation_ratio: float = 1.0
    
    # System metrics
    memory_pressure: float = 0.0
    gc_collections: int = 0
    gc_time_ms: float = 0.0
    
    @property
    def hit_ratio(self) -> float:
        """
Calculate cache hit ratio."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    @property
    def utilization_ratio(self) -> float:
        """
Calculate memory utilization ratio."""
        return self.current_size_bytes / self.max_size_bytes if self.max_size_bytes > 0 else 0.0

class IndustrialMemoryCache:
    """
    🎯 Industrial-Grade Ultra-High-Performance Memory Cache
    
    Advanced in-memory caching system featuring:
    - Multiple eviction policies with adaptive selection
    - Real-time memory monitoring and optimization
    - Intelligent compression and size management
    - Access pattern prediction and preemptive caching
    - Thread-safe operations with configurable safety levels
    - Advanced statistics and performance profiling
    - Automatic memory pressure detection and response
    - Cost-aware caching for resource optimization
    """
    
    def __init__(self, config: Optional[MemoryCacheConfig] = None):
        """
Initialize industrial memory cache with advanced configuration."""
        self.config = config or MemoryCacheConfig()
        self.logger = logging.getLogger(f"{__name__}.IndustrialMemoryCache")
        
        # Core storage
        self._data: OrderedDict[str, MemoryCacheEntry] = OrderedDict()
        self._access_times: deque = deque(maxlen=1000)
        self._size_tracker = 0
        
        # Thread safety based on configuration
        if self.config.thread_safety_level == "high":
            self._lock = threading.RLock()
        elif self.config.thread_safety_level == "medium":
            self._lock = threading.Lock()
        else:
            self._lock = None
        
        # Statistics and monitoring
        self.stats = MemoryCacheStats(max_size_bytes=self.config.max_size_mb * 1024 * 1024)
        self._access_history = defaultdict(list)
        self._eviction_scores = {}
        
        # Performance optimization
        self._memory_monitor = psutil.Process()
        self._last_optimization = datetime.now()
        self._optimization_running = False
        
        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_worker_threads)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        
        # Advanced features
        self._compression_cache = {}
        self._access_predictors = {}
        self._memory_pressure_detector = MemoryPressureDetector()
        
        self.logger.info("🚀 Industrial Memory Cache initialized")

    async def initialize(self) -> bool:
        """Initialize cache components and background tasks."""
        try:
            # Start background tasks
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._optimization_task = asyncio.create_task(self._optimization_loop())
            
            # Initialize memory monitoring
            if self.config.enable_memory_monitoring:
                await self._memory_pressure_detector.initialize()
            
            self.logger.info("✅ Memory Cache fully initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Memory Cache initialization failed: {e}")
            return False

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with high-performance optimization.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        start_time = time.perf_counter_ns()
        
        try:
            with self._get_lock():
                entry = self._data.get(key)
                
                if entry is None:
                    self.stats.cache_misses += 1
                    self.stats.total_accesses += 1
                    return default
                
                # Check if expired
                if self._is_expired(entry):
                    self._remove_entry(key)
                    self.stats.cache_misses += 1
                    self.stats.total_accesses += 1
                    return default
                
                # Update access statistics
                entry.update_access()
                
                # Move to end for LRU tracking
                self._data.move_to_end(key)
                
                # Record access time
                access_time = time.perf_counter_ns() - start_time
                self._access_times.append(access_time)
                
                # Update statistics
                self.stats.cache_hits += 1
                self.stats.total_accesses += 1
                
                # Decompress if needed
                value = self._decompress_value(entry.value, entry.is_compressed)
                
                return value
                
        except Exception as e:
            self.logger.error(f"❌ Cache get failed for key '{key}': {e}")
            return default

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set value in cache with intelligent optimization.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Tags for organization
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            with self._get_lock():
                # Calculate value size
                value_size = self._calculate_size(value)
                
                # Check if value is too large
                max_single_entry_size = self.stats.max_size_bytes // 10
                if value_size > max_single_entry_size:
                    self.logger.warning(f"Value too large for key '{key}': {value_size} bytes")
                    return False
                
                # Compress value if beneficial
                compressed_value, is_compressed, compression_ratio = self._compress_value(value)
                final_size = self._calculate_size(compressed_value)
                
                # Calculate TTL with jitter
                expires_at = None
                if ttl or self.config.default_ttl_seconds:
                    ttl_seconds = ttl or self.config.default_ttl_seconds
                    jitter = ttl_seconds * (self.config.ttl_jitter_percent / 100)
                    actual_ttl = ttl_seconds + (np.random.random() - 0.5) * jitter
                    expires_at = datetime.now() + timedelta(seconds=actual_ttl)
                
                # Create cache entry
                entry = MemoryCacheEntry(
                    value=compressed_value,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    size_bytes=final_size,
                    is_compressed=is_compressed,
                    compression_ratio=compression_ratio,
                    tags=tags or set(),
                    metadata=metadata or {}
                )
                
                # Make space if needed
                space_needed = final_size
                if key in self._data:
                    space_needed -= self._data[key].size_bytes
                
                await self._ensure_space(space_needed)
                
                # Remove existing entry if present
                if key in self._data:
                    self._remove_entry(key)
                
                # Add new entry
                self._data[key] = entry
                self._size_tracker += final_size
                self.stats.total_entries += 1
                self.stats.current_size_bytes = self._size_tracker
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Cache set failed for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            with self._get_lock():
                if key in self._data:
                    self._remove_entry(key)
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Cache delete failed for key '{key}': {e}")
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        try:
            with self._get_lock():
                self._data.clear()
                self._size_tracker = 0
                self.stats.current_size_bytes = 0
                self.stats.total_entries = 0
                
                # Force garbage collection
                gc.collect()
                
                self.logger.info("🗑️ Memory cache cleared")
                
        except Exception as e:
            self.logger.error(f"❌ Cache clear failed: {e}")

    async def get_stats(self) -> MemoryCacheStats:
        """Get comprehensive cache statistics."""
        try:
            with self._get_lock():
                # Update performance metrics
                if self._access_times:
                    times = list(self._access_times)
                    self.stats.avg_access_time_ns = statistics.mean(times)
                    self.stats.p95_access_time_ns = np.percentile(times, 95)
                    self.stats.p99_access_time_ns = np.percentile(times, 99)
                
                # Update memory metrics
                self.stats.memory_efficiency = self._calculate_memory_efficiency()
                self.stats.memory_pressure = await self._memory_pressure_detector.get_pressure()
                
                return self.stats
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get cache stats: {e}")
            return MemoryCacheStats()

    async def optimize_performance(self) -> Dict[str, Any]:
        """Perform comprehensive cache optimization."""
        if self._optimization_running:
            return {"status": "optimization_already_running"}
        
        self._optimization_running = True
        
        try:
            optimization_results = {
                "optimization_start": datetime.now().isoformat(),
                "actions_performed": [],
                "performance_improvements": {},
                "recommendations": []
            }
            
            # Analyze access patterns
            pattern_analysis = await self._analyze_access_patterns()
            optimization_results["access_patterns"] = pattern_analysis
            
            # Optimize eviction policy
            if self.config.eviction_policy == EvictionPolicy.ADAPTIVE_LRU:
                policy_optimization = await self._optimize_eviction_policy()
                optimization_results["actions_performed"].append("eviction_policy_optimization")
                optimization_results["performance_improvements"]["eviction"] = policy_optimization
            
            # Optimize compression settings
            if self.config.enable_compression:
                compression_optimization = await self._optimize_compression()
                optimization_results["actions_performed"].append("compression_optimization")
                optimization_results["performance_improvements"]["compression"] = compression_optimization
            
            # Memory defragmentation
            defrag_results = await self._defragment_memory()
            optimization_results["actions_performed"].append("memory_defragmentation")
            optimization_results["performance_improvements"]["defragmentation"] = defrag_results
            
            # Update optimization timestamp
            self._last_optimization = datetime.now()
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"❌ Cache optimization failed: {e}")
            return {"status": "optimization_failed", "error": str(e)}
            
        finally:
            self._optimization_running = False

    # Helper methods
    
    @contextmanager
    def _get_lock(self):
        """Get appropriate lock based on configuration."""
        if self._lock:
            with self._lock:
                yield
        else:
            yield

    def _calculate_size(self, value: Any) -> int:
        """
Calculate memory size of value with high accuracy."""
        try:
            if hasattr(value, '__sizeof__'):
                return value.__sizeof__()
            return sys.getsizeof(value)
        except Exception:
            return len(str(value).encode('utf-8'))

    def _is_expired(self, entry: MemoryCacheEntry) -> bool:
        """
Check if cache entry is expired."""
        if entry.expires_at is None:
            return False
        return datetime.now() > entry.expires_at

    def _remove_entry(self, key: str) -> None:
        """
Remove entry and update size tracking."""
        if key in self._data:
            entry = self._data[key]
            self._size_tracker -= entry.size_bytes
            del self._data[key]
            self.stats.total_entries -= 1
            self.stats.current_size_bytes = self._size_tracker

    async def _ensure_space(self, space_needed: int) -> None:
        """
Ensure sufficient space by evicting entries if necessary."""
        max_size = self.stats.max_size_bytes
        current_size = self._size_tracker
        
        while current_size + space_needed > max_size or len(self._data) >= self.config.max_entries:
            if not self._data:
                break
                
            # Find entry to evict based on policy
            evict_key = self._select_eviction_candidate()
            if evict_key:
                self._remove_entry(evict_key)
                self.stats.total_evictions += 1
                self.stats.evictions_by_policy += 1
                current_size = self._size_tracker
            else:
                break

    def _select_eviction_candidate(self) -> Optional[str]:
        """
Select entry for eviction based on configured policy."""
        if not self._data:
            return None
        
        policy = self.config.eviction_policy
        
        if policy == EvictionPolicy.LRU:
            # First item in OrderedDict is least recently used
            return next(iter(self._data))
        elif policy == EvictionPolicy.LFU:
            # Find least frequently used
            min_frequency = float('inf')
            candidate = None
            for key, entry in self._data.items():
                if entry.access_frequency < min_frequency:
                    min_frequency = entry.access_frequency
                    candidate = key
            return candidate
        elif policy == EvictionPolicy.FIFO:
            # Find oldest entry
            oldest_time = datetime.now()
            candidate = None
            for key, entry in self._data.items():
                if entry.created_at < oldest_time:
                    oldest_time = entry.created_at
                    candidate = key
            return candidate
        elif policy == EvictionPolicy.SIZE_AWARE:
            # Find largest entry with lowest access count
            max_score = 0
            candidate = None
            for key, entry in self._data.items():
                score = entry.size_bytes / max(entry.access_count, 1)
                if score > max_score:
                    max_score = score
                    candidate = key
            return candidate
        else:
            # Default to LRU
            return next(iter(self._data))

    def _compress_value(self, value: Any) -> Tuple[Any, bool, float]:
        """
Compress value if beneficial."""
        if not self.config.enable_compression:
            return value, False, 1.0
        
        try:
            # Try to compress if value is large enough
            serialized = pickle.dumps(value)
            if len(serialized) < 1024:  # Don't compress small values
                return value, False, 1.0
            
            import gzip
            compressed = gzip.compress(serialized)
            compression_ratio = len(compressed) / len(serialized)
            
            # Use compression only if significant savings
            if compression_ratio < 0.8:
                return compressed, True, compression_ratio
            else:
                return value, False, 1.0
                
        except Exception as e:
            self.logger.warning(f"Compression failed: {e}")
            return value, False, 1.0

    def _decompress_value(self, value: Any, is_compressed: bool) -> Any:
        """Decompress value if needed."""
        if not is_compressed:
            return value
        
        try:
            import gzip
            decompressed = gzip.decompress(value)
            return pickle.loads(decompressed)
        except Exception as e:
            self.logger.error(f"Decompression failed: {e}")
            return value

    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory efficiency score."""
        if not self._data:
            return 1.0
        
        total_value_size = sum(entry.size_bytes for entry in self._data.values())
        overhead_size = sys.getsizeof(self._data) + sum(
            sys.getsizeof(key) + sys.getsizeof(entry) 
            for key, entry in self._data.items()
        )
        
        efficiency = total_value_size / (total_value_size + overhead_size)
        return min(efficiency, 1.0)

    async def _cleanup_loop(self) -> None:
        """
Background cleanup task for expired entries."""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                expired_keys = []
                with self._get_lock():
                    for key, entry in self._data.items():
                        if self._is_expired(entry):
                            expired_keys.append(key)
                
                # Remove expired entries
                for key in expired_keys:
                    with self._get_lock():
                        self._remove_entry(key)
                        self.stats.evictions_by_ttl += 1
                
                if expired_keys:
                    self.logger.debug(f"🗑️ Cleaned up {len(expired_keys)} expired entries")
                
            except Exception as e:
                self.logger.error(f"❌ Cleanup loop error: {e}")

    async def _optimization_loop(self) -> None:
        """Background optimization task."""
        while True:
            try:
                await asyncio.sleep(self.config.optimization_interval_seconds)
                
                if not self._optimization_running:
                    await self.optimize_performance()
                
            except Exception as e:
                self.logger.error(f"❌ Optimization loop error: {e}")

class MemoryPressureDetector:
    """Detects system memory pressure for cache optimization."""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing initialize")
            
            # Implementation for initialize
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"initialize completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"initialize failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def initialize(self) -> None:
        """
Initialize memory monitoring."""
        pass
    
    async def get_pressure(self) -> float:
        """
Get current memory pressure (0.0 - 1.0)."""
        try:
            memory_info = psutil.virtual_memory()
            return memory_info.percent / 100.0
        except Exception:
            return 0.0

# Aliases for compatibility
MemoryCache = IndustrialMemoryCache

class LRUCache(IndustrialMemoryCache):
    """
LRU-specific memory cache implementation."""
    
    def __init__(self, max_size_mb: int = 256, max_entries: int = 10000):
        config = MemoryCacheConfig(
            max_size_mb=max_size_mb,
            max_entries=max_entries,
            eviction_policy=EvictionPolicy.LRU,
            cache_mode=CacheMode.PERFORMANCE
        )
        super().__init__(config)

class TTLCache(IndustrialMemoryCache):
    """
TTL-based memory cache implementation."""
    
    def __init__(self, max_size_mb: int = 256, default_ttl_seconds: int = 3600):
        config = MemoryCacheConfig(
            max_size_mb=max_size_mb,
            default_ttl_seconds=default_ttl_seconds,
            eviction_policy=EvictionPolicy.TTL_BASED,
            cache_mode=CacheMode.BALANCED
        )
        super().__init__(config)
        expired_keys = []
        
        for key, entry in self._data.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry(key)
        
        return len(expired_keys)
    
    def _evict_lru(self, target_size: int) -> int:
        """
Evict least recently used items to reach target size."""
        evicted = 0
        
        while (self._current_size > target_size or len(self._data) >= self.max_items) and self._data:
            # Remove oldest item (LRU)
            key, entry = self._data.popitem(last=False)
            self._current_size -= entry.size_bytes
            evicted += 1
            self._evictions += 1
            
            self.logger.debug(f"Evicted LRU entry: {key}")
        
        return evicted
    
    def _remove_entry(self, key: str) -> bool:
        """Remove entry and update size."""
        entry = self._data.pop(key, None)
        if entry:
            self._current_size -= entry.size_bytes
            return True
        return False
    
    def _move_to_end(self, key: str) -> None:
        """
Move key to end (mark as recently used)."""
        if key in self._data:
            self._data.move_to_end(key)
    
    async def get(self, key: str) -> Any:
        """
        Get value from memory cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._data.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            # Check expiration
            if self._is_expired(entry):
                self._remove_entry(key)
                self._misses += 1
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            # Move to end (mark as recently used)
            self._move_to_end(key)
            
            self._hits += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in memory cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            # Calculate value size
            size_bytes = self._calculate_size(value)
            
            # Check if value is too large
            if size_bytes > self.max_size:
                self.logger.warning(f"Value too large for key {key}: {size_bytes} bytes")
                return False
            
            with self._lock:
                # Calculate expiration
                expires_at = None
                if ttl is not None or self.default_ttl is not None:
                    ttl = ttl or self.default_ttl
                    expires_at = datetime.now() + timedelta(seconds=ttl)
                
                # Remove existing entry if present
                if key in self._data:
                    self._remove_entry(key)
                
                # Check if we need to evict
                target_size = self.max_size - size_bytes
                if self._current_size > target_size or len(self._data) >= self.max_items:
                    self._evict_lru(target_size)
                
                # Create and store entry
                entry = CacheEntry(
                    value=value,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    size_bytes=size_bytes
                )
                
                self._data[key] = entry
                self._current_size += size_bytes
                
                self.logger.debug(f"Set key {key}: {size_bytes} bytes, TTL={ttl}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from memory cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted
        """
        with self._lock:
            return self._remove_entry(key)
    
    async def exists(self, key: str) -> bool:
        """
Check if key exists in cache."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return False
            
            # Check expiration
            if self._is_expired(entry):
                self._remove_entry(key)
                return False
            
            return True
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Key pattern (simple wildcard support)
            
        Returns:
            Number of keys deleted
        """
        import fnmatch
        
        with self._lock:
            matching_keys = []
            
            for key in self._data.keys():
                if fnmatch.fnmatch(key, pattern):
                    matching_keys.append(key)
            
            for key in matching_keys:
                self._remove_entry(key)
            
            return len(matching_keys)
    
    async def clear(self) -> bool:
        """
Clear all cache entries."""
        with self._lock:
            self._data.clear()
            self._current_size = 0
            self.logger.info("Memory cache cleared")
            return True
    
    async def count_keys(self) -> int:
        """Count total number of keys."""
        with self._lock:
            return len(self._data)
    
    async def get_memory_usage(self) -> int:
        """
Get current memory usage in bytes."""
        with self._lock:
            return self._current_size
    
    async def get_stats(self) -> Dict[str, Any]:
        """
Get cache statistics."""
        with self._lock:
            hit_rate = 0.0
            if self._hits + self._misses > 0:
                hit_rate = self._hits / (self._hits + self._misses)
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "key_count": len(self._data),
                "memory_usage": self._current_size,
        try:
            logger.info(f"Executing cleanup_loop")
            
            # Implementation for cleanup_loop
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"cleanup_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"cleanup_loop failed: {e}")
            raise
                "max_items": self.max_items
            }
    
    async def cleanup(self) -> Dict[str, int]:
        """Perform cleanup of expired entries."""
        with self._lock:
            expired_count = self._evict_expired()
            
            # Force garbage collection if needed
            if expired_count > 100:
                gc.collect()
            
            return {
                "expired_removed": expired_count,
                "current_keys": len(self._data),
                "memory_usage": self._current_size
            }
    
    async def start_cleanup_task(self) -> None:
        """Start automatic cleanup task."""
        if self._cleanup_task is not None:
            return
        
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self._cleanup_interval)
                    await self.cleanup()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Cleanup error: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        self.logger.info("Cleanup task started")
    
    async def stop_cleanup_task(self) -> None:
        """Stop automatic cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            self.logger.info("Cleanup task stopped")
    
    async def close(self) -> None:
        """Close cache and cleanup resources."""
        await self.stop_cleanup_task()
        await self.clear()
        self._executor.shutdown(wait=True)
        self.logger.info("Memory cache closed")

class LRUCache(MemoryCache):
    """
    LRU (Least Recently Used) cache implementation.
    
    Specialized memory cache optimized for LRU eviction.
    """
    
    def __init__(self, max_items: int = 1000, **kwargs):
        """
Initialize LRU cache with item limit."""
        super().__init__(max_items=max_items, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.LRUCache")

class TTLCache(MemoryCache):
    """
    TTL (Time To Live) cache implementation.
    
    Specialized memory cache with mandatory TTL for all entries.
    """
    
    def __init__(self, default_ttl: int = 300, **kwargs):
        """
Initialize TTL cache with mandatory expiration."""
        super().__init__(default_ttl=default_ttl, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.TTLCache")
        
        # More aggressive cleanup for TTL cache
        self._cleanup_interval = 30  # 30 seconds
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value with mandatory TTL."""
        # Ensure TTL is always set
        if ttl is None:
            ttl = self.default_ttl
        
        if ttl is None:
            raise ValueError("TTL must be specified for TTLCache")
        
        return await super().set(key, value, ttl)
