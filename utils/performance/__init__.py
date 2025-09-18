"""
Performance Utilities Module - Enterprise Architecture Level 3
============================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Ultra-optimized performance utilities for enterprise scalability:
- Multi-level intelligent caching
- Prometheus metrics collection
- Real-time performance monitoring
- Circuit breaker patterns
- Intelligent rate limiting

Performance Targets:
- Cache operations: < 1ms (P95)
- Utility functions: < 10ms (P95)
- Memory usage: < 100MB per utility
- CPU usage: < 5% per operation
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cache_manager import CacheManager
    from .metrics_collector import MetricsCollector
    from .performance_monitor import PerformanceMonitor
    from .circuit_breaker import CircuitBreaker
    from .rate_limiter import RateLimiter
    from .resource_optimizer import ResourceOptimizer
    from .memory_profiler import MemoryProfiler
    from .cpu_optimizer import CPUOptimizer
    from .disk_optimizer import DiskOptimizer
    from .network_optimizer import NetworkOptimizer
    from .database_optimizer import DatabaseOptimizer
    from .compression_manager import CompressionManager
    from .load_balancer import LoadBalancer
    from .thread_pool_manager import ThreadPoolManager
    from .async_optimizer import AsyncOptimizer

__all__ = [
    "CacheManager",
    "MetricsCollector",
    "PerformanceMonitor",
    "CircuitBreaker", 
    "RateLimiter",
    "ResourceOptimizer",
    "MemoryProfiler",
    "CPUOptimizer",
    "DiskOptimizer",
    "NetworkOptimizer",
    "DatabaseOptimizer",
    "CompressionManager",
    "LoadBalancer",
    "ThreadPoolManager",
    "AsyncOptimizer",
    "CacheManagerFactory",
    "MetricsCollectorFactory",
    "PerformanceMonitorFactory",
    "CircuitBreakerFactory",
    "RateLimiterFactory",
    "ResourceOptimizerFactory",
    "MemoryProfilerFactory",
    "CPUOptimizerFactory",
    "DiskOptimizerFactory",
    "NetworkOptimizerFactory",
    "DatabaseOptimizerFactory",
    "CompressionManagerFactory",
    "LoadBalancerFactory",
    "ThreadPoolManagerFactory",
    "AsyncOptimizerFactory"
]

# Lazy loading for enterprise performance
def __getattr__(name: str):
    if name == "CacheManager":
        from .cache_manager import CacheManager
        return CacheManager
    elif name == "MetricsCollector":
        from .metrics_collector import MetricsCollector
        return MetricsCollector
    elif name == "PerformanceMonitor":
        from .performance_monitor import PerformanceMonitor
        return PerformanceMonitor
    elif name == "CircuitBreaker":
        from .circuit_breaker import CircuitBreaker
        return CircuitBreaker
    elif name == "RateLimiter":
        from .rate_limiter import RateLimiter
        return RateLimiter
    elif name == "ResourceOptimizer":
        from .resource_optimizer import ResourceOptimizer
        return ResourceOptimizer
    elif name == "MemoryProfiler":
        from .memory_profiler import MemoryProfiler
        return MemoryProfiler
    elif name == "CPUOptimizer":
        from .cpu_optimizer import CPUOptimizer
        return CPUOptimizer
    elif name == "DiskOptimizer":
        from .disk_optimizer import DiskOptimizer
        return DiskOptimizer
    elif name == "NetworkOptimizer":
        from .network_optimizer import NetworkOptimizer
        return NetworkOptimizer
    elif name == "DatabaseOptimizer":
        from .database_optimizer import DatabaseOptimizer
        return DatabaseOptimizer
    elif name == "CompressionManager":
        from .compression_manager import CompressionManager
        return CompressionManager
    elif name == "LoadBalancer":
        from .load_balancer import LoadBalancer
        return LoadBalancer
    elif name == "ThreadPoolManager":
        from .thread_pool_manager import ThreadPoolManager
        return ThreadPoolManager
    elif name == "AsyncOptimizer":
        from .async_optimizer import AsyncOptimizer
        return AsyncOptimizer
    elif name == "CacheManagerFactory":
        from .cache_manager import CacheManagerFactory
        return CacheManagerFactory
    elif name == "MetricsCollectorFactory":
        from .metrics_collector import MetricsCollectorFactory
        return MetricsCollectorFactory
    elif name == "PerformanceMonitorFactory":
        from .performance_monitor import PerformanceMonitorFactory
        return PerformanceMonitorFactory
    elif name == "CircuitBreakerFactory":
        from .circuit_breaker import CircuitBreakerFactory
        return CircuitBreakerFactory
    elif name == "RateLimiterFactory":
        from .rate_limiter import RateLimiterFactory
        return RateLimiterFactory
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")