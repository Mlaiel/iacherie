"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

Performance Monitoring Enterprise Module
Advanced technical performance monitoring for Creator Economy platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

from .performance_monitor import (
    PerformanceMonitor,
    EndpointMetrics,
    PerformanceStats
)

# Module version
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Export public API
__all__ = [
    "PerformanceMonitor",
    "EndpointMetrics", 
    "PerformanceStats",
    # System monitoring
    "SystemResourceMonitor",
    "DatabasePerformanceAnalyzer",
    "ApiPerformanceProfiler",
    "ContentProcessingPerformance",
    # Network monitoring
    "NetworkPerformanceMonitor",
    "MicroservicesPerformanceTracker", 
    "CachePerformanceOptimizer",
    "LoadBalancerPerformance",
    # Application monitoring
    "ApplicationProfiler",
    "RealTimePerformanceDashboard",
    "UserExperiencePerformance",
    "BackgroundJobPerformance",
    # Analytics & optimization
    "PerformanceAnomalyDetector",
    "CapacityPlanningAnalyzer",
    "PerformanceOptimizationEngine",
    "MultiCloudPerformanceMonitor"
]

# Lazy imports for performance
def __getattr__(name: str):
    """Lazy import of performance monitoring components"""
    if name == "SystemResourceMonitor":
        from .system_resource_monitor import SystemResourceMonitor
        return SystemResourceMonitor
    elif name == "DatabasePerformanceAnalyzer":
        from .database_performance_analyzer import DatabasePerformanceAnalyzer
        return DatabasePerformanceAnalyzer
    elif name == "ApiPerformanceProfiler":
        from .api_performance_profiler import ApiPerformanceProfiler
        return ApiPerformanceProfiler
    elif name == "ContentProcessingPerformance":
        from .content_processing_performance import ContentProcessingPerformance
        return ContentProcessingPerformance
    elif name == "NetworkPerformanceMonitor":
        from .network_performance_monitor import NetworkPerformanceMonitor
        return NetworkPerformanceMonitor
    elif name == "MicroservicesPerformanceTracker":
        from .microservices_performance_tracker import MicroservicesPerformanceTracker
        return MicroservicesPerformanceTracker
    elif name == "CachePerformanceOptimizer":
        from .cache_performance_optimizer import CachePerformanceOptimizer
        return CachePerformanceOptimizer
    elif name == "LoadBalancerPerformance":
        from .load_balancer_performance import LoadBalancerPerformance
        return LoadBalancerPerformance
    elif name == "ApplicationProfiler":
        from .application_profiler import ApplicationProfiler
        return ApplicationProfiler
    elif name == "RealTimePerformanceDashboard":
        from .real_time_performance_dashboard import RealTimePerformanceDashboard
        return RealTimePerformanceDashboard
    elif name == "UserExperiencePerformance":
        from .user_experience_performance import UserExperiencePerformance
        return UserExperiencePerformance
    elif name == "BackgroundJobPerformance":
        from .background_job_performance import BackgroundJobPerformance
        return BackgroundJobPerformance
    elif name == "PerformanceAnomalyDetector":
        from .performance_anomaly_detector import PerformanceAnomalyDetector
        return PerformanceAnomalyDetector
    elif name == "CapacityPlanningAnalyzer":
        from .capacity_planning_analyzer import CapacityPlanningAnalyzer
        return CapacityPlanningAnalyzer
    elif name == "PerformanceOptimizationEngine":
        from .performance_optimization_engine import PerformanceOptimizationEngine
        return PerformanceOptimizationEngine
    elif name == "MultiCloudPerformanceMonitor":
        from .multi_cloud_performance_monitor import MultiCloudPerformanceMonitor
        return MultiCloudPerformanceMonitor
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Performance monitoring configuration
PERFORMANCE_CONFIG = {
    "metrics_retention_days": 365,
    "real_time_update_interval": 5,  # seconds
    "anomaly_detection_enabled": True,
    "auto_optimization_enabled": True,
    "sla_thresholds": {
        "api_response_time_p95_ms": 200,
        "api_response_time_p99_ms": 500,
        "page_load_time_seconds": 2,
        "database_query_time_p95_ms": 100,
        "cpu_utilization_percent": 80,
        "memory_utilization_percent": 85
    }
}