#!/usr/bin/env python3
"""
Platform Health Monitor - Enterprise Core Component
System-wide health monitoring and automated recovery system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive platform health monitoring including:
- System-wide health monitoring and alerting
- Performance metrics aggregation
- Predictive failure detection
- Automated recovery and self-healing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Recovery action types"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    FAILOVER = "failover"
    NOTIFY_ADMIN = "notify_admin"
    CUSTOM = "custom"


@dataclass
class HealthCheck:
    """Health check definition"""
    check_id: str
    name: str
    description: str
    target_service: str
    check_type: str  # http, tcp, command, custom
    parameters: Dict[str, Any] = field(default_factory=dict)
    interval_seconds: int = 30
    timeout_seconds: int = 10
    retry_count: int = 3
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class HealthResult:
    """Health check result"""
    check_id: str
    status: HealthStatus
    response_time_ms: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_count: int = 0


@dataclass
class SystemMetrics:
    """System performance metrics"""
    service_id: str
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_in_mbps: float
    network_out_mbps: float
    response_time_ms: float
    throughput_rps: float
    error_rate_percent: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    """System alert definition"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    source_service: str
    affected_services: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recovery_actions: List[RecoveryAction] = field(default_factory=list)
    acknowledged: bool = False
    resolved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


@dataclass
class RecoveryPlan:
    """Automated recovery plan"""
    plan_id: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    max_attempts: int = 3
    cooldown_minutes: int = 5
    enabled: bool = True
    last_executed: Optional[datetime] = None


