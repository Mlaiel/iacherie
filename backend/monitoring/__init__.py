"""Backend Monitoring Module
=========================

Unified monitoring and observability system for the Ainflue platform.
Consolidates 60+ monitoring files into 12 focused modules for enterprise-grade observability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core observability (existing)
from .observability import (
    EnterpriseObservability,
    EnterpriseConfig,
    ObservabilityLevel,
    TracingBackend,
    LoggingBackend
)

# Unified monitoring modules (consolidated)
from .metrics import (
    UnifiedMetricsCollector,
    Metric,
    MetricType,
    MetricCategory,
    MetricPeriod,
    metrics_collector,
    start_metrics_collection,
    stop_metrics_collection,
    get_metric,
    get_business_metrics,
    get_performance_metrics,
    get_system_summary
)

from .alerts import (
    UnifiedAlertManager,
    Alert,
    AlertCategory,
    AlertSeverity,
    AlertStatus,
    AlertChannel,
    alert_manager,
    create_business_alert,
    create_technical_alert,
    create_ai_alert,
    create_security_alert,
    get_open_alerts,
    get_alert_statistics
)

from .health import (
    UnifiedHealthManager,
    HealthCheck,
    HealthStatus,
    HealthCheckType,
    SLAMonitor,
    CircuitBreaker,
    health_manager,
    start_health_monitoring,
    stop_health_monitoring,
    run_health_checks,
    get_health_status,
    get_health_summary,
    get_sla_status
)

from .logging import (
    UnifiedLoggingManager,
    LogEntry,
    LogLevel,
    LogCategory,
    ErrorReport,
    ErrorSeverity,
    logging_manager,
    log_info,
    log_warning,
    log_error,
    log_debug,
    capture_error,
    log_business_event,
    log_security_event,
    start_operation,
    end_operation,
    get_log_statistics,
    get_error_reports
)

from .profiling import (
    UnifiedProfilingManager,
    PerformanceProfile,
    ResourceUsage,
    CapacityForecast,
    ResourceType,
    ProfileType,
    profiling_manager,
    start_performance_monitoring,
    stop_performance_monitoring,
    profile_function,
    get_performance_summary,
    get_optimization_recommendations,
    get_capacity_forecast
)

from .dashboards import (
    UnifiedDashboardManager,
    Dashboard,
    DashboardWidget,
    DashboardType,
    WidgetType,
    dashboard_manager,
    get_production_dashboard,
    get_business_dashboard,
    get_system_dashboard,
    get_dashboard_list,
    create_custom_dashboard
)

from .enterprise import (
    UnifiedEnterpriseManager,
    EnterpriseOrchestrator,
    PrometheusIntegration,
    GrafanaIntegration,
    DatadogIntegration,
    ElasticsearchIntegration,
    enterprise_manager,
    start_enterprise_monitoring,
    stop_enterprise_monitoring,
    get_enterprise_status,
    setup_enterprise_dashboards,
    query_metrics,
    search_enterprise_logs
)

# Consolidated exports
__all__ = [
    # Original observability components
    'EnterpriseObservability',
    'EnterpriseConfig', 
    'ObservabilityLevel',
    'TracingBackend',
    'LoggingBackend',
    
    # Metrics module
    'UnifiedMetricsCollector',
    'Metric',
    'MetricType',
    'MetricCategory',
    'MetricPeriod',
    'metrics_collector',
    'start_metrics_collection',
    'stop_metrics_collection',
    'get_metric',
    'get_business_metrics',
    'get_performance_metrics',
    'get_system_summary',
    
    # Alerts module
    'UnifiedAlertManager',
    'Alert',
    'AlertCategory',
    'AlertSeverity',
    'AlertStatus',
    'AlertChannel',
    'alert_manager',
    'create_business_alert',
    'create_technical_alert',
    'create_ai_alert',
    'create_security_alert',
    'get_open_alerts',
    'get_alert_statistics',
    
    # Health module
    'UnifiedHealthManager',
    'HealthCheck',
    'HealthStatus',
    'HealthCheckType',
    'SLAMonitor',
    'CircuitBreaker',
    'health_manager',
    'start_health_monitoring',
    'stop_health_monitoring',
    'run_health_checks',
    'get_health_status',
    'get_health_summary',
    'get_sla_status',
    
    # Logging module
    'UnifiedLoggingManager',
    'LogEntry',
    'LogLevel',
    'LogCategory',
    'ErrorReport',
    'ErrorSeverity',
    'logging_manager',
    'log_info',
    'log_warning',
    'log_error',
    'log_debug',
    'capture_error',
    'log_business_event',
    'log_security_event',
    'start_operation',
    'end_operation',
    'get_log_statistics',
    'get_error_reports',
    
    # Profiling module
    'UnifiedProfilingManager',
    'PerformanceProfile',
    'ResourceUsage',
    'CapacityForecast',
    'ResourceType',
    'ProfileType',
    'profiling_manager',
    'start_performance_monitoring',
    'stop_performance_monitoring',
    'profile_function',
    'get_performance_summary',
    'get_optimization_recommendations',
    'get_capacity_forecast',
    
    # Dashboards module
    'UnifiedDashboardManager',
    'Dashboard',
    'DashboardWidget',
    'DashboardType',
    'WidgetType',
    'dashboard_manager',
    'get_production_dashboard',
    'get_business_dashboard',
    'get_system_dashboard',
    'get_dashboard_list',
    'create_custom_dashboard',
    
    # Enterprise module
    'UnifiedEnterpriseManager',
    'EnterpriseOrchestrator',
    'PrometheusIntegration',
    'GrafanaIntegration',
    'DatadogIntegration',
    'ElasticsearchIntegration',
    'enterprise_manager',
    'start_enterprise_monitoring',
    'stop_enterprise_monitoring',
    'get_enterprise_status',
    'setup_enterprise_dashboards',
    'query_metrics',
    'search_enterprise_logs'
]

# Module information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Unified monitoring system - consolidates 60+ files into 12 focused modules"

# Quick start functions for convenience
async def start_all_monitoring(config: dict = None):
    """Start all monitoring components"""
    try:
        # Start metrics collection
        await start_metrics_collection()
        
        # Start health monitoring  
        await start_health_monitoring()
        
        # Start performance monitoring
        await start_performance_monitoring()
        
        # Start enterprise monitoring if configured
        if config and config.get("enterprise"):
            await start_enterprise_monitoring(config["enterprise"])
        
        print("✅ All monitoring components started successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")
        return False


async def stop_all_monitoring():
    """Stop all monitoring components"""
    try:
        await stop_metrics_collection()
        await stop_health_monitoring()
        await stop_performance_monitoring()
        await stop_enterprise_monitoring()
        
        print("✅ All monitoring components stopped successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to stop monitoring: {e}")
        return False


def get_monitoring_status():
    """Get status of all monitoring components"""
    return {
        "metrics": get_system_summary(),
        "alerts": get_alert_statistics(),
        "health": get_health_summary(),
        "logs": get_log_statistics(),
        "performance": get_performance_summary(),
        "enterprise": get_enterprise_status(),
        "dashboards": len(get_dashboard_list())
    }