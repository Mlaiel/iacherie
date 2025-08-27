"""
Advanced Memory Cache Implementation for IA Influencer Agent Platform
Enterprise-grade in-memory caching with multiple eviction policies, compression, and monitoring

Business Logic Integration:
- Creator content caching with tenant isolation
- AI processing result caching for faster content analysis
- Revenue tracking and analytics caching
- Content protection and fingerprint caching
- Platform API response caching

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
      Microservices Architect + Audio Processing Expert + DevOps Engineer + IA Prompt Engineer
"""

import asyncio
import logging
import threading
import time
import json
import pickle
import gzip
import hashlib
import uuid
from typing import Any, Dict, Optional, List, Callable, TypeVar, Generic, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
from enum import Enum
import weakref
import gc
import traceback
from concurrent.futures import ThreadPoolExecutor
import psutil
import zlib

logger = logging.getLogger(__name__)

T = TypeVar('T')

class EvictionPolicy(Enum):
    """Advanced cache eviction policies for IA Influencer Agent"""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used  
    TTL = "ttl"              # Time To Live
    FIFO = "fifo"            # First In First Out
    RANDOM = "random"        # Random eviction
    ADAPTIVE = "adaptive"    # AI-driven adaptive eviction
    CREATOR_PRIORITY = "creator_priority"  # Creator-based priority
    CONTENT_VALUE = "content_value"        # Content monetization value

class CompressionType(Enum):
    """Compression algorithms for memory optimization"""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    PICKLE = "pickle"

class CacheNamespace(Enum):
    """Cache namespaces for IA Influencer Agent business logic"""
    CREATOR_CONTENT = "creator_content"
    AI_PROCESSING = "ai_processing"
    CONTENT_PROTECTION = "content_protection"
    REVENUE_ANALYTICS = "revenue_analytics"
    PLATFORM_API = "platform_api"
    AUDIO_FINGERPRINTS = "audio_fingerprints"
    ML_MODELS = "ml_models"
    USER_SESSIONS = "user_sessions"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"

class CachePriority(Enum):
    """Cache priority levels for intelligent eviction"""
    CRITICAL = 5    # Revenue-critical data
    HIGH = 4        # User-facing content
    MEDIUM = 3      # Processing results
    LOW = 2         # Analytics data
    BACKGROUND = 1  # Background tasks

