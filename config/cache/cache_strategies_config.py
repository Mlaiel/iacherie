"""Cache Strategies Configuration for IA-Influencer Agent Platform
===============================================================

Advanced caching strategies implementation including write-through,
write-back, read-through, and cache-aside patterns for optimal performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, validator


class CacheStrategy(str, Enum):
    """
Cache strategy patterns"""

    CACHE_ASIDE = "cache_aside"  # Lazy loading
    READ_THROUGH = "read_through"  # Cache loads data on miss
    WRITE_THROUGH = "write_through"  # Cache and DB updated together
    WRITE_BEHIND = "write_behind"  # Cache updated first, DB later
    REFRESH_AHEAD = "refresh_ahead"  # Proactive cache refresh


class EvictionPolicy(str, Enum):
    """Cache eviction policies"""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live based
    RANDOM = "random"  # Random eviction
    CUSTOM = "custom"  # Custom eviction logic


class ConsistencyLevel(str, Enum):
    """Cache consistency levels"""

    STRONG = "strong"  # Immediate consistency
    EVENTUAL = "eventual"  # Eventual consistency
    WEAK = "weak"  # No consistency guarantees
    SESSION = "session"  # Session consistency


@dataclass
class CacheKeyConfig:
    """Cache key configuration"""
    namespace: str = "ia_agent"
    separator: str = ":"
    include_version: bool = True
    include_tenant: bool = True
    hash_long_keys: bool = True
    max_key_length: int = 250
    
    def generate_key(self, *parts: str, tenant_id: Optional[str] = None, 
                    version: Optional[str] = None) -> str:
        """Generate cache key with namespace and separators"""
        key_parts = [self.namespace]
        
        if self.include_tenant and tenant_id:
            key_parts.append(f"tenant_{tenant_id}")
        
        if self.include_version and version:
            key_parts.append(f"v{version}")
        
        key_parts.extend(parts)
        key = self.separator.join(key_parts)
        
        # Hash long keys
        if self.hash_long_keys and len(key) > self.max_key_length:
            import hashlib
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{self.namespace}:hash:{key_hash}"
        
        return key


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    errors: int = 0
    total_time: float = 0.0
    
    @property
    def hit_ratio(self) -> float:
        total_requests = self.hits + self.misses
        return self.hits / total_requests if total_requests > 0 else 0.0
    
    @property
    def average_time(self) -> float:
        total_operations = self.hits + self.misses + self.sets + self.deletes
        return self.total_time / total_operations if total_operations > 0 else 0.0


class BaseCacheStrategy(ABC):
    """
Abstract base class for cache strategies"""
    
    def __init__(self, config: 'CacheStrategiesConfig'):
        self.config = config
        self.metrics = CacheMetrics()
    
    @abstractmethod
    async def get(self, key: str, **kwargs) -> Any:
        """
Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """
Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str, **kwargs) -> bool:
        """
Delete value from cache"""
        pass
    
    def track_operation(self, operation: str, duration: float):
        """
Track cache operation metrics"""
        self.metrics.total_time += duration
        
        if operation == "hit":
            self.metrics.hits += 1
        elif operation == "miss":
            self.metrics.misses += 1
        elif operation == "set":
            self.metrics.sets += 1
        elif operation == "delete":
            self.metrics.deletes += 1
        elif operation == "error":
            self.metrics.errors += 1


class CacheAsideStrategy(BaseCacheStrategy):
    """Cache-aside (lazy loading) strategy implementation"""
    
    async def get(self, key: str, loader: Optional[Callable] = None, **kwargs) -> Any:
        """
Get value with cache-aside pattern"""
        start_time = time.time()
        
        try:
            # Try to get from cache first
            value = await self._get_from_cache(key)
            
            if value is not None:
                self.track_operation("hit", time.time() - start_time)
                return value
            
            # Cache miss - load from source if loader provided
            if loader:
                value = await self._load_with_loader(loader, key, **kwargs)
                if value is not None:
                    await self.set(key, value)
                    self.track_operation("miss", time.time() - start_time)
                    return value
            
            self.track_operation("miss", time.time() - start_time)
            return None
            
        except Exception:
            self.track_operation("error", time.time() - start_time)
            # Fallback to loader on cache error
            if loader:
                return await self._load_with_loader(loader, key, **kwargs)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Set value in cache"""
        start_time = time.time()
        
        try:
            result = await self._set_to_cache(key, value, ttl)
            self.track_operation("set", time.time() - start_time)
            return result
        except Exception:
            self.track_operation("error", time.time() - start_time)
            return False
    
    async def delete(self, key: str, **kwargs) -> bool:
        """Delete value from cache"""
        start_time = time.time()
        
        try:
            result = await self._delete_from_cache(key)
            self.track_operation("delete", time.time() - start_time)
            return result
        except Exception:
            self.track_operation("error", time.time() - start_time)
            return False
    
    async def _get_from_cache(self, key: str) -> Any:
        """Get value from cache backend"""
        # Implementation depends on cache backend
        return None
    
    async def _set_to_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
