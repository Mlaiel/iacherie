"""
Observability Module Index - Central Access Point

Provides centralized access to all observability components with
easy initialization, configuration, and management capabilities
for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Import all observability components
from . import (
    # Analytics
    RealTimeAnalytics,
    HistoricalAnalytics,
    ContentPerformanceAnalyzer,
    UserBehaviorAnalytics,
    ROIOptimizer,
    AdvancedAnalyticsManager,
    
    # Business Process Monitoring (New)
    ContentProcessingMonitor,
    CollaborationMonitor,
    MonetizationMonitor,
    BusinessProcessOrchestrator,
    ContentType,
    CreatorType,
    ProcessStage,
    ProcessStatus,
    DistributionPlatform,
    
    # Reporting
    ReportGenerator,
    AutomatedReportingEngine,
    VisualizationEngine,
    
    # Monitoring
    IntelligentMonitoringSystem,
    AnomalyDetector,
    PredictiveEngine,
    IncidentManager,
    
    # Core Components
    SystemMonitor,
    MetricsCollector,
    HealthMonitor,
    AlertManager,
    AIObservabilityManager,
    
    # Data Structures
    MonitoringMetric,
    PredictiveAlert,
    BusinessInsight,
    KPI,
    ReportTemplate,
    
    # Enums
    AlertSeverity,
    ReportType,
    MonitoringScope,
    PredictionType
)


class ObservabilityIndex:
    """Central index and factory for all observability components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or self._get_default_config()
        self.components = {}
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize all observability components"""



        try:
            self.logger.info("Initializing Observability Suite...")
            
            # Initialize core monitoring
            await self._initialize_monitoring()
            
            # Initialize analytics
            await self._initialize_analytics()
            
            # Initialize business process monitoring (New)
            await self._initialize_business_monitoring()
            
            # Initialize reporting
            await self._initialize_reporting()
            
            # Initialize AI observability
            await self._initialize_ai_observability()
            
            self._initialized = True
            self.logger.info("Observability Suite initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Observability initialization failed: {str(e)}")
            return False
    
    async def _initialize_monitoring(self):
        """Initialize monitoring components"""



        try:
            # Core monitoring system
            self.components['monitoring_system'] = IntelligentMonitoringSystem()
            
            # System monitor
            self.components['system_monitor'] = SystemMonitor()
            
            # Metrics collector
            self.components['metrics_collector'] = MetricsCollector()
            
            # Health monitor
            self.components['health_monitor'] = HealthMonitor()
            
            # Alert manager
            self.components['alert_manager'] = AlertManager()
            
            self.logger.info("Monitoring components initialized")
            
        except Exception as e:
            self.logger.error(f"Monitoring initialization failed: {str(e)}")
            raise
    
    async def _initialize_analytics(self):
        """Initialize analytics components"""



        try:
            # Advanced analytics manager
            self.components['analytics_manager'] = AdvancedAnalyticsManager()
            
            # Specialized analyzers
            self.components['content_analyzer'] = ContentPerformanceAnalyzer()
            self.components['user_analytics'] = UserBehaviorAnalytics()
            self.components['roi_optimizer'] = ROIOptimizer()
            
            # Real-time analytics
            self.components['realtime_analytics'] = RealTimeAnalytics()
            
            # Historical analytics
            self.components['historical_analytics'] = HistoricalAnalytics()
            
            self.logger.info("Analytics components initialized")
            
        except Exception as e:
            self.logger.error(f"Analytics initialization failed: {str(e)}")
            raise
    
    async def _initialize_business_monitoring(self):
        """Initialize business process monitoring components"""



        try:
            # Business process orchestrator
            business_config = self.config.get('business_monitoring', {})
            self.components['business_orchestrator'] = BusinessProcessOrchestrator(business_config)
            
            # Individual monitors (available through orchestrator)
            self.components['content_monitor'] = self.components['business_orchestrator'].content_monitor
            self.components['collaboration_monitor'] = self.components['business_orchestrator'].collaboration_monitor
            self.components['monetization_monitor'] = self.components['business_orchestrator'].monetization_monitor
            
            # Start monitoring processes
            await self.components['business_orchestrator'].start_monitoring()
            
            self.logger.info("Business process monitoring components initialized")
            
        except Exception as e:
            self.logger.error(f"Business monitoring initialization failed: {str(e)}")
            raise
    
    async def _initialize_reporting(self):
        """Initialize reporting components"""



        try:
            # Report generator
            self.components['report_generator'] = ReportGenerator()
            
            # Automated reporting
            self.components['automated_reporting'] = AutomatedReportingEngine()
            
            # Visualization engine
            self.components['visualization_engine'] = VisualizationEngine()
            
            self.logger.info("Reporting components initialized")
            
        except Exception as e:
            self.logger.error(f"Reporting initialization failed: {str(e)}")
            raise
    
    async def _initialize_ai_observability(self):
        """Initialize AI observability components"""



        try:
            # AI observability manager
            self.components['ai_observability'] = AIObservabilityManager()
            
            self.logger.info("AI observability components initialized")
            
        except Exception as e:
            self.logger.error(f"AI observability initialization failed: {str(e)}")
            raise
    
        return self.components.get(component_name)
    
    # Business Process Monitoring Access Methods
    def get_business_orchestrator(self) -> Optional[BusinessProcessOrchestrator]:
        """Get business process orchestrator"""



        return self.get_component('business_orchestrator')
    
    def get_content_monitor(self) -> Optional[ContentProcessingMonitor]:
        """Get content processing monitor"""



        return self.get_component('content_monitor')
    
    def get_collaboration_monitor(self) -> Optional[CollaborationMonitor]:
        """Get collaboration monitor"""



        return self.get_component('collaboration_monitor')
    
    def get_monetization_monitor(self) -> Optional[MonetizationMonitor]:
        """Get monetization monitor"""



        return self.get_component('monetization_monitor')
    
    async def track_content_processing(self, **kwargs) -> None:
        """Track content processing through the pipeline"""
        content_monitor = self.get_content_monitor()
        if content_monitor:
            await content_monitor.track_content_processing(**kwargs)
    
    async def track_collaboration_match(self, **kwargs) -> None:
        """Track collaboration matching"""
        collaboration_monitor = self.get_collaboration_monitor()
        if collaboration_monitor:
            await collaboration_monitor.track_collaboration_match(**kwargs)
    
    async def track_revenue_event(self, **kwargs) -> None:
        """Track revenue generation event"""
        monetization_monitor = self.get_monetization_monitor()
        if monetization_monitor:
            await monetization_monitor.track_revenue_event(**kwargs)
    
    async def get_business_intelligence_report(self) -> Dict[str, Any]:
        """Get comprehensive business intelligence report"""
        business_orchestrator = self.get_business_orchestrator()
        if business_orchestrator:
            return await business_orchestrator.get_comprehensive_business_report()
        return {}
    
    # Existing component access methods
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a specific component by name"""
        if not self._initialized:
            self.logger.warning("Observability suite not initialized")
            return None
        
        return self.components.get(component_name)
    
    def get_monitoring_system(self) -> Optional[IntelligentMonitoringSystem]:
        """Get the intelligent monitoring system"""



        return self.get_component('monitoring_system')
    
    def get_analytics_manager(self) -> Optional[AdvancedAnalyticsManager]:
        """Get the advanced analytics manager"""



        return self.get_component('analytics_manager')
    
    def get_report_generator(self) -> Optional[ReportGenerator]:
        """Get the report generator"""



        return self.get_component('report_generator')
    
    def get_content_analyzer(self) -> Optional[ContentPerformanceAnalyzer]:
        """Get the content performance analyzer"""



        return self.get_component('content_analyzer')
    
    def get_user_analytics(self) -> Optional[UserBehaviorAnalytics]:
        """Get the user behavior analytics"""



        return self.get_component('user_analytics')
    
    def get_roi_optimizer(self) -> Optional[ROIOptimizer]:
        """Get the ROI optimizer"""



        return self.get_component('roi_optimizer')
    
    async def generate_executive_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive dashboard with all key metrics"""



        try:
            if not self._initialized:
                await self.initialize()
            
            dashboard_data = {
                "generated_at": datetime.utcnow().isoformat(),
                "sections": {}
            }
            
            # System health section
            monitoring_system = self.get_monitoring_system()
            if monitoring_system:
                system_status = await monitoring_system.get_system_status()
                dashboard_data["sections"]["system_health"] = system_status
            
            # Analytics section
            analytics_manager = self.get_analytics_manager()
            if analytics_manager:
                analytics_report = await analytics_manager.generate_comprehensive_report(data)
                dashboard_data["sections"]["analytics"] = analytics_report
            
            # Visualization section
            viz_engine = self.get_component('visualization_engine')
            if viz_engine:
                executive_viz = await viz_engine.create_executive_dashboard(data)
                dashboard_data["sections"]["visualizations"] = executive_viz
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Executive dashboard generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def run_comprehensive_analysis(self, analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive analysis across all components"""



        try:
            if not self._initialized:
                await self.initialize()
            
            analysis_results = {
                "analysis_id": analysis_request.get("analysis_id", "comprehensive_analysis"),
                "timestamp": datetime.utcnow().isoformat(),
                "results": {}
            }
            
            # Content performance analysis
            if "content_data" in analysis_request:
                content_analyzer = self.get_content_analyzer()
                if content_analyzer:
                    content_analysis = await content_analyzer.analyze_content_performance(
                        analysis_request["content_data"]
                    )
                    analysis_results["results"]["content_performance"] = content_analysis
            
            # User behavior analysis
            if "user_data" in analysis_request:
                user_analytics = self.get_user_analytics()
                if user_analytics:
                    user_analysis = await user_analytics.analyze_user_behavior(
                        analysis_request["user_data"]
                    )
                    analysis_results["results"]["user_behavior"] = user_analysis
            
            # ROI analysis
            if "financial_data" in analysis_request:
                roi_optimizer = self.get_roi_optimizer()
                if roi_optimizer:
                    roi_analysis = await roi_optimizer.analyze_roi_performance(
                        analysis_request["financial_data"]
                    )
                    analysis_results["results"]["roi_analysis"] = roi_analysis
            
            # Anomaly detection
            monitoring_system = self.get_monitoring_system()
            if monitoring_system:
                manual_analysis = await monitoring_system.run_manual_analysis("anomaly_detection")
                analysis_results["results"]["anomaly_detection"] = manual_analysis
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def generate_automated_report(self, report_config: Dict[str, Any]) -> str:
        """Generate and schedule an automated report"""



        try:
            if not self._initialized:
                await self.initialize()
            
            automated_reporting = self.get_component('automated_reporting')
            if not automated_reporting:
                return ""
            
            report_id = automated_reporting.schedule_report(report_config)
            
            self.logger.info(f"Automated report scheduled: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Automated report scheduling failed: {str(e)}")
            return ""
    
    def get_available_components(self) -> List[str]:
        """Get list of available component names"""



        return list(self.components.keys())
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive system capabilities"""



        return {
            "observability_suite_version": "3.0.0",
            "initialized": self._initialized,
            "available_components": self.get_available_components(),
            "capabilities": {
                "real_time_monitoring": True,
                "predictive_analytics": True,
                "anomaly_detection": True,
                "automated_reporting": True,
                "business_intelligence": True,
                "ai_model_observability": True,
                "content_performance_analysis": True,
                "user_behavior_analytics": True,
                "roi_optimization": True,
                "incident_management": True,
                "compliance_monitoring": True,
                "multi_dimensional_visualization": True
            },
            "supported_data_sources": [
                "application_metrics",
                "system_metrics", 
                "user_behavior_data",
                "content_performance_data",
                "financial_data",
                "ai_model_metrics",
                "security_events",
                "business_events"
            ],
            "output_formats": [
                "json",
                "pdf_reports",
                "html_dashboards",
                "excel_spreadsheets",
                "csv_exports",
                "real_time_streams"
            ],
            "business_logic_alignment": {
                "content_creator_workflow": "Monitoring upload → AI processing → protection analysis → performance tracking",
                "user_engagement_flow": "Behavior tracking → analytics → personalization → retention optimization",
                "monetization_tracking": "Revenue analysis → ROI optimization → forecasting → strategic planning",
                "collaboration_matching": "Performance correlation → recommendation engine → success tracking"
            }
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""



        return {
            "monitoring": {
                "enable_real_time": True,
                "enable_predictive": True,
                "enable_anomaly_detection": True,
                "alert_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90,
                    "response_time": 1000,
                    "error_rate": 5
                }
            },
            "analytics": {
                "enable_content_analysis": True,
                "enable_user_behavior": True,
                "enable_roi_optimization": True,
                "analysis_intervals": {
                    "real_time": 60,  # seconds
                    "batch": 3600,    # 1 hour
                    "reporting": 86400 # 1 day
                }
            },
            "reporting": {
                "enable_automated": True,
                "default_format": "pdf",
                "distribution": {
                    "email_enabled": True,
                    "dashboard_updates": True,
                    "api_webhooks": True
                }
            },
            "storage": {
                "metric_retention_days": 365,
                "alert_retention_days": 90,
                "report_retention_days": 1095  # 3 years
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown all components"""



        try:
            self.logger.info("Shutting down Observability Suite...")
            
            # Stop monitoring system
            monitoring_system = self.get_monitoring_system()
            if monitoring_system:
                monitoring_system.stop_monitoring()
            
            # Stop analytics manager
            analytics_manager = self.get_analytics_manager()
            if analytics_manager:
                analytics_manager.stop_processing()
            
            # Stop automated reporting
            automated_reporting = self.get_component('automated_reporting')
            if automated_reporting:
                automated_reporting.stop_automated_reporting()
            
            self.components.clear()
            self._initialized = False
            
            self.logger.info("Observability Suite shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {str(e)}")


