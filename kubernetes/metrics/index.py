"""IA Influencer Agent - Metrics Deployment Module Index
Central entry point for enterprise metrics collection and monitoring deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Centralized metrics management
- Multi-tenant metrics deployment
- Enterprise-grade monitoring solutions
- Real-time analytics and dashboards
- Content protection metrics tracking
- Revenue and business intelligence
- AI model performance monitoring
- Infrastructure health monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from .config import get_metrics_config, MetricsConfiguration
from .prometheus_manager import PrometheusManager
from .grafana_manager import GrafanaManager
from .metrics_collector import MetricsCollector
from .alert_manager import AlertManager
from .performance_analytics import PerformanceAnalytics
from .dashboard import MetricsDashboard
from .business_intelligence import BusinessIntelligence
from .business_events_collector import BusinessEventsCollector
from .content_protection_metrics import ContentProtectionMetricsCollector
from .revenue_metrics_collector import RevenueMetricsCollector
from .infrastructure_metrics import InfrastructureMetricsCollector
from .ai_model_metrics import AIModelMetricsCollector

logger = logging.getLogger(__name__)


class MetricsDeploymentManager:
    """
    Central metrics deployment manager for the IA Influencer Agent platform
    
    Orchestrates all metrics collection, monitoring, and analytics services
    for enterprise-grade observability and business intelligence.
    """
    
    def __init__(self, config -> None: Optional[MetricsConfiguration] = None) -> None:
        self.config = config or get_metrics_config()
        self._services: Dict[str, Any] = {}
        self._collectors: Dict[str, Any] = {}
        self._is_initialized = False
        self._is_running = False
        
    async def initialize(self) -> None:
        """