Set value to cache backend"""
        # Implementation depends on cache backend
        return True
    
    async def _delete_from_cache(self, key: str) -> bool:
        """
Delete value from cache backend"""
        # Implementation depends on cache backend
        return True
    
    async def _load_with_loader(self, loader: Callable, key: str, **kwargs) -> Any:
        """
Load data using provided loader function"""
        if asyncio.iscoroutinefunction(loader):
            return await loader(key, **kwargs)
        else:
            # Run synchronous loader in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, loader, key)


class WriteThroughStrategy(BaseCacheStrategy):
    """
Write-through strategy implementation"""
    
    def __init__(self, config: 'CacheStrategiesConfig', data_store: Callable):
        super().__init__(config)
        self.data_store = data_store
    
    async def get(self, key: str, **kwargs) -> Any:
        """
Get value from cache, fallback to data store"""
        start_time = time.time()
        
        try:
            # Try cache first
            value = await self._get_from_cache(key)
            if value is not None:
                self.track_operation("hit", time.time() - start_time)
                return value
            
            # Load from data store
            value = await self._load_from_store(key)
            if value is not None:
                await self._set_to_cache(key, value)
                self.track_operation("miss", time.time() - start_time)
                return value
            
            self.track_operation("miss", time.time() - start_time)
            return None
            
        except Exception:
            self.track_operation("error", time.time() - start_time)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Set value to both cache and data store"""
        start_time = time.time()
        
        try:
            # Write to data store first
            store_success = await self._write_to_store(key, value)
            
            if store_success:
                # Then write to cache
                cache_success = await self._set_to_cache(key, value, ttl)
                self.track_operation("set", time.time() - start_time)
                return cache_success
            
            self.track_operation("error", time.time() - start_time)
            return False
            
        except Exception:
            self.track_operation("error", time.time() - start_time)
            return False
    
    async def delete(self, key: str, **kwargs) -> bool:
        """Delete from both cache and data store"""
        start_time = time.time()
        
        try:
            # Delete from data store first
            store_success = await self._delete_from_store(key)
            
            # Delete from cache regardless of store result
            cache_success = await self._delete_from_cache(key)
            
            self.track_operation("delete", time.time() - start_time)
            return store_success and cache_success
            
        except Exception:
            self.track_operation("error", time.time() - start_time)
            return False
    
    async def _load_from_store(self, key: str) -> Any:
        """Load data from data store"""
        if asyncio.iscoroutinefunction(self.data_store.get):
            return await self.data_store.get(key)
        else:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, self.data_store.get, key)
    
    async def _write_to_store(self, key: str, value: Any) -> bool:
        """
Write data to data store"""
        try:
            if asyncio.iscoroutinefunction(self.data_store.set):
                return await self.data_store.set(key, value)
            else:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    return await loop.run_in_executor(executor, self.data_store.set, key, value)
        except Exception:
            return False
    
    async def _delete_from_store(self, key: str) -> bool:
        """
Delete data from data store"""
        try:
            if asyncio.iscoroutinefunction(self.data_store.delete):
                return await self.data_store.delete(key)
            else:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    return await loop.run_in_executor(executor, self.data_store.delete, key)
        except Exception:
            return False


