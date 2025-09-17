"""⚡ Cache Performance Profiler
=============================

Advanced profiling system for cache performance in the Creator Economy platform.
Provides real-time monitoring of Redis cache, memory cache, CDN cache performance and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
import hashlib
import re
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cache systems"""
    
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    CDN = "cdn"
    APPLICATION = "application"
    DATABASE = "database"
    BROWSER = "browser"
    DISTRIBUTED = "distributed"


class CacheOperation(Enum):
    """Cache operations"""
    
    GET = "get"
    SET = "set"
    DELETE = "delete"
    EXISTS = "exists"
    EXPIRE = "expire"
    FLUSH = "flush"
    MULTI_GET = "multi_get"
    MULTI_SET = "multi_set"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    APPEND = "append"
    PREPEND = "prepend"


class EvictionPolicy(Enum):
    """Cache eviction policies"""
    
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    RANDOM = "random"
    TTL = "ttl"  # Time To Live
    ALLKEYS_LRU = "allkeys_lru"
    VOLATILE_LRU = "volatile_lru"
    ALLKEYS_RANDOM = "allkeys_random"


@dataclass
class CacheKeyMetadata:
    """Cache key metadata"""
    
    key: str
    key_pattern: str
    namespace: str
    data_type: str
    data_size: int  # bytes
    ttl: Optional[int] = None  # seconds
    access_count: int = 0
    hit_count: int = 0
    miss_count: int = 0
    last_access: Optional[datetime] = None
    creation_time: datetime = field(default_factory=datetime.now)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    
    cache_type: CacheType
    cache_name: str
    operation: CacheOperation
    key_metadata: CacheKeyMetadata
    operation_time: float  # seconds
    data_size: int  # bytes
    hit: bool
    ttl_remaining: Optional[int] = None  # seconds
    memory_usage: int = 0  # MB
    network_latency: float = 0.0  # seconds
    serialization_time: float = 0.0  # seconds
    deserialization_time: float = 0.0  # seconds
    compression_ratio: Optional[float] = None
    cache_instance_id: Optional[str] = None
    connection_pool_size: int = 0
    active_connections: int = 0
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def throughput_mbps(self) -> float:
        """Calculate throughput in MB/s"""
        if self.operation_time > 0:
            return (self.data_size / (1024 * 1024)) / self.operation_time
        return 0.0


@dataclass
class CacheInstanceStats:
    """Cache instance statistics"""
    
    cache_type: CacheType
    instance_id: str
    total_memory: int  # MB
    used_memory: int  # MB
    total_keys: int
    expired_keys: int
    evicted_keys: int
    hit_rate: float  # percentage
    miss_rate: float  # percentage
    operations_per_second: float
    connected_clients: int
    blocked_clients: int
    eviction_policy: EvictionPolicy
    max_memory_policy: str
    uptime: int  # seconds
    cpu_usage: float = 0.0  # percentage
    network_io_rate: float = 0.0  # MB/s
    replication_lag: float = 0.0  # seconds
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def memory_utilization(self) -> float:
        """Calculate memory utilization percentage"""
        return (self.used_memory / self.total_memory) * 100 if self.total_memory > 0 else 0


