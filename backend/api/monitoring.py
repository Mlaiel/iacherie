"""Monitoring - API Metrics, Logging, Health
Consolidated monitoring functionality for API observability.

This module consolidates monitoring from:
- Health checks and system status monitoring
- Performance metrics and analytics
- Request/response logging and tracing
- Error tracking and alerting
- Real-time dashboard metrics
- System resource monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import time
import psutil
import asyncio
import json
import uuid
from collections import defaultdict, deque
import logging

from fastapi import FastAPI, Request, Response, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ========================================
# MONITORING ENUMS
# ========================================

class HealthStatus(str, Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ComponentType(str, Enum):
    """System component types"""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    FILE_STORAGE = "file_storage"
    MESSAGE_QUEUE = "message_queue"
    AI_ENGINE = "ai_engine"

# ========================================
# MONITORING MODELS
# ========================================

class HealthCheck(BaseModel):
    """Health check result model"""
    component: str = Field(..., description="Component name")
    status: HealthStatus = Field(..., description="Health status")
    response_time: float = Field(..., description="Response time in seconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    last_check: datetime = Field(default_factory=datetime.now, description="Last check timestamp")
    error: Optional[str] = Field(None, description="Error message if unhealthy")

class SystemMetrics(BaseModel):
    """System metrics model"""
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_io: Dict[str, int] = Field(default_factory=dict, description="Network I/O bytes")
    active_connections: int = Field(default=0, description="Active connections")
    request_rate: float = Field(default=0.0, description="Requests per second")
    error_rate: float = Field(default=0.0, description="Error rate percentage")

class APIMetrics(BaseModel):
    """API-specific metrics model"""
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    status_code: int = Field(..., description="HTTP status code")
    response_time: float = Field(..., description="Response time in seconds")
    request_size: int = Field(default=0, description="Request size in bytes")
    response_size: int = Field(default=0, description="Response size in bytes")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")

class Alert(BaseModel):
    """Alert model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Alert ID")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    severity: AlertSeverity = Field(..., description="Alert severity")
    component: str = Field(..., description="Affected component")
    created_at: datetime = Field(default_factory=datetime.now, description="Alert creation time")
    resolved_at: Optional[datetime] = Field(None, description="Alert resolution time")
    resolved: bool = Field(default=False, description="Is alert resolved")

# ========================================
# HEALTH CHECK MANAGER
# ========================================

