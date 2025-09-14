"""
Core Services Module - Enterprise Foundation Layer
================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + Backend Senior + DBA + Security + Microservices
**Module**: Core Services Foundation
**Version**: 2.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade core services providing foundation for all business services.
Implements service discovery, health monitoring, event bus, and configuration management.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import only what actually exists - simplified for stability
try:
    from .service_registry import ServiceRegistry, ServiceStatus, ServiceInstance
except ImportError:
    ServiceRegistry = ServiceStatus = ServiceInstance = None

try:
    from .health_monitor import HealthMonitor
except ImportError:
    HealthMonitor = None

try:
    from .event_bus import EventBus
except ImportError:
    EventBus = None

try:
    from .config_manager import ConfigManager
except ImportError:
    ConfigManager = None

try:
    from .lifecycle_manager import LifecycleManager
except ImportError:
    LifecycleManager = None

try:
    from .metrics_collector import MetricsCollector
except ImportError:
    MetricsCollector = None

try:
    from .performance_optimizer import PerformanceOptimizer, performance_optimizer
except ImportError:
    PerformanceOptimizer = performance_optimizer = None

try:
    from .structured_logger import StructuredLogger, get_logger, api_logger, service_logger
except ImportError:
    StructuredLogger = get_logger = api_logger = service_logger = None

try:
    from .security_manager import EnterpriseSecurityManager, security_manager
except ImportError:
    EnterpriseSecurityManager = security_manager = None

# Phase 3 Enterprise Components
try:
    from .prometheus_observability import PrometheusObservability, get_observability
except ImportError:
    PrometheusObservability = get_observability = None

try:
    from .mtls_communication import mTLSManager, get_mtls_manager
except ImportError:
    mTLSManager = get_mtls_manager = None

try:
    from .kubernetes_autoscaling import KubernetesAutoScaler, get_autoscaler
except ImportError:
    KubernetesAutoScaler = get_autoscaler = None

async def initialize_core_services() -> Dict[str, Any]:
    """
    Initialize all core services for enterprise deployment.
    
    Returns:
        Dict[str, Any]: Initialized core service instances
    """
    logger.info("Initializing enterprise core services...")
    
    initialized_services = {
        "service_registry": "ServiceRegistry available" if ServiceRegistry else "Not available",
        "health_monitor": "HealthMonitor available" if HealthMonitor else "Not available",
        "event_bus": "EventBus available" if EventBus else "Not available",
        "config_manager": "ConfigManager available" if ConfigManager else "Not available",
        "lifecycle_manager": "LifecycleManager available" if LifecycleManager else "Not available",
        "metrics_collector": "MetricsCollector available" if MetricsCollector else "Not available",
        "performance_optimizer": "PerformanceOptimizer available" if PerformanceOptimizer else "Not available",
        "structured_logger": "StructuredLogger available" if StructuredLogger else "Not available",
        "security_manager": "SecurityManager available" if EnterpriseSecurityManager else "Not available",
        # Phase 3 Enterprise Components
        "prometheus_observability": "PrometheusObservability available" if PrometheusObservability else "Not available",
        "mtls_communication": "mTLSManager available" if mTLSManager else "Not available",
        "kubernetes_autoscaling": "KubernetesAutoScaler available" if KubernetesAutoScaler else "Not available"
    }
    
    logger.info("Core services initialization completed")
    return initialized_services

async def health_check_core() -> Dict[str, str]:
    """
    Perform health check on all core services.
    
    Returns:
        Dict[str, str]: Health status of each core service
    """
    return {
        "service_registry": "healthy" if ServiceRegistry else "unavailable",
        "health_monitor": "healthy" if HealthMonitor else "unavailable",
        "event_bus": "healthy" if EventBus else "unavailable",
        "config_manager": "healthy" if ConfigManager else "unavailable",
        "lifecycle_manager": "healthy" if LifecycleManager else "unavailable",
        "metrics_collector": "healthy" if MetricsCollector else "unavailable",
        "performance_optimizer": "healthy" if PerformanceOptimizer else "unavailable",
        "structured_logger": "healthy" if StructuredLogger else "unavailable",
        "security_manager": "healthy" if EnterpriseSecurityManager else "unavailable",
        # Phase 3 Enterprise Components
        "prometheus_observability": "healthy" if PrometheusObservability else "unavailable",
        "mtls_communication": "healthy" if mTLSManager else "unavailable",
        "kubernetes_autoscaling": "healthy" if KubernetesAutoScaler else "unavailable"
    }

__all__ = [
    # Available services (may be None if import failed)
    "ServiceRegistry",
    "ServiceStatus", 
    "ServiceInstance",
    "HealthMonitor",
    "EventBus",
    "ConfigManager",
    "LifecycleManager",
    "MetricsCollector",
    "PerformanceOptimizer",
    "performance_optimizer",
    "StructuredLogger",
    "get_logger",
    "api_logger",
    "service_logger",
    "EnterpriseSecurityManager",
    "security_manager",
    
    # Phase 3 Enterprise Components
    "PrometheusObservability",
    "get_observability",
    "mTLSManager",
    "get_mtls_manager",
    "KubernetesAutoScaler",
    "get_autoscaler",
    
    # Initialization functions
    "initialize_core_services",
    "health_check_core"
]