class PlatformHealthMonitor:
    """
    Enterprise Platform Health Monitor
    
    Provides comprehensive system-wide health monitoring, performance metrics
    aggregation, predictive failure detection, and automated recovery with
    enterprise-grade reliability and self-healing capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_results: Dict[str, List[HealthResult]] = {}
        self.system_metrics: Dict[str, List[SystemMetrics]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        self.recovery_handlers: Dict[RecoveryAction, Callable] = {}
        self.alert_subscribers: List[Callable[[Alert], Awaitable[None]]] = []
        
        # Configuration
        self._check_interval = self.config.get('check_interval', 30)
        self._metrics_retention_hours = self.config.get('metrics_retention_hours', 168)  # 7 days
        self._alert_retention_days = self.config.get('alert_retention_days', 30)
        self._prediction_window_hours = self.config.get('prediction_window_hours', 4)
        self._recovery_enabled = self.config.get('recovery_enabled', True)
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._analysis_task: Optional[asyncio.Task] = None
        self._recovery_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Initialize default recovery handlers
        self._initialize_default_handlers()
        
        logger.info("Platform Health Monitor initialized")
    
    async def start(self) -> None:
        """Start the health monitor"""
        try:
            logger.info("Starting Platform Health Monitor...")
            
            # Initialize default health checks
            await self._initialize_default_checks()
            
            # Initialize default recovery plans
            await self._initialize_default_recovery_plans()
            
            # Start background tasks
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._analysis_task = asyncio.create_task(self._analysis_loop())
            self._recovery_task = asyncio.create_task(self._recovery_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Platform Health Monitor started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Platform Health Monitor: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the health monitor"""
        try:
            logger.info("Stopping Platform Health Monitor...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
            if self._analysis_task:
                self._analysis_task.cancel()
            if self._recovery_task:
                self._recovery_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            logger.info("Platform Health Monitor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Platform Health Monitor: {e}")
    
    # Health Check Management
    async def register_health_check(self, health_check: HealthCheck) -> bool:
        """Register a new health check"""
        try:
            self.health_checks[health_check.check_id] = health_check
            
            # Initialize results list
            if health_check.check_id not in self.health_results:
                self.health_results[health_check.check_id] = []
            
            logger.info(f"Health check registered: {health_check.check_id} for {health_check.target_service}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register health check {health_check.check_id}: {e}")
            return False
    
    async def unregister_health_check(self, check_id: str) -> bool:
        """Unregister a health check"""
        try:
            if check_id in self.health_checks:
                check = self.health_checks.pop(check_id)
                logger.info(f"Health check unregistered: {check_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister health check {check_id}: {e}")
            return False
    
    async def execute_health_check(self, check_id: str) -> Optional[HealthResult]:
        """Execute a specific health check"""
        try:
            check = self.health_checks.get(check_id)
            if not check or not check.enabled:
                return None
            
            start_time = datetime.utcnow()
            
            # Execute check based on type
            if check.check_type == "http":
                result = await self._execute_http_check(check)
            elif check.check_type == "tcp":
                result = await self._execute_tcp_check(check)
            elif check.check_type == "command":
                result = await self._execute_command_check(check)
            elif check.check_type == "custom":
                result = await self._execute_custom_check(check)
            else:
                result = HealthResult(
                    check_id=check_id,
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0.0,
                    message=f"Unknown check type: {check.check_type}"
                )
            
            # Calculate response time
            end_time = datetime.utcnow()
            result.response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Store result
            self.health_results[check_id].append(result)
            
            # Limit result history
            max_results = int(self._metrics_retention_hours * 3600 / check.interval_seconds)
            if len(self.health_results[check_id]) > max_results:
                self.health_results[check_id] = self.health_results[check_id][-max_results:]
            
            logger.debug(f"Health check executed: {check_id} - {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute health check {check_id}: {e}")
            return HealthResult(
                check_id=check_id,
                status=HealthStatus.CRITICAL,
                response_time_ms=0.0,
                message=f"Check execution failed: {e}"
            )
    
    # Metrics Collection
    async def record_system_metrics(self, metrics: SystemMetrics) -> bool:
        """Record system performance metrics"""
        try:
            if metrics.service_id not in self.system_metrics:
                self.system_metrics[metrics.service_id] = []
            
            self.system_metrics[metrics.service_id].append(metrics)
            
            # Limit metrics history
            max_metrics = int(self._metrics_retention_hours * 120)  # Every 30 seconds
            if len(self.system_metrics[metrics.service_id]) > max_metrics:
                self.system_metrics[metrics.service_id] = self.system_metrics[metrics.service_id][-max_metrics:]
            
            logger.debug(f"System metrics recorded for {metrics.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record system metrics for {metrics.service_id}: {e}")
            return False
    
    # Alert Management
    async def create_alert(self, alert: Alert) -> bool:
        """Create a new system alert"""
        try:
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Notify subscribers
            for subscriber in self.alert_subscribers:
                try:
                    await subscriber(alert)
                except Exception as e:
                    logger.error(f"Alert subscriber failed: {e}")
            
            logger.warning(f"Alert created: {alert.title} ({alert.severity.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create alert {alert.alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, resolution_message: Optional[str] = None) -> bool:
        """Resolve an active alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts.pop(alert_id)
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                if resolution_message:
                    alert.description += f" | Resolution: {resolution_message}"
                
                logger.info(f"Alert resolved: {alert.title}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    # Recovery Management
    async def register_recovery_plan(self, plan: RecoveryPlan) -> bool:
        """Register an automated recovery plan"""
        try:
            self.recovery_plans[plan.plan_id] = plan
            logger.info(f"Recovery plan registered: {plan.plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register recovery plan {plan.plan_id}: {e}")
            return False
    
    def register_recovery_handler(self, action: RecoveryAction, handler: Callable) -> None:
        """Register a recovery action handler"""
        self.recovery_handlers[action] = handler
        logger.info(f"Recovery handler registered for action: {action.value}")
    
    async def execute_recovery_action(self, action: RecoveryAction, service_id: str, parameters: Dict[str, Any] = None) -> bool:
        """Execute a recovery action"""
        try:
            if not self._recovery_enabled:
                logger.info(f"Recovery disabled, skipping action: {action.value}")
                return False
            
            handler = self.recovery_handlers.get(action)
            if not handler:
                logger.warning(f"No handler registered for recovery action: {action.value}")
                return False
            
            logger.info(f"Executing recovery action: {action.value} for service {service_id}")
            
            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(service_id, parameters or {})
            else:
                result = handler(service_id, parameters or {})
            
            if result:
                logger.info(f"Recovery action successful: {action.value}")
            else:
                logger.error(f"Recovery action failed: {action.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute recovery action {action.value}: {e}")
            return False
    
    # Status and Reports
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall platform health status"""
        try:
            health_summary = {
                "overall_status": HealthStatus.HEALTHY.value,
                "total_checks": len(self.health_checks),
                "healthy_checks": 0,
                "warning_checks": 0,
                "critical_checks": 0,
                "active_alerts": len(self.active_alerts),
                "services": {},
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Analyze recent health check results
            for check_id, check in self.health_checks.items():
                if not check.enabled:
                    continue
                
                results = self.health_results.get(check_id, [])
                if results:
                    latest_result = results[-1]
                    service_id = check.target_service
                    
                    if service_id not in health_summary["services"]:
                        health_summary["services"][service_id] = {
                            "status": HealthStatus.HEALTHY.value,
                            "checks": [],
                            "last_check": None
                        }
                    
                    check_info = {
                        "check_id": check_id,
                        "name": check.name,
                        "status": latest_result.status.value,
                        "response_time_ms": latest_result.response_time_ms,
                        "message": latest_result.message,
                        "timestamp": latest_result.timestamp.isoformat()
                    }
                    
                    health_summary["services"][service_id]["checks"].append(check_info)
                    
                    # Update service status to worst check status
                    if latest_result.status == HealthStatus.CRITICAL:
                        health_summary["services"][service_id]["status"] = HealthStatus.CRITICAL.value
                        health_summary["critical_checks"] += 1
                    elif latest_result.status == HealthStatus.WARNING and health_summary["services"][service_id]["status"] != HealthStatus.CRITICAL.value:
                        health_summary["services"][service_id]["status"] = HealthStatus.WARNING.value
                        health_summary["warning_checks"] += 1
                    elif latest_result.status == HealthStatus.HEALTHY:
                        health_summary["healthy_checks"] += 1
                    
                    # Update last check time
                    if not health_summary["services"][service_id]["last_check"] or latest_result.timestamp > datetime.fromisoformat(health_summary["services"][service_id]["last_check"]):
                        health_summary["services"][service_id]["last_check"] = latest_result.timestamp.isoformat()
            
            # Determine overall status
            if health_summary["critical_checks"] > 0:
                health_summary["overall_status"] = HealthStatus.CRITICAL.value
            elif health_summary["warning_checks"] > 0:
                health_summary["overall_status"] = HealthStatus.WARNING.value
            
            return health_summary
            
        except Exception as e:
            logger.error(f"Failed to get overall health: {e}")
            return {"error": str(e)}
    
    async def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """Get health status for a specific service"""
        try:
            service_health = {
                "service_id": service_id,
                "status": HealthStatus.UNKNOWN.value,
                "checks": [],
                "metrics": {},
                "alerts": []
            }
            
            # Collect health check results
            for check_id, check in self.health_checks.items():
                if check.target_service == service_id and check.enabled:
                    results = self.health_results.get(check_id, [])
                    if results:
                        latest_result = results[-1]
                        service_health["checks"].append({
                            "check_id": check_id,
                            "name": check.name,
                            "status": latest_result.status.value,
                            "response_time_ms": latest_result.response_time_ms,
                            "message": latest_result.message,
                            "timestamp": latest_result.timestamp.isoformat()
                        })
                        
                        # Update service status
                        if latest_result.status == HealthStatus.CRITICAL:
                            service_health["status"] = HealthStatus.CRITICAL.value
                        elif latest_result.status == HealthStatus.WARNING and service_health["status"] != HealthStatus.CRITICAL.value:
                            service_health["status"] = HealthStatus.WARNING.value
                        elif latest_result.status == HealthStatus.HEALTHY and service_health["status"] == HealthStatus.UNKNOWN.value:
                            service_health["status"] = HealthStatus.HEALTHY.value
            
            # Collect recent metrics
            metrics = self.system_metrics.get(service_id, [])
            if metrics:
                latest_metrics = metrics[-1]
                service_health["metrics"] = {
                    "cpu_usage_percent": latest_metrics.cpu_usage_percent,
                    "memory_usage_percent": latest_metrics.memory_usage_percent,
                    "disk_usage_percent": latest_metrics.disk_usage_percent,
                    "response_time_ms": latest_metrics.response_time_ms,
                    "throughput_rps": latest_metrics.throughput_rps,
                    "error_rate_percent": latest_metrics.error_rate_percent,
                    "timestamp": latest_metrics.timestamp.isoformat()
                }
            
            # Collect active alerts
            for alert in self.active_alerts.values():
                if service_id in alert.affected_services or alert.source_service == service_id:
                    service_health["alerts"].append({
                        "alert_id": alert.alert_id,
                        "title": alert.title,
                        "severity": alert.severity.value,
                        "created_at": alert.created_at.isoformat(),
                        "acknowledged": alert.acknowledged
                    })
            
            return service_health
            
        except Exception as e:
            logger.error(f"Failed to get service health for {service_id}: {e}")
            return {"error": str(e)}
    
    async def get_performance_trends(self, service_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends for a service"""
        try:
            metrics = self.system_metrics.get(service_id, [])
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_metrics = [m for m in metrics if m.timestamp > cutoff_time]
            
            if not recent_metrics:
                return {"service_id": service_id, "trends": {}, "message": "No metrics available"}
            
            trends = {
                "cpu_usage": {
                    "current": recent_metrics[-1].cpu_usage_percent,
                    "average": statistics.mean([m.cpu_usage_percent for m in recent_metrics]),
                    "max": max([m.cpu_usage_percent for m in recent_metrics]),
                    "trend": self._calculate_trend([m.cpu_usage_percent for m in recent_metrics])
                },
                "memory_usage": {
                    "current": recent_metrics[-1].memory_usage_percent,
                    "average": statistics.mean([m.memory_usage_percent for m in recent_metrics]),
                    "max": max([m.memory_usage_percent for m in recent_metrics]),
                    "trend": self._calculate_trend([m.memory_usage_percent for m in recent_metrics])
                },
                "response_time": {
                    "current": recent_metrics[-1].response_time_ms,
                    "average": statistics.mean([m.response_time_ms for m in recent_metrics]),
                    "max": max([m.response_time_ms for m in recent_metrics]),
                    "trend": self._calculate_trend([m.response_time_ms for m in recent_metrics])
                },
                "error_rate": {
                    "current": recent_metrics[-1].error_rate_percent,
                    "average": statistics.mean([m.error_rate_percent for m in recent_metrics]),
                    "max": max([m.error_rate_percent for m in recent_metrics]),
                    "trend": self._calculate_trend([m.error_rate_percent for m in recent_metrics])
                }
            }
            
            return {
                "service_id": service_id,
                "period_hours": hours,
                "data_points": len(recent_metrics),
                "trends": trends,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance trends for {service_id}: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"
        
        recent_values = values[-min(10, len(values)):]  # Last 10 values
        
        if len(recent_values) < 2:
            return "stable"
        
        # Simple trend calculation
        first_half = recent_values[:len(recent_values)//2]
        second_half = recent_values[len(recent_values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    # Alert Subscription
    def subscribe_to_alerts(self, callback: Callable[[Alert], Awaitable[None]]) -> None:
        """Subscribe to alert notifications"""
        self.alert_subscribers.append(callback)
        logger.info("New alert subscriber registered")
    
    def unsubscribe_from_alerts(self, callback: Callable[[Alert], Awaitable[None]]) -> None:
        """Unsubscribe from alert notifications"""
        try:
            self.alert_subscribers.remove(callback)
            logger.info("Alert subscriber removed")
        except ValueError:
            pass
    
    # Internal Methods
    def _initialize_default_handlers(self) -> None:
        """Initialize default recovery handlers"""
        
        async def restart_service_handler(service_id: str, parameters: Dict[str, Any]) -> bool:
            """Default restart service handler"""
            logger.info(f"[MOCK] Restarting service: {service_id}")
            await asyncio.sleep(1)  # Simulate restart time
            return True
        
        async def scale_up_handler(service_id: str, parameters: Dict[str, Any]) -> bool:
            """Default scale up handler"""
            instances = parameters.get('instances', 1)
            logger.info(f"[MOCK] Scaling up service {service_id} by {instances} instances")
            await asyncio.sleep(2)  # Simulate scaling time
            return True
        
        async def notify_admin_handler(service_id: str, parameters: Dict[str, Any]) -> bool:
            """Default admin notification handler"""
            logger.warning(f"[NOTIFICATION] Admin notified about issue with service: {service_id}")
            return True
        
        self.recovery_handlers[RecoveryAction.RESTART_SERVICE] = restart_service_handler
        self.recovery_handlers[RecoveryAction.SCALE_UP] = scale_up_handler
        self.recovery_handlers[RecoveryAction.NOTIFY_ADMIN] = notify_admin_handler
    
    async def _initialize_default_checks(self) -> None:
        """Initialize default health checks"""
        try:
            # Database health check
            db_check = HealthCheck(
                check_id="database_health",
                name="Database Health Check",
                description="Check database connectivity and performance",
                target_service="database_service",
                check_type="custom",
                parameters={"check_type": "database"},
                interval_seconds=60
            )
            
            await self.register_health_check(db_check)
            
            # API health check
            api_check = HealthCheck(
                check_id="api_health",
                name="API Health Check",
                description="Check API endpoints availability",
                target_service="api_service",
                check_type="http",
                parameters={"url": "http://api-service/health", "expected_status": 200},
                interval_seconds=30
            )
            
            await self.register_health_check(api_check)
            
            logger.info("Default health checks initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default health checks: {e}")
    
    async def _initialize_default_recovery_plans(self) -> None:
        """Initialize default recovery plans"""
        try:
            # High CPU recovery plan
            cpu_recovery = RecoveryPlan(
                plan_id="high_cpu_recovery",
                trigger_conditions={"cpu_usage_percent": {"gt": 90}},
                actions=[
                    {"action": RecoveryAction.SCALE_UP.value, "parameters": {"instances": 2}},
                    {"action": RecoveryAction.NOTIFY_ADMIN.value, "delay_minutes": 5}
                ],
                max_attempts=3,
                cooldown_minutes=10
            )
            
            await self.register_recovery_plan(cpu_recovery)
            
            # Service failure recovery plan
            failure_recovery = RecoveryPlan(
                plan_id="service_failure_recovery",
                trigger_conditions={"health_status": HealthStatus.CRITICAL.value},
                actions=[
                    {"action": RecoveryAction.RESTART_SERVICE.value},
                    {"action": RecoveryAction.NOTIFY_ADMIN.value, "delay_minutes": 2}
                ],
                max_attempts=2,
                cooldown_minutes=5
            )
            
            await self.register_recovery_plan(failure_recovery)
            
            logger.info("Default recovery plans initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default recovery plans: {e}")
    
    async def _execute_http_check(self, check: HealthCheck) -> HealthResult:
        """Execute HTTP health check"""
        try:
            # Mock HTTP check implementation
            url = check.parameters.get("url", "")
            expected_status = check.parameters.get("expected_status", 200)
            
            # Simulate HTTP request
            await asyncio.sleep(0.05)  # Simulate network delay
            
            # Mock random success/failure
            import random
            if random.random() > 0.1:  # 90% success rate
                return HealthResult(
                    check_id=check.check_id,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=50.0,
                    message=f"HTTP check successful: {url}",
                    details={"status_code": expected_status, "url": url}
                )
            else:
                return HealthResult(
                    check_id=check.check_id,
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    message=f"HTTP check failed: {url}",
                    details={"error": "Connection timeout", "url": url}
                )
            
        except Exception as e:
            return HealthResult(
                check_id=check.check_id,
                status=HealthStatus.CRITICAL,
                response_time_ms=0.0,
                message=f"HTTP check error: {e}"
            )
    
    async def _execute_tcp_check(self, check: HealthCheck) -> HealthResult:
        """Execute TCP health check"""
        try:
            host = check.parameters.get("host", "localhost")
            port = check.parameters.get("port", 80)
            
            # Mock TCP check
            await asyncio.sleep(0.01)
            
            return HealthResult(
                check_id=check.check_id,
                status=HealthStatus.HEALTHY,
                response_time_ms=10.0,
                message=f"TCP connection successful: {host}:{port}",
                details={"host": host, "port": port}
            )
            
        except Exception as e:
            return HealthResult(
                check_id=check.check_id,
                status=HealthStatus.CRITICAL,
                response_time_ms=0.0,
                message=f"TCP check error: {e}"
            )
    
    async def _execute_command_check(self, check: HealthCheck) -> HealthResult:
        """Execute command health check"""
        try:
            command = check.parameters.get("command", "echo 'healthy'")
            
            # Mock command execution
            await asyncio.sleep(0.1)
            
            return HealthResult(
                check_id=check.check_id,
                status=HealthStatus.HEALTHY,
                response_time_ms=100.0,
                message=f"Command executed successfully: {command}",
                details={"command": command, "exit_code": 0}
            )
            
        except Exception as e:
            return HealthResult(
                check_id=check.check_id,
                status=HealthStatus.CRITICAL,
                response_time_ms=0.0,
                message=f"Command check error: {e}"
            )
    
    async def _execute_custom_check(self, check: HealthCheck) -> HealthResult:
        """Execute custom health check"""
        try:
            check_type = check.parameters.get("check_type", "generic")
            
            # Mock custom check based on type
            if check_type == "database":
                import random
                if random.random() > 0.05:  # 95% success rate
                    return HealthResult(
                        check_id=check.check_id,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=25.0,
                        message="Database connection healthy",
                        details={"connections": 45, "max_connections": 100}
                    )
                else:
                    return HealthResult(
                        check_id=check.check_id,
                        status=HealthStatus.WARNING,
                        response_time_ms=150.0,
                        message="Database connection slow",
                        details={"connections": 85, "max_connections": 100}
                    )
            else:
                return HealthResult(
                    check_id=check.check_id,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=20.0,
                    message="Custom check successful"
                )
            
        except Exception as e:
            return HealthResult(
                check_id=check.check_id,
                status=HealthStatus.CRITICAL,
                response_time_ms=0.0,
                message=f"Custom check error: {e}"
            )
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Execute all enabled health checks
                check_tasks = []
                for check_id, check in self.health_checks.items():
                    if check.enabled:
                        task = asyncio.create_task(self.execute_health_check(check_id))
                        check_tasks.append(task)
                
                if check_tasks:
                    await asyncio.gather(*check_tasks, return_exceptions=True)
                
                await asyncio.sleep(self._check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(30)
    
    async def _analysis_loop(self) -> None:
        """Background analysis and alerting loop"""
        while not self._shutdown_event.is_set():
            try:
                # Analyze health results and generate alerts
                for check_id, results in self.health_results.items():
                    if not results:
                        continue
                    
                    latest_result = results[-1]
                    check = self.health_checks.get(check_id)
                    
                    if not check:
                        continue
                    
                    # Check for critical status
                    if latest_result.status == HealthStatus.CRITICAL:
                        alert_id = f"health_critical_{check_id}_{int(datetime.utcnow().timestamp())}"
                        alert = Alert(
                            alert_id=alert_id,
                            title=f"Health Check Critical: {check.name}",
                            description=latest_result.message,
                            severity=AlertSeverity.CRITICAL,
                            source_service=check.target_service,
                            affected_services=[check.target_service],
                            recovery_actions=[RecoveryAction.RESTART_SERVICE, RecoveryAction.NOTIFY_ADMIN]
                        )
                        
                        await self.create_alert(alert)
                
                # Analyze system metrics for performance alerts
                for service_id, metrics_list in self.system_metrics.items():
                    if not metrics_list:
                        continue
                    
                    latest_metrics = metrics_list[-1]
                    
                    # Check for high CPU usage
                    if latest_metrics.cpu_usage_percent > 90:
                        alert_id = f"cpu_high_{service_id}_{int(datetime.utcnow().timestamp())}"
                        alert = Alert(
                            alert_id=alert_id,
                            title=f"High CPU Usage: {service_id}",
                            description=f"CPU usage is {latest_metrics.cpu_usage_percent:.1f}%",
                            severity=AlertSeverity.WARNING,
                            source_service=service_id,
                            affected_services=[service_id],
                            metrics={"cpu_usage_percent": latest_metrics.cpu_usage_percent},
                            recovery_actions=[RecoveryAction.SCALE_UP]
                        )
                        
                        await self.create_alert(alert)
                
                await asyncio.sleep(60)  # Analyze every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
                await asyncio.sleep(60)
    
    async def _recovery_loop(self) -> None:
        """Background automated recovery loop"""
        while not self._shutdown_event.is_set():
            try:
                if not self._recovery_enabled:
                    await asyncio.sleep(60)
                    continue
                
                # Check for alerts that require recovery actions
                for alert in list(self.active_alerts.values()):
                    if alert.acknowledged or not alert.recovery_actions:
                        continue
                    
                    # Execute recovery actions
                    for action in alert.recovery_actions:
                        try:
                            await self.execute_recovery_action(action, alert.source_service)
                        except Exception as e:
                            logger.error(f"Recovery action failed for alert {alert.alert_id}: {e}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Recovery loop error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                # Clean up old alert history
                cutoff_time = current_time - timedelta(days=self._alert_retention_days)
                self.alert_history = [
                    alert for alert in self.alert_history
                    if alert.created_at > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(1800)  # 30 minutes
    
    # Context Manager Support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Factory function
def create_platform_health_monitor(config: Optional[Dict[str, Any]] = None) -> PlatformHealthMonitor:
    """Factory function to create a Platform Health Monitor"""
    return PlatformHealthMonitor(config)


# Example alert handler
async def alert_handler(alert: Alert) -> None:
    """Example alert handler"""
    logger.info(f"ALERT RECEIVED: {alert.title} - {alert.severity.value}")


# Example usage
async def main():
    """Example usage of Platform Health Monitor"""
    async with create_platform_health_monitor() as monitor:
        # Subscribe to alerts
        monitor.subscribe_to_alerts(alert_handler)
        
        # Register a custom health check
        custom_check = HealthCheck(
            check_id="custom_service_check",
            name="Custom Service Health",
            description="Check custom service availability",
            target_service="custom_service",
            check_type="http",
            parameters={"url": "http://custom-service/health", "expected_status": 200},
            interval_seconds=30
        )
        
        await monitor.register_health_check(custom_check)
        
        # Record some system metrics
        metrics = SystemMetrics(
            service_id="custom_service",
            cpu_usage_percent=75.0,
            memory_usage_percent=60.0,
            disk_usage_percent=45.0,
            network_in_mbps=10.5,
            network_out_mbps=8.2,
            response_time_ms=120.0,
            throughput_rps=50.0,
            error_rate_percent=0.1
        )
        
        await monitor.record_system_metrics(metrics)
        
        # Wait for monitoring to run
        await asyncio.sleep(5)
        
        # Get overall health
        health = await monitor.get_overall_health()
        print(f"Platform health: {json.dumps(health, indent=2, default=str)}")
        
        # Get service-specific health
        service_health = await monitor.get_service_health("custom_service")
        print(f"Custom service health: {json.dumps(service_health, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())