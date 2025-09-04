"""Business Process Monitoring - IA Influencer Agent Platform
==========================================================

Consolidated business process monitoring for real-time tracking, health checks,
alerting, and performance monitoring across all business operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import statistics
from collections import deque, defaultdict

# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class MonitoringType(Enum):
    """Types of monitoring."""
    SYSTEM_HEALTH = "system_health"
    BUSINESS_METRICS = "business_metrics"
    APPLICATION_PERFORMANCE = "application_performance"
    USER_ACTIVITY = "user_activity"
    SECURITY_EVENTS = "security_events"
    FINANCIAL_OPERATIONS = "financial_operations"
    CONTENT_OPERATIONS = "content_operations"
    COLLABORATION_PROCESSES = "collaboration_processes"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MonitoringStatus(Enum):
    """Monitoring status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


@dataclass
class MonitoringMetric:
    """Monitoring metric definition."""
    metric_id: str
    name: str
    value: Union[int, float, str, bool]
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    monitoring_type: MonitoringType = MonitoringType.SYSTEM_HEALTH
    thresholds: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert definition."""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    monitoring_type: MonitoringType
    source: str
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    is_active: bool = True
    actions_taken: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check definition."""
    check_id: str
    name: str
    check_type: MonitoringType
    status: MonitoringStatus
    last_check: datetime = field(default_factory=datetime.utcnow)
    response_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    failure_count: int = 0
    success_count: int = 0


