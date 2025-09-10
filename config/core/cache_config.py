#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Cache Configuration Module
====================================

Enterprise-grade caching configuration for the Ainflue platform.
Handles multi-level caching, distributed caching, cache invalidation,
performance optimization, and intelligent cache management strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import redis
import memcache
import time
from pathlib import Path
import pickle
import json
import hashlib

class CacheType(str, Enum):
    """Cache implementation types"""
    IN_MEMORY = "in_memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    HYBRID = "hybrid"
    DISTRIBUTED = "distributed"

class CacheLevel(str, Enum):
    """Cache hierarchy levels"""
    L1 = "l1"  # CPU cache-like (in-memory)
    L2 = "l2"  # Redis cache
    L3 = "l3"  # Distributed cache
    L4 = "l4"  # Persistent cache (disk)

class EvictionPolicy(str, Enum):
    """Cache eviction policies"""
    LRU = "lru"          # Least Recently Used
    LFU = "lfu"          # Least Frequently Used
    FIFO = "fifo"        # First In, First Out
    LIFO = "lifo"        # Last In, First Out
    RANDOM = "random"    # Random eviction
    TTL = "ttl"          # Time To Live based

class CacheStrategy(str, Enum):
    """Cache loading strategies"""
    LAZY_LOADING = "lazy_loading"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    REFRESH_AHEAD = "refresh_ahead"

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    load_count: int = 0
    load_time_total: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 1.0 - self.hit_rate
    
    @property
    def average_load_time(self) -> float:
        """Calculate average load time"""
        return self.load_time_total / self.load_count if self.load_count > 0 else 0.0

@dataclass
class L1CacheConfig:
    """L1 Cache (In-Memory) configuration"""
    max_size: int = 1000
    ttl: int = 300  # 5 minutes
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    enable_compression: bool = False
    compression_threshold: int = 1024  # bytes
    
    def get_config(self) -> Dict[str, Any]:
        """Get L1 cache configuration"""
        return {
            "max_size": self.max_size,
            "ttl": self.ttl,
            "eviction_policy": self.eviction_policy.value,
            "enable_compression": self.enable_compression,
            "compression_threshold": self.compression_threshold
        }

