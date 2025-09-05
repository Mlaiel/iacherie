"""Edge Health Checker System
==========================

Comprehensive health checking system for edge computing infrastructure,
providing automated health monitoring, diagnostics, and recovery actions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import aiohttp
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json
import subprocess
import psutil

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class CheckType(str, Enum):
    """Types of health checks."""
    HTTP = "http"
    TCP = "tcp"
    PING = "ping"
    PROCESS = "process"
    RESOURCE = "resource"
    DATABASE = "database"
    CUSTOM = "custom"


@dataclass
class HealthCheck:
    """Health check configuration."""
    check_id: str
    name: str
    check_type: CheckType
    target: str
    interval: int = 30  # seconds
    timeout: int = 10   # seconds
    retries: int = 3
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    """Health check execution result."""
    check_id: str
    status: HealthStatus
    timestamp: datetime
    response_time: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class EdgeHealthChecker:
    """Comprehensive edge health checking system."""
    
    def __init__(self,
                 default_interval: int = 30,
                 max_concurrent_checks: int = 50,
                 result_retention: int = 3600):  # 1 hour
        
        self.default_interval = default_interval
        self.max_concurrent_checks = max_concurrent_checks
        self.result_retention = result_retention
        
        # Health checks storage
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_results: Dict[str, List[HealthCheckResult]] = {}
        self.current_status: Dict[str, HealthStatus] = {}
        
        # Check execution
        self.active_checks: Dict[str, asyncio.Task] = {}
        self.check_semaphore = asyncio.Semaphore(max_concurrent_checks)
        
        # Event handlers
        self.status_change_handlers: List[Callable] = []
        self.check_failure_handlers: List[Callable] = []
        
        # Background tasks
        self.scheduler_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Control flags
        self.running = False
        
        # Built-in check implementations
        self.check_implementations = {
            CheckType.HTTP: self._http_check,
            CheckType.TCP: self._tcp_check,
            CheckType.PING: self._ping_check,
            CheckType.PROCESS: self._process_check,
            CheckType.RESOURCE: self._resource_check,
            CheckType.DATABASE: self._database_check
        }
        
        logger.info("EdgeHealthChecker initialized")
    
    async def start(self):
        """Start the health checking system."""
        if self.running:
            logger.warning("Health checker already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Initialize system health checks
        await self._initialize_system_checks()
        
        logger.info("Edge health checking started")
    
    async def stop(self):
        """Stop the health checking system."""
        self.running = False
        
        # Cancel active checks
        for task in self.active_checks.values():
            task.cancel()
        
        # Cancel background tasks
        tasks = [self.scheduler_task, self.cleanup_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        all_tasks = list(self.active_checks.values()) + tasks
        if all_tasks:
            await asyncio.gather(*all_tasks, return_exceptions=True)
        
        logger.info("Edge health checking stopped")
    
    async def add_health_check(self, health_check: HealthCheck) -> bool:
        """Add a health check configuration."""
        try:
            self.health_checks[health_check.check_id] = health_check
            self.check_results[health_check.check_id] = []
            self.current_status[health_check.check_id] = HealthStatus.UNKNOWN
            
            logger.info(f"Added health check: {health_check.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add health check {health_check.name}: {e}")
            return False
    
    async def remove_health_check(self, check_id: str) -> bool:
        """Remove a health check."""
        try:
            if check_id in self.health_checks:
                # Cancel active check
                if check_id in self.active_checks:
                    self.active_checks[check_id].cancel()
                    del self.active_checks[check_id]
                
                # Remove from storage
                del self.health_checks[check_id]
                del self.check_results[check_id]
                del self.current_status[check_id]
                
                logger.info(f"Removed health check: {check_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove health check {check_id}: {e}")
            return False
    
    async def execute_check(self, check_id: str) -> Optional[HealthCheckResult]:
        """Execute a specific health check immediately."""
        if check_id not in self.health_checks:
            logger.warning(f"Health check {check_id} not found")
            return None
        
        health_check = self.health_checks[check_id]
        
        if not health_check.enabled:
            logger.debug(f"Health check {check_id} is disabled")
            return None
        
        return await self._execute_single_check(health_check)
    
    async def get_health_status(self, check_id: Optional[str] = None) -> Union[HealthStatus, Dict[str, HealthStatus]]:
        """Get health status for specific check or all checks."""
        if check_id:
            return self.current_status.get(check_id, HealthStatus.UNKNOWN)
        else:
            return self.current_status.copy()
    
    async def get_check_results(self,
                               check_id: str,
                               limit: Optional[int] = None,
                               since: Optional[datetime] = None) -> List[HealthCheckResult]:
        """Get health check results with optional filtering."""
        
        if check_id not in self.check_results:
            return []
        
        results = self.check_results[check_id].copy()
        
        # Apply time filter
        if since:
            results = [r for r in results if r.timestamp > since]
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        
        total_checks = len(self.health_checks)
        if total_checks == 0:
            return {
                'overall_status': HealthStatus.UNKNOWN,
                'total_checks': 0,
                'status_counts': {},
                'failed_checks': []
            }
        
        status_counts = {}
        failed_checks = []
        
        for check_id, status in self.current_status.items():
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
            
            if status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                check_name = self.health_checks[check_id].name
                failed_checks.append({
                    'check_id': check_id,
                    'name': check_name,
                    'status': status.value
                })
        
        # Determine overall status
        if status_counts.get(HealthStatus.CRITICAL.value, 0) > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts.get(HealthStatus.WARNING.value, 0) > 0:
            overall_status = HealthStatus.WARNING
        elif status_counts.get(HealthStatus.HEALTHY.value, 0) == total_checks:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        return {
            'overall_status': overall_status,
            'total_checks': total_checks,
            'status_counts': status_counts,
            'failed_checks': failed_checks,
            'last_updated': datetime.now()
        }
    
    async def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        
        overall_health = await self.get_overall_health()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'overall_health': overall_health,
            'checks': {}
        }
        
        # Add details for each check
        for check_id, health_check in self.health_checks.items():
            recent_results = await self.get_check_results(check_id, limit=10)
            
            check_report = {
                'name': health_check.name,
                'type': health_check.check_type.value,
                'target': health_check.target,
                'current_status': self.current_status.get(check_id, HealthStatus.UNKNOWN).value,
                'enabled': health_check.enabled,
                'interval': health_check.interval,
                'recent_results_count': len(recent_results)
            }
            
            # Add latest result details
            if recent_results:
                latest = recent_results[0]
                check_report['latest_result'] = {
                    'timestamp': latest.timestamp.isoformat(),
                    'response_time': latest.response_time,
                    'message': latest.message,
                    'error': latest.error
                }
            
            # Calculate availability (last 24 hours)
            since_24h = datetime.now() - timedelta(hours=24)
            results_24h = await self.get_check_results(check_id, since=since_24h)
            
            if results_24h:
                healthy_count = sum(1 for r in results_24h if r.status == HealthStatus.HEALTHY)
                availability = (healthy_count / len(results_24h)) * 100
                check_report['availability_24h'] = f"{availability:.2f}%"
            
            report['checks'][check_id] = check_report
        
        return report
    
    def add_status_change_handler(self, handler: Callable):
        """Add status change event handler."""
        self.status_change_handlers.append(handler)
    
    def add_check_failure_handler(self, handler: Callable):
        """Add check failure event handler."""
        self.check_failure_handlers.append(handler)
    
    # Private methods
    
    async def _initialize_system_checks(self):
        """Initialize default system health checks."""
        
        # System resource check
        resource_check = HealthCheck(
            check_id="system_resources",
            name="System Resources",
            check_type=CheckType.RESOURCE,
            target="system",
            interval=30
        )
        await self.add_health_check(resource_check)
        
        # Network connectivity check
        ping_check = HealthCheck(
            check_id="network_connectivity",
            name="Network Connectivity",
            check_type=CheckType.PING,
            target="8.8.8.8",  # Google DNS
            interval=60
        )
        await self.add_health_check(ping_check)
    
    async def _scheduler_loop(self):
        """Main scheduler loop for health checks."""
        last_check_times = {}
        
        while self.running:
            try:
                current_time = datetime.now()
                
                for check_id, health_check in self.health_checks.items():
                    if not health_check.enabled:
                        continue
                    
                    # Check if it's time to run this check
                    last_run = last_check_times.get(check_id)
                    
                    if (last_run is None or 
                        (current_time - last_run).seconds >= health_check.interval):
                        
                        # Don't start new check if one is already running
                        if check_id not in self.active_checks:
                            task = asyncio.create_task(
                                self._execute_check_with_retry(health_check)
                            )
                            self.active_checks[check_id] = task
                            last_check_times[check_id] = current_time
                
                # Clean up completed tasks
                completed_tasks = [
                    check_id for check_id, task in self.active_checks.items()
                    if task.done()
                ]
                
                for check_id in completed_tasks:
                    del self.active_checks[check_id]
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self.running:
            try:
                await self._cleanup_old_results()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def _execute_check_with_retry(self, health_check: HealthCheck):
        """Execute health check with retry logic."""
        
        async with self.check_semaphore:
            for attempt in range(health_check.retries + 1):
                try:
                    result = await self._execute_single_check(health_check)
                    
                    if result:
                        await self._process_check_result(result)
                        return result
                    
                except Exception as e:
                    logger.error(f"Health check {health_check.name} failed on attempt {attempt + 1}: {e}")
                    
                    if attempt == health_check.retries:
                        # Final attempt failed, create error result
                        error_result = HealthCheckResult(
                            check_id=health_check.check_id,
                            status=HealthStatus.CRITICAL,
                            timestamp=datetime.now(),
                            response_time=0.0,
                            message=f"Check failed after {health_check.retries + 1} attempts",
                            error=str(e)
                        )
                        await self._process_check_result(error_result)
                        return error_result
                    
                    # Wait before retry
                    await asyncio.sleep(1)
        
        return None
    
    async def _execute_single_check(self, health_check: HealthCheck) -> Optional[HealthCheckResult]:
        """Execute a single health check."""
        
        start_time = time.time()
        
        try:
            # Get the appropriate check implementation
            check_impl = self.check_implementations.get(health_check.check_type)
            
            if not check_impl:
                # Try custom check
                if health_check.check_type == CheckType.CUSTOM:
                    check_impl = self._custom_check
                else:
                    raise ValueError(f"Unknown check type: {health_check.check_type}")
            
            # Execute the check with timeout
            result = await asyncio.wait_for(
                check_impl(health_check),
                timeout=health_check.timeout
            )
            
            response_time = time.time() - start_time
            
            if result is None:
                result = HealthCheckResult(
                    check_id=health_check.check_id,
                    status=HealthStatus.UNKNOWN,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    message="Check returned no result"
                )
            else:
                result.response_time = response_time
            
            return result
            
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=health_check.timeout,
                message="Check timed out",
                error="Timeout"
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                message=f"Check failed: {str(e)}",
                error=str(e)
            )
    
    async def _process_check_result(self, result: HealthCheckResult):
        """Process and store health check result."""
        
        check_id = result.check_id
        previous_status = self.current_status.get(check_id, HealthStatus.UNKNOWN)
        
        # Store result
        if check_id not in self.check_results:
            self.check_results[check_id] = []
        
        self.check_results[check_id].append(result)
        self.current_status[check_id] = result.status
        
        # Trigger status change handlers
        if result.status != previous_status:
            for handler in self.status_change_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(check_id, previous_status, result.status)
                    else:
                        handler(check_id, previous_status, result.status)
                except Exception as e:
                    logger.error(f"Error in status change handler: {e}")
        
        # Trigger failure handlers
        if result.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            for handler in self.check_failure_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(result)
                    else:
                        handler(result)
                except Exception as e:
                    logger.error(f"Error in check failure handler: {e}")
        
        logger.debug(f"Health check {check_id}: {result.status.value} ({result.response_time:.2f}s)")
    
    async def _cleanup_old_results(self):
        """Clean up old health check results."""
        cutoff_time = datetime.now() - timedelta(seconds=self.result_retention)
        
        for check_id in list(self.check_results.keys()):
            results = self.check_results[check_id]
            
            # Remove old results
            self.check_results[check_id] = [
                result for result in results
                if result.timestamp > cutoff_time
            ]
            
            # Remove empty result lists
            if not self.check_results[check_id]:
                del self.check_results[check_id]
    
    # Check implementations
    
    async def _http_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """HTTP health check implementation."""
        
        url = health_check.target
        expected_status = health_check.metadata.get('expected_status', 200)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                status = HealthStatus.HEALTHY if response.status == expected_status else HealthStatus.CRITICAL
                
                return HealthCheckResult(
                    check_id=health_check.check_id,
                    status=status,
                    timestamp=datetime.now(),
                    response_time=0.0,  # Will be set by caller
                    message=f"HTTP {response.status}",
                    details={
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'url': url
                    }
                )
    
    async def _tcp_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """TCP health check implementation."""
        
        host, port = health_check.target.split(':')
        port = int(port)
        
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                response_time=0.0,
                message=f"TCP connection to {host}:{port} successful",
                details={'host': host, 'port': port}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=0.0,
                message=f"TCP connection to {host}:{port} failed",
                error=str(e),
                details={'host': host, 'port': port}
            )
    
    async def _ping_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Ping health check implementation."""
        
        host = health_check.target
        
        try:
            # Use system ping command
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', '5', host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                status = HealthStatus.HEALTHY
                message = f"Ping to {host} successful"
            else:
                status = HealthStatus.CRITICAL
                message = f"Ping to {host} failed"
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=status,
                timestamp=datetime.now(),
                response_time=0.0,
                message=message,
                details={
                    'host': host,
                    'return_code': process.returncode,
                    'stdout': stdout.decode() if stdout else None,
                    'stderr': stderr.decode() if stderr else None
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=0.0,
                message=f"Ping check failed",
                error=str(e),
                details={'host': host}
            )
    
    async def _process_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Process health check implementation."""
        
        process_name = health_check.target
        
        try:
            # Check if process is running
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    return HealthCheckResult(
                        check_id=health_check.check_id,
                        status=HealthStatus.HEALTHY,
                        timestamp=datetime.now(),
                        response_time=0.0,
                        message=f"Process {process_name} is running",
                        details={'process_name': process_name, 'pid': proc.info['pid']}
                    )
            
            # Process not found
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=0.0,
                message=f"Process {process_name} not found",
                details={'process_name': process_name}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=0.0,
                message=f"Process check failed",
                error=str(e),
                details={'process_name': process_name}
            )
    
    async def _resource_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Resource health check implementation."""
        
        try:
            # Get system resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Define thresholds
            cpu_warning = health_check.metadata.get('cpu_warning', 80)
            cpu_critical = health_check.metadata.get('cpu_critical', 95)
            memory_warning = health_check.metadata.get('memory_warning', 85)
            memory_critical = health_check.metadata.get('memory_critical', 95)
            disk_warning = health_check.metadata.get('disk_warning', 90)
            disk_critical = health_check.metadata.get('disk_critical', 98)
            
            # Determine status
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent >= cpu_critical:
                status = HealthStatus.CRITICAL
                issues.append(f"CPU usage critical: {cpu_percent:.1f}%")
            elif cpu_percent >= cpu_warning:
                status = HealthStatus.WARNING
                issues.append(f"CPU usage high: {cpu_percent:.1f}%")
            
            if memory.percent >= memory_critical:
                status = HealthStatus.CRITICAL
                issues.append(f"Memory usage critical: {memory.percent:.1f}%")
            elif memory.percent >= memory_warning and status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
                issues.append(f"Memory usage high: {memory.percent:.1f}%")
            
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent >= disk_critical:
                status = HealthStatus.CRITICAL
                issues.append(f"Disk usage critical: {disk_percent:.1f}%")
            elif disk_percent >= disk_warning and status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
                issues.append(f"Disk usage high: {disk_percent:.1f}%")
            
            message = "Resource usage normal" if not issues else "; ".join(issues)
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=status,
                timestamp=datetime.now(),
                response_time=0.0,
                message=message,
                details={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk_percent,
                    'memory_total_gb': memory.total // (1024**3),
                    'disk_total_gb': disk.total // (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=0.0,
                message="Resource check failed",
                error=str(e)
            )
    
    async def _database_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Database health check implementation."""
        
        # This is a placeholder - would be implemented based on specific database type
        return HealthCheckResult(
            check_id=health_check.check_id,
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            response_time=0.0,
            message="Database check placeholder",
            details={'target': health_check.target}
        )
    
    async def _custom_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Custom health check implementation."""
        
        # This would execute custom check logic based on metadata
        return HealthCheckResult(
            check_id=health_check.check_id,
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            response_time=0.0,
            message="Custom check placeholder",
            details={'target': health_check.target}
        )


