"""
📋 Service Registry - Enterprise Service Discovery & Health Monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ AVERTISSEMENT LÉGAL: Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, vol ou reproduction sans autorisation écrite de Fahed Mlaiel (mlaiel@live.de)
est strictement interdite et passible de poursuites judiciaires.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import hashlib
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class HealthCheckType(Enum):
    """Health check types"""
    HTTP = "http"
    TCP = "tcp"
    SCRIPT = "script"
    CUSTOM = "custom"
    DATABASE = "database"
    QUEUE = "queue"
    CACHE = "cache"


class LoadBalanceStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    LEAST_RESPONSE_TIME = "least_response_time"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    host: str
    port: int
    protocol: str = "http"
    path: str = "/"
    weight: int = 100
    max_connections: int = 1000
    timeout_seconds: int = 30
    ssl_enabled: bool = False
    health_check_path: str = "/health"


@dataclass
class HealthCheck:
    """Health check configuration"""
    check_id: str
    check_type: HealthCheckType
    endpoint: ServiceEndpoint
    interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3
    success_threshold: int = 2
    check_script: Optional[str] = None
    expected_response: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthResult:
    """Health check result"""
    check_id: str
    service_id: str
    status: ServiceStatus
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_id: str
    requests_per_second: float = 0.0
    average_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0
    cpu_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0
    active_connections: int = 0
    throughput_mbps: float = 0.0
    uptime_seconds: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ServiceDefinition:
    """Service registration definition"""
    service_id: str
    service_name: str
    service_type: str
    version: str
    endpoints: List[ServiceEndpoint]
    health_checks: List[HealthCheck]
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    environment: str = "production"
    region: str = "default"
    registration_time: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: int = 300


@dataclass
class ServiceInstance:
    """Service instance tracking"""
    instance_id: str
    service_definition: ServiceDefinition
    current_status: ServiceStatus
    health_results: List[HealthResult] = field(default_factory=list)
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)
    circuit_breaker_state: str = "closed"
    load_balance_weight: int = 100
    connection_count: int = 0
    last_request_time: Optional[datetime] = None
    maintenance_mode: bool = False


class CircuitBreaker:
    """Circuit breaker implementation for service resilience"""
    
    def __init__(self, service_id: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.service_id = service_id
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    async def call_service(self, service_call: Callable) -> Any:
        """Execute service call with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
                logger.info(f"Circuit breaker for {self.service_id} moved to half-open state")
            else:
                raise Exception(f"Circuit breaker open for service {self.service_id}")
        
        try:
            result = await service_call()
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return False
        
        time_since_last_failure = datetime.utcnow() - self.last_failure_time
        return time_since_last_failure.total_seconds() >= self.recovery_timeout
    
    async def _on_success(self):
        """Handle successful service call"""
        if self.state == "half_open":
            self.state = "closed"
            self.failure_count = 0
            logger.info(f"Circuit breaker for {self.service_id} reset to closed state")
    
    async def _on_failure(self):
        """Handle failed service call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker for {self.service_id} opened due to {self.failure_count} failures")


class HealthChecker:
    """Health check executor"""
    
    def __init__(self):
        self.active_checks = {}
        self.check_history = {}
    
    async def execute_health_check(self, health_check: HealthCheck, service_instance: ServiceInstance) -> HealthResult:
        """Execute individual health check"""
        start_time = datetime.utcnow()
        
        try:
            if health_check.check_type == HealthCheckType.HTTP:
                result = await self._execute_http_check(health_check)
            elif health_check.check_type == HealthCheckType.TCP:
                result = await self._execute_tcp_check(health_check)
            elif health_check.check_type == HealthCheckType.SCRIPT:
                result = await self._execute_script_check(health_check)
            elif health_check.check_type == HealthCheckType.DATABASE:
                result = await self._execute_database_check(health_check)
            else:
                result = await self._execute_custom_check(health_check)
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            health_result = HealthResult(
                check_id=health_check.check_id,
                service_id=service_instance.service_definition.service_id,
                status=ServiceStatus.HEALTHY if result["success"] else ServiceStatus.UNHEALTHY,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details=result.get("details", {}),
                error_message=result.get("error")
            )
            
            # Update consecutive counters
            if result["success"]:
                health_result.consecutive_successes = self._get_consecutive_successes(health_check.check_id) + 1
                health_result.consecutive_failures = 0
            else:
                health_result.consecutive_failures = self._get_consecutive_failures(health_check.check_id) + 1
                health_result.consecutive_successes = 0
            
            # Store result
            self._store_health_result(health_result)
            
            return health_result
            
        except Exception as e:
            logger.error(f"Health check {health_check.check_id} failed: {e}")
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            health_result = HealthResult(
                check_id=health_check.check_id,
                service_id=service_instance.service_definition.service_id,
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                error_message=str(e),
                consecutive_failures=self._get_consecutive_failures(health_check.check_id) + 1,
                consecutive_successes=0
            )
            
            self._store_health_result(health_result)
            return health_result
    
    async def _execute_http_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute HTTP health check"""
        endpoint = health_check.endpoint
        url = f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{health_check.endpoint.health_check_path}"
        
        # Simulate HTTP request
        await asyncio.sleep(0.05)  # Simulate network delay
        
        # Simulate success/failure based on service health
        success = hash(health_check.check_id) % 10 > 1  # 80% success rate
        
        return {
            "success": success,
            "details": {
                "url": url,
                "status_code": 200 if success else 500,
                "response_body": "OK" if success else "Internal Server Error"
            },
            "error": None if success else "HTTP 500 error"
        }
    
    async def _execute_tcp_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute TCP health check"""
        endpoint = health_check.endpoint
        
        # Simulate TCP connection
        await asyncio.sleep(0.02)  # Simulate connection time
        
        success = hash(health_check.check_id) % 10 > 0  # 90% success rate
        
        return {
            "success": success,
            "details": {
                "host": endpoint.host,
                "port": endpoint.port,
                "connection_time_ms": 20
            },
            "error": None if success else "Connection refused"
        }
    
    async def _execute_script_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute script-based health check"""
        # Simulate script execution
        await asyncio.sleep(0.1)
        
        success = hash(health_check.check_id) % 10 > 2  # 70% success rate
        
        return {
            "success": success,
            "details": {
                "script": health_check.check_script,
                "exit_code": 0 if success else 1,
                "output": "Health check passed" if success else "Health check failed"
            },
            "error": None if success else "Script returned non-zero exit code"
        }
    
    async def _execute_database_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute database health check"""
        # Simulate database query
        await asyncio.sleep(0.03)
        
        success = hash(health_check.check_id) % 10 > 1  # 80% success rate
        
        return {
            "success": success,
            "details": {
                "query_time_ms": 30,
                "connections_active": 15,
                "connections_max": 100
            },
            "error": None if success else "Database connection failed"
        }
    
    async def _execute_custom_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute custom health check"""
        # Simulate custom check
        await asyncio.sleep(0.05)
        
        success = hash(health_check.check_id) % 10 > 2  # 70% success rate
        
        return {
            "success": success,
            "details": {
                "custom_metric": 85.5,
                "threshold": 80.0
            },
            "error": None if success else "Custom check threshold not met"
        }
    
    def _get_consecutive_failures(self, check_id: str) -> int:
        """Get consecutive failure count for check"""
        history = self.check_history.get(check_id, [])
        consecutive = 0
        for result in reversed(history):
            if result.status == ServiceStatus.UNHEALTHY:
                consecutive += 1
            else:
                break
        return consecutive
    
    def _get_consecutive_successes(self, check_id: str) -> int:
        """Get consecutive success count for check"""
        history = self.check_history.get(check_id, [])
        consecutive = 0
        for result in reversed(history):
            if result.status == ServiceStatus.HEALTHY:
                consecutive += 1
            else:
                break
        return consecutive
    
    def _store_health_result(self, result: HealthResult):
        """Store health check result"""
        if result.check_id not in self.check_history:
            self.check_history[result.check_id] = []
        
        self.check_history[result.check_id].append(result)
        
        # Keep only last 100 results
        if len(self.check_history[result.check_id]) > 100:
            self.check_history[result.check_id] = self.check_history[result.check_id][-100:]


