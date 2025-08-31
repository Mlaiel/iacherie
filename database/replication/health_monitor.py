"""Replication Health Monitor - IA Influencer Agent Platform

Comprehensive health monitoring and alerting system for database replication.
Tracks performance metrics, detects issues, and triggers automated recovery
for the content creator platform's multi-database infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics
import json


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthMetric:
    """Health metric data point"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthAlert:
    """Health alert record"""
    id: str
    severity: AlertSeverity
    component: str
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentHealth:
    """Component health status"""
    component_name: str
    status: HealthStatus
    last_check: datetime
    metrics: Dict[str, HealthMetric]
    alerts: List[HealthAlert]
    uptime_percentage: float = 100.0
    error_count: int = 0


class ReplicationHealthMonitor:
    """
    Comprehensive health monitoring system for database replication.
    
    Monitors performance metrics, detects anomalies, generates alerts,
    and provides health dashboards for the content creator platform's
    replication infrastructure.
    """
    
    def __init__(self, config):
        """Initialize health monitor"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReplicationHealthMonitor")
        
        # Component registry
        self.components: Dict[str, ComponentHealth] = {}
        self.handlers: Dict[str, Any] = {}
        
        # Alert management
        self.active_alerts: List[HealthAlert] = []
        self.alert_history: List[HealthAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_interval = config.health_check_interval
        
        # Health thresholds
        self.thresholds = {
            "replication_lag": {
                "warning": config.lag_threshold / 1000,  # Convert to seconds
                "critical": config.lag_threshold / 1000 * 2
            },
            "error_rate": {
                "warning": 0.01,  # 1%
                "critical": 0.05  # 5%
            },
            "connection_failure_rate": {
                "warning": 0.05,  # 5%
                "critical": 0.10  # 10%
            },
            "disk_usage": {
                "warning": 0.80,  # 80%
                "critical": 0.90  # 90%
            },
            "memory_usage": {
                "warning": 0.80,  # 80%
                "critical": 0.90  # 90%
            },
            "cpu_usage": {
                "warning": 0.80,  # 80%
                "critical": 0.90  # 90%
            }
        }
        
        # Statistics
        self.health_statistics = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "alerts_generated": 0,
            "alerts_resolved": 0
        }
        
        self.logger.info("ReplicationHealthMonitor initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize health monitor.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing replication health monitor...")
            
            # Initialize component health tracking
            await self._initialize_component_tracking()
            
            self.logger.info("Replication health monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize health monitor: {e}")
            return False
    
    def register_handler(self, database_type: str, handler: Any) -> None:
        """
        Register database handler for monitoring.
        
        Args:
            database_type: Type of database
            handler: Handler instance
        """
        self.handlers[database_type] = handler
        
        # Initialize component health
        self.components[database_type] = ComponentHealth(
            component_name=database_type,
            status=HealthStatus.UNKNOWN,
            last_check=datetime.utcnow(),
            metrics={},
            alerts=[]
        )
        
        self.logger.debug(f"Registered handler for monitoring: {database_type}")
    
    def register_alert_callback(self, callback: Callable[[HealthAlert], None]) -> None:
        """
        Register callback for alert notifications.
        
        Args:
            callback: Alert callback function
        """
        self.alert_callbacks.append(callback)
        self.logger.debug("Alert callback registered")
    
    async def _initialize_component_tracking(self) -> None:
        """Initialize health tracking for all components"""
        # Default components to monitor
        default_components = ["postgresql", "redis", "mongodb", "elasticsearch", "vector_store"]
        
        for component in default_components:
            if component not in self.components:
                self.components[component] = ComponentHealth(
                    component_name=component,
                    status=HealthStatus.UNKNOWN,
                    last_check=datetime.utcnow(),
                    metrics={},
                    alerts=[]
                )
        
        self.logger.debug(f"Initialized tracking for {len(self.components)} components")
    
    async def start_monitoring(self) -> None:
        """Start health monitoring"""
        if self.is_monitoring:
            self.logger.warning("Health monitoring is already running")
            return
        
        self.is_monitoring = True
        
        # Start monitoring tasks
        monitoring_tasks = [
            self._health_check_loop(),
            self._alert_processing_loop(),
            self._metrics_collection_loop(),
            self._uptime_calculation_loop()
        ]
        
        for task in monitoring_tasks:
            asyncio.create_task(task)
        
        self.logger.info("Health monitoring started")
    
    async def _health_check_loop(self) -> None:
        """Main health check loop"""
        while self.is_monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def _alert_processing_loop(self) -> None:
        """Alert processing and notification loop"""
        while self.is_monitoring:
            try:
                await self._process_alerts()
                await asyncio.sleep(5)  # Check alerts every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_collection_loop(self) -> None:
        """Metrics collection loop"""
        while self.is_monitoring:
            try:
                await self._collect_detailed_metrics()
                await asyncio.sleep(self.config.get("metrics_collection_interval", 60))
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(30)
    
    async def _uptime_calculation_loop(self) -> None:
        """Uptime calculation loop"""
        while self.is_monitoring:
            try:
                await self._calculate_uptime_percentages()
                await asyncio.sleep(300)  # Calculate every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in uptime calculation loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all components"""
        for component_name, component in self.components.items():
            try:
                self.health_statistics["total_checks"] += 1
                
                # Get handler for this component
                handler = self.handlers.get(component_name)
                if not handler:
                    component.status = HealthStatus.UNKNOWN
                    continue
                
                # Perform health check
                health_result = await handler.check_health()
                
                # Update component health
                await self._update_component_health(component_name, health_result)
                
                self.health_statistics["successful_checks"] += 1
                
            except Exception as e:
                self.logger.error(f"Health check failed for {component_name}: {e}")
                component.status = HealthStatus.CRITICAL
                component.error_count += 1
                self.health_statistics["failed_checks"] += 1
                
                # Generate alert for failed health check
                await self._generate_alert(
                    component_name,
                    AlertSeverity.CRITICAL,
                    f"Health check failed: {e}",
                    "health_check_failure",
                    1.0,
                    0.0
                )
            
            component.last_check = datetime.utcnow()
    
    async def _update_component_health(self, component_name: str, health_result: Dict[str, Any]) -> None:
        """Update component health based on check result"""
        component = self.components[component_name]
        
        # Update overall status
        if health_result.get("healthy", False):
            component.status = HealthStatus.HEALTHY
        else:
            issues = health_result.get("issues", [])
            if any("critical" in issue.lower() for issue in issues):
                component.status = HealthStatus.CRITICAL
            else:
                component.status = HealthStatus.WARNING
        
        # Update metrics
        metrics_data = health_result.get("metrics", {})
        for metric_name, metric_value in metrics_data.items():
            if isinstance(metric_value, dict):
                value = metric_value.get("value", 0)
                unit = metric_value.get("unit", "")
            else:
                value = metric_value
                unit = ""
            
            metric = HealthMetric(
                name=metric_name,
                value=float(value),
                unit=unit,
                timestamp=datetime.utcnow()
            )
            
            # Add thresholds if available
            if metric_name in self.thresholds:
                metric.threshold_warning = self.thresholds[metric_name].get("warning")
                metric.threshold_critical = self.thresholds[metric_name].get("critical")
            
            component.metrics[metric_name] = metric
            
            # Check for threshold violations
            await self._check_metric_thresholds(component_name, metric)
    
    async def _check_metric_thresholds(self, component_name: str, metric: HealthMetric) -> None:
        """Check if metric violates thresholds and generate alerts"""
        if metric.threshold_critical and metric.value >= metric.threshold_critical:
            await self._generate_alert(
                component_name,
                AlertSeverity.CRITICAL,
                f"{metric.name} is critical: {metric.value}{metric.unit} >= {metric.threshold_critical}{metric.unit}",
                metric.name,
                metric.value,
                metric.threshold_critical
            )
        elif metric.threshold_warning and metric.value >= metric.threshold_warning:
            await self._generate_alert(
                component_name,
                AlertSeverity.WARNING,
                f"{metric.name} is high: {metric.value}{metric.unit} >= {metric.threshold_warning}{metric.unit}",
                metric.name,
                metric.value,
                metric.threshold_warning
            )
    
    async def _generate_alert(
        self,
        component: str,
        severity: AlertSeverity,
        message: str,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Generate health alert"""
        try:
            alert = HealthAlert(
                id=f"alert_{component}_{metric_name}_{int(datetime.utcnow().timestamp())}",
                severity=severity,
                component=component,
                message=message,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Check for duplicate alerts
            duplicate = any(
                a.component == alert.component and 
                a.metric_name == alert.metric_name and 
                a.severity == alert.severity and
                not a.resolved
                for a in self.active_alerts
            )
            
            if not duplicate:
                self.active_alerts.append(alert)
                self.alert_history.append(alert)
                self.health_statistics["alerts_generated"] += 1
                
                # Add alert to component
                if component in self.components:
                    self.components[component].alerts.append(alert)
                
                self.logger.warning(f"Generated {severity.value} alert for {component}: {message}")
                
                # Notify callbacks
                for callback in self.alert_callbacks:
                    try:
                        await callback(alert)
                    except Exception as e:
                        self.logger.error(f"Error calling alert callback: {e}")
            
        except Exception as e:
            self.logger.error(f"Error generating alert: {e}")
    
    async def _process_alerts(self) -> None:
        """Process and resolve alerts"""
        for alert in self.active_alerts.copy():
            try:
                # Check if alert should be auto-resolved
                if await self._should_resolve_alert(alert):
                    await self._resolve_alert(alert)
                
            except Exception as e:
                self.logger.error(f"Error processing alert {alert.id}: {e}")
    
    async def _should_resolve_alert(self, alert: HealthAlert) -> bool:
        """Check if alert should be automatically resolved"""
        try:
            component = self.components.get(alert.component)
            if not component:
                return False
            
            # Check if metric is back to normal
            metric = component.metrics.get(alert.metric_name)
            if not metric:
                return False
            
            # Alert should be resolved if value is below warning threshold
            if alert.severity == AlertSeverity.CRITICAL:
                return metric.value < (metric.threshold_warning or alert.threshold_value)
            elif alert.severity == AlertSeverity.WARNING:
                return metric.value < alert.threshold_value
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking alert resolution: {e}")
            return False
    
    async def _resolve_alert(self, alert: HealthAlert) -> None:
        """Resolve alert"""
        try:
            alert.resolved = True
            alert.resolution_time = datetime.utcnow()
            
            # Remove from active alerts
            if alert in self.active_alerts:
                self.active_alerts.remove(alert)
            
            self.health_statistics["alerts_resolved"] += 1
            
            self.logger.info(f"Resolved alert {alert.id} for {alert.component}")
            
        except Exception as e:
            self.logger.error(f"Error resolving alert {alert.id}: {e}")
    
    async def _collect_detailed_metrics(self) -> None:
        """Collect detailed metrics from all handlers"""
        for component_name, handler in self.handlers.items():
            try:
                metrics = await handler.get_replication_metrics()
                
                # Store detailed metrics
                for metric_name, value in metrics.items():
                    if isinstance(value, (int, float)):
                        metric = HealthMetric(
                            name=f"detailed_{metric_name}",
                            value=float(value),
                            unit="",
                            timestamp=datetime.utcnow()
                        )
                        self.components[component_name].metrics[metric.name] = metric
                
            except Exception as e:
                self.logger.error(f"Error collecting detailed metrics for {component_name}: {e}")
    
    async def _calculate_uptime_percentages(self) -> None:
        """Calculate uptime percentages for components"""
        window = timedelta(hours=24)  # 24-hour window
        current_time = datetime.utcnow()
        
        for component in self.components.values():
            try:
                # Count health checks in the window
                total_checks = 0
                successful_checks = 0
                
                # This would ideally use stored health check history
                # For now, we'll use a simplified calculation
                if component.status == HealthStatus.HEALTHY:
                    component.uptime_percentage = max(0, min(100, 100 - component.error_count))
                elif component.status == HealthStatus.WARNING:
                    component.uptime_percentage = max(0, min(100, 90 - component.error_count))
                else:
                    component.uptime_percentage = max(0, min(100, 50 - component.error_count))
                
            except Exception as e:
                self.logger.error(f"Error calculating uptime for {component.component_name}: {e}")
    
    async def check_all_connections(self) -> bool:
        """
        Check all database connections.
        
        Returns:
            bool: True if all connections are healthy
        """
        try:
            all_healthy = True
            
            for component_name, handler in self.handlers.items():
                try:
                    health = await handler.check_health()
                    if not health.get("healthy", False):
                        all_healthy = False
                        self.logger.warning(f"Connection unhealthy for {component_name}")
                        
                except Exception as e:
                    all_healthy = False
                    self.logger.error(f"Error checking connection for {component_name}: {e}")
            
            return all_healthy
            
        except Exception as e:
            self.logger.error(f"Error checking all connections: {e}")
            return False
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Dict containing health status for all components
        """
        health_status = {}
        
        for component_name, component in self.components.items():
            try:
                # Get latest metrics
                handler = self.handlers.get(component_name)
                if handler:
                    health_result = await handler.check_health()
                    await self._update_component_health(component_name, health_result)
                
                # Compile status
                health_status[component_name] = {
                    "status": component.status.value,
                    "last_check": component.last_check.isoformat(),
                    "uptime_percentage": component.uptime_percentage,
                    "error_count": component.error_count,
                    "active_alerts": len([a for a in component.alerts if not a.resolved]),
                    "requires_failover": component.status == HealthStatus.CRITICAL,
                    "metrics": {
                        name: {
                            "value": metric.value,
                            "unit": metric.unit,
                            "timestamp": metric.timestamp.isoformat()
                        }
                        for name, metric in component.metrics.items()
                    }
                }
                
            except Exception as e:
                health_status[component_name] = {
                    "status": "error",
                    "error": str(e),
                    "requires_failover": True
                }
        
        return health_status
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """
        Get overall system health summary.
        
        Returns:
            Dict containing overall health information
        """
        try:
            healthy_components = sum(1 for c in self.components.values() if c.status == HealthStatus.HEALTHY)
            total_components = len(self.components)
            
            overall_status = HealthStatus.HEALTHY
            if healthy_components == 0:
                overall_status = HealthStatus.CRITICAL
            elif healthy_components < total_components:
                overall_status = HealthStatus.WARNING
            
            return {
                "overall_status": overall_status.value,
                "healthy_components": healthy_components,
                "total_components": total_components,
                "health_percentage": (healthy_components / max(1, total_components)) * 100,
                "active_alerts": len(self.active_alerts),
                "critical_alerts": len([a for a in self.active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "statistics": self.health_statistics.copy(),
                "monitoring_active": self.is_monitoring,
                "last_check": max(
                    (c.last_check for c in self.components.values()),
                    default=datetime.min
                ).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting overall health: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "monitoring_active": self.is_monitoring
            }
    
    async def get_component_health(self, component_name: str) -> Dict[str, Any]:
        """
        Get detailed health information for specific component.
        
        Args:
            component_name: Name of component
            
        Returns:
            Dict containing component health details
        """
        component = self.components.get(component_name)
        if not component:
            return {"error": f"Component {component_name} not found"}
        
        return {
            "component_name": component.component_name,
            "status": component.status.value,
            "last_check": component.last_check.isoformat(),
            "uptime_percentage": component.uptime_percentage,
            "error_count": component.error_count,
            "metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "threshold_warning": metric.threshold_warning,
                    "threshold_critical": metric.threshold_critical
                }
                for name, metric in component.metrics.items()
            },
            "alerts": [
                {
                    "id": alert.id,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "resolution_time": alert.resolution_time.isoformat() if alert.resolution_time else None
                }
                for alert in component.alerts[-10:]  # Last 10 alerts
            ]
        }
    
    async def shutdown(self) -> None:
        """Shutdown health monitor"""
        try:
            self.logger.info("Shutting down health monitor...")
            
            self.is_monitoring = False
            
            # Resolve all active alerts
            for alert in self.active_alerts:
                alert.resolved = True
                alert.resolution_time = datetime.utcnow()
            
            # Clear state
            self.active_alerts.clear()
            self.alert_callbacks.clear()
            self.handlers.clear()
            
            self.logger.info("Health monitor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during health monitor shutdown: {e}")
            raise
