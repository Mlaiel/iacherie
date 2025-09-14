"""Monitoring Services Interface
Main entry point for Ainflue Platform monitoring infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """MetricType class implementation"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram" 
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """AlertSeverity class implementation"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class MonitoringAlert:
    """Monitoring alert configuration"""
    alert_id: str
    service_name: str
    severity: AlertSeverity
    message: str
    metric_name: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

@dataclass
class MetricDefinition:
    """Metric definition and configuration"""
    name: str
    type: MetricType
    description: str
    labels: Optional[Dict[str, str]] = None
    help_text: Optional[str] = None

class MonitoringOrchestrator:
    """Main orchestrator for monitoring services"""
    
    def __init__(self) -> None:
        self.prometheus_collector = None
        self.grafana_dashboard = None
        self.jaeger_tracing = None
        self.elk_stack = None
        self.alertmanager = None
        self.health_checker = None
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.registered_metrics: Dict[str, MetricDefinition] = {}
    
    async def initialize(self) -> None:
        """Initialize all monitoring services"""
        logger.info("Initializing Monitoring Orchestrator...")
        
        # Initialize core monitoring services
        await self._initialize_prometheus()
        await self._initialize_grafana()
        await self._initialize_jaeger()
        await self._initialize_elk_stack()
        await self._initialize_alertmanager()
        await self._initialize_health_checker()
        
        # Register default metrics
        await self._register_default_metrics()
        
        logger.info("Monitoring Orchestrator initialized successfully")
    
    async def _initialize_prometheus(self) -> None:
        """Initialize Prometheus metrics collector"""
        from .prometheus_collector import PrometheusCollector
        self.prometheus_collector = PrometheusCollector()
        await self.prometheus_collector.initialize()
        logger.info("✅ Prometheus collector initialized")
    
    async def _initialize_grafana(self) -> None:
        """Initialize Grafana dashboard service"""
        from .grafana_dashboard import GrafanaDashboard
        self.grafana_dashboard = GrafanaDashboard()
        await self.grafana_dashboard.initialize()
        logger.info("✅ Grafana dashboard initialized")
    
    async def _initialize_jaeger(self) -> None:
        """Initialize Jaeger distributed tracing"""
        from .jaeger_tracing import JaegerTracing
        self.jaeger_tracing = JaegerTracing()
        await self.jaeger_tracing.initialize()
        logger.info("✅ Jaeger tracing initialized")
    
    async def _initialize_elk_stack(self) -> None:
        """Initialize ELK stack for log management"""
        from .elk_stack import ELKStack
        self.elk_stack = ELKStack()
        await self.elk_stack.initialize()
        logger.info("✅ ELK stack initialized")
    
    async def _initialize_alertmanager(self) -> None:
        """Initialize Alert Manager"""
        from .alertmanager import AlertManager
        self.alertmanager = AlertManager()
        await self.alertmanager.initialize()
        logger.info("✅ Alert Manager initialized")
    
    async def _initialize_health_checker(self) -> None:
        """Initialize Health Checker"""
        from .health_checker import HealthChecker
        self.health_checker = HealthChecker()
        await self.health_checker.initialize()
        logger.info("✅ Health Checker initialized")
    
    async def _register_default_metrics(self) -> None:
        """Register default platform metrics"""
        default_metrics = [
            MetricDefinition(
                name="ainflue_content_uploads_total",
                type=MetricType.COUNTER,
                description="Total number of content uploads",
                labels={"creator_type": "", "content_type": ""},
                help_text="Tracks total content uploads by creator and content type"
            ),
            MetricDefinition(
                name="ainflue_api_request_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="API request duration in seconds",
                labels={"method": "", "endpoint": "", "status_code": ""},
                help_text="Measures API request latency"
            ),
            MetricDefinition(
                name="ainflue_active_users",
                type=MetricType.GAUGE,
                description="Number of currently active users",
                labels={"platform": ""},
                help_text="Current number of active users on the platform"
            ),
            MetricDefinition(
                name="ainflue_revenue_generated",
                type=MetricType.COUNTER,
                description="Total revenue generated",
                labels={"revenue_type": "", "creator_id": ""},
                help_text="Tracks total revenue generated by type and creator"
            ),
            MetricDefinition(
                name="ainflue_processing_queue_size",
                type=MetricType.GAUGE,
                description="Current processing queue size",
                labels={"queue_type": "", "priority": ""},
                help_text="Number of items in processing queues"
            )
        ]
        
        for metric in default_metrics:
            await self.register_metric(metric)
    
    async def register_metric(self, metric -> None: MetricDefinition) -> None:
        """Register a new metric with Prometheus"""
        try:
            await self.prometheus_collector.register_metric(metric)
            self.registered_metrics[metric.name] = metric
            logger.info(f"✅ Registered metric: {metric.name}")
        except Exception as e:
            logger.error(f"❌ Failed to register metric {metric.name}: {e}")
            raise
    
    async def record_metric(self, metric_name -> None: str, value -> None: float, 
                           labels -> None: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value"""
        try:
            await self.prometheus_collector.record_metric(metric_name, value, labels)
        except Exception as e:
            logger.error(f"❌ Failed to record metric {metric_name}: {e}")
            raise
    
    async def create_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Create a new Grafana dashboard"""
        try:
            dashboard_id = await self.grafana_dashboard.create_dashboard(dashboard_config)
            logger.info(f"✅ Created dashboard: {dashboard_id}")
            return dashboard_id
        except Exception as e:
            logger.error(f"❌ Failed to create dashboard: {e}")
            raise
    
    async def start_trace(self, operation_name: str, 
                         tags: Optional[Dict[str, str]] = None) -> str:
        """Start a distributed trace"""
        try:
            trace_id = await self.jaeger_tracing.start_trace(operation_name, tags)
            return trace_id
        except Exception as e:
            logger.error(f"❌ Failed to start trace {operation_name}: {e}")
            raise
    
    async def finish_trace(self, trace_id -> None: str, 
                          tags -> None: Optional[Dict[str, str]] = None) -> None:
        """Finish a distributed trace"""
        try:
            await self.jaeger_tracing.finish_trace(trace_id, tags)
        except Exception as e:
            logger.error(f"❌ Failed to finish trace {trace_id}: {e}")
            raise
    
    async def log_event(self, service_name -> None: str, level -> None: str, 
                       message -> None: str, metadata -> None: Optional[Dict] = None) -> None:
        """Log an event to ELK stack"""
        try:
            await self.elk_stack.log_event(service_name, level, message, metadata)
        except Exception as e:
            logger.error(f"❌ Failed to log event: {e}")
            raise
    
    async def create_alert(self, alert -> None: MonitoringAlert) -> None:
        """Create a new monitoring alert"""
        try:
            self.active_alerts[alert.alert_id] = alert
            
            # Send to AlertManager
            await self.alertmanager.send_alert(alert)
            
            logger.info(f"🚨 Alert created: {alert.alert_id} - {alert.message}")
        except Exception as e:
            logger.error(f"❌ Failed to create alert {alert.alert_id}: {e}")
            raise
    
    async def resolve_alert(self, alert_id -> None: str, resolution_notes -> None: str) -> None:
        """Resolve a monitoring alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved_at = datetime.now()
                
                # Send resolution to AlertManager
                await self.alertmanager.resolve_alert(alert_id, resolution_notes)
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                logger.info(f"✅ Alert resolved: {alert_id}")
            else:
                logger.warning(f"⚠️ Alert not found: {alert_id}")
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert {alert_id}: {e}")
            raise
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for a specific service"""
        try:
            health_status = await self.health_checker.check_service_health(service_name)
            return health_status
        except Exception as e:
            logger.error(f"❌ Failed to get health for {service_name}: {e}")
            raise
    
    async def get_platform_metrics(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get comprehensive platform metrics"""
        try:
            metrics = await self.prometheus_collector.query_metrics([
                "ainflue_content_uploads_total",
                "ainflue_api_request_duration_seconds",
                "ainflue_active_users",
                "ainflue_revenue_generated",
                "ainflue_processing_queue_size"
            ], time_range)
            
            return {
                "content_uploads": metrics.get("ainflue_content_uploads_total", 0),
                "api_latency": metrics.get("ainflue_api_request_duration_seconds", 0),
                "active_users": metrics.get("ainflue_active_users", 0),
                "revenue": metrics.get("ainflue_revenue_generated", 0),
                "queue_size": metrics.get("ainflue_processing_queue_size", 0),
                "timestamp": datetime.now().isoformat(),
                "time_range": time_range
            }
        except Exception as e:
            logger.error(f"❌ Failed to get platform metrics: {e}")
            raise
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        try:
            dashboard_data = {
                "active_alerts": len(self.active_alerts),
                "alert_breakdown": {severity.value: 0 for severity in AlertSeverity},
                "registered_metrics": len(self.registered_metrics),
                "service_health": await self._get_all_service_health(),
                "platform_metrics": await self.get_platform_metrics(),
                "recent_traces": await self.jaeger_tracing.get_recent_traces(limit=10),
                "system_status": await self._get_system_status()
            }
            
            # Count alerts by severity
            for alert in self.active_alerts.values():
                dashboard_data["alert_breakdown"][alert.severity.value] += 1
            
            return dashboard_data
        except Exception as e:
            logger.error(f"❌ Failed to generate monitoring dashboard: {e}")
            raise
    
    async def _get_all_service_health(self) -> Dict[str, str]:
        """Get health status for all services"""
        services = [
            "prometheus", "grafana", "jaeger", "elasticsearch", 
            "logstash", "kibana", "alertmanager"
        ]
        
        health_status = {}
        for service in services:
            try:
                status = await self.get_service_health(service)
                health_status[service] = status.get("status", "unknown")
            except Exception:
                health_status[service] = "error"
        
        return health_status
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            # Get resource utilization
            resource_metrics = await self.prometheus_collector.query_metrics([
                "container_cpu_usage_seconds_total",
                "container_memory_usage_bytes",
                "container_network_receive_bytes_total"
            ], "5m")
            
            return {
                "cpu_usage": resource_metrics.get("container_cpu_usage_seconds_total", 0),
                "memory_usage": resource_metrics.get("container_memory_usage_bytes", 0),
                "network_traffic": resource_metrics.get("container_network_receive_bytes_total", 0),
                "uptime": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all monitoring services"""
        logger.info("Shutting down Monitoring Orchestrator...")
        
        services = [
            ("prometheus_collector", self.prometheus_collector),
            ("grafana_dashboard", self.grafana_dashboard),
            ("jaeger_tracing", self.jaeger_tracing),
            ("elk_stack", self.elk_stack),
            ("alertmanager", self.alertmanager),
            ("health_checker", self.health_checker)
        ]
        
        for service_name, service in services:
            try:
                if service and hasattr(service, 'shutdown'):
                    await service.shutdown()
                    logger.info(f"✅ {service_name} shutdown")
            except Exception as e:
                logger.error(f"❌ Error shutting down {service_name}: {e}")
        
        logger.info("✅ Monitoring Orchestrator shutdown complete")

# Global monitoring orchestrator instance
monitoring_orchestrator = MonitoringOrchestrator()

async def initialize_monitoring_services() -> None:
    """Initialize monitoring services"""
    await monitoring_orchestrator.initialize()

async def shutdown_monitoring_services() -> None:
    """Shutdown monitoring services"""
    await monitoring_orchestrator.shutdown()

__all__ = [
    'MetricType', 'AlertSeverity', 'MonitoringAlert', 'MetricDefinition',
    'MonitoringOrchestrator', 'monitoring_orchestrator', 'initialize_monitoring_services',
    'shutdown_monitoring_services'
]