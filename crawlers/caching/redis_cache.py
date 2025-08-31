#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Redis Cache Implementation - Industrial-Grade Redis Caching System
================================================================

Enterprise Redis cache with clustering, sharding, high availability,
and advanced performance optimization features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

BUSINESS LOGIC:
High-frequency cache requests → Redis cluster routing → Intelligent sharding →
Performance optimization → Ultra-fast response → Monitoring & analytics
"""
import asyncio
import logging
import json
import pickle
import gzip
import lz4.frame
import zstandard as zstd
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
import threading
from contextlib import asynccontextmanager
from collections import defaultdict, deque
import struct

try:
    import redis.asyncio as redis
    from redis.asyncio.cluster import RedisCluster
    from redis.asyncio.sentinel import Sentinel
    from redis.exceptions import RedisError, ConnectionError, TimeoutError
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None
    RedisCluster = None
    Sentinel = None
    RedisError = Exception
    ConnectionError = Exception
    TimeoutError = Exception

logger = logging.getLogger(__name__)

class RedisMode(Enum):
    """Redis deployment modes for enterprise scalability."""
    STANDALONE = "standalone"
    CLUSTER = "cluster"
    SENTINEL = "sentinel"
    SHARDED = "sharded"

class RedisCompressionMode(Enum):
    """Compression algorithms for Redis data optimization."""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"

class RedisConsistency(Enum):
    """Consistency levels for distributed Redis operations."""
    EVENTUAL = "eventual"
    STRONG = "strong"
    CAUSAL = "causal"

@dataclass
class RedisConfig:
    """Industrial Redis configuration with enterprise features."""
    # Basic connection settings
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    ssl: bool = False
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    
    # Connection pool settings
    max_connections: int = 100
    retry_on_timeout: bool = True
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=dict)
    
    # Cluster settings
    mode: RedisMode = RedisMode.STANDALONE
    cluster_nodes: List[str] = field(default_factory=list)
    cluster_skip_full_coverage_check: bool = False
    cluster_max_connections_per_node: int = 50
    
    # Sentinel settings
    sentinel_hosts: List[Tuple[str, int]] = field(default_factory=list)
    sentinel_service_name: str = "mymaster"
    sentinel_socket_timeout: float = 0.1
    
    # Performance optimization
    key_prefix: str = "ia_influencer_cache:"
    compression_mode: RedisCompressionMode = RedisCompressionMode.ZSTD
    compression_threshold: int = 1024  # Compress data > 1KB
    default_ttl: int = 3600
    max_value_size: int = 100 * 1024 * 1024  # 100MB
    
    # Advanced features
    pipeline_enabled: bool = True
    pipeline_batch_size: int = 100
    lua_script_caching: bool = True
    read_from_replicas: bool = True
    write_to_master_only: bool = True
    
    # Monitoring and metrics
    metrics_enabled: bool = True
    health_check_interval: int = 30
    slow_query_threshold_ms: int = 100
    
    # Consistency and reliability
    consistency_level: RedisConsistency = RedisConsistency.EVENTUAL
    replication_factor: int = 2
    automatic_failover: bool = True
    
    # Memory management
    memory_usage_threshold: float = 0.8
    eviction_policy: str = "allkeys-lru"
    max_memory_samples: int = 5

@dataclass
class RedisMetrics:
    """Comprehensive Redis performance metrics."""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    
    # Timing metrics
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    # Connection metrics
    active_connections: int = 0
    total_connections_created: int = 0
    connection_failures: int = 0
    
    # Memory metrics
    memory_usage_bytes: int = 0
    memory_fragmentation_ratio: float = 1.0
    evicted_keys: int = 0
    expired_keys: int = 0
    
    # Performance metrics
    keyspace_hits: int = 0
    keyspace_misses: int = 0
    operations_per_second: float = 0.0
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total = self.keyspace_hits + self.keyspace_misses
        return self.keyspace_hits / total if total > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        return (self.total_response_time / self.successful_commands 
                if self.successful_commands > 0 else 0.0)
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        return (self.failed_commands / self.total_commands * 100 
                if self.total_commands > 0 else 0.0)

class IndustrialRedisCache:
    """
    🎯 Industrial-Grade Redis Cache Implementation
    
    Enterprise Redis caching system featuring:
    - Multi-mode support (Standalone, Cluster, Sentinel, Sharded)
    - Advanced compression and optimization
    - High availability and automatic failover
    - Comprehensive monitoring and metrics
    - Intelligent connection pooling
    - Pipeline operations for performance
    - Lua script caching and optimization
    - Memory management and eviction policies
    - Consistent hashing for sharding
    - Read/write splitting for replicas
    """
    
    def __init__(self, config: Optional[RedisConfig] = None, **kwargs):
        """Initialize industrial Redis cache with advanced configuration."""
        if not HAS_REDIS:
            raise ImportError("redis package required for RedisCache")
        
        self.config = config or RedisConfig(**kwargs)
        self.logger = logging.getLogger(f"{__name__}.IndustrialRedisCache")
        
        # Redis connections
        self.redis_client: Optional[Union[redis.Redis, RedisCluster]] = None
        self.read_replicas: List[redis.Redis] = []
        self.connection_pools: Dict[str, redis.ConnectionPool] = {}
        
        # Performance optimization
        self.pipeline_queue = deque()
        self.lua_scripts: Dict[str, str] = {}
        self.compiled_scripts: Dict[str, Any] = {}
        
        # Metrics and monitoring
        self.metrics = RedisMetrics()
        self.response_times = deque(maxlen=1000)
        self.operation_stats = defaultdict(int)
        self.error_log = deque(maxlen=100)
        
        # Thread safety
        self._lock = threading.RLock()
        self._pipeline_lock = asyncio.Lock()
        
        # Compression engines
        self._compression_engines = {
            RedisCompressionMode.GZIP: self._gzip_compress,
            RedisCompressionMode.LZ4: self._lz4_compress,
            RedisCompressionMode.ZSTD: self._zstd_compress
        }
        
        self._decompression_engines = {
            RedisCompressionMode.GZIP: self._gzip_decompress,
            RedisCompressionMode.LZ4: self._lz4_decompress,
            RedisCompressionMode.ZSTD: self._zstd_decompress
        }
        
        # Health monitoring
        self._last_health_check = datetime.now()
        self._health_status = True
        
        self.logger.info("🚀 Industrial Redis Cache initialized")

    async def initialize(self) -> bool:
        """Initialize Redis connections and components."""
        try:
            self.logger.info("🔧 Initializing Redis connections...")
            
            # Initialize based on deployment mode
            if self.config.mode == RedisMode.CLUSTER:
                await self._initialize_cluster()
            elif self.config.mode == RedisMode.SENTINEL:
                await self._initialize_sentinel()
            elif self.config.mode == RedisMode.SHARDED:
                await self._initialize_sharded()
            else:
                await self._initialize_standalone()
            
            # Initialize read replicas if configured
            if self.config.read_from_replicas:
                await self._initialize_read_replicas()
            
            # Pre-compile Lua scripts
            if self.config.lua_script_caching:
                await self._initialize_lua_scripts()
            
            # Start background monitoring
            if self.config.metrics_enabled:
                asyncio.create_task(self._monitoring_loop())
            
            # Verify connection
            await self._verify_connection()
            
            self.logger.info("✅ Redis Cache successfully initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Redis Cache initialization failed: {e}")
            return False

    async def _initialize_standalone(self) -> None:
        """Initialize standalone Redis connection."""
        pool = redis.ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
            username=self.config.username,
            ssl=self.config.ssl,
            ssl_cert_reqs=self.config.ssl_cert_reqs,
            ssl_ca_certs=self.config.ssl_ca_certs,
            ssl_certfile=self.config.ssl_certfile,
            ssl_keyfile=self.config.ssl_keyfile,
            max_connections=self.config.max_connections,
            retry_on_timeout=self.config.retry_on_timeout,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            socket_keepalive=self.config.socket_keepalive,
            socket_keepalive_options=self.config.socket_keepalive_options
        )
        
        self.redis_client = redis.Redis(connection_pool=pool)
        self.connection_pools['master'] = pool

    async def _initialize_cluster(self) -> None:
        """Initialize Redis Cluster connections."""
        startup_nodes = []
        for node in self.config.cluster_nodes:
            if ':' in node:
                host, port = node.split(':')
                startup_nodes.append({"host": host, "port": int(port)})
            else:
                startup_nodes.append({"host": node, "port": 6379})
        
        self.redis_client = RedisCluster(
            startup_nodes=startup_nodes,
            password=self.config.password,
            skip_full_coverage_check=self.config.cluster_skip_full_coverage_check,
            max_connections_per_node=self.config.cluster_max_connections_per_node,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            retry_on_timeout=self.config.retry_on_timeout
        )

    async def _initialize_sentinel(self) -> None:
        """Initialize Redis Sentinel connections."""
        sentinel = Sentinel(
            self.config.sentinel_hosts,
            socket_timeout=self.config.sentinel_socket_timeout
        )
        
        # Get master connection
        master = sentinel.master_for(
            self.config.sentinel_service_name,
            socket_timeout=self.config.socket_timeout,
            password=self.config.password,
            db=self.config.db
        )
        
        self.redis_client = master

    async def _initialize_sharded(self) -> None:
        """Initialize sharded Redis setup with consistent hashing."""
        # This would implement consistent hashing across multiple Redis instances
        # For now, fall back to standalone
        await self._initialize_standalone()
        self.logger.warning("Sharded mode not fully implemented, using standalone")

    async def _initialize_read_replicas(self) -> None:
        """Initialize read replica connections for read scaling."""
        # Implementation would connect to read replicas
        # For now, use master for reads as well
        pass

    async def _initialize_lua_scripts(self) -> None:
        """Pre-compile commonly used Lua scripts for performance."""
        # Multi-get script for pipeline optimization
        self.lua_scripts['multi_get'] = """
            local keys = KEYS
            local result = {}
            for i, key in ipairs(keys) do
                result[i] = redis.call('GET', key)
            end
            return result
        """
        
        # Atomic increment with expiry
        self.lua_scripts['incr_expire'] = """
            local key = KEYS[1]
            local ttl = ARGV[1]
            local value = redis.call('INCR', key)
            if value == 1 then
                redis.call('EXPIRE', key, ttl)
            end
            return value
        """
        
        # Safe deletion with pattern
        self.lua_scripts['safe_delete_pattern'] = """
            local pattern = KEYS[1]
            local keys = redis.call('KEYS', pattern)
            local deleted = 0
            for i, key in ipairs(keys) do
                deleted = deleted + redis.call('DEL', key)
            end
            return deleted
        """
        
        # Compile scripts
        for name, script in self.lua_scripts.items():
            try:
                self.compiled_scripts[name] = self.redis_client.register_script(script)
                self.logger.debug(f"✅ Compiled Lua script: {name}")
            except Exception as e:
                self.logger.warning(f"❌ Failed to compile Lua script {name}: {e}")

    async def _verify_connection(self) -> None:
        """Verify Redis connection is working."""
        try:
            await self.redis_client.ping()
            self.logger.info("✅ Redis connection verified")
        except Exception as e:
            raise ConnectionError(f"Redis connection verification failed: {e}")

    async def get(self, key: str, use_compression: bool = True) -> Optional[Any]:
        """
        Get value from Redis with automatic decompression and optimization.
        
        Args:
            key: Cache key
            use_compression: Whether to attempt decompression
            
        Returns:
            Cached value or None
        """
        start_time = time.time()
        cache_key = f"{self.config.key_prefix}{key}"
        
        try:
            # Use read replica if available and configured
            client = self._get_read_client()
            
            # Get raw value
            raw_value = await client.get(cache_key)
            
            if raw_value is None:
                await self._record_miss(key)
                return None
            
            # Record hit and timing
            response_time = (time.time() - start_time) * 1000
            await self._record_hit(key, response_time)
            
            # Decompress and deserialize
            return self._deserialize_value(raw_value, use_compression)
            
        except Exception as e:
            await self._record_error('get', key, e)
            self.logger.error(f"❌ Redis GET failed for key '{key}': {e}")
            return None

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        use_compression: bool = True,
        compression_threshold: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis with intelligent compression and optimization.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            use_compression: Whether to compress large values
            compression_threshold: Size threshold for compression
            
        Returns:
            Success status
        """
        start_time = time.time()
        cache_key = f"{self.config.key_prefix}{key}"
        
        try:
            # Serialize and optionally compress
            serialized_value = self._serialize_value(
                value, use_compression, compression_threshold
            )
            
            # Check size limits
            if len(serialized_value) > self.config.max_value_size:
                self.logger.warning(
                    f"Value too large for key '{key}': {len(serialized_value)} bytes"
                )
                return False
            
            # Set value with TTL
            ttl = ttl or self.config.default_ttl
            success = await self.redis_client.setex(cache_key, ttl, serialized_value)
            
            # Record metrics
            response_time = (time.time() - start_time) * 1000
            await self._record_set(key, len(serialized_value), response_time)
            
            return bool(success)
            
        except Exception as e:
            await self._record_error('set', key, e)
            self.logger.error(f"❌ Redis SET failed for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        cache_key = f"{self.config.key_prefix}{key}"
        
        try:
            result = await self.redis_client.delete(cache_key)
            await self._record_delete(key)
            return bool(result)
            
        except Exception as e:
            await self._record_error('delete', key, e)
            self.logger.error(f"❌ Redis DELETE failed for key '{key}': {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern using optimized Lua script."""
        try:
            if 'safe_delete_pattern' in self.compiled_scripts:
                # Use compiled Lua script for atomic operation
                deleted = await self.compiled_scripts['safe_delete_pattern'](
                    keys=[f"{self.config.key_prefix}{pattern}"]
                )
            else:
                # Fallback to regular pattern deletion
                keys = await self.redis_client.keys(f"{self.config.key_prefix}{pattern}")
                if keys:
                    deleted = await self.redis_client.delete(*keys)
                else:
                    deleted = 0
            
            self.logger.info(f"🗑️ Invalidated {deleted} keys matching pattern '{pattern}'")
            return int(deleted)
            
        except Exception as e:
            await self._record_error('invalidate_pattern', pattern, e)
            self.logger.error(f"❌ Pattern invalidation failed for '{pattern}': {e}")
            return 0

    # Compression methods
    
    def _serialize_value(
        self, 
        value: Any, 
        use_compression: bool = True,
        compression_threshold: Optional[int] = None
    ) -> bytes:
        """Serialize value with intelligent compression."""
        # Serialize
        serialized = pickle.dumps(value)
        
        # Apply compression if beneficial
        if (use_compression and 
            len(serialized) > (compression_threshold or self.config.compression_threshold)):
            
            compressed = self._compress_data(serialized)
            
            # Use compression only if it provides significant savings
            if len(compressed) < len(serialized) * 0.9:
                # Add compression header
                return b'COMPRESSED:' + compressed
            
        return serialized
    
    def _deserialize_value(self, raw_value: bytes, use_decompression: bool = True) -> Any:
        """Deserialize value with automatic decompression detection."""
        try:
            # Check for compression header
            if use_decompression and raw_value.startswith(b'COMPRESSED:'):
                compressed_data = raw_value[11:]  # Remove header
                decompressed = self._decompress_data(compressed_data)
                return pickle.loads(decompressed)
            else:
                return pickle.loads(raw_value)
                
        except Exception as e:
            self.logger.error(f"❌ Value deserialization failed: {e}")
            return None
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using configured algorithm."""
        compress_func = self._compression_engines.get(self.config.compression_mode)
        if compress_func:
            return compress_func(data)
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data using configured algorithm."""
        decompress_func = self._decompression_engines.get(self.config.compression_mode)
        if decompress_func:
            return decompress_func(data)
        return data
    
    def _gzip_compress(self, data: bytes) -> bytes:
        """GZIP compression."""
        return gzip.compress(data)
    
    def _gzip_decompress(self, data: bytes) -> bytes:
        """GZIP decompression."""
        return gzip.decompress(data)
    
    def _lz4_compress(self, data: bytes) -> bytes:
        """LZ4 compression for high-speed scenarios."""
        return lz4.frame.compress(data)
    
    def _lz4_decompress(self, data: bytes) -> bytes:
        """LZ4 decompression."""
        return lz4.frame.decompress(data)
    
    def _zstd_compress(self, data: bytes) -> bytes:
        """Zstandard compression for optimal ratio."""
        cctx = zstd.ZstdCompressor()
        return cctx.compress(data)
    
    def _zstd_decompress(self, data: bytes) -> bytes:
        """Zstandard decompression."""
        dctx = zstd.ZstdDecompressor()
        return dctx.decompress(data)

    # Helper methods
    
    def _get_read_client(self) -> Union[redis.Redis, RedisCluster]:
        """Get appropriate client for read operations."""
        if self.config.read_from_replicas and self.read_replicas:
            # Simple round-robin for now
            import random
            return random.choice(self.read_replicas)
        return self.redis_client
    
    async def _record_hit(self, key: str, response_time: float) -> None:
        """Record cache hit metrics."""
        with self._lock:
            self.metrics.keyspace_hits += 1
            self.metrics.successful_commands += 1
            self.metrics.total_response_time += response_time
            self.response_times.append(response_time)
            
            if response_time < self.metrics.min_response_time:
                self.metrics.min_response_time = response_time
            if response_time > self.metrics.max_response_time:
                self.metrics.max_response_time = response_time
    
    async def _record_miss(self, key: str) -> None:
        """Record cache miss metrics."""
        with self._lock:
            self.metrics.keyspace_misses += 1
    
    async def _record_set(self, key: str, size: int, response_time: float) -> None:
        """Record set operation metrics."""
        with self._lock:
            self.metrics.successful_commands += 1
            self.operation_stats['set'] += 1
            self.metrics.total_response_time += response_time
            self.response_times.append(response_time)
    
    async def _record_delete(self, key: str) -> None:
        """Record delete operation metrics."""
        with self._lock:
            self.operation_stats['delete'] += 1
    
    async def _record_error(self, operation: str, key: str, error: Exception) -> None:
        """Record error metrics."""
        with self._lock:
            self.metrics.failed_commands += 1
            self.metrics.total_commands += 1
            self.error_log.append({
                'timestamp': datetime.now(),
                'operation': operation,
                'key': key,
                'error': str(error)
            })

    async def get_metrics(self) -> RedisMetrics:
        """Get comprehensive Redis metrics."""
        return self.metrics

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            start_time = time.time()
            await self.redis_client.ping()
            ping_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = await self.redis_client.info()
            
            return {
                'healthy': True,
                'ping_time_ms': ping_time,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'hit_ratio': self.metrics.hit_ratio,
                'error_rate': self.metrics.error_rate
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'ping_time_ms': None
            }

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop for health and metrics."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                # Update health status
                health = await self.health_check()
                self._health_status = health['healthy']
                
                # Log performance metrics periodically
                if self.metrics.successful_commands > 0:
                    self.logger.info(
                        f"📊 Redis Metrics - "
                        f"Hit Ratio: {self.metrics.hit_ratio:.2%}, "
                        f"Avg Response: {self.metrics.avg_response_time:.2f}ms, "
                        f"Error Rate: {self.metrics.error_rate:.2f}%"
                    )
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")

# Create aliases for backward compatibility
RedisCache = IndustrialRedisCache

class RedisClusterCache(IndustrialRedisCache):
    """Redis Cluster implementation with automatic sharding."""
    
    def __init__(self, nodes: List[str], **kwargs):
        config = RedisConfig(
            mode=RedisMode.CLUSTER,
            cluster_nodes=nodes,
            **kwargs
        )
        super().__init__(config)
                'db': self.config.db,
                'password': self.config.password,
                'ssl': self.config.ssl,
                'socket_timeout': self.config.socket_timeout,
                'socket_connect_timeout': self.config.socket_connect_timeout,
                'max_connections': self.config.max_connections,
                'decode_responses': False,  # We handle our own serialization
                'retry_on_timeout': True,
                'health_check_interval': 30
            }
            
            if self.config.connection_pool_kwargs:
                pool_kwargs.update(self.config.connection_pool_kwargs)
            
            # Create connection pool
            self.connection_pool = redis.ConnectionPool(**pool_kwargs)
            
            # Create Redis client
            self.redis = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            await self.redis.ping()
            
            self.logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self._error_count += 1
            self._last_error = str(e)
            raise
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Redis storage."""
        try:
            # Try JSON first for simple types
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                return json.dumps(value, default=str).encode('utf-8')
            else:
                # Use pickle for complex objects
                return pickle.dumps(value)
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from Redis storage."""
        try:
            # Try JSON first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback to pickle
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            raise
    
    async def get(self, key: str) -> Any:
        """
        Get value from Redis cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if self.redis is None:
            await self.connect()
        
        try:
            self._operations_count += 1
            redis_key = self._make_key(key)
            
            data = await self.redis.get(redis_key)
            if data is None:
                return None
            
            value = self._deserialize_value(data)
            self.logger.debug(f"Cache hit for key: {key}")
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting key {key}: {e}")
            self._error_count += 1
            self._last_error = str(e)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in Redis cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if self.redis is None:
            await self.connect()
        
        try:
            self._operations_count += 1
            redis_key = self._make_key(key)
            
            # Serialize value
            data = self._serialize_value(value)
            
            # Check size limit
            if len(data) > self.max_value_size:
                self.logger.warning(f"Value too large for key {key}: {len(data)} bytes")
                return False
            
            # Set with TTL
            ttl = ttl or self.default_ttl
            result = await self.redis.setex(redis_key, ttl, data)
            
            self.logger.debug(f"Set key {key} with TTL {ttl}s")
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Error setting key {key}: {e}")
            self._error_count += 1
            self._last_error = str(e)
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted
        """
        if self.redis is None:
            await self.connect()
        
        try:
            self._operations_count += 1
            redis_key = self._make_key(key)
            
            result = await self.redis.delete(redis_key)
            
            self.logger.debug(f"Deleted key: {key}")
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Error deleting key {key}: {e}")
            self._error_count += 1
            self._last_error = str(e)
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self.redis is None:
            await self.connect()
        
        try:
            redis_key = self._make_key(key)
            result = await self.redis.exists(redis_key)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error checking existence of key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        if self.redis is None:
            await self.connect()
        
        try:
            redis_key = self._make_key(key)
            result = await self.redis.expire(redis_key, ttl)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error setting TTL for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for key (-1 if no expiry, -2 if not exists)."""
        if self.redis is None:
            await self.connect()
        
        try:
            redis_key = self._make_key(key)
            result = await self.redis.ttl(redis_key)
            return result
        except Exception as e:
            self.logger.error(f"Error getting TTL for key {key}: {e}")
            return -2
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            
        Returns:
            Number of keys deleted
        """
        if self.redis is None:
            await self.connect()
        
        try:
            redis_pattern = self._make_key(pattern)
            
            # Find matching keys
            keys = []
            async for key in self.redis.scan_iter(match=redis_pattern):
                keys.append(key)
            
            if not keys:
                return 0
            
            # Delete in batches
            deleted = 0
            batch_size = 100
            
            for i in range(0, len(keys), batch_size):
                batch = keys[i:i + batch_size]
                result = await self.redis.delete(*batch)
                deleted += result
            
            self.logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Clear all keys with our prefix."""
        if self.redis is None:
            await self.connect()
        
        try:
            pattern = f"{self.key_prefix}*"
            deleted = await self.invalidate_pattern("*")
            
            self.logger.info(f"Cleared cache: {deleted} keys deleted")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False
    
    async def count_keys(self) -> int:
        """Count keys with our prefix."""
        if self.redis is None:
            await self.connect()
        
        try:
            pattern = f"{self.key_prefix}*"
            count = 0
            
            async for _ in self.redis.scan_iter(match=pattern):
                count += 1
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error counting keys: {e}")
            return 0
    
    async def get_memory_usage(self) -> int:
        """Get memory usage of Redis instance."""
        if self.redis is None:
            await self.connect()
        
        try:
            info = await self.redis.info("memory")
            return info.get("used_memory", 0)
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "operations_count": self._operations_count,
            "error_count": self._error_count,
            "last_error": self._last_error,
            "key_count": await self.count_keys(),
            "memory_usage": await self.get_memory_usage()
        }
        
        if self.redis:
            try:
                info = await self.redis.info()
                stats.update({
                    "redis_version": info.get("redis_version"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                })
            except Exception as e:
                self.logger.error(f"Error getting Redis info: {e}")
        
        return stats
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        if self.redis is None:
            return False
        
        try:
            response = await self.redis.ping()
            return response is True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            try:
                await self.redis.aclose()
                self.logger.info("Redis connection closed")
            except Exception as e:
                self.logger.error(f"Error closing Redis connection: {e}")
            finally:
                self.redis = None
                self.connection_pool = None

class RedisClusterCache(RedisCache):
    """
    Redis Cluster cache implementation.
    
    Extends RedisCache with cluster-specific features.
    """
    
    def __init__(self, nodes: List[Dict[str, Any]], **kwargs):
        """Initialize Redis Cluster cache."""
        super().__init__(**kwargs)
        self.nodes = nodes
        self.logger = logging.getLogger(f"{__name__}.RedisClusterCache")
    
    async def connect(self) -> None:
        """Establish Redis Cluster connection."""
        if self.redis is not None:
            return
        
        try:
            # Create cluster client
            startup_nodes = [
                {"host": node["host"], "port": node["port"]}
                for node in self.nodes
            ]
            
            self.redis = RedisCluster(
                startup_nodes=startup_nodes,
                password=self.config.password,
                ssl=self.config.ssl,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=False,
                skip_full_coverage_check=True,
                max_connections_per_node=20
            )
            
            # Test connection
            await self.redis.ping()
            
            self.logger.info(f"Connected to Redis Cluster with {len(self.nodes)} nodes")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis Cluster: {e}")
            raise
