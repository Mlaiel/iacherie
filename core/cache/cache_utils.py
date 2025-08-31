"""
Cache Module Configuration and Utilities
Central configuration and utility functions for the cache system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GlobalCacheConfig:
    """Global cache configuration"""
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    redis_cluster: bool = False
    redis_cluster_nodes: list = None
    redis_max_connections: int = 100
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    
    # Memory cache configuration
    memory_cache_size: int = 1000
    memory_cache_ttl: int = 3600
    memory_eviction_policy: str = "lru"
    
    # Vector cache configuration
    vector_index_type: str = "faiss"
    vector_dimension: int = 512
    vector_metric: str = "cosine"
    vector_index_factory: str = "Flat"
    
    # Content cache configuration
    content_chunk_size: int = 1024 * 1024  # 1MB
    content_compression: bool = True
    content_encryption: bool = False
    
    # Analytics configuration
    analytics_batch_size: int = 1000
    analytics_flush_interval: int = 300  # 5 minutes
    
    # Monitoring configuration
    monitoring_enabled: bool = True
    monitoring_interval: int = 30
    metrics_retention_hours: int = 24
    
    # Performance tuning
    max_concurrent_operations: int = 1000
    operation_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        if self.redis_cluster_nodes is None:
            self.redis_cluster_nodes = []
    
    @classmethod
    def from_env(cls) -> 'GlobalCacheConfig':
        """Create configuration from environment variables"""



        return cls(
            redis_host=os.getenv('CACHE_REDIS_HOST', 'localhost'),
            redis_port=int(os.getenv('CACHE_REDIS_PORT', '6379')),
            redis_db=int(os.getenv('CACHE_REDIS_DB', '0')),
            redis_password=os.getenv('CACHE_REDIS_PASSWORD'),
            redis_ssl=os.getenv('CACHE_REDIS_SSL', 'false').lower() == 'true',
            redis_cluster=os.getenv('CACHE_REDIS_CLUSTER', 'false').lower() == 'true',
            redis_max_connections=int(os.getenv('CACHE_REDIS_MAX_CONNECTIONS', '100')),
            
            memory_cache_size=int(os.getenv('CACHE_MEMORY_SIZE', '1000')),
            memory_cache_ttl=int(os.getenv('CACHE_MEMORY_TTL', '3600')),
            memory_eviction_policy=os.getenv('CACHE_MEMORY_EVICTION_POLICY', 'lru'),
            
            vector_dimension=int(os.getenv('CACHE_VECTOR_DIMENSION', '512')),
            vector_metric=os.getenv('CACHE_VECTOR_METRIC', 'cosine'),
            
            content_chunk_size=int(os.getenv('CACHE_CONTENT_CHUNK_SIZE', str(1024 * 1024))),
            content_compression=os.getenv('CACHE_CONTENT_COMPRESSION', 'true').lower() == 'true',
            content_encryption=os.getenv('CACHE_CONTENT_ENCRYPTION', 'false').lower() == 'true',
            
            analytics_batch_size=int(os.getenv('CACHE_ANALYTICS_BATCH_SIZE', '1000')),
            analytics_flush_interval=int(os.getenv('CACHE_ANALYTICS_FLUSH_INTERVAL', '300')),
            
            monitoring_enabled=os.getenv('CACHE_MONITORING_ENABLED', 'true').lower() == 'true',
            monitoring_interval=int(os.getenv('CACHE_MONITORING_INTERVAL', '30')),
            metrics_retention_hours=int(os.getenv('CACHE_METRICS_RETENTION_HOURS', '24')),
            
            max_concurrent_operations=int(os.getenv('CACHE_MAX_CONCURRENT_OPERATIONS', '1000')),
            operation_timeout=int(os.getenv('CACHE_OPERATION_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('CACHE_RETRY_ATTEMPTS', '3')),
            retry_delay=float(os.getenv('CACHE_RETRY_DELAY', '1.0'))
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'GlobalCacheConfig':
        """Create configuration from JSON file"""



        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_path}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'redis': {
                'host': self.redis_host,
                'port': self.redis_port,
                'db': self.redis_db,
                'password': self.redis_password,
                'ssl': self.redis_ssl,
                'cluster': self.redis_cluster,
                'cluster_nodes': self.redis_cluster_nodes,
                'max_connections': self.redis_max_connections,
                'socket_timeout': self.redis_socket_timeout,
                'socket_connect_timeout': self.redis_socket_connect_timeout
            },
            'memory': {
                'size': self.memory_cache_size,
                'ttl': self.memory_cache_ttl,
                'eviction_policy': self.memory_eviction_policy
            },
            'vector': {
                'index_type': self.vector_index_type,
                'dimension': self.vector_dimension,
                'metric': self.vector_metric,
                'index_factory': self.vector_index_factory
            },
            'content': {
                'chunk_size': self.content_chunk_size,
                'compression': self.content_compression,
                'encryption': self.content_encryption
            },
            'analytics': {
                'batch_size': self.analytics_batch_size,
                'flush_interval': self.analytics_flush_interval
            },
            'monitoring': {
                'enabled': self.monitoring_enabled,
                'interval': self.monitoring_interval,
                'metrics_retention_hours': self.metrics_retention_hours
            },
            'performance': {
                'max_concurrent_operations': self.max_concurrent_operations,
                'operation_timeout': self.operation_timeout,
                'retry_attempts': self.retry_attempts,
                'retry_delay': self.retry_delay
            }
        }

# Global configuration instance
_global_config: Optional[GlobalCacheConfig] = None

def get_global_config() -> GlobalCacheConfig:
    """Get global cache configuration"""
    global _global_config
    if _global_config is None:
        _global_config = GlobalCacheConfig.from_env()
    return _global_config

def set_global_config(config: GlobalCacheConfig):
    """Set global cache configuration"""
    global _global_config
    _global_config = config

def reset_global_config():
    """Reset global configuration to default"""
    global _global_config
    _global_config = None

# Cache key utilities

def build_cache_key(*parts: str, namespace: str = "", separator: str = ":") -> str:
    """Build cache key from parts"""
    key_parts = []
    
    if namespace:
        key_parts.append(namespace)
    
    key_parts.extend(str(part) for part in parts if part)
    
    return separator.join(key_parts)

def extract_namespace(cache_key: str, separator: str = ":") -> str:
    """Extract namespace from cache key"""
    parts = cache_key.split(separator)
    return parts[0] if parts else ""

def extract_key_parts(cache_key: str, separator: str = ":") -> list:
    """Extract key parts from cache key"""



    return cache_key.split(separator)

# Serialization utilities

def serialize_cache_value(value: Any, compression: bool = False) -> bytes:
    """Serialize value for caching"""
    import json
    import gzip
    
    try:
        # Convert to JSON
        json_data = json.dumps(value, default=str, ensure_ascii=False)
        data = json_data.encode('utf-8')
        
        # Compress if requested
        if compression:
            data = gzip.compress(data)
        
        return data
    except Exception as e:
        raise ValueError(f"Failed to serialize cache value: {e}")

def deserialize_cache_value(data: bytes, compression: bool = False) -> Any:
    """Deserialize cached value"""
    import json
    import gzip
    
    try:
        # Decompress if needed
        if compression:
            data = gzip.decompress(data)
        
        # Parse JSON
        json_data = data.decode('utf-8')
        return json.loads(json_data)
    except Exception as e:
        raise ValueError(f"Failed to deserialize cache value: {e}")

# Cache size utilities

def calculate_object_size(obj: Any) -> int:
    """Calculate approximate size of object in bytes"""
    import sys
    import json
    
    try:
        # For simple types
        if isinstance(obj, (int, float, bool, type(None))):
            return sys.getsizeof(obj)
        
        # For strings
        if isinstance(obj, str):
            return len(obj.encode('utf-8'))
        
        # For complex objects, use JSON serialization size
        json_str = json.dumps(obj, default=str, ensure_ascii=False)
        return len(json_str.encode('utf-8'))
    except:
        # Fallback to sys.getsizeof
        return sys.getsizeof(obj)

def format_bytes(size_bytes: int) -> str:
    """Format bytes as human readable string"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

