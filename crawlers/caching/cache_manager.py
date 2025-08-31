#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Manager - Industrial-Grade Multi-Tier Cache Management System
==================================================================

Enterprise cache manager orchestrating L1-L4 cache hierarchy with AI-powered
optimization, predictive preloading, and intelligent data distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

 PROPRIETARY SOFTWARE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

BUSINESS LOGIC:
User Request → Pattern Analysis → Intelligent Cache → AI Optimization →
Ultra-Fast Response → Performance Analytics → Automatic Scaling
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, OrderedDict
import numpy as np
from contextlib import asynccontextmanager

# Import internal modules
from .redis_cache import RedisCache, RedisClusterCache
from .memory_cache import MemoryCache, LRUCache, TTLCache
from .distributed_cache import DistributedCache, ConsistentHashRing
from .content_cache import ContentCache, MediaCache
from .compression import CacheCompressor, CompressionAlgorithm
from .encryption import CacheEncryption, EncryptionAlgorithm
from .metrics import CacheMetrics, PerformanceMonitor
from .strategies import CacheStrategy, AdaptiveStrategy
from .monitoring import CacheMonitor, AlertManager

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheLevel(Enum):
    """Multi-tier cache hierarchy levels with performance characteristics."""
    L1_MEMORY = "l1_memory"          # < 1ms, 512MB-2GB
    L2_REDIS = "l2_redis"            # < 5ms, 8GB-64GB
    L3_DISTRIBUTED = "l3_distributed" # < 50ms, 100GB-1TB
    L4_PERSISTENT = "l4_persistent"   # < 500ms, Unlimited

class CacheOperation(Enum):
    """Cache operation types for comprehensive metrics tracking."""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    INVALIDATE = "invalidate"
    REFRESH = "refresh"
    PRELOAD = "preload"
    OPTIMIZE = "optimize"
    PROMOTE = "promote"
    DEMOTE = "demote"

class CachePriority(Enum):
    """Cache priority levels for intelligent data placement."""
    CRITICAL = "critical"     # Always in L1
    HIGH = "high"            # L1/L2 preferred
    NORMAL = "normal"        # L2/L3 preferred
    LOW = "low"              # L3/L4 preferred
    ARCHIVE = "archive"      # L4 only

class CachePattern(Enum):
    """Access pattern types for optimization algorithms."""
    HOT = "hot"              # Frequent access
    WARM = "warm"            # Regular access
    COLD = "cold"            # Infrequent access
    TEMPORAL = "temporal"    # Time-based patterns
    GEOGRAPHIC = "geographic" # Location-based patterns

