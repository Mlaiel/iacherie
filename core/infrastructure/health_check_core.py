"""
Health Check Core module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Core Infrastructure - Advanced Health Check Engine
=========================================================

Enterprise-grade health checking system for distributed microservices
with deep health monitoring, dependency tracking, circuit breaker
integration, and comprehensive reporting capabilities.

Features:
- Multi-layer health checking (shallow, deep, critical)
- Dependency health tracking and cascade monitoring
- Integration with circuit breakers and load balancers
- Custom health check plugins and extensions
- Real-time health metrics and alerting
- Health check aggregation across service clusters
- SLA monitoring and health scoring
- Integration with monitoring systems (Prometheus, Grafana)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union, Set, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp
import psutil
from datetime import datetime, timedelta
import hashlib
import threading
import statistics
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class HealthCheckType(str, Enum):
    """Types of health checks"""
    SHALLOW = "shallow"      # Quick checks (< 100ms)
    DEEP = "deep"           # Thorough checks (< 1s)
    CRITICAL = "critical"   # Essential service checks
    DEPENDENCY = "dependency" # External dependency checks
    CUSTOM = "custom"       # User-defined checks

class HealthCheckPriority(str, Enum):
    """Health check priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "error": self.error
        }

@dataclass
class HealthCheckConfig:
    """Configuration for a health check"""
    name: str
    check_type: HealthCheckType
    priority: HealthCheckPriority = HealthCheckPriority.MEDIUM
    interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3
    success_threshold: int = 2
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceHealth:
    """Overall health status of a service"""
    service_name: str
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    score: float = 100.0  # Health score 0-100
    uptime_percentage: float = 100.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    dependencies_healthy: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "service_name": self.service_name,
            "overall_status": self.overall_status.value,
            "score": self.score,
            "uptime_percentage": self.uptime_percentage,
            "last_updated": self.last_updated.isoformat(),
            "dependencies_healthy": self.dependencies_healthy,
            "checks": [check.to_dict() for check in self.checks]
        }

