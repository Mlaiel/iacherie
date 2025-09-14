"""Language Cache - Advanced Caching and Performance Optimization Engine
================================================================================
Module: backend/languages/language_cache.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Language Cache Engine - Multi-tier Caching and Performance
Responsibility: Advanced caching, performance optimization, cache invalidation strategies
Technologies: Python, Redis, Memory Caching, Performance Monitoring, Cache Strategies
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Cache request → Cache strategy selection → Multi-tier lookup → 
Performance monitoring → Cache optimization → Invalidation management → Response delivery
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import hashlib
import pickle
from pathlib import Path

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels in multi-tier architecture"""
    L1_MEMORY = "l1_memory"         # In-memory cache (fastest)
    L2_REDIS = "l2_redis"          # Redis cache (fast)
    L3_DISK = "l3_disk"            # Disk cache (slower but persistent)
    L4_DATABASE = "l4_database"     # Database cache (slowest but most persistent)


class CacheStrategy(Enum):
    """Cache strategies for different content types"""
    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used
    FIFO = "fifo"                  # First In, First Out
    TTL = "ttl"                    # Time To Live
    ADAPTIVE = "adaptive"          # Adaptive based on usage patterns
    WRITE_THROUGH = "write_through" # Write to cache and storage simultaneously
    WRITE_BACK = "write_back"      # Write to cache first, then to storage


class CacheOperation(Enum):
    """Cache operations"""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    INVALIDATE = "invalidate"
    REFRESH = "refresh"
    PRELOAD = "preload"


class CacheContentType(Enum):
    """Types of content that can be cached"""
    TRANSLATION = "translation"
    DETECTION = "detection"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    VOICE_SYNTHESIS = "voice_synthesis"
    QUALITY_ASSESSMENT = "quality_assessment"
    LANGUAGE_MODEL = "language_model"
    ANALYTICS = "analytics"
    ACCESSIBILITY = "accessibility"


