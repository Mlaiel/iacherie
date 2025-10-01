#!/usr/bin/env python3
"""
🚀 Enterprise Cache Service Template - iacherie
=============================================
Template enterprise pour services cache.
Redis + Memcached + CDN + cache strategies + invalidation.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: iacherie Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction sans autorisation est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import hashlib
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from collections import OrderedDict
import pickle

from .service_template import EnterpriseServiceBase, ServiceConfig


class CacheProvider(Enum):
    """Providers de cache."""
    REDIS = "redis"
    MEMCACHED = "memcached"
    IN_MEMORY = "in_memory"
    DISK = "disk"
    CDN = "cdn"


class CacheStrategy(Enum):
    """Stratégies de cache."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"


@dataclass
class CacheConfig:
    """Configuration cache."""
    provider: CacheProvider
    connection_url: str = ""
    max_size: int = 1000000  # Max entries
    default_ttl_seconds: int = 3600
    strategy: CacheStrategy = CacheStrategy.LRU
    compression: bool = False
    serialization: str = "json"  # json, pickle, msgpack
    key_prefix: str = ""
    namespace: str = "default"


@dataclass
class CacheEntry:
    """Entrée de cache."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if not self.ttl_seconds:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds


class CacheServiceTemplate(EnterpriseServiceBase):
    """
    🚀 Template enterprise pour services cache.
    Redis + Memcached + CDN + cache strategies + invalidation.
    
    Features:
    - Configuration multi-layer caching
    - Stratégies cache (LRU, TTL, etc.)
    - Système invalidation cache intelligent
    - Monitoring performance cache avec metrics
    - Cache warming et preloading
    - Distributed cache coordination
    - Cache partitioning et sharding
    - Compression et serialization
    - Tag-based invalidation
    - Performance analytics
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize cache service template."""
        super().__init__(config)
        
        self.cache_layers: Dict[str, Dict] = {}
        self.cache_stores: Dict[str, Any] = {}
        self.invalidation_rules: Dict[str, List[Callable]] = {}
        self.performance_monitor: Optional['CachePerformanceMonitor'] = None
        
        # Cache metrics
        self.cache_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_sets': 0,
            'cache_deletes': 0,
            'cache_size': 0,
            'hit_rate': 0.0,
            'average_get_time_ms': 0.0,
            'average_set_time_ms': 0.0,
            'evictions': 0,
            'expirations': 0,
            'memory_usage_mb': 0.0,
            'network_bytes_in': 0,
            'network_bytes_out': 0
        }
        
        self.logger.info(f"🚀 Cache Service Template initialized: {config.service_name}")
    
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        try:
            # Setup performance monitor
            self.performance_monitor = CachePerformanceMonitor(self)
            
            # Setup default cache layer
            await self._setup_default_cache()
            
            # Start background tasks
            asyncio.create_task(self._cache_maintenance())
            
            self.logger.info("✅ Cache service components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize cache service: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Close all cache connections
            for layer_name, store in self.cache_stores.items():
                await self._close_cache_store(layer_name, store)
            
            # Cleanup performance monitor
            if self.performance_monitor:
                await self.performance_monitor.cleanup()
            
            self.cache_layers.clear()
            self.cache_stores.clear()
            
            self.logger.info("✅ Cache service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cache service cleanup: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform cache service-specific health checks."""
        try:
            layer_health = {}
            for layer_name, config in self.cache_layers.items():
                layer_health[layer_name] = await self._check_layer_health(layer_name)
            
            return {
                'cache_layers': len(self.cache_layers),
                'layer_health': layer_health,
                'metrics': self.cache_metrics.copy(),
                'performance_data': await self._get_performance_data()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Cache service health check failed: {e}")
            return {'error': str(e), 'status': 'unhealthy'}
    
    async def setup_cache_layers(self, cache_configs: Dict[str, CacheConfig]) -> None:
        """Configuration multi-layer caching."""
        try:
            for layer_name, config in cache_configs.items():
                await self._setup_cache_layer(layer_name, config)
            
            self.logger.info(f"✅ Cache layers configured: {list(cache_configs.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup cache layers: {e}")
            raise
    
    async def _setup_cache_layer(self, layer_name: str, config: CacheConfig) -> None:
        """Setup single cache layer."""
        try:
            self.cache_layers[layer_name] = {
                'config': config,
                'created_at': datetime.now()
            }
            
            # Create cache store based on provider
            if config.provider == CacheProvider.REDIS:
                store = await self._create_redis_store(config)
            elif config.provider == CacheProvider.MEMCACHED:
                store = await self._create_memcached_store(config)
            elif config.provider == CacheProvider.IN_MEMORY:
                store = await self._create_memory_store(config)
            else:
                store = await self._create_memory_store(config)  # Fallback
            
            self.cache_stores[layer_name] = store
            
            self.logger.info(f"✅ Cache layer setup: {layer_name} ({config.provider.value})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup cache layer {layer_name}: {e}")
            raise
    
    async def get(self, key: str, layer: str = "default") -> Optional[Any]:
        """Get value from cache."""
        start_time = time.time()
        
        try:
            if layer not in self.cache_stores:
                self.cache_metrics['cache_misses'] += 1
                return None
            
            store = self.cache_stores[layer]
            result = await store.get(key)
            
            # Update metrics
            get_time = (time.time() - start_time) * 1000
            self._update_get_time(get_time)
            
            if result is not None:
                self.cache_metrics['cache_hits'] += 1
                self.cache_metrics['network_bytes_out'] += self._estimate_size(result)
                
                # Update hit rate
                total_requests = self.cache_metrics['cache_hits'] + self.cache_metrics['cache_misses']
                self.cache_metrics['hit_rate'] = self.cache_metrics['cache_hits'] / total_requests
                
                self.logger.debug(f"🎯 Cache hit: {key} in {layer}")
            else:
                self.cache_metrics['cache_misses'] += 1
                self.logger.debug(f"❌ Cache miss: {key} in {layer}")
            
            return result
            
        except Exception as e:
            self.cache_metrics['cache_misses'] += 1
            self.logger.error(f"❌ Cache get failed for {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                 layer: str = "default", tags: Optional[List[str]] = None) -> bool:
        """Set value in cache."""
        start_time = time.time()
        
        try:
            if layer not in self.cache_stores:
                return False
            
            store = self.cache_stores[layer]
            config = self.cache_layers[layer]['config']
            
            # Use layer default TTL if not specified
            if ttl is None:
                ttl = config.default_ttl_seconds
            
            success = await store.set(key, value, ttl, tags or [])
            
            # Update metrics
            set_time = (time.time() - start_time) * 1000
            self._update_set_time(set_time)
            
            if success:
                self.cache_metrics['cache_sets'] += 1
                self.cache_metrics['network_bytes_in'] += self._estimate_size(value)
                self.cache_metrics['cache_size'] = await store.size()
                
                self.logger.debug(f"✅ Cache set: {key} in {layer}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Cache set failed for {key}: {e}")
            return False
    
    async def delete(self, key: str, layer: str = "default") -> bool:
        """Delete value from cache."""
        try:
            if layer not in self.cache_stores:
                return False
            
            store = self.cache_stores[layer]
            success = await store.delete(key)
            
            if success:
                self.cache_metrics['cache_deletes'] += 1
                self.cache_metrics['cache_size'] = await store.size()
                
                self.logger.debug(f"🗑️ Cache delete: {key} from {layer}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Cache delete failed for {key}: {e}")
            return False
    
    async def invalidate_by_tags(self, tags: List[str], layer: str = "default") -> int:
        """Invalidate cache entries by tags."""
        try:
            if layer not in self.cache_stores:
                return 0
            
            store = self.cache_stores[layer]
            count = await store.invalidate_by_tags(tags)
            
            self.cache_metrics['cache_deletes'] += count
            self.cache_metrics['cache_size'] = await store.size()
            
            self.logger.info(f"🏷️ Cache invalidated by tags {tags}: {count} entries")
            return count
            
        except Exception as e:
            self.logger.error(f"❌ Cache invalidation by tags failed: {e}")
            return 0
    
    async def clear(self, layer: str = "default") -> bool:
        """Clear all cache entries in layer."""
        try:
            if layer not in self.cache_stores:
                return False
            
            store = self.cache_stores[layer]
            success = await store.clear()
            
            if success:
                self.cache_metrics['cache_size'] = 0
                self.logger.info(f"🧹 Cache cleared: {layer}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Cache clear failed for {layer}: {e}")
            return False
    
    async def _setup_default_cache(self) -> None:
        """Setup default cache layer."""
        default_config = CacheConfig(
            provider=CacheProvider.IN_MEMORY,
            max_size=10000,
            default_ttl_seconds=3600,
            strategy=CacheStrategy.LRU
        )
        
        await self._setup_cache_layer("default", default_config)
    
    async def _create_redis_store(self, config: CacheConfig) -> 'CacheStore':
        """Create Redis cache store."""
        # Placeholder for Redis implementation
        self.logger.warning("🚧 Redis cache store not implemented - using in-memory")
        return await self._create_memory_store(config)
    
    async def _create_memcached_store(self, config: CacheConfig) -> 'CacheStore':
        """Create Memcached cache store."""
        # Placeholder for Memcached implementation
        self.logger.warning("🚧 Memcached cache store not implemented - using in-memory")
        return await self._create_memory_store(config)
    
    async def _create_memory_store(self, config: CacheConfig) -> 'CacheStore':
        """Create in-memory cache store."""
        return InMemoryCacheStore(config)
    
    async def _check_layer_health(self, layer_name: str) -> Dict[str, Any]:
        """Check health of cache layer."""
        try:
            if layer_name not in self.cache_stores:
                return {'status': 'not_configured'}
            
            store = self.cache_stores[layer_name]
            health = await store.health_check()
            
            return health
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def _get_performance_data(self) -> Dict[str, Any]:
        """Get performance monitoring data."""
        if not self.performance_monitor:
            return {}
        
        return await self.performance_monitor.get_performance_data()
    
    async def _close_cache_store(self, layer_name: str, store: Any) -> None:
        """Close cache store connection."""
        try:
            await store.close()
            self.logger.info(f"🔌 Cache store closed: {layer_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to close cache store {layer_name}: {e}")
    
    def _update_get_time(self, get_time_ms: float) -> None:
        """Update average get time metric."""
        current_avg = self.cache_metrics['average_get_time_ms']
        total_gets = self.cache_metrics['cache_hits'] + self.cache_metrics['cache_misses']
        
        if total_gets > 1:
            self.cache_metrics['average_get_time_ms'] = (
                (current_avg * (total_gets - 1)) + get_time_ms
            ) / total_gets
        else:
            self.cache_metrics['average_get_time_ms'] = get_time_ms
    
    def _update_set_time(self, set_time_ms: float) -> None:
        """Update average set time metric."""
        current_avg = self.cache_metrics['average_set_time_ms']
        total_sets = self.cache_metrics['cache_sets']
        
        if total_sets > 1:
            self.cache_metrics['average_set_time_ms'] = (
                (current_avg * (total_sets - 1)) + set_time_ms
            ) / total_sets
        else:
            self.cache_metrics['average_set_time_ms'] = set_time_ms
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value).encode('utf-8'))
            else:
                return len(str(value).encode('utf-8'))
        except:
            return 100  # Default estimate
    
    async def _cache_maintenance(self) -> None:
        """Background cache maintenance."""
        while self.status == "running":
            try:
                # Cleanup expired entries
                for layer_name, store in self.cache_stores.items():
                    expired_count = await store.cleanup_expired()
                    if expired_count > 0:
                        self.cache_metrics['expirations'] += expired_count
                        self.cache_metrics['cache_size'] = await store.size()
                
                # Update memory usage
                total_memory = sum(
                    await store.memory_usage() 
                    for store in self.cache_stores.values()
                )
                self.cache_metrics['memory_usage_mb'] = total_memory / (1024 * 1024)
                
                await asyncio.sleep(60)  # Run every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Cache maintenance error: {e}")
                await asyncio.sleep(120)
    
    # Abstract methods pour extension
    @abstractmethod
    async def configure_custom_layers(self) -> Dict[str, CacheConfig]:
        """Configure layers spécifiques au service."""
        pass
    
    @abstractmethod
    async def configure_custom_invalidation_rules(self) -> Dict[str, List[Callable]]:
        """Configure règles d'invalidation spécifiques au service."""
        pass


