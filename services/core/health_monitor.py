"""
Health Check Service - Enterprise Health Monitoring and Service Discovery
========================================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: DevOps Engineer & Backend Senior
**Module**: Security & Monitoring Services  
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Comprehensive health monitoring with service discovery, dependency tracking,
circuit breaker patterns, and automated recovery mechanisms.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import aiohttp
import psutil


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Types of services to monitor"""
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    EXTERNAL = "external"
    MICROSERVICE = "microservice"
    QUEUE = "queue"
    STORAGE = "storage"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    name: str
    service_type: ServiceType
    endpoint: str
    method: str = "GET"
    timeout: int = 5
    interval: int = 30
    retries: int = 3
    expected_status: int = 200
    expected_response: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)


@dataclass
class HealthResult:
    """Health check result"""
    service_name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceMetrics:
    """Service health metrics"""
    service_name: str
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    avg_response_time: float = 0.0
    uptime_percentage: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


@dataclass
class CircuitBreaker:
    """Circuit breaker for service protection"""
    service_name: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    recovery_timeout: int = 60
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None


class HealthCheckService:
    """
    Enterprise Health Check Service
    
    Comprehensive health monitoring with:
    - Multi-service health checking and monitoring
    - Service discovery and dependency tracking
    - Circuit breaker pattern for service protection
    - Automated recovery and healing mechanisms
    - Real-time health dashboard and alerting
    - Performance metrics and trend analysis
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Health check configurations
        self.health_checks: Dict[str, HealthCheckConfig] = {}
        
        # Circuit breakers for service protection
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Health results and metrics
        self.health_results: Dict[str, HealthResult] = {}
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        
        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Service registry
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        
        # Overall system health
        self.system_health = HealthStatus.UNKNOWN
        
        # Initialize default health checks
        self._initialize_default_health_checks()
        
        self.logger.info("Health Check Service initialized")

    async def initialize(self):
        """Initialize health check service"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Load existing configuration
            await self._load_health_check_config()
            
            # Initialize circuit breakers
            self._initialize_circuit_breakers()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            self.logger.info("Health Check Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Health Check Service: {e}")
            raise

    def _initialize_default_health_checks(self):
        """Initialize default health checks for common services"""
        
        default_checks = [
            HealthCheckConfig(
                name="redis_health",
                service_type=ServiceType.CACHE,
                endpoint="redis://localhost:6379",
                timeout=3,
                interval=30
            ),
            HealthCheckConfig(
                name="database_health",
                service_type=ServiceType.DATABASE,
                endpoint="/health/database",
                timeout=5,
                interval=30,
                dependencies=["redis_health"]
            ),
            HealthCheckConfig(
                name="api_gateway",
                service_type=ServiceType.API,
                endpoint="/health",
                timeout=5,
                interval=60
            ),
            HealthCheckConfig(
                name="content_service",
                service_type=ServiceType.MICROSERVICE,
                endpoint="/health/content",
                timeout=10,
                interval=60,
                dependencies=["database_health", "redis_health"]
            ),
            HealthCheckConfig(
                name="ai_service",
                service_type=ServiceType.MICROSERVICE,
                endpoint="/health/ai",
                timeout=15,
                interval=90,
                dependencies=["content_service"]
            ),
            HealthCheckConfig(
                name="external_api",
                service_type=ServiceType.EXTERNAL,
                endpoint="https://api.external-service.com/health",
                timeout=10,
                interval=300  # Check less frequently for external services
            )
        ]
        
        for check in default_checks:
            self.health_checks[check.name] = check

    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for all services"""
        
        for service_name in self.health_checks.keys():
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                failure_threshold=5,
                recovery_timeout=60
            )

    async def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        
        # Health checking task
        self.monitoring_tasks.append(
            asyncio.create_task(self._health_check_loop())
        )
        
        # Circuit breaker management
        self.monitoring_tasks.append(
            asyncio.create_task(self._circuit_breaker_management())
        )
        
        # Service discovery
        self.monitoring_tasks.append(
            asyncio.create_task(self._service_discovery_loop())
        )
        
        # Metrics calculation
        self.monitoring_tasks.append(
            asyncio.create_task(self._calculate_metrics_loop())
        )
        
        # System health assessment
        self.monitoring_tasks.append(
            asyncio.create_task(self._assess_system_health_loop())
        )
        
        self.logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")

    async def _health_check_loop(self):
        """Main health checking loop"""
        
        while True:
            try:
                # Run health checks for all configured services
                check_tasks = []
                
                for service_name, config in self.health_checks.items():
                    if config.enabled:
                        # Check circuit breaker state
                        circuit_breaker = self.circuit_breakers.get(service_name)
                        if circuit_breaker and circuit_breaker.state == CircuitBreakerState.OPEN:
                            # Skip check if circuit breaker is open and timeout hasn't passed
                            if self._should_skip_check(circuit_breaker):
                                continue
                        
                        # Create health check task
                        task = asyncio.create_task(
                            self._perform_health_check(service_name, config)
                        )
                        check_tasks.append(task)
                
                # Wait for all health checks to complete
                if check_tasks:
                    results = await asyncio.gather(*check_tasks, return_exceptions=True)
                    
                    # Process results
                    for result in results:
                        if isinstance(result, HealthResult):
                            await self._process_health_result(result)
                        elif isinstance(result, Exception):
                            self.logger.error(f"Health check error: {result}")
                
                # Wait for next check cycle
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)

    async def _perform_health_check(self, service_name: str, 
                                  config: HealthCheckConfig) -> HealthResult:
        """Perform individual health check"""
        
        start_time = time.time()
        
        result = HealthResult(
            service_name=service_name,
            status=HealthStatus.UNKNOWN,
            response_time=0.0,
            timestamp=datetime.utcnow()
        )
        
        try:
            # Check dependencies first
            if config.dependencies:
                dependency_check = await self._check_dependencies(config.dependencies)
                if not dependency_check["all_healthy"]:
                    result.status = HealthStatus.UNHEALTHY
                    result.error_message = f"Dependencies unhealthy: {dependency_check['unhealthy']}"
                    result.response_time = time.time() - start_time
                    return result
            
            # Perform actual health check based on service type
            if config.service_type == ServiceType.CACHE and "redis" in config.endpoint:
                result = await self._check_redis_health(service_name, config, start_time)
            elif config.service_type == ServiceType.DATABASE:
                result = await self._check_database_health(service_name, config, start_time)
            else:
                result = await self._check_http_health(service_name, config, start_time)
            
        except Exception as e:
            result.status = HealthStatus.CRITICAL
            result.error_message = str(e)
            result.response_time = time.time() - start_time
            
            self.logger.error(f"Health check failed for {service_name}: {e}")
        
        return result

    async def _check_redis_health(self, service_name: str, 
                                config: HealthCheckConfig, 
                                start_time: float) -> HealthResult:
        """Check Redis health"""
        
        result = HealthResult(
            service_name=service_name,
            status=HealthStatus.UNKNOWN,
            response_time=0.0,
            timestamp=datetime.utcnow()
        )
        
        try:
            # Connect to Redis
            redis_client = aioredis.from_url(config.endpoint)
            
            # Ping Redis
            ping_result = await asyncio.wait_for(
                redis_client.ping(),
                timeout=config.timeout
            )
            
            # Get Redis info
            info = await redis_client.info()
            
            result.response_time = time.time() - start_time
            result.status = HealthStatus.HEALTHY if ping_result else HealthStatus.UNHEALTHY
            
            result.details = {
                "ping_successful": ping_result,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
            await redis_client.close()
            
        except asyncio.TimeoutError:
            result.status = HealthStatus.CRITICAL
            result.error_message = "Redis connection timeout"
            result.response_time = time.time() - start_time
        except Exception as e:
            result.status = HealthStatus.CRITICAL
            result.error_message = f"Redis error: {str(e)}"
            result.response_time = time.time() - start_time
        
        return result

    async def _check_database_health(self, service_name: str,
                                   config: HealthCheckConfig,
                                   start_time: float) -> HealthResult:
        """Check database health"""
        
        result = HealthResult(
            service_name=service_name,
            status=HealthStatus.UNKNOWN,
            response_time=0.0,
            timestamp=datetime.utcnow()
        )
        
        try:
            # Simulate database health check
            # In production, use actual database connection
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"http://localhost:8000{config.endpoint}"
                
                async with session.request(
                    config.method,
                    url,
                    headers=config.headers,
                    data=config.body
                ) as response:
                    
                    result.response_time = time.time() - start_time
                    
                    if response.status == config.expected_status:
                        result.status = HealthStatus.HEALTHY
                        
                        # Try to get response data
                        try:
                            response_data = await response.json()
                            result.details = response_data
                        except:
                            result.details = {"status_code": response.status}
                    else:
                        result.status = HealthStatus.UNHEALTHY
                        result.error_message = f"Unexpected status code: {response.status}"
                        
        except asyncio.TimeoutError:
            result.status = HealthStatus.CRITICAL
            result.error_message = "Database connection timeout"
            result.response_time = time.time() - start_time
        except Exception as e:
            result.status = HealthStatus.CRITICAL
            result.error_message = f"Database error: {str(e)}"
            result.response_time = time.time() - start_time
        
        return result

    async def _check_http_health(self, service_name: str,
                               config: HealthCheckConfig,
                               start_time: float) -> HealthResult:
        """Check HTTP service health"""
        
        result = HealthResult(
            service_name=service_name,
            status=HealthStatus.UNKNOWN,
            response_time=0.0,
            timestamp=datetime.utcnow()
        )
        
        try:
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Determine URL
                if config.endpoint.startswith("http"):
                    url = config.endpoint
                else:
                    url = f"http://localhost:8000{config.endpoint}"
                
                async with session.request(
                    config.method,
                    url,
                    headers=config.headers,
                    data=config.body
                ) as response:
                    
                    result.response_time = time.time() - start_time
                    
                    if response.status == config.expected_status:
                        result.status = HealthStatus.HEALTHY
                        
                        # Check response content if expected
                        if config.expected_response:
                            response_text = await response.text()
                            if config.expected_response in response_text:
                                result.status = HealthStatus.HEALTHY
                            else:
                                result.status = HealthStatus.WARNING
                                result.error_message = "Unexpected response content"
                        
                        # Try to get response data
                        try:
                            response_data = await response.json()
                            result.details = response_data
                        except:
                            result.details = {
                                "status_code": response.status,
                                "content_length": len(await response.text())
                            }
                    else:
                        result.status = HealthStatus.UNHEALTHY
                        result.error_message = f"HTTP {response.status}: {response.reason}"
                        
        except asyncio.TimeoutError:
            result.status = HealthStatus.CRITICAL
            result.error_message = f"HTTP timeout after {config.timeout}s"
            result.response_time = time.time() - start_time
        except aiohttp.ClientConnectorError as e:
            result.status = HealthStatus.CRITICAL
            result.error_message = f"Connection error: {str(e)}"
            result.response_time = time.time() - start_time
        except Exception as e:
            result.status = HealthStatus.CRITICAL
            result.error_message = f"HTTP error: {str(e)}"
            result.response_time = time.time() - start_time
        
        return result

    async def _check_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check if all dependencies are healthy"""
        
        dependency_status = {
            "all_healthy": True,
            "healthy": [],
            "unhealthy": []
        }
        
        for dep_name in dependencies:
            if dep_name in self.health_results:
                result = self.health_results[dep_name]
                if result.status == HealthStatus.HEALTHY:
                    dependency_status["healthy"].append(dep_name)
                else:
                    dependency_status["unhealthy"].append(dep_name)
                    dependency_status["all_healthy"] = False
            else:
                dependency_status["unhealthy"].append(f"{dep_name} (no data)")
                dependency_status["all_healthy"] = False
        
        return dependency_status

    async def _process_health_result(self, result: HealthResult):
        """Process health check result and update state"""
        
        # Store result
        self.health_results[result.service_name] = result
        
        # Update circuit breaker
        await self._update_circuit_breaker(result)
        
        # Update service metrics
        await self._update_service_metrics(result)
        
        # Store result in Redis
        await self._store_health_result(result)
        
        # Send alerts if needed
        await self._check_health_alerts(result)
        
        self.logger.debug(f"Health result processed: {result.service_name} - {result.status.value}")

    async def _update_circuit_breaker(self, result: HealthResult):
        """Update circuit breaker state based on health result"""
        
        circuit_breaker = self.circuit_breakers.get(result.service_name)
        if not circuit_breaker:
            return
        
        if result.status == HealthStatus.HEALTHY:
            # Success - reset failure count and update state
            circuit_breaker.failure_count = 0
            circuit_breaker.last_success = result.timestamp
            
            if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                circuit_breaker.state = CircuitBreakerState.CLOSED
                self.logger.info(f"Circuit breaker CLOSED for {result.service_name}")
        
        elif result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            # Failure - increment failure count
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure = result.timestamp
            
            # Check if threshold exceeded
            if (circuit_breaker.failure_count >= circuit_breaker.failure_threshold and
                circuit_breaker.state == CircuitBreakerState.CLOSED):
                circuit_breaker.state = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker OPENED for {result.service_name}")

    async def _circuit_breaker_management(self):
        """Manage circuit breaker state transitions"""
        
        while True:
            try:
                for service_name, circuit_breaker in self.circuit_breakers.items():
                    if circuit_breaker.state == CircuitBreakerState.OPEN:
                        # Check if recovery timeout has passed
                        if (circuit_breaker.last_failure and 
                            datetime.utcnow() - circuit_breaker.last_failure >= 
                            timedelta(seconds=circuit_breaker.recovery_timeout)):
                            
                            circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                            self.logger.info(f"Circuit breaker HALF-OPEN for {service_name}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in circuit breaker management: {e}")
                await asyncio.sleep(60)

    def _should_skip_check(self, circuit_breaker: CircuitBreaker) -> bool:
        """Check if health check should be skipped due to circuit breaker"""
        
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            if (circuit_breaker.last_failure and
                datetime.utcnow() - circuit_breaker.last_failure < 
                timedelta(seconds=circuit_breaker.recovery_timeout)):
                return True
        
        return False

    async def _update_service_metrics(self, result: HealthResult):
        """Update service metrics based on health result"""
        
        metrics = self.service_metrics.get(result.service_name)
        if not metrics:
            metrics = ServiceMetrics(service_name=result.service_name)
            self.service_metrics[result.service_name] = metrics
        
        # Update counters
        metrics.total_checks += 1
        
        if result.status == HealthStatus.HEALTHY:
            metrics.successful_checks += 1
            metrics.last_success = result.timestamp
        else:
            metrics.failed_checks += 1
            metrics.last_failure = result.timestamp
        
        # Update average response time
        metrics.avg_response_time = (
            (metrics.avg_response_time * (metrics.total_checks - 1) + result.response_time) /
            metrics.total_checks
        )
        
        # Calculate uptime percentage
        if metrics.total_checks > 0:
            metrics.uptime_percentage = (metrics.successful_checks / metrics.total_checks) * 100

    async def _service_discovery_loop(self):
        """Service discovery and registration loop"""
        
        while True:
            try:
                # Discover new services
                await self._discover_services()
                
                # Update service registry
                await self._update_service_registry()
                
                await asyncio.sleep(300)  # Discovery every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in service discovery: {e}")
                await asyncio.sleep(600)

    async def _discover_services(self):
        """Discover new services automatically"""
        
        try:
            # Check for new Redis instances
            await self._discover_redis_services()
            
            # Check for new HTTP services
            await self._discover_http_services()
            
            # Check system processes for known services
            await self._discover_process_services()
            
        except Exception as e:
            self.logger.error(f"Service discovery error: {e}")

    async def _discover_redis_services(self):
        """Discover Redis services"""
        
        common_redis_ports = [6379, 6380, 6381]
        
        for port in common_redis_ports:
            service_name = f"redis_auto_{port}"
            
            if service_name not in self.health_checks:
                try:
                    # Test connection
                    redis_client = aioredis.from_url(f"redis://localhost:{port}")
                    await asyncio.wait_for(redis_client.ping(), timeout=3)
                    await redis_client.close()
                    
                    # Add to health checks
                    self.health_checks[service_name] = HealthCheckConfig(
                        name=service_name,
                        service_type=ServiceType.CACHE,
                        endpoint=f"redis://localhost:{port}",
                        timeout=3,
                        interval=60
                    )
                    
                    self.logger.info(f"Discovered Redis service: {service_name}")
                    
                except:
                    pass  # Service not available

    async def _discover_http_services(self):
        """Discover HTTP services"""
        
        common_ports = [8080, 8081, 8082, 3000, 3001, 5000, 5001]
        
        for port in common_ports:
            service_name = f"http_auto_{port}"
            
            if service_name not in self.health_checks:
                try:
                    timeout = aiohttp.ClientTimeout(total=3)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(f"http://localhost:{port}/health") as response:
                            if response.status in [200, 404]:  # Service responds
                                self.health_checks[service_name] = HealthCheckConfig(
                                    name=service_name,
                                    service_type=ServiceType.API,
                                    endpoint=f"http://localhost:{port}/health",
                                    timeout=5,
                                    interval=120
                                )
                                
                                self.logger.info(f"Discovered HTTP service: {service_name}")
                except:
                    pass

    async def _discover_process_services(self):
        """Discover services by process names"""
        
        service_processes = {
            "postgres": ServiceType.DATABASE,
            "mysql": ServiceType.DATABASE,
            "nginx": ServiceType.API,
            "rabbitmq": ServiceType.QUEUE,
            "elasticsearch": ServiceType.DATABASE
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                
                for service_name, service_type in service_processes.items():
                    if service_name in proc_name:
                        auto_service_name = f"{service_name}_process"
                        
                        if auto_service_name not in self.health_checks:
                            # Create a process-based health check
                            self.health_checks[auto_service_name] = HealthCheckConfig(
                                name=auto_service_name,
                                service_type=service_type,
                                endpoint=f"/health/{service_name}",
                                timeout=5,
                                interval=120
                            )
                            
                            self.logger.info(f"Discovered process service: {auto_service_name}")
            except:
                pass

    async def _update_service_registry(self):
        """Update service registry with current service information"""
        
        registry_data = {}
        
        for service_name, config in self.health_checks.items():
            result = self.health_results.get(service_name)
            metrics = self.service_metrics.get(service_name)
            circuit_breaker = self.circuit_breakers.get(service_name)
            
            registry_data[service_name] = {
                "service_type": config.service_type.value,
                "endpoint": config.endpoint,
                "status": result.status.value if result else "unknown",
                "last_check": result.timestamp.isoformat() if result else None,
                "response_time": result.response_time if result else None,
                "uptime_percentage": metrics.uptime_percentage if metrics else 0.0,
                "circuit_breaker_state": circuit_breaker.state.value if circuit_breaker else "unknown",
                "dependencies": config.dependencies
            }
        
        self.service_registry = registry_data
        
        # Store in Redis
        await self.redis_client.setex(
            "service_registry",
            300,  # 5 minutes TTL
            json.dumps(registry_data)
        )

    async def _calculate_metrics_loop(self):
        """Calculate and update service metrics periodically"""
        
        while True:
            try:
                # Calculate aggregated metrics
                total_services = len(self.health_checks)
                healthy_services = sum(
                    1 for result in self.health_results.values()
                    if result.status == HealthStatus.HEALTHY
                )
                
                system_uptime = (healthy_services / total_services * 100) if total_services > 0 else 0
                
                # Store system metrics
                system_metrics = {
                    "total_services": total_services,
                    "healthy_services": healthy_services,
                    "unhealthy_services": total_services - healthy_services,
                    "system_uptime_percentage": system_uptime,
                    "last_calculated": datetime.utcnow().isoformat()
                }
                
                await self.redis_client.setex(
                    "health_system_metrics",
                    300,
                    json.dumps(system_metrics)
                )
                
                await asyncio.sleep(60)  # Calculate every minute
                
            except Exception as e:
                self.logger.error(f"Error calculating metrics: {e}")
                await asyncio.sleep(120)

    async def _assess_system_health_loop(self):
        """Assess overall system health periodically"""
        
        while True:
            try:
                await self._assess_overall_system_health()
                await asyncio.sleep(30)  # Assess every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error assessing system health: {e}")
                await asyncio.sleep(60)

    async def _assess_overall_system_health(self):
        """Assess overall system health status"""
        
        if not self.health_results:
            self.system_health = HealthStatus.UNKNOWN
            return
        
        # Count services by status
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.WARNING: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0
        }
        
        for result in self.health_results.values():
            status_counts[result.status] += 1
        
        total_services = len(self.health_results)
        critical_services = status_counts[HealthStatus.CRITICAL]
        unhealthy_services = status_counts[HealthStatus.UNHEALTHY]
        healthy_services = status_counts[HealthStatus.HEALTHY]
        
        # Determine overall system health
        if critical_services > 0:
            self.system_health = HealthStatus.CRITICAL
        elif unhealthy_services > total_services * 0.5:  # More than 50% unhealthy
            self.system_health = HealthStatus.UNHEALTHY
        elif unhealthy_services > 0 or status_counts[HealthStatus.WARNING] > 0:
            self.system_health = HealthStatus.WARNING
        else:
            self.system_health = HealthStatus.HEALTHY

    async def _store_health_result(self, result: HealthResult):
        """Store health result in Redis"""
        
        result_data = {
            "service_name": result.service_name,
            "status": result.status.value,
            "response_time": result.response_time,
            "timestamp": result.timestamp.isoformat(),
            "details": result.details,
            "error_message": result.error_message,
            "metadata": result.metadata
        }
        
        # Store latest result
        await self.redis_client.setex(
            f"health_result:{result.service_name}",
            3600,  # 1 hour TTL
            json.dumps(result_data)
        )
        
        # Store in time series
        await self.redis_client.lpush(
            f"health_history:{result.service_name}",
            json.dumps(result_data)
        )
        
        # Keep only last 100 results
        await self.redis_client.ltrim(f"health_history:{result.service_name}", 0, 99)

    async def _check_health_alerts(self, result: HealthResult):
        """Check if health result should trigger alerts"""
        
        if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            alert_data = {
                "service_name": result.service_name,
                "status": result.status.value,
                "error_message": result.error_message,
                "response_time": result.response_time,
                "timestamp": result.timestamp.isoformat(),
                "alert_type": "service_health"
            }
            
            # Send alert notification
            await self.redis_client.lpush(
                f"health_alerts:{result.status.value}",
                json.dumps(alert_data)
            )
            
            self.logger.warning(f"Health alert for {result.service_name}: {result.status.value}")

    async def _load_health_check_config(self):
        """Load health check configuration from Redis"""
        
        try:
            config_data = await self.redis_client.get("health_check_config")
            if config_data:
                configs = json.loads(config_data)
                
                for name, config in configs.items():
                    self.health_checks[name] = HealthCheckConfig(**config)
                
                self.logger.info(f"Loaded {len(configs)} health check configurations")
        
        except Exception as e:
            self.logger.warning(f"Could not load health check config: {e}")

    async def register_service(self, config: HealthCheckConfig):
        """Register a new service for health monitoring"""
        
        self.health_checks[config.name] = config
        
        # Initialize circuit breaker
        self.circuit_breakers[config.name] = CircuitBreaker(
            service_name=config.name,
            failure_threshold=5,
            recovery_timeout=60
        )
        
        # Save configuration
        await self._save_health_check_config()
        
        self.logger.info(f"Registered service for health monitoring: {config.name}")

    async def unregister_service(self, service_name: str):
        """Unregister a service from health monitoring"""
        
        if service_name in self.health_checks:
            del self.health_checks[service_name]
        
        if service_name in self.circuit_breakers:
            del self.circuit_breakers[service_name]
        
        if service_name in self.health_results:
            del self.health_results[service_name]
        
        if service_name in self.service_metrics:
            del self.service_metrics[service_name]
        
        # Save configuration
        await self._save_health_check_config()
        
        self.logger.info(f"Unregistered service from health monitoring: {service_name}")

    async def _save_health_check_config(self):
        """Save health check configuration to Redis"""
        
        configs = {}
        for name, config in self.health_checks.items():
            configs[name] = {
                "name": config.name,
                "service_type": config.service_type.value,
                "endpoint": config.endpoint,
                "method": config.method,
                "timeout": config.timeout,
                "interval": config.interval,
                "retries": config.retries,
                "expected_status": config.expected_status,
                "expected_response": config.expected_response,
                "headers": config.headers,
                "body": config.body,
                "enabled": config.enabled,
                "dependencies": config.dependencies
            }
        
        await self.redis_client.setex(
            "health_check_config",
            86400,  # 24 hours
            json.dumps(configs)
        )

    async def get_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive health dashboard data"""
        
        # Service health summary
        service_health = {}
        for service_name, result in self.health_results.items():
            service_health[service_name] = {
                "status": result.status.value,
                "response_time": result.response_time,
                "last_check": result.timestamp.isoformat(),
                "error_message": result.error_message
            }
        
        # Circuit breaker status
        circuit_breaker_status = {}
        for service_name, cb in self.circuit_breakers.items():
            circuit_breaker_status[service_name] = {
                "state": cb.state.value,
                "failure_count": cb.failure_count,
                "last_failure": cb.last_failure.isoformat() if cb.last_failure else None
            }
        
        # Service metrics summary
        metrics_summary = {}
        for service_name, metrics in self.service_metrics.items():
            metrics_summary[service_name] = {
                "total_checks": metrics.total_checks,
                "uptime_percentage": metrics.uptime_percentage,
                "avg_response_time": metrics.avg_response_time
            }
        
        return {
            "system_health": self.system_health.value,
            "service_health": service_health,
            "circuit_breakers": circuit_breaker_status,
            "service_metrics": metrics_summary,
            "service_registry": self.service_registry,
            "total_services": len(self.health_checks),
            "monitoring_active": len(self.monitoring_tasks) > 0,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self):
        """Shutdown health check service gracefully"""
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Health Check Service shutdown completed")


# Example usage
async def main():
    """Example usage of Health Check Service"""
    
    health_service = HealthCheckService()
    await health_service.initialize()
    
    try:
        # Register a custom service
        custom_service = HealthCheckConfig(
            name="custom_api",
            service_type=ServiceType.API,
            endpoint="/api/custom/health",
            timeout=10,
            interval=60
        )
        await health_service.register_service(custom_service)
        
        # Let monitoring run for a bit
        await asyncio.sleep(30)
        
        # Get dashboard
        dashboard = await health_service.get_health_dashboard()
        print(f"Health dashboard: {dashboard}")
        
    finally:
        await health_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())