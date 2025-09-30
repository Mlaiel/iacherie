"""
⚠️ CONFIDENTIEL - IA Chérie Creator Platform ⚠️

Cache Performance Optimizer - Enterprise Performance Monitoring
Advanced cache performance optimization for Creator Economy platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import redis
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import memcache
import json
import hashlib
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import threading
from prometheus_client import Gauge, Counter, Histogram
import requests
import aiohttp
from urllib.parse import urljoin
import pickle
import zlib

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Cache operation metrics"""
    cache_name: str
    cache_type: str  # redis, memcached, in_memory, cdn
    operation: str  # get, set, delete, exists
    key: str
    key_pattern: str  # normalized pattern
    hit: bool
    execution_time_ms: float
    data_size_bytes: int
    ttl_seconds: Optional[int]
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class CacheHitRatioMetrics:
    """Cache hit ratio metrics"""
    cache_name: str
    cache_type: str
    time_window_minutes: int
    total_operations: int
    cache_hits: int
    cache_misses: int
    hit_ratio_percent: float
    avg_hit_time_ms: float
    avg_miss_time_ms: float
    timestamp: datetime

@dataclass
class CacheInvalidationMetrics:
    """Cache invalidation pattern metrics"""
    cache_name: str
    invalidation_pattern: str
    keys_invalidated: int
    invalidation_reason: str  # ttl_expire, manual_delete, memory_pressure
    invalidation_time_ms: float
    data_recovered_bytes: int
    timestamp: datetime

@dataclass
class CacheWarmingMetrics:
    """Cache warming performance metrics"""
    cache_name: str
    warming_strategy: str  # preload, lazy_load, predictive
    keys_warmed: int
    warming_time_ms: float
    success_rate_percent: float
    data_preloaded_mb: float
    cache_efficiency_gain_percent: float
    timestamp: datetime

@dataclass
class CDNCacheMetrics:
    """CDN cache performance metrics"""
    cdn_provider: str
    edge_location: str
    origin_host: str
    cache_hit_ratio: float
    origin_offload_percent: float
    bandwidth_saved_mb: float
    avg_response_time_ms: float
    cache_purge_requests: int
    timestamp: datetime

@dataclass
class CacheOptimizationRecommendation:
    """Cache optimization recommendation"""
    cache_name: str
    recommendation_type: str
    priority: str  # high, medium, low
    description: str
    estimated_improvement_percent: float
    implementation_effort: str  # low, medium, high
    potential_savings: str
    timestamp: datetime

