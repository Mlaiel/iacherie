"""Mobile AI Cache Manager
=========================

Mobile IA cache management system providing intelligent caching strategies,
offline support, and performance optimization for mobile devices.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
import hashlib
import pickle
import gzip
import os
from pathlib import Path
import sqlite3
import aiosqlite

logger = logging.getLogger(__name__)


class CacheStrategy(str, Enum):
    """Cache strategies for mobile optimization."""
    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used
    TTL = "ttl"                    # Time To Live
    PRIORITY_BASED = "priority_based"  # Priority-based eviction
    ADAPTIVE = "adaptive"          # Adaptive based on conditions
    MOBILE_OPTIMIZED = "mobile_optimized"  # Mobile-specific optimization


class CacheLevel(str, Enum):
    """Cache levels for hierarchical caching."""
    MEMORY = "memory"              # In-memory cache (fastest)
    DEVICE_STORAGE = "device_storage"  # Local device storage
    CLOUD_CACHE = "cloud_cache"    # Cloud-based cache
    EDGE_CACHE = "edge_cache"      # Edge server cache


class CachePriority(str, Enum):
    """Cache priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CacheEntry:
    """Cache entry metadata."""
    cache_key: str
    content_type: str
    data_size_bytes: int
    creation_time: datetime
    last_accessed: datetime
    access_count: int
    expiry_time: Optional[datetime]
    priority: CachePriority
    cache_level: CacheLevel
    compression_ratio: float
    mobile_optimized: bool
    creator_id: str
    content_id: str
    ai_model_version: str
    confidence_score: float
    cache_metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.cache_metadata is None:
            self.cache_metadata = {}


@dataclass
class CacheConfiguration:
    """Mobile AI cache configuration."""
    strategy: CacheStrategy
    max_memory_cache_mb: int = 50     # 50MB memory cache
    max_device_cache_mb: int = 500    # 500MB device cache
    max_cloud_cache_mb: int = 2000    # 2GB cloud cache
    default_ttl_hours: int = 24       # 24 hours default TTL
    compression_enabled: bool = True
    encryption_enabled: bool = True
    offline_cache_enabled: bool = True
    preload_popular_results: bool = True
    adaptive_cache_sizing: bool = True
    battery_aware_caching: bool = True
    network_aware_sync: bool = True
    cache_analytics_enabled: bool = True


@dataclass
class CachePerformanceMetrics:
    """Cache performance metrics."""
    cache_hits: int = 0
    cache_misses: int = 0
    memory_hits: int = 0
    device_hits: int = 0
    cloud_hits: int = 0
    total_requests: int = 0
    average_response_time_ms: float = 0.0
    cache_size_mb: float = 0.0
    cache_efficiency: float = 0.0
    eviction_count: int = 0
    compression_savings_mb: float = 0.0
    network_savings_mb: float = 0.0
    battery_savings_percent: float = 0.0