class HealthChecker(ABC):
    """Abstract base class for health checkers"""
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform health check"""
        pass

class DatabaseHealthChecker(HealthChecker):
    """Database connectivity health checker"""
    
    def __init__(self, db_pool -> None: Any, name -> None: str = "database") -> None:
        self.db_pool = db_pool
        self.name = name
    
    async def check(self) -> HealthCheckResult:
        """Check database connectivity"""
        start_time = time.time()
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Database connection failed",
                duration_ms=duration,
                error=str(e)
            )

class RedisHealthChecker(HealthChecker):
    """Redis connectivity health checker"""
    
    def __init__(self, redis_client -> None: Any, name -> None: str = "redis") -> None:
        self.redis_client = redis_client
        self.name = name
    
    async def check(self) -> HealthCheckResult:
        """Check Redis connectivity"""
        start_time = time.time()
        try:
            await self.redis_client.ping()
            
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Redis connection failed",
                duration_ms=duration,
                error=str(e)
            )

class HttpServiceHealthChecker(HealthChecker):
    """HTTP service health checker"""
    
    def __init__(self, url -> None: str, name -> None: str, timeout -> None: int = 5) -> None:
        self.url = url
        self.name = name
        self.timeout = timeout
    
    async def check(self) -> HealthCheckResult:
        """Check HTTP service availability"""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=self.timeout) as response:
                    duration = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"HTTP service responded with {response.status}",
                            duration_ms=duration,
                            metadata={"status_code": response.status}
                        )
                    else:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"HTTP service responded with {response.status}",
                            duration_ms=duration,
                            metadata={"status_code": response.status}
                        )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="HTTP service unreachable",
                duration_ms=duration,
                error=str(e)
            )

class SystemResourcesHealthChecker(HealthChecker):
    """System resources health checker"""
    
    def __init__(self, name -> None: str = "system_resources") -> None:
        self.name = name
    
    async def check(self) -> HealthCheckResult:
        """Check system resources"""
        start_time = time.time()
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            duration = (time.time() - start_time) * 1000
            
            # Determine status based on thresholds
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"CPU usage critical: {cpu_percent}%")
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                issues.append(f"CPU usage high: {cpu_percent}%")
            
            if memory.percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"Memory usage critical: {memory.percent}%")
            elif memory.percent > 80:
                status = HealthStatus.DEGRADED
                issues.append(f"Memory usage high: {memory.percent}%")
            
            if disk.percent > 95:
                status = HealthStatus.CRITICAL
                issues.append(f"Disk usage critical: {disk.percent}%")
            elif disk.percent > 85:
                status = HealthStatus.DEGRADED
                issues.append(f"Disk usage high: {disk.percent}%")
            
            message = "System resources normal" if not issues else "; ".join(issues)
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                duration_ms=duration,
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3)
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="Failed to check system resources",
                duration_ms=duration,
                error=str(e)
            )

class CustomHealthChecker(HealthChecker):
    """Custom health checker with user-defined function"""
    
    def __init__(self, name -> None: str, check_function -> None: Callable[[], Any]) -> None:
        self.name = name
        self.check_function = check_function
    
    async def check(self) -> HealthCheckResult:
        """Execute custom health check"""
        start_time = time.time()
        try:
            result = self.check_function()
            if asyncio.iscoroutine(result):
                result = await result
            
            duration = (time.time() - start_time) * 1000
            
            # Handle different return types
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Custom check passed" if result else "Custom check failed"
            elif isinstance(result, dict):
                status = HealthStatus(result.get('status', 'healthy'))
                message = result.get('message', 'Custom check completed')
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Custom check failed",
                duration_ms=duration,
                error=str(e)
            )

@dataclass
class HealthCheckHistory:
    """Historical health check data"""
    results: List[HealthCheckResult] = field(default_factory=list)
    max_history: int = 100
    
    def add_result(self, result -> None: HealthCheckResult) -> None:
        """Add health check result to history"""
        self.results.append(result)
        if len(self.results) > self.max_history:
            self.results.pop(0)
    
    def get_uptime_percentage(self, since: Optional[datetime] = None) -> float:
        """Calculate uptime percentage"""
        if not self.results:
            return 100.0
        
        relevant_results = self.results
        if since:
            relevant_results = [r for r in self.results if r.timestamp >= since]
        
        if not relevant_results:
            return 100.0
        
        healthy_count = sum(1 for r in relevant_results 
                          if r.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED])
        return (healthy_count / len(relevant_results)) * 100.0
    
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if not self.results:
            return 0.0
        
        response_times = [r.duration_ms for r in self.results if r.duration_ms > 0]
        return statistics.mean(response_times) if response_times else 0.0
    
    def get_failure_rate(self) -> float:
        """Get failure rate percentage"""
        if not self.results:
            return 0.0
        
        failed_count = sum(1 for r in self.results 
                         if r.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL])
        return (failed_count / len(self.results)) * 100.0

class HealthCheckCore:
    """Advanced enterprise health check core"""
    
    def __init__(self, level -> None: str = "enterprise", service_name -> None: str = "ainflue-service") -> None:
        self.level = level
        self.service_name = service_name
        self.checkers: Dict[str, HealthChecker] = {}
        self.configs: Dict[str, HealthCheckConfig] = {}
        self.history: Dict[str, HealthCheckHistory] = {}
        self.current_results: Dict[str, HealthCheckResult] = {}
        self.failure_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
        self.enabled = True
        self._check_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        
        # Performance settings based on level
        self.performance_config = self._get_performance_config()
        
        # Health check scheduling
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
    def _get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration based on level"""
        configs = {
            "basic": {
                "max_checkers": 10,
                "history_retention": 50,
                "check_timeout": 5,
                "max_concurrent": 3
            },
            "standard": {
                "max_checkers": 25,
                "history_retention": 100,
                "check_timeout": 10,
                "max_concurrent": 5
            },
            "professional": {
                "max_checkers": 50,
                "history_retention": 200,
                "check_timeout": 15,
                "max_concurrent": 10
            },
            "enterprise": {
                "max_checkers": 100,
                "history_retention": 500,
                "check_timeout": 30,
                "max_concurrent": 20
            }
        }
        return configs.get(self.level, configs["enterprise"])
    
    async def initialize(self) -> bool:
        """Initialize health check system"""
        try:
            logger.info(f"🚀 Initializing HealthCheckCore - Level: {self.level}")
            
            # Add default health checkers
            await self._add_default_checkers()
            
            # Start health check scheduler
            await self.start_scheduler()
            
            logger.info("✅ HealthCheckCore initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize HealthCheckCore: {e}")
            return False
    
    async def _add_default_checkers(self) -> None:
        """Add default health checkers"""
        # System resources checker
        system_checker = SystemResourcesHealthChecker()
        await self.add_checker(
            "system_resources",
            system_checker,
            HealthCheckConfig(
                name="system_resources",
                check_type=HealthCheckType.CRITICAL,
                priority=HealthCheckPriority.HIGH,
                interval_seconds=30
            )
        )
        
        # Add custom memory check
        async def memory_check() -> None:
            memory = psutil.virtual_memory()
            return {
                'status': 'healthy' if memory.percent < 85 else 'degraded',
                'message': f'Memory usage: {memory.percent}%'
            }
        
        memory_checker = CustomHealthChecker("memory_detailed", memory_check)
        await self.add_checker(
            "memory_detailed",
            memory_checker,
            HealthCheckConfig(
                name="memory_detailed",
                check_type=HealthCheckType.SHALLOW,
                priority=HealthCheckPriority.MEDIUM,
                interval_seconds=60
            )
        )
    
    async def add_checker(
        self, 
        name: str, 
        checker: HealthChecker, 
        config: HealthCheckConfig
    ) -> bool:
        """Add health checker"""
        try:
            async with self._lock:
                if len(self.checkers) >= self.performance_config["max_checkers"]:
                    logger.warning(f"Maximum number of checkers reached: {self.performance_config['max_checkers']}")
                    return False
                
                self.checkers[name] = checker
                self.configs[name] = config
                self.history[name] = HealthCheckHistory(
                    max_history=self.performance_config["history_retention"]
                )
                self.failure_counts[name] = 0
                self.success_counts[name] = 0
                
                # Start individual checker task if scheduler is running
                if self.scheduler_running:
                    await self._start_checker_task(name)
                
                logger.info(f"✅ Health checker added: {name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add health checker {name}: {e}")
            return False
    
    async def remove_checker(self, name: str) -> bool:
        """Remove health checker"""
        try:
            async with self._lock:
                if name in self._check_tasks:
                    self._check_tasks[name].cancel()
                    del self._check_tasks[name]
                
                self.checkers.pop(name, None)
                self.configs.pop(name, None)
                self.history.pop(name, None)
                self.current_results.pop(name, None)
                self.failure_counts.pop(name, None)
                self.success_counts.pop(name, None)
                
                logger.info(f"✅ Health checker removed: {name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to remove health checker {name}: {e}")
            return False
    
    async def add_database_checker(self, name: str, db_pool: Any) -> bool:
        """Add database health checker"""
        checker = DatabaseHealthChecker(db_pool, name)
        config = HealthCheckConfig(
            name=name,
            check_type=HealthCheckType.CRITICAL,
            priority=HealthCheckPriority.CRITICAL,
            interval_seconds=30,
            failure_threshold=2
        )
        return await self.add_checker(name, checker, config)
    
    async def add_redis_checker(self, name: str, redis_client: Any) -> bool:
        """Add Redis health checker"""
        checker = RedisHealthChecker(redis_client, name)
        config = HealthCheckConfig(
            name=name,
            check_type=HealthCheckType.CRITICAL,
            priority=HealthCheckPriority.HIGH,
            interval_seconds=30,
            failure_threshold=2
        )
        return await self.add_checker(name, checker, config)
    
    async def add_http_service_checker(self, name: str, url: str, timeout: int = 5) -> bool:
        """Add HTTP service health checker"""
        checker = HttpServiceHealthChecker(url, name, timeout)
        config = HealthCheckConfig(
            name=name,
            check_type=HealthCheckType.DEPENDENCY,
            priority=HealthCheckPriority.MEDIUM,
            interval_seconds=60,
            timeout_seconds=timeout,
            failure_threshold=3
        )
        return await self.add_checker(name, checker, config)
    
    async def add_custom_checker(
        self, 
        name: str, 
        check_function: Callable[[], Any], 
        config: Optional[HealthCheckConfig] = None
    ) -> bool:
        """Add custom health checker"""
        checker = CustomHealthChecker(name, check_function)
        if not config:
            config = HealthCheckConfig(
                name=name,
                check_type=HealthCheckType.CUSTOM,
                priority=HealthCheckPriority.MEDIUM,
                interval_seconds=60
            )
        return await self.add_checker(name, checker, config)
    
    async def check_health(self, checker_name: Optional[str] = None) -> Union[HealthCheckResult, Dict[str, HealthCheckResult]]:
        """Run health check(s)"""
        if checker_name:
            return await self._run_single_check(checker_name)
        else:
            return await self._run_all_checks()
    
    async def _run_single_check(self, name: str) -> Optional[HealthCheckResult]:
        """Run single health check"""
        try:
            checker = self.checkers.get(name)
            config = self.configs.get(name)
            
            if not checker or not config or not config.enabled:
                return None
            
            # Run check with timeout
            result = await asyncio.wait_for(
                checker.check(),
                timeout=config.timeout_seconds
            )
            
            # Update history and counters
            self.history[name].add_result(result)
            self.current_results[name] = result
            
            if result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                self.success_counts[name] += 1
                self.failure_counts[name] = 0  # Reset failure count on success
            else:
                self.failure_counts[name] += 1
                self.success_counts[name] = 0  # Reset success count on failure
            
            return result
            
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
                error="Timeout exceeded"
            )
            self.history[name].add_result(result)
            self.current_results[name] = result
            self.failure_counts[name] += 1
            return result
            
        except Exception as e:
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="Health check failed",
                error=str(e)
            )
            self.history[name].add_result(result)
            self.current_results[name] = result
            self.failure_counts[name] += 1
            return result
    
    async def _run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks concurrently"""
        semaphore = asyncio.Semaphore(self.performance_config["max_concurrent"])
        
        async def run_with_semaphore(name -> None: str) -> None:
            async with semaphore:
                return await self._run_single_check(name)
        
        tasks = [
            run_with_semaphore(name) 
            for name in self.checkers.keys()
            if self.configs[name].enabled
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            name: result for name, result in zip(self.checkers.keys(), results)
            if isinstance(result, HealthCheckResult)
        }
    
    async def get_service_health(self) -> ServiceHealth:
        """Get overall service health"""
        # Run all checks
        check_results = await self._run_all_checks()
        
        # Calculate overall status and score
        overall_status = self._calculate_overall_status(check_results)
        health_score = self._calculate_health_score(check_results)
        uptime_percentage = self._calculate_uptime_percentage()
        dependencies_healthy = self._check_dependencies_health(check_results)
        
        return ServiceHealth(
            service_name=self.service_name,
            overall_status=overall_status,
            checks=list(check_results.values()),
            score=health_score,
            uptime_percentage=uptime_percentage,
            dependencies_healthy=dependencies_healthy
        )
    
    def _calculate_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """Calculate overall health status"""
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in results.values()]
        
        # If any critical check is unhealthy, overall is critical
        critical_checks = [
            result for result in results.values()
            if self.configs.get(result.name, {}).priority == HealthCheckPriority.CRITICAL
        ]
        
        if any(check.status == HealthStatus.CRITICAL for check in critical_checks):
            return HealthStatus.CRITICAL
        
        if any(check.status == HealthStatus.UNHEALTHY for check in critical_checks):
            return HealthStatus.UNHEALTHY
        
        # Check overall status distribution
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.DEGRADED
    
    def _calculate_health_score(self, results: Dict[str, HealthCheckResult]) -> float:
        """Calculate health score (0-100)"""
        if not results:
            return 0.0
        
        total_weight = 0
        weighted_score = 0
        
        for result in results.values():
            config = self.configs.get(result.name)
            if not config:
                continue
            
            # Weight based on priority
            weight = {
                HealthCheckPriority.LOW: 1,
                HealthCheckPriority.MEDIUM: 2,
                HealthCheckPriority.HIGH: 3,
                HealthCheckPriority.CRITICAL: 5
            }.get(config.priority, 1)
            
            # Score based on status
            score = {
                HealthStatus.HEALTHY: 100,
                HealthStatus.DEGRADED: 75,
                HealthStatus.UNHEALTHY: 25,
                HealthStatus.CRITICAL: 0,
                HealthStatus.UNKNOWN: 50
            }.get(result.status, 0)
            
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_uptime_percentage(self) -> float:
        """Calculate overall uptime percentage"""
        if not self.history:
            return 100.0
        
        # Calculate uptime for last 24 hours
        since = datetime.utcnow() - timedelta(hours=24)
        uptimes = [
            history.get_uptime_percentage(since)
            for history in self.history.values()
        ]
        
        return statistics.mean(uptimes) if uptimes else 100.0
    
    def _check_dependencies_health(self, results: Dict[str, HealthCheckResult]) -> bool:
        """Check if all dependencies are healthy"""
        dependency_checks = [
            result for result in results.values()
            if self.configs.get(result.name, {}).check_type == HealthCheckType.DEPENDENCY
        ]
        
        return all(
            check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            for check in dependency_checks
        )
    
    async def start_scheduler(self) -> bool:
        """Start health check scheduler"""
        try:
            if self.scheduler_running:
                return True
            
            self.scheduler_running = True
            
            # Start individual checker tasks
            for name in self.checkers.keys():
                await self._start_checker_task(name)
            
            logger.info("✅ Health check scheduler started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start health check scheduler: {e}")
            return False
    
    async def _start_checker_task(self, name -> None: str) -> None:
        """Start individual health checker task"""
        config = self.configs[name]
        
        async def checker_loop() -> None:
            while self.scheduler_running and config.enabled:
                try:
                    await self._run_single_check(name)
                    await asyncio.sleep(config.interval_seconds)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in health checker {name}: {e}")
                    await asyncio.sleep(config.interval_seconds)
        
        self._check_tasks[name] = asyncio.create_task(checker_loop())
    
    async def stop_scheduler(self) -> bool:
        """Stop health check scheduler"""
        try:
            self.scheduler_running = False
            
            # Cancel all checker tasks
            for task in self._check_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._check_tasks.values(), return_exceptions=True)
            
            self._check_tasks.clear()
            logger.info("✅ Health check scheduler stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop health check scheduler: {e}")
            return False
    
    async def get_checker_history(self, name: str) -> Optional[HealthCheckHistory]:
        """Get history for specific checker"""
        return self.history.get(name)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get health check metrics"""
        total_checks = len(self.checkers)
        enabled_checks = sum(1 for config in self.configs.values() if config.enabled)
        
        # Calculate average response times
        avg_response_times = {}
        for name, history in self.history.items():
            avg_response_times[name] = history.get_average_response_time()
        
        # Calculate failure rates
        failure_rates = {}
        for name, history in self.history.items():
            failure_rates[name] = history.get_failure_rate()
        
        return {
            "total_checkers": total_checks,
            "enabled_checkers": enabled_checks,
            "scheduler_running": self.scheduler_running,
            "average_response_times": avg_response_times,
            "failure_rates": failure_rates,
            "current_results": {
                name: result.to_dict() 
                for name, result in self.current_results.items()
            }
        }
    
    async def health_check(self) -> bool:
        """Self health check"""
        try:
            # Check if scheduler is running and we have checkers
            return self.scheduler_running and len(self.checkers) > 0
        except Exception as e:
            logger.error(f"HealthCheckCore self-check failed: {e}")
            return False
    
    async def start(self) -> bool:
        """Start health check service"""
        try:
            logger.info("🚀 Starting HealthCheckCore service")
            return await self.start_scheduler()
        except Exception as e:
            logger.error(f"❌ Failed to start HealthCheckCore: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop health check service"""
        try:
            logger.info("🛑 Stopping HealthCheckCore service")
            return await self.stop_scheduler()
        except Exception as e:
            logger.error(f"❌ Failed to stop HealthCheckCore: {e}")
            return False

# Export main classes
__all__ = [
    "HealthCheckCore", "HealthChecker", "HealthCheckResult", "HealthCheckConfig",
    "ServiceHealth", "HealthStatus", "HealthCheckType", "HealthCheckPriority",
    "DatabaseHealthChecker", "RedisHealthChecker", "HttpServiceHealthChecker",
    "SystemResourcesHealthChecker", "CustomHealthChecker"
]