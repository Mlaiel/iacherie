"""
Enterprise-grade health checking system for IA Influencer Agent.
Professional health monitoring with comprehensive dependency checks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import time
import threading
from contextlib import asynccontextmanager


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of system components."""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    QUEUE = "queue"
    STORAGE = "storage"
    SERVICE = "service"
    NETWORK = "network"
    SYSTEM = "system"


@dataclass
class HealthCheckResult:
    """Result of individual health check."""
    component_name: str
    component_type: ComponentType
    status: HealthStatus
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: Optional[float] = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_name": self.component_name,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "response_time_ms": self.response_time_ms,
            "checked_at": self.checked_at.isoformat(),
            "tags": self.tags
        }


@dataclass
class SystemHealthStatus:
    """Overall system health status."""
    overall_status: HealthStatus
    component_results: List[HealthCheckResult] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    uptime_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "status": self.overall_status.value,
            "version": self.version,
            "checked_at": self.checked_at.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "components": {
                result.component_name: result.to_dict()
                for result in self.component_results
            }
        }
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.overall_status == HealthStatus.HEALTHY
    
    @property
    def unhealthy_components(self) -> List[HealthCheckResult]:
        """Get list of unhealthy components."""
        return [
            result for result in self.component_results
            if result.status == HealthStatus.UNHEALTHY
        ]
    
    @property
    def degraded_components(self) -> List[HealthCheckResult]:
        """Get list of degraded components."""
        return [
            result for result in self.component_results
            if result.status == HealthStatus.DEGRADED
        ]


class IHealthCheck(ABC):
    """Interface for health check implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Health check name."""
        pass
    
    @property
    @abstractmethod
    def component_type(self) -> ComponentType:
        """Component type being checked."""
        pass
    
    @abstractmethod
    async def check_health(self) -> HealthCheckResult:
        """Execute health check and return result."""
        pass
    
    @property
    def timeout_seconds(self) -> float:
        """Health check timeout in seconds."""
        return 5.0
    
    @property
    def tags(self) -> Dict[str, str]:
        """Additional tags for the health check."""
        return {}


class DatabaseHealthCheck(IHealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, name: str, connection_factory: Callable):
        self._name = name
        self.connection_factory = connection_factory
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def component_type(self) -> ComponentType:
        return ComponentType.DATABASE
    
    async def check_health(self) -> HealthCheckResult:
        """Check database connectivity and responsiveness."""
        start_time = time.perf_counter()
        
        try:
            # Attempt to get connection and execute simple query
            async with self.connection_factory() as conn:
                await conn.execute("SELECT 1")
            
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time_ms
            )
        
        except Exception as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time_ms,
                details={"error": str(e)}
            )


class RedisHealthCheck(IHealthCheck):
    """Health check for Redis cache connectivity."""
    
    def __init__(self, name: str, redis_client):
        self._name = name
        self.redis_client = redis_client
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def component_type(self) -> ComponentType:
        return ComponentType.CACHE
    
    async def check_health(self) -> HealthCheckResult:
        """Check Redis connectivity and responsiveness."""
        start_time = time.perf_counter()
        
        try:
            # Test Redis connection with ping
            await self.redis_client.ping()
            
            # Test basic operations
            test_key = "health_check_test"
            await self.redis_client.set(test_key, "ok", ex=60)
            value = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)
            
            if value != b"ok":
                raise Exception("Redis set/get test failed")
            
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                response_time_ms=response_time_ms
            )
        
        except Exception as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=response_time_ms,
                details={"error": str(e)}
            )


class ExternalAPIHealthCheck(IHealthCheck):
    """Health check for external API dependencies."""
    
    def __init__(self, name: str, url: str, http_client, expected_status: int = 200):
        self._name = name
        self.url = url
        self.http_client = http_client
        self.expected_status = expected_status
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def component_type(self) -> ComponentType:
        return ComponentType.EXTERNAL_API
    
    @property
    def timeout_seconds(self) -> float:
        return 10.0
    
    async def check_health(self) -> HealthCheckResult:
        """Check external API availability."""
        start_time = time.perf_counter()
        
        try:
            async with self.http_client.get(
                self.url,
                timeout=self.timeout_seconds
            ) as response:
                response_time_ms = (time.perf_counter() - start_time) * 1000
                
                if response.status == self.expected_status:
                    return HealthCheckResult(
                        component_name=self.name,
                        component_type=self.component_type,
                        status=HealthStatus.HEALTHY,
                        message=f"API responded with status {response.status}",
                        response_time_ms=response_time_ms,
                        details={"status_code": response.status}
                    )
                else:
                    return HealthCheckResult(
                        component_name=self.name,
                        component_type=self.component_type,
                        status=HealthStatus.DEGRADED,
                        message=f"API returned unexpected status {response.status}",
                        response_time_ms=response_time_ms,
                        details={"status_code": response.status}
                    )
        
        except Exception as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"API health check failed: {str(e)}",
                response_time_ms=response_time_ms,
                details={"error": str(e)}
            )


