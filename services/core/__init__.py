"""
Core Services Module - Enterprise Foundation Layer
================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + Backend Senior + DBA + Security + Microservices
**Module**: Core Services Foundation
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade core services providing foundation for all business services.
Implements service discovery, health monitoring, event bus, and configuration management.
"""

from .service_registry import (
    ServiceRegistry,
    ServiceInstance,
    ServiceStatus,
    ServiceType,
    DiscoveryStrategy
)

from .health_monitor import (
    HealthMonitor,
    HealthStatus,
    HealthCheck,
    CircuitBreakerState,
    ServiceHealthMetrics
)

from .event_bus import (
    EventBus,
    Event,
    EventType,
    EventHandler,
    Subscription
)

from .config_manager import (
    ConfigManager,
    ConfigSource,
    ConfigUpdate,
    SecretManager
)

from .lifecycle_manager import (
    LifecycleManager,
    ServiceLifecycle,
    LifecycleEvent,
    LifecycleState
)

from .metrics_collector import (
    MetricsCollector,
    Metric,
    MetricType,
    TimeSeriesData,
    PerformanceMetrics
)

__all__ = [
    # Service Discovery & Registry
    "ServiceRegistry",
    "ServiceInstance", 
    "ServiceStatus",
    "ServiceType",
    "DiscoveryStrategy",
    
    # Health Monitoring
    "HealthMonitor",
    "HealthStatus",
    "HealthCheck",
    "CircuitBreakerState", 
    "ServiceHealthMetrics",
    
    # Event Management
    "EventBus",
    "Event",
    "EventType",
    "EventHandler",
    "Subscription",
    
    # Configuration
    "ConfigManager",
    "ConfigSource",
    "ConfigUpdate",
    "SecretManager",
    
    # Lifecycle Management
    "LifecycleManager",
    "ServiceLifecycle",
    "LifecycleEvent",
    "LifecycleState",
    
    # Metrics & Observability
    "MetricsCollector",
    "Metric",
    "MetricType", 
    "TimeSeriesData",
    "PerformanceMetrics"
]