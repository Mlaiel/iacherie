#!/usr/bin/env python3
"""
Enterprise Health Check Orchestrator Service
Comprehensive health monitoring system for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
import aiohttp
import json
import weakref

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class HealthCheckType(Enum):
    """Health check type enumeration"""
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"
    DEPENDENCY = "dependency"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    name: str
    endpoint: Optional[str] = None
    check_function: Optional[Callable[[], Awaitable[bool]]] = None
    check_type: HealthCheckType = HealthCheckType.LIVENESS
    interval: float = 30.0
    timeout: float = 10.0
    retry_count: int = 3
    retry_delay: float = 1.0
    enabled: bool = True
    critical: bool = False
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheckResult:
    """Health check result"""
    name: str
    status: HealthStatus
    timestamp: float
    duration: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    attempt: int = 1

@dataclass
class ServiceHealth:
    """Service health summary"""
    service_name: str
    overall_status: HealthStatus
    last_check: float
    checks: Dict[str, HealthCheckResult] = field(default_factory=dict)
    uptime: float = 0.0
    failure_count: int = 0
    recovery_time: Optional[float] = None

@dataclass
class AlertRule:
    """Health alert rule"""
    name: str
    condition: Callable[[ServiceHealth], bool]
    severity: AlertSeverity
    message_template: str
    cooldown: float = 300.0  # 5 minutes
    enabled: bool = True

class HealthCheckOrchestrator:
    """
    Enterprise Health Check Orchestrator
    
    Provides comprehensive health monitoring with:
    - Multiple health check types (liveness, readiness, startup)
    - Dependency tracking
    - Automated alerting
    - Performance monitoring
    - Recovery tracking
    """
    
    def __init__(self):
        """Initialize health check orchestrator"""
        self.health_checks: Dict[str, HealthCheckConfig] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.last_alerts: Dict[str, float] = {}
        
        self.check_tasks: Dict[str, asyncio.Task] = {}
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # HTTP session for endpoint checks
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Built-in alert rules
        self._setup_default_alert_rules()
        
        logger.info("HealthCheckOrchestrator initialized")
    
    async def start(self):
        """Start the health check orchestrator"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Start health check tasks
            await self._start_health_checks()
            
            logger.info("HealthCheckOrchestrator started successfully")
        except Exception as e:
            logger.error("Failed to start HealthCheckOrchestrator: %s", e)
            raise
    
    async def stop(self):
        """Stop the health check orchestrator"""
        try:
            self.shutdown_event.set()
            
            # Stop all check tasks
            await self._stop_health_checks()
            
            # Close HTTP session
            if self.session:
                await self.session.close()
                self.session = None
            
            logger.info("HealthCheckOrchestrator stopped successfully")
        except Exception as e:
            logger.error("Error stopping HealthCheckOrchestrator: %s", e)
    
    async def register_service(
        self,
        service_name: str,
        checks: List[HealthCheckConfig]
    ):
        """Register a service with health checks"""
        async with self._lock:
            # Initialize service health
            if service_name not in self.service_health:
                self.service_health[service_name] = ServiceHealth(
                    service_name=service_name,
                    overall_status=HealthStatus.UNKNOWN,
                    last_check=time.time()
                )
            
            # Register health checks
            for check in checks:
                check_key = f"{service_name}.{check.name}"
                self.health_checks[check_key] = check
                
                # Start check task if orchestrator is running
                if not self.shutdown_event.is_set():
                    await self._start_check_task(check_key, check)
        
        logger.info("Registered service '%s' with %d health checks", service_name, len(checks))
    
    async def unregister_service(self, service_name: str):
        """Unregister a service"""
        async with self._lock:
            # Stop and remove check tasks
            tasks_to_remove = [
                key for key in self.check_tasks.keys()
                if key.startswith(f"{service_name}.")
            ]
            
            for task_key in tasks_to_remove:
                task = self.check_tasks.pop(task_key, None)
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Remove health checks
            checks_to_remove = [
                key for key in self.health_checks.keys()
                if key.startswith(f"{service_name}.")
            ]
            
            for check_key in checks_to_remove:
                self.health_checks.pop(check_key, None)
            
            # Remove service health
            self.service_health.pop(service_name, None)
        
        logger.info("Unregistered service '%s'", service_name)
    
    async def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health status for a specific service"""
        async with self._lock:
            return self.service_health.get(service_name)
    
    async def get_all_health(self) -> Dict[str, ServiceHealth]:
        """Get health status for all services"""
        async with self._lock:
            return dict(self.service_health)
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        async with self._lock:
            if not self.service_health:
                return {
                    "status": HealthStatus.UNKNOWN.value,
                    "message": "No services registered",
                    "services": 0,
                    "healthy": 0,
                    "degraded": 0,
                    "unhealthy": 0,
                    "critical": 0
                }
            
            status_counts = {
                HealthStatus.HEALTHY: 0,
                HealthStatus.DEGRADED: 0,
                HealthStatus.UNHEALTHY: 0,
                HealthStatus.CRITICAL: 0,
                HealthStatus.UNKNOWN: 0
            }
            
            for service in self.service_health.values():
                status_counts[service.overall_status] += 1
            
            total_services = len(self.service_health)
            
            # Determine overall status
            if status_counts[HealthStatus.CRITICAL] > 0:
                overall_status = HealthStatus.CRITICAL
            elif status_counts[HealthStatus.UNHEALTHY] > 0:
                overall_status = HealthStatus.UNHEALTHY
            elif status_counts[HealthStatus.DEGRADED] > 0:
                overall_status = HealthStatus.DEGRADED
            elif status_counts[HealthStatus.HEALTHY] == total_services:
                overall_status = HealthStatus.HEALTHY
            else:
                overall_status = HealthStatus.UNKNOWN
            
            return {
                "status": overall_status.value,
                "message": f"{status_counts[HealthStatus.HEALTHY]}/{total_services} services healthy",
                "services": total_services,
                "healthy": status_counts[HealthStatus.HEALTHY],
                "degraded": status_counts[HealthStatus.DEGRADED],
                "unhealthy": status_counts[HealthStatus.UNHEALTHY],
                "critical": status_counts[HealthStatus.CRITICAL],
                "unknown": status_counts[HealthStatus.UNKNOWN],
                "timestamp": time.time()
            }
    
    async def force_check(self, service_name: str, check_name: Optional[str] = None):
        """Force immediate health check"""
        if check_name:
            check_key = f"{service_name}.{check_name}"
            if check_key in self.health_checks:
                await self._execute_health_check(check_key, self.health_checks[check_key])
        else:
            # Force all checks for the service
            service_checks = [
                (key, config) for key, config in self.health_checks.items()
                if key.startswith(f"{service_name}.")
            ]
            
            for check_key, config in service_checks:
                await self._execute_health_check(check_key, config)
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule"""
        async with self._lock:
            self.alert_rules[rule.name] = rule
        logger.info("Added alert rule: %s", rule.name)
    
    async def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule"""
        async with self._lock:
            self.alert_rules.pop(rule_name, None)
        logger.info("Removed alert rule: %s", rule_name)
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        async with self._lock:
            return self.alert_history[-limit:]
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            "service_down": AlertRule(
                name="service_down",
                condition=lambda health: health.overall_status == HealthStatus.CRITICAL,
                severity=AlertSeverity.CRITICAL,
                message_template="Service {service_name} is down",
                cooldown=60.0
            ),
            "service_degraded": AlertRule(
                name="service_degraded",
                condition=lambda health: health.overall_status == HealthStatus.DEGRADED,
                severity=AlertSeverity.WARNING,
                message_template="Service {service_name} is degraded",
                cooldown=300.0
            ),
            "high_failure_rate": AlertRule(
                name="high_failure_rate",
                condition=lambda health: health.failure_count > 5,
                severity=AlertSeverity.ERROR,
                message_template="Service {service_name} has high failure rate",
                cooldown=600.0
            )
        }
    
    async def _start_health_checks(self):
        """Start all health check tasks"""
        for check_key, config in self.health_checks.items():
            await self._start_check_task(check_key, config)
    
    async def _start_check_task(self, check_key: str, config: HealthCheckConfig):
        """Start a single health check task"""
        if not config.enabled:
            return
        
        if check_key in self.check_tasks:
            # Stop existing task
            self.check_tasks[check_key].cancel()
        
        self.check_tasks[check_key] = asyncio.create_task(
            self._health_check_loop(check_key, config)
        )
    
    async def _stop_health_checks(self):
        """Stop all health check tasks"""
        tasks = list(self.check_tasks.values())
        self.check_tasks.clear()
        
        for task in tasks:
            task.cancel()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _health_check_loop(self, check_key: str, config: HealthCheckConfig):
        """Health check execution loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._execute_health_check(check_key, config)
                await asyncio.sleep(config.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health check loop for %s: %s", check_key, e)
                await asyncio.sleep(config.interval)
    
    async def _execute_health_check(self, check_key: str, config: HealthCheckConfig):
        """Execute a single health check"""
        service_name = check_key.split('.')[0]
        start_time = time.time()
        result = None
        
        for attempt in range(1, config.retry_count + 1):
            try:
                # Execute health check
                if config.check_function:
                    success = await asyncio.wait_for(
                        config.check_function(),
                        timeout=config.timeout
                    )
                elif config.endpoint:
                    success = await self._check_endpoint(config.endpoint, config.timeout)
                else:
                    success = True  # Default to healthy if no check specified
                
                duration = time.time() - start_time
                
                result = HealthCheckResult(
                    name=config.name,
                    status=HealthStatus.HEALTHY if success else HealthStatus.UNHEALTHY,
                    timestamp=time.time(),
                    duration=duration,
                    message="Health check passed" if success else "Health check failed",
                    attempt=attempt
                )
                
                if success or attempt == config.retry_count:
                    break
                
                await asyncio.sleep(config.retry_delay)
                
            except asyncio.TimeoutError:
                duration = time.time() - start_time
                result = HealthCheckResult(
                    name=config.name,
                    status=HealthStatus.UNHEALTHY,
                    timestamp=time.time(),
                    duration=duration,
                    message="Health check timed out",
                    error="Timeout",
                    attempt=attempt
                )
                
                if attempt < config.retry_count:
                    await asyncio.sleep(config.retry_delay)
                
            except Exception as e:
                duration = time.time() - start_time
                result = HealthCheckResult(
                    name=config.name,
                    status=HealthStatus.CRITICAL if config.critical else HealthStatus.UNHEALTHY,
                    timestamp=time.time(),
                    duration=duration,
                    message=f"Health check error: {str(e)}",
                    error=str(e),
                    attempt=attempt
                )
                
                if attempt < config.retry_count:
                    await asyncio.sleep(config.retry_delay)
        
        # Update service health
        if result:
            await self._update_service_health(service_name, config.name, result)
    
    async def _check_endpoint(self, endpoint: str, timeout: float) -> bool:
        """Check HTTP endpoint health"""
        if not self.session:
            return False
        
        try:
            async with self.session.get(endpoint, timeout=timeout) as response:
                return response.status < 400
        except Exception:
            return False
    
    async def _update_service_health(
        self,
        service_name: str,
        check_name: str,
        result: HealthCheckResult
    ):
        """Update service health based on check result"""
        async with self._lock:
            if service_name not in self.service_health:
                self.service_health[service_name] = ServiceHealth(
                    service_name=service_name,
                    overall_status=HealthStatus.UNKNOWN,
                    last_check=time.time()
                )
            
            service = self.service_health[service_name]
            service.checks[check_name] = result
            service.last_check = time.time()
            
            # Update failure count
            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                service.failure_count += 1
            else:
                service.failure_count = max(0, service.failure_count - 1)
            
            # Calculate overall status
            check_statuses = [check.status for check in service.checks.values()]
            
            if any(status == HealthStatus.CRITICAL for status in check_statuses):
                service.overall_status = HealthStatus.CRITICAL
            elif any(status == HealthStatus.UNHEALTHY for status in check_statuses):
                service.overall_status = HealthStatus.UNHEALTHY
            elif any(status == HealthStatus.DEGRADED for status in check_statuses):
                service.overall_status = HealthStatus.DEGRADED
            elif all(status == HealthStatus.HEALTHY for status in check_statuses):
                service.overall_status = HealthStatus.HEALTHY
                # Reset failure count on recovery
                if service.failure_count > 0:
                    service.recovery_time = time.time()
                    service.failure_count = 0
            else:
                service.overall_status = HealthStatus.UNKNOWN
            
            # Check alert rules
            await self._check_alert_rules(service)
    
    async def _check_alert_rules(self, service: ServiceHealth):
        """Check alert rules for a service"""
        current_time = time.time()
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown
            last_alert_key = f"{service.service_name}.{rule_name}"
            last_alert_time = self.last_alerts.get(last_alert_key, 0)
            
            if current_time - last_alert_time < rule.cooldown:
                continue
            
            # Check condition
            try:
                if rule.condition(service):
                    await self._trigger_alert(service, rule)
                    self.last_alerts[last_alert_key] = current_time
            except Exception as e:
                logger.error("Error checking alert rule %s: %s", rule_name, e)
    
    async def _trigger_alert(self, service: ServiceHealth, rule: AlertRule):
        """Trigger an alert"""
        alert = {
            "timestamp": time.time(),
            "service": service.service_name,
            "rule": rule.name,
            "severity": rule.severity.value,
            "message": rule.message_template.format(service_name=service.service_name),
            "status": service.overall_status.value,
            "failure_count": service.failure_count
        }
        
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        logger.warning(
            "Health alert triggered: %s - %s",
            alert["message"], alert["severity"]
        )

# Global health check orchestrator instance
_orchestrator: Optional[HealthCheckOrchestrator] = None

async def get_health_orchestrator() -> HealthCheckOrchestrator:
    """Get global health check orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = HealthCheckOrchestrator()
        await _orchestrator.start()
    return _orchestrator

async def shutdown_health_orchestrator():
    """Shutdown global health check orchestrator"""
    global _orchestrator
    if _orchestrator:
        await _orchestrator.stop()
        _orchestrator = None

if __name__ == "__main__":
    async def test_health_orchestrator():
        """Test health orchestrator functionality"""
        orchestrator = HealthCheckOrchestrator()
        await orchestrator.start()
        
        try:
            # Define test health checks
            async def always_healthy():
                return True
            
            async def always_unhealthy():
                return False
            
            checks = [
                HealthCheckConfig(
                    name="liveness",
                    check_function=always_healthy,
                    check_type=HealthCheckType.LIVENESS,
                    interval=5.0
                ),
                HealthCheckConfig(
                    name="readiness",
                    check_function=always_unhealthy,
                    check_type=HealthCheckType.READINESS,
                    interval=5.0
                )
            ]
            
            # Register test service
            await orchestrator.register_service("test_service", checks)
            
            # Wait for some checks
            await asyncio.sleep(2)
            
            # Get health status
            service_health = await orchestrator.get_service_health("test_service")
            print(f"Service health: {service_health}")
            
            overall_health = await orchestrator.get_overall_health()
            print(f"Overall health: {overall_health}")
            
            # Force a check
            await orchestrator.force_check("test_service")
            
            # Get alert history
            alerts = await orchestrator.get_alert_history()
            print(f"Alerts: {alerts}")
            
        finally:
            await orchestrator.stop()
    
    # Run test
    asyncio.run(test_health_orchestrator())