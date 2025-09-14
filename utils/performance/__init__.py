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

__all__ = [
    "CacheManager",
    "MetricsCollector",
    "PerformanceMonitor",
    "CircuitBreaker", 
    "RateLimiter"
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
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")