class LoadBalancer:
    """Intelligent load balancer"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.round_robin_index = {}
        self.service_metrics = {}
    
    async def select_instance(
        self,
        service_instances: List[ServiceInstance],
        request_context: Dict[str, Any] = None
    ) -> Optional[ServiceInstance]:
        """Select service instance using load balancing strategy"""
        available_instances = [
            instance for instance in service_instances
            if instance.current_status == ServiceStatus.HEALTHY and not instance.maintenance_mode
        ]
        
        if not available_instances:
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_instances)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_instances)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_instances)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_selection(available_instances)
        elif self.strategy == LoadBalanceStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_selection(available_instances)
        elif self.strategy == LoadBalanceStrategy.IP_HASH:
            return self._ip_hash_selection(available_instances, request_context)
        else:
            return available_instances[0]  # Fallback
    
    def _round_robin_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin selection"""
        service_key = instances[0].service_definition.service_name
        
        if service_key not in self.round_robin_index:
            self.round_robin_index[service_key] = 0
        
        selected_instance = instances[self.round_robin_index[service_key]]
        self.round_robin_index[service_key] = (self.round_robin_index[service_key] + 1) % len(instances)
        
        return selected_instance
    
    def _weighted_round_robin_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round-robin selection"""
        total_weight = sum(instance.load_balance_weight for instance in instances)
        if total_weight == 0:
            return self._round_robin_selection(instances)
        
        # Create weighted list
        weighted_instances = []
        for instance in instances:
            weight_ratio = instance.load_balance_weight / total_weight
            count = max(1, int(weight_ratio * 10))  # Scale to reasonable number
            weighted_instances.extend([instance] * count)
        
        return self._round_robin_selection(weighted_instances)
    
    def _least_connections_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection"""
        return min(instances, key=lambda x: x.connection_count)
    
    def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection"""
        import random
        return random.choice(instances)
    
    def _least_response_time_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least response time selection"""
        return min(instances, key=lambda x: x.metrics.average_response_time_ms)
    
    def _ip_hash_selection(self, instances: List[ServiceInstance], context: Dict[str, Any]) -> ServiceInstance:
        """IP hash-based selection for session affinity"""
        client_ip = context.get("client_ip", "127.0.0.1") if context else "127.0.0.1"
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(instances)
        return instances[index]