@dataclass
class CacheEntry:
    """Enhanced cache entry with comprehensive metadata for IA Influencer Agent"""
    value: Any
    created_at: float
    accessed_at: float
    access_count: int = 0
    ttl: Optional[float] = None
    size: int = 0
    
    # Business logic metadata
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    namespace: CacheNamespace = CacheNamespace.CREATOR_CONTENT
    priority: CachePriority = CachePriority.MEDIUM
    monetization_value: float = 0.0
    compressed: bool = False
    compression_type: CompressionType = CompressionType.NONE
    
    # Analytics metadata
    revenue_impact: float = 0.0
    processing_cost: float = 0.0
    cache_hit_value: float = 0.0
    last_modified_at: Optional[float] = None
    tags: Set[str] = field(default_factory=set)
    
    # Performance metadata
    serialization_time: float = 0.0
    deserialization_time: float = 0.0
    compression_ratio: float = 1.0
    access_pattern: List[float] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    @property
    def age(self) -> float:
        """Get entry age in seconds"""
        return time.time() - self.created_at
    
    @property
    def time_since_access(self) -> float:
        """Time since last access"""
        return time.time() - self.accessed_at
    
    @property
    def access_frequency(self) -> float:
        """Calculate access frequency (accesses per hour)"""
        if self.age <= 0:
            return float('inf')
        return (self.access_count / (self.age / 3600))
    
    @property
    def value_score(self) -> float:
        """Calculate overall value score for eviction decisions"""
        base_score = self.priority.value * 10
        
        # Factor in monetization value
        monetization_bonus = min(self.monetization_value * 5, 20)
        
        # Factor in access frequency
        frequency_bonus = min(self.access_frequency, 10)
        
        # Factor in recency
        recency_factor = max(0, 10 - (self.time_since_access / 3600))
        
        return base_score + monetization_bonus + frequency_bonus + recency_factor
    
    def update_access(self):
        """Update access metadata"""
        current_time = time.time()
        self.accessed_at = current_time
        self.access_count += 1
        
        # Track access pattern (keep last 10 accesses)
        self.access_pattern.append(current_time)
        if len(self.access_pattern) > 10:
            self.access_pattern.pop(0)
    
    def add_tag(self, tag: str):
        """Add tag to entry"""
        self.tags.add(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if entry has tag"""
        return tag in self.tags

@dataclass 
class CacheConfig:
    """Configuration for enterprise memory cache"""
    max_size: int = 10000
    max_memory_bytes: int = 500 * 1024 * 1024  # 500MB
    eviction_policy: EvictionPolicy = EvictionPolicy.ADAPTIVE
    default_ttl: Optional[float] = None
    cleanup_interval: float = 60.0
    
    # Compression settings
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress items > 1KB
    compression_type: CompressionType = CompressionType.ZLIB
    
    # Performance settings
    enable_async_cleanup: bool = True
    max_cleanup_threads: int = 2
    memory_pressure_threshold: float = 0.8  # 80% memory usage
    
    # Business logic settings
    creator_isolation: bool = True
    namespace_isolation: bool = True
    priority_based_eviction: bool = True
    revenue_aware_caching: bool = True
    
    # Monitoring settings
    enable_metrics: bool = True
    slow_operation_threshold: float = 0.1  # 100ms
    health_check_interval: float = 300.0  # 5 minutes

class CacheMetrics:
    """Advanced metrics tracking for cache performance"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.compressions = 0
        self.decompressions = 0
        
        # Business metrics
        self.revenue_impact_saved = 0.0
        self.processing_cost_saved = 0.0
        self.creator_cache_hits = defaultdict(int)
        self.namespace_stats = defaultdict(lambda: {'hits': 0, 'misses': 0, 'size': 0})
        
        # Performance metrics
        self.total_operation_time = 0.0
        self.slow_operations = 0
        self.memory_pressure_events = 0
        self.compression_ratio_total = 0.0
        self.compression_time_total = 0.0
        
        # System metrics
        self.start_time = time.time()
        self.last_reset = time.time()
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def operations_per_second(self) -> float:
        """Calculate operations per second"""
        duration = time.time() - self.start_time
        total_ops = self.hits + self.misses + self.sets + self.deletes
        return total_ops / duration if duration > 0 else 0.0
    
    @property
    def average_compression_ratio(self) -> float:
        """Calculate average compression ratio"""
        return self.compression_ratio_total / max(1, self.compressions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'cache_stats': {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'deletes': self.deletes,
                'evictions': self.evictions,
                'hit_rate': self.hit_rate,
                'operations_per_second': self.operations_per_second
            },
            'business_metrics': {
                'revenue_impact_saved': self.revenue_impact_saved,
                'processing_cost_saved': self.processing_cost_saved,
                'top_creators': dict(sorted(self.creator_cache_hits.items(), 
                                          key=lambda x: x[1], reverse=True)[:10])
            },
            'performance_metrics': {
                'slow_operations': self.slow_operations,
                'memory_pressure_events': self.memory_pressure_events,
                'average_compression_ratio': self.average_compression_ratio,
                'compression_time_avg': self.compression_time_total / max(1, self.compressions)
            },
            'namespace_stats': dict(self.namespace_stats)
        }

class EnterpriseMemoryCache(Generic[T]):
    """
    Enterprise-grade memory cache for IA Influencer Agent Platform
    
    Features:
    - Multi-tenant creator isolation
    - Business logic aware caching 
    - Revenue-based prioritization
    - Advanced compression and optimization
    - Real-time performance monitoring
    - AI-driven adaptive eviction
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        
        # Core storage
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order = OrderedDict()  # For LRU
        self._frequency_counter: Dict[str, int] = {}  # For LFU
        
        # Business logic storage
        self._creator_cache: Dict[str, Set[str]] = defaultdict(set)  # creator_id -> keys
        self._namespace_cache: Dict[CacheNamespace, Set[str]] = defaultdict(set)
        self._priority_queues: Dict[CachePriority, Set[str]] = defaultdict(set)
        
        # Threading and async
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_cleanup_threads)
        
        # Metrics and monitoring
        self.metrics = CacheMetrics()
        self._health_status = {'status': 'healthy', 'last_check': time.time()}
        
        # Background tasks
        self._cleanup_task = None
        self._health_task = None
        self._stop_tasks = threading.Event()
        
        # Compression cache
        self._compression_cache: Dict[str, bytes] = {}
        
        self._start_background_tasks()
        
        logger.info(f"EnterpriseMemoryCache initialized - Policy: {self.config.eviction_policy}")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        def cleanup_worker():
            while not self._stop_tasks.wait(self.config.cleanup_interval):
                try:
                    if self.config.enable_async_cleanup:
                        self._async_cleanup()
                    else:
                        self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
        
        def health_worker():
            while not self._stop_tasks.wait(self.config.health_check_interval):
                try:
                    self._health_check()
                except Exception as e:
                    logger.error(f"Health check error: {e}")
        
        self._cleanup_task = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_task.start()
        
        self._health_task = threading.Thread(target=health_worker, daemon=True) 
        self._health_task.start()
    
    def _get_object_size(self, obj: Any) -> int:
        """Advanced object size calculation with caching awareness"""
        try:
            if hasattr(obj, '__sizeof__'):
                size = obj.__sizeof__()
            else:
                import sys
                size = sys.getsizeof(obj)
            
            # Enhanced recursive size calculation
            if isinstance(obj, dict):
                size += sum(self._get_object_size(k) + self._get_object_size(v) 
                           for k, v in obj.items())
            elif isinstance(obj, (list, tuple)):
                size += sum(self._get_object_size(item) for item in obj)
            elif isinstance(obj, set):
                size += sum(self._get_object_size(item) for item in obj)
            elif isinstance(obj, str):
                size = len(obj.encode('utf-8'))
            elif hasattr(obj, '__dict__'):
                size += self._get_object_size(obj.__dict__)
                
            return max(size, 64)  # Minimum size estimate
        except Exception:
            return 256  # Conservative estimate for unknown objects
    
    def _compress_value(self, value: Any) -> Tuple[Any, CompressionType, float, float]:
        """Compress value if beneficial"""
        if not self.config.enable_compression:
            return value, CompressionType.NONE, 1.0, 0.0
        
        start_time = time.time()
        
        try:
            # Serialize first
            if isinstance(value, (str, bytes)):
                data = value.encode('utf-8') if isinstance(value, str) else value
            else:
                data = pickle.dumps(value)
            
            original_size = len(data)
            
            # Skip compression for small objects
            if original_size < self.config.compression_threshold:
                compression_time = time.time() - start_time
                return value, CompressionType.NONE, 1.0, compression_time
            
            # Choose compression algorithm
            if self.config.compression_type == CompressionType.GZIP:
                compressed = gzip.compress(data)
            elif self.config.compression_type == CompressionType.ZLIB:
                compressed = zlib.compress(data)
            else:
                compressed = data
            
            compressed_size = len(compressed)
            compression_ratio = original_size / compressed_size
            compression_time = time.time() - start_time
            
            # Only use compression if it provides significant benefit
            if compression_ratio > 1.2:  # At least 20% reduction
                self.metrics.compressions += 1
                self.metrics.compression_ratio_total += compression_ratio
                self.metrics.compression_time_total += compression_time
                
                return compressed, self.config.compression_type, compression_ratio, compression_time
            else:
                return value, CompressionType.NONE, 1.0, compression_time
                
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            compression_time = time.time() - start_time
            return value, CompressionType.NONE, 1.0, compression_time
    
    def _decompress_value(self, compressed_value: Any, compression_type: CompressionType) -> Tuple[Any, float]:
        """Decompress value"""
        if compression_type == CompressionType.NONE:
            return compressed_value, 0.0
        
        start_time = time.time()
        
        try:
            if compression_type == CompressionType.GZIP:
                data = gzip.decompress(compressed_value)
            elif compression_type == CompressionType.ZLIB:
                data = zlib.decompress(compressed_value)
            else:
                data = compressed_value
            
            # Deserialize if needed
            try:
                value = pickle.loads(data)
            except:
                value = data.decode('utf-8') if isinstance(data, bytes) else data
            
            decompression_time = time.time() - start_time
            self.metrics.decompressions += 1
            
            return value, decompression_time
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            decompression_time = time.time() - start_time
            return compressed_value, decompression_time
    
    def _update_access_tracking(self, key: str, entry: CacheEntry):
        """Update access tracking for various eviction policies"""
        entry.update_access()
        
        if self.config.eviction_policy == EvictionPolicy.LRU:
            with self._lock:
                if key in self._access_order:
                    del self._access_order[key]
                self._access_order[key] = True
        
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            with self._lock:
                self._frequency_counter[key] = self._frequency_counter.get(key, 0) + 1
    
    def _calculate_memory_pressure(self) -> float:
        """Calculate current memory pressure"""
        current_memory = sum(entry.size for entry in self._cache.values())
        return current_memory / self.config.max_memory_bytes
    
    def _should_evict(self) -> bool:
        """Intelligent eviction decision"""
        size_pressure = len(self._cache) >= self.config.max_size
        memory_pressure = self._calculate_memory_pressure() >= self.config.memory_pressure_threshold
        
        return size_pressure or memory_pressure
    
    def _select_eviction_candidate(self) -> Optional[str]:
        """Advanced eviction candidate selection"""
        if not self._cache:
            return None
        
        with self._lock:
            if self.config.eviction_policy == EvictionPolicy.ADAPTIVE:
                return self._adaptive_eviction_selection()
            
            elif self.config.eviction_policy == EvictionPolicy.CREATOR_PRIORITY:
                return self._creator_priority_eviction()
            
            elif self.config.eviction_policy == EvictionPolicy.CONTENT_VALUE:
                return self._content_value_eviction()
            
            elif self.config.eviction_policy == EvictionPolicy.LRU:
                return next(iter(self._access_order)) if self._access_order else None
            
            elif self.config.eviction_policy == EvictionPolicy.LFU:
                if self._frequency_counter:
                    return min(self._frequency_counter.keys(), 
                             key=lambda k: self._frequency_counter[k])
                return next(iter(self._cache))
            
            elif self.config.eviction_policy == EvictionPolicy.TTL:
                # Find entry with shortest remaining TTL
                candidates = []
                current_time = time.time()
                
                for key, entry in self._cache.items():
                    if entry.ttl is not None:
                        if entry.is_expired:
                            return key
                        remaining_ttl = (entry.created_at + entry.ttl) - current_time
                        candidates.append((key, remaining_ttl))
                
                if candidates:
                    return min(candidates, key=lambda x: x[1])[0]
                return next(iter(self._cache))
            
            elif self.config.eviction_policy == EvictionPolicy.FIFO:
                return min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            
            elif self.config.eviction_policy == EvictionPolicy.RANDOM:
                import random
                return random.choice(list(self._cache.keys()))
            
            # Default fallback
            return next(iter(self._cache))
    
    def _adaptive_eviction_selection(self) -> Optional[str]:
        """AI-driven adaptive eviction using value scoring"""
        if not self._cache:
            return None
        
        # Calculate value scores for all entries
        scored_entries = []
        for key, entry in self._cache.items():
            score = entry.value_score
            scored_entries.append((key, score))
        
        # Sort by score (lowest first for eviction)
        scored_entries.sort(key=lambda x: x[1])
        
        return scored_entries[0][0] if scored_entries else None
    
    def _creator_priority_eviction(self) -> Optional[str]:
        """Evict based on creator priority and usage patterns"""
        # Prioritize evicting content from creators with lower engagement
        creator_scores = {}
        
        for creator_id, keys in self._creator_cache.items():
            if not keys:
                continue
            
            total_accesses = sum(self._cache[key].access_count for key in keys if key in self._cache)
            total_revenue = sum(self._cache[key].monetization_value for key in keys if key in self._cache)
            avg_age = sum(self._cache[key].age for key in keys if key in self._cache) / len(keys)
            
            # Lower score = higher eviction priority
            score = (total_accesses * 0.4) + (total_revenue * 0.4) - (avg_age * 0.2)
            creator_scores[creator_id] = score
        
        if not creator_scores:
            return next(iter(self._cache))
        
        # Find creator with lowest score
        lowest_creator = min(creator_scores.keys(), key=lambda c: creator_scores[c])
        creator_keys = self._creator_cache[lowest_creator]
        
        if creator_keys:
            # Select oldest entry from this creator
            oldest_key = min(creator_keys, key=lambda k: self._cache[k].created_at if k in self._cache else float('inf'))
            return oldest_key if oldest_key in self._cache else None
        
        return next(iter(self._cache))
    
    def _content_value_eviction(self) -> Optional[str]:
        """Evict based on content monetization value"""
        if not self._cache:
            return None
        
        # Find entry with lowest value score
        return min(self._cache.keys(), key=lambda k: self._cache[k].value_score)
    
    def _evict_entries(self, target_count: int = 1):
        """Evict multiple entries efficiently"""
        evicted_count = 0
        
        while evicted_count < target_count and self._cache and self._should_evict():
            key = self._select_eviction_candidate()
            if key and key in self._cache:
                entry = self._cache[key]
                
                # Track business impact of eviction
                self.metrics.revenue_impact_saved -= entry.revenue_impact
                
                self._remove_entry(key)
                evicted_count += 1
                
                # Prevent infinite loops
                if evicted_count > 100:
                    break
        
        if evicted_count > 0:
            self.metrics.evictions += evicted_count
            logger.debug(f"Evicted {evicted_count} cache entries")
    
    def _remove_entry(self, key: str) -> bool:
        """Remove entry and update all tracking structures"""
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        
        # Remove from main cache
        del self._cache[key]
        
        # Update creator tracking
        if entry.creator_id:
            self._creator_cache[entry.creator_id].discard(key)
            if not self._creator_cache[entry.creator_id]:
                del self._creator_cache[entry.creator_id]
        
        # Update namespace tracking
        self._namespace_cache[entry.namespace].discard(key)
        if not self._namespace_cache[entry.namespace]:
            del self._namespace_cache[entry.namespace]
        
        # Update priority tracking
        self._priority_queues[entry.priority].discard(key)
        if not self._priority_queues[entry.priority]:
            del self._priority_queues[entry.priority]
        
        # Update eviction policy tracking
        if key in self._access_order:
            del self._access_order[key]
        if key in self._frequency_counter:
            del self._frequency_counter[key]
        
        # Remove compressed data
        if key in self._compression_cache:
            del self._compression_cache[key]
        
        return True
    
    def _async_cleanup(self):
        """Asynchronous cleanup of expired entries"""
        def cleanup_batch():
            expired_keys = []
            current_time = time.time()
            
            with self._lock:
                # Collect expired keys in batches
                for key, entry in list(self._cache.items())[:1000]:  # Process in batches
                    if entry.is_expired:
                        expired_keys.append(key)
                    
                    if len(expired_keys) >= 100:  # Batch size
                        break
            
            # Remove expired entries
            removed_count = 0
            for key in expired_keys:
                if self._remove_entry(key):
                    removed_count += 1
            
            return removed_count
        
        future = self._executor.submit(cleanup_batch)
        try:
            removed_count = future.result(timeout=5.0)
            if removed_count > 0:
                logger.debug(f"Async cleanup removed {removed_count} expired entries")
        except Exception as e:
            logger.warning(f"Async cleanup failed: {e}")
    
    def _cleanup_expired(self):
        """Synchronous cleanup of expired entries"""
        expired_keys = []
        current_time = time.time()
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
        
        removed_count = 0
        for key in expired_keys:
            if self._remove_entry(key):
                removed_count += 1
        
        if removed_count > 0:
            logger.debug(f"Cleanup removed {removed_count} expired entries")
    
    def _health_check(self):
        """Comprehensive health check"""
        try:
            memory_pressure = self._calculate_memory_pressure()
            
            # Check memory pressure
            if memory_pressure > 0.9:
                self.metrics.memory_pressure_events += 1
                logger.warning(f"High memory pressure: {memory_pressure:.2%}")
                
                # Aggressive cleanup
                if self.config.eviction_policy == EvictionPolicy.ADAPTIVE:
                    self._evict_entries(target_count=max(10, len(self._cache) // 20))
            
            # Check system memory
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory_percent = process.memory_percent()
            
            health_status = {
                'status': 'healthy',
                'last_check': time.time(),
                'memory_pressure': memory_pressure,
                'system_memory_percent': system_memory_percent,
                'cache_size': len(self._cache),
                'hit_rate': self.metrics.hit_rate,
                'operations_per_second': self.metrics.operations_per_second
            }
            
            # Determine health status
            if memory_pressure > 0.9 or system_memory_percent > 80:
                health_status['status'] = 'warning'
            if memory_pressure > 0.95 or system_memory_percent > 90:
                health_status['status'] = 'critical'
            
            self._health_status = health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._health_status = {
                'status': 'error',
                'last_check': time.time(),
                'error': str(e)
            }
    
    # Public API methods
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get value from cache with comprehensive tracking"""
        operation_start = time.time()
        
        try:
            with self._lock:
                if key not in self._cache:
                    self.metrics.misses += 1
                    return default
                
                entry = self._cache[key]
                
                # Check expiration
                if entry.is_expired:
                    self._remove_entry(key)
                    self.metrics.misses += 1
                    return default
                
                # Update access tracking
                self._update_access_tracking(key, entry)
                
                # Decompress if needed
                value, decompression_time = self._decompress_value(
                    entry.value, entry.compression_type
                )
                entry.deserialization_time = decompression_time
                
                # Update business metrics
                self.metrics.hits += 1
                self.metrics.revenue_impact_saved += entry.revenue_impact
                self.metrics.processing_cost_saved += entry.processing_cost
                
                if entry.creator_id:
                    self.metrics.creator_cache_hits[entry.creator_id] += 1
                
                namespace_stat = self.metrics.namespace_stats[entry.namespace]
                namespace_stat['hits'] += 1
                
                operation_time = time.time() - operation_start
                self.metrics.total_operation_time += operation_time
                
                if operation_time > self.config.slow_operation_threshold:
                    self.metrics.slow_operations += 1
                    logger.warning(f"Slow get operation: {operation_time:.3f}s for key {key}")
                
                return value
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.misses += 1
            return default
    
    def set(self, 
            key: str, 
            value: T, 
            ttl: Optional[float] = None,
            creator_id: Optional[str] = None,
            content_type: Optional[str] = None,
            namespace: CacheNamespace = CacheNamespace.CREATOR_CONTENT,
            priority: CachePriority = CachePriority.MEDIUM,
            monetization_value: float = 0.0,
            revenue_impact: float = 0.0,
            processing_cost: float = 0.0,
            tags: Optional[Set[str]] = None) -> bool:
        """Set value in cache with business logic integration"""
        
        operation_start = time.time()
        
        try:
            ttl = ttl or self.config.default_ttl
            current_time = time.time()
            
            # Compress value if beneficial
            compressed_value, compression_type, compression_ratio, compression_time = self._compress_value(value)
            
            # Calculate size
            value_size = self._get_object_size(compressed_value)
            
            with self._lock:
                # Remove existing entry if present
                if key in self._cache:
                    self._remove_entry(key)
                
                # Check if we need to evict
                estimated_memory = sum(entry.size for entry in self._cache.values()) + value_size
                if (len(self._cache) >= self.config.max_size or 
                    estimated_memory >= self.config.max_memory_bytes):
                    
                    # Calculate how many entries to evict
                    target_evictions = max(1, int(self.config.max_size * 0.1))  # Evict 10%
                    self._evict_entries(target_count=target_evictions)
                
                # Create new entry with comprehensive metadata
                entry = CacheEntry(
                    value=compressed_value,
                    created_at=current_time,
                    accessed_at=current_time,
                    access_count=1,
                    ttl=ttl,
                    size=value_size,
                    creator_id=creator_id,
                    content_type=content_type,
                    namespace=namespace,
                    priority=priority,
                    monetization_value=monetization_value,
                    revenue_impact=revenue_impact,
                    processing_cost=processing_cost,
                    compressed=compression_type != CompressionType.NONE,
                    compression_type=compression_type,
                    compression_ratio=compression_ratio,
                    serialization_time=compression_time,
                    tags=tags or set(),
                    last_modified_at=current_time
                )
                
                # Store entry
                self._cache[key] = entry
                
                # Update tracking structures
                if creator_id:
                    self._creator_cache[creator_id].add(key)
                
                self._namespace_cache[namespace].add(key)
                self._priority_queues[priority].add(key)
                
                # Update eviction policy tracking
                self._update_access_tracking(key, entry)
                
                # Update metrics
                self.metrics.sets += 1
                namespace_stat = self.metrics.namespace_stats[namespace]
                namespace_stat['size'] += 1
                
                operation_time = time.time() - operation_start
                self.metrics.total_operation_time += operation_time
                
                if operation_time > self.config.slow_operation_threshold:
                    self.metrics.slow_operations += 1
                    logger.warning(f"Slow set operation: {operation_time:.3f}s for key {key}")
                
                logger.debug(f"Cached {key} (size: {value_size}, compressed: {entry.compressed}, "
                           f"ratio: {compression_ratio:.2f}, creator: {creator_id}, namespace: {namespace.value})")
                
                return True
                
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if self._remove_entry(key):
                self.metrics.deletes += 1
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            if entry.is_expired:
                self._remove_entry(key)
                return False
            
            return True
    
    def touch(self, key: str, ttl: Optional[float] = None) -> bool:
        """Update TTL and access time for existing key"""
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            if entry.is_expired:
                self._remove_entry(key)
                return False
            
            # Update TTL if provided
            if ttl is not None:
                entry.ttl = ttl
                entry.created_at = time.time()  # Reset creation time for new TTL
            
            # Update access tracking
            self._update_access_tracking(key, entry)
            
            return True
    
    def increment(self, key: str, amount: Union[int, float] = 1, 
                  default: Union[int, float] = 0) -> Union[int, float]:
        """Increment numeric value"""
        with self._lock:
            if key not in self._cache:
                self.set(key, default + amount)
                return default + amount
            
            entry = self._cache[key]
            if entry.is_expired:
                self._remove_entry(key)
                self.set(key, default + amount)
                return default + amount
            
            # Decompress and update value
            current_value, _ = self._decompress_value(entry.value, entry.compression_type)
            
            if not isinstance(current_value, (int, float)):
                raise TypeError(f"Cannot increment non-numeric value: {type(current_value)}")
            
            new_value = current_value + amount
            
            # Compress and store updated value
            compressed_value, compression_type, compression_ratio, compression_time = self._compress_value(new_value)
            
            entry.value = compressed_value
            entry.compression_type = compression_type
            entry.compression_ratio = compression_ratio
            entry.last_modified_at = time.time()
            
            self._update_access_tracking(key, entry)
            
            return new_value
    
    # Business logic methods for IA Influencer Agent
    
    def get_creator_stats(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a creator"""
        with self._lock:
            creator_keys = self._creator_cache.get(creator_id, set())
            
            if not creator_keys:
                return {
                    'creator_id': creator_id,
                    'total_entries': 0,
                    'total_size': 0,
                    'cache_hits': 0,
                    'message': 'No cached content found'
                }
            
            # Collect metrics
            total_size = 0
            total_accesses = 0
            total_monetization = 0.0
            content_types = defaultdict(int)
            namespaces = defaultdict(int)
            
            for key in creator_keys:
                if key in self._cache:
                    entry = self._cache[key]
                    total_size += entry.size
                    total_accesses += entry.access_count
                    total_monetization += entry.monetization_value
                    
                    if entry.content_type:
                        content_types[entry.content_type] += 1
                    namespaces[entry.namespace.value] += 1
            
            return {
                'creator_id': creator_id,
                'total_entries': len(creator_keys),
                'total_size_mb': total_size / (1024 * 1024),
                'total_accesses': total_accesses,
                'total_monetization_value': total_monetization,
                'cache_hits': self.metrics.creator_cache_hits.get(creator_id, 0),
                'content_types': dict(content_types),
                'namespaces': dict(namespaces),
                'avg_access_frequency': total_accesses / len(creator_keys) if creator_keys else 0
            }
    
    def get_namespace_stats(self, namespace: CacheNamespace) -> Dict[str, Any]:
        """Get statistics for a cache namespace"""
        with self._lock:
            namespace_keys = self._namespace_cache.get(namespace, set())
            namespace_stat = self.metrics.namespace_stats[namespace]
            
            if not namespace_keys:
                return {
                    'namespace': namespace.value,
                    'total_entries': 0,
                    'hits': namespace_stat['hits'],
                    'misses': namespace_stat['misses']
                }
            
            total_size = sum(self._cache[key].size for key in namespace_keys if key in self._cache)
            total_value = sum(self._cache[key].monetization_value for key in namespace_keys if key in self._cache)
            
            return {
                'namespace': namespace.value,
                'total_entries': len(namespace_keys),
                'total_size_mb': total_size / (1024 * 1024),
                'total_monetization_value': total_value,
                'hits': namespace_stat['hits'],
                'misses': namespace_stat['misses'],
                'hit_rate': namespace_stat['hits'] / (namespace_stat['hits'] + namespace_stat['misses']) 
                           if (namespace_stat['hits'] + namespace_stat['misses']) > 0 else 0
            }
    
    def clear_creator_cache(self, creator_id: str) -> int:
        """Clear all cached content for a specific creator"""
        with self._lock:
            creator_keys = self._creator_cache.get(creator_id, set()).copy()
            cleared_count = 0
            
            for key in creator_keys:
                if self._remove_entry(key):
                    cleared_count += 1
            
            if creator_id in self._creator_cache:
                del self._creator_cache[creator_id]
            
            logger.info(f"Cleared {cleared_count} cache entries for creator {creator_id}")
            return cleared_count
    
    def clear_namespace(self, namespace: CacheNamespace) -> int:
        """Clear all entries in a specific namespace"""
        with self._lock:
            namespace_keys = self._namespace_cache.get(namespace, set()).copy()
            cleared_count = 0
            
            for key in namespace_keys:
                if self._remove_entry(key):
                    cleared_count += 1
            
            if namespace in self._namespace_cache:
                del self._namespace_cache[namespace]
            
            logger.info(f"Cleared {cleared_count} cache entries from namespace {namespace.value}")
            return cleared_count
    
    def get_priority_queue_stats(self) -> Dict[CachePriority, Dict[str, Any]]:
        """Get statistics for each priority queue"""
        stats = {}
        
        with self._lock:
            for priority, keys in self._priority_queues.items():
                if keys:
                    total_size = sum(self._cache[key].size for key in keys if key in self._cache)
                    total_value = sum(self._cache[key].monetization_value for key in keys if key in self._cache)
                    
                    stats[priority] = {
                        'count': len(keys),
                        'total_size_mb': total_size / (1024 * 1024),
                        'total_monetization_value': total_value,
                        'priority_level': priority.value
                    }
                else:
                    stats[priority] = {
                        'count': 0,
                        'total_size_mb': 0,
                        'total_monetization_value': 0,
                        'priority_level': priority.value
                    }
        
        return stats
    
    def search_by_tags(self, tags: Set[str], match_all: bool = False) -> List[str]:
        """Search cache entries by tags"""
        matching_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired:
                    continue
                
                if match_all:
                    # All tags must be present
                    if tags.issubset(entry.tags):
                        matching_keys.append(key)
                else:
                    # Any tag matches
                    if tags.intersection(entry.tags):
                        matching_keys.append(key)
        
        return matching_keys
    
    def get_memory_breakdown(self) -> Dict[str, Any]:
        """Get detailed memory usage breakdown"""
        breakdown = {
            'total_entries': 0,
            'total_size_mb': 0,
            'by_namespace': {},
            'by_priority': {},
            'by_creator': {},
            'compression_stats': {
                'compressed_entries': 0,
                'uncompressed_entries': 0,
                'total_compression_ratio': 0.0,
                'estimated_savings_mb': 0.0
            }
        }
        
        with self._lock:
            total_size = 0
            total_original_size = 0
            compressed_count = 0
            
            for entry in self._cache.values():
                total_size += entry.size
                breakdown['total_entries'] += 1
                
                # Compression stats
                if entry.compressed:
                    compressed_count += 1
                    original_size = entry.size * entry.compression_ratio
                    total_original_size += original_size
                else:
                    breakdown['compression_stats']['uncompressed_entries'] += 1
                    total_original_size += entry.size
            
            breakdown['total_size_mb'] = total_size / (1024 * 1024)
            breakdown['compression_stats']['compressed_entries'] = compressed_count
            
            if compressed_count > 0:
                compression_savings = total_original_size - total_size
                breakdown['compression_stats']['estimated_savings_mb'] = compression_savings / (1024 * 1024)
                breakdown['compression_stats']['total_compression_ratio'] = total_original_size / total_size
            
            # Namespace breakdown
            for namespace, keys in self._namespace_cache.items():
                namespace_size = sum(self._cache[key].size for key in keys if key in self._cache)
                breakdown['by_namespace'][namespace.value] = {
                    'entries': len(keys),
                    'size_mb': namespace_size / (1024 * 1024)
                }
            
            # Priority breakdown
            for priority, keys in self._priority_queues.items():
                priority_size = sum(self._cache[key].size for key in keys if key in self._cache)
                breakdown['by_priority'][priority.value] = {
                    'entries': len(keys),
                    'size_mb': priority_size / (1024 * 1024)
                }
            
            # Top creators by cache usage
            creator_sizes = {}
            for creator_id, keys in self._creator_cache.items():
                creator_size = sum(self._cache[key].size for key in keys if key in self._cache)
                creator_sizes[creator_id] = creator_size
            
            # Sort and get top 10
            top_creators = sorted(creator_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
            breakdown['by_creator'] = {
                creator_id: {'size_mb': size / (1024 * 1024)}
                for creator_id, size in top_creators
            }
        
        return breakdown
    
    # Standard cache operations
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._frequency_counter.clear()
            self._creator_cache.clear()
            self._namespace_cache.clear()
            self._priority_queues.clear()
            self._compression_cache.clear()
            self.metrics.reset()
    
    def clear_pattern(self, pattern: str):
        """Clear entries matching pattern (simple prefix/suffix matching)"""
        keys_to_remove = []
        
        with self._lock:
            for key in self._cache.keys():
                if pattern.endswith('*'):
                    prefix = pattern[:-1]
                    if key.startswith(prefix):
                        keys_to_remove.append(key)
                elif pattern.startswith('*'):
                    suffix = pattern[1:]
                    if key.endswith(suffix):
                        keys_to_remove.append(key)
                elif key == pattern:
                    keys_to_remove.append(key)
        
        removed_count = 0
        for key in keys_to_remove:
            if self._remove_entry(key):
                removed_count += 1
        
        logger.info(f"Cleared {removed_count} entries matching pattern: {pattern}")
        return removed_count
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            
            matched_keys = []
            for key in self._cache.keys():
                if pattern.endswith('*'):
                    prefix = pattern[:-1]
                    if key.startswith(prefix):
                        matched_keys.append(key)
                elif pattern.startswith('*'):
                    suffix = pattern[1:]
                    if key.endswith(suffix):
                        matched_keys.append(key)
                elif key == pattern:
                    matched_keys.append(key)
            
            return matched_keys
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        base_stats = self.metrics.to_dict()
        
        with self._lock:
            total_entries = len(self._cache)
            current_memory = sum(entry.size for entry in self._cache.values())
            
            additional_stats = {
                'cache_info': {
                    'total_entries': total_entries,
                    'current_memory_mb': current_memory / (1024 * 1024),
                    'memory_utilization': current_memory / self.config.max_memory_bytes,
                    'size_utilization': total_entries / self.config.max_size,
                    'eviction_policy': self.config.eviction_policy.value,
                    'compression_enabled': self.config.enable_compression
                },
                'health_status': self._health_status,
                'memory_breakdown': self.get_memory_breakdown(),
                'priority_stats': self.get_priority_queue_stats()
            }
            
            # Merge stats
            return {**base_stats, **additional_stats}
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about cache entry"""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            return {
                'key': key,
                'created_at': datetime.fromtimestamp(entry.created_at).isoformat(),
                'accessed_at': datetime.fromtimestamp(entry.accessed_at).isoformat(),
                'last_modified_at': datetime.fromtimestamp(entry.last_modified_at).isoformat() if entry.last_modified_at else None,
                'access_count': entry.access_count,
                'ttl': entry.ttl,
                'size_bytes': entry.size,
                'age_seconds': entry.age,
                'time_since_access': entry.time_since_access,
                'is_expired': entry.is_expired,
                'creator_id': entry.creator_id,
                'content_type': entry.content_type,
                'namespace': entry.namespace.value,
                'priority': entry.priority.value,
                'monetization_value': entry.monetization_value,
                'revenue_impact': entry.revenue_impact,
                'processing_cost': entry.processing_cost,
                'compressed': entry.compressed,
                'compression_type': entry.compression_type.value,
                'compression_ratio': entry.compression_ratio,
                'tags': list(entry.tags),
                'value_score': entry.value_score,
                'access_frequency': entry.access_frequency
            }
    
    def __len__(self) -> int:
        """Get number of entries in cache"""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache"""
        return self.exists(key)
    
    def close(self):
        """Close cache and cleanup resources"""
        self._stop_tasks.set()
        
        # Wait for background tasks to complete
        if self._cleanup_task:
            self._cleanup_task.join(timeout=5.0)
        if self._health_task:
            self._health_task.join(timeout=5.0)
        
        # Shutdown executor
        self._executor.shutdown(wait=True)
        
        self.clear()
        logger.info("EnterpriseMemoryCache closed")

# Specialized cache implementations for IA Influencer Agent

class CreatorContentCache(EnterpriseMemoryCache[T]):
    """Specialized cache for creator content with content-aware policies"""
    
    def __init__(self, max_size: int = 5000, **kwargs):
        config = CacheConfig(
            max_size=max_size,
            max_memory_bytes=200 * 1024 * 1024,  # 200MB
            eviction_policy=EvictionPolicy.CREATOR_PRIORITY,
            default_ttl=3600 * 24,  # 24 hours
            creator_isolation=True,
            namespace_isolation=True,
            priority_based_eviction=True,
            **kwargs
        )
        super().__init__(config)
    
    def cache_content(self, 
                     content_id: str,
                     creator_id: str, 
                     content: T,
                     content_type: str,
                     monetization_value: float = 0.0,
                     tags: Optional[Set[str]] = None) -> bool:
        """Cache creator content with appropriate metadata"""
        return self.set(
            key=f"content:{creator_id}:{content_id}",
            value=content,
            creator_id=creator_id,
            content_type=content_type,
            namespace=CacheNamespace.CREATOR_CONTENT,
            priority=CachePriority.HIGH,
            monetization_value=monetization_value,
            tags=tags or set()
        )

class AIProcessingCache(EnterpriseMemoryCache[T]):
    """Specialized cache for AI processing results"""
    
    def __init__(self, max_size: int = 2000, **kwargs):
        config = CacheConfig(
            max_size=max_size,
            max_memory_bytes=100 * 1024 * 1024,  # 100MB
            eviction_policy=EvictionPolicy.LRU,
            default_ttl=3600 * 6,  # 6 hours
            enable_compression=True,
            compression_threshold=512,
            **kwargs
        )
        super().__init__(config)
    
    def cache_ai_result(self,
                       content_id: str,
                       creator_id: str,
                       processing_result: T,
                       processing_cost: float,
                       model_version: str) -> bool:
        """Cache AI processing result"""
        tags = {f"model:{model_version}", "ai_processed"}
        
        return self.set(
            key=f"ai:{creator_id}:{content_id}",
            value=processing_result,
            creator_id=creator_id,
            namespace=CacheNamespace.AI_PROCESSING,
            priority=CachePriority.MEDIUM,
            processing_cost=processing_cost,
            tags=tags
        )

class RevenueAnalyticsCache(EnterpriseMemoryCache[T]):
    """Specialized cache for revenue and analytics data"""
    
    def __init__(self, max_size: int = 1000, **kwargs):
        config = CacheConfig(
            max_size=max_size,
            max_memory_bytes=50 * 1024 * 1024,  # 50MB
            eviction_policy=EvictionPolicy.CONTENT_VALUE,
            default_ttl=3600,  # 1 hour
            revenue_aware_caching=True,
            **kwargs
        )
        super().__init__(config)
    
    def cache_revenue_data(self,
                          metric_key: str,
                          creator_id: str,
                          data: T,
                          revenue_impact: float) -> bool:
        """Cache revenue analytics data"""
        return self.set(
            key=f"revenue:{creator_id}:{metric_key}",
            value=data,
            creator_id=creator_id,
            namespace=CacheNamespace.REVENUE_ANALYTICS,
            priority=CachePriority.CRITICAL,
            revenue_impact=revenue_impact
        )

# Legacy compatibility aliases
MemoryCache = EnterpriseMemoryCache
LRUCache = EnterpriseMemoryCache
LFUCache = EnterpriseMemoryCache  
TTLCache = EnterpriseMemoryCache

# Factory functions for easy instantiation
def create_memory_cache(config: Optional[CacheConfig] = None) -> EnterpriseMemoryCache:
    """Create standard memory cache"""
    return EnterpriseMemoryCache(config)

def create_creator_cache(max_size: int = 5000) -> CreatorContentCache:
    """Create creator content cache"""
    return CreatorContentCache(max_size=max_size)

def create_ai_cache(max_size: int = 2000) -> AIProcessingCache:
    """Create AI processing cache"""
    return AIProcessingCache(max_size=max_size)

def create_revenue_cache(max_size: int = 1000) -> RevenueAnalyticsCache:
    """Create revenue analytics cache"""
    return RevenueAnalyticsCache(max_size=max_size)

# Global cache instances
_memory_cache_instance: Optional[EnterpriseMemoryCache] = None
_creator_cache_instance: Optional[CreatorContentCache] = None
_ai_cache_instance: Optional[AIProcessingCache] = None
_revenue_cache_instance: Optional[RevenueAnalyticsCache] = None

def get_memory_cache() -> EnterpriseMemoryCache:
    """Get or create global memory cache instance"""
    global _memory_cache_instance
    if _memory_cache_instance is None:
        _memory_cache_instance = create_memory_cache()
    return _memory_cache_instance

def get_creator_cache() -> CreatorContentCache:
    """Get or create global creator cache instance"""
    global _creator_cache_instance
    if _creator_cache_instance is None:
        _creator_cache_instance = create_creator_cache()
    return _creator_cache_instance

def get_ai_cache() -> AIProcessingCache:
    """Get or create global AI cache instance"""
    global _ai_cache_instance
    if _ai_cache_instance is None:
        _ai_cache_instance = create_ai_cache()
    return _ai_cache_instance

def get_revenue_cache() -> RevenueAnalyticsCache:
    """Get or create global revenue cache instance"""
    global _revenue_cache_instance
    if _revenue_cache_instance is None:
        _revenue_cache_instance = create_revenue_cache()
    return _revenue_cache_instance