class HealthCheckManager:
    """Manages health checks for different system components"""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_intervals: Dict[str, int] = {}  # component -> interval in seconds
        self.running_checks: Dict[str, bool] = {}
    
    def register_health_check(
        self, 
        component: str, 
        check_func: Callable, 
        interval: int = 60,
        component_type: ComponentType = ComponentType.EXTERNAL_API
    ):
        """Register a health check for a component"""
        self.check_intervals[component] = interval
        self.running_checks[component] = False
        
        # Run initial check
        asyncio.create_task(self._run_health_check(component, check_func))
    
    async def _run_health_check(self, component: str, check_func: Callable):
        """Run health check for a component"""
        start_time = time.time()
        
        try:
            # Run the health check function
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = time.time() - start_time
            
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "healthy"))
                details = result.get("details", {})
                error = result.get("error")
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                details = {}
                error = None if result else "Health check returned False"
            else:
                status = HealthStatus.HEALTHY
                details = {"result": str(result)}
                error = None
            
            self.health_checks[component] = HealthCheck(
                component=component,
                status=status,
                response_time=response_time,
                details=details,
                error=error
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.health_checks[component] = HealthCheck(
                component=component,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                error=str(e)
            )
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Mock database health check
            await asyncio.sleep(0.1)  # Simulate DB query
            return {
                "status": "healthy",
                "details": {
                    "connection_pool": "available",
                    "query_time": "< 100ms",
                    "active_connections": 5
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_cache_health(self) -> Dict[str, Any]:
        """Check cache (Redis) health"""
        try:
            # Mock Redis health check
            await asyncio.sleep(0.05)
            return {
                "status": "healthy",
                "details": {
                    "memory_usage": "45%",
                    "connected_clients": 12,
                    "response_time": "< 10ms"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_ai_engine_health(self) -> Dict[str, Any]:
        """Check AI engine health"""
        try:
            # Mock AI engine health check
            await asyncio.sleep(0.2)
            return {
                "status": "healthy",
                "details": {
                    "model_status": "loaded",
                    "gpu_memory": "60%",
                    "inference_queue": 3
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        if not self.health_checks:
            return {
                "status": "unknown",
                "message": "No health checks registered"
            }
        
        statuses = [check.status for check in self.health_checks.values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(status == HealthStatus.CRITICAL for status in statuses):
            overall_status = HealthStatus.CRITICAL
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "components": {
                component: {
                    "status": check.status.value,
                    "response_time": check.response_time,
                    "last_check": check.last_check.isoformat(),
                    "error": check.error
                }
                for component, check in self.health_checks.items()
            },
            "timestamp": datetime.now().isoformat()
        }

# ========================================
# METRICS COLLECTOR
# ========================================

class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Prometheus metrics
        self.request_counter = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
        self.active_connections = Gauge('api_active_connections', 'Active API connections')
        self.system_cpu = Gauge('system_cpu_usage_percent', 'System CPU usage')
        self.system_memory = Gauge('system_memory_usage_percent', 'System memory usage')
        self.system_disk = Gauge('system_disk_usage_percent', 'System disk usage')
    
    async def record_api_request(self, metrics: APIMetrics):
        """Record API request metrics"""
        # Update Prometheus metrics
        self.request_counter.labels(
            method=metrics.method,
            endpoint=metrics.endpoint,
            status=str(metrics.status_code)
        ).inc()
        
        self.request_duration.labels(
            method=metrics.method,
            endpoint=metrics.endpoint
        ).observe(metrics.response_time)
        
        # Store in buffer for real-time analytics
        key = f"{metrics.method}:{metrics.endpoint}"
        self.metrics_buffer[key].append(metrics.dict())
        
        # Store in Redis for persistence
        if self.redis:
            await self.redis.lpush(
                f"api_metrics:{datetime.now().strftime('%Y-%m-%d')}",
                json.dumps(metrics.dict(), default=str)
            )
            await self.redis.expire(
                f"api_metrics:{datetime.now().strftime('%Y-%m-%d')}",
                86400 * 7  # Keep for 7 days
            )
    
    async def record_system_metrics(self):
        """Record system-level metrics"""
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Update Prometheus metrics
        self.system_cpu.set(cpu_percent)
        self.system_memory.set(memory.percent)
        self.system_disk.set(disk.percent)
        
        # Create system metrics object
        system_metrics = SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=(disk.used / disk.total) * 100,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        )
        
        # Store in buffer
        self.metrics_buffer["system"].append(system_metrics.dict())
        
        # Store in Redis
        if self.redis:
            await self.redis.set(
                "system_metrics:current",
                json.dumps(system_metrics.dict(), default=str),
                ex=300  # Expire in 5 minutes
            )
    
    def get_metrics_summary(self, component: str = None, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary"""
        if component and component in self.metrics_buffer:
            metrics_data = list(self.metrics_buffer[component])
        else:
            # Aggregate all metrics
            metrics_data = []
            for key, data in self.metrics_buffer.items():
                metrics_data.extend(list(data))
        
        if not metrics_data:
            return {"message": "No metrics data available"}
        
        # Calculate summary statistics
        if component == "system":
            return self._summarize_system_metrics(metrics_data)
        else:
            return self._summarize_api_metrics(metrics_data)
    
    def _summarize_system_metrics(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize system metrics"""
        if not metrics_data:
            return {}
        
        cpu_values = [m["cpu_usage"] for m in metrics_data]
        memory_values = [m["memory_usage"] for m in metrics_data]
        
        return {
            "cpu": {
                "average": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "average": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "sample_count": len(metrics_data)
        }
    
    def _summarize_api_metrics(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize API metrics"""
        if not metrics_data:
            return {}
        
        response_times = [m["response_time"] for m in metrics_data]
        status_codes = [m["status_code"] for m in metrics_data]
        
        return {
            "total_requests": len(metrics_data),
            "response_time": {
                "average": sum(response_times) / len(response_times),
                "max": max(response_times),
                "min": min(response_times),
                "p95": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
            },
            "status_codes": {
                str(code): status_codes.count(code) for code in set(status_codes)
            },
            "error_rate": len([code for code in status_codes if code >= 400]) / len(status_codes) * 100
        }

# ========================================
# ALERT MANAGER
# ========================================

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_handlers: List[Callable] = []
    
    def add_alert_rule(
        self, 
        name: str, 
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        component: str,
        description: str
    ):
        """Add alert rule"""
        self.alert_rules.append({
            "name": name,
            "condition": condition,
            "severity": severity,
            "component": component,
            "description": description
        })
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against alert rules"""
        for rule in self.alert_rules:
            try:
                if rule["condition"](metrics):
                    await self._trigger_alert(
                        title=rule["name"],
                        description=rule["description"],
                        severity=rule["severity"],
                        component=rule["component"]
                    )
            except Exception as e:
                print(f"Error checking alert rule {rule['name']}: {e}")
    
    async def _trigger_alert(self, title: str, description: str, severity: AlertSeverity, component: str):
        """Trigger an alert"""
        alert_id = f"{component}:{title}".lower().replace(" ", "_")
        
        # Check if alert already exists and is unresolved
        if alert_id in self.alerts and not self.alerts[alert_id].resolved:
            return  # Don't create duplicate alerts
        
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            component=component
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                print(f"Error sending alert notification: {e}")
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alerts.values()
            if alert.created_at >= cutoff_time
        ]

# ========================================
# MONITORING MIDDLEWARE
# ========================================

class MonitoringMiddleware:
    """Middleware for collecting monitoring data"""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
    
    async def __call__(self, request: Request, call_next):
        """Collect metrics for each request"""
        start_time = time.time()
        
        # Get request size
        request_size = 0
        if hasattr(request, "body"):
            try:
                body = await request.body()
                request_size = len(body)
            except:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Get response size
        response_size = 0
        if hasattr(response, "body"):
            try:
                response_size = len(response.body)
            except:
                pass
        
        # Extract user ID if available
        user_id = None
        if hasattr(request.state, "user"):
            user_id = getattr(request.state.user, "id", None)
        
        # Create metrics object
        api_metrics = APIMetrics(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time=response_time,
            request_size=request_size,
            response_size=response_size,
            user_id=user_id
        )
        
        # Record metrics
        await self.metrics_collector.record_api_request(api_metrics)
        
        return response

# ========================================
# MONITORING ENDPOINTS
# ========================================

class MonitoringEndpoints:
    """Monitoring and health check endpoints"""
    
    def __init__(
        self, 
        health_manager: HealthCheckManager,
        metrics_collector: MetricsCollector,
        alert_manager: AlertManager
    ):
        self.health_manager = health_manager
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
    
    async def health_check(self) -> JSONResponse:
        """Health check endpoint"""
        health_status = self.health_manager.get_overall_health()
        
        status_code = 200
        if health_status["status"] in ["unhealthy", "critical"]:
            status_code = 503
        elif health_status["status"] == "degraded":
            status_code = 200  # Still serving requests
        
        return JSONResponse(content=health_status, status_code=status_code)
    
    async def detailed_health(self) -> Dict[str, Any]:
        """Detailed health check with all components"""
        return self.health_manager.get_overall_health()
    
    async def metrics_summary(self, component: str = None, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary"""
        return self.metrics_collector.get_metrics_summary(component, hours)
    
    async def system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        await self.metrics_collector.record_system_metrics()
        return self.metrics_collector.get_metrics_summary("system", 1)
    
    async def prometheus_metrics(self) -> Response:
        """Prometheus metrics endpoint"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    async def active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        alerts = self.alert_manager.get_active_alerts()
        return [alert.dict() for alert in alerts]
    
    async def alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history"""
        alerts = self.alert_manager.get_alert_history(hours)
        return [alert.dict() for alert in alerts]

# ========================================
# MONITORING SERVICE
# ========================================

class MonitoringService:
    """Main monitoring service"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.health_manager = HealthCheckManager()
        self.metrics_collector = MetricsCollector(redis_client)
        self.alert_manager = AlertManager()
        self.middleware = MonitoringMiddleware(self.metrics_collector, self.alert_manager)
        self.endpoints = MonitoringEndpoints(
            self.health_manager,
            self.metrics_collector, 
            self.alert_manager
        )
        
        self._setup_default_health_checks()
        self._setup_default_alert_rules()
    
    def _setup_default_health_checks(self):
        """Setup default health checks"""
        self.health_manager.register_health_check(
            "database",
            self.health_manager.check_database_health,
            interval=30
        )
        
        self.health_manager.register_health_check(
            "cache",
            self.health_manager.check_cache_health,
            interval=30
        )
        
        self.health_manager.register_health_check(
            "ai_engine",
            self.health_manager.check_ai_engine_health,
            interval=60
        )
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        # High CPU usage alert
        self.alert_manager.add_alert_rule(
            name="High CPU Usage",
            condition=lambda metrics: metrics.get("cpu", {}).get("average", 0) > 80,
            severity=AlertSeverity.WARNING,
            component="system",
            description="System CPU usage is above 80%"
        )
        
        # High memory usage alert
        self.alert_manager.add_alert_rule(
            name="High Memory Usage",
            condition=lambda metrics: metrics.get("memory", {}).get("average", 0) > 90,
            severity=AlertSeverity.CRITICAL,
            component="system",
            description="System memory usage is above 90%"
        )
        
        # High error rate alert
        self.alert_manager.add_alert_rule(
            name="High Error Rate",
            condition=lambda metrics: metrics.get("error_rate", 0) > 5,
            severity=AlertSeverity.ERROR,
            component="api",
            description="API error rate is above 5%"
        )
    
    def setup_monitoring(self, app: FastAPI):
        """Setup monitoring for FastAPI app"""
        # Add middleware
        app.middleware("http")(self.middleware)
        
        # Add monitoring endpoints
        app.add_api_route("/health", self.endpoints.health_check, methods=["GET"])
        app.add_api_route("/health/detailed", self.endpoints.detailed_health, methods=["GET"])
        app.add_api_route("/metrics", self.endpoints.prometheus_metrics, methods=["GET"])
        app.add_api_route("/api/v1/monitoring/metrics", self.endpoints.metrics_summary, methods=["GET"])
        app.add_api_route("/api/v1/monitoring/system", self.endpoints.system_metrics, methods=["GET"])
        app.add_api_route("/api/v1/monitoring/alerts", self.endpoints.active_alerts, methods=["GET"])
        app.add_api_route("/api/v1/monitoring/alerts/history", self.endpoints.alert_history, methods=["GET"])
        
        # Start background tasks
        asyncio.create_task(self._background_monitoring())
    
    async def _background_monitoring(self):
        """Background monitoring tasks"""
        while True:
            try:
                # Record system metrics
                await self.metrics_collector.record_system_metrics()
                
                # Check alerts
                system_metrics = self.metrics_collector.get_metrics_summary("system", 1)
                api_metrics = self.metrics_collector.get_metrics_summary("api", 1)
                
                combined_metrics = {**system_metrics, **api_metrics}
                await self.alert_manager.check_alerts(combined_metrics)
                
                # Sleep for 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Error in background monitoring: {e}")
                await asyncio.sleep(60)

# ========================================
# EXPORTS
# ========================================

__all__ = [
    "HealthStatus",
    "MetricType",
    "AlertSeverity",
    "ComponentType",
    "HealthCheck",
    "SystemMetrics",
    "APIMetrics",
    "Alert",
    "HealthCheckManager",
    "MetricsCollector",
    "AlertManager",
    "MonitoringMiddleware",
    "MonitoringEndpoints",
    "MonitoringService"
]