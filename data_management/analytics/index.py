"""Analytics Index - Unified Analytics System Entry Point
====================================================

Central coordination module for the comprehensive analytics system
providing unified access to all analytics capabilities including
business intelligence, predictive analytics, real-time dashboards,
and advanced metrics aggregation.

Core Features:
- Unified analytics system orchestration
- Centralized configuration and initialization
- Cross-module integration and coordination
- Enterprise-grade system monitoring and health checks
- Performance optimization and resource management
- Automated system scaling and load balancing
- Comprehensive logging and audit trails

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved

Enterprise Warning:
===================
This analytics orchestration system contains proprietary integration frameworks,
system coordination algorithms, and enterprise architecture patterns developed by Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
All system integration patterns and orchestration logic are protected intellectual property.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

from .collectors import BusinessMetricsCollector
from .predictive_analytics import PredictiveAnalyticsEngine, PredictionScheduler
from .realtime_dashboard import RealTimeDashboard
from .business_intelligence import BusinessIntelligenceEngine
from .metrics_aggregator import AdvancedMetricsAggregator
from .processors import MetricsProcessor
from .storage import AnalyticsStorage, MetricsWarehouse
from .exporters import create_exporter, ExportFormat


class SystemStatus(Enum):
    """Analytics system status levels."""    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class ModuleStatus(Enum):
    """Individual module status levels."""    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class AnalyticsConfig:
    """Comprehensive analytics system configuration."""    enable_predictive_analytics: bool = True
    enable_realtime_dashboard: bool = True
    enable_business_intelligence: bool = True
    enable_metrics_aggregation: bool = True
    cache_ttl_seconds: int = 3600
    batch_processing_size: int = 1000
    max_concurrent_jobs: int = 10
    data_retention_days: int = 365
    backup_frequency_hours: int = 24
    monitoring_interval_seconds: int = 60
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'cpu_usage': 80.0,
        'memory_usage': 85.0,
        'disk_usage': 90.0,
        'error_rate': 5.0
    })


@dataclass
class SystemHealth:
    """System health monitoring data."""    overall_status: SystemStatus
    module_statuses: Dict[str, ModuleStatus]
    performance_metrics: Dict[str, float]
    error_counts: Dict[str, int]
    last_updated: datetime
    uptime_seconds: float
    active_connections: int
    processing_queue_size: int


class AnalyticsOrchestrator:
    """    Central orchestrator for the comprehensive analytics system.
    
    Coordinates all analytics modules, manages system health,
    and provides unified access to analytics capabilities.
    """    
    def __init__(self, config: AnalyticsConfig = None):
        self.config = config or AnalyticsConfig()
        self.logger = logging.getLogger(__name__)
        
        # Module instances
        self.metrics_collector = None
        self.predictive_engine = None
        self.dashboard = None
        self.business_intelligence = None
        self.metrics_aggregator = None
        self.metrics_processor = None
        self.analytics_storage = None
        self.metrics_warehouse = None
        
        # System state
        self.system_health = SystemHealth(
            overall_status=SystemStatus.OFFLINE,
            module_statuses={},
            performance_metrics={},
            error_counts={},
            last_updated=datetime.now(),
            uptime_seconds=0,
            active_connections=0,
            processing_queue_size=0
        )
        
        self.start_time = None
        self.monitoring_task = None
        
    async def initialize(self) -> bool:
        """        Initialize the complete analytics system.
        
        Returns:
            Success status
        """        try:
            self.start_time = datetime.now()
            self.logger.info("Initializing comprehensive analytics system...")
            
            # Initialize storage components first
            if self.config.enable_metrics_aggregation:
                self.analytics_storage = AnalyticsStorage()
                self.metrics_warehouse = MetricsWarehouse()
                await self._initialize_module("storage", self.analytics_storage.initialize)
            
            # Initialize core metrics collection
            self.metrics_collector = BusinessMetricsCollector()
            await self._initialize_module("metrics_collector", self.metrics_collector.initialize)
            
            # Initialize metrics processing
            self.metrics_processor = MetricsProcessor()
            await self._initialize_module("metrics_processor", self.metrics_processor.initialize)
            
            # Initialize advanced metrics aggregation
            if self.config.enable_metrics_aggregation:
                self.metrics_aggregator = AdvancedMetricsAggregator()
                await self._initialize_module("metrics_aggregator", self.metrics_aggregator.initialize)
            
            # Initialize predictive analytics
            if self.config.enable_predictive_analytics:
                self.predictive_engine = PredictiveAnalyticsEngine()
                await self._initialize_module("predictive_analytics", self.predictive_engine.initialize)
            
            # Initialize real-time dashboard
            if self.config.enable_realtime_dashboard:
                self.dashboard = RealTimeDashboard()
                await self._initialize_module("realtime_dashboard", self.dashboard.initialize)
            
            # Initialize business intelligence
            if self.config.enable_business_intelligence:
                self.business_intelligence = BusinessIntelligenceEngine()
                await self._initialize_module("business_intelligence", self.business_intelligence.initialize)
            
            # Start system monitoring
            await self._start_monitoring()
            
            self.system_health.overall_status = SystemStatus.HEALTHY
            self.logger.info("Analytics system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Analytics system initialization failed: {e}")
            self.system_health.overall_status = SystemStatus.CRITICAL
            return False
    
    async def shutdown(self):
        """Gracefully shutdown the analytics system."""        try:
            self.logger.info("Shutting down analytics system...")
            
            # Stop monitoring
            if self.monitoring_task:
                self.monitoring_task.cancel()
            
            # Shutdown modules
            modules = [
                ("business_intelligence", self.business_intelligence),
                ("realtime_dashboard", self.dashboard),
                ("predictive_analytics", self.predictive_engine),
                ("metrics_aggregator", self.metrics_aggregator),
                ("metrics_processor", self.metrics_processor),
                ("metrics_collector", self.metrics_collector),
                ("storage", self.analytics_storage)
            ]
            
            for module_name, module in modules:
                if module and hasattr(module, 'shutdown'):
                    try:
                        await module.shutdown()
                        self.system_health.module_statuses[module_name] = ModuleStatus.INACTIVE
                    except Exception as e:
                        self.logger.error(f"Error shutting down {module_name}: {e}")
            
            self.system_health.overall_status = SystemStatus.OFFLINE
            self.logger.info("Analytics system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Analytics system shutdown failed: {e}")
    
    async def get_comprehensive_analytics(
        self,
        time_range: Dict[str, datetime],
        analysis_type: str = "complete",
        include_predictions: bool = True,
        include_intelligence: bool = True
    ) -> Dict[str, Any]:
        """        Get comprehensive analytics across all modules.
        
        Args:
            time_range: Time range for analysis
            analysis_type: Type of analysis to perform
            include_predictions: Include predictive analytics
            include_intelligence: Include business intelligence
            
        Returns:
            Comprehensive analytics results
        """        try:
            analytics_results = {
                'timestamp': datetime.now().isoformat(),
                'time_range': {
                    'start': time_range.get('start').isoformat() if time_range.get('start') else None,
                    'end': time_range.get('end').isoformat() if time_range.get('end') else None
                },
                'analysis_type': analysis_type
            }
            
            # Collect business metrics
            if self.metrics_collector:
                business_metrics = await self.metrics_collector.collect_all_metrics(
                    time_range.get('start'),
                    time_range.get('end')
                )
                analytics_results['business_metrics'] = business_metrics
            
            # Aggregate key metrics
            if self.metrics_aggregator:
                key_metrics = [
                    'daily_active_users',
                    'revenue_per_day',
                    'content_uploads_daily'
                ]
                aggregated_metrics = await self.metrics_aggregator.aggregate_metrics(
                    key_metrics,
                    time_range
                )
                analytics_results['aggregated_metrics'] = [
                    metric.__dict__ for metric in aggregated_metrics
                ]
            
            # Include predictive analytics
            if include_predictions and self.predictive_engine:
                # Content performance prediction
                sample_content = {
                    'type': 'audio',
                    'duration': 180,
                    'quality_score': 0.85,
                    'tags': ['music', 'original'],
                    'upload_hour': 14
                }
                content_prediction = await self.predictive_engine.predict_content_performance(
                    sample_content
                )
                analytics_results['predictions'] = {
                    'content_performance': content_prediction.__dict__
                }
            
            # Include business intelligence
            if include_intelligence and self.business_intelligence:
                from .business_intelligence import IntelligenceType, AnalysisDepth
                
                strategic_report = await self.business_intelligence.generate_strategic_report(
                    IntelligenceType.STRATEGIC_OVERVIEW,
                    AnalysisDepth.EXECUTIVE_SUMMARY,
                    time_range
                )
                analytics_results['business_intelligence'] = {
                    'strategic_report': strategic_report.__dict__
                }
            
            # System health
            analytics_results['system_health'] = self.system_health.__dict__
            
            return analytics_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive analytics failed: {e}")
            raise
    
    async def create_executive_dashboard(
        self,
        dashboard_name: str,
        owner_id: str,
        custom_widgets: List[Dict[str, Any]] = None
    ) -> str:
        """        Create an executive dashboard with comprehensive analytics.
        
        Args:
            dashboard_name: Name for the dashboard
            owner_id: Owner user ID
            custom_widgets: Custom widget configurations
            
        Returns:
            Dashboard ID
        """        try:
            if not self.dashboard:
                raise RuntimeError("Real-time dashboard not initialized")
            
            from .realtime_dashboard import DashboardType
            
            # Create dashboard
            dashboard_id = await self.dashboard.create_dashboard(
                dashboard_name,
                DashboardType.EXECUTIVE,
                owner_id,
                custom_widgets
            )
            
            self.logger.info(f"Executive dashboard created: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            self.logger.error(f"Executive dashboard creation failed: {e}")
            raise
    
    async def generate_executive_report(
        self,
        report_period: Dict[str, datetime],
        stakeholders: List[str] = None,
        export_format: ExportFormat = ExportFormat.PDF
    ) -> str:
        """        Generate comprehensive executive report.
        
        Args:
            report_period: Period for the report
            stakeholders: Target stakeholders
            export_format: Export format for the report
            
        Returns:
            Report file path or URL
        """        try:
            # Get comprehensive analytics
            analytics_data = await self.get_comprehensive_analytics(
                report_period,
                analysis_type="executive",
                include_predictions=True,
                include_intelligence=True
            )
            
            # Create exporter
            exporter = create_exporter(export_format)
            
            # Export report
            report_path = await exporter.export_executive_report(
                analytics_data,
                f"Executive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            self.logger.info(f"Executive report generated: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Executive report generation failed: {e}")
            raise
    
    async def get_system_health(self) -> SystemHealth:
        """        Get current system health status.
        
        Returns:
            Current system health information
        """        await self._update_system_health()
        return self.system_health
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """        Optimize system performance across all modules.
        
        Returns:
            Optimization results and recommendations
        """        try:
            optimization_results = {
                'timestamp': datetime.now().isoformat(),
                'optimizations_applied': [],
                'recommendations': []
            }
            
            # Optimize metrics aggregation
            if self.metrics_aggregator:
                key_metrics = list(self.metrics_aggregator.metric_definitions.keys())
                if key_metrics:
                    agg_optimization = await self.metrics_aggregator.optimize_aggregation_performance(
                        key_metrics[:5]  # Optimize top 5 metrics
                    )
                    optimization_results['aggregation_optimization'] = agg_optimization
                    optimization_results['optimizations_applied'].append('metrics_aggregation')
            
            # Performance recommendations
            recommendations = await self._generate_performance_recommendations()
            optimization_results['recommendations'].extend(recommendations)
            
            self.logger.info("Performance optimization completed")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            raise
    
    # Private helper methods
    
    async def _initialize_module(self, module_name: str, init_func: callable):
        """Initialize an individual module."""        try:
            self.system_health.module_statuses[module_name] = ModuleStatus.INITIALIZING
            
            if asyncio.iscoroutinefunction(init_func):
                await init_func()
            else:
                init_func()
            
            self.system_health.module_statuses[module_name] = ModuleStatus.ACTIVE
            self.logger.info(f"Module {module_name} initialized successfully")
            
        except Exception as e:
            self.system_health.module_statuses[module_name] = ModuleStatus.ERROR
            self.logger.error(f"Module {module_name} initialization failed: {e}")
            raise
    
    async def _start_monitoring(self):
        """Start system health monitoring."""        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop."""        while True:
            try:
                await self._update_system_health()
                await asyncio.sleep(self.config.monitoring_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _update_system_health(self):
        """Update system health metrics."""        try:
            # Update uptime
            if self.start_time:
                self.system_health.uptime_seconds = (
                    datetime.now() - self.start_time
                ).total_seconds()
            
            # Update performance metrics
            self.system_health.performance_metrics.update({
                'cpu_usage': await self._get_cpu_usage(),
                'memory_usage': await self._get_memory_usage(),
                'disk_usage': await self._get_disk_usage(),
                'active_modules': len([
                    status for status in self.system_health.module_statuses.values()
                    if status == ModuleStatus.ACTIVE
                ])
            })
            
            # Check overall health
            if self._is_system_healthy():
                if self.system_health.overall_status == SystemStatus.CRITICAL:
                    self.system_health.overall_status = SystemStatus.DEGRADED
                elif self.system_health.overall_status == SystemStatus.DEGRADED:
                    self.system_health.overall_status = SystemStatus.HEALTHY
            else:
                if any(status == ModuleStatus.ERROR for status in self.system_health.module_statuses.values()):
                    self.system_health.overall_status = SystemStatus.CRITICAL
                else:
                    self.system_health.overall_status = SystemStatus.DEGRADED
            
            self.system_health.last_updated = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Health update failed: {e}")
    
    def _is_system_healthy(self) -> bool:
        """Check if system is healthy based on thresholds."""        metrics = self.system_health.performance_metrics
        thresholds = self.config.alert_thresholds
        
        for metric, threshold in thresholds.items():
            if metric in metrics and metrics[metric] > threshold:
                return False
        
        return True
    
    async def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""        # Placeholder implementation
        import psutil
        return psutil.cpu_percent(interval=1)
    
    async def _get_memory_usage(self) -> float:
        """Get current memory usage percentage."""        # Placeholder implementation
        import psutil
        return psutil.virtual_memory().percent
    
    async def _get_disk_usage(self) -> float:
        """Get current disk usage percentage."""        # Placeholder implementation
        import psutil
        return psutil.disk_usage('/').percent
    
    async def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""        recommendations = []
        
        metrics = self.system_health.performance_metrics
        
        if metrics.get('cpu_usage', 0) > 70:
            recommendations.append("Consider scaling compute resources or optimizing CPU-intensive operations")
        
        if metrics.get('memory_usage', 0) > 80:
            recommendations.append("Increase memory allocation or optimize memory usage patterns")
        
        if metrics.get('disk_usage', 0) > 85:
            recommendations.append("Archive old data or expand storage capacity")
        
        if self.system_health.processing_queue_size > 1000:
            recommendations.append("Increase parallel processing capacity or optimize queue management")
        
        return recommendations


# Convenience functions for common operations

async def create_analytics_system(
    config: AnalyticsConfig = None
) -> AnalyticsOrchestrator:
    """    Create and initialize a complete analytics system.
    
    Args:
        config: System configuration
        
    Returns:
        Initialized analytics orchestrator
    """    orchestrator = AnalyticsOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator


async def get_quick_analytics(
    time_range: Dict[str, datetime],
    metrics: List[str] = None
) -> Dict[str, Any]:
    """    Get quick analytics without full system initialization.
    
    Args:
        time_range: Time range for analysis
        metrics: Specific metrics to retrieve
        
    Returns:
        Quick analytics results
    """    try:
        # Initialize minimal components
        collector = BusinessMetricsCollector()
        
        # Collect basic metrics
        results = await collector.collect_all_metrics(
            time_range.get('start'),
            time_range.get('end')
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'time_range': time_range,
            'metrics': results
        }
        
    except Exception as e:
        logging.error(f"Quick analytics failed: {e}")
        raise


# Global analytics orchestrator instance
_global_orchestrator: Optional[AnalyticsOrchestrator] = None


async def get_global_analytics() -> AnalyticsOrchestrator:
    """Get or create global analytics orchestrator instance."""    global _global_orchestrator
    
    if not _global_orchestrator:
        _global_orchestrator = await create_analytics_system()
    
    return _global_orchestrator