# Cache health utilities

def calculate_cache_efficiency(hits: int, misses: int) -> float:
    """Calculate cache efficiency score (0.0 to 1.0)"""
    total = hits + misses
    if total == 0:
        return 0.0
    
    hit_rate = hits / total
    
    # Weight hit rate more heavily for higher efficiency
    if hit_rate >= 0.9:
        return 1.0
    elif hit_rate >= 0.8:
        return 0.8 + (hit_rate - 0.8) * 2  # 0.8 to 1.0
    elif hit_rate >= 0.6:
        return 0.6 + (hit_rate - 0.6) * 1  # 0.6 to 0.8
    else:
        return hit_rate  # 0.0 to 0.6

def get_cache_recommendations(
    hit_rate: float,
    memory_utilization: float,
    latency_ms: float,
    error_rate: float
) -> list:
    """Get cache optimization recommendations"""
    recommendations = []
    
    if hit_rate < 0.5:
        recommendations.append({
            'priority': 'high',
            'category': 'performance',
            'message': 'Very low hit rate. Consider increasing cache size or adjusting TTL.',
            'actions': ['increase_cache_size', 'optimize_ttl', 'review_access_patterns']
        })
    elif hit_rate < 0.8:
        recommendations.append({
            'priority': 'medium',
            'category': 'performance', 
            'message': 'Hit rate could be improved. Consider cache warming or prefetching.',
            'actions': ['implement_cache_warming', 'add_prefetching', 'optimize_eviction_policy']
        })
    
    if memory_utilization > 0.9:
        recommendations.append({
            'priority': 'high',
            'category': 'capacity',
            'message': 'Memory utilization is very high. Risk of performance degradation.',
            'actions': ['increase_memory_limit', 'implement_compression', 'optimize_data_structures']
        })
    elif memory_utilization > 0.8:
        recommendations.append({
            'priority': 'medium',
            'category': 'capacity',
            'message': 'Memory utilization is high. Monitor for potential issues.',
            'actions': ['monitor_memory_growth', 'consider_memory_increase']
        })
    
    if latency_ms > 100:
        recommendations.append({
            'priority': 'medium',
            'category': 'latency',
            'message': 'High cache latency detected. Consider optimization.',
            'actions': ['optimize_serialization', 'check_network_latency', 'review_cache_topology']
        })
    
    if error_rate > 0.05:  # 5%
        recommendations.append({
            'priority': 'high',
            'category': 'reliability',
            'message': 'High error rate detected. Investigation required.',
            'actions': ['check_cache_logs', 'verify_connections', 'review_error_patterns']
        })
    elif error_rate > 0.01:  # 1%
        recommendations.append({
            'priority': 'medium',
            'category': 'reliability',
            'message': 'Elevated error rate. Monitor for trends.',
            'actions': ['monitor_error_trends', 'review_retry_policies']
        })
    
    return recommendations