class CacheStrategiesConfig(BaseModel):
    """
    Comprehensive cache strategies configuration
    """
    
    # Strategy selection
    primary_strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    fallback_strategy: Optional[CacheStrategy] = CacheStrategy.READ_THROUGH
    
    # Key configuration
    key_config: CacheKeyConfig = CacheKeyConfig()
    
    # Eviction policy
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    
    # Consistency settings
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    
    # Performance settings
    batch_size: int = 100
    concurrent_requests: int = 10
    timeout_seconds: float = 5.0
    retry_attempts: int = 3
    retry_delay: float = 0.1
    
    # Multi-level caching
    enable_l1_cache: bool = True  # In-memory cache
    enable_l2_cache: bool = True  # Distributed cache
    l1_cache_size: int = 1000
    l1_cache_ttl: int = 300  # 5 minutes
    
    # Write strategies
    write_buffer_size: int = 1000
    write_buffer_timeout: float = 10.0
    write_behind_delay: float = 1.0
    
    # Refresh ahead settings
    refresh_ahead_factor: float = 0.8  # Refresh when 80% of TTL elapsed
    refresh_ahead_workers: int = 2
    
    # Monitoring and metrics
    enable_metrics: bool = True
    metrics_collection_interval: int = 60
    slow_operation_threshold: float = 1.0
    
    # Circuit breaker
    enable_circuit_breaker: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 30
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v <= 0:
            raise ValueError("Batch size must be positive")
        return v
    
    @validator('refresh_ahead_factor')
    def validate_refresh_ahead_factor(cls, v):
        if not 0.0 < v < 1.0:
            raise ValueError("Refresh ahead factor must be between 0 and 1")
        return v
    
    def get_strategy_instance(self, data_store: Optional[Callable] = None) -> BaseCacheStrategy:
        """Get strategy instance based on configuration"""
        if self.primary_strategy == CacheStrategy.CACHE_ASIDE:
            return CacheAsideStrategy(self)
        elif self.primary_strategy == CacheStrategy.WRITE_THROUGH:
            if not data_store:
                raise ValueError("Data store required for write-through strategy")
            return WriteThroughStrategy(self, data_store)
        else:
            # Default to cache-aside
            return CacheAsideStrategy(self)
    
    def should_refresh_ahead(self, ttl_remaining: float, original_ttl: float) -> bool:
        """Check if key should be refreshed ahead of expiry"""
        if original_ttl <= 0:
            return False
        
        elapsed_ratio = (original_ttl - ttl_remaining) / original_ttl
        return elapsed_ratio >= self.refresh_ahead_factor
    
    def get_l1_cache_config(self) -> Dict[str, Any]:
        """
Get L1 (in-memory) cache configuration"""
        return {
            "enabled": self.enable_l1_cache,
            "size": self.l1_cache_size,
            "ttl": self.l1_cache_ttl,
            "eviction_policy": self.eviction_policy
        }
    
    def get_l2_cache_config(self) -> Dict[str, Any]:
        """Get L2 (distributed) cache configuration"""
        return {
            "enabled": self.enable_l2_cache,
            "consistency_level": self.consistency_level,
            "timeout": self.timeout_seconds,
            "retry_attempts": self.retry_attempts
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-related configuration"""
        return {
            "batch_size": self.batch_size,
            "concurrent_requests": self.concurrent_requests,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "slow_operation_threshold": self.slow_operation_threshold
        }


# Strategy factory for different use cases
class CacheStrategyFactory:
    """Factory for creating cache strategy configurations"""
    
    @staticmethod
    def create_high_performance_config() -> CacheStrategiesConfig:
        """
Configuration optimized for high performance"""
        return CacheStrategiesConfig(
            primary_strategy=CacheStrategy.CACHE_ASIDE,
            enable_l1_cache=True,
            enable_l2_cache=True,
            l1_cache_size=5000,
            l1_cache_ttl=300,
            concurrent_requests=50,
            batch_size=500,
            eviction_policy=EvictionPolicy.LRU,
            consistency_level=ConsistencyLevel.EVENTUAL
        )
    
    @staticmethod
    def create_consistency_focused_config() -> CacheStrategiesConfig:
        """
Configuration optimized for data consistency"""
        return CacheStrategiesConfig(
            primary_strategy=CacheStrategy.WRITE_THROUGH,
            consistency_level=ConsistencyLevel.STRONG,
            enable_l1_cache=False,  # Disable L1 for consistency
            enable_l2_cache=True,
            retry_attempts=5,
            timeout_seconds=10.0,
            enable_circuit_breaker=True
        )
    
    @staticmethod
    def create_memory_optimized_config() -> CacheStrategiesConfig:
        """
Configuration optimized for memory usage"""
        return CacheStrategiesConfig(
            primary_strategy=CacheStrategy.CACHE_ASIDE,
            eviction_policy=EvictionPolicy.LFU,
            enable_l1_cache=True,
            l1_cache_size=1000,
            l1_cache_ttl=600,
            enable_l2_cache=True,
            batch_size=50,
            concurrent_requests=10
        )


# Default configurations
DEFAULT_CONFIG = CacheStrategiesConfig()

PRODUCTION_CONFIG = CacheStrategyFactory.create_high_performance_config()

DEVELOPMENT_CONFIG = CacheStrategiesConfig(
    enable_metrics=True,
    slow_operation_threshold=0.5,
    enable_circuit_breaker=False,
    l1_cache_size=500
)

TESTING_CONFIG = CacheStrategiesConfig(
    enable_l1_cache=False,
    enable_l2_cache=True,
    enable_metrics=False,
    timeout_seconds=1.0,
    retry_attempts=1
)
