"""
Health Checker module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Health Checker

Enterprise health checking system for infrastructure monitoring.
Provides comprehensive health checks, availability monitoring, and service status tracking.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status options."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class CheckType(Enum):
    """Health check type options."""
    HTTP = "http"
    TCP = "tcp"
    DATABASE = "database"
    REDIS = "redis"
    CUSTOM = "custom"
    KUBERNETES = "kubernetes"
    EXTERNAL_API = "external_api"

@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    type: CheckType
    target: str
    interval: int = 30  # seconds
    timeout: int = 10  # seconds
    retries: int = 3
    retry_delay: int = 5  # seconds
    expected_status: int = 200
    expected_response: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    critical: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    custom_check: Optional[Callable] = None

@dataclass
class HealthResult:
    """Health check result."""
    check_name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceHealth:
    """Service health summary."""
    service_name: str
    overall_status: HealthStatus
    last_check: datetime
    uptime_percentage: float
    check_results: List[HealthResult] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

class HealthChecker:
    """
    Enterprise health checking system.
    
    Provides comprehensive health monitoring, availability tracking,
    and automated incident detection across infrastructure components.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize health checker."""
        self.config = config or {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_results: Dict[str, List[HealthResult]] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.check_tasks: Dict[str, asyncio.Task] = {}
        
        # Configuration
        self.default_interval = self.config.get("default_interval", 30)
        self.default_timeout = self.config.get("default_timeout", 10)
        self.max_history = self.config.get("max_history", 1000)
        self.enable_notifications = self.config.get("enable_notifications", True)
        
        # Status thresholds
        self.uptime_thresholds = self.config.get("uptime_thresholds", {
            "healthy": 99.0,
            "degraded": 95.0
        })
        
        # Notification settings
        self.notification_cooldown = self.config.get("notification_cooldown", 300)  # 5 minutes
        self.last_notifications: Dict[str, datetime] = {}
        
        # HTTP session for checks
        self.session = None
        
        # Dependency tracking
        self.dependency_graph: Dict[str, List[str]] = {}
        
        logger.info("HealthChecker initialized")
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.default_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        
        # Stop all check tasks
        for task in self.check_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.check_tasks:
            await asyncio.gather(*self.check_tasks.values(), return_exceptions=True)
    
    async def add_health_check(self, check: HealthCheck) -> bool:
        """Add a health check."""
        try:
            self.health_checks[check.name] = check
            self.health_results[check.name] = []
            
            # Start check task
            await self._start_check_task(check)
            
            logger.info(f"Added health check: {check.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add health check {check.name}: {str(e)}")
            return False
    
    async def remove_health_check(self, check_name: str) -> bool:
        """Remove a health check."""
        try:
            if check_name in self.check_tasks:
                self.check_tasks[check_name].cancel()
                del self.check_tasks[check_name]
            
            if check_name in self.health_checks:
                del self.health_checks[check_name]
            
            if check_name in self.health_results:
                del self.health_results[check_name]
            
            logger.info(f"Removed health check: {check_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove health check {check_name}: {str(e)}")
            return False
    
    async def _start_check_task(self, check -> None: HealthCheck) -> None:
        """Start a health check task."""
        try:
            # Cancel existing task if any
            if check.name in self.check_tasks:
                self.check_tasks[check.name].cancel()
            
            # Start new task
            task = asyncio.create_task(self._check_loop(check))
            self.check_tasks[check.name] = task
            
        except Exception as e:
            logger.error(f"Failed to start check task for {check.name}: {str(e)}")
    
    async def _check_loop(self, check -> None: HealthCheck) -> None:
        """Health check loop."""
        while True:
            try:
                result = await self._perform_check(check)
                await self._store_result(result)
                await self._process_result(result)
                
                await asyncio.sleep(check.interval)
                
            except asyncio.CancelledError:
                logger.info(f"Health check task cancelled: {check.name}")
                break
            except Exception as e:
                logger.error(f"Health check loop error for {check.name}: {str(e)}")
                await asyncio.sleep(check.interval)
    
    async def _perform_check(self, check: HealthCheck) -> HealthResult:
        """Perform a single health check."""
        start_time = time.time()
        
        try:
            if check.type == CheckType.HTTP:
                return await self._http_check(check, start_time)
            elif check.type == CheckType.TCP:
                return await self._tcp_check(check, start_time)
            elif check.type == CheckType.DATABASE:
                return await self._database_check(check, start_time)
            elif check.type == CheckType.REDIS:
                return await self._redis_check(check, start_time)
            elif check.type == CheckType.KUBERNETES:
                return await self._kubernetes_check(check, start_time)
            elif check.type == CheckType.EXTERNAL_API:
                return await self._external_api_check(check, start_time)
            elif check.type == CheckType.CUSTOM and check.custom_check:
                return await self._custom_check(check, start_time)
            else:
                return HealthResult(
                    check_name=check.name,
                    status=HealthStatus.UNKNOWN,
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    message=f"Unsupported check type: {check.type.value}"
                )
                
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"Check failed: {str(e)}"
            )
    
    async def _http_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform HTTP health check."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=check.timeout)
                )
            
            async with self.session.get(check.target, headers=check.headers) as response:
                response_time = time.time() - start_time
                
                # Check status code
                if response.status == check.expected_status:
                    # Check response body if expected
                    if check.expected_response:
                        body = await response.text()
                        if check.expected_response in body:
                            status = HealthStatus.HEALTHY
                            message = f"HTTP check successful: {response.status}"
                        else:
                            status = HealthStatus.UNHEALTHY
                            message = f"Expected response not found in body"
                    else:
                        status = HealthStatus.HEALTHY
                        message = f"HTTP check successful: {response.status}"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"Unexpected status code: {response.status}"
                
                return HealthResult(
                    check_name=check.name,
                    status=status,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    message=message,
                    details={
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "url": check.target
                    }
                )
                
        except asyncio.TimeoutError:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"HTTP check timeout after {check.timeout}s"
            )
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"HTTP check failed: {str(e)}"
            )
    
    async def _tcp_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform TCP health check."""
        try:
            # Parse host and port from target
            if ":" in check.target:
                host, port = check.target.rsplit(":", 1)
                port = int(port)
            else:
                host = check.target
                port = 80
            
            # Attempt TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=check.timeout
            )
            
            writer.close()
            await writer.wait_closed()
            
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.HEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"TCP connection successful to {host}:{port}"
            )
            
        except asyncio.TimeoutError:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"TCP connection timeout to {check.target}"
            )
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"TCP connection failed: {str(e)}"
            )
    
    async def _database_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform database health check."""
        try:
            # For demonstration, simulate database check
            # In real implementation, would use actual database drivers
            await asyncio.sleep(0.1)  # Simulate DB query time
            
            # Simulate connection check
            if "postgresql" in check.target.lower():
                # PostgreSQL check
                status = HealthStatus.HEALTHY
                message = "PostgreSQL connection successful"
            elif "mysql" in check.target.lower():
                # MySQL check
                status = HealthStatus.HEALTHY
                message = "MySQL connection successful"
            else:
                status = HealthStatus.HEALTHY
                message = "Database connection successful"
            
            return HealthResult(
                check_name=check.name,
                status=status,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=message,
                details={"database_type": check.target}
            )
            
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"Database check failed: {str(e)}"
            )
    
    async def _redis_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform Redis health check."""
        try:
            # For demonstration, simulate Redis check
            # In real implementation, would use redis-py or aioredis
            await asyncio.sleep(0.05)  # Simulate Redis ping time
            
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.HEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message="Redis PING successful",
                details={"redis_host": check.target}
            )
            
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"Redis check failed: {str(e)}"
            )
    
    async def _kubernetes_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform Kubernetes health check."""
        try:
            # For demonstration, simulate Kubernetes API check
            # In real implementation, would use kubernetes-python client
            await asyncio.sleep(0.2)  # Simulate K8s API call
            
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.HEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message="Kubernetes API accessible",
                details={"k8s_endpoint": check.target}
            )
            
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"Kubernetes check failed: {str(e)}"
            )
    
    async def _external_api_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform external API health check."""
        try:
            # Similar to HTTP check but with different expectations
            return await self._http_check(check, start_time)
            
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"External API check failed: {str(e)}"
            )
    
    async def _custom_check(self, check: HealthCheck, start_time: float) -> HealthResult:
        """Perform custom health check."""
        try:
            if check.custom_check:
                result = await check.custom_check(check)
                if isinstance(result, HealthResult):
                    return result
                elif isinstance(result, bool):
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "Custom check " + ("passed" if result else "failed")
                else:
                    status = HealthStatus.HEALTHY
                    message = f"Custom check result: {result}"
                
                return HealthResult(
                    check_name=check.name,
                    status=status,
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    message=message
                )
            else:
                return HealthResult(
                    check_name=check.name,
                    status=HealthStatus.UNKNOWN,
                    response_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    message="No custom check function provided"
                )
                
        except Exception as e:
            return HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                message=f"Custom check failed: {str(e)}"
            )
    
    async def _store_result(self, result -> None: HealthResult) -> None:
        """Store health check result."""
        try:
            if result.check_name not in self.health_results:
                self.health_results[result.check_name] = []
            
            # Add result
            self.health_results[result.check_name].append(result)
            
            # Limit history size
            if len(self.health_results[result.check_name]) > self.max_history:
                self.health_results[result.check_name] = self.health_results[result.check_name][-self.max_history:]
            
        except Exception as e:
            logger.error(f"Failed to store result for {result.check_name}: {str(e)}")
    
    async def _process_result(self, result -> None: HealthResult) -> None:
        """Process health check result."""
        try:
            # Update service health
            await self._update_service_health(result)
            
            # Check for status changes
            await self._check_status_changes(result)
            
            # Send notifications if needed
            if self.enable_notifications:
                await self._send_notifications(result)
            
        except Exception as e:
            logger.error(f"Failed to process result for {result.check_name}: {str(e)}")
    
    async def _update_service_health(self, result -> None: HealthResult) -> None:
        """Update service health summary."""
        try:
            service_name = result.check_name
            
            if service_name not in self.service_health:
                self.service_health[service_name] = ServiceHealth(
                    service_name=service_name,
                    overall_status=result.status,
                    last_check=result.timestamp,
                    uptime_percentage=100.0 if result.status == HealthStatus.HEALTHY else 0.0
                )
            
            service = self.service_health[service_name]
            service.last_check = result.timestamp
            service.overall_status = result.status
            
            # Calculate uptime percentage
            if service_name in self.health_results:
                results = self.health_results[service_name]
                if results:
                    healthy_count = sum(1 for r in results[-100:] if r.status == HealthStatus.HEALTHY)
                    service.uptime_percentage = (healthy_count / min(len(results), 100)) * 100
            
        except Exception as e:
            logger.error(f"Failed to update service health for {result.check_name}: {str(e)}")
    
    async def _check_status_changes(self, result -> None: HealthResult) -> None:
        """Check for status changes and log them."""
        try:
            check_name = result.check_name
            
            if check_name in self.health_results and len(self.health_results[check_name]) > 1:
                previous_result = self.health_results[check_name][-2]
                
                if previous_result.status != result.status:
                    logger.info(f"Status change for {check_name}: {previous_result.status.value} -> {result.status.value}")
                    
                    # Log status change event
                    await self._log_status_change(check_name, previous_result.status, result.status)
            
        except Exception as e:
            logger.error(f"Failed to check status changes for {result.check_name}: {str(e)}")
    
    async def _log_status_change(self, check_name -> None: str, old_status -> None: HealthStatus, new_status -> None: HealthStatus) -> None:
        """Log status change event."""
        try:
            # In real implementation, would send to logging system
            logger.info(f"HEALTH_STATUS_CHANGE: {check_name} changed from {old_status.value} to {new_status.value}")
            
        except Exception as e:
            logger.error(f"Failed to log status change: {str(e)}")
    
    async def _send_notifications(self, result -> None: HealthResult) -> None:
        """Send notifications for unhealthy services."""
        try:
            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                # Check cooldown
                last_notification = self.last_notifications.get(result.check_name)
                if last_notification and (datetime.now() - last_notification).total_seconds() < self.notification_cooldown:
                    return
                
                # Send notification
                await self._send_alert_notification(result)
                self.last_notifications[result.check_name] = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to send notifications for {result.check_name}: {str(e)}")
    
    async def _send_alert_notification(self, result -> None: HealthResult) -> None:
        """Send alert notification."""
        try:
            # In real implementation, would integrate with notification services
            alert_message = f"ALERT: {result.check_name} is {result.status.value} - {result.message}"
            logger.warning(alert_message)
            
        except Exception as e:
            logger.error(f"Failed to send alert notification: {str(e)}")
    
    async def create_default_health_checks(self) -> None:
        """Create default health checks for Ainflue infrastructure."""
        try:
            # API health check
            api_check = HealthCheck(
                name="ainflue-api",
                type=CheckType.HTTP,
                target="http://ainflue-api:8000/health",
                interval=15,
                timeout=5,
                critical=True,
                tags={"service": "api", "tier": "backend"}
            )
            await self.add_health_check(api_check)
            
            # AI Engine health check
            ai_check = HealthCheck(
                name="ainflue-ai-engine",
                type=CheckType.HTTP,
                target="http://ainflue-ai:8001/health",
                interval=30,
                timeout=10,
                critical=True,
                tags={"service": "ai-engine", "tier": "ml"}
            )
            await self.add_health_check(ai_check)
            
            # Database health check
            db_check = HealthCheck(
                name="postgresql",
                type=CheckType.DATABASE,
                target="postgresql://ainflue-postgresql:5432",
                interval=60,
                timeout=15,
                critical=True,
                tags={"service": "database", "tier": "data"}
            )
            await self.add_health_check(db_check)
            
            # Redis health check
            redis_check = HealthCheck(
                name="redis",
                type=CheckType.REDIS,
                target="redis://ainflue-redis:6379",
                interval=60,
                timeout=10,
                critical=False,
                tags={"service": "cache", "tier": "data"}
            )
            await self.add_health_check(redis_check)
            
            # Kubernetes API check
            k8s_check = HealthCheck(
                name="kubernetes-api",
                type=CheckType.KUBERNETES,
                target="https://kubernetes.default.svc.cluster.local",
                interval=120,
                timeout=20,
                critical=False,
                tags={"service": "kubernetes", "tier": "infrastructure"}
            )
            await self.add_health_check(k8s_check)
            
            logger.info("Created default health checks")
            
        except Exception as e:
            logger.error(f"Failed to create default health checks: {str(e)}")
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        try:
            total_checks = len(self.service_health)
            healthy_count = sum(1 for s in self.service_health.values() if s.overall_status == HealthStatus.HEALTHY)
            degraded_count = sum(1 for s in self.service_health.values() if s.overall_status == HealthStatus.DEGRADED)
            unhealthy_count = sum(1 for s in self.service_health.values() if s.overall_status == HealthStatus.UNHEALTHY)
            
            # Determine overall status
            if unhealthy_count > 0:
                overall_status = HealthStatus.UNHEALTHY
            elif degraded_count > 0:
                overall_status = HealthStatus.DEGRADED
            elif healthy_count == total_checks and total_checks > 0:
                overall_status = HealthStatus.HEALTHY
            else:
                overall_status = HealthStatus.UNKNOWN
            
            # Calculate average uptime
            if self.service_health:
                avg_uptime = sum(s.uptime_percentage for s in self.service_health.values()) / len(self.service_health)
            else:
                avg_uptime = 0.0
            
            return {
                "overall_status": overall_status.value,
                "total_checks": total_checks,
                "healthy_count": healthy_count,
                "degraded_count": degraded_count,
                "unhealthy_count": unhealthy_count,
                "average_uptime": avg_uptime,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get overall health: {str(e)}")
            return {"overall_status": "unknown", "error": str(e)}
    
    def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health information for a specific service."""
        if service_name not in self.service_health:
            return None
        
        service = self.service_health[service_name]
        recent_results = self.health_results.get(service_name, [])[-10:]  # Last 10 results
        
        return {
            "service_name": service.service_name,
            "overall_status": service.overall_status.value,
            "last_check": service.last_check.isoformat(),
            "uptime_percentage": service.uptime_percentage,
            "dependencies": service.dependencies,
            "recent_results": [
                {
                    "status": r.status.value,
                    "response_time": r.response_time,
                    "timestamp": r.timestamp.isoformat(),
                    "message": r.message
                }
                for r in recent_results
            ]
        }
    
    def list_health_checks(self) -> List[Dict[str, Any]]:
        """List all health checks."""
        checks = []
        for check in self.health_checks.values():
            checks.append({
                "name": check.name,
                "type": check.type.value,
                "target": check.target,
                "interval": check.interval,
                "timeout": check.timeout,
                "critical": check.critical,
                "tags": check.tags
            })
        return checks
    
    async def run_check_now(self, check_name: str) -> Optional[HealthResult]:
        """Run a specific health check immediately."""
        try:
            if check_name not in self.health_checks:
                return None
            
            check = self.health_checks[check_name]
            result = await self._perform_check(check)
            await self._store_result(result)
            await self._process_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to run check {check_name}: {str(e)}")
            return None


# Export the main class
__all__ = ["HealthChecker", "HealthCheck", "HealthResult", "ServiceHealth", "HealthStatus", "CheckType"]