"""Health Check Configuration for IA-Influencer Agent Platform
===========================================================

Professional health check configuration for microservices monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator
import aiohttp
import psutil
import redis
import psycopg2
from datetime import datetime, timedelta


class HealthStatus(str, Enum):
    """Health check status types."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthCheckType(str, Enum):
    """Health check types."""
    HTTP = "http"
    TCP = "tcp"
    DATABASE = "database"
    REDIS = "redis"
    CUSTOM = "custom"
    COMPOSITE = "composite"


class ServiceType(str, Enum):
    """Service types for health checking."""
    WEB_SERVICE = "web_service"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_BROKER = "message_broker"
    EXTERNAL_API = "external_api"
    STORAGE = "storage"


@dataclass
class HealthCheckResult:
    """Health check result data."""
    service_name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "service_name": self.service_name,
            "status": self.status.value,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "error": self.error
        }


@dataclass
class HealthCheckDefinition:
    """Health check definition."""
    name: str
    type: HealthCheckType
    service_type: ServiceType
    enabled: bool = True
    interval: int = 30  # seconds
    timeout: int = 10   # seconds
    retries: int = 3
    retry_delay: float = 1.0
    
    # HTTP specific
    url: Optional[str] = None
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    expected_status: int = 200
    expected_response: Optional[str] = None
    
    # TCP specific
    host: Optional[str] = None
    port: Optional[int] = None
    
    # Database specific
    connection_string: Optional[str] = None
    query: Optional[str] = None
    
    # Redis specific
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Custom check function
    custom_function: Optional[Callable] = None
    
    # Composite checks (list of other check names)
    composite_checks: List[str] = field(default_factory=list)
    
    # Alert thresholds
    warning_threshold: Optional[float] = None  # Response time in seconds
    critical_threshold: Optional[float] = None
    
    # Tags and metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthCheckConfig(BaseSettings):
    """
    Centralized health check configuration for microservices monitoring.
    Supports HTTP, TCP, database, Redis, and custom health checks.
    """
    
    # Global health check settings
    enabled: bool = Field(True, env="HEALTH_CHECK_ENABLED")
    global_interval: int = Field(30, env="HEALTH_CHECK_GLOBAL_INTERVAL")
    global_timeout: int = Field(10, env="HEALTH_CHECK_GLOBAL_TIMEOUT")
    global_retries: int = Field(3, env="HEALTH_CHECK_GLOBAL_RETRIES")
    
    # Health check API settings
    api_enabled: bool = Field(True, env="HEALTH_CHECK_API_ENABLED")
    api_host: str = Field("0.0.0.0", env="HEALTH_CHECK_API_HOST")
    api_port: int = Field(8888, env="HEALTH_CHECK_API_PORT")
    api_path: str = Field("/health", env="HEALTH_CHECK_API_PATH")
    api_detailed_path: str = Field("/health/detailed", env="HEALTH_CHECK_API_DETAILED_PATH")
    
    # Storage settings
    store_results: bool = Field(True, env="HEALTH_CHECK_STORE_RESULTS")
    results_retention_days: int = Field(7, env="HEALTH_CHECK_RESULTS_RETENTION_DAYS")
    redis_host: str = Field("localhost", env="HEALTH_CHECK_REDIS_HOST")
    redis_port: int = Field(6379, env="HEALTH_CHECK_REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="HEALTH_CHECK_REDIS_PASSWORD")
    redis_db: int = Field(1, env="HEALTH_CHECK_REDIS_DB")
    
    # Alerting settings
    alerting_enabled: bool = Field(True, env="HEALTH_CHECK_ALERTING_ENABLED")
    webhook_url: Optional[str] = Field(None, env="HEALTH_CHECK_WEBHOOK_URL")
    email_enabled: bool = Field(False, env="HEALTH_CHECK_EMAIL_ENABLED")
    email_smtp_host: Optional[str] = Field(None, env="HEALTH_CHECK_EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(587, env="HEALTH_CHECK_EMAIL_SMTP_PORT")
    email_username: Optional[str] = Field(None, env="HEALTH_CHECK_EMAIL_USERNAME")
    email_password: Optional[str] = Field(None, env="HEALTH_CHECK_EMAIL_PASSWORD")
    email_recipients: List[str] = Field([], env="HEALTH_CHECK_EMAIL_RECIPIENTS")
    
    # Graceful degradation settings
    degraded_threshold: float = Field(0.7, env="HEALTH_CHECK_DEGRADED_THRESHOLD")  # 70% services healthy
    circuit_breaker_threshold: float = Field(0.5, env="HEALTH_CHECK_CIRCUIT_BREAKER_THRESHOLD")  # 50% services healthy
    
    # System resource monitoring
    monitor_system_resources: bool = Field(True, env="HEALTH_CHECK_MONITOR_SYSTEM_RESOURCES")
    cpu_threshold: float = Field(80.0, env="HEALTH_CHECK_CPU_THRESHOLD")
    memory_threshold: float = Field(80.0, env="HEALTH_CHECK_MEMORY_THRESHOLD")
    disk_threshold: float = Field(90.0, env="HEALTH_CHECK_DISK_THRESHOLD")
    
    class Config:
        env_prefix = "HEALTH_CHECK_"
        case_sensitive = False


class HealthChecker:
    """
    Production-ready health checker with support for multiple check types.
    """
    
    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self.checks: Dict[str, HealthCheckDefinition] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        
        if config.store_results:
            try:
                self.redis_client = redis.Redis(
                    host=config.redis_host,
                    port=config.redis_port,
                    password=config.redis_password,
                    db=config.redis_db,
                    decode_responses=True
                )
            except Exception as e:
                print(f"Warning: Failed to connect to Redis for health check storage: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def add_check(self, check: HealthCheckDefinition):
        """Add health check definition."""
        self.checks[check.name] = check
    
    def remove_check(self, name: str):
        """Remove health check definition."""
        if name in self.checks:
            del self.checks[name]
        if name in self.results:
            del self.results[name]
    
    async def check_http(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Perform HTTP health check."""
        start_time = time.time()
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.request(
                check.method,
                check.url,
                headers=check.headers,
                timeout=aiohttp.ClientTimeout(total=check.timeout)
            ) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                status = HealthStatus.HEALTHY
                error = None
                
                if response.status != check.expected_status:
                    status = HealthStatus.UNHEALTHY
                    error = f"Expected status {check.expected_status}, got {response.status}"
                
                if check.expected_response and check.expected_response not in response_text:
                    status = HealthStatus.UNHEALTHY
                    error = f"Expected response content not found"
                
                # Check response time thresholds
                if check.critical_threshold and response_time > check.critical_threshold:
                    status = HealthStatus.UNHEALTHY
                    error = f"Response time {response_time:.2f}s exceeds critical threshold {check.critical_threshold}s"
                elif check.warning_threshold and response_time > check.warning_threshold:
                    status = HealthStatus.DEGRADED
                    error = f"Response time {response_time:.2f}s exceeds warning threshold {check.warning_threshold}s"
                
                return HealthCheckResult(
                    service_name=check.name,
                    status=status,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={
                        "status_code": response.status,
                        "response_size": len(response_text),
                        "url": check.url
                    },
                    error=error
                )
        
        except Exception as e:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def check_tcp(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Perform TCP health check."""
        start_time = time.time()
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(check.host, check.port),
                timeout=check.timeout
            )
            writer.close()
            await writer.wait_closed()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                details={
                    "host": check.host,
                    "port": check.port
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def check_database(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Perform database health check."""
        start_time = time.time()
        
        try:
            conn = psycopg2.connect(check.connection_string)
            cursor = conn.cursor()
            
            query = check.query or "SELECT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                details={
                    "query": query,
                    "result": str(result) if result else None
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def check_redis(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Perform Redis health check."""
        start_time = time.time()
        
        try:
            redis_client = redis.Redis(
                host=check.redis_host,
                port=check.redis_port,
                password=check.redis_password,
                db=check.redis_db,
                socket_timeout=check.timeout
            )
            
            # Test ping
            redis_client.ping()
            
            # Test set/get
            test_key = f"health_check_{check.name}_{int(time.time())}"
            redis_client.set(test_key, "test_value", ex=60)
            value = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                details={
                    "host": check.redis_host,
                    "port": check.redis_port,
                    "db": check.redis_db,
                    "test_successful": value == b"test_value"
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def check_custom(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Perform custom health check."""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(check.custom_function):
                result = await check.custom_function()
            else:
                result = check.custom_function()
            
            response_time = time.time() - start_time
            
            if isinstance(result, HealthCheckResult):
                result.response_time = response_time
                return result
            elif isinstance(result, bool):
                return HealthCheckResult(
                    service_name=check.name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    response_time=response_time,
                    timestamp=datetime.now()
                )
            else:
                return HealthCheckResult(
                    service_name=check.name,
                    status=HealthStatus.HEALTHY,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={"result": str(result)}
                )
        
        except Exception as e:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def check_composite(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Perform composite health check."""
        start_time = time.time()
        
        results = []
        for check_name in check.composite_checks:
            if check_name in self.results:
                results.append(self.results[check_name])
        
        if not results:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNKNOWN,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error="No composite check results available"
            )
        
        # Determine overall status
        healthy_count = sum(1 for r in results if r.status == HealthStatus.HEALTHY)
        total_count = len(results)
        health_ratio = healthy_count / total_count
        
        if health_ratio >= self.config.degraded_threshold:
            status = HealthStatus.HEALTHY
        elif health_ratio >= self.config.circuit_breaker_threshold:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        return HealthCheckResult(
            service_name=check.name,
            status=status,
            response_time=time.time() - start_time,
            timestamp=datetime.now(),
            details={
                "healthy_services": healthy_count,
                "total_services": total_count,
                "health_ratio": health_ratio,
                "component_results": [r.to_dict() for r in results]
            }
        )
    
    async def check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage."""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > self.config.cpu_threshold:
                status = HealthStatus.DEGRADED
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > self.config.memory_threshold:
                if status != HealthStatus.UNHEALTHY:
                    status = HealthStatus.DEGRADED
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > self.config.disk_threshold:
                status = HealthStatus.UNHEALTHY
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            return HealthCheckResult(
                service_name="system_resources",
                status=status,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                },
                error="; ".join(issues) if issues else None
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name="system_resources",
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def run_single_check(self, check: HealthCheckDefinition) -> HealthCheckResult:
        """Run a single health check with retries."""
        if not check.enabled:
            return HealthCheckResult(
                service_name=check.name,
                status=HealthStatus.UNKNOWN,
                response_time=0.0,
                timestamp=datetime.now(),
                error="Check disabled"
            )
        
        last_error = None
        
        for attempt in range(check.retries):
            try:
                if check.type == HealthCheckType.HTTP:
                    result = await self.check_http(check)
                elif check.type == HealthCheckType.TCP:
                    result = await self.check_tcp(check)
                elif check.type == HealthCheckType.DATABASE:
                    result = await self.check_database(check)
                elif check.type == HealthCheckType.REDIS:
                    result = await self.check_redis(check)
                elif check.type == HealthCheckType.CUSTOM:
                    result = await self.check_custom(check)
                elif check.type == HealthCheckType.COMPOSITE:
                    result = await self.check_composite(check)
                else:
                    result = HealthCheckResult(
                        service_name=check.name,
                        status=HealthStatus.UNKNOWN,
                        response_time=0.0,
                        timestamp=datetime.now(),
                        error=f"Unknown check type: {check.type}"
                    )
                
                # If successful, return result
                if result.status != HealthStatus.UNHEALTHY:
                    self.results[check.name] = result
                    await self._store_result(result)
                    return result
                
                last_error = result.error
                
            except Exception as e:
                last_error = str(e)
            
            # Wait before retry (except last attempt)
            if attempt < check.retries - 1:
                await asyncio.sleep(check.retry_delay)
        
        # All retries failed
        result = HealthCheckResult(
            service_name=check.name,
            status=HealthStatus.UNHEALTHY,
            response_time=0.0,
            timestamp=datetime.now(),
            error=f"All {check.retries} retries failed. Last error: {last_error}"
        )
        
        self.results[check.name] = result
        await self._store_result(result)
        return result
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all configured health checks."""
        tasks = []
        
        # Add system resource check if enabled
        if self.config.monitor_system_resources:
            tasks.append(self.check_system_resources())
        
        # Add all configured checks
        for check in self.checks.values():
            tasks.append(self.run_single_check(check))
        
        # Run all checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = {}
        for result in results:
            if isinstance(result, HealthCheckResult):
                processed_results[result.service_name] = result
            elif isinstance(result, Exception):
                # Handle unexpected exceptions
                processed_results["unknown_error"] = HealthCheckResult(
                    service_name="unknown_error",
                    status=HealthStatus.UNHEALTHY,
                    response_time=0.0,
                    timestamp=datetime.now(),
                    error=str(result)
                )
        
        return processed_results
    
    async def _store_result(self, result: HealthCheckResult):
        """Store health check result in Redis."""
        if not self.config.store_results or not self.redis_client:
            return
        
        try:
            key = f"health_check:{result.service_name}:{int(result.timestamp.timestamp())}"
            self.redis_client.setex(
                key,
                timedelta(days=self.config.results_retention_days),
                str(result.to_dict())
            )
        except Exception as e:
            print(f"Warning: Failed to store health check result: {e}")
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self.results:
            return HealthStatus.UNKNOWN
        
        healthy_count = sum(
            1 for result in self.results.values()
            if result.status == HealthStatus.HEALTHY
        )
        total_count = len(self.results)
        health_ratio = healthy_count / total_count
        
        if health_ratio >= self.config.degraded_threshold:
            return HealthStatus.HEALTHY
        elif health_ratio >= self.config.circuit_breaker_threshold:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY


# Pre-configured health checks for IA-Influencer Agent microservices
MICROSERVICE_HEALTH_CHECKS = {
    "api_gateway": HealthCheckDefinition(
        name="api_gateway",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8000/health",
        interval=30,
        timeout=10,
        retries=3,
        expected_status=200,
        warning_threshold=2.0,
        critical_threshold=5.0,
        tags=["api", "gateway", "critical"]
    ),
    "spotify_agent": HealthCheckDefinition(
        name="spotify_agent",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8001/health",
        interval=30,
        timeout=15,
        retries=3,
        expected_status=200,
        warning_threshold=3.0,
        critical_threshold=10.0,
        tags=["spotify", "ai", "important"]
    ),
    "content_protection": HealthCheckDefinition(
        name="content_protection",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8002/health",
        interval=60,
        timeout=30,
        retries=2,
        expected_status=200,
        warning_threshold=5.0,
        critical_threshold=15.0,
        tags=["protection", "important"]
    ),
    "fingerprinting_engine": HealthCheckDefinition(
        name="fingerprinting_engine",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8003/health",
        interval=60,
        timeout=30,
        retries=2,
        expected_status=200,
        warning_threshold=10.0,
        critical_threshold=30.0,
        tags=["fingerprinting", "ai", "important"]
    ),
    "web_crawler": HealthCheckDefinition(
        name="web_crawler",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8004/health",
        interval=120,
        timeout=30,
        retries=2,
        expected_status=200,
        warning_threshold=10.0,
        critical_threshold=60.0,
        tags=["crawler", "monitoring"]
    ),
    "monetization_engine": HealthCheckDefinition(
        name="monetization_engine",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8005/health",
        interval=60,
        timeout=20,
        retries=3,
        expected_status=200,
        warning_threshold=3.0,
        critical_threshold=10.0,
        tags=["monetization", "critical"]
    ),
    "notification_service": HealthCheckDefinition(
        name="notification_service",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8006/health",
        interval=30,
        timeout=10,
        retries=3,
        expected_status=200,
        warning_threshold=2.0,
        critical_threshold=5.0,
        tags=["notifications", "important"]
    ),
    "analytics_engine": HealthCheckDefinition(
        name="analytics_engine",
        type=HealthCheckType.HTTP,
        service_type=ServiceType.WEB_SERVICE,
        url="http://localhost:8007/health",
        interval=60,
        timeout=30,
        retries=2,
        expected_status=200,
        warning_threshold=5.0,
        critical_threshold=20.0,
        tags=["analytics", "important"]
    ),
    "database_primary": HealthCheckDefinition(
        name="database_primary",
        type=HealthCheckType.DATABASE,
        service_type=ServiceType.DATABASE,
        connection_string="postgresql://user:password@localhost:5432/ia_influencer",
        query="SELECT 1",
        interval=30,
        timeout=10,
        retries=3,
        warning_threshold=1.0,
        critical_threshold=3.0,
        tags=["database", "critical"]
    ),
    "redis_cache": HealthCheckDefinition(
        name="redis_cache",
        type=HealthCheckType.REDIS,
        service_type=ServiceType.CACHE,
        redis_host="localhost",
        redis_port=6379,
        redis_db=0,
        interval=30,
        timeout=5,
        retries=3,
        warning_threshold=0.5,
        critical_threshold=2.0,
        tags=["cache", "critical"]
    ),
    "redis_sessions": HealthCheckDefinition(
        name="redis_sessions",
        type=HealthCheckType.REDIS,
        service_type=ServiceType.CACHE,
        redis_host="localhost",
        redis_port=6379,
        redis_db=1,
        interval=60,
        timeout=5,
        retries=2,
        tags=["sessions", "important"]
    ),
    "platform_overall": HealthCheckDefinition(
        name="platform_overall",
        type=HealthCheckType.COMPOSITE,
        service_type=ServiceType.WEB_SERVICE,
        composite_checks=[
            "api_gateway",
            "spotify_agent",
            "database_primary",
            "redis_cache"
        ],
        interval=60,
        tags=["composite", "platform"]
    )
}


# Export configuration instance
health_check_config = HealthCheckConfig()