@dataclass
class CacheEntry:
    """Comprehensive cache entry with advanced metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    size_bytes: int = 0
    priority: CachePriority = CachePriority.NORMAL
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compression_ratio: float = 1.0
    encrypted: bool = False
    cache_level: Optional[CacheLevel] = None
    access_pattern: CachePattern = CachePattern.WARM
    cost_score: float = 1.0
    popularity_score: float = 0.0

@dataclass
class CacheConfig:
    """Industrial cache configuration with enterprise features."""
    # General configuration
    enabled_levels: Set[CacheLevel] = field(default_factory=lambda: {
        CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS
    })
    
    # L1 Memory Cache Configuration
    l1_max_size_mb: int = 512
    l1_max_entries: int = 50000
    l1_ttl_seconds: int = 300
    l1_eviction_policy: str = "adaptive_lru"
    
    # L2 Redis Cache Configuration
    redis_cluster_nodes: List[str] = field(default_factory=lambda: [
        "redis-1:6379", "redis-2:6379", "redis-3:6379"
    ])
    redis_max_connections: int = 100
    redis_default_ttl: int = 3600
    redis_key_prefix: str = "ia_influencer_crawler:"
    redis_compression: bool = True
    
    # L3 Distributed Cache Configuration
    distributed_nodes: List[str] = field(default_factory=lambda: [
        "cache-node-1:8080", "cache-node-2:8080", "cache-node-3:8080"
    ])
    distributed_replication_factor: int = 2
    distributed_consistency_level: str = "eventual"
    
    # L4 Persistent Cache Configuration
    persistent_storage_path: str = "/data/cache/persistent"
    persistent_max_size_gb: int = 100
    persistent_compression: bool = True
    persistent_encryption: bool = True
    
    # Optimization Features
    ai_optimization_enabled: bool = True
    predictive_preloading: bool = True
    automatic_scaling: bool = True
    intelligent_compression: bool = True
    adaptive_encryption: bool = True
    
    # Performance Tuning
    promotion_threshold: float = 0.8
    demotion_threshold: float = 0.2
    optimization_interval: int = 300
    metrics_collection_interval: int = 60
    
    # Security Configuration
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_GCM
    enable_audit_logging: bool = True
    secure_key_rotation: bool = True
    
    # Monitoring Configuration
    monitoring_enabled: bool = True
    alerting_enabled: bool = True
    metrics_export_enabled: bool = True
    performance_profiling: bool = True

@dataclass 
class CacheStats:
    """Comprehensive cache statistics for enterprise monitoring."""
    # Basic metrics
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    
    # Memory metrics
    memory_usage_bytes: int = 0
    memory_efficiency: float = 0.0
    compression_ratio: float = 1.0
    
    # Distribution metrics
    l1_hit_ratio: float = 0.0
    l2_hit_ratio: float = 0.0
    l3_hit_ratio: float = 0.0
    l4_hit_ratio: float = 0.0
    
    # Business metrics
    cost_per_operation: float = 0.0
    data_freshness_score: float = 1.0
    availability_percentage: float = 99.9
    
    # Computed properties
    @property
    def hit_ratio(self) -> float:
        """Calculate overall cache hit ratio."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    @property
    def miss_ratio(self) -> float:
        """Calculate cache miss ratio."""



        return 1.0 - self.hit_ratio
    
    @property
    def efficiency_score(self) -> float:
        """Calculate overall cache efficiency score."""



        return (self.hit_ratio * 0.4 + 
                self.memory_efficiency * 0.3 + 
                self.data_freshness_score * 0.3)