Initialize all metrics services and collectors"""
        if self._is_initialized:
            logger.warning("Metrics deployment manager already initialized")
            return
            
        try:
            logger.info("Initializing metrics deployment manager...")
            
            # Validate configuration
            validation_issues = self.config.validate_configuration()
            if validation_issues:
                logger.warning(f"Configuration validation issues: {validation_issues}")
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Initialize specialized collectors
            await self._initialize_collectors()
            
            # Setup inter-service connections
            await self._setup_service_connections()
            
            self._is_initialized = True
            logger.info("Metrics deployment manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics deployment manager: {e}")
            raise
    
    async def _initialize_core_services(self) -> None:
        """Initialize core metrics services"""
        
        # Prometheus metrics manager
        if self.config.prometheus.enabled:
            self._services['prometheus'] = PrometheusManager()
            logger.info("Prometheus manager initialized")
        
        # Grafana dashboard manager
        if self.config.grafana.enabled:
            self._services['grafana'] = GrafanaManager(
                url=self.config.grafana.url,
                api_key=self.config.grafana.api_key
            )
            logger.info("Grafana manager initialized")
        
        # Alert manager
        if self.config.alerts.enabled:
            self._services['alerts'] = AlertManager(
                notification_channels=self.config.get_notification_channels(),
                evaluation_interval=self.config.alerts.evaluation_interval
            )
            logger.info("Alert manager initialized")
        
        # Metrics collector
        self._services['collector'] = MetricsCollector(
            prometheus_manager=self._services.get('prometheus'),
            alert_manager=self._services.get('alerts')
        )
        
        # Performance analytics
        self._services['analytics'] = PerformanceAnalytics(
            metrics_collector=self._services['collector']
        )
        
        # Dashboard manager
        self._services['dashboard'] = MetricsDashboard(
            grafana_manager=self._services.get('grafana'),
            dashboard_configs=self.config.get_dashboard_configs()
        )
        
        # Business intelligence
        self._services['business_intelligence'] = BusinessIntelligence(
            metrics_collector=self._services['collector'],
            analytics=self._services['analytics']
        )
    
    async def _initialize_collectors(self) -> None:
        """Initialize specialized metrics collectors"""
        
        # Business events collector
        self._collectors['business_events'] = BusinessEventsCollector(
            prometheus_manager=self._services.get('prometheus')
        )
        
        # Content protection metrics collector
        self._collectors['content_protection'] = ContentProtectionMetricsCollector(
            prometheus_manager=self._services.get('prometheus')
        )
        
        # Revenue metrics collector
        self._collectors['revenue'] = RevenueMetricsCollector(
            prometheus_manager=self._services.get('prometheus')
        )
        
        # Infrastructure metrics collector
        self._collectors['infrastructure'] = InfrastructureMetricsCollector(
            prometheus_manager=self._services.get('prometheus')
        )
        
        # AI model metrics collector
        self._collectors['ai_models'] = AIModelMetricsCollector(
            prometheus_manager=self._services.get('prometheus')
        )
        
        logger.info(f"Initialized {len(self._collectors)} specialized collectors")
    
    async def _setup_service_connections(self) -> None:
        """Setup connections between services"""
        
        # Connect collectors to alert manager
        if 'alerts' in self._services:
            for collector_name, collector in self._collectors.items():
                if hasattr(collector, 'set_alert_manager'):
                    collector.set_alert_manager(self._services['alerts'])
        
        # Connect analytics to dashboard
        if 'dashboard' in self._services and 'analytics' in self._services:
            self._services['dashboard'].set_analytics_provider(
                self._services['analytics']
            )
        
        logger.info("Service connections established")
    
    async def start(self) -> None:
        """Start all metrics services"""
        if not self._is_initialized:
            await self.initialize()
        
        if self._is_running:
            logger.warning("Metrics deployment manager already running")
            return
        
        try:
            logger.info("Starting metrics deployment manager...")
            
            # Start core services
            await self._start_services()
            
            # Start collectors
            await self._start_collectors()
            
            # Deploy default dashboards
            await self._deploy_default_dashboards()
            
            # Setup default alerts
            await self._setup_default_alerts()
            
            self._is_running = True
            logger.info("Metrics deployment manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start metrics deployment manager: {e}")
            raise
    
    async def _start_services(self) -> None:
        """Start core services"""
        
        # Start Prometheus if enabled
        if 'prometheus' in self._services:
            await self._services['prometheus'].start()
            logger.info("Prometheus service started")
        
        # Start alert manager if enabled
        if 'alerts' in self._services:
            await self._services['alerts'].start()
            logger.info("Alert manager started")
        
        # Start analytics
        if 'analytics' in self._services:
            await self._services['analytics'].start()
            logger.info("Performance analytics started")
    
    async def _start_collectors(self) -> None:
        """Start metrics collectors"""
        
        start_tasks = []
        for collector_name, collector in self._collectors.items():
            if hasattr(collector, 'start'):
                start_tasks.append(collector.start())
        
        if start_tasks:
            await asyncio.gather(*start_tasks, return_exceptions=True)
            logger.info(f"Started {len(start_tasks)} collectors")
    
    async def _deploy_default_dashboards(self) -> None:
        """Deploy default Grafana dashboards"""
        
        if 'dashboard' in self._services:
            try:
                await self._services['dashboard'].deploy_default_dashboards()
                logger.info("Default dashboards deployed")
            except Exception as e:
                logger.warning(f"Failed to deploy default dashboards: {e}")
    
    async def _setup_default_alerts(self) -> None:
        """Setup default alert rules"""
        
        if 'alerts' in self._services:
            try:
                thresholds = self.config.get_alert_thresholds()
                await self._services['alerts'].setup_default_alerts(thresholds)
                logger.info("Default alerts configured")
            except Exception as e:
                logger.warning(f"Failed to setup default alerts: {e}")
    
    async def stop(self) -> None:
        """Stop all metrics services"""
        if not self._is_running:
            return
        
        try:
            logger.info("Stopping metrics deployment manager...")
            
            # Stop collectors
            stop_tasks = []
            for collector_name, collector in self._collectors.items():
                if hasattr(collector, 'stop'):
                    stop_tasks.append(collector.stop())
            
            if stop_tasks:
                await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            # Stop services
            for service_name, service in self._services.items():
                if hasattr(service, 'stop'):
                    try:
                        await service.stop()
                        logger.info(f"Stopped {service_name} service")
                    except Exception as e:
                        logger.warning(f"Error stopping {service_name}: {e}")
            
            self._is_running = False
            logger.info("Metrics deployment manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping metrics deployment manager: {e}")
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a specific service by name"""
        return self._services.get(service_name)
    
    def get_collector(self, collector_name: str) -> Optional[Any]:
        """
Get a specific collector by name"""
        return self._collectors.get(collector_name)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