class StorageHealthCheck(IHealthCheck):
    """Health check for storage systems (S3, file system, etc.)."""
    
    def __init__(self, name: str, storage_client):
        self._name = name
        self.storage_client = storage_client
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def component_type(self) -> ComponentType:
        return ComponentType.STORAGE
    
    async def check_health(self) -> HealthCheckResult:
        """Check storage system availability."""
        start_time = time.perf_counter()
        
        try:
            # Test storage connectivity (implementation depends on storage type)
            # This is a generic example - implement specific logic for your storage
            test_data = b"health_check_test_data"
            test_key = f"health_check/{datetime.now().isoformat()}"
            
            # Upload test data
            await self.storage_client.put_object(test_key, test_data)
            
            # Download and verify
            retrieved_data = await self.storage_client.get_object(test_key)
            
            # Cleanup
            await self.storage_client.delete_object(test_key)
            
            if retrieved_data != test_data:
                raise Exception("Storage data integrity check failed")
            
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.HEALTHY,
                message="Storage system operational",
                response_time_ms=response_time_ms
            )
        
        except Exception as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=self.name,
                component_type=self.component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Storage health check failed: {str(e)}",
                response_time_ms=response_time_ms,
                details={"error": str(e)}
            )


class HealthCheckManager:
    """Manager for coordinating health checks."""
    
    def __init__(self, app_version: str = "1.0.0"):
        self.app_version = app_version
        self.start_time = datetime.now(timezone.utc)
        self._health_checks: Dict[str, IHealthCheck] = {}
        self._lock = threading.RLock()
    
    def register_health_check(self, health_check: IHealthCheck) -> None:
        """Register a health check."""
        with self._lock:
            self._health_checks[health_check.name] = health_check
    
    def unregister_health_check(self, name: str) -> bool:
        """Unregister a health check."""
        with self._lock:
            if name in self._health_checks:
                del self._health_checks[name]
                return True
            return False
    
    async def check_health(self, component_name: Optional[str] = None) -> SystemHealthStatus:
        """Execute health checks and return system status."""
        if component_name:
            # Check specific component
            if component_name not in self._health_checks:
                return SystemHealthStatus(
                    overall_status=HealthStatus.UNKNOWN,
                    component_results=[],
                    version=self.app_version,
                    uptime_seconds=self._get_uptime_seconds()
                )
            
            health_check = self._health_checks[component_name]
            result = await self._execute_health_check(health_check)
            
            return SystemHealthStatus(
                overall_status=result.status,
                component_results=[result],
                version=self.app_version,
                uptime_seconds=self._get_uptime_seconds()
            )
        
        # Check all components
        health_checks = list(self._health_checks.values())
        
        # Execute all health checks concurrently
        tasks = [self._execute_health_check(hc) for hc in health_checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        component_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Health check failed with exception
                component_results.append(HealthCheckResult(
                    component_name=health_checks[i].name,
                    component_type=health_checks[i].component_type,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check exception: {str(result)}",
                    details={"error": str(result)}
                ))
            else:
                component_results.append(result)
        
        # Determine overall status
        overall_status = self._calculate_overall_status(component_results)
        
        return SystemHealthStatus(
            overall_status=overall_status,
            component_results=component_results,
            version=self.app_version,
            uptime_seconds=self._get_uptime_seconds()
        )
    
    async def _execute_health_check(self, health_check: IHealthCheck) -> HealthCheckResult:
        """Execute single health check with timeout."""
        try:
            return await asyncio.wait_for(
                health_check.check_health(),
                timeout=health_check.timeout_seconds
            )
        except asyncio.TimeoutError:
            return HealthCheckResult(
                component_name=health_check.name,
                component_type=health_check.component_type,
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
                response_time_ms=health_check.timeout_seconds * 1000,
                details={"timeout_seconds": health_check.timeout_seconds}
            )
        except Exception as e:
            return HealthCheckResult(
                component_name=health_check.name,
                component_type=health_check.component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall system status from component results."""
        if not results:
            return HealthStatus.UNKNOWN
        
        unhealthy_count = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        
        # If any component is unhealthy, system is unhealthy
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        
        # If any component is degraded, system is degraded
        if degraded_count > 0:
            return HealthStatus.DEGRADED
        
        # All components healthy
        return HealthStatus.HEALTHY
    
    def _get_uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    def get_registered_checks(self) -> List[str]:
        """Get list of registered health check names."""
        with self._lock:
            return list(self._health_checks.keys())


class SimpleHealthCheck(IHealthCheck):
    """Simple health check that always returns healthy."""
    
    def __init__(self, name: str, component_type: ComponentType = ComponentType.SERVICE):
        self._name = name
        self._component_type = component_type
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def component_type(self) -> ComponentType:
        return self._component_type
    
    async def check_health(self) -> HealthCheckResult:
        """Always return healthy status."""
        return HealthCheckResult(
            component_name=self.name,
            component_type=self.component_type,
            status=HealthStatus.HEALTHY,
            message="Service is operational"
        )


# Global health check manager
_health_manager = HealthCheckManager()

# Register basic health checks
_health_manager.register_health_check(
    SimpleHealthCheck("application", ComponentType.SERVICE)
)


def get_health_manager() -> HealthCheckManager:
    """Get global health check manager."""
    return _health_manager


def register_health_check(health_check: IHealthCheck) -> None:
    """Register a health check with global manager."""
    _health_manager.register_health_check(health_check)


async def check_system_health() -> SystemHealthStatus:
    """Check overall system health."""
    return await _health_manager.check_health()


async def check_component_health(component_name: str) -> SystemHealthStatus:
    """Check specific component health."""
    return await _health_manager.check_health(component_name)