# Performance profiling utilities

class CacheProfiler:
    """Simple cache operation profiler"""
    
    def __init__(self):
        self.operation_times = {}
        self.operation_counts = {}
    
    def start_operation(self, operation_name: str):
        """Start timing an operation"""
        import time
        self.operation_times[operation_name] = time.time()
    
    def end_operation(self, operation_name: str):
        """End timing an operation"""
        import time
        if operation_name in self.operation_times:
            elapsed = time.time() - self.operation_times[operation_name]
            
            if operation_name not in self.operation_counts:
                self.operation_counts[operation_name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0
                }
            
            stats = self.operation_counts[operation_name]
            stats['count'] += 1
            stats['total_time'] += elapsed
            stats['min_time'] = min(stats['min_time'], elapsed)
            stats['max_time'] = max(stats['max_time'], elapsed)
            
            del self.operation_times[operation_name]
            return elapsed
        return 0.0
    
    def get_stats(self) -> dict:
        """Get profiling statistics"""
        stats = {}
        for operation, data in self.operation_counts.items():
            if data['count'] > 0:
                stats[operation] = {
                    'count': data['count'],
                    'total_time': data['total_time'],
                    'average_time': data['total_time'] / data['count'],
                    'min_time': data['min_time'],
                    'max_time': data['max_time']
                }
        return stats
    
    def reset(self):
        """Reset profiler statistics"""
        self.operation_times.clear()
        self.operation_counts.clear()

