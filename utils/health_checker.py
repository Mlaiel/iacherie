"""
Health Checker - DevOps Expert Implementation
===========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade health checking system for monitoring service health.
"""

import asyncio
import logging
import time
import httpx
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check configuration"""
    name: str
    check_function: Callable
    interval: int = 30  # seconds
    timeout: int = 10   # seconds
    threshold: int = 3  # failed attempts before marking unhealthy
    critical: bool = False  # if True, affects overall system health


@dataclass
class HealthResult:
    """Health check result"""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration: float  # execution time in seconds
    details: Dict[str, Any] = None


class HealthChecker:
    """
    Enterprise health checking system
    Implements comprehensive health monitoring for all system components
    """
    
    def __init__(self) -> None:
        """Initialize health checker"""
        self.checks: Dict[str, HealthCheck] = {}
        self.results: Dict[str, List[HealthResult]] = {}
        self.failure_counts: Dict[str, int] = {}
        self.is_running = False
        self.check_tasks: Dict[str, asyncio.Task] = {}
        
        # System health thresholds
        self.thresholds = {
            'cpu_usage_warning': 70.0,
            'cpu_usage_critical': 85.0,
            'memory_usage_warning': 80.0,
            'memory_usage_critical': 90.0,
            'disk_usage_warning': 80.0,
            'disk_usage_critical': 90.0,
            'response_time_warning': 1.0,
            'response_time_critical': 3.0
        }
        
        # Register default health checks
        self._register_default_checks()
        
        logger.info("HealthChecker initialized")
    
    def _register_default_checks(self) -> None:
        """Register default system health checks"""
        
        # Database connectivity check
        self.register_check(HealthCheck(
            name="database_connectivity",
            check_function=self._check_database,
            interval=30,
            critical=True
        ))
        
        # Redis connectivity check
        self.register_check(HealthCheck(
            name="redis_connectivity",
            check_function=self._check_redis,
            interval=30,
            critical=False
        ))
        
        # System resources check
        self.register_check(HealthCheck(
            name="system_resources",
            check_function=self._check_system_resources,
            interval=60,
            critical=True
        ))
        
        # AI services check
        self.register_check(HealthCheck(
            name="ai_services",
            check_function=self._check_ai_services,
            interval=120,
            critical=False
        ))
    
    async def _check_database(self) -> HealthResult:
        """Check database connectivity"""
        start_time = time.time()
        
        try:
            # Mock database check - in real implementation, would ping actual DB
            await asyncio.sleep(0.1)  # Simulate DB query
            
            # Simulate occasional failure for testing
            import random
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Database connection timeout")
            
            duration = time.time() - start_time
            return HealthResult(
                name="database_connectivity",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                timestamp=datetime.now(),
                duration=duration,
                details={"connection_time": duration}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return HealthResult(
                name="database_connectivity",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                timestamp=datetime.now(),
                duration=duration,
                details={"error": str(e)}
            )
    
    async def _check_redis(self) -> HealthResult:
        """Check Redis connectivity"""
        start_time = time.time()
        
        try:
            # Mock Redis check
            await asyncio.sleep(0.05)
            
            duration = time.time() - start_time
            return HealthResult(
                name="redis_connectivity",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                timestamp=datetime.now(),
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return HealthResult(
                name="redis_connectivity",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis check failed: {str(e)}",
                timestamp=datetime.now(),
                duration=duration
            )
    
    async def _check_system_resources(self) -> HealthResult:
        """Check system resource usage"""
        start_time = time.time()
        
        try:
            import psutil
            
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on thresholds
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_usage > self.thresholds['cpu_usage_critical']:
                status = HealthStatus.UNHEALTHY
                issues.append(f"CPU usage critical: {cpu_usage}%")
            elif cpu_usage > self.thresholds['cpu_usage_warning']:
                status = HealthStatus.DEGRADED
                issues.append(f"CPU usage high: {cpu_usage}%")
            
            if memory.percent > self.thresholds['memory_usage_critical']:
                status = HealthStatus.UNHEALTHY
                issues.append(f"Memory usage critical: {memory.percent}%")
            elif memory.percent > self.thresholds['memory_usage_warning']:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
                issues.append(f"Memory usage high: {memory.percent}%")
            
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.thresholds['disk_usage_critical']:
                status = HealthStatus.UNHEALTHY
                issues.append(f"Disk usage critical: {disk_percent:.1f}%")
            elif disk_percent > self.thresholds['disk_usage_warning']:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
                issues.append(f"Disk usage high: {disk_percent:.1f}%")
            
            message = "System resources normal"
            if issues:
                message = "; ".join(issues)
            
            duration = time.time() - start_time
            return HealthResult(
                name="system_resources",
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration=duration,
                details={
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "disk_usage": disk_percent,
                    "available_memory": memory.available
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return HealthResult(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message=f"System check failed: {str(e)}",
                timestamp=datetime.now(),
                duration=duration
            )
    
    async def _check_ai_services(self) -> HealthResult:
        """Check AI services health"""
        start_time = time.time()
        
        try:
            # Mock AI services check
            services_checked = ["openai", "anthropic", "huggingface"]
            healthy_services = []
            
            for service in services_checked:
                # Simulate service check
                await asyncio.sleep(0.1)
                healthy_services.append(service)
            
            status = HealthStatus.HEALTHY if len(healthy_services) == len(services_checked) else HealthStatus.DEGRADED
            
            duration = time.time() - start_time
            return HealthResult(
                name="ai_services",
                status=status,
                message=f"AI services: {len(healthy_services)}/{len(services_checked)} healthy",
                timestamp=datetime.now(),
                duration=duration,
                details={
                    "healthy_services": healthy_services,
                    "total_services": len(services_checked)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return HealthResult(
                name="ai_services",
                status=HealthStatus.UNKNOWN,
                message=f"AI services check failed: {str(e)}",
                timestamp=datetime.now(),
                duration=duration
            )
    
    def register_check(self, health_check -> None: HealthCheck) -> None:
        """Register a new health check"""
        self.checks[health_check.name] = health_check
        self.results[health_check.name] = []
        self.failure_counts[health_check.name] = 0
        logger.info(f"Registered health check: {health_check.name}")
    
    async def run_check(self, check_name: str) -> HealthResult:
        """Run a specific health check"""
        if check_name not in self.checks:
            raise ValueError(f"Health check '{check_name}' not found")
        
        check = self.checks[check_name]
        
        try:
            # Run the check with timeout
            result = await asyncio.wait_for(
                check.check_function(),
                timeout=check.timeout
            )
            
            # Update failure count
            if result.status == HealthStatus.HEALTHY:
                self.failure_counts[check_name] = 0
            else:
                self.failure_counts[check_name] += 1
            
            # Store result
            self.results[check_name].append(result)
            
            # Trim old results (keep last 100)
            if len(self.results[check_name]) > 100:
                self.results[check_name] = self.results[check_name][-50:]
            
            return result
            
        except asyncio.TimeoutError:
            self.failure_counts[check_name] += 1
            result = HealthResult(
                name=check_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {check.timeout}s",
                timestamp=datetime.now(),
                duration=check.timeout
            )
            self.results[check_name].append(result)
            return result
        
        except Exception as e:
            self.failure_counts[check_name] += 1
            result = HealthResult(
                name=check_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.now(),
                duration=0
            )
            self.results[check_name].append(result)
            return result
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        self.is_running = True
        logger.info("Starting health monitoring")
        
        # Start check tasks
        for check_name, check in self.checks.items():
            self.check_tasks[check_name] = asyncio.create_task(
                self._run_periodic_check(check_name, check)
            )
    
    async def _run_periodic_check(self, check_name -> None: str, check -> None: HealthCheck) -> None:
        """Run a health check periodically"""
        while self.is_running:
            try:
                await self.run_check(check_name)
                logger.debug(f"Completed health check: {check_name}")
                
            except Exception as e:
                logger.error(f"Error in periodic health check {check_name}: {e}")
            
            await asyncio.sleep(check.interval)
    
    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self.is_running = False
        
        # Cancel all check tasks
        for task in self.check_tasks.values():
            task.cancel()
        
        self.check_tasks.clear()
        logger.info("Stopped health monitoring")
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        if not self.results:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks performed yet",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get latest results
        latest_results = {}
        for check_name, results in self.results.items():
            if results:
                latest_results[check_name] = results[-1]
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        critical_issues = []
        warnings = []
        
        for check_name, result in latest_results.items():
            check = self.checks[check_name]
            
            if result.status == HealthStatus.UNHEALTHY:
                if check.critical:
                    overall_status = HealthStatus.UNHEALTHY
                    critical_issues.append(f"{check_name}: {result.message}")
                else:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
                    warnings.append(f"{check_name}: {result.message}")
            
            elif result.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                warnings.append(f"{check_name}: {result.message}")
        
        # Build message
        message = "All systems healthy"
        if critical_issues:
            message = f"Critical issues: {'; '.join(critical_issues)}"
        elif warnings:
            message = f"Warnings: {'; '.join(warnings)}"
        
        return {
            "status": overall_status.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "last_check": result.timestamp.isoformat(),
                    "duration": result.duration
                }
                for name, result in latest_results.items()
            }
        }


# Global instance
health_checker = HealthChecker()