class CachePerformanceOptimizer:
    """
    Enterprise-grade cache performance optimizer
    Monitors Redis, Memcached, CDN caches and provides optimization recommendations
    """
    
    def __init__(self,
                 redis_clusters: List[Dict] = None,
                 memcached_servers: List[str] = None,
                 cdn_endpoints: List[Dict] = None,
                 enable_cache_warming: bool = True,
                 enable_intelligent_prefetch: bool = True,
                 monitoring_interval: int = 60):
        """
        Initialize cache performance optimizer
        
        Args:
            redis_clusters: List of Redis cluster configurations
            memcached_servers: List of Memcached server addresses
            cdn_endpoints: List of CDN endpoint configurations
            enable_cache_warming: Enable intelligent cache warming
            enable_intelligent_prefetch: Enable intelligent prefetching
            monitoring_interval: Monitoring interval in seconds
        """
        self.redis_clusters = redis_clusters or []
        self.memcached_servers = memcached_servers or []
        self.cdn_endpoints = cdn_endpoints or []
        self.enable_cache_warming = enable_cache_warming
        self.enable_intelligent_prefetch = enable_intelligent_prefetch
        self.monitoring_interval = monitoring_interval
        
        # Cache clients
        self.redis_clients: Dict[str, redis.Redis] = {}
        self.redis_async_clients: Dict[str, aioredis.Redis] = {}
        self.memcached_clients: Dict[str, memcache.Client] = {}
        
        # Metrics storage
        self.cache_metrics: deque = deque(maxlen=50000)
        self.hit_ratio_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.invalidation_metrics: deque = deque(maxlen=10000)
        self.warming_metrics: deque = deque(maxlen=5000)
        self.cdn_metrics: deque = deque(maxlen=5000)
        
        # Cache operation tracking
        self.cache_operations: Dict[str, Dict] = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'total_operations': 0,
            'total_time_ms': 0.0,
            'last_reset': datetime.utcnow()
        })
        
        # Key pattern analysis
        self.key_patterns: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'avg_size': 0,
            'hit_ratio': 0.0,
            'avg_ttl': 0
        })
        
        # Cache warming state
        self.warming_queue: Dict[str, List] = defaultdict(list)
        self.warming_strategies: Dict[str, str] = {}
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_tasks = []
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.cache_hit_ratio_gauge = Gauge(
            'cache_hit_ratio_percent',
            'Cache hit ratio percentage',
            ['cache_name', 'cache_type']
        )
        
        self.cache_operation_duration_histogram = Histogram(
            'cache_operation_duration_seconds',
            'Cache operation duration',
            ['cache_name', 'operation', 'hit_miss'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        self.cache_memory_usage_gauge = Gauge(
            'cache_memory_usage_bytes',
            'Cache memory usage in bytes',
            ['cache_name', 'cache_type']
        )
        
        self.cache_key_count_gauge = Gauge(
            'cache_key_count',
            'Number of keys in cache',
            ['cache_name', 'cache_type']
        )
        
        self.cache_eviction_rate_gauge = Gauge(
            'cache_eviction_rate_per_second',
            'Cache eviction rate per second',
            ['cache_name', 'eviction_reason']
        )
        
        self.cdn_cache_efficiency_gauge = Gauge(
            'cdn_cache_efficiency_percent',
            'CDN cache efficiency percentage',
            ['cdn_provider', 'edge_location']
        )
        
        self.cache_warming_success_rate_gauge = Gauge(
            'cache_warming_success_rate_percent',
            'Cache warming success rate percentage',
            ['cache_name', 'strategy']
        )
    
    async def initialize_cache_clients(self):
        """Initialize cache clients"""
        try:
            # Initialize Redis clients
            for cluster_config in self.redis_clusters:
                cluster_name = cluster_config['name']
                
                # Sync Redis client
                self.redis_clients[cluster_name] = redis.Redis(
                    host=cluster_config['host'],
                    port=cluster_config.get('port', 6379),
                    db=cluster_config.get('db', 0),
                    password=cluster_config.get('password'),
                    socket_timeout=cluster_config.get('timeout', 5),
                    health_check_interval=30
                )
                
                # Async Redis client
                self.redis_async_clients[cluster_name] = await aioredis.from_url(
                    f"redis://{cluster_config['host']}:{cluster_config.get('port', 6379)}/{cluster_config.get('db', 0)}",
                    password=cluster_config.get('password'),
                    socket_timeout=cluster_config.get('timeout', 5)
                )
                
                logger.info(f"Redis client initialized for cluster: {cluster_name}")
            
            # Initialize Memcached clients
            for i, server in enumerate(self.memcached_servers):
                client_name = f"memcached_{i}"
                self.memcached_clients[client_name] = memcache.Client([server])
                logger.info(f"Memcached client initialized for server: {server}")
        
        except Exception as e:
            logger.error(f"Error initializing cache clients: {e}")
            raise
    
    def record_cache_operation(self,
                             cache_name: str,
                             cache_type: str,
                             operation: str,
                             key: str,
                             hit: bool,
                             execution_time_ms: float,
                             data_size_bytes: int = 0,
                             ttl_seconds: Optional[int] = None,
                             success: bool = True,
                             error_message: Optional[str] = None):
        """Record cache operation metrics"""
        
        # Normalize key pattern
        key_pattern = self._normalize_key_pattern(key)
        
        metrics = CacheMetrics(
            cache_name=cache_name,
            cache_type=cache_type,
            operation=operation,
            key=key,
            key_pattern=key_pattern,
            hit=hit,
            execution_time_ms=execution_time_ms,
            data_size_bytes=data_size_bytes,
            ttl_seconds=ttl_seconds,
            timestamp=datetime.utcnow(),
            success=success,
            error_message=error_message
        )
        
        # Store metrics
        self.cache_metrics.append(metrics)
        
        # Update operation tracking
        ops = self.cache_operations[cache_name]
        ops['total_operations'] += 1
        ops['total_time_ms'] += execution_time_ms
        
        if hit:
            ops['hits'] += 1
        else:
            ops['misses'] += 1
        
        # Update key pattern analysis
        pattern_data = self.key_patterns[key_pattern]
        pattern_data['count'] += 1
        pattern_data['avg_size'] = (pattern_data['avg_size'] * (pattern_data['count'] - 1) + data_size_bytes) / pattern_data['count']
        
        if ttl_seconds:
            pattern_data['avg_ttl'] = (pattern_data['avg_ttl'] * (pattern_data['count'] - 1) + ttl_seconds) / pattern_data['count']
        
        # Update hit ratio for pattern
        if pattern_data['count'] > 0:
            pattern_data['hit_ratio'] = (pattern_data['hit_ratio'] * (pattern_data['count'] - 1) + (1 if hit else 0)) / pattern_data['count']
        
        # Update Prometheus metrics
        self.cache_operation_duration_histogram.labels(
            cache_name=cache_name,
            operation=operation,
            hit_miss='hit' if hit else 'miss'
        ).observe(execution_time_ms / 1000)
        
        # Update hit ratio (calculate periodically)
        if ops['total_operations'] % 100 == 0:  # Update every 100 operations
            hit_ratio = (ops['hits'] / ops['total_operations']) * 100
            self.cache_hit_ratio_gauge.labels(
                cache_name=cache_name,
                cache_type=cache_type
            ).set(hit_ratio)
    
    def _normalize_key_pattern(self, key: str) -> str:
        """Normalize cache key to pattern for analysis"""
        import re
        
        # Replace common patterns
        normalized = key
        
        # Replace UUIDs with placeholder
        normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '{uuid}', normalized)
        
        # Replace numbers with placeholder
        normalized = re.sub(r'\b\d+\b', '{id}', normalized)
        
        # Replace timestamps
        normalized = re.sub(r'\b\d{10,13}\b', '{timestamp}', normalized)
        
        # Replace common separators patterns
        normalized = re.sub(r':[^:]+:([^:]+:)*', ':{value}:', normalized)
        
        return normalized
    
    async def analyze_cache_hit_ratios(self, time_window_minutes: int = 5) -> Dict[str, CacheHitRatioMetrics]:
        """Analyze cache hit ratios"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        recent_metrics = [m for m in self.cache_metrics if m.timestamp >= cutoff_time]
        
        # Group by cache
        by_cache = defaultdict(list)
        for metric in recent_metrics:
            by_cache[metric.cache_name].append(metric)
        
        hit_ratio_analysis = {}
        
        for cache_name, metrics_list in by_cache.items():
            if not metrics_list:
                continue
            
            cache_type = metrics_list[0].cache_type
            total_ops = len(metrics_list)
            hits = len([m for m in metrics_list if m.hit])
            misses = total_ops - hits
            
            hit_ratio = (hits / total_ops) * 100 if total_ops > 0 else 0
            
            # Calculate average times
            hit_times = [m.execution_time_ms for m in metrics_list if m.hit]
            miss_times = [m.execution_time_ms for m in metrics_list if not m.hit]
            
            avg_hit_time = statistics.mean(hit_times) if hit_times else 0
            avg_miss_time = statistics.mean(miss_times) if miss_times else 0
            
            hit_ratio_metrics = CacheHitRatioMetrics(
                cache_name=cache_name,
                cache_type=cache_type,
                time_window_minutes=time_window_minutes,
                total_operations=total_ops,
                cache_hits=hits,
                cache_misses=misses,
                hit_ratio_percent=hit_ratio,
                avg_hit_time_ms=avg_hit_time,
                avg_miss_time_ms=avg_miss_time,
                timestamp=datetime.utcnow()
            )
            
            hit_ratio_analysis[cache_name] = hit_ratio_metrics
            self.hit_ratio_metrics[cache_name].append(hit_ratio_metrics)
        
        return hit_ratio_analysis
    
    async def collect_redis_metrics(self, cluster_name: str) -> Dict[str, Any]:
        """Collect Redis cluster metrics"""
        if cluster_name not in self.redis_async_clients:
            return {}
        
        client = self.redis_async_clients[cluster_name]
        
        try:
            # Get Redis info
            info = await client.info()
            
            # Extract key metrics
            memory_used = info.get('used_memory', 0)
            memory_peak = info.get('used_memory_peak', 0)
            keyspace_hits = info.get('keyspace_hits', 0)
            keyspace_misses = info.get('keyspace_misses', 0)
            evicted_keys = info.get('evicted_keys', 0)
            expired_keys = info.get('expired_keys', 0)
            
            # Calculate hit ratio
            total_ops = keyspace_hits + keyspace_misses
            hit_ratio = (keyspace_hits / total_ops * 100) if total_ops > 0 else 0
            
            # Get key count
            key_count = 0
            for db_key, db_info in info.items():
                if db_key.startswith('db'):
                    key_count += db_info.get('keys', 0)
            
            metrics = {
                'memory_used_bytes': memory_used,
                'memory_peak_bytes': memory_peak,
                'hit_ratio_percent': hit_ratio,
                'key_count': key_count,
                'evicted_keys': evicted_keys,
                'expired_keys': expired_keys,
                'connected_clients': info.get('connected_clients', 0),
                'operations_per_second': info.get('instantaneous_ops_per_sec', 0)
            }
            
            # Update Prometheus metrics
            self.cache_memory_usage_gauge.labels(
                cache_name=cluster_name,
                cache_type='redis'
            ).set(memory_used)
            
            self.cache_key_count_gauge.labels(
                cache_name=cluster_name,
                cache_type='redis'
            ).set(key_count)
            
            self.cache_hit_ratio_gauge.labels(
                cache_name=cluster_name,
                cache_type='redis'
            ).set(hit_ratio)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting Redis metrics for {cluster_name}: {e}")
            return {}
    
    async def collect_cdn_cache_metrics(self, cdn_config: Dict) -> CDNCacheMetrics:
        """Collect CDN cache metrics"""
        try:
            # This would integrate with CDN APIs (CloudFlare, AWS CloudFront, etc.)
            # For now, we'll simulate the metrics collection
            
            cdn_provider = cdn_config['provider']
            edge_location = cdn_config.get('edge_location', 'unknown')
            origin_host = cdn_config.get('origin_host', 'unknown')
            
            # In a real implementation, this would query CDN APIs
            # Simulated metrics for demonstration
            cache_hit_ratio = 85.0  # Would come from CDN API
            origin_offload = 75.0
            bandwidth_saved = 500.0  # MB
            avg_response_time = 50.0  # ms
            purge_requests = 0
            
            metrics = CDNCacheMetrics(
                cdn_provider=cdn_provider,
                edge_location=edge_location,
                origin_host=origin_host,
                cache_hit_ratio=cache_hit_ratio,
                origin_offload_percent=origin_offload,
                bandwidth_saved_mb=bandwidth_saved,
                avg_response_time_ms=avg_response_time,
                cache_purge_requests=purge_requests,
                timestamp=datetime.utcnow()
            )
            
            self.cdn_metrics.append(metrics)
            
            # Update Prometheus metrics
            self.cdn_cache_efficiency_gauge.labels(
                cdn_provider=cdn_provider,
                edge_location=edge_location
            ).set(cache_hit_ratio)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting CDN metrics: {e}")
            return None
    
    async def perform_cache_warming(self, cache_name: str, strategy: str = 'predictive') -> CacheWarmingMetrics:
        """Perform intelligent cache warming"""
        start_time = time.time()
        keys_warmed = 0
        successful_warms = 0
        data_preloaded = 0
        
        try:
            if strategy == 'predictive':
                # Predictive warming based on access patterns
                warming_keys = await self._get_predictive_warming_keys(cache_name)
            elif strategy == 'preload':
                # Preload known hot keys
                warming_keys = await self._get_preload_warming_keys(cache_name)
            else:
                # Default lazy loading approach
                warming_keys = []
            
            # Warm the cache
            for key_data in warming_keys:
                try:
                    key = key_data['key']
                    value = await self._fetch_cache_value(key_data)
                    
                    if value is not None:
                        # Store in cache
                        await self._store_cache_value(cache_name, key, value, key_data.get('ttl'))
                        keys_warmed += 1
                        successful_warms += 1
                        data_preloaded += len(str(value).encode('utf-8'))
                    
                except Exception as e:
                    logger.debug(f"Failed to warm key {key_data.get('key', 'unknown')}: {e}")
                    keys_warmed += 1  # Count attempted
            
            warming_time_ms = (time.time() - start_time) * 1000
            success_rate = (successful_warms / keys_warmed * 100) if keys_warmed > 0 else 0
            data_preloaded_mb = data_preloaded / (1024 * 1024)
            
            # Estimate efficiency gain (simplified)
            cache_efficiency_gain = min(50.0, success_rate * 0.5)  # Max 50% gain
            
            metrics = CacheWarmingMetrics(
                cache_name=cache_name,
                warming_strategy=strategy,
                keys_warmed=keys_warmed,
                warming_time_ms=warming_time_ms,
                success_rate_percent=success_rate,
                data_preloaded_mb=data_preloaded_mb,
                cache_efficiency_gain_percent=cache_efficiency_gain,
                timestamp=datetime.utcnow()
            )
            
            self.warming_metrics.append(metrics)
            
            # Update Prometheus metrics
            self.cache_warming_success_rate_gauge.labels(
                cache_name=cache_name,
                strategy=strategy
            ).set(success_rate)
            
            logger.info(f"Cache warming completed: {keys_warmed} keys, {success_rate:.1f}% success rate")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error performing cache warming: {e}")
            return CacheWarmingMetrics(
                cache_name=cache_name,
                warming_strategy=strategy,
                keys_warmed=0,
                warming_time_ms=0,
                success_rate_percent=0,
                data_preloaded_mb=0,
                cache_efficiency_gain_percent=0,
                timestamp=datetime.utcnow()
            )
    
    async def _get_predictive_warming_keys(self, cache_name: str) -> List[Dict]:
        """Get keys for predictive warming based on access patterns"""
        # Analyze recent access patterns
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_metrics = [m for m in self.cache_metrics 
                         if m.cache_name == cache_name and m.timestamp >= cutoff_time]
        
        # Count key pattern frequencies
        pattern_freq = defaultdict(int)
        for metric in recent_metrics:
            pattern_freq[metric.key_pattern] += 1
        
        # Get top patterns
        top_patterns = sorted(pattern_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Generate warming keys based on patterns
        warming_keys = []
        for pattern, freq in top_patterns:
            # Generate likely keys based on pattern
            # This is simplified - real implementation would be more sophisticated
            for i in range(min(5, freq // 10)):  # Warm up to 5 keys per pattern
                key = pattern.replace('{id}', str(i)).replace('{uuid}', f'uuid-{i}')
                warming_keys.append({
                    'key': key,
                    'pattern': pattern,
                    'frequency': freq,
                    'ttl': 3600  # 1 hour default TTL
                })
        
        return warming_keys
    
    async def _get_preload_warming_keys(self, cache_name: str) -> List[Dict]:
        """Get keys for preload warming"""
        # These would typically come from configuration or database
        # For Creator Economy, these might be popular creator profiles, trending content, etc.
        warming_keys = [
            {'key': 'popular_creators', 'ttl': 1800},
            {'key': 'trending_content', 'ttl': 900},
            {'key': 'platform_config', 'ttl': 3600},
            {'key': 'monetization_rates', 'ttl': 3600}
        ]
        
        return warming_keys
    
    async def _fetch_cache_value(self, key_data: Dict) -> Optional[Any]:
        """Fetch value for cache warming"""
        # This would typically fetch from database or API
        # For demonstration, return a simulated value
        key = key_data['key']
        
        if 'creators' in key:
            return {'type': 'creator_data', 'size': 'medium', 'popularity': 'high'}
        elif 'content' in key:
            return {'type': 'content_data', 'size': 'large', 'engagement': 'high'}
        else:
            return {'type': 'generic_data', 'size': 'small'}
    
    async def _store_cache_value(self, cache_name: str, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in cache"""
        if cache_name in self.redis_async_clients:
            client = self.redis_async_clients[cache_name]
            serialized_value = json.dumps(value)
            
            if ttl:
                await client.setex(key, ttl, serialized_value)
            else:
                await client.set(key, serialized_value)
    
    def generate_optimization_recommendations(self) -> List[CacheOptimizationRecommendation]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        # Analyze hit ratios
        for cache_name, hit_ratio_metrics in self.hit_ratio_metrics.items():
            if not hit_ratio_metrics:
                continue
            
            latest_metrics = hit_ratio_metrics[-1]
            
            # Low hit ratio recommendation
            if latest_metrics.hit_ratio_percent < 70:
                recommendations.append(CacheOptimizationRecommendation(
                    cache_name=cache_name,
                    recommendation_type='increase_ttl',
                    priority='high',
                    description=f'Hit ratio is low at {latest_metrics.hit_ratio_percent:.1f}%. Consider increasing TTL or implementing cache warming.',
                    estimated_improvement_percent=20,
                    implementation_effort='low',
                    potential_savings='15-25% response time improvement',
                    timestamp=datetime.utcnow()
                ))
            
            # High miss penalty recommendation
            if latest_metrics.avg_miss_time_ms > latest_metrics.avg_hit_time_ms * 10:
                recommendations.append(CacheOptimizationRecommendation(
                    cache_name=cache_name,
                    recommendation_type='cache_warming',
                    priority='medium',
                    description=f'Cache misses are {latest_metrics.avg_miss_time_ms/latest_metrics.avg_hit_time_ms:.1f}x slower than hits. Implement predictive cache warming.',
                    estimated_improvement_percent=15,
                    implementation_effort='medium',
                    potential_savings='10-20% average response time improvement',
                    timestamp=datetime.utcnow()
                ))
        
        # Analyze key patterns
        for pattern, pattern_data in self.key_patterns.items():
            if pattern_data['count'] > 100 and pattern_data['hit_ratio'] < 0.5:
                recommendations.append(CacheOptimizationRecommendation(
                    cache_name='pattern_analysis',
                    recommendation_type='key_optimization',
                    priority='medium',
                    description=f'Key pattern "{pattern}" has low hit ratio ({pattern_data["hit_ratio"]*100:.1f}%). Consider optimizing key structure or caching strategy.',
                    estimated_improvement_percent=10,
                    implementation_effort='medium',
                    potential_savings='5-15% cache efficiency improvement',
                    timestamp=datetime.utcnow()
                ))
        
        return recommendations
    
    async def get_cache_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive cache performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        recent_metrics = [m for m in self.cache_metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {'message': 'No recent cache data available'}
        
        # Overall statistics
        total_operations = len(recent_metrics)
        cache_hits = len([m for m in recent_metrics if m.hit])
        overall_hit_ratio = (cache_hits / total_operations) * 100
        
        # Average times
        hit_times = [m.execution_time_ms for m in recent_metrics if m.hit]
        miss_times = [m.execution_time_ms for m in recent_metrics if not m.hit]
        
        avg_hit_time = statistics.mean(hit_times) if hit_times else 0
        avg_miss_time = statistics.mean(miss_times) if miss_times else 0
        
        # Group by cache
        by_cache = defaultdict(list)
        for metric in recent_metrics:
            by_cache[metric.cache_name].append(metric)
        
        cache_summary = {}
        for cache_name, cache_metrics_list in by_cache.items():
            cache_hits_local = len([m for m in cache_metrics_list if m.hit])
            cache_hit_ratio = (cache_hits_local / len(cache_metrics_list)) * 100
            
            cache_summary[cache_name] = {
                'operations': len(cache_metrics_list),
                'hit_ratio_percent': cache_hit_ratio,
                'avg_operation_time_ms': statistics.mean([m.execution_time_ms for m in cache_metrics_list])
            }
        
        return {
            'time_window_minutes': 30,
            'total_operations': total_operations,
            'overall_hit_ratio_percent': overall_hit_ratio,
            'avg_hit_time_ms': avg_hit_time,
            'avg_miss_time_ms': avg_miss_time,
            'cache_efficiency_score': min(100, overall_hit_ratio + (100 - avg_hit_time)),
            'by_cache': cache_summary,
            'optimization_opportunities': len(self.generate_optimization_recommendations())
        }
    
    async def start_monitoring(self):
        """Start continuous cache monitoring"""
        if self.monitoring_active:
            logger.warning("Cache monitoring already active")
            return
        
        await self.initialize_cache_clients()
        self.monitoring_active = True
        
        # Start monitoring tasks
        tasks = [
            self._cache_metrics_collection_loop(),
            self._cache_warming_loop(),
            self._optimization_analysis_loop()
        ]
        
        self._monitoring_tasks = [asyncio.create_task(task) for task in tasks]
        logger.info("Cache performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        
        for task in self._monitoring_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Close async clients
        for client in self.redis_async_clients.values():
            await client.close()
        
        self._monitoring_tasks.clear()
        logger.info("Cache performance monitoring stopped")
    
    async def _cache_metrics_collection_loop(self):
        """Cache metrics collection loop"""
        while self.monitoring_active:
            try:
                # Collect Redis metrics
                for cluster_name in self.redis_clusters:
                    await self.collect_redis_metrics(cluster_name['name'])
                
                # Collect CDN metrics
                for cdn_config in self.cdn_endpoints:
                    await self.collect_cdn_cache_metrics(cdn_config)
                
                # Analyze hit ratios
                await self.analyze_cache_hit_ratios(5)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache metrics collection loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _cache_warming_loop(self):
        """Cache warming loop"""
        while self.monitoring_active:
            try:
                if self.enable_cache_warming:
                    # Perform cache warming for each cache
                    for cluster_config in self.redis_clusters:
                        cache_name = cluster_config['name']
                        await self.perform_cache_warming(cache_name, 'predictive')
                
                # Run cache warming less frequently
                await asyncio.sleep(self.monitoring_interval * 5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache warming loop: {e}")
                await asyncio.sleep(self.monitoring_interval * 5)
    
    async def _optimization_analysis_loop(self):
        """Optimization analysis loop"""
        while self.monitoring_active:
            try:
                # Generate optimization recommendations
                recommendations = self.generate_optimization_recommendations()
                
                # Log high priority recommendations
                for rec in recommendations:
                    if rec.priority == 'high':
                        logger.warning(f"Cache optimization needed: {rec.description}")
                
                await asyncio.sleep(self.monitoring_interval * 10)  # Run every 10 intervals
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization analysis loop: {e}")
                await asyncio.sleep(self.monitoring_interval * 10)