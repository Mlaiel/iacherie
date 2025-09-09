"""Health Check Utilities
Enterprise-grade health monitoring and system diagnostics for Ainflue Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Optional psutil import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: float
    duration: float


class HealthChecker:
    """
    Enterprise-grade health checking system with configurable checks,
    thresholds, and automatic monitoring.
    """
    
    def __init__(self, check_interval: int = 30):
        """Initialize health checker
        
        Args:
            check_interval: Interval in seconds between automatic health checks
        """
        self.check_interval = check_interval
        self.checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, HealthCheck] = {}
        self.thresholds: Dict[str, Dict] = {}
        self.running = False
        self.lock = threading.Lock()
        
        # Register default system checks
        self._register_system_checks()
        
        logger.info(f"HealthChecker initialized with check_interval={check_interval}s")
    
    def _register_system_checks(self):
        """Register built-in system health checks"""
        self.register_check("cpu_usage", self._check_cpu_usage)
        self.register_check("memory_usage", self._check_memory_usage)
        self.register_check("disk_usage", self._check_disk_usage)
        self.register_check("network_connectivity", self._check_network_connectivity)
        
        # Set default thresholds
        self.set_threshold("cpu_usage", warning=70, critical=90)
        self.set_threshold("memory_usage", warning=80, critical=95)
        self.set_threshold("disk_usage", warning=85, critical=95)
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check function
        
        Args:
            name: Unique name for the health check
            check_func: Function that returns HealthCheck result
        """
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    def set_threshold(self, check_name: str, warning: float, critical: float):
        """Set thresholds for a health check
        
        Args:
            check_name: Name of the health check
            warning: Warning threshold value
            critical: Critical threshold value
        """
        self.thresholds[check_name] = {
            "warning": warning,
            "critical": critical
        }
        logger.info(f"Set thresholds for {check_name}: warning={warning}, critical={critical}")
    
    async def run_check(self, name: str) -> HealthCheck:
        """Run a specific health check
        
        Args:
            name: Name of the health check to run
            
        Returns:
            HealthCheck result
        """
        if name not in self.checks:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' not found",
                details={},
                timestamp=time.time(),
                duration=0
            )
        
        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(self.checks[name]):
                result = await self.checks[name]()
            else:
                result = self.checks[name]()
            
            duration = time.time() - start_time
            
            if isinstance(result, HealthCheck):
                result.duration = duration
                return result
            else:
                # Convert simple return to HealthCheck
                return HealthCheck(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    message=str(result),
                    details={},
                    timestamp=time.time(),
                    duration=duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Health check '{name}' failed: {e}")
            return HealthCheck(
                name=name,
                status=HealthStatus.CRITICAL,
                message=f"Check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time(),
                duration=duration
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks
        
        Returns:
            Dictionary of health check results
        """
        results = {}
        
        # Run checks concurrently
        tasks = [self.run_check(name) for name in self.checks.keys()]
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(check_results):
            check_name = list(self.checks.keys())[i]
            if isinstance(result, Exception):
                results[check_name] = HealthCheck(
                    name=check_name,
                    status=HealthStatus.CRITICAL,
                    message=f"Check exception: {str(result)}",
                    details={"exception": str(result)},
                    timestamp=time.time(),
                    duration=0
                )
            else:
                results[check_name] = result
        
        # Store results
        with self.lock:
            self.last_results.update(results)
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.last_results:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in self.last_results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        overall_status = self.get_overall_status()
        
        summary = {
            "overall_status": overall_status.value,
            "timestamp": time.time(),
            "checks": len(self.checks),
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "unknown": 0,
            "details": {}
        }
        
        for name, result in self.last_results.items():
            summary["details"][name] = {
                "status": result.status.value,
                "message": result.message,
                "timestamp": result.timestamp,
                "duration": result.duration
            }
            
            # Count by status
            if result.status == HealthStatus.HEALTHY:
                summary["healthy"] += 1
            elif result.status == HealthStatus.WARNING:
                summary["warning"] += 1
            elif result.status == HealthStatus.CRITICAL:
                summary["critical"] += 1
            else:
                summary["unknown"] += 1
        
        return summary
    
    def start_monitoring(self):
        """Start automatic health monitoring"""
        if self.running:
            return
        
        self.running = True
        
        async def monitor_worker():
            while self.running:
                try:
                    await self.run_all_checks()
                    await asyncio.sleep(self.check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(5)  # Brief pause on error
        
        # Start monitoring in background
        asyncio.create_task(monitor_worker())
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic health monitoring"""
        self.running = False
        logger.info("Health monitoring stopped")
    
    # Built-in system health checks
    
    def _check_cpu_usage(self) -> HealthCheck:
        """Check CPU usage"""
        try:
            if not PSUTIL_AVAILABLE:
                return HealthCheck(
                    name="cpu_usage",
                    status=HealthStatus.UNKNOWN,
                    message="psutil not available for CPU monitoring",
                    details={"error": "psutil_missing"},
                    timestamp=time.time(),
                    duration=0
                )
            
            cpu_percent = psutil.cpu_percent(interval=1)
            thresholds = self.thresholds.get("cpu_usage", {"warning": 70, "critical": 90})
            
            if cpu_percent >= thresholds["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent >= thresholds["warning"]:
                status = HealthStatus.WARNING
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return HealthCheck(
                name="cpu_usage",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                timestamp=time.time(),
                duration=0
            )
            
        except Exception as e:
            return HealthCheck(
                name="cpu_usage",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check CPU usage: {e}",
                details={"error": str(e)},
                timestamp=time.time(),
                duration=0
            )
    
    def _check_memory_usage(self) -> HealthCheck:
        """Check memory usage"""
        try:
            if not PSUTIL_AVAILABLE:
                return HealthCheck(
                    name="memory_usage",
                    status=HealthStatus.UNKNOWN,
                    message="psutil not available for memory monitoring",
                    details={"error": "psutil_missing"},
                    timestamp=time.time(),
                    duration=0
                )
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            thresholds = self.thresholds.get("memory_usage", {"warning": 80, "critical": 95})
            
            if memory_percent >= thresholds["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory_percent:.1f}%"
            elif memory_percent >= thresholds["warning"]:
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_percent:.1f}%"
            
            return HealthCheck(
                name="memory_usage",
                status=status,
                message=message,
                details={
                    "memory_percent": memory_percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free
                },
                timestamp=time.time(),
                duration=0
            )
            
        except Exception as e:
            return HealthCheck(
                name="memory_usage",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check memory usage: {e}",
                details={"error": str(e)},
                timestamp=time.time(),
                duration=0
            )
    
    def _check_disk_usage(self) -> HealthCheck:
        """Check disk usage"""
        try:
            if not PSUTIL_AVAILABLE:
                return HealthCheck(
                    name="disk_usage",
                    status=HealthStatus.UNKNOWN,
                    message="psutil not available for disk monitoring",
                    details={"error": "psutil_missing"},
                    timestamp=time.time(),
                    duration=0
                )
            
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            thresholds = self.thresholds.get("disk_usage", {"warning": 85, "critical": 95})
            
            if disk_percent >= thresholds["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent >= thresholds["warning"]:
                status = HealthStatus.WARNING
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            
            return HealthCheck(
                name="disk_usage",
                status=status,
                message=message,
                details={
                    "disk_percent": disk_percent,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free
                },
                timestamp=time.time(),
                duration=0
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk_usage",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check disk usage: {e}",
                details={"error": str(e)},
                timestamp=time.time(),
                duration=0
            )
    
    def _check_network_connectivity(self) -> HealthCheck:
        """Check network connectivity"""
        try:
            import socket
            
            # Test DNS resolution
            socket.gethostbyname("google.com")
            
            # Test network interfaces if psutil available
            if PSUTIL_AVAILABLE:
                network_stats = psutil.net_if_stats()
                active_interfaces = sum(1 for interface, stats in network_stats.items() if stats.isup)
                interface_list = list(network_stats.keys())
            else:
                active_interfaces = 1  # Assume we have at least one since DNS worked
                interface_list = ["unknown"]
            
            if active_interfaces == 0:
                status = HealthStatus.CRITICAL
                message = "No active network interfaces"
            else:
                status = HealthStatus.HEALTHY
                message = f"Network connectivity OK ({active_interfaces} active interfaces)"
            
            return HealthCheck(
                name="network_connectivity",
                status=status,
                message=message,
                details={
                    "active_interfaces": active_interfaces,
                    "interfaces": interface_list
                },
                timestamp=time.time(),
                duration=0
            )
            
        except Exception as e:
            return HealthCheck(
                name="network_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Network connectivity failed: {e}",
                details={"error": str(e)},
                timestamp=time.time(),
                duration=0
            )


# Global health checker instance
_global_health_checker: Optional[HealthChecker] = None


def get_global_health_checker() -> HealthChecker:
    """Get global health checker instance"""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker


async def health_check() -> Dict[str, Any]:
    """Quick health check using global checker"""
    checker = get_global_health_checker()
    await checker.run_all_checks()
    return checker.get_health_summary()