class MobileAICacheManager:
    """Mobile IA cache management system."""

    def __init__(self, cache_dir: str = "/tmp/mobile_ai_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache levels
        self.memory_cache: Dict[str, Any] = {}
        self.device_cache_db_path = self.cache_dir / "device_cache.db"
        self.cloud_cache_registry: Dict[str, str] = {}
        
        # Cache management
        self.cache_entries: Dict[str, CacheEntry] = {}
        self.access_patterns: Dict[str, List[datetime]] = {}
        self.performance_metrics = CachePerformanceMetrics()
        
        # Configuration
        self.config = CacheConfiguration(strategy=CacheStrategy.MOBILE_OPTIMIZED)
        
        # Cache strategies
        self.cache_strategies = self._initialize_cache_strategies()
        self.compression_handlers = self._initialize_compression_handlers()
        self.eviction_policies = self._initialize_eviction_policies()
        
        # Initialize database (will be called when first needed)
        self._db_initialized = False

    def _initialize_cache_strategies(self) -> Dict[CacheStrategy, Any]:
        """Initialize cache strategies."""
        return {
            CacheStrategy.LRU: self._create_lru_strategy(),
            CacheStrategy.LFU: self._create_lfu_strategy(),
            CacheStrategy.TTL: self._create_ttl_strategy(),
            CacheStrategy.PRIORITY_BASED: self._create_priority_strategy(),
            CacheStrategy.ADAPTIVE: self._create_adaptive_strategy(),
            CacheStrategy.MOBILE_OPTIMIZED: self._create_mobile_strategy()
        }

    def _initialize_compression_handlers(self) -> Dict[str, Any]:
        """Initialize compression handlers."""
        return {
            "gzip": self._create_gzip_handler(),
            "lz4": self._create_lz4_handler(),
            "brotli": self._create_brotli_handler(),
            "mobile_optimized": self._create_mobile_compression_handler()
        }

    def _initialize_eviction_policies(self) -> Dict[str, Any]:
        """Initialize cache eviction policies."""
        return {
            "size_based": self._create_size_eviction(),
            "time_based": self._create_time_eviction(),
            "priority_based": self._create_priority_eviction(),
            "mobile_adaptive": self._create_mobile_eviction()
        }

    async def _initialize_device_cache_db(self) -> None:
        """Initialize device cache database."""
        try:
            async with aiosqlite.connect(self.device_cache_db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        cache_key TEXT PRIMARY KEY,
                        content_type TEXT,
                        data_blob BLOB,
                        data_size INTEGER,
                        creation_time TEXT,
                        last_accessed TEXT,
                        access_count INTEGER,
                        expiry_time TEXT,
                        priority TEXT,
                        cache_level TEXT,
                        compression_ratio REAL,
                        mobile_optimized BOOLEAN,
                        creator_id TEXT,
                        content_id TEXT,
                        ai_model_version TEXT,
                        confidence_score REAL,
                        cache_metadata TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_last_accessed 
                    ON cache_entries(last_accessed)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_expiry 
                    ON cache_entries(expiry_time)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_creator 
                    ON cache_entries(creator_id)
                """)
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize device cache database: {e}")

    async def _ensure_db_initialized(self) -> None:
        """Ensure database is initialized."""
        if not self._db_initialized:
            await self._initialize_device_cache_db()
            self._db_initialized = True

    async def cache_ai_result(self, cache_key: str, data: Any, 
                            cache_metadata: Dict[str, Any] = None) -> bool:
        """Cache AI processing result with mobile optimization."""
        try:
            await self._ensure_db_initialized()
            logger.debug(f"Caching AI result with key: {cache_key}")
            
            # Determine optimal cache level
            cache_level = await self._determine_optimal_cache_level(data, cache_metadata or {})
            
            # Prepare cache entry
            entry = CacheEntry(
                cache_key=cache_key,
                content_type=cache_metadata.get("content_type", "unknown"),
                data_size_bytes=self._estimate_data_size(data),
                creation_time=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=1,
                expiry_time=self._calculate_expiry_time(cache_metadata or {}),
                priority=CachePriority(cache_metadata.get("priority", "normal")),
                cache_level=cache_level,
                compression_ratio=1.0,
                mobile_optimized=True,
                creator_id=cache_metadata.get("creator_id", ""),
                content_id=cache_metadata.get("content_id", ""),
                ai_model_version=cache_metadata.get("ai_model_version", "v1.0"),
                confidence_score=cache_metadata.get("confidence_score", 0.8),
                cache_metadata=cache_metadata or {}
            )
            
            # Apply mobile optimization
            optimized_data = await self._optimize_data_for_mobile(data, entry)
            
            # Compress data if enabled
            if self.config.compression_enabled:
                compressed_data, compression_ratio = await self._compress_data(optimized_data)
                entry.compression_ratio = compression_ratio
                final_data = compressed_data
            else:
                final_data = optimized_data
            
            # Cache at appropriate level
            success = await self._cache_at_level(cache_key, final_data, entry, cache_level)
            
            if success:
                # Register cache entry
                self.cache_entries[cache_key] = entry
                
                # Update access patterns
                self._update_access_pattern(cache_key)
                
                # Update performance metrics
                self.performance_metrics.cache_size_mb += entry.data_size_bytes / (1024 * 1024)
                
                # Trigger eviction if needed
                await self._check_and_evict_if_needed(cache_level)
                
                logger.debug(f"Successfully cached AI result at {cache_level.value} level")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cache AI result: {e}")
            return False

    async def get_cached_ai_result(self, cache_key: str) -> Optional[Tuple[Any, CacheEntry]]:
        """Retrieve cached AI result with mobile optimization."""
        try:
            await self._ensure_db_initialized()
            start_time = datetime.utcnow()
            
            # Check if entry exists
            if cache_key not in self.cache_entries:
                self.performance_metrics.cache_misses += 1
                self.performance_metrics.total_requests += 1
                return None
            
            entry = self.cache_entries[cache_key]
            
            # Check expiry
            if entry.expiry_time and datetime.utcnow() > entry.expiry_time:
                await self._evict_cache_entry(cache_key)
                self.performance_metrics.cache_misses += 1
                self.performance_metrics.total_requests += 1
                return None
            
            # Retrieve data from appropriate cache level
            data = await self._retrieve_from_cache_level(cache_key, entry.cache_level)
            
            if data is None:
                # Entry exists but data not found - cleanup
                await self._evict_cache_entry(cache_key)
                self.performance_metrics.cache_misses += 1
                self.performance_metrics.total_requests += 1
                return None
            
            # Decompress if needed
            if self.config.compression_enabled and entry.compression_ratio != 1.0:
                decompressed_data = await self._decompress_data(data)
                final_data = decompressed_data
            else:
                final_data = data
            
            # Update access metadata
            entry.last_accessed = datetime.utcnow()
            entry.access_count += 1
            
            # Update access patterns
            self._update_access_pattern(cache_key)
            
            # Update performance metrics
            self.performance_metrics.cache_hits += 1
            self.performance_metrics.total_requests += 1
            
            if entry.cache_level == CacheLevel.MEMORY:
                self.performance_metrics.memory_hits += 1
            elif entry.cache_level == CacheLevel.DEVICE_STORAGE:
                self.performance_metrics.device_hits += 1
            elif entry.cache_level == CacheLevel.CLOUD_CACHE:
                self.performance_metrics.cloud_hits += 1
            
            # Update response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            current_avg = self.performance_metrics.average_response_time_ms
            total_requests = self.performance_metrics.total_requests
            new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
            self.performance_metrics.average_response_time_ms = new_avg
            
            logger.debug(f"Cache hit for key {cache_key} from {entry.cache_level.value}")
            return final_data, entry
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached AI result: {e}")
            self.performance_metrics.cache_misses += 1
            self.performance_metrics.total_requests += 1
            return None

    async def _determine_optimal_cache_level(self, data: Any, metadata: Dict[str, Any]) -> CacheLevel:
        """Determine optimal cache level for data."""
        data_size = self._estimate_data_size(data)
        priority = CachePriority(metadata.get("priority", "normal"))
        content_type = metadata.get("content_type", "unknown")
        
        # High priority or small data -> Memory cache
        if priority == CachePriority.CRITICAL or data_size < 1024 * 1024:  # < 1MB
            return CacheLevel.MEMORY
        
        # Medium priority or moderate size -> Device storage
        if priority in [CachePriority.HIGH, CachePriority.NORMAL] or data_size < 10 * 1024 * 1024:  # < 10MB
            return CacheLevel.DEVICE_STORAGE
        
        # Large data or low priority -> Cloud cache
        return CacheLevel.CLOUD_CACHE

    async def _optimize_data_for_mobile(self, data: Any, entry: CacheEntry) -> Any:
        """Optimize data for mobile storage and retrieval."""
        # Apply mobile-specific optimizations
        optimized_data = data
        
        # Remove unnecessary metadata for mobile
        if isinstance(data, dict):
            # Keep only essential fields for mobile
            mobile_essential_fields = [
                "result", "confidence", "primary_analysis", 
                "mobile_optimized", "summary", "key_insights"
            ]
            
            optimized_data = {
                key: value for key, value in data.items()
                if key in mobile_essential_fields or key.startswith("mobile_")
            }
        
        return optimized_data

    async def _compress_data(self, data: Any) -> Tuple[bytes, float]:
        """Compress data with mobile-optimized compression."""
        try:
            # Serialize data
            serialized_data = pickle.dumps(data)
            original_size = len(serialized_data)
            
            # Compress with gzip (mobile-friendly)
            compressed_data = gzip.compress(serialized_data, compresslevel=6)
            compressed_size = len(compressed_data)
            
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            return compressed_data, compression_ratio
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return pickle.dumps(data), 1.0

    async def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress cached data."""
        try:
            decompressed_data = gzip.decompress(compressed_data)
            return pickle.loads(decompressed_data)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return None

    async def _cache_at_level(self, cache_key: str, data: Any, 
                            entry: CacheEntry, cache_level: CacheLevel) -> bool:
        """Cache data at specified level."""
        try:
            if cache_level == CacheLevel.MEMORY:
                return await self._cache_in_memory(cache_key, data, entry)
            elif cache_level == CacheLevel.DEVICE_STORAGE:
                return await self._cache_on_device(cache_key, data, entry)
            elif cache_level == CacheLevel.CLOUD_CACHE:
                return await self._cache_in_cloud(cache_key, data, entry)
            else:
                return False
        except Exception as e:
            logger.error(f"Failed to cache at level {cache_level}: {e}")
            return False

    async def _cache_in_memory(self, cache_key: str, data: Any, entry: CacheEntry) -> bool:
        """Cache data in memory."""
        try:
            # Check memory limit
            current_memory_mb = sum(
                self._estimate_data_size(v) for v in self.memory_cache.values()
            ) / (1024 * 1024)
            
            if current_memory_mb >= self.config.max_memory_cache_mb:
                await self._evict_from_memory()
            
            self.memory_cache[cache_key] = data
            return True
            
        except Exception as e:
            logger.error(f"Memory caching failed: {e}")
            return False

    async def _cache_on_device(self, cache_key: str, data: Any, entry: CacheEntry) -> bool:
        """Cache data on device storage."""
        try:
            async with aiosqlite.connect(self.device_cache_db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (cache_key, content_type, data_blob, data_size, creation_time, 
                     last_accessed, access_count, expiry_time, priority, cache_level,
                     compression_ratio, mobile_optimized, creator_id, content_id,
                     ai_model_version, confidence_score, cache_metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cache_key,
                    entry.content_type,
                    data if isinstance(data, bytes) else pickle.dumps(data),
                    entry.data_size_bytes,
                    entry.creation_time.isoformat(),
                    entry.last_accessed.isoformat(),
                    entry.access_count,
                    entry.expiry_time.isoformat() if entry.expiry_time else None,
                    entry.priority.value,
                    entry.cache_level.value,
                    entry.compression_ratio,
                    entry.mobile_optimized,
                    entry.creator_id,
                    entry.content_id,
                    entry.ai_model_version,
                    entry.confidence_score,
                    json.dumps(entry.cache_metadata)
                ))
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Device caching failed: {e}")
            return False

    async def _cache_in_cloud(self, cache_key: str, data: Any, entry: CacheEntry) -> bool:
        """Cache data in cloud (placeholder for actual cloud integration)."""
        try:
            # Placeholder for cloud caching
            # In real implementation, this would upload to cloud storage
            self.cloud_cache_registry[cache_key] = f"cloud_storage_url/{cache_key}"
            return True
        except Exception as e:
            logger.error(f"Cloud caching failed: {e}")
            return False

    async def _retrieve_from_cache_level(self, cache_key: str, cache_level: CacheLevel) -> Optional[Any]:
        """Retrieve data from specified cache level."""
        try:
            if cache_level == CacheLevel.MEMORY:
                return self.memory_cache.get(cache_key)
            elif cache_level == CacheLevel.DEVICE_STORAGE:
                return await self._retrieve_from_device(cache_key)
            elif cache_level == CacheLevel.CLOUD_CACHE:
                return await self._retrieve_from_cloud(cache_key)
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve from {cache_level}: {e}")
            return None

    async def _retrieve_from_device(self, cache_key: str) -> Optional[Any]:
        """Retrieve data from device storage."""
        try:
            async with aiosqlite.connect(self.device_cache_db_path) as db:
                cursor = await db.execute(
                    "SELECT data_blob FROM cache_entries WHERE cache_key = ?",
                    (cache_key,)
                )
                row = await cursor.fetchone()
                
                if row:
                    data_blob = row[0]
                    if isinstance(data_blob, bytes):
                        return data_blob
                    else:
                        return pickle.loads(data_blob)
                return None
                
        except Exception as e:
            logger.error(f"Device retrieval failed: {e}")
            return None

    async def _retrieve_from_cloud(self, cache_key: str) -> Optional[Any]:
        """Retrieve data from cloud (placeholder)."""
        try:
            # Placeholder for cloud retrieval
            if cache_key in self.cloud_cache_registry:
                # In real implementation, this would download from cloud
                return {"cloud_data": "placeholder"}
            return None
        except Exception as e:
            logger.error(f"Cloud retrieval failed: {e}")
            return None

    def _calculate_expiry_time(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """Calculate cache entry expiry time."""
        ttl_hours = metadata.get("ttl_hours", self.config.default_ttl_hours)
        if ttl_hours > 0:
            return datetime.utcnow() + timedelta(hours=ttl_hours)
        return None

    def _estimate_data_size(self, data: Any) -> int:
        """Estimate data size in bytes."""
        try:
            if isinstance(data, bytes):
                return len(data)
            elif isinstance(data, str):
                return len(data.encode('utf-8'))
            else:
                return len(pickle.dumps(data))
        except:
            return 1024  # Default estimate

    def _update_access_pattern(self, cache_key: str) -> None:
        """Update access pattern for cache key."""
        if cache_key not in self.access_patterns:
            self.access_patterns[cache_key] = []
        
        self.access_patterns[cache_key].append(datetime.utcnow())
        
        # Keep only recent access times (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.access_patterns[cache_key] = [
            access_time for access_time in self.access_patterns[cache_key]
            if access_time > cutoff_time
        ]

    async def _check_and_evict_if_needed(self, cache_level: CacheLevel) -> None:
        """Check cache size and evict if needed."""
        if cache_level == CacheLevel.MEMORY:
            await self._check_memory_cache_size()
        elif cache_level == CacheLevel.DEVICE_STORAGE:
            await self._check_device_cache_size()
        elif cache_level == CacheLevel.CLOUD_CACHE:
            await self._check_cloud_cache_size()

    async def _check_memory_cache_size(self) -> None:
        """Check and manage memory cache size."""
        current_size_mb = sum(
            self._estimate_data_size(v) for v in self.memory_cache.values()
        ) / (1024 * 1024)
        
        if current_size_mb > self.config.max_memory_cache_mb:
            await self._evict_from_memory()

    async def _evict_from_memory(self) -> None:
        """Evict entries from memory cache."""
        if not self.memory_cache:
            return
        
        # Use LRU eviction for memory cache
        entries_by_access = sorted(
            [(k, self.cache_entries[k].last_accessed) for k in self.memory_cache.keys()
             if k in self.cache_entries],
            key=lambda x: x[1]
        )
        
        # Remove oldest 25% of entries
        evict_count = max(1, len(entries_by_access) // 4)
        for cache_key, _ in entries_by_access[:evict_count]:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                self.performance_metrics.eviction_count += 1

    async def _check_device_cache_size(self) -> None:
        """Check and manage device cache size."""
        try:
            async with aiosqlite.connect(self.device_cache_db_path) as db:
                cursor = await db.execute("SELECT SUM(data_size) FROM cache_entries")
                row = await cursor.fetchone()
                total_size_bytes = row[0] or 0
                total_size_mb = total_size_bytes / (1024 * 1024)
                
                if total_size_mb > self.config.max_device_cache_mb:
                    await self._evict_from_device()
                    
        except Exception as e:
            logger.error(f"Device cache size check failed: {e}")

    async def _evict_from_device(self) -> None:
        """Evict entries from device cache."""
        try:
            async with aiosqlite.connect(self.device_cache_db_path) as db:
                # Remove expired entries first
                await db.execute("""
                    DELETE FROM cache_entries 
                    WHERE expiry_time IS NOT NULL AND expiry_time < ?
                """, (datetime.utcnow().isoformat(),))
                
                # Remove oldest accessed entries if still over limit
                await db.execute("""
                    DELETE FROM cache_entries 
                    WHERE cache_key IN (
                        SELECT cache_key FROM cache_entries 
                        ORDER BY last_accessed ASC 
                        LIMIT (SELECT COUNT(*) FROM cache_entries) / 4
                    )
                """)
                
                await db.commit()
                self.performance_metrics.eviction_count += 1
                
        except Exception as e:
            logger.error(f"Device cache eviction failed: {e}")

    async def _check_cloud_cache_size(self) -> None:
        """Check and manage cloud cache size."""
        # Placeholder for cloud cache size management
        pass

    async def _evict_cache_entry(self, cache_key: str) -> None:
        """Evict specific cache entry."""
        if cache_key in self.cache_entries:
            entry = self.cache_entries[cache_key]
            
            # Remove from appropriate cache level
            if entry.cache_level == CacheLevel.MEMORY and cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            elif entry.cache_level == CacheLevel.DEVICE_STORAGE:
                try:
                    async with aiosqlite.connect(self.device_cache_db_path) as db:
                        await db.execute("DELETE FROM cache_entries WHERE cache_key = ?", (cache_key,))
                        await db.commit()
                except Exception as e:
                    logger.error(f"Device cache entry deletion failed: {e}")
            elif entry.cache_level == CacheLevel.CLOUD_CACHE and cache_key in self.cloud_cache_registry:
                del self.cloud_cache_registry[cache_key]
            
            # Remove from registry
            del self.cache_entries[cache_key]
            
            # Remove access patterns
            if cache_key in self.access_patterns:
                del self.access_patterns[cache_key]

    # Placeholder strategy creation methods
    def _create_lru_strategy(self): return None
    def _create_lfu_strategy(self): return None
    def _create_ttl_strategy(self): return None
    def _create_priority_strategy(self): return None
    def _create_adaptive_strategy(self): return None
    def _create_mobile_strategy(self): return None
    
    def _create_gzip_handler(self): return None
    def _create_lz4_handler(self): return None
    def _create_brotli_handler(self): return None
    def _create_mobile_compression_handler(self): return None
    
    def _create_size_eviction(self): return None
    def _create_time_eviction(self): return None
    def _create_priority_eviction(self): return None
    def _create_mobile_eviction(self): return None

    # Public API methods
    async def get_cache_statistics(self) -> CachePerformanceMetrics:
        """Get comprehensive cache statistics."""
        # Update cache efficiency
        total_requests = self.performance_metrics.total_requests
        if total_requests > 0:
            hit_rate = self.performance_metrics.cache_hits / total_requests
            self.performance_metrics.cache_efficiency = hit_rate * 100
        
        return self.performance_metrics

    async def get_cache_entries_for_creator(self, creator_id: str) -> List[CacheEntry]:
        """Get cache entries for specific creator."""
        return [
            entry for entry in self.cache_entries.values()
            if entry.creator_id == creator_id
        ]

    async def invalidate_cache_by_creator(self, creator_id: str) -> int:
        """Invalidate all cache entries for a creator."""
        invalidated_count = 0
        
        entries_to_remove = [
            cache_key for cache_key, entry in self.cache_entries.items()
            if entry.creator_id == creator_id
        ]
        
        for cache_key in entries_to_remove:
            await self._evict_cache_entry(cache_key)
            invalidated_count += 1
        
        return invalidated_count

    async def invalidate_cache_by_content(self, content_id: str) -> bool:
        """Invalidate cache entries for specific content."""
        entries_to_remove = [
            cache_key for cache_key, entry in self.cache_entries.items()
            if entry.content_id == content_id
        ]
        
        for cache_key in entries_to_remove:
            await self._evict_cache_entry(cache_key)
        
        return len(entries_to_remove) > 0

    async def preload_popular_results(self, creator_id: str) -> int:
        """Preload popular AI results for creator."""
        # Placeholder for preloading logic
        # Would analyze access patterns and preload frequently used results
        return 0

    async def optimize_cache_for_device(self, device_capabilities: Dict[str, Any]) -> None:
        """Optimize cache configuration for device capabilities."""
        # Adjust cache sizes based on device capabilities
        device_ram_gb = device_capabilities.get("ram_gb", 4)
        storage_gb = device_capabilities.get("storage_gb", 32)
        
        # Adjust memory cache based on available RAM
        if device_ram_gb >= 8:
            self.config.max_memory_cache_mb = 100
        elif device_ram_gb >= 4:
            self.config.max_memory_cache_mb = 50
        else:
            self.config.max_memory_cache_mb = 25
        
        # Adjust device cache based on available storage
        if storage_gb >= 128:
            self.config.max_device_cache_mb = 1000
        elif storage_gb >= 64:
            self.config.max_device_cache_mb = 500
        else:
            self.config.max_device_cache_mb = 250

    async def clear_cache(self, cache_level: Optional[CacheLevel] = None) -> bool:
        """Clear cache at specified level or all levels."""
        try:
            if cache_level is None or cache_level == CacheLevel.MEMORY:
                self.memory_cache.clear()
            
            if cache_level is None or cache_level == CacheLevel.DEVICE_STORAGE:
                async with aiosqlite.connect(self.device_cache_db_path) as db:
                    await db.execute("DELETE FROM cache_entries")
                    await db.commit()
            
            if cache_level is None or cache_level == CacheLevel.CLOUD_CACHE:
                self.cloud_cache_registry.clear()
            
            if cache_level is None:
                self.cache_entries.clear()
                self.access_patterns.clear()
                self.performance_metrics = CachePerformanceMetrics()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return False

    async def get_cache_health_report(self) -> Dict[str, Any]:
        """Get comprehensive cache health report."""
        stats = await self.get_cache_statistics()
        
        return {
            "overall_health": "good" if stats.cache_efficiency > 70 else "needs_attention",
            "cache_efficiency_percent": stats.cache_efficiency,
            "memory_cache_entries": len(self.memory_cache),
            "total_cache_entries": len(self.cache_entries),
            "hit_rate_percent": (stats.cache_hits / max(1, stats.total_requests)) * 100,
            "average_response_time_ms": stats.average_response_time_ms,
            "cache_size_mb": stats.cache_size_mb,
            "compression_savings_mb": stats.compression_savings_mb,
            "recommendations": await self._generate_cache_recommendations(stats)
        }

    async def _generate_cache_recommendations(self, stats: CachePerformanceMetrics) -> List[str]:
        """Generate cache optimization recommendations."""
        recommendations = []
        
        if stats.cache_efficiency < 50:
            recommendations.append("Consider increasing cache size or adjusting TTL")
        
        if stats.average_response_time_ms > 500:
            recommendations.append("Optimize for faster cache access")
        
        if stats.eviction_count > stats.cache_hits * 0.1:
            recommendations.append("Cache size may be too small for usage pattern")
        
        return recommendations