@dataclass
class L2CacheConfig:
    """L2 Cache (Redis) configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 100
    connection_pool_size: int = 50
    ttl: int = 3600  # 1 hour
    
    # Redis specific settings
    decode_responses: bool = False
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=lambda: {})
    
    # Clustering
    enable_cluster: bool = False
    cluster_nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_config(self) -> Dict[str, Any]:
        """Get L2 cache configuration"""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "password": self.password,
            "max_connections": self.max_connections,
            "connection_pool_size": self.connection_pool_size,
            "ttl": self.ttl,
            "decode_responses": self.decode_responses,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "socket_keepalive": self.socket_keepalive,
            "socket_keepalive_options": self.socket_keepalive_options,
            "enable_cluster": self.enable_cluster,
            "cluster_nodes": self.cluster_nodes
        }

@dataclass
class L3CacheConfig:
    """L3 Cache (Distributed) configuration"""
    cache_type: CacheType = CacheType.MEMCACHED
    servers: List[str] = field(default_factory=lambda: ["localhost:11211"])
    ttl: int = 7200  # 2 hours
    
    # Memcached specific
    binary_protocol: bool = True
    behaviors: Dict[str, Any] = field(default_factory=dict)
    
    # Distributed cache settings
    consistent_hashing: bool = True
    replication_factor: int = 2
    
    def get_config(self) -> Dict[str, Any]:
        """Get L3 cache configuration"""
        return {
            "cache_type": self.cache_type.value,
            "servers": self.servers,
            "ttl": self.ttl,
            "binary_protocol": self.binary_protocol,
            "behaviors": self.behaviors,
            "consistent_hashing": self.consistent_hashing,
            "replication_factor": self.replication_factor
        }

@dataclass
class L4CacheConfig:
    """L4 Cache (Persistent/Disk) configuration"""
    cache_dir: str = "/var/cache/ainflue"
    max_disk_size: str = "10GB"
    ttl: int = 86400  # 24 hours
    compression_enabled: bool = True
    encryption_enabled: bool = True
    
    # File organization
    subdirectory_levels: int = 2
    files_per_directory: int = 1000
    
    def get_config(self) -> Dict[str, Any]:
        """Get L4 cache configuration"""
        return {
            "cache_dir": self.cache_dir,
            "max_disk_size": self.max_disk_size,
            "ttl": self.ttl,
            "compression_enabled": self.compression_enabled,
            "encryption_enabled": self.encryption_enabled,
            "subdirectory_levels": self.subdirectory_levels,
            "files_per_directory": self.files_per_directory
        }

class BusinessCacheConfig:
    """Business logic specific cache configuration"""
    
    def __init__(self):
        # Creator and content caching
        self.creator_profile_ttl = 1800  # 30 minutes
        self.content_metadata_ttl = 3600  # 1 hour
        self.content_thumbnails_ttl = 86400  # 24 hours
        
        # AI and ML model caching
        self.model_inference_ttl = 300  # 5 minutes
        self.ai_analysis_ttl = 1800  # 30 minutes
        self.training_data_ttl = 7200  # 2 hours
        
        # SEO and analytics caching
        self.seo_analysis_ttl = 3600  # 1 hour
        self.analytics_data_ttl = 900  # 15 minutes
        self.trending_data_ttl = 300  # 5 minutes
        
        # Monetization caching
        self.revenue_calculations_ttl = 1800  # 30 minutes
        self.payment_status_ttl = 60  # 1 minute
        self.subscription_data_ttl = 3600  # 1 hour
        
        # Collaboration caching
        self.collaboration_matches_ttl = 900  # 15 minutes
        self.collaboration_history_ttl = 3600  # 1 hour
        
        # Protection and security caching
        self.copyright_fingerprints_ttl = 86400  # 24 hours
        self.violation_reports_ttl = 1800  # 30 minutes
        self.security_tokens_ttl = 900  # 15 minutes
    
    def get_business_cache_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get business-specific cache rules"""
        return {
            "creator_data": {
                "profiles": {"ttl": self.creator_profile_ttl, "level": "L2"},
                "content_metadata": {"ttl": self.content_metadata_ttl, "level": "L2"},
                "thumbnails": {"ttl": self.content_thumbnails_ttl, "level": "L3"}
            },
            "ai_ml": {
                "model_inference": {"ttl": self.model_inference_ttl, "level": "L1"},
                "ai_analysis": {"ttl": self.ai_analysis_ttl, "level": "L2"},
                "training_data": {"ttl": self.training_data_ttl, "level": "L3"}
            },
            "seo_analytics": {
                "seo_analysis": {"ttl": self.seo_analysis_ttl, "level": "L2"},
                "analytics_data": {"ttl": self.analytics_data_ttl, "level": "L1"},
                "trending_data": {"ttl": self.trending_data_ttl, "level": "L1"}
            },
            "monetization": {
                "revenue_calculations": {"ttl": self.revenue_calculations_ttl, "level": "L2"},
                "payment_status": {"ttl": self.payment_status_ttl, "level": "L1"},
                "subscription_data": {"ttl": self.subscription_data_ttl, "level": "L2"}
            },
            "collaboration": {
                "matches": {"ttl": self.collaboration_matches_ttl, "level": "L2"},
                "history": {"ttl": self.collaboration_history_ttl, "level": "L3"}
            },
            "protection": {
                "copyright_fingerprints": {"ttl": self.copyright_fingerprints_ttl, "level": "L3"},
                "violation_reports": {"ttl": self.violation_reports_ttl, "level": "L2"},
                "security_tokens": {"ttl": self.security_tokens_ttl, "level": "L1"}
            }
        }