class BusinessMonitor:
    """
    Consolidated business process monitoring system for the IA Influencer platform.
    
    Provides real-time monitoring, health checks, alerting, and performance tracking
    for all business operations including content, revenue, users, and systems.
    """
    
    def __init__(self):
        """Initialize the business monitor."""
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))  # Store last 1000 values
        self.alerts: Dict[str, Alert] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alert_handlers: Dict[AlertSeverity, List[Callable]] = defaultdict(list)
        self.monitoring_config: Dict[str, Dict[str, Any]] = {}
        self.is_monitoring: bool = False
        self.logger = logging.getLogger(__name__)
        self._setup_default_monitoring()
        self._setup_default_health_checks()
    
    def _setup_default_monitoring(self):
        """Setup default monitoring configuration."""
        self.monitoring_config.update({
            "system_health": {
                "cpu_usage": {"warning": 70, "critical": 90},
                "memory_usage": {"warning": 80, "critical": 95},
                "disk_usage": {"warning": 85, "critical": 95},
                "response_time": {"warning": 2000, "critical": 5000}  # milliseconds
            },
            "business_metrics": {
                "revenue_per_hour": {"warning": 100, "critical": 50},  # Below threshold is bad
                "active_users": {"warning": 1000, "critical": 500},
                "error_rate": {"warning": 5, "critical": 10},  # percentage
                "conversion_rate": {"warning": 10, "critical": 5}  # Below threshold is bad
            },
            "application_performance": {
                "api_response_time": {"warning": 1000, "critical": 3000},  # milliseconds
                "database_connections": {"warning": 80, "critical": 95},  # percentage of pool
                "cache_hit_ratio": {"warning": 80, "critical": 60},  # Below threshold is bad
                "queue_length": {"warning": 100, "critical": 500}
            },
            "content_operations": {
                "upload_success_rate": {"warning": 95, "critical": 90},  # Below threshold is bad
                "processing_time": {"warning": 30, "critical": 60},  # seconds
                "storage_usage": {"warning": 80, "critical": 90},  # percentage
                "content_violations": {"warning": 10, "critical": 20}  # count per hour
            },
            "financial_operations": {
                "payment_success_rate": {"warning": 98, "critical": 95},  # Below threshold is bad
                "transaction_volume": {"warning": 1000, "critical": 500},  # per hour
                "fraud_detection_rate": {"warning": 2, "critical": 5},  # percentage
                "refund_rate": {"warning": 5, "critical": 10}  # percentage
            }
        })
    
    def _setup_default_health_checks(self):
        """Setup default health checks."""
        health_checks = [
            HealthCheck(
                check_id="database_connection",
                name="Database Connection",
                check_type=MonitoringType.SYSTEM_HEALTH,
                status=MonitoringStatus.HEALTHY
            ),
            HealthCheck(
                check_id="redis_connection",
                name="Redis Connection",
                check_type=MonitoringType.SYSTEM_HEALTH,
                status=MonitoringStatus.HEALTHY
            ),
            HealthCheck(
                check_id="api_endpoints",
                name="API Endpoints",
                check_type=MonitoringType.APPLICATION_PERFORMANCE,
                status=MonitoringStatus.HEALTHY
            ),
            HealthCheck(
                check_id="payment_gateway",
                name="Payment Gateway",
                check_type=MonitoringType.FINANCIAL_OPERATIONS,
                status=MonitoringStatus.HEALTHY
            ),
            HealthCheck(
                check_id="content_storage",
                name="Content Storage",
                check_type=MonitoringType.CONTENT_OPERATIONS,
                status=MonitoringStatus.HEALTHY
            ),
            HealthCheck(
                check_id="user_authentication",
                name="User Authentication",
                check_type=MonitoringType.SECURITY_EVENTS,
                status=MonitoringStatus.HEALTHY
            )
        ]
        
        for check in health_checks:
            self.health_checks[check.check_id] = check
    
    async def start_monitoring(self) -> None:
        """Start the monitoring system."""
        try:
            self.is_monitoring = True
            self.logger.info("Starting business monitoring system")
            
            # Start monitoring tasks
            await asyncio.gather(
                self._monitor_system_health(),
                self._monitor_business_metrics(),
                self._monitor_application_performance(),
                self._run_health_checks(),
                self._process_alerts(),
                return_exceptions=True
            )
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {str(e)}")
            self.is_monitoring = False
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        try:
            self.is_monitoring = False
            self.logger.info("Stopped business monitoring system")
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")
    
    async def _monitor_system_health(self) -> None:
        """Monitor system health metrics."""
        while self.is_monitoring:
            try:
                if PSUTIL_AVAILABLE:
                    # CPU Usage
                    cpu_usage = psutil.cpu_percent(interval=1)
                    await self.record_metric(MonitoringMetric(
                        metric_id="cpu_usage",
                        name="CPU Usage",
                        value=cpu_usage,
                        unit="percentage",
                        monitoring_type=MonitoringType.SYSTEM_HEALTH,
                        thresholds=self.monitoring_config["system_health"]["cpu_usage"]
                    ))
                    
                    # Memory Usage
                    memory = psutil.virtual_memory()
                    memory_usage = memory.percent
                    await self.record_metric(MonitoringMetric(
                        metric_id="memory_usage",
                        name="Memory Usage",
                        value=memory_usage,
                        unit="percentage",
                        monitoring_type=MonitoringType.SYSTEM_HEALTH,
                        thresholds=self.monitoring_config["system_health"]["memory_usage"]
                    ))
                    
                    # Disk Usage
                    disk = psutil.disk_usage('/')
                    disk_usage = (disk.used / disk.total) * 100
                    await self.record_metric(MonitoringMetric(
                        metric_id="disk_usage",
                        name="Disk Usage",
                        value=disk_usage,
                        unit="percentage",
                        monitoring_type=MonitoringType.SYSTEM_HEALTH,
                        thresholds=self.monitoring_config["system_health"]["disk_usage"]
                    ))
                else:
                    # Simulate system metrics when psutil is not available
                    import random
                    await self.record_metric(MonitoringMetric(
                        metric_id="cpu_usage",
                        name="CPU Usage",
                        value=random.uniform(10, 80),
                        unit="percentage",
                        monitoring_type=MonitoringType.SYSTEM_HEALTH,
                        thresholds=self.monitoring_config["system_health"]["cpu_usage"]
                    ))
                    
                    await self.record_metric(MonitoringMetric(
                        metric_id="memory_usage",
                        name="Memory Usage",
                        value=random.uniform(30, 90),
                        unit="percentage",
                        monitoring_type=MonitoringType.SYSTEM_HEALTH,
                        thresholds=self.monitoring_config["system_health"]["memory_usage"]
                    ))
                    
                    await self.record_metric(MonitoringMetric(
                        metric_id="disk_usage",
                        name="Disk Usage",
                        value=random.uniform(20, 85),
                        unit="percentage",
                        monitoring_type=MonitoringType.SYSTEM_HEALTH,
                        thresholds=self.monitoring_config["system_health"]["disk_usage"]
                    ))
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring system health: {str(e)}")
                await asyncio.sleep(60)
    
    async def _monitor_business_metrics(self) -> None:
        """Monitor business metrics."""
        while self.is_monitoring:
            try:
                import random
                
                # Simulate business metrics
                revenue_per_hour = random.randint(80, 200)
                await self.record_metric(MonitoringMetric(
                    metric_id="revenue_per_hour",
                    name="Revenue per Hour",
                    value=revenue_per_hour,
                    unit="USD",
                    monitoring_type=MonitoringType.BUSINESS_METRICS,
                    thresholds=self.monitoring_config["business_metrics"]["revenue_per_hour"]
                ))
                
                active_users = random.randint(800, 1500)
                await self.record_metric(MonitoringMetric(
                    metric_id="active_users",
                    name="Active Users",
                    value=active_users,
                    unit="count",
                    monitoring_type=MonitoringType.BUSINESS_METRICS,
                    thresholds=self.monitoring_config["business_metrics"]["active_users"]
                ))
                
                error_rate = random.uniform(0.5, 8.0)
                await self.record_metric(MonitoringMetric(
                    metric_id="error_rate",
                    name="Error Rate",
                    value=error_rate,
                    unit="percentage",
                    monitoring_type=MonitoringType.BUSINESS_METRICS,
                    thresholds=self.monitoring_config["business_metrics"]["error_rate"]
                ))
                
                conversion_rate = random.uniform(8.0, 15.0)
                await self.record_metric(MonitoringMetric(
                    metric_id="conversion_rate",
                    name="Conversion Rate",
                    value=conversion_rate,
                    unit="percentage",
                    monitoring_type=MonitoringType.BUSINESS_METRICS,
                    thresholds=self.monitoring_config["business_metrics"]["conversion_rate"]
                ))
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring business metrics: {str(e)}")
                await asyncio.sleep(300)
    
    async def _monitor_application_performance(self) -> None:
        """Monitor application performance metrics."""
        while self.is_monitoring:
            try:
                import random
                
                # Simulate application performance metrics
                api_response_time = random.randint(200, 2500)
                await self.record_metric(MonitoringMetric(
                    metric_id="api_response_time",
                    name="API Response Time",
                    value=api_response_time,
                    unit="milliseconds",
                    monitoring_type=MonitoringType.APPLICATION_PERFORMANCE,
                    thresholds=self.monitoring_config["application_performance"]["api_response_time"]
                ))
                
                db_connections = random.randint(40, 90)
                await self.record_metric(MonitoringMetric(
                    metric_id="database_connections",
                    name="Database Connections",
                    value=db_connections,
                    unit="percentage",
                    monitoring_type=MonitoringType.APPLICATION_PERFORMANCE,
                    thresholds=self.monitoring_config["application_performance"]["database_connections"]
                ))
                
                cache_hit_ratio = random.uniform(70, 95)
                await self.record_metric(MonitoringMetric(
                    metric_id="cache_hit_ratio",
                    name="Cache Hit Ratio",
                    value=cache_hit_ratio,
                    unit="percentage",
                    monitoring_type=MonitoringType.APPLICATION_PERFORMANCE,
                    thresholds=self.monitoring_config["application_performance"]["cache_hit_ratio"]
                ))
                
                queue_length = random.randint(10, 200)
                await self.record_metric(MonitoringMetric(
                    metric_id="queue_length",
                    name="Queue Length",
                    value=queue_length,
                    unit="count",
                    monitoring_type=MonitoringType.APPLICATION_PERFORMANCE,
                    thresholds=self.monitoring_config["application_performance"]["queue_length"]
                ))
                
                await asyncio.sleep(120)  # Monitor every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring application performance: {str(e)}")
                await asyncio.sleep(120)
    
    async def _run_health_checks(self) -> None:
        """Run health checks periodically."""
        while self.is_monitoring:
            try:
                for check_id, health_check in self.health_checks.items():
                    await self._perform_health_check(health_check)
                
                await asyncio.sleep(180)  # Run health checks every 3 minutes
                
            except Exception as e:
                self.logger.error(f"Error running health checks: {str(e)}")
                await asyncio.sleep(180)
    
    async def _perform_health_check(self, health_check: HealthCheck) -> None:
        """Perform a specific health check."""
        try:
            start_time = time.time()
            
            # Simulate health check based on type
            success = await self._simulate_health_check(health_check.check_id)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            health_check.last_check = datetime.utcnow()
            health_check.response_time = response_time
            
            if success:
                health_check.status = MonitoringStatus.HEALTHY
                health_check.success_count += 1
                health_check.failure_count = 0  # Reset failure count on success
                health_check.details = {
                    "status": "operational",
                    "response_time_ms": response_time,
                    "last_successful_check": datetime.utcnow().isoformat()
                }
            else:
                health_check.failure_count += 1
                
                if health_check.failure_count >= 3:
                    health_check.status = MonitoringStatus.CRITICAL
                    await self._create_alert(
                        title=f"Health Check Failed: {health_check.name}",
                        description=f"Health check {health_check.name} has failed {health_check.failure_count} times",
                        severity=AlertSeverity.CRITICAL,
                        monitoring_type=health_check.check_type,
                        source=health_check.check_id
                    )
                else:
                    health_check.status = MonitoringStatus.WARNING
                
                health_check.details = {
                    "status": "failed",
                    "failure_count": health_check.failure_count,
                    "last_failure": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            health_check.status = MonitoringStatus.UNKNOWN
            health_check.details = {"error": str(e)}
            self.logger.error(f"Error performing health check {health_check.check_id}: {str(e)}")
    
    async def _simulate_health_check(self, check_id: str) -> bool:
        """Simulate health check execution."""
        import random
        
        # Simulate different success rates for different checks
        success_rates = {
            "database_connection": 0.98,
            "redis_connection": 0.97,
            "api_endpoints": 0.95,
            "payment_gateway": 0.99,
            "content_storage": 0.96,
            "user_authentication": 0.98
        }
        
        success_rate = success_rates.get(check_id, 0.95)
        return random.random() < success_rate
    
    async def record_metric(self, metric: MonitoringMetric) -> None:
        """Record a monitoring metric."""
        try:
            # Store the metric
            self.metrics[metric.metric_id].append(metric)
            
            # Check thresholds and create alerts if necessary
            await self._check_metric_thresholds(metric)
            
        except Exception as e:
            self.logger.error(f"Error recording metric {metric.metric_id}: {str(e)}")
    
    async def _check_metric_thresholds(self, metric: MonitoringMetric) -> None:
        """Check metric thresholds and create alerts."""
        try:
            if not metric.thresholds:
                return
            
            warning_threshold = metric.thresholds.get("warning")
            critical_threshold = metric.thresholds.get("critical")
            
            # Determine if metric value breaches thresholds
            # Different logic for different types of metrics
            is_reverse_metric = metric.metric_id in [
                "revenue_per_hour", "active_users", "conversion_rate", 
                "upload_success_rate", "payment_success_rate", "cache_hit_ratio"
            ]
            
            alert_severity = None
            
            if is_reverse_metric:
                # For these metrics, lower values are bad
                if critical_threshold and metric.value < critical_threshold:
                    alert_severity = AlertSeverity.CRITICAL
                elif warning_threshold and metric.value < warning_threshold:
                    alert_severity = AlertSeverity.HIGH
            else:
                # For these metrics, higher values are bad
                if critical_threshold and metric.value > critical_threshold:
                    alert_severity = AlertSeverity.CRITICAL
                elif warning_threshold and metric.value > warning_threshold:
                    alert_severity = AlertSeverity.HIGH
            
            if alert_severity:
                await self._create_alert(
                    title=f"Threshold Breach: {metric.name}",
                    description=f"{metric.name} is {metric.value} {metric.unit}, threshold breach detected",
                    severity=alert_severity,
                    monitoring_type=metric.monitoring_type,
                    source=metric.metric_id,
                    metadata={
                        "metric_value": metric.value,
                        "threshold_type": "warning" if alert_severity == AlertSeverity.HIGH else "critical",
                        "threshold_value": warning_threshold if alert_severity == AlertSeverity.HIGH else critical_threshold
                    }
                )
            
        except Exception as e:
            self.logger.error(f"Error checking metric thresholds: {str(e)}")
    
    async def _create_alert(self, title: str, description: str, severity: AlertSeverity, 
                          monitoring_type: MonitoringType, source: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new alert."""
        try:
            # Check if similar alert already exists and is active
            existing_alerts = [
                alert for alert in self.alerts.values()
                if alert.source == source and alert.is_active and 
                (datetime.utcnow() - alert.triggered_at) < timedelta(minutes=30)
            ]
            
            if existing_alerts:
                # Don't create duplicate alerts within 30 minutes
                return existing_alerts[0].alert_id
            
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                title=title,
                description=description,
                severity=severity,
                monitoring_type=monitoring_type,
                source=source,
                metadata=metadata or {}
            )
            
            self.alerts[alert.alert_id] = alert
            
            # Trigger alert handlers
            for handler in self.alert_handlers[severity]:
                try:
                    await handler(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert handler: {str(e)}")
            
            self.logger.warning(f"Alert created: {alert.title} (Severity: {alert.severity.value})")
            return alert.alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            return ""
    
    async def _process_alerts(self) -> None:
        """Process and manage alerts."""
        while self.is_monitoring:
            try:
                # Auto-resolve old alerts that haven't been updated
                for alert in self.alerts.values():
                    if (alert.is_active and 
                        datetime.utcnow() - alert.triggered_at > timedelta(hours=24)):
                        
                        # Auto-resolve alerts older than 24 hours
                        alert.is_active = False
                        alert.resolved_at = datetime.utcnow()
                        alert.actions_taken.append("Auto-resolved due to age")
                
                await asyncio.sleep(3600)  # Process alerts every hour
                
            except Exception as e:
                self.logger.error(f"Error processing alerts: {str(e)}")
                await asyncio.sleep(3600)
    
    def register_alert_handler(self, severity: AlertSeverity, handler: Callable) -> None:
        """Register an alert handler for specific severity."""
        try:
            self.alert_handlers[severity].append(handler)
            self.logger.info(f"Registered alert handler for severity: {severity.value}")
        except Exception as e:
            self.logger.error(f"Error registering alert handler: {str(e)}")
    
    async def resolve_alert(self, alert_id: str, resolution_notes: str) -> bool:
        """Resolve an alert."""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.is_active = False
            alert.resolved_at = datetime.utcnow()
            alert.actions_taken.append(f"Manually resolved: {resolution_notes}")
            
            self.logger.info(f"Resolved alert: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving alert {alert_id}: {str(e)}")
            return False
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard."""
        try:
            # System health summary
            system_health = {}
            for metric_id in ["cpu_usage", "memory_usage", "disk_usage"]:
                if metric_id in self.metrics and self.metrics[metric_id]:
                    latest = self.metrics[metric_id][-1]
                    system_health[metric_id] = {
                        "value": latest.value,
                        "unit": latest.unit,
                        "timestamp": latest.timestamp.isoformat()
                    }
            
            # Active alerts summary
            active_alerts = [alert for alert in self.alerts.values() if alert.is_active]
            alerts_by_severity = {
                severity.value: len([a for a in active_alerts if a.severity == severity])
                for severity in AlertSeverity
            }
            
            # Health checks summary
            health_status = {
                "healthy": len([h for h in self.health_checks.values() if h.status == MonitoringStatus.HEALTHY]),
                "warning": len([h for h in self.health_checks.values() if h.status == MonitoringStatus.WARNING]),
                "critical": len([h for h in self.health_checks.values() if h.status == MonitoringStatus.CRITICAL]),
                "unknown": len([h for h in self.health_checks.values() if h.status == MonitoringStatus.UNKNOWN])
            }
            
            # Business metrics summary
            business_metrics = {}
            for metric_id in ["revenue_per_hour", "active_users", "conversion_rate", "error_rate"]:
                if metric_id in self.metrics and self.metrics[metric_id]:
                    latest = self.metrics[metric_id][-1]
                    business_metrics[metric_id] = {
                        "value": latest.value,
                        "unit": latest.unit,
                        "timestamp": latest.timestamp.isoformat()
                    }
            
            # Performance metrics summary
            performance_metrics = {}
            for metric_id in ["api_response_time", "database_connections", "cache_hit_ratio"]:
                if metric_id in self.metrics and self.metrics[metric_id]:
                    latest = self.metrics[metric_id][-1]
                    performance_metrics[metric_id] = {
                        "value": latest.value,
                        "unit": latest.unit,
                        "timestamp": latest.timestamp.isoformat()
                    }
            
            return {
                "monitoring_status": "active" if self.is_monitoring else "inactive",
                "system_health": system_health,
                "business_metrics": business_metrics,
                "performance_metrics": performance_metrics,
                "alerts_summary": {
                    "total_active": len(active_alerts),
                    "by_severity": alerts_by_severity,
                    "recent_alerts": [
                        {
                            "alert_id": alert.alert_id,
                            "title": alert.title,
                            "severity": alert.severity.value,
                            "triggered_at": alert.triggered_at.isoformat(),
                            "source": alert.source
                        } for alert in sorted(active_alerts, key=lambda a: a.triggered_at, reverse=True)[:5]
                    ]
                },
                "health_checks": {
                    "summary": health_status,
                    "details": [
                        {
                            "check_id": check.check_id,
                            "name": check.name,
                            "status": check.status.value,
                            "last_check": check.last_check.isoformat(),
                            "response_time": check.response_time,
                            "failure_count": check.failure_count
                        } for check in self.health_checks.values()
                    ]
                },
                "metrics_count": sum(len(metric_queue) for metric_queue in self.metrics.values()),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def get_metric_history(self, metric_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metric history for a specific metric."""
        try:
            if metric_id not in self.metrics:
                return []
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_metrics = [
                metric for metric in self.metrics[metric_id]
                if metric.timestamp >= cutoff_time
            ]
            
            return [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.value,
                    "unit": metric.unit
                } for metric in recent_metrics
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting metric history: {str(e)}")
            return []
    
    async def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_alerts = [
                alert for alert in self.alerts.values()
                if alert.triggered_at >= cutoff_time
            ]
            
            return [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "monitoring_type": alert.monitoring_type.value,
                    "source": alert.source,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "is_active": alert.is_active,
                    "actions_taken": alert.actions_taken
                } for alert in sorted(recent_alerts, key=lambda a: a.triggered_at, reverse=True)
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting alert history: {str(e)}")
            return []
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring system."""
        try:
            return {
                "is_monitoring": self.is_monitoring,
                "total_metrics": sum(len(metric_queue) for metric_queue in self.metrics.values()),
                "tracked_metric_types": len(self.metrics),
                "total_alerts": len(self.alerts),
                "active_alerts": len([a for a in self.alerts.values() if a.is_active]),
                "total_health_checks": len(self.health_checks),
                "healthy_checks": len([h for h in self.health_checks.values() if h.status == MonitoringStatus.HEALTHY]),
                "monitoring_types": [mt.value for mt in MonitoringType],
                "alert_severities": [asev.value for asev in AlertSeverity],
                "configured_thresholds": len(self.monitoring_config),
                "registered_alert_handlers": sum(len(handlers) for handlers in self.alert_handlers.values())
            }
        except Exception as e:
            self.logger.error(f"Error getting monitoring summary: {str(e)}")
            return {}