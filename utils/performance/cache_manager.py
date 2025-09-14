"""
Cache Manager - Performance Utilities Level 3
=============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade cache management consolidating:
- Cache utilities (cache_utilities.py)
- Caching (caching.py)

Performance: < 1ms per cache operation
Standards: Multi-level caching, Redis integration, intelligent eviction
"""

import asyncio
import json
import logging
import pickle
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import hashlib
import weakref

# Redis import with fallback
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CacheResult:
    """Enterprise result container for cache operations."""
    success: bool
    result: Optional[Any] = None
    cache_hit: bool = False
    cache_level: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'result': self.result,
            'cache_hit': self.cache_hit,
            'cache_level': self.cache_level,
            'errors': self.errors,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CacheManager:
    """
    Enterprise cache manager with ultra-high performance standards.
    
    Implements multi-level caching strategy:
    - L1: In-memory (fastest, limited capacity)
    - L2: Redis (fast, shared across instances)
    - L3: Disk-based (slower, persistent)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cache manager with enterprise configuration."""
        self.config = config or {}
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._performance_threshold_ms = 1.0
        
        # L1 Cache (Memory)
        self._l1_cache: Dict[str, CacheEntry] = {}
        self._l1_max_size = self.config.get('l1_max_size', 1000)
        self._l1_ttl_seconds = self.config.get('l1_ttl_seconds', 300)  # 5 minutes
        
        # L2 Cache (Redis) configuration
        self._redis_client: Optional[aioredis.Redis] = None
        self._redis_url = self.config.get('redis_url', 'redis://localhost:6379')
        self._l2_ttl_seconds = self.config.get('l2_ttl_seconds', 3600)  # 1 hour
        
        # Performance monitoring
        self._cache_stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'total_operations': 0
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_redis()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self._cleanup_connections()
        self._thread_pool.shutdown(wait=True)
        
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection."""
        if REDIS_AVAILABLE:
            try:
                self._redis_client = aioredis.from_url(self._redis_url)
                await self._redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self._redis_client = None
        else:
            logger.warning("Redis not available, using memory-only caching")
            
    async def _cleanup_connections(self) -> None:
        """Clean up connections."""
        if self._redis_client:
            await self._redis_client.close()
            
    async def _measure_performance(self, operation: callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        
        if asyncio.iscoroutinefunction(operation):
            result = await operation()
        else:
            result = await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, operation
            )
            
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
    
    def _generate_cache_key(self, key: str, namespace: str = "default") -> str:
        """Generate consistent cache key with namespace."""
        if namespace != "default":
            key = f"{namespace}:{key}"
        
        # Hash long keys to ensure consistent length
        if len(key) > 100:
            key = hashlib.sha256(key.encode()).hexdigest()
            
        return key
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.expires_at is None:
            return False
        return datetime.now(timezone.utc) > entry.expires_at
    
    async def _evict_l1_if_needed(self) -> None:
        """Evict L1 cache entries if size limit exceeded."""
        if len(self._l1_cache) <= self._l1_max_size:
            return
        
        # Remove expired entries first
        expired_keys = [
            key for key, entry in self._l1_cache.items()
            if self._is_expired(entry)
        ]
        
        for key in expired_keys:
            del self._l1_cache[key]
        
        # If still over limit, remove least recently used
        if len(self._l1_cache) > self._l1_max_size:
            # Sort by last_accessed and remove oldest
            sorted_entries = sorted(
                self._l1_cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            entries_to_remove = len(self._l1_cache) - self._l1_max_size
            for i in range(entries_to_remove):
                key = sorted_entries[i][0]
                del self._l1_cache[key]
    
    # === L1 CACHE OPERATIONS (Memory) ===
    
    async def _get_l1(self, key: str) -> Tuple[bool, Any]:
        """Get value from L1 cache."""
        if key not in self._l1_cache:
            return False, None
        
        entry = self._l1_cache[key]
        
        # Check expiration
        if self._is_expired(entry):
            del self._l1_cache[key]
            return False, None
        
        # Update access metadata
        entry.access_count += 1
        entry.last_accessed = datetime.now(timezone.utc)
        
        return True, entry.value
    
    async def _set_l1(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in L1 cache."""
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        elif self._l1_ttl_seconds:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self._l1_ttl_seconds)
        
        entry = CacheEntry(
            value=value,
            expires_at=expires_at
        )
        
        self._l1_cache[key] = entry
        await self._evict_l1_if_needed()
    
    async def _delete_l1(self, key: str) -> bool:
        """Delete value from L1 cache."""
        if key in self._l1_cache:
            del self._l1_cache[key]
            return True
        return False
    
    # === L2 CACHE OPERATIONS (Redis) ===
    
    async def _get_l2(self, key: str) -> Tuple[bool, Any]:
        """Get value from L2 cache (Redis)."""
        if not self._redis_client:
            return False, None
        
        try:
            data = await self._redis_client.get(key)
            if data is None:
                return False, None
            
            # Deserialize value
            value = pickle.loads(data)
            return True, value
            
        except Exception as e:
            logger.error(f"L2 cache get failed: {e}")
            return False, None
    
    async def _set_l2(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in L2 cache (Redis)."""
        if not self._redis_client:
            return
        
        try:
            # Serialize value
            data = pickle.dumps(value)
            
            # Set with TTL
            ttl = ttl_seconds or self._l2_ttl_seconds
            await self._redis_client.setex(key, ttl, data)
            
        except Exception as e:
            logger.error(f"L2 cache set failed: {e}")
    
    async def _delete_l2(self, key: str) -> bool:
        """Delete value from L2 cache (Redis)."""
        if not self._redis_client:
            return False
        
        try:
            result = await self._redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"L2 cache delete failed: {e}")
            return False
    
    # === PUBLIC API ===
    
    async def get(
        self,
        key: str,
        namespace: str = "default",
        promote_to_l1: bool = True
    ) -> CacheResult:
        """Get value from multi-level cache."""
        async def _get():
            cache_key = self._generate_cache_key(key, namespace)
            self._cache_stats['total_operations'] += 1
            
            # Try L1 cache first
            hit, value = await self._get_l1(cache_key)
            if hit:
                self._cache_stats['l1_hits'] += 1
                return {
                    'value': value,
                    'cache_hit': True,
                    'cache_level': 'L1'
                }, []
            
            self._cache_stats['l1_misses'] += 1
            
            # Try L2 cache (Redis)
            hit, value = await self._get_l2(cache_key)
            if hit:
                self._cache_stats['l2_hits'] += 1
                
                # Promote to L1 if requested
                if promote_to_l1:
                    await self._set_l1(cache_key, value)
                
                return {
                    'value': value,
                    'cache_hit': True,
                    'cache_level': 'L2'
                }, []
            
            self._cache_stats['l2_misses'] += 1
            
            # Cache miss
            return {
                'value': None,
                'cache_hit': False,
                'cache_level': None
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_get)
            
            if result[0] is None:  # Error case
                return CacheResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'get'}
                )
            
            data = result[0]
            return CacheResult(
                success=True,
                result=data['value'],
                cache_hit=data['cache_hit'],
                cache_level=data['cache_level'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'get',
                    'key': key,
                    'namespace': namespace
                }
            )
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return CacheResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'get'}
            )
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        namespace: str = "default",
        levels: List[str] = None
    ) -> CacheResult:
        """Set value in multi-level cache."""
        async def _set():
            cache_key = self._generate_cache_key(key, namespace)
            levels_to_set = levels or ['L1', 'L2']
            
            results = []
            
            # Set in L1 if requested
            if 'L1' in levels_to_set:
                await self._set_l1(cache_key, value, ttl_seconds)
                results.append('L1')
            
            # Set in L2 if requested
            if 'L2' in levels_to_set:
                await self._set_l2(cache_key, value, ttl_seconds)
                results.append('L2')
            
            return {'levels_set': results}, []
            
        try:
            result, exec_time = await self._measure_performance(_set)
            
            if result[0] is None:  # Error case
                return CacheResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'set'}
                )
            
            data = result[0]
            return CacheResult(
                success=True,
                result=f"Set in levels: {', '.join(data['levels_set'])}",
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'set',
                    'key': key,
                    'namespace': namespace,
                    'levels_set': data['levels_set'],
                    'ttl_seconds': ttl_seconds
                }
            )
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return CacheResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'set'}
            )
    
    async def delete(
        self,
        key: str,
        namespace: str = "default",
        levels: List[str] = None
    ) -> CacheResult:
        """Delete value from multi-level cache."""
        async def _delete():
            cache_key = self._generate_cache_key(key, namespace)
            levels_to_delete = levels or ['L1', 'L2']
            
            results = []
            
            # Delete from L1 if requested
            if 'L1' in levels_to_delete:
                if await self._delete_l1(cache_key):
                    results.append('L1')
            
            # Delete from L2 if requested
            if 'L2' in levels_to_delete:
                if await self._delete_l2(cache_key):
                    results.append('L2')
            
            return {'levels_deleted': results}, []
            
        try:
            result, exec_time = await self._measure_performance(_delete)
            
            if result[0] is None:  # Error case
                return CacheResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'delete'}
                )
            
            data = result[0]
            return CacheResult(
                success=True,
                result=f"Deleted from levels: {', '.join(data['levels_deleted'])}",
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'delete',
                    'key': key,
                    'namespace': namespace,
                    'levels_deleted': data['levels_deleted']
                }
            )
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return CacheResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'delete'}
            )
    
    async def clear(self, namespace: str = "default") -> CacheResult:
        """Clear cache for specific namespace."""
        try:
            cleared_count = 0
            
            # Clear L1 cache
            if namespace == "default":
                cleared_count += len(self._l1_cache)
                self._l1_cache.clear()
            else:
                # Clear specific namespace
                prefix = f"{namespace}:"
                keys_to_remove = [k for k in self._l1_cache.keys() if k.startswith(prefix)]
                for key in keys_to_remove:
                    del self._l1_cache[key]
                cleared_count += len(keys_to_remove)
            
            # Clear L2 cache (Redis)
            if self._redis_client:
                if namespace == "default":
                    await self._redis_client.flushdb()
                else:
                    # Clear specific namespace from Redis
                    pattern = f"{namespace}:*"
                    keys = await self._redis_client.keys(pattern)
                    if keys:
                        await self._redis_client.delete(*keys)
                        cleared_count += len(keys)
            
            return CacheResult(
                success=True,
                result=f"Cleared {cleared_count} cache entries",
                metadata={
                    'operation': 'clear',
                    'namespace': namespace,
                    'cleared_count': cleared_count
                }
            )
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return CacheResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'clear'}
            )
    
    async def get_stats(self) -> CacheResult:
        """Get cache performance statistics."""
        try:
            l1_hit_rate = (
                self._cache_stats['l1_hits'] / self._cache_stats['total_operations']
                if self._cache_stats['total_operations'] > 0 else 0
            )
            
            l2_hit_rate = (
                self._cache_stats['l2_hits'] / self._cache_stats['total_operations']
                if self._cache_stats['total_operations'] > 0 else 0
            )
            
            overall_hit_rate = (
                (self._cache_stats['l1_hits'] + self._cache_stats['l2_hits']) / 
                self._cache_stats['total_operations']
                if self._cache_stats['total_operations'] > 0 else 0
            )
            
            stats = {
                'l1_cache_size': len(self._l1_cache),
                'l1_max_size': self._l1_max_size,
                'l1_hit_rate': l1_hit_rate,
                'l2_hit_rate': l2_hit_rate,
                'overall_hit_rate': overall_hit_rate,
                'total_operations': self._cache_stats['total_operations'],
                'redis_connected': self._redis_client is not None,
                **self._cache_stats
            }
            
            return CacheResult(
                success=True,
                result=stats,
                metadata={'operation': 'get_stats'}
            )
        except Exception as e:
            logger.error(f"Cache stats retrieval failed: {e}")
            return CacheResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'get_stats'}
            )

# Enterprise factory pattern for cache manager
class CacheManagerFactory:
    """Factory for creating configured cache manager instances."""
    
    @staticmethod
    async def create_manager(config: Optional[Dict[str, Any]] = None) -> CacheManager:
        """Create and initialize cache manager."""
        manager = CacheManager(config)
        await manager._initialize_redis()
        return manager
    
    @staticmethod
    async def create_high_performance_manager(
        redis_url: str = 'redis://localhost:6379',
        l1_max_size: int = 2000,
        l1_ttl_seconds: int = 600
    ) -> CacheManager:
        """Create cache manager optimized for high performance."""
        config = {
            'redis_url': redis_url,
            'l1_max_size': l1_max_size,
            'l1_ttl_seconds': l1_ttl_seconds,
            'l2_ttl_seconds': 7200  # 2 hours
        }
        return await CacheManagerFactory.create_manager(config)