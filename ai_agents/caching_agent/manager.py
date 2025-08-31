"""
Caching Manager - Central Cache Management System

Advanced caching orchestration providing intelligent cache coordination,
performance optimization, and seamless multi-layer cache management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic
from enum import Enum
import json
import uuid

from ..base import BaseAgent, AgentRequest, AgentResponse, AgentStatus
from .strategies import CacheStrategy, LRUStrategy, TTLStrategy, AdaptiveStrategy
from .storage import CacheStorage, HybridStorage
from .invalidation import InvalidationEngine
from .analytics import CacheAnalytics
from .coordinator import DistributedCacheCoordinator
from .optimizer import CacheOptimizer

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheLevel(Enum):
    """Cache storage levels in hierarchy"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"  
    L3_DATABASE = "l3_database"
    L4_CDN = "l4_cdn"

class CachePriority(Enum):
    """Cache entry priority levels"""
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    MINIMAL = 1

@dataclass
class CacheEntry:
    """Enhanced cache entry with comprehensive metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    hit_count: int = 0
    size_bytes: int = 0
    ttl: Optional[int] = None
    priority: CachePriority = CachePriority.NORMAL
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compression_enabled: bool = False
    encryption_enabled: bool = False
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    content_type: Optional[str] = None
    checksum: Optional[str] = None

@dataclass
class CacheConfig:
    """Comprehensive cache configuration"""
    max_memory_size: int = 1024 * 1024 * 1024  # 1GB
    max_entries: int = 1000000
    default_ttl: int = 3600  # 1 hour
    compression_threshold: int = 1024  # bytes
    enable_encryption: bool = False
    enable_analytics: bool = True
    enable_distributed_coordination: bool = True
    cache_levels: List[CacheLevel] = field(default_factory=lambda: [
        CacheLevel.L1_MEMORY,
        CacheLevel.L2_REDIS
    ])
    invalidation_strategies: List[str] = field(default_factory=lambda: [
        "ttl", "lru", "tag_based"
    ])
    optimization_interval: int = 300  # 5 minutes
    
@dataclass
class CacheStats:
    """Real-time cache performance statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_ratio: float = 0.0
    average_response_time: float = 0.0
    total_size_bytes: int = 0
    entry_count: int = 0
    evictions: int = 0
    invalidations: int = 0
    memory_usage_percent: float = 0.0
    network_requests_saved: int = 0
    cost_savings_estimate: float = 0.0