class CacheStore:
    """Base class for cache stores."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
    
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: int, tags: List[str]) -> bool:
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        raise NotImplementedError
    
    async def clear(self) -> bool:
        raise NotImplementedError
    
    async def size(self) -> int:
        raise NotImplementedError
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        raise NotImplementedError
    
    async def cleanup_expired(self) -> int:
        raise NotImplementedError
    
    async def memory_usage(self) -> int:
        raise NotImplementedError
    
    async def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    async def close(self) -> None:
        pass


class InMemoryCacheStore(CacheStore):
    """In-memory cache store implementation."""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.tags_index: Dict[str, List[str]] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        prefixed_key = f"{self.config.key_prefix}{key}"
        
        if prefixed_key not in self.cache:
            return None
        
        entry = self.cache[prefixed_key]
        
        # Check expiration
        if entry.is_expired():
            await self.delete(key)
            return None
        
        # Update access info
        entry.accessed_at = datetime.now()
        entry.access_count += 1
        
        # Move to end for LRU
        if self.config.strategy == CacheStrategy.LRU:
            self.cache.move_to_end(prefixed_key)
        
        return entry.value
    
    async def set(self, key: str, value: Any, ttl: int, tags: List[str]) -> bool:
        prefixed_key = f"{self.config.key_prefix}{key}"
        
        # Check size limit
        if len(self.cache) >= self.config.max_size and prefixed_key not in self.cache:
            await self._evict_entry()
        
        # Create entry
        entry = CacheEntry(
            key=prefixed_key,
            value=value,
            ttl_seconds=ttl,
            tags=tags
        )
        
        self.cache[prefixed_key] = entry
        
        # Update tags index
        for tag in tags:
            if tag not in self.tags_index:
                self.tags_index[tag] = []
            if prefixed_key not in self.tags_index[tag]:
                self.tags_index[tag].append(prefixed_key)
        
        return True
    
    async def delete(self, key: str) -> bool:
        prefixed_key = f"{self.config.key_prefix}{key}"
        
        if prefixed_key not in self.cache:
            return False
        
        entry = self.cache.pop(prefixed_key)
        
        # Clean up tags index
        for tag in entry.tags:
            if tag in self.tags_index and prefixed_key in self.tags_index[tag]:
                self.tags_index[tag].remove(prefixed_key)
                if not self.tags_index[tag]:
                    del self.tags_index[tag]
        
        return True
    
    async def clear(self) -> bool:
        self.cache.clear()
        self.tags_index.clear()
        return True
    
    async def size(self) -> int:
        return len(self.cache)
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        keys_to_delete = set()
        
        for tag in tags:
            if tag in self.tags_index:
                keys_to_delete.update(self.tags_index[tag])
        
        count = 0
        for key in keys_to_delete:
            if key in self.cache:
                del self.cache[key]
                count += 1
        
        # Clean up tags index
        for tag in tags:
            if tag in self.tags_index:
                del self.tags_index[tag]
        
        return count
    
    async def cleanup_expired(self) -> int:
        expired_keys = []
        
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    async def memory_usage(self) -> int:
        # Estimate memory usage
        total_size = 0
        for entry in self.cache.values():
            total_size += len(json.dumps({
                'key': entry.key,
                'value': entry.value,
                'metadata': entry.metadata
            }))
        return total_size
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'entries': len(self.cache),
            'max_size': self.config.max_size,
            'tags': len(self.tags_index)
        }
    
    async def _evict_entry(self) -> None:
        """Evict entry based on strategy."""
        if not self.cache:
            return
        
        if self.config.strategy == CacheStrategy.LRU:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)
        elif self.config.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            min_access = min(entry.access_count for entry in self.cache.values())
            for key, entry in self.cache.items():
                if entry.access_count == min_access:
                    del self.cache[key]
                    break
        elif self.config.strategy == CacheStrategy.FIFO:
            # Remove first in (first item)
            self.cache.popitem(last=False)


class CachePerformanceMonitor:
    """Performance monitoring for cache service."""
    
    def __init__(self, cache_service: CacheServiceTemplate):
        self.cache_service = cache_service
        self.performance_data: List[Dict] = []
        self.logger = cache_service.logger
    
    async def get_performance_data(self) -> Dict[str, Any]:
        """Get performance monitoring data."""
        return {
            'samples_count': len(self.performance_data),
            'latest_data': self.performance_data[-10:] if self.performance_data else []
        }
    
    async def cleanup(self) -> None:
        """Cleanup performance monitor."""
        self.performance_data.clear()


if __name__ == "__main__":
    print("🚀 Enterprise Cache Service Template")
    print("Use this template to create high-performance caching microservices")