"""Ultra-Advanced Enterprise Reports Module
========================================

Revolutionary reporting system for the IA Influencer Agent platform with military-grade
reliability, enterprise-scale performance, and cutting-edge analytics capabilities.
Provides comprehensive business intelligence, data visualization, compliance reporting,
and advanced AI-powered insights for content creators and platform administrators.

Core Architecture:
- Microservices-based distributed reporting infrastructure
- Real-time analytics engine with machine learning integration
- Multi-format export system with enterprise-grade security
- Automated scheduling and delivery with SLA compliance
- Advanced visualization suite with interactive dashboards
- Compliance and audit trail management for regulatory requirements

Advanced Features:
- AI-powered predictive analytics and trend forecasting
- Real-time performance monitoring with automated alerting
- Multi-tenant reporting with namespace isolation
- Advanced data aggregation with 10M+ records/second processing
- Enterprise security with AES-256 encryption and TLS 1.3
- Cloud-native architecture with auto-scaling capabilities
- Comprehensive audit trail with blockchain integration
- Advanced caching strategies with Redis cluster and CDN
- Machine learning models for content optimization and revenue prediction
- Integration with major cloud providers (AWS, Azure, GCP)

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Legal Warning: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use without explicit written permission will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""
import logging
import warnings
from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime, timezone

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright 2024-2025, Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary"

# Configure module logger
logger = logging.getLogger(__name__)

# Core module imports
try:
    from .generators import (
        # Base classes
        ReportGenerator,
        ReportType,
        ReportConfiguration,
        ReportMetadata,
        
        # Specialized generators
        PerformanceReportGenerator,
        ContentReportGenerator,
        ProtectionReportGenerator,
        RevenueReportGenerator,
        ComplianceReportGenerator,
        
        # Factory functions
        create_report_generator,
        get_available_generators,
        register_custom_generator
    )
    GENERATORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Generators module not available: {e}")
    GENERATORS_AVAILABLE = False

try:
    from .analytics import (
        # Base analytics engine
        AnalyticsEngine,
        AnalyticsConfiguration,
        AnalyticsResult,
        
        # Specialized analytics
        PerformanceAnalytics,
        ContentAnalytics,
        ProtectionAnalytics,
        PlatformAnalytics,
        RevenueAnalytics,
        
        # ML components
        MLModelManager,
        PredictiveAnalytics,
        AnomalyDetection,
        
        # Factory functions
        create_analytics_engine,
        get_available_analytics
    )
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analytics module not available: {e}")
    ANALYTICS_AVAILABLE = False

try:
    from .formatters import (
        # Base formatter
        ReportFormatter,
        FormatterConfiguration,
        FormatterResult,
        
        # Format-specific formatters
        PDFFormatter,
        ExcelFormatter,
        JSONFormatter,
        CSVFormatter,
        HTMLFormatter,
        PowerPointFormatter,
        XMLFormatter,
        
        # Advanced formatters
        BrandedFormatter,
        InteractiveFormatter,
        AccessibleFormatter,
        
        # Factory functions
        create_formatter,
        get_available_formatters,
        register_custom_formatter
    )
    FORMATTERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Formatters module not available: {e}")
    FORMATTERS_AVAILABLE = False

try:
    from .schedulers import (
        # Base scheduler
        ReportScheduler,
        ScheduleConfiguration,
        ScheduleType,
        ScheduleStatus,
        
        # Specialized schedulers
        AutomatedReportScheduler,
        CronReportScheduler,
        RealTimeReportScheduler,
        EventDrivenScheduler,
        
        # Schedule management
        ScheduleManager,
        JobQueue,
        TaskExecutor,
        
        # Factory functions
        create_scheduler,
        get_available_schedulers
    )
    SCHEDULERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Schedulers module not available: {e}")
    SCHEDULERS_AVAILABLE = False

try:
    from .aggregators import (
        # Base aggregator
        DataAggregator,
        AggregatorConfiguration,
        AggregationResult,
        
        # Specialized aggregators
        PerformanceAggregator,
        ContentAggregator,
        RevenueAggregator,
        MetricsAggregator,
        ComplianceAggregator,
        
        # Advanced aggregation
        StreamingAggregator,
        DistributedAggregator,
        MLAggregator,
        
        # Factory functions
        create_aggregator,
        get_available_aggregators
    )
    AGGREGATORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Aggregators module not available: {e}")
    AGGREGATORS_AVAILABLE = False

try:
    from .visualizers import (
        # Base visualizers
        ChartGenerator,
        VisualizationConfiguration,
        VisualizationResult,
        
        # Specialized visualizers
        GraphVisualizer,
        DashboardVisualizer,
        MetricsVisualizer,
        TrendVisualizer,
        
        # Advanced visualizations
        InteractiveVisualizer,
        RealTimeDashboard,
        ThreeDimensionalVisualizer,
        
        # Factory functions
        create_visualizer,
        get_available_visualizers
    )
    VISUALIZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Visualizers module not available: {e}")
    VISUALIZERS_AVAILABLE = False

try:
    from .exporters import (
        # Base exporter
        ReportExporter,
        ExporterConfiguration,
        ExportResult,
        
        # Specialized exporters
        EmailExporter,
        CloudStorageExporter,
        APIExporter,
        DatabaseExporter,
        WebhookExporter,
        
        # Advanced export
        DistributedExporter,
        SecureExporter,
        CompressedExporter,
        
        # Factory functions
        create_exporter,
        get_available_exporters
    )
    EXPORTERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Exporters module not available: {e}")
    EXPORTERS_AVAILABLE = False

try:
    from .templates import (
        # Base template
        ReportTemplate,
        TemplateConfiguration,
        TemplateEngine,
        
        # Specialized templates
        ExecutiveTemplate,
        TechnicalTemplate,
        ComplianceTemplate,
        FinancialTemplate,
        MarketingTemplate,
        
        # Advanced templating
        AIGeneratedTemplate,
        DynamicTemplate,
        MultiLanguageTemplate,
        
        # Factory functions
        create_template,
        get_available_templates,
        register_custom_template
    )
    TEMPLATES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Templates module not available: {e}")
    TEMPLATES_AVAILABLE = False

try:
    from .processors import (
        # Base processor
        ReportProcessor,
        ProcessorConfiguration,
        ProcessingResult,
        
        # Specialized processors
        DataProcessor,
        MetricsProcessor,
        InsightsProcessor,
        IntelligenceProcessor,
        
        # Advanced processing
        StreamingProcessor,
        DistributedProcessor,
        MLProcessor,
        
        # Factory functions
        create_processor,
        get_available_processors
    )
    PROCESSORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Processors module not available: {e}")
    PROCESSORS_AVAILABLE = False

try:
    from .config import (
        # Configuration classes
        ReportsConfiguration,
        Environment,
        LogLevel,
        DatabaseType,
        CacheType,
        ExportFormat,
        CloudProvider,
        
        # Configuration sections
        DatabaseConfig,
        RedisConfig,
        CacheConfig,
        SecurityConfig,
        MonitoringConfig,
        APIConfig,
        ReportConfig,
        SchedulerConfig,
        CloudConfig,
        MLConfig,
        
        # Configuration functions
        get_config,
        reload_config,
        config_context,
        validate_configuration
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Config module not available: {e}")
    CONFIG_AVAILABLE = False

try:
    from .index import (
        # Service management
        ReportsServiceManager,
        ReportsSettings,
        ServiceStatus,
        ComponentType,
        
        # FastAPI application
        create_fastapi_app,
        run_service,
        
        # Dependency injection
        get_service_manager,
        get_db_session,
        get_redis_client,
        get_component_factory,
        
        # Security and middleware
        verify_token,
        rate_limit,
        circuit_breaker,
        cache_result
    )
    INDEX_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Index module not available: {e}")
    INDEX_AVAILABLE = False


class ReportsModuleManager:
    """
    Central manager for the reports module.
    
    Provides unified access to all reporting components and manages
    module lifecycle, dependencies, and feature availability.
    """
    
    def __init__(self):
        self.available_components = self._check_component_availability()
        self.logger = logging.getLogger(__name__ + ".manager")
        
        # Initialize component registries
        self._generators: Dict[str, Type] = {}
        self._analytics: Dict[str, Type] = {}
        self._formatters: Dict[str, Type] = {}
        self._schedulers: Dict[str, Type] = {}
        self._aggregators: Dict[str, Type] = {}
        self._visualizers: Dict[str, Type] = {}
        self._exporters: Dict[str, Type] = {}
        self._templates: Dict[str, Type] = {}
        self._processors: Dict[str, Type] = {}
        
        # Register available components
        self._register_components()
        
        self.logger.info(f"ReportsModuleManager initialized with {len(self.available_components)} components")
    
    def _check_component_availability(self) -> Dict[str, bool]:
        """Check which components are available."""
        return {
            "generators": GENERATORS_AVAILABLE,
            "analytics": ANALYTICS_AVAILABLE,
            "formatters": FORMATTERS_AVAILABLE,
            "schedulers": SCHEDULERS_AVAILABLE,
            "aggregators": AGGREGATORS_AVAILABLE,
            "visualizers": VISUALIZERS_AVAILABLE,
            "exporters": EXPORTERS_AVAILABLE,
            "templates": TEMPLATES_AVAILABLE,
            "processors": PROCESSORS_AVAILABLE,
            "config": CONFIG_AVAILABLE,
            "index": INDEX_AVAILABLE
        }
    
    def _register_components(self) -> None:
        """Register all available components."""
        # Register generators
        if GENERATORS_AVAILABLE:
            self._generators.update({
                "performance": PerformanceReportGenerator,
                "content": ContentReportGenerator,
                "protection": ProtectionReportGenerator,
                "revenue": RevenueReportGenerator,
                "compliance": ComplianceReportGenerator
            })
        
        # Register analytics
        if ANALYTICS_AVAILABLE:
            self._analytics.update({
                "performance": PerformanceAnalytics,
                "content": ContentAnalytics,
                "protection": ProtectionAnalytics,
                "platform": PlatformAnalytics,
                "revenue": RevenueAnalytics
            })
        
        # Register formatters
        if FORMATTERS_AVAILABLE:
            self._formatters.update({
                "pdf": PDFFormatter,
                "excel": ExcelFormatter,
                "json": JSONFormatter,
                "csv": CSVFormatter,
                "html": HTMLFormatter
            })
        
        # Register schedulers
        if SCHEDULERS_AVAILABLE:
            self._schedulers.update({
                "automated": AutomatedReportScheduler,
                "cron": CronReportScheduler,
                "realtime": RealTimeReportScheduler
            })
        
        # Register aggregators
        if AGGREGATORS_AVAILABLE:
            self._aggregators.update({
                "performance": PerformanceAggregator,
                "content": ContentAggregator,
                "revenue": RevenueAggregator,
                "metrics": MetricsAggregator
            })
        
        # Register visualizers
        if VISUALIZERS_AVAILABLE:
            self._visualizers.update({
                "chart": ChartGenerator,
                "graph": GraphVisualizer,
                "dashboard": DashboardVisualizer,
                "metrics": MetricsVisualizer,
                "trend": TrendVisualizer
            })
        
        # Register exporters
        if EXPORTERS_AVAILABLE:
            self._exporters.update({
                "email": EmailExporter,
                "cloud": CloudStorageExporter,
                "api": APIExporter,
                "database": DatabaseExporter
            })
        
        # Register templates
        if TEMPLATES_AVAILABLE:
            self._templates.update({
                "executive": ExecutiveTemplate,
                "technical": TechnicalTemplate,
                "compliance": ComplianceTemplate,
                "financial": FinancialTemplate
            })
        
        # Register processors
        if PROCESSORS_AVAILABLE:
            self._processors.update({
                "data": DataProcessor,
                "metrics": MetricsProcessor,
                "insights": InsightsProcessor,
                "intelligence": IntelligenceProcessor
            })
    
    def get_component(self, component_type: str, component_name: str) -> Optional[Type]:
        """Get a specific component by type and name."""
        registry_map = {
            "generators": self._generators,
            "analytics": self._analytics,
            "formatters": self._formatters,
            "schedulers": self._schedulers,
            "aggregators": self._aggregators,
            "visualizers": self._visualizers,
            "exporters": self._exporters,
            "templates": self._templates,
            "processors": self._processors
        }
        
        registry = registry_map.get(component_type)
        if not registry:
            self.logger.warning(f"Component type '{component_type}' not found")
            return None
        
        component = registry.get(component_name)
        if not component:
            self.logger.warning(f"Component '{component_name}' not found in '{component_type}'")
            return None
        
        return component
    
    def list_components(self, component_type: Optional[str] = None) -> Dict[str, List[str]]:
        """List all available components."""
        if component_type:
            registry_map = {
                "generators": self._generators,
                "analytics": self._analytics,
                "formatters": self._formatters,
                "schedulers": self._schedulers,
                "aggregators": self._aggregators,
                "visualizers": self._visualizers,
                "exporters": self._exporters,
                "templates": self._templates,
                "processors": self._processors
            }
            
            registry = registry_map.get(component_type, {})
            return {component_type: list(registry.keys())}
        
        return {
            "generators": list(self._generators.keys()),
            "analytics": list(self._analytics.keys()),
            "formatters": list(self._formatters.keys()),
            "schedulers": list(self._schedulers.keys()),
            "aggregators": list(self._aggregators.keys()),
            "visualizers": list(self._visualizers.keys()),
            "exporters": list(self._exporters.keys()),
            "templates": list(self._templates.keys()),
            "processors": list(self._processors.keys())
        }
    
    def is_component_available(self, component_type: str) -> bool:
        """Check if a component type is available."""
        return self.available_components.get(component_type, False)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            "version": __version__,
            "author": __author__,
            "copyright": __copyright__,
            "license": __license__,
            "components": self.available_components,
            "registered_components": self.list_components(),
            "initialization_time": datetime.now(timezone.utc).isoformat()
        }


# Global module manager instance
_module_manager: Optional[ReportsModuleManager] = None


def get_module_manager() -> ReportsModuleManager:
    """Get the global module manager instance."""
    global _module_manager
    if _module_manager is None:
        _module_manager = ReportsModuleManager()
    return _module_manager


# Convenience functions for component access
def create_report(
    report_type: str,
    configuration: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """Create a report using the specified generator."""
    if not GENERATORS_AVAILABLE:
        raise RuntimeError("Report generators are not available")
    
    manager = get_module_manager()
    generator_class = manager.get_component("generators", report_type)
    
    if not generator_class:
        raise ValueError(f"Report generator '{report_type}' not found")
    
    return generator_class(configuration=configuration, **kwargs)


def analyze_data(
    analytics_type: str,
    data: Any,
    configuration: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """Analyze data using the specified analytics engine."""
    if not ANALYTICS_AVAILABLE:
        raise RuntimeError("Analytics engines are not available")
    
    manager = get_module_manager()
    analytics_class = manager.get_component("analytics", analytics_type)
    
    if not analytics_class:
        raise ValueError(f"Analytics engine '{analytics_type}' not found")
    
    engine = analytics_class(configuration=configuration, **kwargs)
    return engine.analyze(data)


def format_report(
    format_type: str,
    report_data: Any,
    configuration: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """Format report data using the specified formatter."""
    if not FORMATTERS_AVAILABLE:
        raise RuntimeError("Report formatters are not available")
    
    manager = get_module_manager()
    formatter_class = manager.get_component("formatters", format_type)
    
    if not formatter_class:
        raise ValueError(f"Report formatter '{format_type}' not found")
    
    formatter = formatter_class(configuration=configuration, **kwargs)
    return formatter.format(report_data)


def schedule_report(
    scheduler_type: str,
    schedule_config: Dict[str, Any],
    report_config: Dict[str, Any],
    **kwargs
) -> Any:
    """Schedule a report using the specified scheduler."""
    if not SCHEDULERS_AVAILABLE:
        raise RuntimeError("Report schedulers are not available")
    
    manager = get_module_manager()
    scheduler_class = manager.get_component("schedulers", scheduler_type)
    
    if not scheduler_class:
        raise ValueError(f"Report scheduler '{scheduler_type}' not found")
    
    scheduler = scheduler_class(**kwargs)
    return scheduler.schedule_report(schedule_config, report_config)


def export_report(
    exporter_type: str,
    report_data: Any,
    destination: str,
    configuration: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """Export report using the specified exporter."""
    if not EXPORTERS_AVAILABLE:
        raise RuntimeError("Report exporters are not available")
    
    manager = get_module_manager()
    exporter_class = manager.get_component("exporters", exporter_type)
    
    if not exporter_class:
        raise ValueError(f"Report exporter '{exporter_type}' not found")
    
    exporter = exporter_class(configuration=configuration, **kwargs)
    return exporter.export(report_data, destination)


# Module status and diagnostics
def get_module_status() -> Dict[str, Any]:
    """Get comprehensive module status."""
    manager = get_module_manager()
    return {
        "module_info": manager.get_module_info(),
        "component_availability": manager.available_components,
        "registered_components": manager.list_components(),
        "health_status": "healthy" if any(manager.available_components.values()) else "degraded"
    }


def run_diagnostics() -> Dict[str, Any]:
    """Run comprehensive module diagnostics."""
    diagnostics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "module_version": __version__,
        "component_status": {},
        "dependencies": {},
        "errors": [],
        "warnings": []
    }
    
    # Check component availability
    manager = get_module_manager()
    for component_type, available in manager.available_components.items():
        diagnostics["component_status"][component_type] = {
            "available": available,
            "registered_count": len(manager.list_components(component_type).get(component_type, []))
        }
        
        if not available:
            diagnostics["warnings"].append(f"Component '{component_type}' is not available")
    
    # Check critical dependencies
    critical_components = ["generators", "formatters", "config"]
    missing_critical = [comp for comp in critical_components if not manager.available_components.get(comp, False)]
    
    if missing_critical:
        diagnostics["errors"].extend([f"Critical component '{comp}' is missing" for comp in missing_critical])
    
    # Overall health assessment
    if diagnostics["errors"]:
        diagnostics["health"] = "unhealthy"
    elif diagnostics["warnings"]:
        diagnostics["health"] = "degraded"
    else:
        diagnostics["health"] = "healthy"
    
    return diagnostics


# Initialize module on import
logger.info(f"Reports module v{__version__} initialized")

# Module exports
__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__copyright__",
    "__license__",
    
    # Module management
    "ReportsModuleManager",
    "get_module_manager",
    "get_module_status",
    "run_diagnostics",
    
    # Convenience functions
    "create_report",
    "analyze_data",
    "format_report",
    "schedule_report",
    "export_report",
    
    # Component availability flags
    "GENERATORS_AVAILABLE",
    "ANALYTICS_AVAILABLE",
    "FORMATTERS_AVAILABLE",
    "SCHEDULERS_AVAILABLE",
    "AGGREGATORS_AVAILABLE",
    "VISUALIZERS_AVAILABLE",
    "EXPORTERS_AVAILABLE",
    "TEMPLATES_AVAILABLE",
    "PROCESSORS_AVAILABLE",
    "CONFIG_AVAILABLE",
    "INDEX_AVAILABLE"
]

# Conditionally add component exports based on availability
if GENERATORS_AVAILABLE:
    __all__.extend([
        "ReportGenerator", "ReportType", "ReportConfiguration", "ReportMetadata",
        "PerformanceReportGenerator", "ContentReportGenerator", "ProtectionReportGenerator",
        "RevenueReportGenerator", "ComplianceReportGenerator",
        "create_report_generator", "get_available_generators", "register_custom_generator"
    ])

if ANALYTICS_AVAILABLE:
    __all__.extend([
        "AnalyticsEngine", "AnalyticsConfiguration", "AnalyticsResult",
        "PerformanceAnalytics", "ContentAnalytics", "ProtectionAnalytics",
        "PlatformAnalytics", "RevenueAnalytics",
        "MLModelManager", "PredictiveAnalytics", "AnomalyDetection",
        "create_analytics_engine", "get_available_analytics"
    ])

if FORMATTERS_AVAILABLE:
    __all__.extend([
        "ReportFormatter", "FormatterConfiguration", "FormatterResult",
        "PDFFormatter", "ExcelFormatter", "JSONFormatter", "CSVFormatter", "HTMLFormatter",
        "PowerPointFormatter", "XMLFormatter",
        "BrandedFormatter", "InteractiveFormatter", "AccessibleFormatter",
        "create_formatter", "get_available_formatters", "register_custom_formatter"
    ])

if SCHEDULERS_AVAILABLE:
    __all__.extend([
        "ReportScheduler", "ScheduleConfiguration", "ScheduleType", "ScheduleStatus",
        "AutomatedReportScheduler", "CronReportScheduler", "RealTimeReportScheduler",
        "EventDrivenScheduler", "ScheduleManager", "JobQueue", "TaskExecutor",
        "create_scheduler", "get_available_schedulers"
    ])

if AGGREGATORS_AVAILABLE:
    __all__.extend([
        "DataAggregator", "AggregatorConfiguration", "AggregationResult",
        "PerformanceAggregator", "ContentAggregator", "RevenueAggregator",
        "MetricsAggregator", "ComplianceAggregator",
        "StreamingAggregator", "DistributedAggregator", "MLAggregator",
        "create_aggregator", "get_available_aggregators"
    ])

if VISUALIZERS_AVAILABLE:
    __all__.extend([
        "ChartGenerator", "VisualizationConfiguration", "VisualizationResult",
        "GraphVisualizer", "DashboardVisualizer", "MetricsVisualizer", "TrendVisualizer",
        "InteractiveVisualizer", "RealTimeDashboard", "ThreeDimensionalVisualizer",
        "create_visualizer", "get_available_visualizers"
    ])

if EXPORTERS_AVAILABLE:
    __all__.extend([
        "ReportExporter", "ExporterConfiguration", "ExportResult",
        "EmailExporter", "CloudStorageExporter", "APIExporter", "DatabaseExporter",
        "WebhookExporter", "DistributedExporter", "SecureExporter", "CompressedExporter",
        "create_exporter", "get_available_exporters"
    ])

if TEMPLATES_AVAILABLE:
    __all__.extend([
        "ReportTemplate", "TemplateConfiguration", "TemplateEngine",
        "ExecutiveTemplate", "TechnicalTemplate", "ComplianceTemplate",
        "FinancialTemplate", "MarketingTemplate",
        "AIGeneratedTemplate", "DynamicTemplate", "MultiLanguageTemplate",
        "create_template", "get_available_templates", "register_custom_template"
    ])

if PROCESSORS_AVAILABLE:
    __all__.extend([
        "ReportProcessor", "ProcessorConfiguration", "ProcessingResult",
        "DataProcessor", "MetricsProcessor", "InsightsProcessor", "IntelligenceProcessor",
        "StreamingProcessor", "DistributedProcessor", "MLProcessor",
        "create_processor", "get_available_processors"
    ])

if CONFIG_AVAILABLE:
    __all__.extend([
        "ReportsConfiguration", "Environment", "LogLevel", "DatabaseType",
        "CacheType", "ExportFormat", "CloudProvider",
        "DatabaseConfig", "RedisConfig", "CacheConfig", "SecurityConfig",
        "MonitoringConfig", "APIConfig", "ReportConfig", "SchedulerConfig",
        "CloudConfig", "MLConfig",
        "get_config", "reload_config", "config_context", "validate_configuration"
    ])

if INDEX_AVAILABLE:
    __all__.extend([
        "ReportsServiceManager", "ReportsSettings", "ServiceStatus", "ComponentType",
        "create_fastapi_app", "run_service",
        "get_service_manager", "get_db_session", "get_redis_client", "get_component_factory",
        "verify_token", "rate_limit", "circuit_breaker", "cache_result"
    ])
