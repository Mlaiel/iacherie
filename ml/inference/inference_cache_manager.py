#!/usr/bin/env python3
"""
⚡ Inference Cache Manager - High-Performance ML Caching System
Backend Senior Implementation - Enterprise Caching Architecture

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

Enterprise-grade inference caching with intelligent cache policies,
distributed caching, and performance optimization for ML workloads.
"""

import asyncio
import logging
import json
import hashlib
import pickle
import time
import redis
import memcache
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import aioredis
import aiocache
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
import psutil
import gc

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache replacement strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    RANDOM = "random"
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # AI-powered adaptive caching

class CacheBackend(Enum):
    """Supported cache backends"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    HYBRID = "hybrid"
    DISTRIBUTED = "distributed"

class CacheLevel(Enum):
    """Cache hierarchy levels"""
    L1_MEMORY = 1  # In-process memory
    L2_LOCAL_SSD = 2  # Local SSD cache
    L3_DISTRIBUTED = 3  # Distributed cache cluster
    L4_PERSISTENT = 4  # Persistent storage

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    evictions: int = 0
    cache_size: int = 0
    
    def update_hit(self, response_time_ms: float):
        """Update metrics for cache hit"""
        self.cache_hits += 1
        self.total_requests += 1
        self._update_response_time(response_time_ms)
        self._recalculate_rates()
    
    def update_miss(self, response_time_ms: float):
        """Update metrics for cache miss"""
        self.cache_misses += 1
        self.total_requests += 1
        self._update_response_time(response_time_ms)
        self._recalculate_rates()
    
    def _update_response_time(self, response_time_ms: float):
        """Update average response time"""
        if self.total_requests == 1:
            self.avg_response_time_ms = response_time_ms
        else:
            # Exponential moving average
            alpha = 0.1
            self.avg_response_time_ms = (
                alpha * response_time_ms + 
                (1 - alpha) * self.avg_response_time_ms
            )
    
    def _recalculate_rates(self):
        """Recalculate hit and miss rates"""
        if self.total_requests > 0:
            self.hit_rate = self.cache_hits / self.total_requests
            self.miss_rate = self.cache_misses / self.total_requests

@dataclass
class CacheConfig:
    """Inference cache configuration"""
    backend: CacheBackend = CacheBackend.HYBRID
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    max_memory_mb: int = 1024
    max_cache_size: int = 10000
    ttl_seconds: int = 3600
    enable_compression: bool = True
    enable_encryption: bool = False
    shard_count: int = 4
    redis_url: str = "redis://localhost:6379"
    memcached_servers: List[str] = field(default_factory=lambda: ["localhost:11211"])
    enable_prefetch: bool = True
    prefetch_threshold: float = 0.8  # Prefetch when cache is 80% full
    enable_analytics: bool = True

class IntelligentCacheKey:
    """Intelligent cache key generation with content awareness"""
    
    @staticmethod
    def generate_key(
        model_id: str,
        input_data: Any,
        creator_type: str = "general",
        include_model_version: bool = True
    ) -> str:
        """Generate intelligent cache key based on content"""
        key_components = [model_id, creator_type]
        
        # Hash input data efficiently
        if isinstance(input_data, dict):
            # Sort keys for consistent hashing
            sorted_data = json.dumps(input_data, sort_keys=True)
            data_hash = hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
        elif isinstance(input_data, np.ndarray):
            # Use array characteristics for hashing
            data_hash = hashlib.sha256(
                f"{input_data.shape}_{input_data.dtype}_{input_data.sum()}"
                .encode()
            ).hexdigest()[:16]
        else:
            # Generic string hashing
            data_hash = hashlib.sha256(str(input_data).encode()).hexdigest()[:16]
        
        key_components.append(data_hash)
        
        # Add model version if requested
        if include_model_version:
            key_components.append("v1.0")  # In real impl, get actual version
        
        return ":".join(key_components)
    
    @staticmethod
    def extract_creator_pattern(cache_key: str) -> str:
        """Extract creator pattern from cache key for analytics"""
        parts = cache_key.split(":")
        return parts[1] if len(parts) > 1 else "unknown"

class AdaptiveCacheStrategy:
    """AI-powered adaptive caching strategy"""
    
    def __init__(self):
        self.access_patterns: Dict[str, List[float]] = {}
        self.creator_preferences: Dict[str, Dict[str, float]] = {}
        self.time_patterns: Dict[int, int] = {}  # hour -> access_count
        self.prediction_model = None
        
    def record_access(self, cache_key: str, timestamp: float):
        """Record cache access for pattern learning"""
        if cache_key not in self.access_patterns:
            self.access_patterns[cache_key] = []
        
        self.access_patterns[cache_key].append(timestamp)
        
        # Record hourly patterns
        hour = int(time.time() // 3600) % 24
        self.time_patterns[hour] = self.time_patterns.get(hour, 0) + 1
        
        # Analyze creator patterns
        creator_type = IntelligentCacheKey.extract_creator_pattern(cache_key)
        if creator_type not in self.creator_preferences:
            self.creator_preferences[creator_type] = {}
        
        # Update creator access frequency
        model_pattern = cache_key.split(":")[0]
        if model_pattern not in self.creator_preferences[creator_type]:
            self.creator_preferences[creator_type][model_pattern] = 0
        self.creator_preferences[creator_type][model_pattern] += 1
    
    def predict_next_access(self, cache_key: str) -> float:
        """Predict probability of next access"""
        if cache_key not in self.access_patterns:
            return 0.1  # Low probability for new keys
        
        accesses = self.access_patterns[cache_key]
        if len(accesses) < 2:
            return 0.3
        
        # Calculate access frequency
        time_span = accesses[-1] - accesses[0]
        if time_span == 0:
            return 0.9  # Very recent multiple accesses
        
        frequency = len(accesses) / time_span
        
        # Factor in creator preferences
        creator_type = IntelligentCacheKey.extract_creator_pattern(cache_key)
        creator_bonus = self._get_creator_bonus(creator_type, cache_key)
        
        # Factor in time patterns
        current_hour = int(time.time() // 3600) % 24
        time_bonus = self.time_patterns.get(current_hour, 0) / 1000.0
        
        prediction = min(0.95, frequency * 1000 + creator_bonus + time_bonus)
        return max(0.05, prediction)
    
    def _get_creator_bonus(self, creator_type: str, cache_key: str) -> float:
        """Get bonus score based on creator preferences"""
        if creator_type not in self.creator_preferences:
            return 0.0
        
        model_pattern = cache_key.split(":")[0]
        creator_prefs = self.creator_preferences[creator_type]
        
        if model_pattern not in creator_prefs:
            return 0.0
        
        total_accesses = sum(creator_prefs.values())
        return creator_prefs[model_pattern] / total_accesses * 0.2
    
    def should_cache(self, cache_key: str, prediction_result: Any) -> bool:
        """Decide whether to cache based on adaptive strategy"""
        access_probability = self.predict_next_access(cache_key)
        
        # High probability items should always be cached
        if access_probability > 0.7:
            return True
        
        # Consider computation cost (mock implementation)
        computation_cost = self._estimate_computation_cost(prediction_result)
        
        # Cache if access probability * computation cost is high
        cache_score = access_probability * computation_cost
        return cache_score > 0.5
    
    def _estimate_computation_cost(self, result: Any) -> float:
        """Estimate computation cost of result"""
        if isinstance(result, dict):
            return len(result) / 1000.0  # Normalize by complexity
        elif isinstance(result, np.ndarray):
            return result.size / 100000.0  # Normalize by array size
        else:
            return 0.5  # Default medium cost

class InferenceCacheManager:
    """
    ⚡ Enterprise Inference Cache Manager
    
    High-performance caching system for ML inference with intelligent
    cache strategies, distributed backends, and performance optimization.
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.metrics = CacheMetrics()
        self.adaptive_strategy = AdaptiveCacheStrategy()
        self.cache_levels: Dict[CacheLevel, Any] = {}
        self.locks: Dict[str, threading.Lock] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Initialize cache backends
        asyncio.create_task(self._initialize_backends())
        
        # Start background tasks
        asyncio.create_task(self._background_maintenance())
        
        logger.info(f"⚡ Inference Cache Manager initialized with {config.backend.value} backend")
    
    async def _initialize_backends(self):
        """Initialize cache backends based on configuration"""
        try:
            # L1 Memory Cache
            self.cache_levels[CacheLevel.L1_MEMORY] = {}
            
            # L2 Redis Cache
            if self.config.backend in [CacheBackend.REDIS, CacheBackend.HYBRID, CacheBackend.DISTRIBUTED]:
                self.cache_levels[CacheLevel.L3_DISTRIBUTED] = aioredis.from_url(
                    self.config.redis_url,
                    encoding="utf-8",
                    decode_responses=False
                )
            
            # Configure aiocache for high-level operations
            aiocache.caches.set_config({
                'default': {
                    'cache': "aiocache.RedisCache",
                    'endpoint': self.config.redis_url.split("//")[1],
                    'serializer': {
                        'class': "aiocache.serializers.PickleSerializer"
                    }
                }
            })
            
            logger.info("✅ Cache backends initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cache backends: {str(e)}")
            # Fallback to memory-only cache
            self.config.backend = CacheBackend.MEMORY
    
    async def get_cached_inference(
        self,
        model_id: str,
        input_data: Any,
        creator_type: str = "general"
    ) -> Optional[Any]:
        """
        Retrieve cached inference result with intelligent lookup
        
        Args:
            model_id: Model identifier
            input_data: Input data for inference
            creator_type: Type of creator (musician, blogger, etc.)
            
        Returns:
            Cached result if found, None otherwise
        """
        start_time = time.time()
        
        # Generate intelligent cache key
        cache_key = IntelligentCacheKey.generate_key(
            model_id, input_data, creator_type
        )
        
        try:
            # Multi-level cache lookup
            result = await self._multi_level_lookup(cache_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if result is not None:
                self.metrics.update_hit(response_time)
                self.adaptive_strategy.record_access(cache_key, time.time())
                logger.debug(f"🎯 Cache hit for {cache_key[:20]}... in {response_time:.2f}ms")
                return result
            else:
                self.metrics.update_miss(response_time)
                logger.debug(f"❌ Cache miss for {cache_key[:20]}...")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cache lookup error: {str(e)}")
            response_time = (time.time() - start_time) * 1000
            self.metrics.update_miss(response_time)
            return None
    
    async def cache_inference_result(
        self,
        model_id: str,
        input_data: Any,
        result: Any,
        creator_type: str = "general",
        custom_ttl: Optional[int] = None
    ) -> bool:
        """
        Cache inference result with intelligent storage strategy
        
        Args:
            model_id: Model identifier
            input_data: Input data used for inference
            result: Inference result to cache
            creator_type: Type of creator
            custom_ttl: Custom TTL override
            
        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = IntelligentCacheKey.generate_key(
            model_id, input_data, creator_type
        )
        
        try:
            # Adaptive caching decision
            if (self.config.strategy == CacheStrategy.ADAPTIVE and
                not self.adaptive_strategy.should_cache(cache_key, result)):
                logger.debug(f"🤖 Adaptive strategy: Skip caching {cache_key[:20]}...")
                return False
            
            # Determine TTL
            ttl = custom_ttl if custom_ttl else self.config.ttl_seconds
            
            # Predict access probability for TTL adjustment
            if self.config.strategy == CacheStrategy.ADAPTIVE:
                access_prob = self.adaptive_strategy.predict_next_access(cache_key)
                ttl = int(ttl * (1 + access_prob))  # Extend TTL for likely accessed items
            
            # Store in multi-level cache
            success = await self._multi_level_store(cache_key, result, ttl)
            
            if success:
                self.adaptive_strategy.record_access(cache_key, time.time())
                logger.debug(f"💾 Cached result for {cache_key[:20]}... (TTL: {ttl}s)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Cache storage error: {str(e)}")
            return False
    
    async def _multi_level_lookup(self, cache_key: str) -> Optional[Any]:
        """Multi-level cache lookup with promotion"""
        # L1 Memory lookup (fastest)
        l1_cache = self.cache_levels.get(CacheLevel.L1_MEMORY)
        if l1_cache and cache_key in l1_cache:
            entry = l1_cache[cache_key]
            if self._is_valid_entry(entry):
                return entry['data']
        
        # L3 Distributed lookup
        redis_cache = self.cache_levels.get(CacheLevel.L3_DISTRIBUTED)
        if redis_cache:
            try:
                cached_data = await redis_cache.get(cache_key)
                if cached_data:
                    result = pickle.loads(cached_data)
                    
                    # Promote to L1 cache
                    await self._promote_to_l1(cache_key, result)
                    
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Redis lookup failed: {str(e)}")
        
        return None
    
    async def _multi_level_store(
        self, 
        cache_key: str, 
        data: Any, 
        ttl: int
    ) -> bool:
        """Store data in multi-level cache hierarchy"""
        success = True
        
        # Store in L1 Memory (with size limit)
        if await self._store_l1(cache_key, data, ttl):
            logger.debug(f"✅ Stored in L1 cache: {cache_key[:20]}...")
        else:
            success = False
        
        # Store in L3 Distributed
        redis_cache = self.cache_levels.get(CacheLevel.L3_DISTRIBUTED)
        if redis_cache:
            try:
                serialized_data = pickle.dumps(data)
                await redis_cache.setex(cache_key, ttl, serialized_data)
                logger.debug(f"✅ Stored in Redis: {cache_key[:20]}...")
            except Exception as e:
                logger.warning(f"⚠️ Redis storage failed: {str(e)}")
                success = False
        
        return success
    
    async def _store_l1(self, cache_key: str, data: Any, ttl: int) -> bool:
        """Store in L1 memory cache with eviction policy"""
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        
        # Check memory limits
        if await self._should_evict_l1():
            await self._evict_l1_entries()
        
        # Store with timestamp and TTL
        l1_cache[cache_key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl,
            'access_count': 0
        }
        
        self.metrics.cache_size = len(l1_cache)
        return True
    
    async def _should_evict_l1(self) -> bool:
        """Check if L1 cache eviction is needed"""
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        
        # Check size limit
        if len(l1_cache) >= self.config.max_cache_size:
            return True
        
        # Check memory usage
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
        if memory_usage > self.config.max_memory_mb:
            return True
        
        return False
    
    async def _evict_l1_entries(self):
        """Evict entries from L1 cache based on strategy"""
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        
        if self.config.strategy == CacheStrategy.LRU:
            # Remove least recently used
            sorted_items = sorted(
                l1_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
        elif self.config.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            sorted_items = sorted(
                l1_cache.items(),
                key=lambda x: x[1]['access_count']
            )
        elif self.config.strategy == CacheStrategy.ADAPTIVE:
            # Remove based on adaptive prediction
            sorted_items = sorted(
                l1_cache.items(),
                key=lambda x: self.adaptive_strategy.predict_next_access(x[0])
            )
        else:
            # FIFO - remove oldest
            sorted_items = sorted(
                l1_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
        
        # Remove 25% of entries
        evict_count = max(1, len(sorted_items) // 4)
        for i in range(evict_count):
            key_to_remove = sorted_items[i][0]
            del l1_cache[key_to_remove]
            self.metrics.evictions += 1
        
        logger.debug(f"🗑️ Evicted {evict_count} entries from L1 cache")
    
    async def _promote_to_l1(self, cache_key: str, data: Any):
        """Promote data from lower cache level to L1"""
        await self._store_l1(cache_key, data, self.config.ttl_seconds)
        logger.debug(f"⬆️ Promoted to L1: {cache_key[:20]}...")
    
    def _is_valid_entry(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        current_time = time.time()
        entry_time = entry['timestamp']
        ttl = entry['ttl']
        
        is_valid = (current_time - entry_time) < ttl
        
        if is_valid:
            # Update access count
            entry['access_count'] += 1
            entry['timestamp'] = current_time  # Update for LRU
        
        return is_valid
    
    async def _background_maintenance(self):
        """Background maintenance tasks"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean expired L1 entries
                await self._cleanup_expired_l1()
                
                # Update memory usage metrics
                self.metrics.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Log cache statistics
                logger.info(f"📊 Cache Stats - Hit Rate: {self.metrics.hit_rate:.2%}, "
                           f"Size: {self.metrics.cache_size}, "
                           f"Memory: {self.metrics.memory_usage_mb:.1f}MB")
                
                # Trigger garbage collection
                gc.collect()
                
            except Exception as e:
                logger.error(f"❌ Background maintenance error: {str(e)}")
    
    async def _cleanup_expired_l1(self):
        """Clean up expired entries from L1 cache"""
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        current_time = time.time()
        expired_keys = []
        
        for key, entry in l1_cache.items():
            if (current_time - entry['timestamp']) > entry['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del l1_cache[key]
        
        if expired_keys:
            logger.debug(f"🧹 Cleaned {len(expired_keys)} expired L1 entries")
    
    @cached(ttl=60, cache=Cache.MEMORY)
    async def get_cache_analytics(self) -> Dict[str, Any]:
        """Get comprehensive cache analytics"""
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        
        # Analyze cache content by creator type
        creator_analysis = {}
        for key in l1_cache.keys():
            creator_type = IntelligentCacheKey.extract_creator_pattern(key)
            creator_analysis[creator_type] = creator_analysis.get(creator_type, 0) + 1
        
        # Performance analysis
        performance_analysis = {
            "cache_efficiency": {
                "hit_rate_percent": self.metrics.hit_rate * 100,
                "miss_rate_percent": self.metrics.miss_rate * 100,
                "avg_response_time_ms": self.metrics.avg_response_time_ms,
                "total_requests": self.metrics.total_requests
            },
            "capacity_analysis": {
                "cache_size": self.metrics.cache_size,
                "max_cache_size": self.config.max_cache_size,
                "utilization_percent": (self.metrics.cache_size / self.config.max_cache_size) * 100,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "max_memory_mb": self.config.max_memory_mb
            },
            "creator_distribution": creator_analysis,
            "eviction_stats": {
                "total_evictions": self.metrics.evictions,
                "eviction_rate": self.metrics.evictions / max(1, self.metrics.total_requests)
            }
        }
        
        return performance_analysis
    
    async def invalidate_cache(
        self, 
        pattern: Optional[str] = None,
        model_id: Optional[str] = None,
        creator_type: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries based on pattern or criteria
        
        Args:
            pattern: Redis-style pattern for key matching
            model_id: Specific model ID to invalidate
            creator_type: Specific creator type to invalidate
            
        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0
        
        # L1 Memory invalidation
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        keys_to_remove = []
        
        for key in l1_cache.keys():
            should_invalidate = False
            
            if pattern and pattern in key:
                should_invalidate = True
            elif model_id and key.startswith(model_id):
                should_invalidate = True
            elif creator_type and f":{creator_type}:" in key:
                should_invalidate = True
            
            if should_invalidate:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del l1_cache[key]
            invalidated_count += 1
        
        # Redis invalidation
        redis_cache = self.cache_levels.get(CacheLevel.L3_DISTRIBUTED)
        if redis_cache and pattern:
            try:
                matching_keys = await redis_cache.keys(pattern)
                if matching_keys:
                    await redis_cache.delete(*matching_keys)
                    invalidated_count += len(matching_keys)
            except Exception as e:
                logger.error(f"❌ Redis invalidation error: {str(e)}")
        
        logger.info(f"🗑️ Invalidated {invalidated_count} cache entries")
        return invalidated_count
    
    async def warmup_cache(
        self,
        warmup_data: List[Dict[str, Any]],
        concurrency: int = 10
    ) -> Dict[str, Any]:
        """
        Warm up cache with predicted hot data
        
        Args:
            warmup_data: List of {model_id, input_data, creator_type, result}
            concurrency: Number of concurrent warmup operations
            
        Returns:
            Warmup statistics
        """
        logger.info(f"🔥 Starting cache warmup with {len(warmup_data)} entries")
        
        semaphore = asyncio.Semaphore(concurrency)
        successful_warmups = 0
        
        async def warmup_single(data_entry: Dict[str, Any]):
            nonlocal successful_warmups
            
            async with semaphore:
                try:
                    success = await self.cache_inference_result(
                        model_id=data_entry['model_id'],
                        input_data=data_entry['input_data'],
                        result=data_entry['result'],
                        creator_type=data_entry.get('creator_type', 'general')
                    )
                    if success:
                        successful_warmups += 1
                except Exception as e:
                    logger.warning(f"⚠️ Warmup failed for entry: {str(e)}")
        
        # Execute warmup tasks
        start_time = time.time()
        tasks = [warmup_single(data) for data in warmup_data]
        await asyncio.gather(*tasks, return_exceptions=True)
        warmup_time = time.time() - start_time
        
        warmup_stats = {
            "total_entries": len(warmup_data),
            "successful_warmups": successful_warmups,
            "success_rate": successful_warmups / len(warmup_data),
            "warmup_time_seconds": warmup_time,
            "throughput_entries_per_second": len(warmup_data) / warmup_time
        }
        
        logger.info(f"✅ Cache warmup completed: {successful_warmups}/{len(warmup_data)} "
                   f"entries in {warmup_time:.2f}s")
        
        return warmup_stats
    
    async def export_cache_state(self, output_path: str) -> Dict[str, Any]:
        """Export current cache state for analysis"""
        l1_cache = self.cache_levels[CacheLevel.L1_MEMORY]
        
        cache_state = {
            "timestamp": time.time(),
            "config": {
                "backend": self.config.backend.value,
                "strategy": self.config.strategy.value,
                "max_memory_mb": self.config.max_memory_mb,
                "max_cache_size": self.config.max_cache_size
            },
            "metrics": {
                "hit_rate": self.metrics.hit_rate,
                "total_requests": self.metrics.total_requests,
                "cache_size": self.metrics.cache_size,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "evictions": self.metrics.evictions
            },
            "cache_entries": []
        }
        
        # Export cache entries (metadata only, not full data)
        for key, entry in l1_cache.items():
            cache_state["cache_entries"].append({
                "key": key,
                "timestamp": entry['timestamp'],
                "ttl": entry['ttl'],
                "access_count": entry['access_count'],
                "data_size_bytes": len(pickle.dumps(entry['data']))
            })
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(cache_state, f, indent=2)
        
        logger.info(f"💾 Exported cache state to {output_path}")
        return cache_state
    
    async def shutdown(self):
        """Graceful shutdown of cache manager"""
        logger.info("🔄 Shutting down Inference Cache Manager...")
        
        # Close Redis connections
        redis_cache = self.cache_levels.get(CacheLevel.L3_DISTRIBUTED)
        if redis_cache:
            await redis_cache.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Export final analytics
        final_analytics = await self.get_cache_analytics()
        logger.info(f"📊 Final cache analytics: {json.dumps(final_analytics, indent=2)}")
        
        logger.info("✅ Inference Cache Manager shutdown complete")

# Factory for creating specialized cache configurations
class CacheFactory:
    """Factory for creating specialized cache configurations"""
    
    @staticmethod
    def create_musician_cache() -> InferenceCacheManager:
        """Create cache optimized for music/audio workloads"""
        config = CacheConfig(
            backend=CacheBackend.HYBRID,
            strategy=CacheStrategy.ADAPTIVE,
            max_memory_mb=2048,  # Larger cache for audio data
            max_cache_size=5000,
            ttl_seconds=1800,  # 30 minutes for audio inference
            enable_compression=True,
            enable_prefetch=True
        )
        return InferenceCacheManager(config)
    
    @staticmethod
    def create_realtime_cache() -> InferenceCacheManager:
        """Create cache optimized for real-time inference"""
        config = CacheConfig(
            backend=CacheBackend.MEMORY,  # Memory-only for speed
            strategy=CacheStrategy.LRU,
            max_memory_mb=512,
            max_cache_size=1000,
            ttl_seconds=300,  # 5 minutes for real-time
            enable_compression=False,  # Disable for speed
            enable_prefetch=True
        )
        return InferenceCacheManager(config)
    
    @staticmethod
    def create_distributed_cache() -> InferenceCacheManager:
        """Create distributed cache for enterprise deployment"""
        config = CacheConfig(
            backend=CacheBackend.DISTRIBUTED,
            strategy=CacheStrategy.ADAPTIVE,
            max_memory_mb=4096,
            max_cache_size=20000,
            ttl_seconds=7200,  # 2 hours
            enable_compression=True,
            enable_encryption=True,
            shard_count=8
        )
        return InferenceCacheManager(config)

async def main():
    """Example usage of Inference Cache Manager"""
    # Create cache manager for musicians
    cache_manager = CacheFactory.create_musician_cache()
    
    # Example inference caching
    model_id = "audio-classifier-v2"
    input_data = {"audio_features": np.random.rand(1000)}
    creator_type = "musician"
    
    # Check cache first
    cached_result = await cache_manager.get_cached_inference(
        model_id, input_data, creator_type
    )
    
    if cached_result is None:
        # Simulate inference
        inference_result = {"classification": "jazz", "confidence": 0.87}
        
        # Cache the result
        await cache_manager.cache_inference_result(
            model_id, input_data, inference_result, creator_type
        )
        
        print("🔮 Inference computed and cached")
    else:
        print("⚡ Inference served from cache")
    
    # Get analytics
    analytics = await cache_manager.get_cache_analytics()
    print(f"📊 Cache Analytics: {json.dumps(analytics, indent=2)}")
    
    # Shutdown
    await cache_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())