Get health status of all services and collectors"""
        status = {
            'initialized': self._is_initialized,
            'running': self._is_running,
            'services': {},
            'collectors': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check services health
        for service_name, service in self._services.items():
            if hasattr(service, 'get_health_status'):
                status['services'][service_name] = service.get_health_status()
            else:
                status['services'][service_name] = {'status': 'unknown'}
        
        # Check collectors health
        for collector_name, collector in self._collectors.items():
            if hasattr(collector, 'get_health_status'):
                status['collectors'][collector_name] = collector.get_health_status()
            else:
                status['collectors'][collector_name] = {'status': 'unknown'}
        
        return status
    
    async def export_metrics(self, format: str = 'prometheus') -> str:
        """
Export metrics in specified format"""
        if format == 'prometheus' and 'prometheus' in self._services:
            return await self._services['prometheus'].export_metrics()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'configuration': {
                'environment': self.config.environment.value,
                'prometheus_enabled': self.config.prometheus.enabled,
                'grafana_enabled': self.config.grafana.enabled,
                'alerts_enabled': self.config.alerts.enabled
            },
            'services_status': {},
            'collectors_status': {},
            'metrics_count': 0
        }
        
        # Get service statuses
        for service_name, service in self._services.items():
            if hasattr(service, 'get_status'):
                summary['services_status'][service_name] = service.get_status()
        
        # Get collector statuses  
        for collector_name, collector in self._collectors.items():
            if hasattr(collector, 'get_status'):
                summary['collectors_status'][collector_name] = collector.get_status()
        
        # Get total metrics count
        if 'prometheus' in self._services:
            summary['metrics_count'] = self._services['prometheus'].get_metrics_count()
        
        return summary


# Context manager for metrics deployment
@asynccontextmanager
async def metrics_deployment_context(config -> None: Optional[MetricsConfiguration] = None) -> None:
    """
Context manager for metrics deployment lifecycle"""
    manager = MetricsDeploymentManager(config)
    
    try:
        await manager.start()
        yield manager
    finally:
        await manager.stop()


# Global deployment manager instance
_deployment_manager: Optional[MetricsDeploymentManager] = None


def get_metrics_deployment_manager() -> MetricsDeploymentManager:
    """
Get global metrics deployment manager instance"""
    global _deployment_manager
    
    if _deployment_manager is None:
        _deployment_manager = MetricsDeploymentManager()
    
    return _deployment_manager


async def initialize_metrics_deployment(config: Optional[MetricsConfiguration] = None) -> None:
    """
Initialize global metrics deployment"""
    manager = get_metrics_deployment_manager()
    if config:
        manager.config = config
    await manager.initialize()


async def start_metrics_deployment() -> None:
    """
Start global metrics deployment"""
    manager = get_metrics_deployment_manager()
    await manager.start()


async def stop_metrics_deployment() -> None:
    """
Stop global metrics deployment"""
    manager = get_metrics_deployment_manager()
    await manager.stop()


if __name__ == "__main__":
    """
    Direct execution for testing and debugging
    """
    async def main() -> None:
        config = get_metrics_config()
        
        async with metrics_deployment_context(config) as manager:
            logger.info("Metrics deployment manager running...")
            
            # Display health status
            health_status = manager.get_health_status()
            logger.info(f"Health status: {health_status}")
            
            # Keep running for demonstration
            await asyncio.sleep(10)
            
            # Display metrics summary
            summary = await manager.get_metrics_summary()
            logger.info(f"Metrics summary: {summary}")
    
    # Run the demo
    asyncio.run(main())
