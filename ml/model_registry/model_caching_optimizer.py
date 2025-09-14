"""📦 Model Caching Optimizer - Enterprise ML Infrastructure
==========================================================
Module: ml/model_registry/model_caching_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODEL CACHING OPTIMIZATION SYSTEM
Intelligent model caching strategies for optimal loading performance
- Multi-tier caching with intelligent eviction
- Predictive model pre-loading
- Performance-based cache optimization
- Creator-specific caching strategies
"""

import asyncio
import logging
import time
import uuid
import hashlib
import pickle
import zlib
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from collections import OrderedDict, defaultdict
import psutil
import threading

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels"""
    L1_MEMORY = "l1_memory"
    L2_DISK = "l2_disk"
    L3_DISTRIBUTED = "l3_distributed"
    L4_CLOUD = "l4_cloud"


class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    PRIORITY = "priority"  # Priority-based
    ADAPTIVE = "adaptive"  # ML-based adaptive


class CacheStatus(Enum):
    """Cache entry status"""
    CACHED = "cached"
    LOADING = "loading"
    EXPIRED = "expired"
    EVICTED = "evicted"
    FAILED = "failed"


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    model_id: str
    version: str
    cache_level: CacheLevel
    size: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    priority: float = 1.0
    ttl: Optional[int] = None
    creator_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    cache_level: CacheLevel
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    loading_time: float = 0.0
    memory_usage: int = 0
    disk_usage: int = 0
    hit_rate: float = 0.0


@dataclass
class PredictionRequest:
    """Prediction request for pre-loading"""
    model_id: str
    creator_type: str
    predicted_time: datetime
    confidence: float
    request_pattern: str


class ModelCachingOptimizer:
    """Intelligent Model Caching Optimizer"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Cache storage
        self.l1_cache: OrderedDict[str, Any] = OrderedDict()
        self.l2_cache: Dict[str, str] = {}  # Key -> file path
        self.cache_entries: Dict[str, CacheEntry] = {}
        
        # Configuration
        self.l1_max_size = self.config.get('l1_max_size', 1024 * 1024 * 1024)  # 1GB
        self.l2_max_size = self.config.get('l2_max_size', 10 * 1024 * 1024 * 1024)  # 10GB
        self.default_ttl = self.config.get('default_ttl', 3600)  # 1 hour
        self.eviction_policy = EvictionPolicy(self.config.get('eviction_policy', 'adaptive'))
        
        # Performance tracking
        self.metrics: Dict[CacheLevel, CacheMetrics] = {
            level: CacheMetrics(level) for level in CacheLevel
        }
        
        # Pre-loading system
        self.prediction_queue: asyncio.Queue = asyncio.Queue()
        self.access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.creator_patterns: Dict[str, Dict[str, List[datetime]]] = defaultdict(lambda: defaultdict(list))
        
        # Monitoring
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.cleanup_interval = self.config.get('cleanup_interval', 300)  # 5 minutes
        
        # Cache directory
        self.cache_dir = Path(self.config.get('cache_dir', '/tmp/model_cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("📦 Model Caching Optimizer initialized")
    
    async def get_model(
        self,
        model_id: str,
        version: str = "latest",
        creator_type: Optional[str] = None
    ) -> Optional[Any]:
        """Get model from cache with intelligent loading"""
        try:
            cache_key = f"{model_id}:{version}"
            current_time = datetime.utcnow()
            
            # Record access pattern
            self.access_patterns[model_id].append(current_time)
            if creator_type:
                self.creator_patterns[creator_type][model_id].append(current_time)
            
            # Try L1 cache first
            model = await self._get_from_l1(cache_key)
            if model is not None:
                await self._update_access_stats(cache_key, CacheLevel.L1_MEMORY)
                return model
            
            # Try L2 cache
            model = await self._get_from_l2(cache_key)
            if model is not None:
                # Promote to L1 if frequently accessed
                if await self._should_promote_to_l1(cache_key):
                    await self._store_in_l1(cache_key, model)
                await self._update_access_stats(cache_key, CacheLevel.L2_DISK)
                return model
            
            # Cache miss - load model
            model = await self._load_model(model_id, version)
            if model is not None:
                # Determine optimal cache level
                cache_level = await self._determine_cache_level(
                    model_id, creator_type, model
                )
                
                # Store in appropriate cache level
                await self._store_model(cache_key, model, cache_level, creator_type)
                
                await self._update_access_stats(cache_key, cache_level, miss=True)
                return model
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting model {model_id}: {e}")
            return None
    
    async def preload_model(
        self,
        model_id: str,
        version: str = "latest",
        creator_type: Optional[str] = None,
        priority: float = 1.0
    ) -> bool:
        """Preload model based on prediction"""
        try:
            cache_key = f"{model_id}:{version}"
            
            # Check if already cached
            if await self._is_cached(cache_key):
                return True
            
            # Load model
            model = await self._load_model(model_id, version)
            if model is None:
                return False
            
            # Determine cache level based on priority
            if priority > 0.8:
                cache_level = CacheLevel.L1_MEMORY
            elif priority > 0.5:
                cache_level = CacheLevel.L2_DISK
            else:
                cache_level = CacheLevel.L3_DISTRIBUTED
            
            # Store with high priority
            await self._store_model(
                cache_key, model, cache_level, creator_type, priority
            )
            
            logger.info(f"✅ Preloaded model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error preloading model {model_id}: {e}")
            return False
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        try:
            optimization_results = {
                'evicted_entries': 0,
                'promoted_entries': 0,
                'preloaded_entries': 0,
                'memory_freed': 0,
                'disk_freed': 0
            }
            
            # Clean up expired entries
            evicted = await self._cleanup_expired_entries()
            optimization_results['evicted_entries'] = evicted
            
            # Optimize L1 cache
            l1_results = await self._optimize_l1_cache()
            optimization_results.update(l1_results)
            
            # Optimize L2 cache
            l2_results = await self._optimize_l2_cache()
            optimization_results.update(l2_results)
            
            # Predict and preload models
            preloaded = await self._predictive_preloading()
            optimization_results['preloaded_entries'] = preloaded
            
            # Update metrics
            await self._update_cache_metrics()
            
            logger.info(f"🔧 Cache optimization completed: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Error optimizing cache: {e}")
            return {}
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            stats = {
                'cache_levels': {},
                'total_entries': len(self.cache_entries),
                'memory_usage': await self._get_memory_usage(),
                'disk_usage': await self._get_disk_usage(),
                'hit_rates': {},
                'top_models': await self._get_top_accessed_models(),
                'creator_patterns': await self._get_creator_access_patterns()
            }
            
            # Cache level statistics
            for level, metrics in self.metrics.items():
                stats['cache_levels'][level.value] = {
                    'total_requests': metrics.total_requests,
                    'cache_hits': metrics.cache_hits,
                    'cache_misses': metrics.cache_misses,
                    'hit_rate': metrics.hit_rate,
                    'evictions': metrics.evictions,
                    'memory_usage': metrics.memory_usage,
                    'disk_usage': metrics.disk_usage
                }
                stats['hit_rates'][level.value] = metrics.hit_rate
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting cache stats: {e}")
            return {}
    
    async def evict_model(self, model_id: str, version: str = "latest") -> bool:
        """Manually evict model from cache"""
        try:
            cache_key = f"{model_id}:{version}"
            
            # Remove from all cache levels
            evicted = False
            
            if cache_key in self.l1_cache:
                del self.l1_cache[cache_key]
                evicted = True
            
            if cache_key in self.l2_cache:
                file_path = self.l2_cache[cache_key]
                if Path(file_path).exists():
                    Path(file_path).unlink()
                del self.l2_cache[cache_key]
                evicted = True
            
            if cache_key in self.cache_entries:
                del self.cache_entries[cache_key]
            
            if evicted:
                logger.info(f"🗑️ Evicted model: {model_id}")
            
            return evicted
            
        except Exception as e:
            logger.error(f"❌ Error evicting model {model_id}: {e}")
            return False
    
    async def _get_from_l1(self, cache_key: str) -> Optional[Any]:
        """Get model from L1 cache"""
        try:
            if cache_key in self.l1_cache:
                # Move to end (LRU)
                model = self.l1_cache.pop(cache_key)
                self.l1_cache[cache_key] = model
                return model
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting from L1 cache: {e}")
            return None
    
    async def _get_from_l2(self, cache_key: str) -> Optional[Any]:
        """Get model from L2 cache"""
        try:
            if cache_key in self.l2_cache:
                file_path = self.l2_cache[cache_key]
                if Path(file_path).exists():
                    with open(file_path, 'rb') as f:
                        compressed_data = f.read()
                        data = zlib.decompress(compressed_data)
                        return pickle.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting from L2 cache: {e}")
            return None
    
    async def _load_model(self, model_id: str, version: str) -> Optional[Any]:
        """Load model from storage"""
        try:
            # Simulate model loading
            # In practice, this would load from model registry
            await asyncio.sleep(0.1)  # Simulate loading time
            
            model_data = {
                'model_id': model_id,
                'version': version,
                'data': f"model_data_{model_id}_{version}",
                'loaded_at': datetime.utcnow().isoformat()
            }
            
            return model_data
            
        except Exception as e:
            logger.error(f"❌ Error loading model {model_id}: {e}")
            return None
    
    async def _store_in_l1(self, cache_key -> None: str, model -> None: Any, priority -> None: float = 1.0) -> None:
        """Store model in L1 cache"""
        try:
            # Check if eviction needed
            if len(self.l1_cache) >= self.l1_max_size:
                await self._evict_from_l1()
            
            self.l1_cache[cache_key] = model
            
            # Update cache entry
            if cache_key not in self.cache_entries:
                self.cache_entries[cache_key] = CacheEntry(
                    key=cache_key,
                    model_id=cache_key.split(':')[0],
                    version=cache_key.split(':')[1],
                    cache_level=CacheLevel.L1_MEMORY,
                    size=len(str(model)),
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    priority=priority
                )
            else:
                self.cache_entries[cache_key].cache_level = CacheLevel.L1_MEMORY
                self.cache_entries[cache_key].last_accessed = datetime.utcnow()
                self.cache_entries[cache_key].priority = priority
            
        except Exception as e:
            logger.error(f"❌ Error storing in L1 cache: {e}")
    
    async def _store_in_l2(self, cache_key -> None: str, model -> None: Any, priority -> None: float = 1.0) -> None:
        """Store model in L2 cache"""
        try:
            # Serialize and compress
            data = pickle.dumps(model)
            compressed_data = zlib.compress(data)
            
            # Generate file path
            file_name = hashlib.md5(cache_key.encode()).hexdigest() + '.cache'
            file_path = self.cache_dir / file_name
            
            # Write to disk
            with open(file_path, 'wb') as f:
                f.write(compressed_data)
            
            self.l2_cache[cache_key] = str(file_path)
            
            # Update cache entry
            if cache_key not in self.cache_entries:
                self.cache_entries[cache_key] = CacheEntry(
                    key=cache_key,
                    model_id=cache_key.split(':')[0],
                    version=cache_key.split(':')[1],
                    cache_level=CacheLevel.L2_DISK,
                    size=len(compressed_data),
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    priority=priority
                )
            else:
                self.cache_entries[cache_key].cache_level = CacheLevel.L2_DISK
                self.cache_entries[cache_key].last_accessed = datetime.utcnow()
                self.cache_entries[cache_key].priority = priority
            
        except Exception as e:
            logger.error(f"❌ Error storing in L2 cache: {e}")
    
    async def _store_model(
        self,
        cache_key -> None: str,
        model -> None: Any,
        cache_level -> None: CacheLevel,
        creator_type -> None: Optional[str] = None,
        priority -> None: float = 1.0
    ) -> None:
        """Store model in specified cache level"""
        try:
            if cache_level == CacheLevel.L1_MEMORY:
                await self._store_in_l1(cache_key, model, priority)
            elif cache_level == CacheLevel.L2_DISK:
                await self._store_in_l2(cache_key, model, priority)
            
            # Update entry metadata
            if cache_key in self.cache_entries:
                self.cache_entries[cache_key].creator_type = creator_type
            
        except Exception as e:
            logger.error(f"❌ Error storing model: {e}")
    
    async def _determine_cache_level(
        self,
        model_id: str,
        creator_type: Optional[str],
        model: Any
    ) -> CacheLevel:
        """Determine optimal cache level for model"""
        try:
            # Factors to consider:
            # 1. Model size
            # 2. Access frequency
            # 3. Creator type patterns
            # 4. Memory availability
            
            model_size = len(str(model))
            access_freq = len(self.access_patterns.get(model_id, []))
            
            # Creator-specific patterns
            creator_boost = 0
            if creator_type:
                creator_access = len(self.creator_patterns.get(creator_type, {}).get(model_id, []))
                creator_boost = min(creator_access / 10, 1.0)
            
            # Memory availability
            memory_usage = await self._get_memory_usage()
            memory_pressure = memory_usage / self.l1_max_size
            
            # Decision logic
            score = access_freq * 0.4 + creator_boost * 0.3 + (1 - memory_pressure) * 0.3
            
            if score > 0.7 and model_size < 100 * 1024 * 1024:  # 100MB
                return CacheLevel.L1_MEMORY
            elif score > 0.3:
                return CacheLevel.L2_DISK
            else:
                return CacheLevel.L3_DISTRIBUTED
                
        except Exception as e:
            logger.error(f"❌ Error determining cache level: {e}")
            return CacheLevel.L2_DISK
    
    async def _should_promote_to_l1(self, cache_key: str) -> bool:
        """Determine if model should be promoted to L1"""
        try:
            if cache_key not in self.cache_entries:
                return False
            
            entry = self.cache_entries[cache_key]
            
            # Promotion criteria
            high_access = entry.access_count > 5
            recent_access = (datetime.utcnow() - entry.last_accessed).seconds < 300  # 5 minutes
            high_priority = entry.priority > 0.7
            
            return high_access and (recent_access or high_priority)
            
        except Exception as e:
            logger.error(f"❌ Error checking promotion criteria: {e}")
            return False
    
    async def _is_cached(self, cache_key: str) -> bool:
        """Check if model is cached"""
        return (cache_key in self.l1_cache or 
                cache_key in self.l2_cache)
    
    async def _update_access_stats(
        self,
        cache_key -> None: str,
        cache_level -> None: CacheLevel,
        miss -> None: bool = False
    ) -> None:
        """Update access statistics"""
        try:
            # Update cache entry
            if cache_key in self.cache_entries:
                self.cache_entries[cache_key].last_accessed = datetime.utcnow()
                self.cache_entries[cache_key].access_count += 1
            
            # Update metrics
            metrics = self.metrics[cache_level]
            metrics.total_requests += 1
            
            if miss:
                metrics.cache_misses += 1
            else:
                metrics.cache_hits += 1
            
            # Update hit rate
            if metrics.total_requests > 0:
                metrics.hit_rate = metrics.cache_hits / metrics.total_requests
            
        except Exception as e:
            logger.error(f"❌ Error updating access stats: {e}")
    
    async def _evict_from_l1(self) -> None:
        """Evict entries from L1 cache"""
        try:
            if self.eviction_policy == EvictionPolicy.LRU:
                # Remove least recently used
                if self.l1_cache:
                    oldest_key = next(iter(self.l1_cache))
                    del self.l1_cache[oldest_key]
            
            elif self.eviction_policy == EvictionPolicy.LFU:
                # Remove least frequently used
                if self.cache_entries:
                    lfu_key = min(
                        self.cache_entries.keys(),
                        key=lambda k: self.cache_entries[k].access_count
                        if k in self.l1_cache else float('inf')
                    )
                    if lfu_key in self.l1_cache:
                        del self.l1_cache[lfu_key]
            
            elif self.eviction_policy == EvictionPolicy.PRIORITY:
                # Remove lowest priority
                if self.cache_entries:
                    low_priority_key = min(
                        self.cache_entries.keys(),
                        key=lambda k: self.cache_entries[k].priority
                        if k in self.l1_cache else float('inf')
                    )
                    if low_priority_key in self.l1_cache:
                        del self.l1_cache[low_priority_key]
            
        except Exception as e:
            logger.error(f"❌ Error evicting from L1: {e}")
    
    async def _cleanup_expired_entries(self) -> int:
        """Clean up expired cache entries"""
        try:
            current_time = datetime.utcnow()
            expired_keys = []
            
            for key, entry in self.cache_entries.items():
                if entry.ttl:
                    expiry_time = entry.created_at + timedelta(seconds=entry.ttl)
                    if current_time > expiry_time:
                        expired_keys.append(key)
            
            for key in expired_keys:
                await self.evict_model(key.split(':')[0], key.split(':')[1])
            
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired entries: {e}")
            return 0
    
    async def _optimize_l1_cache(self) -> Dict[str, int]:
        """Optimize L1 cache"""
        try:
            results = {'promoted_entries': 0, 'memory_freed': 0}
            
            # Check for promotion candidates from L2
            for key in list(self.l2_cache.keys()):
                if await self._should_promote_to_l1(key):
                    model = await self._get_from_l2(key)
                    if model:
                        await self._store_in_l1(key, model)
                        results['promoted_entries'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error optimizing L1 cache: {e}")
            return {'promoted_entries': 0, 'memory_freed': 0}
    
    async def _optimize_l2_cache(self) -> Dict[str, int]:
        """Optimize L2 cache"""
        try:
            results = {'disk_freed': 0}
            
            # Check disk usage and clean if needed
            disk_usage = await self._get_disk_usage()
            if disk_usage > self.l2_max_size * 0.9:  # 90% threshold
                # Remove least accessed entries
                sorted_entries = sorted(
                    [entry for entry in self.cache_entries.values() 
                     if entry.cache_level == CacheLevel.L2_DISK],
                    key=lambda e: e.last_accessed
                )
                
                for entry in sorted_entries[:10]:  # Remove oldest 10
                    await self.evict_model(entry.model_id, entry.version)
                    results['disk_freed'] += entry.size
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error optimizing L2 cache: {e}")
            return {'disk_freed': 0}
    
    async def _predictive_preloading(self) -> int:
        """Predict and preload models"""
        try:
            preloaded = 0
            current_time = datetime.utcnow()
            
            # Analyze access patterns
            for model_id, accesses in self.access_patterns.items():
                if len(accesses) < 3:
                    continue
                
                # Simple pattern: if accessed regularly, predict next access
                recent_accesses = [a for a in accesses if (current_time - a).seconds < 3600]
                if len(recent_accesses) >= 2:
                    cache_key = f"{model_id}:latest"
                    if not await self._is_cached(cache_key):
                        success = await self.preload_model(model_id, priority=0.6)
                        if success:
                            preloaded += 1
            
            return preloaded
            
        except Exception as e:
            logger.error(f"❌ Error in predictive preloading: {e}")
            return 0
    
    async def _get_memory_usage(self) -> int:
        """Get current memory usage"""
        try:
            return sum(len(str(model)) for model in self.l1_cache.values())
        except:
            return 0
    
    async def _get_disk_usage(self) -> int:
        """Get current disk usage"""
        try:
            total_size = 0
            for file_path in self.l2_cache.values():
                if Path(file_path).exists():
                    total_size += Path(file_path).stat().st_size
            return total_size
        except:
            return 0
    
    async def _get_top_accessed_models(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top accessed models"""
        try:
            sorted_entries = sorted(
                self.cache_entries.values(),
                key=lambda e: e.access_count,
                reverse=True
            )
            
            return [
                {
                    'model_id': entry.model_id,
                    'version': entry.version,
                    'access_count': entry.access_count,
                    'cache_level': entry.cache_level.value,
                    'last_accessed': entry.last_accessed.isoformat()
                }
                for entry in sorted_entries[:limit]
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting top accessed models: {e}")
            return []
    
    async def _get_creator_access_patterns(self) -> Dict[str, Dict[str, int]]:
        """Get creator access patterns"""
        try:
            patterns = {}
            
            for creator_type, models in self.creator_patterns.items():
                patterns[creator_type] = {}
                for model_id, accesses in models.items():
                    patterns[creator_type][model_id] = len(accesses)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Error getting creator patterns: {e}")
            return {}
    
    async def _update_cache_metrics(self) -> None:
        """Update cache metrics"""
        try:
            for level in CacheLevel:
                metrics = self.metrics[level]
                
                if level == CacheLevel.L1_MEMORY:
                    metrics.memory_usage = await self._get_memory_usage()
                elif level == CacheLevel.L2_DISK:
                    metrics.disk_usage = await self._get_disk_usage()
                
        except Exception as e:
            logger.error(f"❌ Error updating cache metrics: {e}")


# Global instance
cache_optimizer = ModelCachingOptimizer()


async def main() -> None:
    """Test the Model Caching Optimizer"""
    optimizer = ModelCachingOptimizer()
    
    print("📦 Testing Model Caching Optimizer...")
    
    # Test model caching
    model1 = await optimizer.get_model("creator-classifier", "1.0.0", "musician")
    print(f"Model 1 loaded: {model1 is not None}")
    
    model2 = await optimizer.get_model("creator-classifier", "1.0.0", "musician")
    print(f"Model 2 cached: {model2 is not None}")
    
    # Test preloading
    success = await optimizer.preload_model("content-analyzer", "1.0.0", "blogger", priority=0.8)
    print(f"Preload success: {success}")
    
    # Test optimization
    results = await optimizer.optimize_cache()
    print(f"Optimization results: {results}")
    
    # Test statistics
    stats = await optimizer.get_cache_stats()
    print(f"Cache stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())