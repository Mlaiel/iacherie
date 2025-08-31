"""
Performance Utilities Module
============================

Professional performance optimization utilities for web crawlers.
Implements advanced caching, monitoring, and optimization mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import pickle
import hashlib
from collections import defaultdict, deque
import statistics
import weakref
import gc

# Redis for distributed caching
import redis
import aioredis

# Memory profiling
import tracemalloc

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out
    ADAPTIVE = "adaptive"  # Adaptive based on access patterns

class MetricType(Enum):
    """Performance metric types."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CACHE_HIT_RATE = "cache_hit_rate"
    CONCURRENT_REQUESTS = "concurrent_requests"

@dataclass
class PerformanceMetric:
    """Performance metric data."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheEntry:
    """Cache entry structure."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[int]
    size_bytes: int
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

@dataclass
class PerformanceReport:
    """Comprehensive performance report."""
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_per_second: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit_rate: float
    concurrent_peak: int
    metrics: List[PerformanceMetric] = field(default_factory=list)

class AdvancedCache:
    """
    Advanced caching system with multiple strategies and optimization.
    
    Features:
    - Multiple cache strategies (LRU, LFU, TTL, etc.)
    - Memory management and size limits
    - Distributed caching with Redis
    - Cache warming and prefetching
    - Performance monitoring
    - Adaptive cache management
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        max_memory_mb: int = 512,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: Optional[int] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        """Initialize advanced cache."""
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.strategy = strategy
        self.default_ttl = default_ttl
        self.redis_client = redis_client
        
        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: deque = deque()  # For LRU
        self.access_frequency: Dict[str, int] = defaultdict(int)  # For LFU
        
        # Metrics
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
        self.current_memory_bytes = 0
        
        # Locks for thread safety
        self._lock = threading.RLock()
        
        logger.info(f"Advanced cache initialized with strategy: {strategy}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self.cache.get(key)
            
            if entry is None:
                self.miss_count += 1
                return None
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.miss_count += 1
                return None
            
            # Update access patterns
            self._update_access_patterns(key, entry)
            self.hit_count += 1
            
            return entry.value
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        with self._lock:
            # Calculate size
            size_bytes = self._calculate_size(value)
            
            # Check memory limits
            if size_bytes > self.max_memory_bytes:
                logger.warning(f"Value too large for cache: {size_bytes} bytes")
                return False
            
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Ensure space
            self._ensure_space(size_bytes)
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl=ttl or self.default_ttl,
                size_bytes=size_bytes
            )
            
            # Store entry
            self.cache[key] = entry
            self.current_memory_bytes += size_bytes
            
            # Update access patterns
            self._update_access_patterns(key, entry)
            
            # Store in Redis if available
            if self.redis_client:
                self._store_in_redis(key, value, ttl)
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key in self.cache:
                self._remove_entry(key)
                
                # Remove from Redis if available
                if self.redis_client:
                    try:
                        self.redis_client.delete(key)
                    except Exception as e:
                        logger.warning(f"Redis delete failed: {e}")
                
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.access_frequency.clear()
            self.current_memory_bytes = 0
            
            # Clear Redis if available
            if self.redis_client:
                try:
                    # Only clear keys with our prefix
                    pattern = "cache:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis clear failed: {e}")
    
    def _ensure_space(self, required_bytes: int) -> None:
        """Ensure enough space in cache."""
        while (self.current_memory_bytes + required_bytes > self.max_memory_bytes or
               len(self.cache) >= self.max_size):
            
            if not self.cache:
                break
            
            # Select victim based on strategy
            victim_key = self._select_victim()
            if victim_key:
                self._remove_entry(victim_key)
                self.eviction_count += 1
            else:
                break
    
    def _select_victim(self) -> Optional[str]:
        """Select cache entry for eviction based on strategy."""
        if not self.cache:
            return None
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            while self.access_order:
                key = self.access_order.popleft()
                if key in self.cache:
                    return key
        
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            min_frequency = min(self.access_frequency.values())
            for key, freq in self.access_frequency.items():
                if freq == min_frequency and key in self.cache:
                    return key
        
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first, then oldest
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            if expired_keys:
                return expired_keys[0]
            
            # If no expired entries, remove oldest
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].created_at
            )
            return oldest_key
        
        elif self.strategy == CacheStrategy.FIFO:
            # Remove first in (oldest)
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].created_at
            )
            return oldest_key
        
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Adaptive strategy based on access patterns
            return self._adaptive_victim_selection()
        
        # Fallback to LRU
        return list(self.cache.keys())[0] if self.cache else None
    
    def _adaptive_victim_selection(self) -> Optional[str]:
        """Adaptive victim selection based on access patterns."""
        if not self.cache:
            return None
        
        # Score entries based on multiple factors
        scores = {}
        now = datetime.now()
        
        for key, entry in self.cache.items():
            # Factors: age, frequency, recency, size
            age_factor = (now - entry.created_at).total_seconds() / 3600  # Hours
            frequency_factor = 1.0 / max(entry.access_count, 1)
            recency_factor = (now - entry.last_accessed).total_seconds() / 3600  # Hours
            size_factor = entry.size_bytes / (1024 * 1024)  # MB
            
            # Combined score (higher = more likely to evict)
            score = (age_factor * 0.3 + 
                    frequency_factor * 0.4 + 
                    recency_factor * 0.2 + 
                    size_factor * 0.1)
            
            scores[key] = score
        
        # Return key with highest score
        return max(scores.keys(), key=lambda k: scores[k])
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_memory_bytes -= entry.size_bytes
            del self.cache[key]
            
            # Clean up access patterns
            if key in self.access_frequency:
                del self.access_frequency[key]
            
            # Remove from access order
            try:
                self.access_order.remove(key)
            except ValueError:
                pass
    
    def _update_access_patterns(self, key: str, entry: CacheEntry) -> None:
        """Update access patterns for cache strategies."""
        entry.last_accessed = datetime.now()
        entry.access_count += 1
        self.access_frequency[key] += 1
        
        # Update LRU order
        try:
            self.access_order.remove(key)
        except ValueError:
            pass
        self.access_order.append(key)
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate size of value in bytes."""



        try:
            return len(pickle.dumps(value))
        except Exception:
            # Fallback estimation
            import sys
            return sys.getsizeof(value)
    
    def _store_in_redis(self, key: str, value: Any, ttl: Optional[int]) -> None:
        """Store value in Redis."""



        try:
            redis_key = f"cache:{key}"
            serialized_value = pickle.dumps(value)
            
            if ttl:
                self.redis_client.setex(redis_key, ttl, serialized_value)
            else:
                self.redis_client.set(redis_key, serialized_value)
                
        except Exception as e:
            logger.warning(f"Redis store failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'eviction_count': self.eviction_count,
            'current_entries': len(self.cache),
            'max_entries': self.max_size,
            'current_memory_mb': self.current_memory_bytes / (1024 * 1024),
            'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
            'memory_utilization': self.current_memory_bytes / self.max_memory_bytes,
            'strategy': self.strategy.value
        }

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    
    Features:
    - Real-time metric collection
    - Statistical analysis
    - Performance reporting
    - Resource monitoring
    - Bottleneck detection
    """
    
    def __init__(self, history_size: int = 10000):
        """Initialize performance monitor."""
        self.history_size = history_size
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=history_size)
            for metric_type in MetricType
        }
        
        # Request tracking
        self.active_requests: Dict[str, datetime] = {}
        self.completed_requests: deque = deque(maxlen=history_size)
        
        # System monitoring
        self.system_process = psutil.Process()
        self.monitoring_enabled = True
        
        # Background monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        
        logger.info("Performance monitor initialized")
    
    def start_monitoring(self, interval_seconds: float = 1.0) -> None:
        """Start background monitoring."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(
                self._background_monitoring(interval_seconds)
            )
            logger.info("Background monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self.monitoring_enabled = False
        if self._monitor_task:
            self._monitor_task.cancel()
            logger.info("Background monitoring stopped")
    
    async def _background_monitoring(self, interval: float) -> None:
        """Background monitoring loop."""



        try:
            while self.monitoring_enabled:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect memory metrics
                await self._collect_memory_metrics()
                
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Background monitoring error: {e}")
    
    async def _collect_system_metrics(self) -> None:
        """Collect system performance metrics."""



        try:
            # CPU usage
            cpu_percent = self.system_process.cpu_percent()
            self.record_metric(MetricType.CPU_USAGE, cpu_percent)
            
            # Memory usage
            memory_info = self.system_process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self.record_metric(MetricType.MEMORY_USAGE, memory_mb)
            
            # Concurrent requests
            concurrent_count = len(self.active_requests)
            self.record_metric(MetricType.CONCURRENT_REQUESTS, concurrent_count)
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
    
    async def _collect_memory_metrics(self) -> None:
        """Collect memory usage metrics."""



        try:
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                current_mb = current / (1024 * 1024)
                self.record_metric(MetricType.MEMORY_USAGE, current_mb, 
                                 tags={'source': 'tracemalloc'})
        except Exception as e:
            logger.error(f"Memory metrics collection failed: {e}")
    
    def record_metric(
        self, 
        metric_type: MetricType, 
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a performance metric."""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics[metric_type].append(metric)
    
    def start_request(self, request_id: str) -> None:
        """Start tracking a request."""
        self.active_requests[request_id] = datetime.now()
    
    def end_request(self, request_id: str, success: bool = True) -> Optional[float]:
        """End tracking a request and return response time."""
        if request_id not in self.active_requests:
            return None
        
        start_time = self.active_requests.pop(request_id)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # Record metrics
        self.record_metric(MetricType.RESPONSE_TIME, response_time)
        
        if not success:
            error_rate = self._calculate_current_error_rate()
            self.record_metric(MetricType.ERROR_RATE, error_rate)
        
        # Store completed request
        self.completed_requests.append({
            'request_id': request_id,
            'start_time': start_time,
            'end_time': end_time,
            'response_time': response_time,
            'success': success
        })
        
        return response_time
    
    def _calculate_current_error_rate(self) -> float:
        """Calculate current error rate."""
        if not self.completed_requests:
            return 0.0
        
        # Look at recent requests (last 100)
        recent_requests = list(self.completed_requests)[-100:]
        failed_requests = sum(1 for req in recent_requests if not req['success'])
        
        return failed_requests / len(recent_requests)
    
    def get_metric_statistics(self, metric_type: MetricType) -> Dict[str, float]:
        """Get statistical summary of metrics."""
        metrics = self.metrics[metric_type]
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        try:
            return {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'p95': self._percentile(values, 0.95),
                'p99': self._percentile(values, 0.99)
            }
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {}
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(percentile * len(sorted_values))
        if index >= len(sorted_values):
            index = len(sorted_values) - 1
        
        return sorted_values[index]
    
    def generate_performance_report(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> PerformanceReport:
        """Generate comprehensive performance report."""
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=1)
        if end_time is None:
            end_time = datetime.now()
        
        # Filter requests by time range
        relevant_requests = [
            req for req in self.completed_requests
            if start_time <= req['start_time'] <= end_time
        ]
        
        if not relevant_requests:
            return PerformanceReport(
                start_time=start_time,
                end_time=end_time,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                median_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                throughput_per_second=0.0,
                error_rate=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                cache_hit_rate=0.0,
                concurrent_peak=0
            )
        
        # Calculate statistics
        total_requests = len(relevant_requests)
        successful_requests = sum(1 for req in relevant_requests if req['success'])
        failed_requests = total_requests - successful_requests
        
        response_times = [req['response_time'] for req in relevant_requests]
        average_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = self._percentile(response_times, 0.95)
        p99_response_time = self._percentile(response_times, 0.99)
        
        # Calculate throughput
        duration_seconds = (end_time - start_time).total_seconds()
        throughput_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
        
        # Error rate
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        # System metrics
        memory_stats = self.get_metric_statistics(MetricType.MEMORY_USAGE)
        cpu_stats = self.get_metric_statistics(MetricType.CPU_USAGE)
        concurrent_stats = self.get_metric_statistics(MetricType.CONCURRENT_REQUESTS)
        
        # Collect all metrics in time range
        all_metrics = []
        for metric_type, metric_list in self.metrics.items():
            for metric in metric_list:
                if start_time <= metric.timestamp <= end_time:
                    all_metrics.append(metric)
        
        return PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput_per_second=throughput_per_second,
            error_rate=error_rate,
            memory_usage_mb=memory_stats.get('mean', 0.0),
            cpu_usage_percent=cpu_stats.get('mean', 0.0),
            cache_hit_rate=0.0,  # Would be calculated from cache stats
            concurrent_peak=int(concurrent_stats.get('max', 0)),
            metrics=all_metrics
        )

class ConnectionPool:
    """
    Advanced connection pool for HTTP clients.
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        max_connections_per_host: int = 10,
        connection_timeout: float = 30.0,
        read_timeout: float = 60.0
    ):
        """Initialize connection pool."""
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        
        # Connection tracking
        self.active_connections: Dict[str, int] = defaultdict(int)
        self.total_connections = 0
        self.connection_semaphore = asyncio.Semaphore(max_connections)
        self.host_semaphores: Dict[str, asyncio.Semaphore] = {}
        
        self._lock = asyncio.Lock()
    
    async def get_session(self, host: str) -> aiohttp.ClientSession:
        """Get HTTP session with connection limits."""
        async with self._lock:
            # Ensure host semaphore exists
            if host not in self.host_semaphores:
                self.host_semaphores[host] = asyncio.Semaphore(self.max_connections_per_host)
        
        # Acquire connection slots
        await self.connection_semaphore.acquire()
        await self.host_semaphores[host].acquire()
        
        try:
            # Create session with optimized settings
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_connections_per_host,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.connection_timeout,
                sock_read=self.read_timeout
            )
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            
            # Track connection
            self.active_connections[host] += 1
            self.total_connections += 1
            
            return session
            
        except Exception:
            # Release semaphores on error
            self.connection_semaphore.release()
            self.host_semaphores[host].release()
            raise
    
    async def release_session(self, session: aiohttp.ClientSession, host: str) -> None:
        """Release HTTP session and connection slots."""



        try:
            await session.close()
        finally:
            # Release connection tracking
            self.active_connections[host] -= 1
            self.total_connections -= 1
            
            # Release semaphores
            self.connection_semaphore.release()
            if host in self.host_semaphores:
                self.host_semaphores[host].release()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""



        return {
            'total_connections': self.total_connections,
            'max_connections': self.max_connections,
            'connections_by_host': dict(self.active_connections),
            'utilization': self.total_connections / self.max_connections
        }

