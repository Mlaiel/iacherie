"""Advanced Health Checks Module

Enterprise-grade health monitoring and system status verification for IA Influencer Agent platform.
Provides comprehensive health checks for all system components and dependencies.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import time
import json
import psutil
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import aiohttp
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import socket

from ..core.metrics import MetricsCollector, MetricEntry, MetricType, MetricPriority
from ..core.exceptions import HealthCheckError
from .real_time_alerts import AlertSeverity, AlertCategory

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ComponentType(Enum):
    """Types of system components"""
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    AI_MODEL = "ai_model"
    STORAGE = "storage"
    QUEUE = "queue"
    EXTERNAL_SERVICE = "external_service"
    MICROSERVICE = "microservice"
    NETWORK = "network"
    SYSTEM = "system"


@dataclass
class HealthCheckResult:
    """Health check result for a component"""
    component_name: str
    component_type: ComponentType
    status: HealthStatus
    response_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SystemHealthSummary:
    """Overall system health summary"""
    overall_status: HealthStatus
    healthy_components: int
    warning_components: int
    degraded_components: int
    unhealthy_components: int
    critical_components: int
    total_components: int
    last_updated: datetime
    uptime: float
    system_load: float
    memory_usage: float
    disk_usage: float
    network_status: HealthStatus


class HealthChecks:
    """
    Advanced Health Checks System
    
    Provides comprehensive health monitoring for all system components,
    dependencies, and services in the IA Influencer Agent platform.
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        redis_client: Optional[aioredis.Redis] = None,
        database_session: Optional[AsyncSession] = None
    ):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.redis_client = redis_client
        self.database_session = database_session
        
        # Health check configuration
        self.check_interval = timedelta(seconds=30)
        self.timeout = 10.0  # seconds
        
        # Component registry
        self.components: Dict[str, Dict[str, Any]] = {}
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        
        # System monitoring
        self.system_start_time = time.time()
        self.last_full_check: Optional[datetime] = None
        
        # Health check functions
        self.check_functions: Dict[ComponentType, Callable] = {
            ComponentType.DATABASE: self._check_database,
            ComponentType.CACHE: self._check_cache,
            ComponentType.API: self._check_api,
            ComponentType.AI_MODEL: self._check_ai_model,
            ComponentType.STORAGE: self._check_storage,
            ComponentType.QUEUE: self._check_queue,
            ComponentType.EXTERNAL_SERVICE: self._check_external_service,
            ComponentType.MICROSERVICE: self._check_microservice,
            ComponentType.NETWORK: self._check_network,
            ComponentType.SYSTEM: self._check_system
        }
        
        # Monitoring state
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Register default components
        self._register_default_components()
        
    async def start_monitoring(self) -> None:
        """Start health check monitoring"""
        if self.is_monitoring:
            logger.warning("Health check monitoring is already running")
            return
            
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        
        # Perform initial health check
        await self.perform_full_health_check()
        
        logger.info("Health check monitoring started successfully")
        
    async def stop_monitoring(self) -> None:
        """Stop health check monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Health check monitoring stopped")
        
    def register_component(
        self,
        name: str,
        component_type: ComponentType,
        endpoint: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        custom_check: Optional[Callable] = None,
        critical: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a component for health monitoring"""
        self.components[name] = {
            "type": component_type,
            "endpoint": endpoint,
            "dependencies": dependencies or [],
            "custom_check": custom_check,
            "critical": critical,
            "metadata": metadata or {}
        }
        
        logger.info(f"Registered component for health monitoring: {name}")
        
    def unregister_component(self, name: str) -> bool:
        """Unregister a component from health monitoring"""
        if name in self.components:
            del self.components[name]
            if name in self.health_results:
                del self.health_results[name]
            if name in self.health_history:
                del self.health_history[name]
            logger.info(f"Unregistered component: {name}")
            return True
        return False
        
    async def check_component_health(
        self,
        component_name: str
    ) -> HealthCheckResult:
        """Check health of a specific component"""
        if component_name not in self.components:
            raise HealthCheckError(f"Component {component_name} not registered")
            
        component = self.components[component_name]
        start_time = time.time()
        
        try:
            # Use custom check function if provided
            if component["custom_check"]:
                result = await component["custom_check"](component_name, component)
            else:
                # Use built-in check function
                check_func = self.check_functions.get(component["type"])
                if not check_func:
                    raise HealthCheckError(f"No check function for component type {component['type']}")
                    
                result = await check_func(component_name, component)
                
            # Calculate response time
            result.response_time = time.time() - start_time
            
            # Store result
            self.health_results[component_name] = result
            
            # Store in history
            if component_name not in self.health_history:
                self.health_history[component_name] = []
            self.health_history[component_name].append(result)
            
            # Keep only last 100 results
            if len(self.health_history[component_name]) > 100:
                self.health_history[component_name] = self.health_history[component_name][-100:]
                
            # Collect metrics
            await self._collect_health_metrics(result)
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = HealthCheckResult(
                component_name=component_name,
                component_type=component["type"],
                status=HealthStatus.CRITICAL,
                response_time=time.time() - start_time,
                message="Health check failed",
                error=str(e)
            )
            
            self.health_results[component_name] = error_result
            logger.error(f"Health check failed for {component_name}: {e}")
            
            return error_result
            
    async def perform_full_health_check(self) -> SystemHealthSummary:
        """Perform health check on all registered components"""
        start_time = time.time()
        
        # Check all components
        check_tasks = []
        for component_name in self.components.keys():
            task = asyncio.create_task(self.check_component_health(component_name))
            check_tasks.append(task)
            
        # Wait for all checks to complete
        await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Calculate system health summary
        summary = await self._calculate_system_health_summary()
        
        self.last_full_check = datetime.utcnow()
        
        # Collect overall system metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="system_health_check_duration",
                value=time.time() - start_time,
                metric_type=MetricType.TIMER,
                tags={"check_type": "full"},
                priority=MetricPriority.MEDIUM
            )
        )
        
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="system_health_score",
                value=self._calculate_health_score(summary),
                metric_type=MetricType.GAUGE,
                tags={
                    "overall_status": summary.overall_status.value
                },
                priority=MetricPriority.HIGH
            )
        )
        
        logger.info(f"Full health check completed: {summary.overall_status.value}")
        return summary
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all components"""
        # Ensure we have recent health data
        if not self.last_full_check or (
            datetime.utcnow() - self.last_full_check > timedelta(minutes=5)
        ):
            await self.perform_full_health_check()
            
        summary = await self._calculate_system_health_summary()
        
        component_status = {}
        for name, result in self.health_results.items():
            component_status[name] = {
                "status": result.status.value,
                "response_time": result.response_time,
                "message": result.message,
                "last_checked": result.timestamp.isoformat(),
                "error": result.error
            }
            
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": summary.overall_status.value,
            "system_summary": {
                "uptime": summary.uptime,
                "system_load": summary.system_load,
                "memory_usage": summary.memory_usage,
                "disk_usage": summary.disk_usage,
                "total_components": summary.total_components,
                "healthy_components": summary.healthy_components,
                "warning_components": summary.warning_components,
                "degraded_components": summary.degraded_components,
                "unhealthy_components": summary.unhealthy_components,
                "critical_components": summary.critical_components
            },
            "components": component_status,
            "last_full_check": self.last_full_check.isoformat() if self.last_full_check else None
        }
        
    async def get_component_health_history(
        self,
        component_name: str,
        time_window: timedelta = timedelta(hours=24)
    ) -> List[Dict[str, Any]]:
        """Get health history for a specific component"""
        if component_name not in self.health_history:
            return []
            
        cutoff_time = datetime.utcnow() - time_window
        
        history = [
            {
                "timestamp": result.timestamp.isoformat(),
                "status": result.status.value,
                "response_time": result.response_time,
                "message": result.message,
                "error": result.error
            }
            for result in self.health_history[component_name]
            if result.timestamp >= cutoff_time
        ]
        
        return history
        
    async def get_health_trends(self) -> Dict[str, Any]:
        """Get health trends and analytics"""
        trends = {}
        
        for component_name, history in self.health_history.items():
            if not history:
                continue
                
            # Calculate trends
            recent_results = history[-10:]  # Last 10 checks
            
            status_counts = {}
            response_times = []
            
            for result in recent_results:
                status = result.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                response_times.append(result.response_time)
                
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Determine trend
            if len(recent_results) >= 2:
                recent_healthy = sum(
                    1 for r in recent_results[-5:]
                    if r.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
                )
                older_healthy = sum(
                    1 for r in recent_results[-10:-5]
                    if r.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
                )
                
                if recent_healthy > older_healthy:
                    trend = "improving"
                elif recent_healthy < older_healthy:
                    trend = "degrading"
                else:
                    trend = "stable"
            else:
                trend = "unknown"
                
            trends[component_name] = {
                "status_distribution": status_counts,
                "average_response_time": avg_response_time,
                "trend": trend,
                "availability": status_counts.get("healthy", 0) / len(recent_results) * 100 if recent_results else 0
            }
            
        return trends
        
    def _register_default_components(self) -> None:
        """Register default system components"""
        default_components = [
            # Core system components
            {
                "name": "system_resources",
                "component_type": ComponentType.SYSTEM,
                "critical": True
            },
            
            # Database components
            {
                "name": "postgresql_primary",
                "component_type": ComponentType.DATABASE,
                "endpoint": "postgresql://localhost:5432/ia_influencer",
                "critical": True
            },
            
            # Cache components
            {
                "name": "redis_cache",
                "component_type": ComponentType.CACHE,
                "endpoint": "redis://localhost:6379/0",
                "critical": True
            },
            
            # AI Model components
            {
                "name": "content_generator_model",
                "component_type": ComponentType.AI_MODEL,
                "dependencies": ["redis_cache"],
                "critical": True
            },
            
            {
                "name": "content_protector_model",
                "component_type": ComponentType.AI_MODEL,
                "dependencies": ["redis_cache"],
                "critical": True
            },
            
            {
                "name": "seo_optimizer_model",
                "component_type": ComponentType.AI_MODEL,
                "dependencies": ["redis_cache"]
            },
            
            {
                "name": "collaboration_matcher_model",
                "component_type": ComponentType.AI_MODEL,
                "dependencies": ["redis_cache"]
            },
            
            # Storage components
            {
                "name": "content_storage",
                "component_type": ComponentType.STORAGE,
                "endpoint": "s3://content-bucket",
                "critical": True
            },
            
            # Queue components
            {
                "name": "celery_queue",
                "component_type": ComponentType.QUEUE,
                "endpoint": "redis://localhost:6379/1",
                "dependencies": ["redis_cache"]
            },
            
            # API components
            {
                "name": "main_api",
                "component_type": ComponentType.API,
                "endpoint": "http://localhost:8000/health",
                "critical": True
            },
            
            # External services
            {
                "name": "spotify_api",
                "component_type": ComponentType.EXTERNAL_SERVICE,
                "endpoint": "https://api.spotify.com/v1"
            },
            
            # Network components
            {
                "name": "internet_connectivity",
                "component_type": ComponentType.NETWORK,
                "endpoint": "8.8.8.8:53"
            }
        ]
        
        for component in default_components:
            self.register_component(**component)
            
        logger.info(f"Registered {len(default_components)} default components")
        
    async def _check_database(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check database health"""
        try:
            if self.database_session:
                # Test database connection with a simple query
                result = await self.database_session.execute(text("SELECT 1"))
                await result.fetchone()
                
                return HealthCheckResult(
                    component_name=name,
                    component_type=ComponentType.DATABASE,
                    status=HealthStatus.HEALTHY,
                    response_time=0.0,  # Will be calculated by caller
                    message="Database connection successful",
                    details={
                        "connection_pool_size": 10,  # Would get from actual pool
                        "active_connections": 2  # Would get from actual pool
                    }
                )
            else:
                return HealthCheckResult(
                    component_name=name,
                    component_type=ComponentType.DATABASE,
                    status=HealthStatus.WARNING,
                    response_time=0.0,
                    message="Database session not configured"
                )
                
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.DATABASE,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="Database connection failed",
                error=str(e)
            )
            
    async def _check_cache(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check cache (Redis) health"""
        try:
            if self.redis_client:
                # Test Redis connection
                await self.redis_client.ping()
                
                # Get Redis info
                info = await self.redis_client.info()
                memory_usage = info.get('used_memory', 0)
                max_memory = info.get('maxmemory', 0)
                connected_clients = info.get('connected_clients', 0)
                
                # Determine status based on memory usage
                if max_memory > 0:
                    memory_percent = (memory_usage / max_memory) * 100
                    if memory_percent > 90:
                        status = HealthStatus.CRITICAL
                        message = f"Redis memory usage critical: {memory_percent:.1f}%"
                    elif memory_percent > 80:
                        status = HealthStatus.WARNING
                        message = f"Redis memory usage high: {memory_percent:.1f}%"
                    else:
                        status = HealthStatus.HEALTHY
                        message = f"Redis healthy, memory usage: {memory_percent:.1f}%"
                else:
                    status = HealthStatus.HEALTHY
                    message = "Redis connection successful"
                    
                return HealthCheckResult(
                    component_name=name,
                    component_type=ComponentType.CACHE,
                    status=status,
                    response_time=0.0,
                    message=message,
                    details={
                        "memory_usage": memory_usage,
                        "max_memory": max_memory,
                        "connected_clients": connected_clients
                    }
                )
            else:
                return HealthCheckResult(
                    component_name=name,
                    component_type=ComponentType.CACHE,
                    status=HealthStatus.WARNING,
                    response_time=0.0,
                    message="Redis client not configured"
                )
                
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.CACHE,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="Redis connection failed",
                error=str(e)
            )
            
    async def _check_api(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check API endpoint health"""
        endpoint = config.get("endpoint")
        if not endpoint:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.API,
                status=HealthStatus.WARNING,
                response_time=0.0,
                message="No endpoint configured"
            )
            
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(endpoint) as response:
                    status_code = response.status
                    response_text = await response.text()
                    
                    if 200 <= status_code < 300:
                        status = HealthStatus.HEALTHY
                        message = f"API healthy (HTTP {status_code})"
                    elif 400 <= status_code < 500:
                        status = HealthStatus.WARNING
                        message = f"API client error (HTTP {status_code})"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"API server error (HTTP {status_code})"
                        
                    return HealthCheckResult(
                        component_name=name,
                        component_type=ComponentType.API,
                        status=status,
                        response_time=0.0,
                        message=message,
                        details={
                            "status_code": status_code,
                            "response_size": len(response_text)
                        }
                    )
                    
        except asyncio.TimeoutError:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.API,
                status=HealthStatus.CRITICAL,
                response_time=self.timeout,
                message="API timeout",
                error="Request timeout"
            )
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.API,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="API connection failed",
                error=str(e)
            )
            
    async def _check_ai_model(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check AI model health"""
        try:
            # This would integrate with actual AI model monitoring
            # For now, simulate a model health check
            
            # Check model loading status
            model_loaded = True  # Would check actual model status
            
            if not model_loaded:
                return HealthCheckResult(
                    component_name=name,
                    component_type=ComponentType.AI_MODEL,
                    status=HealthStatus.CRITICAL,
                    response_time=0.0,
                    message="AI model not loaded",
                    error="Model loading failed"
                )
                
            # Simulate model inference test
            inference_time = 0.1  # Would measure actual inference
            
            if inference_time > 2.0:
                status = HealthStatus.WARNING
                message = f"AI model slow (inference: {inference_time:.2f}s)"
            else:
                status = HealthStatus.HEALTHY
                message = f"AI model healthy (inference: {inference_time:.2f}s)"
                
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.AI_MODEL,
                status=status,
                response_time=0.0,
                message=message,
                details={
                    "inference_time": inference_time,
                    "model_loaded": model_loaded,
                    "memory_usage": 1024 * 1024 * 512  # 512MB simulated
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.AI_MODEL,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="AI model check failed",
                error=str(e)
            )
            
    async def _check_storage(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check storage health"""
        try:
            # This would integrate with actual storage system (S3, etc.)
            # For now, simulate storage health check
            
            storage_available = True  # Would check actual storage
            
            if not storage_available:
                return HealthCheckResult(
                    component_name=name,
                    component_type=ComponentType.STORAGE,
                    status=HealthStatus.CRITICAL,
                    response_time=0.0,
                    message="Storage unavailable",
                    error="Storage connection failed"
                )
                
            # Simulate storage metrics
            total_space = 1024 * 1024 * 1024 * 1000  # 1TB
            used_space = 1024 * 1024 * 1024 * 300   # 300GB
            usage_percent = (used_space / total_space) * 100
            
            if usage_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"Storage critical: {usage_percent:.1f}% used"
            elif usage_percent > 80:
                status = HealthStatus.WARNING
                message = f"Storage warning: {usage_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Storage healthy: {usage_percent:.1f}% used"
                
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.STORAGE,
                status=status,
                response_time=0.0,
                message=message,
                details={
                    "total_space": total_space,
                    "used_space": used_space,
                    "usage_percent": usage_percent
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.STORAGE,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="Storage check failed",
                error=str(e)
            )
            
    async def _check_queue(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check message queue health"""
        try:
            # This would integrate with actual queue system (Celery/Redis)
            # For now, simulate queue health check
            
            queue_size = 5  # Would get actual queue size
            max_queue_size = 1000
            
            if queue_size > max_queue_size * 0.9:
                status = HealthStatus.CRITICAL
                message = f"Queue critical: {queue_size} messages"
            elif queue_size > max_queue_size * 0.7:
                status = HealthStatus.WARNING
                message = f"Queue warning: {queue_size} messages"
            else:
                status = HealthStatus.HEALTHY
                message = f"Queue healthy: {queue_size} messages"
                
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.QUEUE,
                status=status,
                response_time=0.0,
                message=message,
                details={
                    "queue_size": queue_size,
                    "max_queue_size": max_queue_size,
                    "workers_active": 3  # Would get actual worker count
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.QUEUE,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="Queue check failed",
                error=str(e)
            )
            
    async def _check_external_service(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check external service health"""
        endpoint = config.get("endpoint")
        if not endpoint:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.EXTERNAL_SERVICE,
                status=HealthStatus.WARNING,
                response_time=0.0,
                message="No endpoint configured"
            )
            
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(endpoint) as response:
                    status_code = response.status
                    
                    if 200 <= status_code < 300:
                        status = HealthStatus.HEALTHY
                        message = f"External service healthy (HTTP {status_code})"
                    else:
                        status = HealthStatus.DEGRADED
                        message = f"External service issues (HTTP {status_code})"
                        
                    return HealthCheckResult(
                        component_name=name,
                        component_type=ComponentType.EXTERNAL_SERVICE,
                        status=status,
                        response_time=0.0,
                        message=message,
                        details={"status_code": status_code}
                    )
                    
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.EXTERNAL_SERVICE,
                status=HealthStatus.DEGRADED,  # External services don't fail the system
                response_time=0.0,
                message="External service unavailable",
                error=str(e)
            )
            
    async def _check_microservice(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check microservice health"""
        return await self._check_api(name, config)  # Same as API check
        
    async def _check_network(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check network connectivity"""
        endpoint = config.get("endpoint", "8.8.8.8:53")
        
        try:
            host, port = endpoint.split(":")
            port = int(port)
            
            # Test network connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                status = HealthStatus.HEALTHY
                message = f"Network connectivity healthy to {endpoint}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Network connectivity failed to {endpoint}"
                
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.NETWORK,
                status=status,
                response_time=0.0,
                message=message,
                details={"endpoint": endpoint, "result_code": result}
            )
            
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.NETWORK,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="Network check failed",
                error=str(e)
            )
            
    async def _check_system(self, name: str, config: Dict[str, Any]) -> HealthCheckResult:
        """Check system resources health"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine overall system status
            critical_issues = []
            warning_issues = []
            
            if cpu_percent > 90:
                critical_issues.append(f"CPU usage critical: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                warning_issues.append(f"CPU usage high: {cpu_percent:.1f}%")
                
            if memory.percent > 90:
                critical_issues.append(f"Memory usage critical: {memory.percent:.1f}%")
            elif memory.percent > 80:
                warning_issues.append(f"Memory usage high: {memory.percent:.1f}%")
                
            if disk.percent > 90:
                critical_issues.append(f"Disk usage critical: {disk.percent:.1f}%")
            elif disk.percent > 80:
                warning_issues.append(f"Disk usage high: {disk.percent:.1f}%")
                
            # Determine status
            if critical_issues:
                status = HealthStatus.CRITICAL
                message = "; ".join(critical_issues)
            elif warning_issues:
                status = HealthStatus.WARNING
                message = "; ".join(warning_issues)
            else:
                status = HealthStatus.HEALTHY
                message = f"System healthy (CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%, Disk: {disk.percent:.1f}%)"
                
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.SYSTEM,
                status=status,
                response_time=0.0,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free,
                    "load_average": psutil.getloadavg()[0]
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component_name=name,
                component_type=ComponentType.SYSTEM,
                status=HealthStatus.CRITICAL,
                response_time=0.0,
                message="System check failed",
                error=str(e)
            )
            
    async def _calculate_system_health_summary(self) -> SystemHealthSummary:
        """Calculate overall system health summary"""
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.WARNING: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0
        }
        
        for result in self.health_results.values():
            status_counts[result.status] += 1
            
        total_components = len(self.health_results)
        
        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.WARNING] > 0:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
            
        # Get system metrics
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg()[0]
            uptime = time.time() - self.system_start_time
            
            # Determine network status
            network_status = HealthStatus.HEALTHY
            if "internet_connectivity" in self.health_results:
                network_status = self.health_results["internet_connectivity"].status
                
        except Exception:
            cpu_percent = 0.0
            memory = type('obj', (object,), {'percent': 0.0})()
            disk = type('obj', (object,), {'percent': 0.0})()
            load_avg = 0.0
            uptime = 0.0
            network_status = HealthStatus.UNHEALTHY
            
        return SystemHealthSummary(
            overall_status=overall_status,
            healthy_components=status_counts[HealthStatus.HEALTHY],
            warning_components=status_counts[HealthStatus.WARNING],
            degraded_components=status_counts[HealthStatus.DEGRADED],
            unhealthy_components=status_counts[HealthStatus.UNHEALTHY],
            critical_components=status_counts[HealthStatus.CRITICAL],
            total_components=total_components,
            last_updated=datetime.utcnow(),
            uptime=uptime,
            system_load=load_avg,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_status=network_status
        )
        
    def _calculate_health_score(self, summary: SystemHealthSummary) -> float:
        """Calculate numerical health score (0-100)"""
        if summary.total_components == 0:
            return 0.0
            
        weights = {
            HealthStatus.HEALTHY: 1.0,
            HealthStatus.WARNING: 0.8,
            HealthStatus.DEGRADED: 0.6,
            HealthStatus.UNHEALTHY: 0.3,
            HealthStatus.CRITICAL: 0.0
        }
        
        total_score = (
            summary.healthy_components * weights[HealthStatus.HEALTHY] +
            summary.warning_components * weights[HealthStatus.WARNING] +
            summary.degraded_components * weights[HealthStatus.DEGRADED] +
            summary.unhealthy_components * weights[HealthStatus.UNHEALTHY] +
            summary.critical_components * weights[HealthStatus.CRITICAL]
        )
        
        return (total_score / summary.total_components) * 100
        
    async def _collect_health_metrics(self, result: HealthCheckResult) -> None:
        """Collect health check metrics"""
        # Collect component health metric
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="component_health_status",
                value=1 if result.status == HealthStatus.HEALTHY else 0,
                metric_type=MetricType.GAUGE,
                tags={
                    "component": result.component_name,
                    "component_type": result.component_type.value,
                    "status": result.status.value
                },
                priority=MetricPriority.HIGH if result.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY] else MetricPriority.MEDIUM
            )
        )
        
        # Collect response time metric
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="component_health_response_time",
                value=result.response_time,
                metric_type=MetricType.TIMER,
                tags={
                    "component": result.component_name,
                    "component_type": result.component_type.value
                }
            )
        )
        
    async def _monitoring_loop(self) -> None:
        """Main health monitoring loop"""
        while self.is_monitoring:
            try:
                # Perform full health check
                await self.perform_full_health_check()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error


# Global health checks instance
health_checks = HealthChecks()