class CachingManager(BaseAgent):
    """
    Advanced multi-layer caching manager with intelligent optimization.
    
    Provides enterprise-grade caching capabilities including:
    - Multi-tier cache hierarchy (L1-L4)
    - Intelligent cache strategies and eviction policies
    - Distributed cache coordination across instances
    - Real-time performance analytics and optimization
    - Content-aware caching with metadata enrichment
    - Security features including encryption and tenant isolation
    """
    
    def __init__(
        self,
        config: Optional[CacheConfig] = None,
        **kwargs
    ):
        super().__init__(
            agent_id=f"caching_manager_{uuid.uuid4().hex[:8]}",
            agent_type="caching_manager", 
            version="1.0.0",
            **kwargs
        )
        
        self.config = config or CacheConfig()
        
        # Initialize cache components
        self.storage = HybridStorage(self.config)
        self.strategy = AdaptiveStrategy()
        self.invalidation_engine = InvalidationEngine()
        self.analytics = CacheAnalytics()
        self.coordinator = DistributedCacheCoordinator()
        self.optimizer = CacheOptimizer()
        
        # Cache state
        self._cache_entries: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._locks: Dict[str, asyncio.Lock] = {}
        
        # Performance tracking
        self._operation_times: List[float] = []
        self._last_optimization = datetime.utcnow()
        
    async def initialize(self) -> bool:
        """Initialize caching manager and all components"""



        try:
            await super().initialize()
            
            # Initialize storage layers
            await self.storage.initialize()
            
            # Setup invalidation engine
            await self.invalidation_engine.initialize()
            
            # Start analytics collection
            if self.config.enable_analytics:
                await self.analytics.initialize()
            
            # Setup distributed coordination
            if self.config.enable_distributed_coordination:
                await self.coordinator.initialize()
            
            # Start optimization scheduler
            asyncio.create_task(self._optimization_loop())
            
            logger.info(f"CachingManager {self.agent_id} fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CachingManager: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def get(
        self, 
        key: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Any]:
        """
        Retrieve value from multi-layer cache with intelligent optimization.
        
        Args:
            key: Cache key identifier
            user_id: User context for tenant isolation
            tenant_id: Tenant context for multi-tenancy
            tags: Associated tags for invalidation
            
        Returns:
            Cached value or None if not found
        """
        start_time = time.time()
        
        try:
            # Generate context-aware cache key
            cache_key = self._generate_cache_key(key, user_id, tenant_id)
            
            # Check cache hierarchy
            value = await self._get_from_hierarchy(cache_key)
            
            if value is not None:
                # Update access statistics
                await self._record_hit(cache_key)
                self._stats.cache_hits += 1
                
                # Promote to higher cache level if beneficial
                await self._promote_cache_entry(cache_key, value)
                
            else:
                self._stats.cache_misses += 1
                await self._record_miss(cache_key)
            
            # Update performance metrics
            execution_time = time.time() - start_time
            self._operation_times.append(execution_time)
            self._stats.total_requests += 1
            self._update_hit_ratio()
            
            return value
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        priority: CachePriority = CachePriority.NORMAL,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store value in cache with intelligent placement and optimization.
        
        Args:
            key: Cache key identifier
            value: Value to cache
            ttl: Time-to-live in seconds
            priority: Cache priority level
            user_id: User context for tenant isolation
            tenant_id: Tenant context for multi-tenancy
            tags: Tags for grouping and invalidation
            content_type: Content type for optimization
            metadata: Additional metadata
            
        Returns:
            True if successfully cached
        """
        start_time = time.time()
        
        try:
            # Generate context-aware cache key
            cache_key = self._generate_cache_key(key, user_id, tenant_id)
            
            # Create comprehensive cache entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                ttl=ttl or self.config.default_ttl,
                priority=priority,
                tags=tags or [],
                metadata=metadata or {},
                tenant_id=tenant_id,
                user_id=user_id,
                content_type=content_type,
                size_bytes=self._calculate_size(value)
            )
            
            # Generate integrity checksum
            entry.checksum = self._generate_checksum(value)
            
            # Apply compression if beneficial
            if entry.size_bytes > self.config.compression_threshold:
                entry.compression_enabled = True
                entry.value = await self._compress_value(value)
            
            # Apply encryption for sensitive data
            if self.config.enable_encryption and self._requires_encryption(content_type):
                entry.encryption_enabled = True
                entry.value = await self._encrypt_value(entry.value)
            
            # Determine optimal cache level placement
            cache_level = await self._determine_optimal_level(entry)
            
            # Store in appropriate cache level
            success = await self._store_in_level(cache_level, entry)
            
            if success:
                self._cache_entries[cache_key] = entry
                await self._update_analytics(entry, "set")
                
                # Schedule invalidation if TTL specified
                if entry.ttl:
                    await self.invalidation_engine.schedule_invalidation(
                        cache_key, entry.ttl
                    )
            
            execution_time = time.time() - start_time
            self._operation_times.append(execution_time)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(
        self,
        key: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> bool:
        """Delete entry from all cache levels"""



        try:
            cache_key = self._generate_cache_key(key, user_id, tenant_id)
            
            # Remove from all cache levels
            success = await self.storage.delete(cache_key)
            
            # Remove from local tracking
            if cache_key in self._cache_entries:
                del self._cache_entries[cache_key]
            
            # Cancel any scheduled invalidation
            await self.invalidation_engine.cancel_invalidation(cache_key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate all entries matching specified tags"""



        try:
            invalidated_count = 0
            
            for cache_key, entry in list(self._cache_entries.items()):
                if any(tag in entry.tags for tag in tags):
                    await self.delete(cache_key)
                    invalidated_count += 1
            
            self._stats.invalidations += invalidated_count
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Tag-based invalidation error: {e}")
            return 0
    
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate entries matching key pattern"""



        try:
            import re
            regex = re.compile(pattern)
            invalidated_count = 0
            
            for cache_key in list(self._cache_entries.keys()):
                if regex.match(cache_key):
                    await self.delete(cache_key)
                    invalidated_count += 1
            
            self._stats.invalidations += invalidated_count
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Pattern-based invalidation error: {e}")
            return 0
    
    async def warm_cache(
        self,
        data_loader: Callable,
        keys: List[str],
        batch_size: int = 100
    ) -> int:
        """Pre-populate cache with anticipated data"""



        try:
            warmed_count = 0
            
            for i in range(0, len(keys), batch_size):
                batch_keys = keys[i:i + batch_size]
                batch_data = await data_loader(batch_keys)
                
                for key, value in batch_data.items():
                    if await self.set(key, value, priority=CachePriority.HIGH):
                        warmed_count += 1
            
            logger.info(f"Cache warmed with {warmed_count} entries")
            return warmed_count
            
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
            return 0
    
    async def get_statistics(self) -> CacheStats:
        """Get comprehensive cache performance statistics"""
        self._stats.hit_ratio = self._calculate_hit_ratio()
        self._stats.average_response_time = self._calculate_average_response_time()
        self._stats.entry_count = len(self._cache_entries)
        self._stats.total_size_bytes = sum(
            entry.size_bytes for entry in self._cache_entries.values()
        )
        self._stats.memory_usage_percent = (
            self._stats.total_size_bytes / self.config.max_memory_size * 100
        )
        
        return self._stats
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Perform comprehensive cache optimization"""



        try:
            optimization_results = await self.optimizer.optimize(
                self._cache_entries,
                self._stats,
                self.config
            )
            
            # Apply optimization recommendations
            if optimization_results.get("evict_entries"):
                for key in optimization_results["evict_entries"]:
                    await self.delete(key)
            
            if optimization_results.get("promote_entries"):
                for key, target_level in optimization_results["promote_entries"].items():
                    await self._promote_to_level(key, target_level)
            
            self._last_optimization = datetime.utcnow()
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization error: {e}")
            return {}
    
    # Private helper methods
    
    def _generate_cache_key(
        self, 
        key: str, 
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Generate context-aware cache key"""
        components = [key]
        
        if tenant_id:
            components.insert(0, f"tenant:{tenant_id}")
        if user_id:
            components.insert(-1, f"user:{user_id}")
            
        return ":".join(components)
    
    def _generate_checksum(self, value: Any) -> str:
        """Generate integrity checksum for cached value"""
        serialized = pickle.dumps(value)
        return hashlib.sha256(serialized).hexdigest()
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate memory size of value in bytes"""



        try:
            return len(pickle.dumps(value))
        except:
            return 0
    
    async def _get_from_hierarchy(self, cache_key: str) -> Optional[Any]:
        """Retrieve value from cache hierarchy (L1->L2->L3->L4)"""
        for level in self.config.cache_levels:
            value = await self.storage.get_from_level(level, cache_key)
            if value is not None:
                return value
        return None
    
    async def _store_in_level(self, level: CacheLevel, entry: CacheEntry) -> bool:
        """Store entry in specific cache level"""



        return await self.storage.set_in_level(level, entry.key, entry)
    
    async def _determine_optimal_level(self, entry: CacheEntry) -> CacheLevel:
        """Determine optimal cache level for entry"""
        # High priority and frequently accessed -> L1 Memory
        if entry.priority in [CachePriority.CRITICAL, CachePriority.HIGH]:
            return CacheLevel.L1_MEMORY
        
        # Medium sized data -> L2 Redis
        if entry.size_bytes < 1024 * 1024:  # < 1MB
            return CacheLevel.L2_REDIS
        
        # Large data -> L3 Database
        return CacheLevel.L3_DATABASE
    
    async def _promote_cache_entry(self, cache_key: str, value: Any):
        """Promote frequently accessed entries to higher cache levels"""
        if cache_key in self._cache_entries:
            entry = self._cache_entries[cache_key]
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            
            # Promote if access frequency justifies it
            if entry.access_count > 10 and entry.access_count % 5 == 0:
                await self._promote_to_level(cache_key, CacheLevel.L1_MEMORY)
    
    async def _promote_to_level(self, cache_key: str, target_level: CacheLevel):
        """Promote entry to specific cache level"""
        if cache_key in self._cache_entries:
            entry = self._cache_entries[cache_key]
            await self._store_in_level(target_level, entry)
    
    async def _record_hit(self, cache_key: str):
        """Record cache hit for analytics"""
        if cache_key in self._cache_entries:
            entry = self._cache_entries[cache_key]
            entry.hit_count += 1
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
    
    async def _record_miss(self, cache_key: str):
        """Record cache miss for analytics"""
        await self.analytics.record_miss(cache_key)
    
    def _update_hit_ratio(self):
        """Update cache hit ratio statistics"""
        total = self._stats.cache_hits + self._stats.cache_misses
        if total > 0:
            self._stats.hit_ratio = self._stats.cache_hits / total
    
    def _calculate_hit_ratio(self) -> float:
        """Calculate current hit ratio"""
        total = self._stats.cache_hits + self._stats.cache_misses
        return self._stats.cache_hits / total if total > 0 else 0.0
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time"""
        if not self._operation_times:
            return 0.0
        return sum(self._operation_times) / len(self._operation_times)
    
    async def _compress_value(self, value: Any) -> bytes:
        """Compress value for storage efficiency"""
        import gzip
        serialized = pickle.dumps(value)
        return gzip.compress(serialized)
    
    async def _encrypt_value(self, value: Any) -> bytes:
        """Encrypt value for security"""



        return await self._encryption.encrypt(pickle.dumps(value))
    
    def _requires_encryption(self, content_type: Optional[str]) -> bool:
        """Determine if content requires encryption"""
        sensitive_types = [
            "user_data", "payment_info", "authentication",
            "personal_info", "financial_data"
        ]
        return content_type in sensitive_types if content_type else False
    
    async def _update_analytics(self, entry: CacheEntry, operation: str):
        """Update analytics with cache operation"""
        if self.config.enable_analytics:
            await self.analytics.record_operation(entry, operation)
    
    async def _optimization_loop(self):
        """Background cache optimization loop"""
        while not self.shutdown_requested:
            try:
                if (datetime.utcnow() - self._last_optimization).seconds >= self.config.optimization_interval:
                    await self.optimize_cache()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Graceful shutdown of caching manager"""
        self.shutdown_requested = True
        await self.storage.close()
        await self.coordinator.shutdown()
        await super().shutdown()
        logger.info(f"CachingManager {self.agent_id} shut down gracefully")