# Global observability index instance
_observability_index = None

def get_observability_index(config: Optional[Dict[str, Any]] = None) -> ObservabilityIndex:
    """Get global observability index instance"""
    global _observability_index
    
    if _observability_index is None:
        _observability_index = ObservabilityIndex(config)
    
    return _observability_index

async def initialize_observability(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize the global observability suite"""
    index = get_observability_index(config)
    return await index.initialize()

async def generate_executive_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate executive summary using the observability suite"""
    index = get_observability_index()
    return await index.generate_executive_dashboard(data)

async def run_system_analysis(analysis_request: Dict[str, Any]) -> Dict[str, Any]:
    """Run system-wide analysis"""
    index = get_observability_index()
    return await index.run_comprehensive_analysis(analysis_request)

def get_system_capabilities() -> Dict[str, Any]:
    """Get system capabilities"""
    index = get_observability_index()
    return index.get_system_capabilities()

# Export key functions and classes
__all__ = [
    'ObservabilityIndex',
    'get_observability_index',
    'initialize_observability', 
    'generate_executive_summary',
    'run_system_analysis',
    'get_system_capabilities'
]

from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
import logging

from .ai_observability import (
    AIObservabilityManager, AIModelMonitor, AgentPerformanceTracker,
    WorkflowAnalytics, MLPipelineMonitor, ContentProtectionMonitor
)

from .monitoring import (
    SystemMonitor, PerformanceMonitor, ResourceMonitor
)

from .observability_logging import (
    StructuredLogger, SecurityLogger,
    AuditLogger, ComplianceLogger
)

from .tracing import (
    DistributedTracer, PerformanceTracer, AIOperationTracer
)

from .metrics import (
    MetricsCollector, BusinessMetrics, TechnicalMetrics,
    MetricsAggregator, MetricsAnalyzer, CustomMetrics
)

from .analytics import (
    RealTimeAnalytics, HistoricalAnalytics, PredictiveAnalytics,
    ContentAnalytics, UserAnalytics, PerformanceAnalytics
)

from .alerting import (
    AlertManager, AlertEvaluator, AlertRule,
    IntelligentAlerting, StandardAlertRules
)

from .dashboards import (
    DashboardManager, ExecutiveDashboard, TechnicalDashboard,
    CreatorDashboard, SecurityDashboard, BusinessIntelligenceDashboard
)

from .health import (
    HealthChecker, SystemHealthMonitor, ServiceHealthChecker,
    AIModelHealthChecker, DatabaseHealthChecker, NetworkHealthChecker
)

from .diagnostics import (
    DiagnosticsEngine, SystemDiagnostics, AIModelDiagnostics,
    PerformanceDiagnostics, SecurityDiagnostics, TroubleshootingAssistant
)

from .quality import (
    DataQualityValidator, MetricsQualityChecker, LogQualityValidator,
    TraceQualityValidator, ComplianceValidator, DataGovernance
)

from .data_management import (
    ObservabilityDataManager, DataLifecycleManager, DataRetentionManager,
    DataArchiver, DataPurger, ComplianceDataManager
)

from .visualization import (
    VisualizationEngine, ChartGenerator, DashboardRenderer,
    RealtimeVisualizer, BusinessVisualization, TechnicalVisualization
)

logger = logging.getLogger(__name__)


@dataclass
class ObservabilityConfiguration:
    """Configuration for observability system"""
    environment: str = "production"
    monitoring_level: str = "detailed"
    business_context: str = "ia_influencer_platform"
    enable_real_time: bool = True
    enable_predictive: bool = True
    retention_days: int = 90
    compliance_mode: bool = True
    security_level: str = "high"


class ObservabilityIndex:
    """
    Central index for all observability components providing unified access
    to monitoring, logging, tracing, analytics, and visualization services.
    """
    
    def __init__(self, config: Optional[ObservabilityConfiguration] = None):
        self.config = config or ObservabilityConfiguration()
        self._components = {}
        self._initialized = False
        
        logger.info(f"Initializing ObservabilityIndex with config: {self.config}")
    
    async def initialize(self) -> None:
        """Initialize all observability components"""
        if self._initialized:
            return
            
        try:
            # Initialize core monitoring
            self._components['monitoring'] = {
                'system': SystemMonitor(),
                'performance': PerformanceMonitor(),
                'resource': ResourceMonitor(),
                'ai_model': CoreAIMonitor(),
                'agent': AgentMonitor(),
                'workflow': WorkflowMonitor()
            }
            
            # Initialize AI-specific observability
            self._components['ai_observability'] = AIObservabilityManager(
                config=self.config
            )
            
            # Initialize logging infrastructure
            self._components['logging'] = {
                'structured': StructuredLogger(),
                'aggregator': LogAggregator(),
                'security': SecurityLogger(),
                'business': BusinessEventLogger(),
                'audit': AuditTrailLogger(),
                'compliance': ComplianceLogger()
            }
            
            # Initialize tracing system
            self._components['tracing'] = {
                'distributed': DistributedTracer(),
                'request': RequestTracer(),
                'workflow': WorkflowTracer(),
                'ai_processing': AIProcessingTracer(),
                'cross_service': CrossServiceTracer(),
                'performance': PerformanceTracer()
            }
            
            # Initialize metrics collection
            self._components['metrics'] = {
                'collector': MetricsCollector(),
                'business': BusinessMetrics(),
                'technical': TechnicalMetrics(),
                'ai': AIMetrics(),
                'security': SecurityMetrics(),
                'revenue': RevenueMetrics()
            }
            
            # Initialize analytics engines
            self._components['analytics'] = {
                'business': BusinessAnalytics(),
                'predictive': PredictiveAnalytics(),
                'anomaly': AnomalyDetector(),
                'creator': CreatorAnalytics(),
                'engagement': EngagementAnalytics(),
                'revenue': RevenueAnalytics()
            }
            
            # Initialize alerting system
            self._components['alerting'] = {
                'manager': AlertManager(),
                'threshold': ThresholdMonitor(),
                'security': SecurityAlerts(),
                'business_kpi': BusinessKPIAlerts(),
                'escalation': EscalationManager(),
                'notifications': NotificationHub()
            }
            
            # Initialize dashboards
            self._components['dashboards'] = {
                'manager': DashboardManager(),
                'executive': ExecutiveDashboard(),
                'technical': TechnicalDashboard(),
                'creator': CreatorDashboard(),
                'security': SecurityDashboard(),
                'business_intelligence': BusinessIntelligenceDashboard()
            }
            
            # Initialize health monitoring
            self._components['health'] = {
                'checker': HealthChecker(),
                'system': SystemHealthMonitor(),
                'service': ServiceHealthChecker(),
                'ai_model': AIModelHealthChecker(),
                'database': DatabaseHealthChecker(),
                'network': NetworkHealthChecker()
            }
            
            # Initialize diagnostics
            self._components['diagnostics'] = {
                'engine': DiagnosticsEngine(),
                'system': SystemDiagnostics(),
                'ai_model': AIModelDiagnostics(),
                'performance': PerformanceDiagnostics(),
                'security': SecurityDiagnostics(),
                'troubleshooting': TroubleshootingAssistant()
            }
            
            # Initialize quality assurance
            self._components['quality'] = {
                'data_validator': DataQualityValidator(),
                'metrics_checker': MetricsQualityChecker(),
                'log_validator': LogQualityValidator(),
                'trace_validator': TraceQualityValidator(),
                'compliance': ComplianceValidator(),
                'governance': DataGovernance()
            }
            
            # Initialize data management
            self._components['data_management'] = {
                'manager': ObservabilityDataManager(),
                'lifecycle': DataLifecycleManager(),
                'retention': DataRetentionManager(),
                'archiver': DataArchiver(),
                'purger': DataPurger(),
                'compliance': ComplianceDataManager()
            }
            
            # Initialize visualization
            self._components['visualization'] = {
                'engine': VisualizationEngine(),
                'chart_generator': ChartGenerator(),
                'dashboard_renderer': DashboardRenderer(),
                'realtime': RealtimeVisualizer(),
                'business': BusinessVisualization(),
                'technical': TechnicalVisualization()
            }
            
            # Start all components
            await self._start_components()
            
            self._initialized = True
            logger.info("ObservabilityIndex successfully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ObservabilityIndex: {e}")
            raise
    
    async def _start_components(self) -> None:
        """Start all initialized components"""
        for category, components in self._components.items():
            logger.debug(f"Starting {category} components")
            
            for name, component in components.items():
                try:
                    if hasattr(component, 'start'):
                        await component.start()
                    elif hasattr(component, 'initialize'):
                        await component.initialize()
                    
                    logger.debug(f"Started {category}.{name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to start {category}.{name}: {e}")
    
    def get_component(self, category: str, name: str) -> Any:
        """Get a specific component by category and name"""
        if not self._initialized:
            raise RuntimeError("ObservabilityIndex not initialized")
        
        return self._components.get(category, {}).get(name)
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all components in a category"""
        if not self._initialized:
            raise RuntimeError("ObservabilityIndex not initialized")
        
        return self._components.get(category, {})
    
    def list_components(self) -> Dict[str, List[str]]:
        """List all available components by category"""



        return {
            category: list(components.keys())
            for category, components in self._components.items()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        if not self._initialized:
            return {"status": "not_initialized", "components": {}}
        
        health_results = {}
        
        for category, components in self._components.items():
            category_health = {}
            
            for name, component in components.items():
                try:
                    if hasattr(component, 'health_check'):
                        health = await component.health_check()
                        category_health[name] = health
                    else:
                        category_health[name] = {"status": "unknown"}
                        
                except Exception as e:
                    category_health[name] = {
                        "status": "error", 
                        "error": str(e)
                    }
            
            health_results[category] = category_health
        
        overall_status = "healthy"
        for category_health in health_results.values():
            for component_health in category_health.values():
                if component_health.get("status") in ["critical", "error"]:
                    overall_status = "critical"
                    break
                elif component_health.get("status") == "warning":
                    overall_status = "warning"
        
        return {
            "status": overall_status,
            "components": health_results,
            "timestamp": logger.makeRecord(
                "", 0, "", 0, "", (), None
            ).created
        }
    
    async def shutdown(self) -> None:
        """Shutdown all observability components"""
        if not self._initialized:
            return
        
        logger.info("Shutting down ObservabilityIndex")
        
        for category, components in self._components.items():
            for name, component in components.items():
                try:
                    if hasattr(component, 'shutdown'):
                        await component.shutdown()
                    elif hasattr(component, 'stop'):
                        await component.stop()
                    
                    logger.debug(f"Shutdown {category}.{name}")
                    
                except Exception as e:
                    logger.warning(f"Error shutting down {category}.{name}: {e}")
        
        self._initialized = False
        logger.info("ObservabilityIndex shutdown complete")


# Global observability index instance
observability_index = ObservabilityIndex()


# Convenience functions for quick access
async def get_monitoring_component(name: str) -> Any:
    """Get a monitoring component by name"""



    return observability_index.get_component('monitoring', name)


async def get_analytics_component(name: str) -> Any:
    """Get an analytics component by name"""



    return observability_index.get_component('analytics', name)


async def get_dashboard_component(name: str) -> Any:
    """Get a dashboard component by name"""



    return observability_index.get_component('dashboards', name)


async def initialize_observability(
    config: Optional[ObservabilityConfiguration] = None
) -> ObservabilityIndex:
    """Initialize the global observability system"""
    global observability_index
    
    if config:
        observability_index = ObservabilityIndex(config)
    
    await observability_index.initialize()
    return observability_index


async def shutdown_observability() -> None:
    """Shutdown the global observability system"""
    await observability_index.shutdown()


# Export main components for easy access
__all__ = [
    # Main index
    'ObservabilityIndex',
    'ObservabilityConfiguration',
    'observability_index',
    
    # Convenience functions
    'initialize_observability',
    'shutdown_observability',
    'get_monitoring_component',
    'get_analytics_component', 
    'get_dashboard_component',
    
    # Component categories
    'AIObservabilityManager',
    'SystemMonitor',
    'StructuredLogger',
    'DistributedTracer',
    'MetricsCollector',
    'BusinessAnalytics',
    'AlertManager',
    'DashboardManager',
    'HealthChecker',
    'DiagnosticsEngine',
    'DataQualityValidator',
    'ObservabilityDataManager',
    'VisualizationEngine'
]