@dataclass
class CacheKey:
    """Cache key structure"""
    content_type: CacheContentType
    language_code: str
    content_hash: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_string(self) -> str:
        """Convert cache key to string"""
        params_str = json.dumps(self.parameters, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{self.content_type.value}:{self.language_code}:{self.content_hash}:{params_hash}"


@dataclass
class CacheEntry:
    """Cache entry structure"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now(timezone.utc) > expiry_time
    
    def update_access(self) -> None:
        """Update access statistics"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1


@dataclass
class CacheRequest:
    """Request for cache operations"""
    operation: CacheOperation
    cache_key: CacheKey
    value: Optional[Any] = None
    ttl_seconds: Optional[int] = None
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    levels: List[CacheLevel] = field(default_factory=lambda: [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS])


@dataclass
class CacheResult:
    """Result from cache operation"""
    success: bool
    value: Optional[Any] = None
    cache_hit: bool = False
    cache_level: Optional[CacheLevel] = None
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    avg_latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    evictions: int = 0
    level_stats: Dict[CacheLevel, Dict[str, int]] = field(default_factory=dict)


@dataclass
class CacheConfig:
    """Cache configuration"""
    max_memory_mb: int = 1024
    default_ttl_seconds: int = 3600
    max_entries_per_level: Dict[CacheLevel, int] = field(default_factory=lambda: {
        CacheLevel.L1_MEMORY: 10000,
        CacheLevel.L2_REDIS: 100000,
        CacheLevel.L3_DISK: 1000000
    })
    eviction_strategy: CacheStrategy = CacheStrategy.LRU
    compression_enabled: bool = True
    encryption_enabled: bool = False


class LanguageCacheEngine:
    """
    Advanced multi-tier caching engine for language processing
    with performance optimization and intelligent cache management
    """
    
    def __init__(self, config -> None: Optional[CacheConfig] = None) -> None:
        """Initialize language cache engine"""
        self.config = config or CacheConfig()
        
        # Cache storage layers
        self.l1_memory_cache: Dict[str, CacheEntry] = {}
        self.l2_redis_cache = None
        self.l3_disk_cache_dir = Path("/tmp/language_cache")
        
        # Cache statistics
        self.stats = CacheStats()
        self.level_stats = {level: {"hits": 0, "misses": 0, "latency_sum": 0.0} 
                           for level in CacheLevel}
        
        # Performance monitoring
        self.performance_metrics = {}
        self.cache_patterns = {}
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            try:
                self.l2_redis_cache = redis.Redis(
                    host='localhost', port=6379, db=0, decode_responses=False
                )
                # Test connection
                self.l2_redis_cache.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                self.l2_redis_cache = None
        
        # Create disk cache directory
        self.l3_disk_cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("LanguageCacheEngine initialized with multi-tier caching")
    
    async def get(self, cache_key: CacheKey, levels: Optional[List[CacheLevel]] = None) -> CacheResult:
        """
        Get value from cache with multi-tier lookup
        
        Args:
            cache_key: Cache key to lookup
            levels: Cache levels to search (default: all configured levels)
            
        Returns:
            CacheResult with value and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_DISK]
        
        key_str = cache_key.to_string()
        
        for level in levels:
            try:
                result = await self._get_from_level(key_str, level)
                if result.success and result.value is not None:
                    # Update statistics
                    self.stats.cache_hits += 1
                    self.level_stats[level]["hits"] += 1
                    
                    # Promote to higher cache levels if beneficial
                    await self._promote_to_higher_levels(key_str, result.value, level, levels)
                    
                    # Update access statistics
                    await self._update_access_stats(key_str, level)
                    
                    latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    self.level_stats[level]["latency_sum"] += latency
                    
                    return CacheResult(
                        success=True,
                        value=result.value,
                        cache_hit=True,
                        cache_level=level,
                        latency_ms=latency,
                        metadata={"source_level": level.value}
                    )
                else:
                    self.level_stats[level]["misses"] += 1
                    
            except Exception as e:
                logger.error(f"Error accessing cache level {level.value}: {e}")
                continue
        
        # Cache miss across all levels
        self.stats.cache_misses += 1
        latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return CacheResult(
            success=True,
            value=None,
            cache_hit=False,
            latency_ms=latency,
            metadata={"searched_levels": [l.value for l in levels]}
        )
    
    async def set(self, cache_key: CacheKey, value: Any, 
                 ttl_seconds: Optional[int] = None,
                 levels: Optional[List[CacheLevel]] = None,
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE) -> CacheResult:
        """
        Set value in cache across specified levels
        
        Args:
            cache_key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            levels: Cache levels to store in
            strategy: Cache strategy to use
            
        Returns:
            CacheResult indicating success
        """
        start_time = datetime.now(timezone.utc)
        
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        if ttl_seconds is None:
            ttl_seconds = self.config.default_ttl_seconds
        
        key_str = cache_key.to_string()
        success_count = 0
        
        for level in levels:
            try:
                result = await self._set_to_level(key_str, value, ttl_seconds, level, strategy)
                if result.success:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error setting cache level {level.value}: {e}")
                continue
        
        latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        # Update cache patterns for optimization
        await self._update_cache_patterns(cache_key, strategy)
        
        return CacheResult(
            success=success_count > 0,
            cache_hit=False,
            latency_ms=latency,
            metadata={"levels_set": success_count, "total_levels": len(levels)}
        )
    
    async def invalidate(self, cache_key: CacheKey, 
                        levels: Optional[List[CacheLevel]] = None) -> CacheResult:
        """
        Invalidate cache entries across specified levels
        
        Args:
            cache_key: Cache key to invalidate
            levels: Cache levels to invalidate from
            
        Returns:
            CacheResult indicating success
        """
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_DISK]
        
        key_str = cache_key.to_string()
        success_count = 0
        
        for level in levels:
            try:
                result = await self._delete_from_level(key_str, level)
                if result.success:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error invalidating cache level {level.value}: {e}")
                continue
        
        return CacheResult(
            success=success_count > 0,
            metadata={"levels_invalidated": success_count}
        )
    
    async def invalidate_pattern(self, pattern: str, 
                               levels: Optional[List[CacheLevel]] = None) -> int:
        """
        Invalidate cache entries matching a pattern
        
        Args:
            pattern: Pattern to match cache keys
            levels: Cache levels to invalidate from
            
        Returns:
            Number of entries invalidated
        """
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_DISK]
        
        total_invalidated = 0
        
        for level in levels:
            try:
                count = await self._invalidate_pattern_level(pattern, level)
                total_invalidated += count
            except Exception as e:
                logger.error(f"Error invalidating pattern on level {level.value}: {e}")
                continue
        
        return total_invalidated
    
    async def preload(self, preload_data: List[Tuple[CacheKey, Any]], 
                     levels: Optional[List[CacheLevel]] = None) -> int:
        """
        Preload cache with commonly used data
        
        Args:
            preload_data: List of (key, value) tuples to preload
            levels: Cache levels to preload to
            
        Returns:
            Number of entries successfully preloaded
        """
        if levels is None:
            levels = [CacheLevel.L1_MEMORY]
        
        success_count = 0
        
        for cache_key, value in preload_data:
            try:
                result = await self.set(cache_key, value, levels=levels)
                if result.success:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error preloading cache entry: {e}")
                continue
        
        logger.info(f"Preloaded {success_count}/{len(preload_data)} cache entries")
        return success_count
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """
        Optimize cache performance based on usage patterns
        
        Returns:
            Optimization report
        """
        optimization_report = {
            "optimizations_applied": [],
            "performance_improvement": {},
            "recommendations": []
        }
        
        # Analyze cache patterns
        patterns = await self._analyze_cache_patterns()
        
        # Optimize memory allocation
        if await self._optimize_memory_allocation():
            optimization_report["optimizations_applied"].append("memory_allocation")
        
        # Optimize TTL settings
        if await self._optimize_ttl_settings(patterns):
            optimization_report["optimizations_applied"].append("ttl_optimization")
        
        # Optimize cache levels
        if await self._optimize_cache_levels(patterns):
            optimization_report["optimizations_applied"].append("level_optimization")
        
        # Generate recommendations
        optimization_report["recommendations"] = await self._generate_optimization_recommendations(patterns)
        
        return optimization_report
    
    async def get_cache_stats(self) -> CacheStats:
        """
        Get comprehensive cache statistics
        
        Returns:
            CacheStats object with current statistics
        """
        # Update statistics
        self.stats.total_requests = self.stats.cache_hits + self.stats.cache_misses
        self.stats.hit_rate = (self.stats.cache_hits / self.stats.total_requests 
                              if self.stats.total_requests > 0 else 0.0)
        
        # Calculate average latency
        total_latency = sum(
            level_stat["latency_sum"] for level_stat in self.level_stats.values()
        )
        total_hits = sum(
            level_stat["hits"] for level_stat in self.level_stats.values()
        )
        self.stats.avg_latency_ms = total_latency / total_hits if total_hits > 0 else 0.0
        
        # Calculate memory usage
        self.stats.memory_usage_mb = await self._calculate_memory_usage()
        
        # Update level statistics
        self.stats.level_stats = {
            level: {
                "hits": stats["hits"],
                "misses": stats["misses"],
                "hit_rate": stats["hits"] / (stats["hits"] + stats["misses"]) 
                           if (stats["hits"] + stats["misses"]) > 0 else 0.0,
                "avg_latency": stats["latency_sum"] / stats["hits"] if stats["hits"] > 0 else 0.0
            }
            for level, stats in self.level_stats.items()
        }
        
        return self.stats
    
    # Private methods for cache level operations
    
    async def _get_from_level(self, key: str, level: CacheLevel) -> CacheResult:
        """Get value from specific cache level"""
        if level == CacheLevel.L1_MEMORY:
            return await self._get_from_memory(key)
        elif level == CacheLevel.L2_REDIS:
            return await self._get_from_redis(key)
        elif level == CacheLevel.L3_DISK:
            return await self._get_from_disk(key)
        else:
            return CacheResult(success=False)
    
    async def _set_to_level(self, key: str, value: Any, ttl_seconds: int, 
                          level: CacheLevel, strategy: CacheStrategy) -> CacheResult:
        """Set value to specific cache level"""
        if level == CacheLevel.L1_MEMORY:
            return await self._set_to_memory(key, value, ttl_seconds, strategy)
        elif level == CacheLevel.L2_REDIS:
            return await self._set_to_redis(key, value, ttl_seconds)
        elif level == CacheLevel.L3_DISK:
            return await self._set_to_disk(key, value, ttl_seconds)
        else:
            return CacheResult(success=False)
    
    async def _delete_from_level(self, key: str, level: CacheLevel) -> CacheResult:
        """Delete value from specific cache level"""
        if level == CacheLevel.L1_MEMORY:
            return await self._delete_from_memory(key)
        elif level == CacheLevel.L2_REDIS:
            return await self._delete_from_redis(key)
        elif level == CacheLevel.L3_DISK:
            return await self._delete_from_disk(key)
        else:
            return CacheResult(success=False)
    
    # Memory cache operations
    
    async def _get_from_memory(self, key: str) -> CacheResult:
        """Get from L1 memory cache"""
        if key in self.l1_memory_cache:
            entry = self.l1_memory_cache[key]
            if not entry.is_expired():
                entry.update_access()
                return CacheResult(success=True, value=entry.value)
            else:
                # Remove expired entry
                del self.l1_memory_cache[key]
        
        return CacheResult(success=True, value=None)
    
    async def _set_to_memory(self, key: str, value: Any, ttl_seconds: int, 
                           strategy: CacheStrategy) -> CacheResult:
        """Set to L1 memory cache"""
        # Check if we need to evict entries
        if len(self.l1_memory_cache) >= self.config.max_entries_per_level[CacheLevel.L1_MEMORY]:
            await self._evict_memory_entries(strategy, 1)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
            ttl_seconds=ttl_seconds
        )
        
        self.l1_memory_cache[key] = entry
        return CacheResult(success=True)
    
    async def _delete_from_memory(self, key: str) -> CacheResult:
        """Delete from L1 memory cache"""
        if key in self.l1_memory_cache:
            del self.l1_memory_cache[key]
            return CacheResult(success=True)
        return CacheResult(success=False)
    
    # Redis cache operations
    
    async def _get_from_redis(self, key: str) -> CacheResult:
        """Get from L2 Redis cache"""
        if self.l2_redis_cache is None:
            return CacheResult(success=True, value=None)
        
        try:
            data = self.l2_redis_cache.get(key)
            if data:
                value = pickle.loads(data)
                return CacheResult(success=True, value=value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        
        return CacheResult(success=True, value=None)
    
    async def _set_to_redis(self, key: str, value: Any, ttl_seconds: int) -> CacheResult:
        """Set to L2 Redis cache"""
        if self.l2_redis_cache is None:
            return CacheResult(success=False)
        
        try:
            serialized_value = pickle.dumps(value)
            self.l2_redis_cache.setex(key, ttl_seconds, serialized_value)
            return CacheResult(success=True)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return CacheResult(success=False)
    
    async def _delete_from_redis(self, key: str) -> CacheResult:
        """Delete from L2 Redis cache"""
        if self.l2_redis_cache is None:
            return CacheResult(success=False)
        
        try:
            result = self.l2_redis_cache.delete(key)
            return CacheResult(success=result > 0)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return CacheResult(success=False)
    
    # Disk cache operations
    
    async def _get_from_disk(self, key: str) -> CacheResult:
        """Get from L3 disk cache"""
        cache_file = self.l3_disk_cache_dir / f"{self._hash_key(key)}.cache"
        
        try:
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    entry_data = pickle.load(f)
                    entry = CacheEntry(**entry_data)
                    
                    if not entry.is_expired():
                        return CacheResult(success=True, value=entry.value)
                    else:
                        # Remove expired file
                        cache_file.unlink()
        except Exception as e:
            logger.error(f"Disk cache get error: {e}")
        
        return CacheResult(success=True, value=None)
    
    async def _set_to_disk(self, key: str, value: Any, ttl_seconds: int) -> CacheResult:
        """Set to L3 disk cache"""
        cache_file = self.l3_disk_cache_dir / f"{self._hash_key(key)}.cache"
        
        try:
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                ttl_seconds=ttl_seconds
            )
            
            entry_data = {
                'key': entry.key,
                'value': entry.value,
                'created_at': entry.created_at,
                'last_accessed': entry.last_accessed,
                'access_count': entry.access_count,
                'ttl_seconds': entry.ttl_seconds,
                'metadata': entry.metadata
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(entry_data, f)
            
            return CacheResult(success=True)
        except Exception as e:
            logger.error(f"Disk cache set error: {e}")
            return CacheResult(success=False)
    
    async def _delete_from_disk(self, key: str) -> CacheResult:
        """Delete from L3 disk cache"""
        cache_file = self.l3_disk_cache_dir / f"{self._hash_key(key)}.cache"
        
        try:
            if cache_file.exists():
                cache_file.unlink()
                return CacheResult(success=True)
        except Exception as e:
            logger.error(f"Disk cache delete error: {e}")
        
        return CacheResult(success=False)
    
    # Helper methods
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for cache key"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    async def _promote_to_higher_levels(self, key -> None: str, value -> None: Any, current_level -> None: CacheLevel, 
                                      available_levels -> None: List[CacheLevel]) -> None:
        """Promote frequently accessed data to higher cache levels"""
        higher_levels = []
        
        if current_level == CacheLevel.L3_DISK and CacheLevel.L2_REDIS in available_levels:
            higher_levels.append(CacheLevel.L2_REDIS)
        if current_level in [CacheLevel.L3_DISK, CacheLevel.L2_REDIS] and CacheLevel.L1_MEMORY in available_levels:
            higher_levels.append(CacheLevel.L1_MEMORY)
        
        for level in higher_levels:
            try:
                await self._set_to_level(key, value, self.config.default_ttl_seconds, 
                                       level, CacheStrategy.LRU)
            except Exception as e:
                logger.error(f"Error promoting to level {level.value}: {e}")
    
    async def _update_access_stats(self, key -> None: str, level -> None: CacheLevel) -> None:
        """Update access statistics for cache optimization"""
        # This would update detailed access patterns for optimization
        pass
    
    async def _evict_memory_entries(self, strategy -> None: CacheStrategy, count -> None: int) -> None:
        """Evict entries from memory cache based on strategy"""
        if strategy == CacheStrategy.LRU:
            # Sort by last accessed time
            sorted_entries = sorted(self.l1_memory_cache.items(), 
                                  key=lambda x: x[1].last_accessed)
        elif strategy == CacheStrategy.LFU:
            # Sort by access count
            sorted_entries = sorted(self.l1_memory_cache.items(), 
                                  key=lambda x: x[1].access_count)
        else:
            # Default to LRU
            sorted_entries = sorted(self.l1_memory_cache.items(), 
                                  key=lambda x: x[1].last_accessed)
        
        # Remove the least valuable entries
        for i in range(min(count, len(sorted_entries))):
            key_to_remove = sorted_entries[i][0]
            del self.l1_memory_cache[key_to_remove]
            self.stats.evictions += 1
    
    async def _invalidate_pattern_level(self, pattern: str, level: CacheLevel) -> int:
        """Invalidate entries matching pattern on specific level"""
        count = 0
        
        if level == CacheLevel.L1_MEMORY:
            keys_to_remove = [key for key in self.l1_memory_cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.l1_memory_cache[key]
                count += 1
        
        elif level == CacheLevel.L2_REDIS and self.l2_redis_cache:
            try:
                keys = self.l2_redis_cache.keys(f"*{pattern}*")
                if keys:
                    self.l2_redis_cache.delete(*keys)
                    count = len(keys)
            except Exception as e:
                logger.error(f"Redis pattern invalidation error: {e}")
        
        elif level == CacheLevel.L3_DISK:
            try:
                cache_files = list(self.l3_disk_cache_dir.glob("*.cache"))
                for cache_file in cache_files:
                    if pattern in cache_file.name:
                        cache_file.unlink()
                        count += 1
            except Exception as e:
                logger.error(f"Disk pattern invalidation error: {e}")
        
        return count
    
    async def _update_cache_patterns(self, cache_key -> None: CacheKey, strategy -> None: CacheStrategy) -> None:
        """Update cache patterns for optimization"""
        pattern_key = f"{cache_key.content_type.value}:{cache_key.language_code}"
        
        if pattern_key not in self.cache_patterns:
            self.cache_patterns[pattern_key] = {
                "access_count": 0,
                "preferred_strategy": strategy,
                "optimal_ttl": self.config.default_ttl_seconds
            }
        
        self.cache_patterns[pattern_key]["access_count"] += 1
    
    async def _analyze_cache_patterns(self) -> Dict[str, Any]:
        """Analyze cache usage patterns"""
        return {
            "most_accessed_types": sorted(
                self.cache_patterns.items(), 
                key=lambda x: x[1]["access_count"], 
                reverse=True
            )[:10],
            "hit_rates_by_level": {
                level.value: stats["hit_rate"] 
                for level, stats in self.stats.level_stats.items()
            }
        }
    
    async def _optimize_memory_allocation(self) -> bool:
        """Optimize memory allocation based on usage"""
        # This would implement dynamic memory allocation optimization
        return False  # Placeholder
    
    async def _optimize_ttl_settings(self, patterns: Dict[str, Any]) -> bool:
        """Optimize TTL settings based on patterns"""
        # This would adjust TTL based on access patterns
        return False  # Placeholder
    
    async def _optimize_cache_levels(self, patterns: Dict[str, Any]) -> bool:
        """Optimize cache level usage"""
        # This would optimize which levels to use for different content types
        return False  # Placeholder
    
    async def _generate_optimization_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if self.stats.hit_rate < 0.7:
            recommendations.append("Consider increasing cache size or TTL")
        
        if self.stats.avg_latency_ms > 100:
            recommendations.append("Consider optimizing cache access patterns")
        
        return recommendations
    
    async def _calculate_memory_usage(self) -> float:
        """Calculate approximate memory usage in MB"""
        import sys
        
        total_size = 0
        for entry in self.l1_memory_cache.values():
            total_size += sys.getsizeof(entry.value)
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def get_cache_capabilities(self) -> Dict[str, Any]:
        """Get cache engine capabilities"""
        return {
            "cache_levels": [level.value for level in CacheLevel],
            "cache_strategies": [strategy.value for strategy in CacheStrategy],
            "content_types_supported": [ct.value for ct in CacheContentType],
            "redis_available": REDIS_AVAILABLE,
            "disk_cache_enabled": True,
            "max_memory_mb": self.config.max_memory_mb,
            "default_ttl_seconds": self.config.default_ttl_seconds,
            "compression_enabled": self.config.compression_enabled,
            "encryption_enabled": self.config.encryption_enabled,
            "current_entries": {
                "memory": len(self.l1_memory_cache),
                "disk": len(list(self.l3_disk_cache_dir.glob("*.cache")))
            }
        }