def create_health_checker(
    default_interval: int = 30,
    max_concurrent_checks: int = 50,
    result_retention: int = 3600
) -> EdgeHealthChecker:
    """Create and configure a health checker instance."""
    return EdgeHealthChecker(
        default_interval=default_interval,
        max_concurrent_checks=max_concurrent_checks,
        result_retention=result_retention
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_health_checker():
        """Test the health checker."""
        checker = create_health_checker(default_interval=10)
        
        # Add status change handler
        async def status_handler(check_id, old_status, new_status):
            print(f"Status change: {check_id} {old_status} -> {new_status}")
        
        checker.add_status_change_handler(status_handler)
        
        # Start checker
        await checker.start()
        
        # Add a custom HTTP check
        http_check = HealthCheck(
            check_id="google_check",
            name="Google HTTP Check",
            check_type=CheckType.HTTP,
            target="https://www.google.com",
            interval=15
        )
        await checker.add_health_check(http_check)
        
        # Let it run and perform checks
        await asyncio.sleep(30)
        
        # Get health status
        overall = await checker.get_overall_health()
        print(f"Overall health: {overall}")
        
        # Generate health report
        report = await checker.get_health_report()
        print(f"Health report generated with {len(report['checks'])} checks")
        
        # Stop checker
        await checker.stop()
    
    # Run test
    asyncio.run(test_health_checker())