class ServiceRegistry:
    """
    Enterprise Service Registry with discovery and health monitoring
    
    Provides comprehensive service discovery, health monitoring, and load balancing
    for the IA Chéries creator platform with support for microservices architecture.
    """
    
    def __init__(self):
        self.services = {}  # service_id -> ServiceInstance
        self.service_groups = {}  # service_name -> List[ServiceInstance]
        self.health_checker = HealthChecker()
        self.load_balancer = LoadBalancer()
        self.circuit_breakers = {}
        self.monitoring_tasks = {}
        self.service_mesh_config = {}
        self.analytics_data = {
            "service_registrations": 0,
            "health_checks_performed": 0,
            "load_balance_decisions": 0,
            "circuit_breaker_trips": 0
        }
    
    async def service_discovery_mesh(
        self,
        service_name: str,
        service_type: Optional[str] = None,
        region: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ServiceInstance]:
        """
        Discover services with mesh networking support
        """
        logger.info(f"Discovering services for {service_name}")
        
        # Get service instances by name
        instances = self.service_groups.get(service_name, [])
        
        # Apply filters
        filtered_instances = []
        for instance in instances:
            service_def = instance.service_definition
            
            # Filter by service type
            if service_type and service_def.service_type != service_type:
                continue
            
            # Filter by region
            if region and service_def.region != region:
                continue
            
            # Filter by tags
            if tags and not any(tag in service_def.tags for tag in tags):
                continue
            
            # Only include healthy services
            if instance.current_status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                filtered_instances.append(instance)
        
        # Update analytics
        self.analytics_data["load_balance_decisions"] += 1
        
        logger.info(f"Discovered {len(filtered_instances)} instances for {service_name}")
        return filtered_instances
    
    async def register_service(self, service_definition: ServiceDefinition) -> str:
        """Register new service in the registry"""
        logger.info(f"Registering service {service_definition.service_name}")
        
        # Create service instance
        instance_id = str(uuid.uuid4())
        service_instance = ServiceInstance(
            instance_id=instance_id,
            service_definition=service_definition,
            current_status=ServiceStatus.STARTING,
            metrics=ServiceMetrics(service_id=service_definition.service_id)
        )
        
        # Store in registry
        self.services[service_definition.service_id] = service_instance
        
        # Group by service name
        if service_definition.service_name not in self.service_groups:
            self.service_groups[service_definition.service_name] = []
        self.service_groups[service_definition.service_name].append(service_instance)
        
        # Create circuit breaker
        self.circuit_breakers[service_definition.service_id] = CircuitBreaker(
            service_definition.service_id
        )
        
        # Start health monitoring
        await self._start_health_monitoring(service_instance)
        
        # Update analytics
        self.analytics_data["service_registrations"] += 1
        
        logger.info(f"Service {service_definition.service_name} registered with ID {service_definition.service_id}")
        return service_definition.service_id
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister service from registry"""
        logger.info(f"Deregistering service {service_id}")
        
        if service_id not in self.services:
            return False
        
        service_instance = self.services[service_id]
        service_name = service_instance.service_definition.service_name
        
        # Stop health monitoring
        if service_id in self.monitoring_tasks:
            self.monitoring_tasks[service_id].cancel()
            del self.monitoring_tasks[service_id]
        
        # Remove from groups
        if service_name in self.service_groups:
            self.service_groups[service_name] = [
                inst for inst in self.service_groups[service_name]
                if inst.service_definition.service_id != service_id
            ]
            if not self.service_groups[service_name]:
                del self.service_groups[service_name]
        
        # Remove from main registry
        del self.services[service_id]
        
        # Remove circuit breaker
        if service_id in self.circuit_breakers:
            del self.circuit_breakers[service_id]
        
        logger.info(f"Service {service_id} deregistered successfully")
        return True
    
    async def health_check_automation(
        self,
        service_id: Optional[str] = None,
        check_all: bool = False
    ) -> Dict[str, List[HealthResult]]:
        """
        Execute health checks with automation
        """
        logger.info(f"Executing health checks for {'all services' if check_all else service_id}")
        
        health_results = {}
        
        services_to_check = []
        if check_all:
            services_to_check = list(self.services.values())
        elif service_id and service_id in self.services:
            services_to_check = [self.services[service_id]]
        
        for service_instance in services_to_check:
            service_id = service_instance.service_definition.service_id
            instance_results = []
            
            for health_check in service_instance.service_definition.health_checks:
                result = await self.health_checker.execute_health_check(
                    health_check,
                    service_instance
                )
                instance_results.append(result)
                
                # Update service status based on health check
                await self._update_service_status(service_instance, result)
            
            health_results[service_id] = instance_results
            
            # Update analytics
            self.analytics_data["health_checks_performed"] += len(instance_results)
        
        return health_results
    
    async def service_mesh_integration(
        self,
        mesh_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure service mesh integration
        """
        logger.info("Configuring service mesh integration")
        
        self.service_mesh_config = mesh_config
        
        # Configure mesh networking
        mesh_features = {
            "traffic_routing": mesh_config.get("traffic_routing", True),
            "load_balancing": mesh_config.get("load_balancing", True),
            "security_policies": mesh_config.get("security_policies", True),
            "observability": mesh_config.get("observability", True),
            "fault_injection": mesh_config.get("fault_injection", False)
        }
        
        # Apply mesh configuration to all services
        for service_instance in self.services.values():
            await self._apply_mesh_configuration(service_instance, mesh_features)
        
        return {
            "mesh_configured": True,
            "features_enabled": mesh_features,
            "services_configured": len(self.services),
            "configuration_timestamp": datetime.utcnow()
        }
    
    async def load_balancing_intelligence(
        self,
        service_name: str,
        request_context: Dict[str, Any] = None,
        strategy: Optional[LoadBalanceStrategy] = None
    ) -> Optional[ServiceInstance]:
        """
        Intelligent load balancing with multiple strategies
        """
        logger.debug(f"Load balancing request for {service_name}")
        
        # Get available service instances
        instances = await self.service_discovery_mesh(service_name)
        
        if not instances:
            logger.warning(f"No healthy instances found for service {service_name}")
            return None
        
        # Use custom strategy if provided
        if strategy:
            original_strategy = self.load_balancer.strategy
            self.load_balancer.strategy = strategy
            
        # Select instance
        selected_instance = await self.load_balancer.select_instance(
            instances,
            request_context
        )
        
        # Restore original strategy
        if strategy:
            self.load_balancer.strategy = original_strategy
        
        if selected_instance:
            # Update connection count
            selected_instance.connection_count += 1
            selected_instance.last_request_time = datetime.utcnow()
            
            # Update analytics
            self.analytics_data["load_balance_decisions"] += 1
        
        return selected_instance
    
    async def circuit_breaker_patterns(
        self,
        service_id: str,
        operation: Callable,
        context: Dict[str, Any] = None
    ) -> Any:
        """
        Execute operation with circuit breaker protection
        """
        logger.debug(f"Executing operation with circuit breaker for service {service_id}")
        
        circuit_breaker = self.circuit_breakers.get(service_id)
        if not circuit_breaker:
            logger.warning(f"No circuit breaker found for service {service_id}")
            return await operation()
        
        try:
            result = await circuit_breaker.call_service(operation)
            return result
        except Exception as e:
            # Update analytics
            if circuit_breaker.state == "open":
                self.analytics_data["circuit_breaker_trips"] += 1
            
            logger.error(f"Circuit breaker protected operation failed for service {service_id}: {e}")
            raise e
    
    async def service_analytics(
        self,
        service_id: Optional[str] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate comprehensive service analytics
        """
        logger.info(f"Generating service analytics for {'all services' if not service_id else service_id}")
        
        analytics = {
            "global_metrics": self.analytics_data.copy(),
            "timestamp": datetime.utcnow(),
            "time_range_hours": time_range_hours
        }
        
        if service_id:
            # Single service analytics
            service_instance = self.services.get(service_id)
            if service_instance:
                analytics["service_analytics"] = await self._generate_service_analytics(
                    service_instance,
                    time_range_hours
                )
        else:
            # All services analytics
            analytics["service_analytics"] = {}
            for sid, service_instance in self.services.items():
                analytics["service_analytics"][sid] = await self._generate_service_analytics(
                    service_instance,
                    time_range_hours
                )
            
            # Global aggregates
            analytics["global_aggregates"] = await self._calculate_global_aggregates()
        
        return analytics
    
    async def update_service_status(
        self,
        service_id: str,
        status: ServiceStatus,
        reason: Optional[str] = None
    ) -> bool:
        """Update service status manually"""
        if service_id not in self.services:
            return False
        
        service_instance = self.services[service_id]
        old_status = service_instance.current_status
        service_instance.current_status = status
        
        logger.info(f"Service {service_id} status changed from {old_status} to {status}")
        if reason:
            logger.info(f"Reason: {reason}")
        
        return True
    
    async def get_service_dependencies(self, service_id: str) -> Dict[str, Any]:
        """Get service dependency graph"""
        if service_id not in self.services:
            return {"error": "Service not found"}
        
        service_instance = self.services[service_id]
        dependencies = service_instance.service_definition.dependencies
        
        dependency_status = {}
        for dep_service_name in dependencies:
            dep_instances = self.service_groups.get(dep_service_name, [])
            healthy_instances = [
                inst for inst in dep_instances
                if inst.current_status == ServiceStatus.HEALTHY
            ]
            
            dependency_status[dep_service_name] = {
                "total_instances": len(dep_instances),
                "healthy_instances": len(healthy_instances),
                "status": "healthy" if healthy_instances else "unhealthy"
            }
        
        return {
            "service_id": service_id,
            "dependencies": dependency_status,
            "dependency_health_score": self._calculate_dependency_health_score(dependency_status)
        }
    
    # Private helper methods
    
    async def _start_health_monitoring(self, service_instance: ServiceInstance):
        """Start health monitoring for service instance"""
        service_id = service_instance.service_definition.service_id
        
        async def monitor_health():
            while service_id in self.services:
                try:
                    # Execute all health checks
                    for health_check in service_instance.service_definition.health_checks:
                        result = await self.health_checker.execute_health_check(
                            health_check,
                            service_instance
                        )
                        
                        # Update service status
                        await self._update_service_status(service_instance, result)
                    
                    # Wait for next check interval
                    await asyncio.sleep(30)  # Default 30 second interval
                    
                except Exception as e:
                    logger.error(f"Error in health monitoring for {service_id}: {e}")
                    await asyncio.sleep(30)
        
        # Start monitoring task
        self.monitoring_tasks[service_id] = asyncio.create_task(monitor_health())
    
    async def _update_service_status(self, service_instance: ServiceInstance, health_result: HealthResult):
        """Update service status based on health check result"""
        health_check = next(
            (hc for hc in service_instance.service_definition.health_checks 
             if hc.check_id == health_result.check_id),
            None
        )
        
        if not health_check:
            return
        
        # Add health result to instance
        service_instance.health_results.append(health_result)
        
        # Keep only recent results
        if len(service_instance.health_results) > 50:
            service_instance.health_results = service_instance.health_results[-50:]
        
        # Determine new status based on consecutive failures/successes
        if health_result.consecutive_failures >= health_check.failure_threshold:
            service_instance.current_status = ServiceStatus.UNHEALTHY
        elif health_result.consecutive_successes >= health_check.success_threshold:
            if service_instance.current_status in [ServiceStatus.STARTING, ServiceStatus.UNHEALTHY]:
                service_instance.current_status = ServiceStatus.HEALTHY
        
        # Update metrics
        service_instance.metrics.last_updated = datetime.utcnow()
        service_instance.metrics.average_response_time_ms = health_result.response_time_ms
    
    async def _apply_mesh_configuration(
        self,
        service_instance: ServiceInstance,
        mesh_features: Dict[str, bool]
    ):
        """Apply service mesh configuration to service instance"""
        # Simulate mesh configuration application
        logger.debug(f"Applying mesh configuration to service {service_instance.service_definition.service_id}")
        
        # Update service metadata with mesh configuration
        service_instance.service_definition.metadata.update({
            "mesh_enabled": True,
            "mesh_features": mesh_features,
            "mesh_config_timestamp": datetime.utcnow().isoformat()
        })
    
    async def _generate_service_analytics(
        self,
        service_instance: ServiceInstance,
        time_range_hours: int
    ) -> Dict[str, Any]:
        """Generate analytics for specific service"""
        # Calculate health metrics
        recent_health_results = [
            result for result in service_instance.health_results
            if (datetime.utcnow() - result.timestamp).total_seconds() <= time_range_hours * 3600
        ]
        
        if recent_health_results:
            avg_response_time = sum(r.response_time_ms for r in recent_health_results) / len(recent_health_results)
            success_rate = len([r for r in recent_health_results if r.status == ServiceStatus.HEALTHY]) / len(recent_health_results) * 100
        else:
            avg_response_time = 0
            success_rate = 0
        
        return {
            "service_id": service_instance.service_definition.service_id,
            "service_name": service_instance.service_definition.service_name,
            "current_status": service_instance.current_status.value,
            "uptime_hours": (datetime.utcnow() - service_instance.service_definition.registration_time).total_seconds() / 3600,
            "health_check_count": len(recent_health_results),
            "average_response_time_ms": avg_response_time,
            "success_rate_percent": success_rate,
            "connection_count": service_instance.connection_count,
            "circuit_breaker_state": service_instance.circuit_breaker_state,
            "maintenance_mode": service_instance.maintenance_mode,
            "metrics": service_instance.metrics.__dict__
        }
    
    async def _calculate_global_aggregates(self) -> Dict[str, Any]:
        """Calculate global service aggregates"""
        total_services = len(self.services)
        healthy_services = len([
            s for s in self.services.values()
            if s.current_status == ServiceStatus.HEALTHY
        ])
        
        unhealthy_services = len([
            s for s in self.services.values()
            if s.current_status == ServiceStatus.UNHEALTHY
        ])
        
        degraded_services = len([
            s for s in self.services.values()
            if s.current_status == ServiceStatus.DEGRADED
        ])
        
        # Calculate average response time across all services
        all_response_times = []
        for service in self.services.values():
            if service.health_results:
                recent_results = service.health_results[-10:]  # Last 10 results
                all_response_times.extend([r.response_time_ms for r in recent_results])
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": unhealthy_services,
            "degraded_services": degraded_services,
            "overall_health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "average_response_time_ms": avg_response_time,
            "total_service_groups": len(self.service_groups),
            "active_monitoring_tasks": len(self.monitoring_tasks)
        }
    
    def _calculate_dependency_health_score(self, dependency_status: Dict[str, Any]) -> float:
        """Calculate dependency health score"""
        if not dependency_status:
            return 100.0
        
        healthy_deps = len([
            dep for dep in dependency_status.values()
            if dep["status"] == "healthy"
        ])
        
        total_deps = len(dependency_status)
        return (healthy_deps / total_deps) * 100 if total_deps > 0 else 100.0

    @asynccontextmanager
    async def service_lifecycle(self, service_definition: ServiceDefinition):
        """Context manager for service lifecycle management"""
        logger.info(f"Starting service lifecycle for {service_definition.service_name}")
        
        # Register service
        service_id = await self.register_service(service_definition)
        
        try:
            yield service_id
        finally:
            # Deregister service on exit
            logger.info(f"Ending service lifecycle for {service_definition.service_name}")
            await self.deregister_service(service_id)


# Export main classes
__all__ = [
    'ServiceRegistry',
    'ServiceStatus',
    'HealthCheckType',
    'LoadBalanceStrategy',
    'ServiceEndpoint',
    'HealthCheck',
    'HealthResult',
    'ServiceMetrics',
    'ServiceDefinition',
    'ServiceInstance',
    'CircuitBreaker',
    'HealthChecker',
    'LoadBalancer'
]