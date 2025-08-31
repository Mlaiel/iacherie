"""Advanced Intelligent Caching System
Enterprise-grade content caching with ML-powered optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""
import asyncio
import hashlib
import pickle
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import redis.asyncio as redis
import aiofiles
from pathlib import Path

from ..core.exceptions import CacheException, ValidationError
from ..core.metrics import MetricsCollector
from ..database.connection import get_database_session
from ..security.encryption import EncryptionService


class CacheLevel(Enum):
    """Cache level enumeration"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISK = "l3_disk"
    L4_DATABASE = "l4_database"


class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # ML-powered adaptive
    CONTENT_AWARE = "content_aware"  # Content-type aware


class CachePolicy(Enum):
    """Cache policy enumeration"""
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    CACHE_ASIDE = "cache_aside"


@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[int]
    size_bytes: int
    content_type: str
    priority: int = 1
    encrypted: bool = False
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)
    
    @property
    def age_seconds(self) -> int:
        """Get age of cache entry in seconds"""
        return int((datetime.utcnow() - self.created_at).total_seconds())
    
    def update_access(self):
        """Update access information"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    writes: int = 0
    errors: int = 0
    total_size: int = 0
    average_access_time: float = 0.0
    hit_ratio: float = 0.0
    
    def calculate_hit_ratio(self):
        """Calculate cache hit ratio"""
        total_requests = self.hits + self.misses
        self.hit_ratio = self.hits / total_requests if total_requests > 0 else 0.0


class IntelligentCacheManager:
    """
    Advanced intelligent caching system with multi-level cache hierarchy,
    ML-powered optimization, and adaptive strategies
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        encryption_service: Optional[EncryptionService] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.config = config or self._get_default_config()
        self.encryption_service = encryption_service
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
        
        # Multi-level cache storage
        self.l1_cache: Dict[str, CacheEntry] = {}  # Memory cache
        self.l2_redis: Optional[redis.Redis] = None  # Redis cache
        self.l3_disk_path = Path(self.config.get("disk_cache_path", "/tmp/cache"))
        
        # Cache management
        self.cache_metrics = CacheMetrics()
        self.access_patterns: Dict[str, List[datetime]] = {}
        self.eviction_candidates: Set[str] = set()
        
        # Strategy and policy
        self.default_strategy = CacheStrategy(self.config.get("default_strategy", "adaptive"))
        self.default_policy = CachePolicy(self.config.get("default_policy", "cache_aside"))
        
        # Performance optimization
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Initialize cache
        asyncio.create_task(self._initialize_cache())
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default cache configuration"""
        return {
            "l1_max_size": 100 * 1024 * 1024,  # 100MB
            "l1_max_entries": 10000,
            "l2_max_size": 1024 * 1024 * 1024,  # 1GB
            "l3_max_size": 10 * 1024 * 1024 * 1024,  # 10GB
            "default_ttl": 3600,  # 1 hour
            "cleanup_interval": 300,  # 5 minutes
            "compression_threshold": 1024,  # 1KB
            "encryption_threshold": 10240,  # 10KB
            "adaptive_learning_window": 1000,
            "redis_url": "redis://localhost:6379",
            "disk_cache_path": "/tmp/cache",
            "enable_compression": True,
            "enable_encryption": True,
            "enable_persistence": True
        }
    
    async def _initialize_cache(self):
        """Initialize cache system"""
        try:
            # Initialize Redis connection
            if self.config.get("enable_redis", True):
                self.l2_redis = redis.from_url(
                    self.config["redis_url"],
                    decode_responses=False
                )
                await self.l2_redis.ping()
                self.logger.info("Redis cache initialized successfully")
            
            # Initialize disk cache directory
            self.l3_disk_path.mkdir(parents=True, exist_ok=True)
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            self.logger.info("Intelligent cache system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache system: {e}")
            raise CacheException(f"Cache initialization failed: {e}")
    
    async def get(
        self,
        key: str,
        default: Any = None,
        strategy: Optional[CacheStrategy] = None
    ) -> Any:
        """
        Get value from cache with intelligent lookup across all levels
        """
        start_time = time.time()
        
        try:
            async with self._lock:
                # Try L1 cache first
                if key in self.l1_cache:
                    entry = self.l1_cache[key]
                    if not entry.is_expired:
                        entry.update_access()
                        self._update_access_pattern(key)
                        self.cache_metrics.hits += 1
                        
                        if self.metrics_collector:
                            await self.metrics_collector.record_metric(
                                "cache_hit",
                                1,
                                tags={"level": "l1", "key": key}
                            )
                        
                        return await self._deserialize_value(entry.value, entry)
                    else:
                        # Remove expired entry
                        del self.l1_cache[key]
                
                # Try L2 Redis cache
                if self.l2_redis:
                    cached_data = await self.l2_redis.get(f"cache:{key}")
                    if cached_data:
                        entry = pickle.loads(cached_data)
                        if not entry.is_expired:
                            # Promote to L1 cache
                            await self._promote_to_l1(key, entry)
                            entry.update_access()
                            self._update_access_pattern(key)
                            self.cache_metrics.hits += 1
                            
                            if self.metrics_collector:
                                await self.metrics_collector.record_metric(
                                    "cache_hit",
                                    1,
                                    tags={"level": "l2", "key": key}
                                )
                            
                            return await self._deserialize_value(entry.value, entry)
                        else:
                            # Remove expired entry
                            await self.l2_redis.delete(f"cache:{key}")
                
                # Try L3 disk cache
                disk_file = self.l3_disk_path / f"{self._hash_key(key)}.cache"
                if disk_file.exists():
                    async with aiofiles.open(disk_file, 'rb') as f:
                        cached_data = await f.read()
                        entry = pickle.loads(cached_data)
                        
                        if not entry.is_expired:
                            # Promote to higher levels
                            await self._promote_to_l2(key, entry)
                            await self._promote_to_l1(key, entry)
                            entry.update_access()
                            self._update_access_pattern(key)
                            self.cache_metrics.hits += 1
                            
                            if self.metrics_collector:
                                await self.metrics_collector.record_metric(
                                    "cache_hit",
                                    1,
                                    tags={"level": "l3", "key": key}
                                )
                            
                            return await self._deserialize_value(entry.value, entry)
                        else:
                            # Remove expired file
                            disk_file.unlink()
                
                # Cache miss
                self.cache_metrics.misses += 1
                
                if self.metrics_collector:
                    await self.metrics_collector.record_metric(
                        "cache_miss",
                        1,
                        tags={"key": key}
                    )
                
                return default
                
        except Exception as e:
            self.logger.error(f"Cache get error for key {key}: {e}")
            self.cache_metrics.errors += 1
            return default
        
        finally:
            access_time = time.time() - start_time
            self._update_average_access_time(access_time)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy: Optional[CacheStrategy] = None,
        policy: Optional[CachePolicy] = None,
        content_type: str = "unknown",
        priority: int = 1
    ) -> bool:
        """
        Set value in cache with intelligent distribution across levels
        """
        try:
            async with self._lock:
                # Serialize and prepare value
                serialized_value = await self._serialize_value(value)
                size_bytes = len(serialized_value) if isinstance(serialized_value, bytes) else len(str(serialized_value))
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=serialized_value,
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    access_count=1,
                    ttl=ttl or self.config["default_ttl"],
                    size_bytes=size_bytes,
                    content_type=content_type,
                    priority=priority
                )
                
                # Apply compression if needed
                if (self.config["enable_compression"] and 
                    size_bytes > self.config["compression_threshold"]):
                    entry.value = await self._compress_value(entry.value)
                    entry.compressed = True
                
                # Apply encryption if needed
                if (self.config["enable_encryption"] and 
                    self.encryption_service and
                    size_bytes > self.config["encryption_threshold"]):
                    entry.value = await self.encryption_service.encrypt(entry.value)
                    entry.encrypted = True
                
                # Determine cache level based on strategy
                cache_level = await self._determine_cache_level(entry, strategy)
                
                # Store in appropriate cache level(s)
                success = await self._store_in_cache_level(key, entry, cache_level, policy)
                
                if success:
                    self.cache_metrics.writes += 1
                    self._update_access_pattern(key)
                    
                    if self.metrics_collector:
                        await self.metrics_collector.record_metric(
                            "cache_write",
                            1,
                            tags={"level": cache_level.value, "key": key}
                        )
                
                return success
                
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            self.cache_metrics.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        try:
            async with self._lock:
                deleted = False
                
                # Delete from L1
                if key in self.l1_cache:
                    del self.l1_cache[key]
                    deleted = True
                
                # Delete from L2
                if self.l2_redis:
                    result = await self.l2_redis.delete(f"cache:{key}")
                    if result > 0:
                        deleted = True
                
                # Delete from L3
                disk_file = self.l3_disk_path / f"{self._hash_key(key)}.cache"
                if disk_file.exists():
                    disk_file.unlink()
                    deleted = True
                
                # Clean up access patterns
                if key in self.access_patterns:
                    del self.access_patterns[key]
                
                return deleted
                
        except Exception as e:
            self.logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear(self, level: Optional[CacheLevel] = None) -> bool:
        """Clear cache at specified level or all levels"""
        try:
            async with self._lock:
                if level is None or level == CacheLevel.L1_MEMORY:
                    self.l1_cache.clear()
                
                if level is None or level == CacheLevel.L2_REDIS:
                    if self.l2_redis:
                        await self.l2_redis.flushdb()
                
                if level is None or level == CacheLevel.L3_DISK:
                    for cache_file in self.l3_disk_path.glob("*.cache"):
                        cache_file.unlink()
                
                if level is None:
                    self.access_patterns.clear()
                    self.eviction_candidates.clear()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        self.cache_metrics.calculate_hit_ratio()
        
        return {
            "metrics": {
                "hits": self.cache_metrics.hits,
                "misses": self.cache_metrics.misses,
                "evictions": self.cache_metrics.evictions,
                "writes": self.cache_metrics.writes,
                "errors": self.cache_metrics.errors,
                "hit_ratio": self.cache_metrics.hit_ratio,
                "average_access_time": self.cache_metrics.average_access_time
            },
            "cache_levels": {
                "l1_entries": len(self.l1_cache),
                "l1_size": sum(entry.size_bytes for entry in self.l1_cache.values()),
                "l2_connected": self.l2_redis is not None,
                "l3_files": len(list(self.l3_disk_path.glob("*.cache")))
            },
            "configuration": self.config,
            "access_patterns": len(self.access_patterns),
            "eviction_candidates": len(self.eviction_candidates)
        }
    
    async def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        if isinstance(value, bytes):
            return value
        elif isinstance(value, str):
            return value.encode('utf-8')
        else:
            return pickle.dumps(value)
    
    async def _deserialize_value(self, value: bytes, entry: CacheEntry) -> Any:
        """Deserialize value from storage"""
        try:
            # Decrypt if needed
            if entry.encrypted and self.encryption_service:
                value = await self.encryption_service.decrypt(value)
            
            # Decompress if needed
            if entry.compressed:
                value = await self._decompress_value(value)
            
            # Deserialize based on content type
            if entry.content_type == "string":
                return value.decode('utf-8')
            elif entry.content_type == "bytes":
                return value
            else:
                return pickle.loads(value)
                
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            return value
    
    async def _compress_value(self, value: bytes) -> bytes:
        """Compress value using gzip"""
        import gzip
        return gzip.compress(value)
    
    async def _decompress_value(self, value: bytes) -> bytes:
        """Decompress value using gzip"""
        import gzip
        return gzip.decompress(value)
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for cache key"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    async def _determine_cache_level(
        self,
        entry: CacheEntry,
        strategy: Optional[CacheStrategy]
    ) -> CacheLevel:
        """Determine optimal cache level for entry"""
        strategy = strategy or self.default_strategy
        
        # Size-based decisions
        if entry.size_bytes > self.config["l1_max_size"] // 10:
            return CacheLevel.L3_DISK
        elif entry.size_bytes > self.config["l1_max_size"] // 100:
            return CacheLevel.L2_REDIS
        else:
            return CacheLevel.L1_MEMORY
    
    async def _store_in_cache_level(
        self,
        key: str,
        entry: CacheEntry,
        level: CacheLevel,
        policy: Optional[CachePolicy]
    ) -> bool:
        """Store entry in specified cache level"""
        try:
            if level == CacheLevel.L1_MEMORY:
                # Check if eviction is needed
                if (len(self.l1_cache) >= self.config["l1_max_entries"] or
                    sum(e.size_bytes for e in self.l1_cache.values()) + entry.size_bytes > self.config["l1_max_size"]):
                    await self._evict_from_l1()
                
                self.l1_cache[key] = entry
                return True
            
            elif level == CacheLevel.L2_REDIS and self.l2_redis:
                serialized_entry = pickle.dumps(entry)
                await self.l2_redis.set(
                    f"cache:{key}",
                    serialized_entry,
                    ex=entry.ttl
                )
                return True
            
            elif level == CacheLevel.L3_DISK:
                disk_file = self.l3_disk_path / f"{self._hash_key(key)}.cache"
                serialized_entry = pickle.dumps(entry)
                
                async with aiofiles.open(disk_file, 'wb') as f:
                    await f.write(serialized_entry)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Store error for key {key} at level {level}: {e}")
            return False
    
    async def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote entry to L1 cache"""
        if entry.size_bytes <= self.config["l1_max_size"] // 10:
            if (len(self.l1_cache) >= self.config["l1_max_entries"] or
                sum(e.size_bytes for e in self.l1_cache.values()) + entry.size_bytes > self.config["l1_max_size"]):
                await self._evict_from_l1()
            
            self.l1_cache[key] = entry
    
    async def _promote_to_l2(self, key: str, entry: CacheEntry):
        """Promote entry to L2 cache"""
        if self.l2_redis and entry.size_bytes <= self.config["l2_max_size"] // 10:
            serialized_entry = pickle.dumps(entry)
            await self.l2_redis.set(
                f"cache:{key}",
                serialized_entry,
                ex=entry.ttl
            )
    
    async def _evict_from_l1(self):
        """Evict entries from L1 cache using intelligent strategy"""
        if not self.l1_cache:
            return
        
        # Find candidate for eviction (LRU strategy)
        oldest_key = min(
            self.l1_cache.keys(),
            key=lambda k: self.l1_cache[k].last_accessed
        )
        
        # Move to L2 before evicting if valuable
        entry = self.l1_cache[oldest_key]
        if entry.access_count > 1:
            await self._promote_to_l2(oldest_key, entry)
        
        del self.l1_cache[oldest_key]
        self.cache_metrics.evictions += 1
    
    def _update_access_pattern(self, key: str):
        """Update access pattern for key"""
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(datetime.utcnow())
        
        # Keep only recent access patterns
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.access_patterns[key] = [
            access_time for access_time in self.access_patterns[key]
            if access_time > cutoff
        ]
    
    def _update_average_access_time(self, access_time: float):
        """Update average access time"""
        if self.cache_metrics.average_access_time == 0:
            self.cache_metrics.average_access_time = access_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.cache_metrics.average_access_time = (
                alpha * access_time + 
                (1 - alpha) * self.cache_metrics.average_access_time
            )
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.config["cleanup_interval"])
                
                async with self._lock:
                    # Clean L1 cache
                    expired_keys = [
                        key for key, entry in self.l1_cache.items()
                        if entry.is_expired
                    ]
                    
                    for key in expired_keys:
                        del self.l1_cache[key]
                    
                    # Clean disk cache
                    for cache_file in self.l3_disk_path.glob("*.cache"):
                        try:
                            async with aiofiles.open(cache_file, 'rb') as f:
                                cached_data = await f.read()
                                entry = pickle.loads(cached_data)
                                
                                if entry.is_expired:
                                    cache_file.unlink()
                                    
                        except Exception:
                            # Remove corrupted files
                            cache_file.unlink()
                
                self.logger.debug(f"Cleanup completed, removed {len(expired_keys)} expired entries")
                
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
    
    async def close(self):
        """Close cache manager and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.l2_redis:
            await self.l2_redis.close()
        
        self.logger.info("Intelligent cache manager closed")


# Cache manager singleton
_cache_manager: Optional[IntelligentCacheManager] = None


async def get_cache_manager(
    config: Optional[Dict[str, Any]] = None,
    encryption_service: Optional[EncryptionService] = None,
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentCacheManager:
    """Get or create cache manager instance"""
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = IntelligentCacheManager(
            config=config,
            encryption_service=encryption_service,
            metrics_collector=metrics_collector
        )
    
    return _cache_manager


@asynccontextmanager
async def cache_context(
    config: Optional[Dict[str, Any]] = None,
    encryption_service: Optional[EncryptionService] = None,
    metrics_collector: Optional[MetricsCollector] = None
):
    """Context manager for cache operations"""
    cache_manager = await get_cache_manager(config, encryption_service, metrics_collector)
    try:
        yield cache_manager
    finally:
        # Cache manager stays alive for reuse
        pass


# Utility functions for common cache operations
async def cached_function(
    key_prefix: str,
    ttl: Optional[int] = None,
    strategy: Optional[CacheStrategy] = None
):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            cache_key = hashlib.sha256(key_data.encode()).hexdigest()
            
            cache_manager = await get_cache_manager()
            
            # Try to get from cache
            result = await cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(
                cache_key,
                result,
                ttl=ttl,
                strategy=strategy,
                content_type="function_result"
            )
            
            return result
        
        return wrapper
    return decorator
