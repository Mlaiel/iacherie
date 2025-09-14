"""
⚡ AINFLUE PLATFORM - PERFORMANCE UTILITIES MODULE
Enterprise-grade performance optimization utilities with ultra-low latency guarantees

Author: Fahed Mlaiel (Performance Engineer + DevOps Expert)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Classification: CONFIDENTIAL ENTERPRISE

This module provides ultra-optimized utilities following strict enterprise standards:
- Sub-10ms response times guaranteed
- Multi-level caching strategies
- Real-time performance monitoring
- Circuit breaker patterns
- Intelligent rate limiting
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

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__performance_target__ = "< 10ms P95"
__optimization_level__ = "ULTRA-ENTERPRISE"