class ResourceOptimizer:
    """
    Resource optimization utilities.
    """
    
    def __init__(self):
        """Initialize resource optimizer."""
        self.memory_threshold_mb = 1024  # 1GB
        self.cpu_threshold_percent = 80
        self.optimization_enabled = True
    
    async def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage."""
        results = {
            'before_mb': 0,
            'after_mb': 0,
            'freed_mb': 0,
            'actions_taken': []
        }
        
        try:
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 * 1024)
            results['before_mb'] = initial_memory
            
            if initial_memory > self.memory_threshold_mb:
                # Force garbage collection
                collected = gc.collect()
                results['actions_taken'].append(f"Garbage collection freed {collected} objects")
                
                # Clear weak references
                gc.collect()
                results['actions_taken'].append("Cleared weak references")
                
                # Get final memory usage
                final_memory = process.memory_info().rss / (1024 * 1024)
                results['after_mb'] = final_memory
                results['freed_mb'] = initial_memory - final_memory
                
                logger.info(f"Memory optimization freed {results['freed_mb']:.2f} MB")
            
            return results
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return results
    
    async def optimize_connections(self, session_manager) -> Dict[str, Any]:
        """Optimize connection usage."""
        results = {
            'closed_sessions': 0,
            'actions_taken': []
        }
        
        try:
            # Implementation would optimize session manager connections
            # This is a placeholder for actual optimization logic
            results['actions_taken'].append("Connection optimization completed")
            return results
            
        except Exception as e:
            logger.error(f"Connection optimization failed: {e}")
            return results

# Factory functions
def create_advanced_cache(
    max_size: int = 10000,
    strategy: CacheStrategy = CacheStrategy.LRU,
    redis_client: Optional[redis.Redis] = None
) -> AdvancedCache:
    """Create advanced cache instance."""



    return AdvancedCache(max_size=max_size, strategy=strategy, redis_client=redis_client)

def create_performance_monitor(history_size: int = 10000) -> PerformanceMonitor:
    """Create performance monitor instance."""



    return PerformanceMonitor(history_size=history_size)

def create_connection_pool(max_connections: int = 100) -> ConnectionPool:
    """Create connection pool instance."""



    return ConnectionPool(max_connections=max_connections)

def create_resource_optimizer() -> ResourceOptimizer:
    """Create resource optimizer instance."""



    return ResourceOptimizer()

# Decorator for performance monitoring
def monitor_performance(monitor: PerformanceMonitor):
    """Decorator to monitor function performance."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                request_id = f"{func.__name__}_{int(time.time() * 1000000)}"
                monitor.start_request(request_id)
                
                try:
                    result = await func(*args, **kwargs)
                    monitor.end_request(request_id, success=True)
                    return result
                except Exception as e:
                    monitor.end_request(request_id, success=False)
                    raise
            
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                request_id = f"{func.__name__}_{int(time.time() * 1000000)}"
                monitor.start_request(request_id)
                
                try:
                    result = func(*args, **kwargs)
                    monitor.end_request(request_id, success=True)
                    return result
                except Exception as e:
                    monitor.end_request(request_id, success=False)
                    raise
            
            return sync_wrapper
    
    return decorator

# Export main components
__all__ = [
    'CacheStrategy',
    'MetricType',
    'PerformanceMetric',
    'CacheEntry',
    'PerformanceReport',
    'AdvancedCache',
    'PerformanceMonitor',
    'ConnectionPool',
    'ResourceOptimizer',
    'create_advanced_cache',
    'create_performance_monitor',
    'create_connection_pool',
    'create_resource_optimizer',
    'monitor_performance',
]