class CacheConfiguration:
    """Main cache configuration manager"""
    
    def __init__(self, strategy: CacheStrategy = CacheStrategy.LAZY_LOADING):
        """Initialize cache configuration"""
        self.strategy = strategy
        
        # Cache level configurations
        self.l1_config = L1CacheConfig()
        self.l2_config = L2CacheConfig()
        self.l3_config = L3CacheConfig()
        self.l4_config = L4CacheConfig()
        
        # Business cache configuration
        self.business_config = BusinessCacheConfig()
        
        # Cache instances
        self.cache_instances: Dict[CacheLevel, Any] = {}
        
        # Metrics tracking
        self.metrics: Dict[CacheLevel, CacheMetrics] = {
            level: CacheMetrics() for level in CacheLevel
        }
        
        self._initialize_cache_instances()
    
    def _initialize_cache_instances(self):
        """Initialize cache instances"""
        # L1 Cache (In-Memory)
        self.cache_instances[CacheLevel.L1] = {}
        
        # L2 Cache (Redis)
        try:
            self.cache_instances[CacheLevel.L2] = redis.Redis(
                host=self.l2_config.host,
                port=self.l2_config.port,
                db=self.l2_config.db,
                password=self.l2_config.password,
                decode_responses=self.l2_config.decode_responses,
                socket_timeout=self.l2_config.socket_timeout,
                socket_connect_timeout=self.l2_config.socket_connect_timeout,
                socket_keepalive=self.l2_config.socket_keepalive
            )
        except Exception as e:
            print(f"Failed to initialize Redis cache: {e}")
            self.cache_instances[CacheLevel.L2] = None
        
        # L3 Cache (Memcached)
        try:
            self.cache_instances[CacheLevel.L3] = memcache.Client(
                self.l3_config.servers,
                binary=self.l3_config.binary_protocol
            )
        except Exception as e:
            print(f"Failed to initialize Memcached cache: {e}")
            self.cache_instances[CacheLevel.L3] = None
        
        # L4 Cache (Disk)
        cache_dir = Path(self.l4_config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_instances[CacheLevel.L4] = cache_dir
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache (multi-level lookup)"""
        # Try L1 cache first
        value = await self._get_from_l1(key)
        if value is not None:
            self.metrics[CacheLevel.L1].hit_count += 1
            return value
        self.metrics[CacheLevel.L1].miss_count += 1
        
        # Try L2 cache
        value = await self._get_from_l2(key)
        if value is not None:
            self.metrics[CacheLevel.L2].hit_count += 1
            # Populate L1 cache
            await self._set_to_l1(key, value, self.l1_config.ttl)
            return value
        self.metrics[CacheLevel.L2].miss_count += 1
        
        # Try L3 cache
        value = await self._get_from_l3(key)
        if value is not None:
            self.metrics[CacheLevel.L3].hit_count += 1
            # Populate L1 and L2 caches
            await self._set_to_l1(key, value, self.l1_config.ttl)
            await self._set_to_l2(key, value, self.l2_config.ttl)
            return value
        self.metrics[CacheLevel.L3].miss_count += 1
        
        # Try L4 cache
        value = await self._get_from_l4(key)
        if value is not None:
            self.metrics[CacheLevel.L4].hit_count += 1
            # Populate all upper level caches
            await self._set_to_l1(key, value, self.l1_config.ttl)
            await self._set_to_l2(key, value, self.l2_config.ttl)
            await self._set_to_l3(key, value, self.l3_config.ttl)
            return value
        self.metrics[CacheLevel.L4].miss_count += 1
        
        return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache (all levels)"""
        # Set in all cache levels based on strategy
        if self.strategy in [CacheStrategy.WRITE_THROUGH, CacheStrategy.REFRESH_AHEAD]:
            await self._set_to_l1(key, value, ttl or self.l1_config.ttl)
            await self._set_to_l2(key, value, ttl or self.l2_config.ttl)
            await self._set_to_l3(key, value, ttl or self.l3_config.ttl)
            await self._set_to_l4(key, value, ttl or self.l4_config.ttl)
        elif self.strategy == CacheStrategy.LAZY_LOADING:
            # Only set in L1 cache for lazy loading
            await self._set_to_l1(key, value, ttl or self.l1_config.ttl)
    
    async def delete(self, key: str):
        """Delete key from all cache levels"""
        await self._delete_from_l1(key)
        await self._delete_from_l2(key)
        await self._delete_from_l3(key)
        await self._delete_from_l4(key)
    
    async def clear(self, level: Optional[CacheLevel] = None):
        """Clear cache (specific level or all levels)"""
        if level:
            if level == CacheLevel.L1:
                self.cache_instances[CacheLevel.L1].clear()
            elif level == CacheLevel.L2 and self.cache_instances[CacheLevel.L2]:
                self.cache_instances[CacheLevel.L2].flushdb()
            elif level == CacheLevel.L3 and self.cache_instances[CacheLevel.L3]:
                self.cache_instances[CacheLevel.L3].flush_all()
            elif level == CacheLevel.L4:
                cache_dir = self.cache_instances[CacheLevel.L4]
                for file_path in cache_dir.glob("**/*"):
                    if file_path.is_file():
                        file_path.unlink()
        else:
            # Clear all levels
            for cache_level in CacheLevel:
                await self.clear(cache_level)
    
    # L1 Cache operations (In-Memory)
    async def _get_from_l1(self, key: str) -> Any:
        """Get from L1 cache"""
        cache = self.cache_instances[CacheLevel.L1]
        entry = cache.get(key)
        if entry and entry['expires'] > time.time():
            return entry['value']
        elif entry:
            # Expired entry
            del cache[key]
        return None
    
    async def _set_to_l1(self, key: str, value: Any, ttl: int):
        """Set to L1 cache"""
        cache = self.cache_instances[CacheLevel.L1]
        cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        
        # Apply eviction policy if cache is full
        if len(cache) > self.l1_config.max_size:
            await self._evict_from_l1()
    
    async def _delete_from_l1(self, key: str):
        """Delete from L1 cache"""
        cache = self.cache_instances[CacheLevel.L1]
        cache.pop(key, None)
    
    async def _evict_from_l1(self):
        """Evict entries from L1 cache based on policy"""
        cache = self.cache_instances[CacheLevel.L1]
        if self.l1_config.eviction_policy == EvictionPolicy.LRU:
            # Remove oldest accessed entry
            oldest_key = min(cache.keys(), key=lambda k: cache[k].get('last_access', 0))
            del cache[oldest_key]
        self.metrics[CacheLevel.L1].eviction_count += 1
    
    # L2 Cache operations (Redis)
    async def _get_from_l2(self, key: str) -> Any:
        """Get from L2 cache"""
        redis_client = self.cache_instances[CacheLevel.L2]
        if not redis_client:
            return None
        try:
            value = redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception:
            pass
        return None
    
    async def _set_to_l2(self, key: str, value: Any, ttl: int):
        """Set to L2 cache"""
        redis_client = self.cache_instances[CacheLevel.L2]
        if not redis_client:
            return
        try:
            serialized_value = pickle.dumps(value)
            redis_client.setex(key, ttl, serialized_value)
        except Exception:
            pass
    
    async def _delete_from_l2(self, key: str):
        """Delete from L2 cache"""
        redis_client = self.cache_instances[CacheLevel.L2]
        if redis_client:
            redis_client.delete(key)
    
    # L3 Cache operations (Memcached)
    async def _get_from_l3(self, key: str) -> Any:
        """Get from L3 cache"""
        memcached_client = self.cache_instances[CacheLevel.L3]
        if not memcached_client:
            return None
        try:
            return memcached_client.get(key)
        except Exception:
            return None
    
    async def _set_to_l3(self, key: str, value: Any, ttl: int):
        """Set to L3 cache"""
        memcached_client = self.cache_instances[CacheLevel.L3]
        if not memcached_client:
            return
        try:
            memcached_client.set(key, value, time=ttl)
        except Exception:
            pass
    
    async def _delete_from_l3(self, key: str):
        """Delete from L3 cache"""
        memcached_client = self.cache_instances[CacheLevel.L3]
        if memcached_client:
            memcached_client.delete(key)
    
    # L4 Cache operations (Disk)
    async def _get_from_l4(self, key: str) -> Any:
        """Get from L4 cache"""
        cache_dir = self.cache_instances[CacheLevel.L4]
        file_path = cache_dir / self._get_cache_file_path(key)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                    if data['expires'] > time.time():
                        return data['value']
                    else:
                        file_path.unlink()  # Remove expired file
            except Exception:
                pass
        return None
    
    async def _set_to_l4(self, key: str, value: Any, ttl: int):
        """Set to L4 cache"""
        cache_dir = self.cache_instances[CacheLevel.L4]
        file_path = cache_dir / self._get_cache_file_path(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                'value': value,
                'expires': time.time() + ttl
            }
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception:
            pass
    
    async def _delete_from_l4(self, key: str):
        """Delete from L4 cache"""
        cache_dir = self.cache_instances[CacheLevel.L4]
        file_path = cache_dir / self._get_cache_file_path(key)
        if file_path.exists():
            file_path.unlink()
    
    def _get_cache_file_path(self, key: str) -> str:
        """Generate cache file path for key"""
        # Create hash-based directory structure
        key_hash = hashlib.md5(key.encode()).hexdigest()
        subdir = '/'.join([key_hash[i:i+2] for i in range(0, self.l4_config.subdirectory_levels * 2, 2)])
        return f"{subdir}/{key_hash}.cache"
    
    def get_metrics(self) -> Dict[str, CacheMetrics]:
        """Get cache metrics for all levels"""
        return {level.value: metrics for level, metrics in self.metrics.items()}
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete cache configuration"""
        return {
            "strategy": self.strategy.value,
            "l1_config": self.l1_config.get_config(),
            "l2_config": self.l2_config.get_config(),
            "l3_config": self.l3_config.get_config(),
            "l4_config": self.l4_config.get_config(),
            "business_rules": self.business_config.get_business_cache_rules(),
            "metrics": {level.value: {
                "hit_rate": metrics.hit_rate,
                "miss_rate": metrics.miss_rate,
                "hit_count": metrics.hit_count,
                "miss_count": metrics.miss_count,
                "eviction_count": metrics.eviction_count
            } for level, metrics in self.metrics.items()}
        }

# Global cache configuration instance
cache_config = CacheConfiguration()

# Export main classes
__all__ = [
    "CacheConfiguration",
    "CacheType",
    "CacheLevel",
    "EvictionPolicy",
    "CacheStrategy",
    "CacheMetrics",
    "L1CacheConfig",
    "L2CacheConfig", 
    "L3CacheConfig",
    "L4CacheConfig",
    "BusinessCacheConfig",
    "cache_config"
]