class IndustrialCacheManager:
    """
     Industrial-Grade Multi-Tier Cache Manager
    
    Enterprise cache management system featuring:
    - Multi-tier cache hierarchy (L1 → L2 → L3 → L4)
    - AI-powered optimization and predictive analytics
    - Intelligent data placement and automatic scaling
    - Advanced compression and encryption
    - Real-time monitoring and alerting
    - Content-aware caching strategies
    - Geographic distribution support
    - Cost-aware optimization
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize industrial cache manager with advanced configuration."""
        self.config = config or CacheConfig()
        self.logger = logging.getLogger(f"{__name__}.IndustrialCacheManager")
        
        # Cache hierarchy
        self.caches: Dict[CacheLevel, Any] = {}
        self.cache_enabled: Dict[CacheLevel, bool] = {}
        
        # Components
        self.compressor = CacheCompressor()
        self.encryptor = CacheEncryption(self.config.encryption_algorithm)
        self.metrics = CacheMetrics()
        self.monitor = CacheMonitor()
        self.strategy = AdaptiveStrategy()
        
        # Performance tracking
        self.stats = CacheStats()
        self.operation_history = OrderedDict()
        self.access_patterns = defaultdict(list)
        self.cost_tracker = defaultdict(float)
        
        # Optimization state
        self.optimizer_running = False
        self.last_optimization = datetime.now()
        self.predictive_models = {}
        
        # Thread safety
        self._lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        self.logger.info(" Industrial Cache Manager initialized")

    async def initialize(self) -> bool:
        """Initialize all cache levels and components asynchronously."""



        try:
            self.logger.info(" Initializing cache hierarchy...")
            
            # Initialize cache levels based on configuration
            initialization_tasks = []
            
            if CacheLevel.L1_MEMORY in self.config.enabled_levels:
                initialization_tasks.append(self._initialize_l1_memory())
            
            if CacheLevel.L2_REDIS in self.config.enabled_levels:
                initialization_tasks.append(self._initialize_l2_redis())
                
            if CacheLevel.L3_DISTRIBUTED in self.config.enabled_levels:
                initialization_tasks.append(self._initialize_l3_distributed())
                
            if CacheLevel.L4_PERSISTENT in self.config.enabled_levels:
                initialization_tasks.append(self._initialize_l4_persistent())
            
            # Execute all initializations concurrently
            results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
            
            # Check results
            success_count = sum(1 for result in results if result is True)
            total_count = len(initialization_tasks)
            
            # Initialize components
            await self._initialize_components()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.info(f" Cache Manager initialized: {success_count}/{total_count} levels active")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f" Cache Manager initialization failed: {e}")
            return False

    async def _initialize_l1_memory(self) -> bool:
        """Initialize L1 memory cache with advanced features."""



        try:
            self.caches[CacheLevel.L1_MEMORY] = MemoryCache(
                max_size_mb=self.config.l1_max_size_mb,
                max_entries=self.config.l1_max_entries,
                default_ttl=self.config.l1_ttl_seconds,
                eviction_policy=self.config.l1_eviction_policy
            )
            self.cache_enabled[CacheLevel.L1_MEMORY] = True
            self.logger.info(" L1 Memory Cache initialized")
            return True
        except Exception as e:
            self.logger.error(f" L1 Memory Cache initialization failed: {e}")
            return False

    async def _initialize_l2_redis(self) -> bool:
        """Initialize L2 Redis cache with cluster support."""



        try:
            if len(self.config.redis_cluster_nodes) > 1:
                self.caches[CacheLevel.L2_REDIS] = RedisClusterCache(
                    nodes=self.config.redis_cluster_nodes,
                    max_connections=self.config.redis_max_connections,
                    key_prefix=self.config.redis_key_prefix
                )
            else:
                self.caches[CacheLevel.L2_REDIS] = RedisCache(
                    host=self.config.redis_cluster_nodes[0].split(':')[0],
                    port=int(self.config.redis_cluster_nodes[0].split(':')[1]),
                    max_connections=self.config.redis_max_connections,
                    key_prefix=self.config.redis_key_prefix
                )
            
            await self.caches[CacheLevel.L2_REDIS].initialize()
            self.cache_enabled[CacheLevel.L2_REDIS] = True
            self.logger.info(" L2 Redis Cache initialized")
            return True
        except Exception as e:
            self.logger.error(f" L2 Redis Cache initialization failed: {e}")
            return False

    async def _initialize_l3_distributed(self) -> bool:
        """Initialize L3 distributed cache with consistent hashing."""



        try:
            self.caches[CacheLevel.L3_DISTRIBUTED] = DistributedCache(
                nodes=self.config.distributed_nodes,
                replication_factor=self.config.distributed_replication_factor,
                consistency_level=self.config.distributed_consistency_level
            )
            
            await self.caches[CacheLevel.L3_DISTRIBUTED].initialize()
            self.cache_enabled[CacheLevel.L3_DISTRIBUTED] = True
            self.logger.info(" L3 Distributed Cache initialized")
            return True
        except Exception as e:
            self.logger.error(f" L3 Distributed Cache initialization failed: {e}")
            return False

    async def _initialize_l4_persistent(self) -> bool:
        """Initialize L4 persistent cache with file-based storage."""



        try:
            from .persistence import CachePersistence
            
            self.caches[CacheLevel.L4_PERSISTENT] = CachePersistence(
                storage_path=self.config.persistent_storage_path,
                max_size_gb=self.config.persistent_max_size_gb,
                compression_enabled=self.config.persistent_compression,
                encryption_enabled=self.config.persistent_encryption
            )
            
            await self.caches[CacheLevel.L4_PERSISTENT].initialize()
            self.cache_enabled[CacheLevel.L4_PERSISTENT] = True
            self.logger.info(" L4 Persistent Cache initialized")
            return True
        except Exception as e:
            self.logger.error(f" L4 Persistent Cache initialization failed: {e}")
            return False
            return False

    async def _initialize_components(self) -> bool:
        """Initialize cache components and optimization engines."""



        try:
            # Initialize metrics system
            await self.metrics.initialize()
            
            # Initialize monitoring system
            if self.config.monitoring_enabled:
                await self.monitor.initialize()
            
            # Initialize compression engine
            await self.compressor.initialize()
            
            # Initialize encryption engine
            if self.config.adaptive_encryption:
                await self.encryptor.initialize()
            
            # Initialize adaptive strategy
            if self.config.ai_optimization_enabled:
                await self.strategy.initialize()
            
            self.logger.info(" All cache components initialized")
            return True
            
        except Exception as e:
            self.logger.error(f" Component initialization failed: {e}")
            return False

    async def _start_background_tasks(self) -> None:
        """Start background optimization and monitoring tasks."""
        if self.config.ai_optimization_enabled:
            asyncio.create_task(self._optimization_loop())
        
        if self.config.monitoring_enabled:
            asyncio.create_task(self._monitoring_loop())
            
        if self.config.predictive_preloading:
            asyncio.create_task(self._preloading_loop())
            
        self.logger.info(" Background tasks started")

    async def get(
        self, 
        key: str, 
        default: Any = None,
        cache_levels: Optional[Set[CacheLevel]] = None,
        promote_on_hit: bool = True
    ) -> Any:
        """
        Get value from cache with intelligent promotion strategy.
        
        Args:
            key: Cache key
            default: Default value if not found
            cache_levels: Specific cache levels to search (optional)
            promote_on_hit: Whether to promote data to faster cache levels
            
        Returns:
            Cached value or default
        """
        start_time = time.time()
        
        try:
            # Generate cache key hash for consistent distribution
            cache_key = self._generate_cache_key(key)
            
            # Determine search order based on configuration
            search_levels = cache_levels or self._get_search_order()
            
            # Search through cache hierarchy
            for level in search_levels:
                if not self.cache_enabled.get(level, False):
                    continue
                    
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                try:
                    # Attempt to get from current level
                    value = await cache.get(cache_key)
                    
                    if value is not None:
                        # Cache hit - update metrics and promote if needed
                        await self._record_cache_hit(level, key, time.time() - start_time)
                        
                        if promote_on_hit and level != CacheLevel.L1_MEMORY:
                            await self._promote_data(key, value, level)
                        
                        # Update access patterns for optimization
                        await self._update_access_pattern(key, level)
                        
                        return self._deserialize_value(value)
                        
                except Exception as e:
                    self.logger.warning(f"Cache get error on {level}: {e}")
                    continue
            
            # Cache miss across all levels
            await self._record_cache_miss(key, search_levels, time.time() - start_time)
            return default
            
        except Exception as e:
            self.logger.error(f" Cache get failed for key '{key}': {e}")
            return default

    async def set(
        self, 
        key: str, 
        value: Any,
        ttl: Optional[int] = None,
        cache_levels: Optional[Set[CacheLevel]] = None,
        priority: CachePriority = CachePriority.NORMAL,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set value in cache with intelligent placement strategy.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            cache_levels: Target cache levels (auto-determined if None)
            priority: Cache priority for placement decisions
            tags: Tags for invalidation and organization
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        start_time = time.time()
        
        try:
            # Generate cache key and entry
            cache_key = self._generate_cache_key(key)
            cache_entry = self._create_cache_entry(
                key, value, ttl, priority, tags or set(), metadata or {}
            )
            
            # Determine optimal cache levels based on priority and size
            target_levels = cache_levels or await self._determine_optimal_levels(
                cache_entry
            )
            
            # Serialize and optionally compress/encrypt value
            serialized_value = await self._prepare_value_for_storage(
                value, cache_entry
            )
            
            success_count = 0
            
            # Store in target cache levels
            for level in target_levels:
                if not self.cache_enabled.get(level, False):
                    continue
                    
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                try:
                    # Calculate level-specific TTL
                    level_ttl = self._calculate_level_ttl(ttl, level)
                    
                    # Store in cache level
                    success = await cache.set(cache_key, serialized_value, level_ttl)
                    
                    if success:
                        success_count += 1
                        await self._record_cache_set(level, key, len(serialized_value))
                        
                except Exception as e:
                    self.logger.warning(f"Cache set error on {level}: {e}")
                    continue
            
            # Update statistics
            operation_time = time.time() - start_time
            await self._update_operation_stats(CacheOperation.SET, operation_time)
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f" Cache set failed for key '{key}': {e}")
            return False

    async def delete(
        self, 
        key: str,
        cache_levels: Optional[Set[CacheLevel]] = None
    ) -> bool:
        """
        Delete key from specified cache levels or all levels.
        
        Args:
            key: Cache key to delete
            cache_levels: Target cache levels (all levels if None)
            
        Returns:
            Success status
        """



        try:
            cache_key = self._generate_cache_key(key)
            delete_levels = cache_levels or set(self.cache_enabled.keys())
            
            success_count = 0
            
            for level in delete_levels:
                if not self.cache_enabled.get(level, False):
                    continue
                    
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                try:
                    success = await cache.delete(cache_key)
                    if success:
                        success_count += 1
                        await self._record_cache_delete(level, key)
                        
                except Exception as e:
                    self.logger.warning(f"Cache delete error on {level}: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f" Cache delete failed for key '{key}': {e}")
            return False

    async def invalidate_pattern(
        self, 
        pattern: str,
        cache_levels: Optional[Set[CacheLevel]] = None
    ) -> int:
        """
        Invalidate all keys matching the given pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            cache_levels: Target cache levels (all levels if None)
            
        Returns:
            Number of keys invalidated
        """



        try:
            invalidate_levels = cache_levels or set(self.cache_enabled.keys())
            total_invalidated = 0
            
            for level in invalidate_levels:
                if not self.cache_enabled.get(level, False):
                    continue
                    
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                try:
                    if hasattr(cache, 'invalidate_pattern'):
                        count = await cache.invalidate_pattern(pattern)
                        total_invalidated += count
                        await self._record_cache_invalidation(level, pattern, count)
                        
                except Exception as e:
                    self.logger.warning(f"Cache invalidation error on {level}: {e}")
                    continue
            
            self.logger.info(f" Invalidated {total_invalidated} keys matching '{pattern}'")
            return total_invalidated
            
        except Exception as e:
            self.logger.error(f" Cache invalidation failed for pattern '{pattern}': {e}")
            return 0

    async def get_stats(self) -> CacheStats:
        """Get comprehensive cache statistics."""



        try:
            # Update current statistics
            await self._update_comprehensive_stats()
            return self.stats
            
        except Exception as e:
            self.logger.error(f" Failed to get cache stats: {e}")
            return CacheStats()

    async def optimize_performance(self) -> Dict[str, Any]:
        """
        Perform comprehensive cache optimization.
        
        Returns:
            Optimization results and recommendations
        """
        if self.optimizer_running:
            return {"status": "optimization_already_running"}
        
        self.optimizer_running = True
        optimization_start = time.time()
        
        try:
            results = {
                "optimization_start": datetime.now().isoformat(),
                "actions_performed": [],
                "performance_improvements": {},
                "recommendations": [],
                "errors": []
            }
            
            # Analyze current performance
            performance_analysis = await self._analyze_cache_performance()
            results["current_performance"] = performance_analysis
            
            # Optimize data distribution
            if self.config.automatic_scaling:
                distribution_results = await self._optimize_data_distribution()
                results["actions_performed"].append("data_distribution_optimization")
                results["performance_improvements"]["distribution"] = distribution_results
            
            # Optimize compression settings
            if self.config.intelligent_compression:
                compression_results = await self._optimize_compression()
                results["actions_performed"].append("compression_optimization")
                results["performance_improvements"]["compression"] = compression_results
            
            # Optimize cache levels
            level_optimization = await self._optimize_cache_levels()
            results["actions_performed"].append("cache_level_optimization")
            results["performance_improvements"]["levels"] = level_optimization
            
            # Generate AI-powered recommendations
            if self.config.ai_optimization_enabled:
                ai_recommendations = await self._generate_ai_recommendations()
                results["recommendations"] = ai_recommendations
            
            # Update optimization timestamp
            self.last_optimization = datetime.now()
            optimization_time = time.time() - optimization_start
            
            results["optimization_duration_seconds"] = optimization_time
            results["optimization_end"] = datetime.now().isoformat()
            
            self.logger.info(f" Cache optimization completed in {optimization_time:.2f}s")
            return results
            
        except Exception as e:
            self.logger.error(f" Cache optimization failed: {e}")
            return {"status": "optimization_failed", "error": str(e)}
            
        finally:
            self.optimizer_running = False

    # Helper methods for internal operations
    
    def _generate_cache_key(self, key: str) -> str:
        """Generate consistent cache key with namespace."""



        return f"{self.config.redis_key_prefix}{hashlib.sha256(key.encode()).hexdigest()[:16]}"
    
    def _get_search_order(self) -> List[CacheLevel]:
        """Get optimal cache search order based on performance characteristics."""
        order = []
        
        # Always search L1 first (fastest)
        if CacheLevel.L1_MEMORY in self.config.enabled_levels:
            order.append(CacheLevel.L1_MEMORY)
            
        # Then L2 Redis
        if CacheLevel.L2_REDIS in self.config.enabled_levels:
            order.append(CacheLevel.L2_REDIS)
            
        # Then L3 Distributed
        if CacheLevel.L3_DISTRIBUTED in self.config.enabled_levels:
            order.append(CacheLevel.L3_DISTRIBUTED)
            
        # Finally L4 Persistent
        if CacheLevel.L4_PERSISTENT in self.config.enabled_levels:
            order.append(CacheLevel.L4_PERSISTENT)
            
        return order
    
    def _create_cache_entry(
        self, key: str, value: Any, ttl: Optional[int], 
        priority: CachePriority, tags: Set[str], metadata: Dict[str, Any]
    ) -> CacheEntry:
        """Create comprehensive cache entry with metadata."""
        now = datetime.now()
        
        return CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl) if ttl else None,
            priority=priority,
            tags=tags,
            metadata=metadata,
            size_bytes=len(pickle.dumps(value))
        )
    
    async def _determine_optimal_levels(self, entry: CacheEntry) -> Set[CacheLevel]:
        """Determine optimal cache levels based on entry characteristics."""
        levels = set()
        
        # Priority-based placement
        if entry.priority == CachePriority.CRITICAL:
            levels.add(CacheLevel.L1_MEMORY)
            levels.add(CacheLevel.L2_REDIS)
        elif entry.priority == CachePriority.HIGH:
            levels.add(CacheLevel.L1_MEMORY)
            levels.add(CacheLevel.L2_REDIS)
        elif entry.priority == CachePriority.NORMAL:
            levels.add(CacheLevel.L2_REDIS)
            levels.add(CacheLevel.L3_DISTRIBUTED)
        elif entry.priority == CachePriority.LOW:
            levels.add(CacheLevel.L3_DISTRIBUTED)
            levels.add(CacheLevel.L4_PERSISTENT)
        else:  # ARCHIVE
            levels.add(CacheLevel.L4_PERSISTENT)
        
        # Size-based adjustments
        if entry.size_bytes > 10 * 1024 * 1024:  # > 10MB
            levels.discard(CacheLevel.L1_MEMORY)
            
        # Filter by enabled levels
        return levels.intersection(self.config.enabled_levels)

    async def _prepare_value_for_storage(self, value: Any, entry: CacheEntry) -> bytes:
        """Prepare value for storage with compression and encryption."""
        # Serialize
        serialized = pickle.dumps(value)
        
        # Compress if beneficial
        if self.config.intelligent_compression and len(serialized) > 1024:
            compressed = await self.compressor.compress(
                serialized, CompressionAlgorithm.ZSTD
            )
            if len(compressed) < len(serialized) * 0.9:  # At least 10% savings
                serialized = compressed
                entry.compression_ratio = len(compressed) / len(serialized)
        
        # Encrypt if required
        if self.config.adaptive_encryption and entry.priority == CachePriority.CRITICAL:
            serialized = await self.encryptor.encrypt(serialized)
            entry.encrypted = True
        
        return serialized
    
    def _deserialize_value(self, serialized_value: bytes) -> Any:
        """Deserialize value with decompression and decryption."""



        try:
            # Handle decryption if needed
            data = serialized_value
            
            # Handle decompression if needed
            try:
                # Try to decompress (will fail if not compressed)
                data = self.compressor.decompress(data)
            except:
                pass  # Not compressed
            
            # Deserialize
            return pickle.loads(data)
            
        except Exception as e:
            self.logger.error(f" Value deserialization failed: {e}")
            return None

