"""Analytics Index - Module Entry Point and API Gateway

Industrial-grade analytics module entry point providing unified access to all
analytics capabilities with advanced routing and service orchestration.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & analytics algorithms
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import json

from .engine import AnalyticsEngine, AnalyticsConfig
from .collector import MetricsCollector, BusinessMetricsCollector, MetricPoint, MetricType, MetricScope
from .aggregator import DataAggregator, TimeSeriesAggregator
from .dashboard import AnalyticsDashboard, RealtimeDashboard
from .intelligence import BusinessIntelligence, PredictiveAnalytics
from .reporting import ReportGenerator, PerformanceReporter
from .tracking import UserTracker, ContentTracker, RevenueTracker
from .processor import AnalyticsProcessor, MetricsProcessor
from .exceptions import (
    AnalyticsError, MetricsError, ReportingError, ConfigurationError,
    create_error_response, handle_analytics_exception
)

logger = logging.getLogger(__name__)


class AnalyticsModule:
    """
    Main analytics module class providing unified access to all analytics services.
    
    This class serves as the primary entry point for all analytics operations,
    providing a clean, industrial-grade API for content creator analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core engine
        self.engine = None
        self._initialized = False
        self._services = {}
        
        # Service instances
        self._collectors = {}
        self._aggregators = {}
        self._dashboards = {}
        self._intelligence = {}
        self._reporting = {}
        self._tracking = {}
        self._processors = {}
        
        # Module metadata
        self.version = "2.0.0"
        self.author = "Fahed Mlaiel"
        self.email = "mlaiel@live.de"
        self.copyright = "(c) 2025 Fahed Mlaiel. All rights reserved."
        
        # Performance metrics
        self.module_stats = {
            'initialization_time': None,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'last_activity': None
        }
    
    async def initialize(self) -> None:
        """Initialize the analytics module and all services"""
        try:
            start_time = datetime.now()
            self.logger.info("Initializing Analytics Module...")
            
            # Initialize core engine
            engine_config = AnalyticsConfig(**self.config.get('engine', {}))
            self.engine = AnalyticsEngine(engine_config)
            await self.engine.start()
            
            # Initialize service collections
            await self._initialize_collectors()
            await self._initialize_aggregators()
            await self._initialize_dashboards()
            await self._initialize_intelligence()
            await self._initialize_reporting()
            await self._initialize_tracking()
            await self._initialize_processors()
            
            # Register services
            self._register_services()
            
            # Mark as initialized
            self._initialized = True
            self.module_stats['initialization_time'] = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Analytics Module initialized successfully in {self.module_stats['initialization_time']:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Analytics Module: {str(e)}")
            raise ConfigurationError(f"Module initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the analytics module and all services"""
        try:
            self.logger.info("Shutting down Analytics Module...")
            
            # Shutdown all services
            for service_collection in [
                self._processors, self._tracking, self._reporting,
                self._intelligence, self._dashboards, self._aggregators,
                self._collectors
            ]:
                for service in service_collection.values():
                    if hasattr(service, 'shutdown'):
                        await service.shutdown()
            
            # Shutdown core engine
            if self.engine:
                await self.engine.stop()
            
            self._initialized = False
            self.logger.info("Analytics Module shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down Analytics Module: {str(e)}")
            raise AnalyticsError(f"Module shutdown failed: {str(e)}")
    
    @asynccontextmanager
    async def get_service(self, service_type: str, service_name: str = "default"):
        """Context manager for getting analytics services"""
        if not self._initialized:
            raise AnalyticsError("Analytics module not initialized")
        
        service = self._get_service_instance(service_type, service_name)
        try:
            yield service
        finally:
            # Cleanup if needed
            pass
    
    async def collect_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType,
        scope: MetricScope,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Collect a single metric point"""
        try:
            start_time = datetime.now()
            
            # Get metrics collector
            collector = self._get_service_instance('collector', 'metrics')
            
            # Create metric point
            metric = MetricPoint(
                name=name,
                value=value,
                metric_type=metric_type,
                scope=scope,
                tags=tags or {},
                metadata=metadata or {}
            )
            
            # Collect metric
            await collector.collect_metric(metric)
            
            # Update stats
            await self._update_request_stats(start_time, success=True)
            
            return metric.timestamp.isoformat()
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error collecting metric: {str(e)}")
            raise MetricsError(f"Metric collection failed: {str(e)}")
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get comprehensive real-time metrics"""
        try:
            start_time = datetime.now()
            
            # Get metrics from all services
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'module_info': await self._get_module_info(),
                'engine_metrics': await self.engine.get_realtime_metrics(),
                'user_metrics': await self._tracking['user'].get_realtime_metrics(),
                'content_metrics': await self._tracking['content'].get_realtime_metrics(),
                'revenue_metrics': await self._tracking['revenue'].get_realtime_metrics(),
                'system_metrics': await self._get_system_metrics()
            }
            
            await self._update_request_stats(start_time, success=True)
            return metrics
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error getting realtime metrics: {str(e)}")
            raise AnalyticsError(f"Realtime metrics failed: {str(e)}")
    
    async def generate_report(
        self,
        report_type: str,
        period_days: int = 30,
        format_type: str = "json",
        include_forecasts: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            start_time = datetime.now()
            
            # Get report generator
            generator = self._get_service_instance('reporting', 'generator')
            
            # Generate report
            report = await generator.generate_performance_report(
                period_days=period_days,
                include_forecasts=include_forecasts,
                format_type=format_type
            )
            
            await self._update_request_stats(start_time, success=True)
            return report
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error generating report: {str(e)}")
            raise ReportingError(f"Report generation failed: {str(e)}")
    
    async def track_user_activity(
        self,
        user_id: str,
        activity: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> str:
        """Track user activity"""
        try:
            start_time = datetime.now()
            
            # Get user tracker
            tracker = self._get_service_instance('tracking', 'user')
            
            # Track activity
            event_id = await tracker.track_activity(user_id, activity, session_id)
            
            await self._update_request_stats(start_time, success=True)
            return event_id
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error tracking user activity: {str(e)}")
            raise AnalyticsError(f"User activity tracking failed: {str(e)}")
    
    async def track_content_performance(
        self,
        content_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """Track content performance"""
        try:
            start_time = datetime.now()
            
            # Get content tracker
            tracker = self._get_service_instance('tracking', 'content')
            
            # Track performance
            await tracker.track_performance(content_id, metrics)
            
            await self._update_request_stats(start_time, success=True)
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error tracking content performance: {str(e)}")
            raise AnalyticsError(f"Content performance tracking failed: {str(e)}")
    
    async def track_revenue_event(
        self,
        event_type: str,
        amount: float,
        metadata: Dict[str, Any]
    ) -> str:
        """Track revenue event"""
        try:
            start_time = datetime.now()
            
            # Get revenue tracker
            tracker = self._get_service_instance('tracking', 'revenue')
            
            # Track event
            event_id = await tracker.track_event(event_type, amount, metadata)
            
            await self._update_request_stats(start_time, success=True)
            return event_id
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error tracking revenue event: {str(e)}")
            raise AnalyticsError(f"Revenue event tracking failed: {str(e)}")
    
    async def get_dashboard_data(
        self,
        dashboard_type: str = "analytics",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            start_time = datetime.now()
            
            # Get dashboard
            dashboard = self._get_service_instance('dashboard', dashboard_type)
            
            # Get data
            data = await dashboard.get_data()
            
            await self._update_request_stats(start_time, success=True)
            return data
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            raise AnalyticsError(f"Dashboard data retrieval failed: {str(e)}")
    
    async def generate_business_insights(
        self,
        period: str = "daily",
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate business intelligence insights"""
        try:
            start_time = datetime.now()
            
            # Get business intelligence
            bi = self._get_service_instance('intelligence', 'business')
            
            # Generate insights
            insights = await bi.generate_insights(period)
            
            await self._update_request_stats(start_time, success=True)
            return insights
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error generating business insights: {str(e)}")
            raise AnalyticsError(f"Business insights generation failed: {str(e)}")
    
    async def get_predictive_forecasts(
        self,
        period: str = "daily",
        forecast_horizon: int = 30
    ) -> Dict[str, Any]:
        """Get predictive analytics forecasts"""
        try:
            start_time = datetime.now()
            
            # Get predictive analytics
            predictor = self._get_service_instance('intelligence', 'predictive')
            
            # Generate forecasts
            forecasts = await predictor.generate_forecasts(period)
            
            await self._update_request_stats(start_time, success=True)
            return forecasts
            
        except Exception as e:
            await self._update_request_stats(start_time, success=False)
            self.logger.error(f"Error getting predictive forecasts: {str(e)}")
            raise AnalyticsError(f"Predictive forecasts failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'module_status': 'healthy' if self._initialized else 'not_initialized',
                'version': self.version,
                'services': {},
                'statistics': self.module_stats.copy()
            }
            
            # Check all services
            for service_type, services in self._services.items():
                health_status['services'][service_type] = {}
                for service_name, service in services.items():
                    try:
                        if hasattr(service, 'health_check'):
                            service_health = await service.health_check()
                        else:
                            service_health = {'status': 'healthy', 'details': 'No health check method'}
                        health_status['services'][service_type][service_name] = service_health
                    except Exception as e:
                        health_status['services'][service_type][service_name] = {
                            'status': 'unhealthy',
                            'error': str(e)
                        }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error performing health check: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'module_status': 'error',
                'error': str(e)
            }
    
    # Private Methods
    
    async def _initialize_collectors(self) -> None:
        """Initialize metrics collectors"""
        self._collectors = {
            'metrics': MetricsCollector(self.config.get('collectors', {}).get('metrics', {})),
            'business': BusinessMetricsCollector(self.config.get('collectors', {}).get('business', {}))
        }
        
        for collector in self._collectors.values():
            await collector.initialize()
    
    async def _initialize_aggregators(self) -> None:
        """
Initialize data aggregators"""
        self._aggregators = {
            'data': DataAggregator(self.config.get('aggregators', {}).get('data', {})),
            'timeseries': TimeSeriesAggregator(self.config.get('aggregators', {}).get('timeseries', {}))
        }
        
        for aggregator in self._aggregators.values():
            await aggregator.initialize()
    
    async def _initialize_dashboards(self) -> None:
        """
Initialize dashboards"""
        self._dashboards = {
            'analytics': AnalyticsDashboard(self.config.get('dashboards', {}).get('analytics', {})),
            'realtime': RealtimeDashboard(self.config.get('dashboards', {}).get('realtime', {}))
        }
        
        for dashboard in self._dashboards.values():
            await dashboard.initialize()
    
    async def _initialize_intelligence(self) -> None:
        """
Initialize intelligence services"""
        self._intelligence = {
            'business': BusinessIntelligence(
                self._collectors.get('business'),
                self._aggregators.get('data')
            ),
            'predictive': PredictiveAnalytics()
        }
        
        for intelligence in self._intelligence.values():
            await intelligence.initialize()
    
    async def _initialize_reporting(self) -> None:
        """
Initialize reporting services"""
        self._reporting = {
            'generator': ReportGenerator(self.config.get('reporting', {}).get('generator', {})),
            'performance': PerformanceReporter(self.config.get('reporting', {}).get('performance', {}))
        }
        
        for reporter in self._reporting.values():
            await reporter.initialize()
    
    async def _initialize_tracking(self) -> None:
        """
Initialize tracking services"""
        self._tracking = {
            'user': UserTracker(self.config.get('tracking', {}).get('user', {})),
            'content': ContentTracker(self.config.get('tracking', {}).get('content', {})),
            'revenue': RevenueTracker(self.config.get('tracking', {}).get('revenue', {}))
        }
        
        for tracker in self._tracking.values():
            await tracker.initialize()
    
    async def _initialize_processors(self) -> None:
        """
Initialize processors"""
        self._processors = {
            'analytics': AnalyticsProcessor(self.config.get('processors', {}).get('analytics', {})),
            'metrics': MetricsProcessor(self.config.get('processors', {}).get('metrics', {}))
        }
        
        for processor in self._processors.values():
            await processor.initialize()
    
    def _register_services(self) -> None:
        """
Register all services in the service registry"""
        self._services = {
            'collector': self._collectors,
            'aggregator': self._aggregators,
            'dashboard': self._dashboards,
            'intelligence': self._intelligence,
            'reporting': self._reporting,
            'tracking': self._tracking,
            'processor': self._processors
        }
    
    def _get_service_instance(self, service_type: str, service_name: str):
        """
Get service instance by type and name"""
        if service_type not in self._services:
            raise AnalyticsError(f"Unknown service type: {service_type}")
        
        if service_name not in self._services[service_type]:
            raise AnalyticsError(f"Unknown service name '{service_name}' for type '{service_type}'")
        
        return self._services[service_type][service_name]
    
    async def _get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            'version': self.version,
            'author': self.author,
            'email': self.email,
            'copyright': self.copyright,
            'initialized': self._initialized,
            'services_count': {
                service_type: len(services)
                for service_type, services in self._services.items()
            }
        }
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """
Get system-level metrics"""
        try:
            import psutil
            
            return {
                'cpu_usage_percent': psutil.cpu_percent(),
                'memory_usage_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids()),
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except ImportError:
            return {'error': 'psutil not available for system metrics'}
        except Exception as e:
            return {'error': f'System metrics error: {str(e)}'}
    
    async def _update_request_stats(self, start_time: datetime, success: bool) -> None:
        """
Update request statistics"""
        try:
            self.module_stats['total_requests'] += 1
            
            if success:
                self.module_stats['successful_requests'] += 1
            else:
                self.module_stats['failed_requests'] += 1
            
            # Update average response time
            response_time = (datetime.now() - start_time).total_seconds()
            current_avg = self.module_stats['average_response_time']
            total_requests = self.module_stats['total_requests']
            
            # Calculate rolling average
            self.module_stats['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            self.module_stats['last_activity'] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error updating request stats: {str(e)}")


# Global module instance
_analytics_module: Optional[AnalyticsModule] = None


async def get_analytics_module(config: Optional[Dict[str, Any]] = None) -> AnalyticsModule:
    """Get or create the global analytics module instance"""
    global _analytics_module
    
    if _analytics_module is None:
        _analytics_module = AnalyticsModule(config)
        await _analytics_module.initialize()
    
    return _analytics_module


async def shutdown_analytics_module() -> None:
    """
Shutdown the global analytics module instance"""
    global _analytics_module
    
    if _analytics_module is not None:
        await _analytics_module.shutdown()
        _analytics_module = None


# Convenience functions for direct access
async def collect_metric(
    name: str,
    value: Union[int, float],
    metric_type: MetricType,
    scope: MetricScope,
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
Convenience function for collecting metrics"""
    module = await get_analytics_module()
    return await module.collect_metric(name, value, metric_type, scope, tags, metadata)


async def get_realtime_metrics() -> Dict[str, Any]:
    """
Convenience function for getting real-time metrics"""
    module = await get_analytics_module()
    return await module.get_realtime_metrics()


async def generate_report(
    report_type: str,
    period_days: int = 30,
    format_type: str = "json",
    include_forecasts: bool = True
) -> Dict[str, Any]:
    """Convenience function for generating reports"""
    module = await get_analytics_module()
    return await module.generate_report(report_type, period_days, format_type, include_forecasts)


async def track_user_activity(
    user_id: str,
    activity: Dict[str, Any],
    session_id: Optional[str] = None
) -> str:
    """
Convenience function for tracking user activity"""
    module = await get_analytics_module()
    return await module.track_user_activity(user_id, activity, session_id)


async def track_content_performance(
    content_id: str,
    metrics: Dict[str, Any]
) -> None:
    """
Convenience function for tracking content performance"""
    module = await get_analytics_module()
    return await module.track_content_performance(content_id, metrics)


async def track_revenue_event(
    event_type: str,
    amount: float,
    metadata: Dict[str, Any]
) -> str:
    """
Convenience function for tracking revenue events"""
    module = await get_analytics_module()
    return await module.track_revenue_event(event_type, amount, metadata)


async def get_dashboard_data(
    dashboard_type: str = "analytics",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function for getting dashboard data"""
    module = await get_analytics_module()
    return await module.get_dashboard_data(dashboard_type, user_id)


async def generate_business_insights(
    period: str = "daily",
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Convenience function for generating business insights"""
    module = await get_analytics_module()
    return await module.generate_business_insights(period, focus_areas)


async def get_predictive_forecasts(
    period: str = "daily",
    forecast_horizon: int = 30
) -> Dict[str, Any]:
    """Convenience function for getting predictive forecasts"""
    module = await get_analytics_module()
    return await module.get_predictive_forecasts(period, forecast_horizon)


async def health_check() -> Dict[str, Any]:
    """
Convenience function for health check"""
    try:
        module = await get_analytics_module()
        return await module.health_check()
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'module_status': 'error',
            'error': str(e)
        }


# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Export everything from __init__.py plus additional index functionality
from . import *

__all__ = [
    # Main module class
    "AnalyticsModule",
    
    # Module management functions
    "get_analytics_module",
    "shutdown_analytics_module",
    
    # Convenience functions
    "collect_metric",
    "get_realtime_metrics", 
    "generate_report",
    "track_user_activity",
    "track_content_performance",
    "track_revenue_event",
    "get_dashboard_data",
    "generate_business_insights",
    "get_predictive_forecasts",
    "health_check",
    
    # Re-export from __init__.py
    "AnalyticsEngine",
    "MetricsCollector",
    "BusinessMetricsCollector",
    "DataAggregator", 
    "TimeSeriesAggregator",
    "AnalyticsProcessor",
    "MetricsProcessor",
    "AnalyticsDashboard",
    "RealtimeDashboard",
    "BusinessIntelligence",
    "PredictiveAnalytics",
    "ReportGenerator",
    "PerformanceReporter",
    "UserTracker",
    "ContentTracker",
    "RevenueTracker",
    "AnalyticsError",
    "MetricsError",
    "ReportingError"
]