@dataclass
class CacheBottleneck:
    """Cache performance bottleneck detection"""
    
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_cache_type: CacheType
    cache_instance: str
    performance_impact: float  # percentage
    optimization_suggestions: List[str]
    configuration_recommendations: List[str]
    infrastructure_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class CacheProfiler:
    """
    Advanced Cache Performance Profiler
    
    Provides comprehensive profiling for cache systems with focus on:
    - Real-time cache operation monitoring
    - Hit/miss ratio analysis
    - Memory usage optimization
    - Network latency tracking
    - Eviction policy effectiveness
    """
    
    def __init__(
        self,
        enable_key_tracking: bool = True,
        enable_pattern_analysis: bool = True,
        enable_instance_monitoring: bool = True,
        sampling_interval: float = 5.0,
        max_history_size: int = 100000,
        hit_rate_threshold: float = 80.0
    ):
        """
        Initialize Cache Profiler
        
        Args:
            enable_key_tracking: Enable individual key tracking
            enable_pattern_analysis: Enable key pattern analysis
            enable_instance_monitoring: Enable cache instance monitoring
            sampling_interval: Metrics collection interval in seconds
            max_history_size: Maximum number of metrics to keep
            hit_rate_threshold: Minimum hit rate threshold for alerts
        """
        self.enable_key_tracking = enable_key_tracking
        self.enable_pattern_analysis = enable_pattern_analysis
        self.enable_instance_monitoring = enable_instance_monitoring
        self.sampling_interval = sampling_interval
        self.max_history_size = max_history_size
        self.hit_rate_threshold = hit_rate_threshold
        
        # Metrics storage
        self.cache_metrics: deque = deque(maxlen=max_history_size)
        self.bottlenecks: deque = deque(maxlen=max_history_size)
        
        # Active profiling sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = threading.Lock()
        
        # Cache instance tracking
        self.cache_instances: Dict[str, CacheInstanceStats] = {}
        
        # Key pattern analysis
        self.key_patterns: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'hit_count': 0,
            'miss_count': 0,
            'total_size': 0,
            'avg_operation_time': 0,
            'last_access': None
        })
        
        # Hot keys tracking
        self.hot_keys: Dict[str, CacheKeyMetadata] = {}
        
        # Cache clients registry
        self.cache_clients: Dict[str, Any] = {}
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("CacheProfiler initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        
        self.cache_operation_time_histogram = Histogram(
            'cache_operation_time_seconds',
            'Cache operation execution time',
            ['cache_type', 'operation', 'cache_name']
        )
        
        self.cache_hit_rate_gauge = Gauge(
            'cache_hit_rate_percent',
            'Cache hit rate percentage',
            ['cache_type', 'cache_name']
        )
        
        self.cache_throughput_gauge = Gauge(
            'cache_throughput_mbps',
            'Cache throughput in MB/s',
            ['cache_type', 'operation']
        )
        
        self.cache_memory_usage_gauge = Gauge(
            'cache_memory_usage_mb',
            'Cache memory usage in MB',
            ['cache_type', 'instance_id']
        )
        
        self.cache_keys_gauge = Gauge(
            'cache_total_keys',
            'Total number of cache keys',
            ['cache_type', 'instance_id']
        )
        
        self.cache_connections_gauge = Gauge(
            'cache_connections',
            'Cache connection metrics',
            ['cache_type', 'instance_id', 'metric_type']
        )
        
        self.cache_evictions_counter = Counter(
            'cache_evictions_total',
            'Total cache key evictions',
            ['cache_type', 'instance_id', 'reason']
        )
        
        self.cache_bottleneck_counter = Counter(
            'cache_bottlenecks_total',
            'Total cache bottlenecks detected',
            ['bottleneck_type', 'severity']
        )
        
        self.cache_error_counter = Counter(
            'cache_errors_total',
            'Total cache errors',
            ['cache_type', 'operation']
        )
    
    def register_cache_client(self, cache_name: str, cache_type: CacheType, client: Any):
        """Register a cache client for monitoring"""
        self.cache_clients[cache_name] = {
            'type': cache_type,
            'client': client,
            'registered_at': datetime.now()
        }
        logger.info("Registered cache client: %s (%s)", cache_name, cache_type.value)
    
    def _extract_key_pattern(self, key: str) -> str:
        """Extract pattern from cache key"""
        # Replace numbers with placeholders
        pattern = key
        
        # Replace UUIDs
        pattern = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{uuid}', pattern)
        
        # Replace numbers
        pattern = re.sub(r'\d+', '{number}', pattern)
        
        # Replace timestamps
        pattern = re.sub(r'\d{10,13}', '{timestamp}', pattern)
        
        return pattern
    
    def _determine_namespace(self, key: str) -> str:
        """Determine namespace from cache key"""
        parts = key.split(':')
        return parts[0] if len(parts) > 1 else 'default'
    
    def _detect_data_type(self, data: Any) -> str:
        """Detect data type for cache value"""
        if isinstance(data, str):
            return 'string'
        elif isinstance(data, (int, float)):
            return 'number'
        elif isinstance(data, (list, tuple)):
            return 'list'
        elif isinstance(data, dict):
            return 'hash'
        elif isinstance(data, set):
            return 'set'
        elif isinstance(data, bytes):
            return 'binary'
        else:
            return 'object'
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Cache background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Cache background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Update cache instance statistics
                if self.enable_instance_monitoring:
                    self._update_instance_stats()
                
                # Analyze key patterns
                if self.enable_pattern_analysis:
                    self._analyze_key_patterns()
                
                # Detect bottlenecks
                self._detect_bottlenecks()
                
                # Update hot keys
                self._update_hot_keys()
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error("Error in cache monitoring loop: %s", e)
                time.sleep(1.0)
    
    def start_cache_profiling(
        self,
        cache_type: CacheType,
        cache_name: str,
        operation: CacheOperation,
        key: str,
        data_size: int = 0,
        ttl: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Start profiling a cache operation
        
        Args:
            cache_type: Type of cache system
            cache_name: Name of cache instance
            operation: Cache operation type
            key: Cache key
            data_size: Size of data in bytes
            ttl: Time to live in seconds
            session_id: Optional session identifier
        
        Returns:
            session_id: Unique identifier for this profiling session
        """
        if session_id is None:
            session_id = f"cache_{operation.value}_{int(time.time() * 1000)}"
        
        # Extract key metadata
        key_pattern = self._extract_key_pattern(key) if self.enable_pattern_analysis else key
        namespace = self._determine_namespace(key)
        
        # Get or create key metadata
        if self.enable_key_tracking:
            if key in self.hot_keys:
                key_metadata = self.hot_keys[key]
                key_metadata.access_count += 1
                key_metadata.last_access = datetime.now()
            else:
                key_metadata = CacheKeyMetadata(
                    key=key,
                    key_pattern=key_pattern,
                    namespace=namespace,
                    data_type='unknown',
                    data_size=data_size,
                    ttl=ttl,
                    access_count=1
                )
        else:
            key_metadata = CacheKeyMetadata(
                key=key,
                key_pattern=key_pattern,
                namespace=namespace,
                data_type='unknown',
                data_size=data_size,
                ttl=ttl
            )
        
        session_data = {
            'cache_type': cache_type,
            'cache_name': cache_name,
            'operation': operation,
            'key_metadata': key_metadata,
            'start_time': time.time(),
            'serialization_start': None,
            'network_start': None,
            'deserialization_start': None,
            'error_count': 0,
            'warnings': []
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
        
        logger.debug("Started cache profiling session: %s", session_id)
        return session_id
    
    def mark_serialization_start(self, session_id: str):
        """Mark the start of serialization phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['serialization_start'] = time.time()
    
    def mark_network_start(self, session_id: str):
        """Mark the start of network communication"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['network_start'] = time.time()
    
    def mark_deserialization_start(self, session_id: str):
        """Mark the start of deserialization phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['deserialization_start'] = time.time()
    
    def add_warning(self, session_id: str, warning: str):
        """Add a warning to the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['warnings'].append(warning)
    
    def increment_error_count(self, session_id: str):
        """Increment error count for the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['error_count'] += 1
    
    def end_cache_profiling(
        self,
        session_id: str,
        hit: bool,
        data: Optional[Any] = None,
        ttl_remaining: Optional[int] = None,
        compression_ratio: Optional[float] = None,
        cache_instance_id: Optional[str] = None
    ) -> CacheMetrics:
        """
        End cache profiling session and return metrics
        
        Args:
            session_id: Session identifier
            hit: Whether the operation was a cache hit
            data: Retrieved/stored data for analysis
            ttl_remaining: Remaining TTL in seconds
            compression_ratio: Compression ratio if applicable
            cache_instance_id: Cache instance identifier
        
        Returns:
            CacheMetrics: Complete cache operation metrics
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions.pop(session_id)
        
        end_time = time.time()
        total_time = end_time - session_data['start_time']
        
        # Calculate phase timings
        serialization_time = 0.0
        network_latency = 0.0
        deserialization_time = 0.0
        
        if session_data['serialization_start']:
            if session_data['network_start']:
                serialization_time = session_data['network_start'] - session_data['serialization_start']
            else:
                serialization_time = end_time - session_data['serialization_start']
        
        if session_data['network_start']:
            if session_data['deserialization_start']:
                network_latency = session_data['deserialization_start'] - session_data['network_start']
            else:
                network_latency = end_time - session_data['network_start']
        
        if session_data['deserialization_start']:
            deserialization_time = end_time - session_data['deserialization_start']
        
        # Update key metadata
        key_metadata = session_data['key_metadata']
        if data is not None:
            key_metadata.data_type = self._detect_data_type(data)
            if hasattr(data, '__sizeof__'):
                key_metadata.data_size = data.__sizeof__()
        
        if hit:
            key_metadata.hit_count += 1
        else:
            key_metadata.miss_count += 1
        
        # Update hot keys tracking
        if self.enable_key_tracking:
            self.hot_keys[key_metadata.key] = key_metadata
        
        # Create metrics object
        metrics = CacheMetrics(
            cache_type=session_data['cache_type'],
            cache_name=session_data['cache_name'],
            operation=session_data['operation'],
            key_metadata=key_metadata,
            operation_time=total_time,
            data_size=key_metadata.data_size,
            hit=hit,
            ttl_remaining=ttl_remaining,
            serialization_time=serialization_time,
            network_latency=network_latency,
            deserialization_time=deserialization_time,
            compression_ratio=compression_ratio,
            cache_instance_id=cache_instance_id,
            error_count=session_data['error_count'],
            warnings=session_data['warnings']
        )
        
        # Store metrics
        self.cache_metrics.append(metrics)
        
        # Update key pattern statistics
        if self.enable_pattern_analysis:
            pattern = key_metadata.key_pattern
            pattern_stats = self.key_patterns[pattern]
            
            if hit:
                pattern_stats['hit_count'] += 1
            else:
                pattern_stats['miss_count'] += 1
            
            pattern_stats['total_size'] += key_metadata.data_size
            pattern_stats['last_access'] = datetime.now()
            
            # Update average operation time
            current_avg = pattern_stats.get('avg_operation_time', 0)
            total_ops = pattern_stats['hit_count'] + pattern_stats['miss_count']
            pattern_stats['avg_operation_time'] = ((current_avg * (total_ops - 1)) + total_time) / total_ops
        
        # Update Prometheus metrics
        self.cache_operation_time_histogram.labels(
            cache_type=metrics.cache_type.value,
            operation=metrics.operation.value,
            cache_name=metrics.cache_name
        ).observe(metrics.operation_time)
        
        self.cache_throughput_gauge.labels(
            cache_type=metrics.cache_type.value,
            operation=metrics.operation.value
        ).set(metrics.throughput_mbps)
        
        if metrics.error_count > 0:
            self.cache_error_counter.labels(
                cache_type=metrics.cache_type.value,
                operation=metrics.operation.value
            ).inc(metrics.error_count)
        
        logger.info("Cache profiling completed for %s: %.3fs, hit=%s, size=%d bytes",
                   session_id, metrics.operation_time, hit, metrics.data_size)
        
        return metrics
    
    def _update_instance_stats(self):
        """Update cache instance statistics"""
        for cache_name, cache_info in self.cache_clients.items():
            try:
                cache_type = cache_info['type']
                client = cache_info['client']
                
                if cache_type == CacheType.REDIS:
                    stats = self._get_redis_stats(client, cache_name)
                elif cache_type == CacheType.MEMCACHED:
                    stats = self._get_memcached_stats(client, cache_name)
                else:
                    continue
                
                if stats:
                    self.cache_instances[cache_name] = stats
                    
                    # Update Prometheus metrics
                    self.cache_memory_usage_gauge.labels(
                        cache_type=cache_type.value,
                        instance_id=cache_name
                    ).set(stats.used_memory)
                    
                    self.cache_keys_gauge.labels(
                        cache_type=cache_type.value,
                        instance_id=cache_name
                    ).set(stats.total_keys)
                    
                    self.cache_hit_rate_gauge.labels(
                        cache_type=cache_type.value,
                        cache_name=cache_name
                    ).set(stats.hit_rate)
                    
                    self.cache_connections_gauge.labels(
                        cache_type=cache_type.value,
                        instance_id=cache_name,
                        metric_type='connected'
                    ).set(stats.connected_clients)
                    
            except Exception as e:
                logger.error("Error updating stats for cache %s: %s", cache_name, e)
    
    def _get_redis_stats(self, redis_client, instance_id: str) -> Optional[CacheInstanceStats]:
        """Get Redis instance statistics"""
        try:
            info = redis_client.info()
            
            return CacheInstanceStats(
                cache_type=CacheType.REDIS,
                instance_id=instance_id,
                total_memory=info.get('maxmemory', 0) // (1024 * 1024),
                used_memory=info.get('used_memory', 0) // (1024 * 1024),
                total_keys=sum(redis_client.dbsize() for db in range(16)),  # Simplified
                expired_keys=info.get('expired_keys', 0),
                evicted_keys=info.get('evicted_keys', 0),
                hit_rate=self._calculate_redis_hit_rate(info),
                miss_rate=100 - self._calculate_redis_hit_rate(info),
                operations_per_second=info.get('instantaneous_ops_per_sec', 0),
                connected_clients=info.get('connected_clients', 0),
                blocked_clients=info.get('blocked_clients', 0),
                eviction_policy=EvictionPolicy.ALLKEYS_LRU,  # Default
                max_memory_policy=info.get('maxmemory_policy', 'noeviction'),
                uptime=info.get('uptime_in_seconds', 0),
                cpu_usage=info.get('used_cpu_sys', 0),
                replication_lag=info.get('master_repl_offset', 0) - info.get('slave_repl_offset', 0)
            )
            
        except Exception as e:
            logger.error("Error getting Redis stats: %s", e)
            return None
    
    def _calculate_redis_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate Redis hit rate from info"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total) * 100 if total > 0 else 0
    
    def _get_memcached_stats(self, memcached_client, instance_id: str) -> Optional[CacheInstanceStats]:
        """Get Memcached instance statistics"""
        try:
            stats = memcached_client.stats()
            
            hits = int(stats.get('get_hits', 0))
            misses = int(stats.get('get_misses', 0))
            total_requests = hits + misses
            hit_rate = (hits / total_requests) * 100 if total_requests > 0 else 0
            
            return CacheInstanceStats(
                cache_type=CacheType.MEMCACHED,
                instance_id=instance_id,
                total_memory=int(stats.get('limit_maxbytes', 0)) // (1024 * 1024),
                used_memory=int(stats.get('bytes', 0)) // (1024 * 1024),
                total_keys=int(stats.get('curr_items', 0)),
                expired_keys=int(stats.get('expired_unfetched', 0)),
                evicted_keys=int(stats.get('evictions', 0)),
                hit_rate=hit_rate,
                miss_rate=100 - hit_rate,
                operations_per_second=int(stats.get('cmd_get', 0)) + int(stats.get('cmd_set', 0)),
                connected_clients=int(stats.get('curr_connections', 0)),
                blocked_clients=0,  # Memcached doesn't have blocked clients
                eviction_policy=EvictionPolicy.LRU,  # Default for Memcached
                max_memory_policy='lru',
                uptime=int(stats.get('uptime', 0)),
                cpu_usage=float(stats.get('rusage_system', 0))
            )
            
        except Exception as e:
            logger.error("Error getting Memcached stats: %s", e)
            return None
    
    def _analyze_key_patterns(self):
        """Analyze cache key access patterns"""
        # Clean up old pattern data
        current_time = datetime.now()
        patterns_to_remove = []
        
        for pattern, stats in self.key_patterns.items():
            last_access = stats.get('last_access')
            if last_access and (current_time - last_access).total_seconds() > 3600:  # 1 hour
                patterns_to_remove.append(pattern)
        
        for pattern in patterns_to_remove:
            del self.key_patterns[pattern]
    
    def _update_hot_keys(self):
        """Update hot keys tracking"""
        # Keep only most frequently accessed keys
        if len(self.hot_keys) > 10000:  # Limit hot keys
            sorted_keys = sorted(
                self.hot_keys.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )
            self.hot_keys = dict(sorted_keys[:5000])  # Keep top 5000
    
    def _detect_bottlenecks(self):
        """Detect cache performance bottlenecks"""
        if len(self.cache_metrics) < 10:
            return
        
        recent_metrics = list(self.cache_metrics)[-100:]  # Last 100 operations
        
        # Analyze hit rates
        cache_hit_rates = defaultdict(list)
        for metric in recent_metrics:
            cache_key = f"{metric.cache_type.value}:{metric.cache_name}"
            cache_hit_rates[cache_key].append(metric.hit)
        
        for cache_key, hits in cache_hit_rates.items():
            if len(hits) >= 20:  # Minimum sample size
                hit_rate = (sum(hits) / len(hits)) * 100
                
                if hit_rate < self.hit_rate_threshold:
                    cache_type_str, cache_name = cache_key.split(':', 1)
                    cache_type = CacheType(cache_type_str)
                    
                    bottleneck = CacheBottleneck(
                        bottleneck_type="low_hit_rate",
                        severity="high" if hit_rate < 50 else "medium",
                        description=f"Cache {cache_name} hit rate is {hit_rate:.1f}%",
                        affected_cache_type=cache_type,
                        cache_instance=cache_name,
                        performance_impact=self.hit_rate_threshold - hit_rate,
                        optimization_suggestions=[
                            "Review cache key patterns and TTL settings",
                            "Implement cache warming strategies",
                            "Analyze application cache usage patterns",
                            "Consider increasing cache size"
                        ],
                        configuration_recommendations=[
                            "Optimize TTL values for different key types",
                            "Configure appropriate eviction policies",
                            "Adjust memory allocation",
                            "Implement cache partitioning"
                        ],
                        infrastructure_recommendations=[
                            "Scale cache cluster horizontally",
                            "Upgrade to faster storage",
                            "Optimize network configuration",
                            "Consider cache replication"
                        ]
                    )
                    self._record_bottleneck(bottleneck)
        
        # Analyze operation times
        operation_times = defaultdict(list)
        for metric in recent_metrics:
            key = f"{metric.cache_type.value}:{metric.operation.value}"
            operation_times[key].append(metric.operation_time)
        
        for operation_key, times in operation_times.items():
            if len(times) >= 10:
                avg_time = statistics.mean(times)
                
                if avg_time > 0.1:  # 100ms threshold
                    cache_type_str, operation = operation_key.split(':', 1)
                    cache_type = CacheType(cache_type_str)
                    
                    bottleneck = CacheBottleneck(
                        bottleneck_type="slow_operations",
                        severity="high" if avg_time > 0.5 else "medium",
                        description=f"{cache_type_str} {operation} operations averaging {avg_time:.3f}s",
                        affected_cache_type=cache_type,
                        cache_instance="multiple",
                        performance_impact=min(100, (avg_time / 0.01) * 10),
                        optimization_suggestions=[
                            "Optimize serialization/deserialization",
                            "Reduce network latency",
                            "Implement connection pooling",
                            "Use asynchronous operations"
                        ],
                        configuration_recommendations=[
                            "Tune connection pool settings",
                            "Optimize serialization format",
                            "Configure compression",
                            "Adjust timeout values"
                        ],
                        infrastructure_recommendations=[
                            "Improve network bandwidth",
                            "Reduce network hops",
                            "Use dedicated cache networks",
                            "Consider local cache layers"
                        ]
                    )
                    self._record_bottleneck(bottleneck)
        
        # Analyze memory usage from instance stats
        for instance_id, stats in self.cache_instances.items():
            if stats.memory_utilization > 90:
                bottleneck = CacheBottleneck(
                    bottleneck_type="high_memory_usage",
                    severity="critical" if stats.memory_utilization > 95 else "high",
                    description=f"Cache {instance_id} memory usage is {stats.memory_utilization:.1f}%",
                    affected_cache_type=stats.cache_type,
                    cache_instance=instance_id,
                    performance_impact=stats.memory_utilization - 70,
                    optimization_suggestions=[
                        "Review key expiration policies",
                        "Implement cache data compression",
                        "Optimize data structures",
                        "Remove unused keys"
                    ],
                    configuration_recommendations=[
                        "Increase memory allocation",
                        "Configure aggressive eviction policies",
                        "Optimize TTL settings",
                        "Implement cache partitioning"
                    ],
                    infrastructure_recommendations=[
                        "Scale cache nodes horizontally",
                        "Upgrade to higher memory instances",
                        "Implement cache tiering",
                        "Consider cache federation"
                    ]
                )
                self._record_bottleneck(bottleneck)
    
    def _record_bottleneck(self, bottleneck: CacheBottleneck):
        """Record a detected bottleneck"""
        self.bottlenecks.append(bottleneck)
        
        # Update Prometheus counter
        self.cache_bottleneck_counter.labels(
            bottleneck_type=bottleneck.bottleneck_type,
            severity=bottleneck.severity
        ).inc()
        
        logger.warning("Cache bottleneck detected: %s (%s severity)",
                      bottleneck.description, bottleneck.severity)
    
    def get_hot_keys_analysis(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get analysis of hot cache keys
        
        Args:
            limit: Maximum number of hot keys to return
        
        Returns:
            List of hot key statistics
        """
        # Sort by access count
        sorted_keys = sorted(
            self.hot_keys.items(),
            key=lambda x: x[1].access_count,
            reverse=True
        )
        
        hot_keys_analysis = []
        for key, metadata in sorted_keys[:limit]:
            total_accesses = metadata.hit_count + metadata.miss_count
            hit_rate = (metadata.hit_count / total_accesses) * 100 if total_accesses > 0 else 0
            
            hot_keys_analysis.append({
                'key': key,
                'pattern': metadata.key_pattern,
                'namespace': metadata.namespace,
                'access_count': metadata.access_count,
                'hit_rate': hit_rate,
                'data_size': metadata.data_size,
                'data_type': metadata.data_type,
                'last_access': metadata.last_access.isoformat() if metadata.last_access else None
            })
        
        return hot_keys_analysis
    
    def get_pattern_analysis(self) -> Dict[str, Any]:
        """
        Get cache key pattern analysis
        
        Returns:
            Pattern analysis results
        """
        pattern_analysis = {}
        
        for pattern, stats in self.key_patterns.items():
            total_requests = stats['hit_count'] + stats['miss_count']
            hit_rate = (stats['hit_count'] / total_requests) * 100 if total_requests > 0 else 0
            
            pattern_analysis[pattern] = {
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'avg_operation_time': stats['avg_operation_time'],
                'total_size': stats['total_size'],
                'last_access': stats['last_access'].isoformat() if stats['last_access'] else None
            }
        
        # Sort by total requests
        sorted_patterns = sorted(
            pattern_analysis.items(),
            key=lambda x: x[1]['total_requests'],
            reverse=True
        )
        
        return dict(sorted_patterns)
    
    def get_optimization_recommendations(
        self,
        cache_type: Optional[CacheType] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get cache optimization recommendations
        
        Args:
            cache_type: Specific cache type to analyze
            time_window: Time window for analysis
        
        Returns:
            List of optimization recommendations
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.cache_metrics
            if (m.timestamp >= cutoff_time and
                (cache_type is None or m.cache_type == cache_type))
        ]
        
        if not recent_metrics:
            return []
        
        recommendations = []
        
        # Analyze hit rates
        total_operations = len(recent_metrics)
        hits = len([m for m in recent_metrics if m.hit])
        hit_rate = (hits / total_operations) * 100
        
        if hit_rate < self.hit_rate_threshold:
            recommendations.append({
                'type': 'hit_rate_optimization',
                'priority': 'high',
                'description': f'Cache hit rate is {hit_rate:.1f}%, below threshold of {self.hit_rate_threshold}%',
                'suggestions': [
                    'Analyze cache key patterns and access frequency',
                    'Implement cache warming for frequently accessed data',
                    'Review and optimize TTL settings',
                    'Consider increasing cache size or implementing tiered caching'
                ],
                'expected_improvement': f'{(self.hit_rate_threshold - hit_rate):.0f}% hit rate improvement'
            })
        
        # Analyze operation performance
        operation_times = [m.operation_time for m in recent_metrics]
        avg_operation_time = statistics.mean(operation_times)
        
        if avg_operation_time > 0.05:  # 50ms threshold
            recommendations.append({
                'type': 'performance_optimization',
                'priority': 'medium',
                'description': f'Average cache operation time is {avg_operation_time:.3f}s',
                'suggestions': [
                    'Optimize serialization/deserialization process',
                    'Implement connection pooling',
                    'Reduce network latency between application and cache',
                    'Use compression for large cache values'
                ],
                'expected_improvement': 'Up to 60% operation time reduction'
            })
        
        # Analyze memory efficiency from instance stats
        for instance_id, stats in self.cache_instances.items():
            if stats.memory_utilization > 80:
                recommendations.append({
                    'type': 'memory_optimization',
                    'priority': 'high' if stats.memory_utilization > 90 else 'medium',
                    'description': f'Cache {instance_id} memory utilization is {stats.memory_utilization:.1f}%',
                    'suggestions': [
                        'Review key expiration and eviction policies',
                        'Implement data compression',
                        'Optimize data structures for memory efficiency',
                        'Consider horizontal scaling'
                    ],
                    'expected_improvement': f'{(stats.memory_utilization - 70):.0f}% memory usage reduction'
                })
        
        # Analyze network efficiency
        network_times = [m.network_latency for m in recent_metrics if m.network_latency > 0]
        if network_times:
            avg_network_latency = statistics.mean(network_times)
            
            if avg_network_latency > 0.01:  # 10ms threshold
                recommendations.append({
                    'type': 'network_optimization',
                    'priority': 'medium',
                    'description': f'Average network latency is {avg_network_latency:.3f}s',
                    'suggestions': [
                        'Optimize network configuration',
                        'Consider cache locality and placement',
                        'Implement local cache layers',
                        'Use connection multiplexing'
                    ],
                    'expected_improvement': 'Up to 50% network latency reduction'
                })
        
        return recommendations
    
    def get_performance_summary(
        self,
        cache_type: Optional[CacheType] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get performance summary for cache operations
        
        Args:
            cache_type: Specific cache type to analyze
            time_window: Time window for analysis
        
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.cache_metrics
            if (m.timestamp >= cutoff_time and
                (cache_type is None or m.cache_type == cache_type))
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        # Calculate statistics
        operation_times = [m.operation_time for m in recent_metrics]
        data_sizes = [m.data_size for m in recent_metrics]
        hits = [m for m in recent_metrics if m.hit]
        
        summary = {
            'time_window': str(time_window),
            'total_operations': len(recent_metrics),
            'cache_types': len(set(m.cache_type for m in recent_metrics)),
            'performance_metrics': {
                'hit_rate': (len(hits) / len(recent_metrics)) * 100,
                'avg_operation_time': statistics.mean(operation_times),
                'p95_operation_time': statistics.quantiles(operation_times, n=20)[18] if len(operation_times) >= 20 else max(operation_times),
                'total_data_transferred': sum(data_sizes),
                'avg_data_size': statistics.mean(data_sizes) if data_sizes else 0,
                'total_errors': sum(m.error_count for m in recent_metrics)
            }
        }
        
        # Operation type distribution
        operation_dist = defaultdict(int)
        for metric in recent_metrics:
            operation_dist[metric.operation.value] += 1
        summary['operation_distribution'] = dict(operation_dist)
        
        # Cache instance summary
        summary['cache_instances'] = {}
        for instance_id, stats in self.cache_instances.items():
            summary['cache_instances'][instance_id] = {
                'memory_utilization': stats.memory_utilization,
                'hit_rate': stats.hit_rate,
                'total_keys': stats.total_keys,
                'operations_per_second': stats.operations_per_second,
                'connected_clients': stats.connected_clients
            }
        
        # Recent bottlenecks
        recent_bottlenecks = [b for b in self.bottlenecks if b.timestamp >= cutoff_time]
        summary['bottlenecks'] = {
            'total_count': len(recent_bottlenecks),
            'by_severity': {
                severity: len([b for b in recent_bottlenecks if b.severity == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }
        
        return summary


# Context manager for easy profiling
class CacheOperationProfiler:
    """Context manager for cache operation profiling"""
    
    def __init__(
        self,
        profiler: CacheProfiler,
        cache_type: CacheType,
        cache_name: str,
        operation: CacheOperation,
        key: str,
        data_size: int = 0,
        ttl: Optional[int] = None
    ):
        self.profiler = profiler
        self.cache_type = cache_type
        self.cache_name = cache_name
        self.operation = operation
        self.key = key
        self.data_size = data_size
        self.ttl = ttl
        self.session_id: Optional[str] = None
    
    def __enter__(self):
        self.session_id = self.profiler.start_cache_profiling(
            cache_type=self.cache_type,
            cache_name=self.cache_name,
            operation=self.operation,
            key=self.key,
            data_size=self.data_size,
            ttl=self.ttl
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None  # Session must be ended explicitly
    
    def mark_serialization_start(self):
        if self.session_id:
            self.profiler.mark_serialization_start(self.session_id)
    
    def mark_network_start(self):
        if self.session_id:
            self.profiler.mark_network_start(self.session_id)
    
    def mark_deserialization_start(self):
        if self.session_id:
            self.profiler.mark_deserialization_start(self.session_id)
    
    def end_profiling(self, hit: bool, **kwargs) -> CacheMetrics:
        if self.session_id:
            return self.profiler.end_cache_profiling(self.session_id, hit, **kwargs)
        raise ValueError("Session not started")


# Factory function for creating profiler instances
def create_cache_profiler(
    enable_key_tracking: bool = True,
    enable_pattern_analysis: bool = True,
    enable_instance_monitoring: bool = True,
    start_monitoring: bool = True
) -> CacheProfiler:
    """
    Factory function to create and configure Cache Profiler
    
    Args:
        enable_key_tracking: Enable individual key tracking
        enable_pattern_analysis: Enable key pattern analysis
        enable_instance_monitoring: Enable cache instance monitoring
        start_monitoring: Start background monitoring immediately
    
    Returns:
        Configured CacheProfiler instance
    """
    profiler = CacheProfiler(
        enable_key_tracking=enable_key_tracking,
        enable_pattern_analysis=enable_pattern_analysis,
        enable_instance_monitoring=enable_instance_monitoring
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


if __name__ == "__main__":
    # Example usage
    import re
    
    # Create profiler
    profiler = create_cache_profiler()
    
    # Example: Profile Redis GET operation
    with CacheOperationProfiler(
        profiler=profiler,
        cache_type=CacheType.REDIS,
        cache_name="main_redis",
        operation=CacheOperation.GET,
        key="user:12345:profile",
        data_size=1024
    ) as session:
        
        # Simulate cache operation
        session.mark_serialization_start()
        time.sleep(0.001)  # Simulate serialization
        
        session.mark_network_start()
        time.sleep(0.005)  # Simulate network
        
        session.mark_deserialization_start()
        time.sleep(0.001)  # Simulate deserialization
        
        # End profiling
        metrics = session.end_profiling(
            hit=True,
            data={'user_id': 12345, 'name': 'John Doe'},
            ttl_remaining=3600
        )
    
    # Get hot keys analysis
    hot_keys = profiler.get_hot_keys_analysis(limit=10)
    print("Hot Keys Analysis:", json.dumps(hot_keys, indent=2, default=str))
    
    # Get pattern analysis
    patterns = profiler.get_pattern_analysis()
    print("Pattern Analysis:", json.dumps(patterns, indent=2, default=str))
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2, default=str))
    
    # Get optimization recommendations
    recommendations = profiler.get_optimization_recommendations()
    print("Optimization Recommendations:", json.dumps(recommendations, indent=2))
    
    # Stop monitoring
    profiler.stop_monitoring()