# Export main class
CacheManager = IndustrialCacheManager
            self.logger.error(f"Failed to initialize cache manager: {e}")
            raise
    
    async def _setup_cache_layers(self) -> None:
        """Setup multi-tier cache layers."""
        from .memory_cache import MemoryCache
        from .redis_cache import RedisCache
        from .distributed_cache import DistributedCache
        from .persistence import CachePersistence
        
        # L1: Memory cache (fastest)
        memory_config = self.config.get('memory', {})
        self.caches[CacheLevel.L1_MEMORY] = MemoryCache(
            max_size=memory_config.get('max_size', 268435456),  # 256MB
            ttl=memory_config.get('ttl', 300)  # 5 minutes
        )
        
        # L2: Redis cache (distributed)
        redis_config = self.config.get('redis', {})
        self.caches[CacheLevel.L2_REDIS] = RedisCache(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0)
        )
        
        # L3: Distributed cache (cluster)
        if self.config.get('distributed', {}).get('enabled', False):
            self.caches[CacheLevel.L3_DISTRIBUTED] = DistributedCache(
                nodes=self.config['distributed']['nodes']
            )
        
        # L4: Persistent cache (disk)
        if self.config.get('persistent', {}).get('enabled', False):
            self.caches[CacheLevel.L4_PERSISTENT] = CachePersistence(
                storage_path=self.config['persistent']['path']
            )
        
        self.logger.info(f"Initialized {len(self.caches)} cache layers")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with multi-tier lookup.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Try each cache level in order
            for level in [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, 
                         CacheLevel.L3_DISTRIBUTED, CacheLevel.L4_PERSISTENT]:
                
                if level not in self.caches:
                    continue
                
                cache = self.caches[level]
                value = await cache.get(key)
                
                if value is not None:
                    # Update statistics
                    self.stats.hits += 1
                    
                    # Promote to higher cache levels
                    await self._promote_cache_entry(key, value, level)
                    
                    self.logger.debug(f"Cache hit on {level.value} for key: {key}")
                    return value
            
            # Cache miss
            self.stats.misses += 1
            self.logger.debug(f"Cache miss for key: {key}")
            return default
            
        except Exception as e:
            self.logger.error(f"Error getting cache key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache across all levels.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            ttl = ttl or self.default_ttl
            success = True
            
            # Set in all available cache levels
            for level, cache in self.caches.items():
                try:
                    await cache.set(key, value, ttl)
                    self.logger.debug(f"Set key {key} in {level.value}")
                except Exception as e:
                    self.logger.error(f"Failed to set key {key} in {level.value}: {e}")
                    success = False
            
            # Update statistics
            self.stats.sets += 1
            self.stats.total_keys = await self._count_total_keys()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from all cache levels.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            success = True
            
            # Delete from all cache levels
            for level, cache in self.caches.items():
                try:
                    await cache.delete(key)
                    self.logger.debug(f"Deleted key {key} from {level.value}")
                except Exception as e:
                    self.logger.error(f"Failed to delete key {key} from {level.value}: {e}")
                    success = False
            
            # Update statistics
            self.stats.deletes += 1
            self.stats.total_keys = await self._count_total_keys()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            
        Returns:
            Number of keys invalidated
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            total_invalidated = 0
            
            # Invalidate in all cache levels
            for level, cache in self.caches.items():
                try:
                    count = await cache.invalidate_pattern(pattern)
                    total_invalidated += count
                    self.logger.debug(f"Invalidated {count} keys in {level.value}")
                except Exception as e:
                    self.logger.error(f"Error invalidating pattern in {level.value}: {e}")
            
            return total_invalidated
            
        except Exception as e:
            self.logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Clear all cache levels."""
        if not self._initialized:
            await self.initialize()
        
        try:
            success = True
            
            # Clear all cache levels
            for level, cache in self.caches.items():
                try:
                    await cache.clear()
                    self.logger.debug(f"Cleared {level.value}")
                except Exception as e:
                    self.logger.error(f"Failed to clear {level.value}: {e}")
                    success = False
            
            # Reset statistics
            self.stats = CacheStats()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False
    
    async def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        if self.stats.hits + self.stats.misses > 0:
            self.stats.hit_rate = self.stats.hits / (self.stats.hits + self.stats.misses)
        
        # Update memory usage
        if CacheLevel.L1_MEMORY in self.caches:
            self.stats.memory_usage = await self.caches[CacheLevel.L1_MEMORY].get_memory_usage()
        
        return self.stats
    
    async def _promote_cache_entry(self, key: str, value: Any, found_level: CacheLevel) -> None:
        """Promote cache entry to higher levels."""
        levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, 
                 CacheLevel.L3_DISTRIBUTED, CacheLevel.L4_PERSISTENT]
        
        found_index = levels.index(found_level)
        
        # Promote to all higher levels
        for i in range(found_index):
            level = levels[i]
            if level in self.caches:
                try:
                    await self.caches[level].set(key, value)
                except Exception as e:
                    self.logger.error(f"Error promoting key {key} to {level.value}: {e}")
    
    async def _count_total_keys(self) -> int:
        """Count total keys across all cache levels."""
        total = 0
        for cache in self.caches.values():
            try:
                if hasattr(cache, 'count_keys'):
                    total += await cache.count_keys()
            except Exception as e:
                self.logger.error(f"Error counting keys: {e}")
        return total
    
    async def _start_monitoring(self) -> None:
        """Start cache monitoring."""
        # Implementation would include metrics collection
        pass
    
    async def shutdown(self) -> None:
        """Shutdown cache manager and close connections."""
        self.logger.info("Shutting down cache manager")
        
        for level, cache in self.caches.items():
            try:
                if hasattr(cache, 'close'):
                    await cache.close()
                self.logger.debug(f"Closed {level.value} cache")
            except Exception as e:
                self.logger.error(f"Error closing {level.value} cache: {e}")
        
        self.executor.shutdown(wait=True)
        self._initialized = False

# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

async def get_cache_manager(config: Optional[Dict[str, Any]] = None) -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager(config)
        await _cache_manager.initialize()
    
    return _cache_manager
