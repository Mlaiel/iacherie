"""Ainflue Core Infrastructure - Enterprise Infrastructure Management
================================================================

Core infrastructure management providing database, caching, message queuing,
event sourcing, performance monitoring, health checks, metrics collection,
configuration management, service discovery, and distributed system primitives.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any

# Infrastructure core imports (existing files to be moved here)
try:
    from .logging import LoggingCore
except ImportError:
    LoggingCore = None

try:
    from .middleware import MiddlewareCore
except ImportError:
    MiddlewareCore = None

try:
    from .performance_monitoring_core import PerformanceMonitoringCore
except ImportError:
    PerformanceMonitoringCore = None

# New infrastructure core files (to be created)
try:
    from .database_core import DatabaseCore
except ImportError:
    DatabaseCore = None

try:
    from .cache_core import CacheCore
except ImportError:
    CacheCore = None

try:
    from .message_queue_core import MessageQueueCore
except ImportError:
    MessageQueueCore = None

try:
    from .event_sourcing_core import EventSourcingCore
except ImportError:
    EventSourcingCore = None

try:
    from .cqrs_core import CQRSCore
except ImportError:
    CQRSCore = None

try:
    from .circuit_breaker_core import CircuitBreakerCore
except ImportError:
    CircuitBreakerCore = None

try:
    from .rate_limiter_core import RateLimiterCore
except ImportError:
    RateLimiterCore = None

try:
    from .health_check_core import HealthCheckCore
except ImportError:
    HealthCheckCore = None

try:
    from .metrics_collector_core import MetricsCollectorCore
except ImportError:
    MetricsCollectorCore = None

try:
    from .tracing_core import TracingCore
except ImportError:
    TracingCore = None

try:
    from .configuration_manager_core import ConfigurationManagerCore
except ImportError:
    ConfigurationManagerCore = None

try:
    from .dependency_injection_core import DependencyInjectionCore
except ImportError:
    DependencyInjectionCore = None

try:
    from .service_discovery_core import ServiceDiscoveryCore
except ImportError:
    ServiceDiscoveryCore = None

try:
    from .load_balancer_core import LoadBalancerCore
except ImportError:
    LoadBalancerCore = None

__all__ = [
    "LoggingCore", "MiddlewareCore", "PerformanceMonitoringCore",
    "DatabaseCore", "CacheCore", "MessageQueueCore", "EventSourcingCore",
    "CQRSCore", "CircuitBreakerCore", "RateLimiterCore", "HealthCheckCore",
    "MetricsCollectorCore", "TracingCore", "ConfigurationManagerCore",
    "DependencyInjectionCore", "ServiceDiscoveryCore", "LoadBalancerCore"
]