# Global profiler instance
_global_profiler = CacheProfiler()

def get_cache_profiler() -> CacheProfiler:
    """Get global cache profiler"""



    return _global_profiler

# Cache warming utilities

def generate_cache_warmup_plan(
    cache_keys: list,
    priority_weights: dict = None,
    batch_size: int = 100
) -> list:
    """Generate cache warmup plan with batched operations"""
    
    if priority_weights is None:
        priority_weights = {}
    
    # Sort keys by priority
    def get_priority(key):
        for pattern, weight in priority_weights.items():
            if pattern in key:
                return weight
        return 0
    
    sorted_keys = sorted(cache_keys, key=get_priority, reverse=True)
    
    # Create batches
    batches = []
    for i in range(0, len(sorted_keys), batch_size):
        batch = sorted_keys[i:i + batch_size]
        batches.append({
            'batch_id': i // batch_size,
            'keys': batch,
            'size': len(batch),
            'estimated_time': len(batch) * 0.01  # Rough estimate: 10ms per key
        })
    
    return batches

# Error handling utilities

class CacheError(Exception):
    """Base cache error"""
    pass

class CacheConnectionError(CacheError):
    """Cache connection error"""
    pass

class CacheTimeoutError(CacheError):
    """Cache operation timeout"""
    pass

class CacheSerializationError(CacheError):
    """Cache serialization error"""
    pass

class CacheInvalidationError(CacheError):
    """Cache invalidation error"""
    pass

def handle_cache_error(func):
    """Decorator for cache error handling"""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log error and re-raise as appropriate cache error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Cache operation failed: {e}")
            
            if "connection" in str(e).lower():
                raise CacheConnectionError(f"Cache connection failed: {e}")
            elif "timeout" in str(e).lower():
                raise CacheTimeoutError(f"Cache operation timed out: {e}")
            elif "serializ" in str(e).lower():
                raise CacheSerializationError(f"Cache serialization failed: {e}")
            else:
                raise CacheError(f"Cache operation failed: {e}")
    
    return wrapper

# Cache metrics collection

class CacheMetricsCollector:
    """Lightweight metrics collector for cache operations"""
    
    def __init__(self):
        self.metrics = {
            'operations': 0,
            'hits': 0,
            'misses': 0,
            'errors': 0,
            'total_latency': 0.0,
            'operations_by_type': {},
            'start_time': None
        }
        import time
        self.metrics['start_time'] = time.time()
    
    def record_operation(self, operation_type: str, hit: bool, latency: float, error: bool = False):
        """Record cache operation"""
        self.metrics['operations'] += 1
        
        if hit:
            self.metrics['hits'] += 1
        else:
            self.metrics['misses'] += 1
        
        if error:
            self.metrics['errors'] += 1
        
        self.metrics['total_latency'] += latency
        
        if operation_type not in self.metrics['operations_by_type']:
            self.metrics['operations_by_type'][operation_type] = 0
        self.metrics['operations_by_type'][operation_type] += 1
    
    def get_summary(self) -> dict:
        """Get metrics summary"""
        import time
        uptime = time.time() - self.metrics['start_time']
        
        total_ops = self.metrics['operations']
        
        return {
            'uptime_seconds': uptime,
            'total_operations': total_ops,
            'operations_per_second': total_ops / uptime if uptime > 0 else 0,
            'hit_rate': self.metrics['hits'] / total_ops if total_ops > 0 else 0,
            'miss_rate': self.metrics['misses'] / total_ops if total_ops > 0 else 0,
            'error_rate': self.metrics['errors'] / total_ops if total_ops > 0 else 0,
            'average_latency': self.metrics['total_latency'] / total_ops if total_ops > 0 else 0,
            'operations_by_type': self.metrics['operations_by_type'].copy()
        }
