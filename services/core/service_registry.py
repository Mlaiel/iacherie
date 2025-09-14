"""
🔧 Microservice Orchestrator
Enterprise microservices orchestration with service mesh, circuit breakers, and auto-scaling

Demonstrates: Microservices + DevOps + Backend Senior expertise
Features: Service discovery, load balancing, circuit breakers, health monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
import json
import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import weakref

# Optional imports with fallbacks
try:
    import structlog
    logger = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False

try:
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    aiohttp = None
    HTTP_AVAILABLE = False
import random
import statistics

class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"

class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"

class ScalingDirection(str, Enum):
    """Scaling directions"""
    UP = "up"
    DOWN = "down"
    NONE = "none"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    host: str
    port: int
    protocol: str = "http"
    path: str = "/"
    weight: int = 100
    max_connections: int = 1000
    timeout_seconds: float = 30.0
    health_check_path: str = "/health"
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}{self.path}"
    
    @property
    def health_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}{self.health_check_path}"

class ServiceDefinition(BaseModel):
    """Service definition and configuration"""
    service_id: str = Field(..., description="Unique service identifier")
    name: str = Field(..., description="Human-readable service name")
    version: str = Field(..., description="Service version")
    description: Optional[str] = None
    endpoints: List[ServiceEndpoint] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    min_instances: int = Field(default=1, ge=1)
    max_instances: int = Field(default=10, ge=1)
    target_cpu_utilization: float = Field(default=70.0, ge=0.0, le=100.0)
    target_memory_utilization: float = Field(default=80.0, ge=0.0, le=100.0)
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    circuit_breaker_enabled: bool = True
    retry_attempts: int = Field(default=3, ge=0, le=10)
    timeout_seconds: float = Field(default=30.0, gt=0.0)
    registered_at: datetime = Field(default_factory=datetime.now)
    
    @validator('max_instances')
    def validate_max_instances(cls, v, values):
        min_instances = values.get('min_instances', 1)
        if v < min_instances:
            raise ValueError('max_instances must be >= min_instances')
        return v

class ServiceInstance(BaseModel):
    """Running service instance"""
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    endpoint: ServiceEndpoint
    status: ServiceStatus = ServiceStatus.UNKNOWN
    started_at: datetime = Field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    active_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CircuitBreaker:
    """
    Circuit breaker implementation for service resilience
    
    DevOps: Resilience patterns, failure handling
    Backend Senior: Advanced state management, performance optimization
    """
    
    def __init__(self, service_id: str, failure_threshold: int = 5, 
                 recovery_timeout: float = 60.0, success_threshold: int = 3):
        self.service_id = service_id
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.request_history = deque(maxlen=100)  # Last 100 requests
        
        logger.info("Circuit breaker initialized",
                   service_id=service_id,
                   failure_threshold=failure_threshold,
                   recovery_timeout=recovery_timeout)
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker transitioning to half-open",
                           service_id=self.service_id)
            else:
                raise Exception(f"Circuit breaker OPEN for service {self.service_id}")
        
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Record success
            self.request_history.append({
                'success': True,
                'response_time': response_time,
                'timestamp': time.time()
            })
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker closed after recovery",
                               service_id=self.service_id)
            else:
                self.failure_count = max(0, self.failure_count - 1)
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Record failure
            self.request_history.append({
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            })
            
            if (self.state == CircuitBreakerState.CLOSED and 
                self.failure_count >= self.failure_threshold):
                self.state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker opened due to failures",
                             service_id=self.service_id,
                             failure_count=self.failure_count)
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker reopened during half-open state",
                             service_id=self.service_id)
            
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        recent_requests = [r for r in self.request_history 
                          if time.time() - r['timestamp'] < 300]  # Last 5 minutes
        
        success_rate = 0.0
        avg_response_time = 0.0
        
        if recent_requests:
            successful = [r for r in recent_requests if r['success']]
            success_rate = len(successful) / len(recent_requests)
            
            if successful:
                avg_response_time = statistics.mean(r['response_time'] for r in successful)
        
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'success_rate': success_rate,
            'average_response_time': avg_response_time,
            'total_requests': len(self.request_history),
            'recent_requests': len(recent_requests)
        }

class LoadBalancer:
    """
    Intelligent load balancer with multiple strategies
    
    Microservices: Service mesh capabilities, intelligent routing
    Backend Senior: Performance optimization, algorithm implementation
    """
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.round_robin_index = 0
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
    
    async def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Select best instance based on load balancing strategy"""
        
        # Filter healthy instances
        healthy_instances = [
            instance for instance in instances 
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            # Try degraded instances as fallback
            healthy_instances = [
                instance for instance in instances
                if instance.status == ServiceStatus.DEGRADED
            ]
        
        if not healthy_instances:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return self._consistent_hash_select(healthy_instances)
        else:
            return self._round_robin_select(healthy_instances)
    
    def _round_robin_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Simple round-robin selection"""
        instance = instances[self.round_robin_index % len(instances)]
        self.round_robin_index += 1
        return instance
    
    def _weighted_round_robin_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round-robin based on endpoint weights"""
        total_weight = sum(instance.endpoint.weight for instance in instances)
        if total_weight == 0:
            return self._round_robin_select(instances)
        
        target_weight = (self.round_robin_index % total_weight) + 1
        current_weight = 0
        
        for instance in instances:
            current_weight += instance.endpoint.weight
            if current_weight >= target_weight:
                self.round_robin_index += 1
                return instance
        
        return instances[0]  # Fallback
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Select instance with least active connections"""
        return min(instances, key=lambda i: i.active_connections)
    
    def _least_response_time_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Select instance with lowest average response time"""
        best_instance = instances[0]
        best_time = float('inf')
        
        for instance in instances:
            avg_time = instance.average_response_time
            if avg_time < best_time:
                best_time = avg_time
                best_instance = instance
        
        return best_instance
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection"""
        return random.choice(instances)
    
    def _consistent_hash_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Consistent hash selection (simplified)"""
        # Simplified implementation - in production would use proper consistent hashing
        hash_value = hash(str(time.time())) % len(instances)
        return instances[hash_value]
    
    def record_request(self, instance_id: str, response_time: float, success: bool):
        """Record request metrics for load balancing decisions"""
        if success:
            self.response_times[instance_id].append(response_time)

class AutoScaler:
    """
    Auto-scaling manager for service instances
    
    DevOps: Auto-scaling, resource management
    Microservices: Dynamic service mesh scaling
    """
    
    def __init__(self, scale_up_threshold: float = 70.0, scale_down_threshold: float = 30.0,
                 cooldown_minutes: float = 5.0):
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_period = cooldown_minutes * 60  # Convert to seconds
        self.last_scaling_actions: Dict[str, float] = {}
        
        logger.info("Auto-scaler initialized",
                   scale_up_threshold=scale_up_threshold,
                   scale_down_threshold=scale_down_threshold,
                   cooldown_minutes=cooldown_minutes)
    
    async def evaluate_scaling(self, service_id: str, instances: List[ServiceInstance],
                             service_def: ServiceDefinition) -> ScalingDirection:
        """Evaluate if service needs scaling"""
        
        # Check cooldown period
        last_action_time = self.last_scaling_actions.get(service_id, 0)
        if time.time() - last_action_time < self.cooldown_period:
            return ScalingDirection.NONE
        
        if not instances:
            return ScalingDirection.UP
        
        # Calculate average utilization
        healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        if not healthy_instances:
            return ScalingDirection.NONE
        
        avg_cpu = statistics.mean(i.cpu_utilization for i in healthy_instances)
        avg_memory = statistics.mean(i.memory_utilization for i in healthy_instances)
        
        # Use the higher of CPU or memory utilization
        utilization = max(avg_cpu, avg_memory)
        
        current_count = len(instances)
        
        # Scale up conditions
        if (utilization > self.scale_up_threshold and 
            current_count < service_def.max_instances):
            logger.info("Scaling up recommended",
                       service_id=service_id,
                       utilization=utilization,
                       current_instances=current_count)
            return ScalingDirection.UP
        
        # Scale down conditions
        elif (utilization < self.scale_down_threshold and 
              current_count > service_def.min_instances):
            logger.info("Scaling down recommended",
                       service_id=service_id,
                       utilization=utilization,
                       current_instances=current_count)
            return ScalingDirection.DOWN
        
        return ScalingDirection.NONE
    
    def record_scaling_action(self, service_id: str):
        """Record scaling action for cooldown tracking"""
        self.last_scaling_actions[service_id] = time.time()

class ServiceRegistry:
    """
    Service registry for service discovery
    
    Microservices: Service discovery, registration
    Backend Senior: Efficient data structures, performance
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {}
        self.instances: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self.service_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        logger.info("Service registry initialized")
    
    async def register_service(self, service_def: ServiceDefinition) -> bool:
        """Register a new service"""
        try:
            self.services[service_def.service_id] = service_def
            
            # Initialize instance list if not exists
            if service_def.service_id not in self.instances:
                self.instances[service_def.service_id] = []
            
            # Store dependencies
            for dep in service_def.dependencies:
                self.service_dependencies[service_def.service_id].add(dep)
            
            logger.info("Service registered",
                       service_id=service_def.service_id,
                       name=service_def.name,
                       version=service_def.version)
            
            return True
            
        except Exception as e:
            logger.error("Service registration failed",
                        service_id=service_def.service_id,
                        error=str(e))
            return False
    
    async def register_instance(self, service_id: str, endpoint: ServiceEndpoint) -> Optional[ServiceInstance]:
        """Register a new service instance"""
        try:
            if service_id not in self.services:
                logger.error("Cannot register instance for unknown service", service_id=service_id)
                return None
            
            instance = ServiceInstance(
                service_id=service_id,
                endpoint=endpoint,
                status=ServiceStatus.UNKNOWN
            )
            
            self.instances[service_id].append(instance)
            
            logger.info("Service instance registered",
                       service_id=service_id,
                       instance_id=instance.instance_id,
                       endpoint=endpoint.url)
            
            return instance
            
        except Exception as e:
            logger.error("Instance registration failed",
                        service_id=service_id,
                        error=str(e))
            return None
    
    async def deregister_instance(self, service_id: str, instance_id: str) -> bool:
        """Deregister a service instance"""
        try:
            instances = self.instances.get(service_id, [])
            for i, instance in enumerate(instances):
                if instance.instance_id == instance_id:
                    instances.pop(i)
                    logger.info("Service instance deregistered",
                               service_id=service_id,
                               instance_id=instance_id)
                    return True
            
            logger.warning("Instance not found for deregistration",
                          service_id=service_id,
                          instance_id=instance_id)
            return False
            
        except Exception as e:
            logger.error("Instance deregistration failed",
                        service_id=service_id,
                        instance_id=instance_id,
                        error=str(e))
            return False
    
    async def discover_services(self, tags: List[str] = None) -> List[ServiceDefinition]:
        """Discover services by tags"""
        if not tags:
            return list(self.services.values())
        
        matching_services = []
        for service in self.services.values():
            if any(tag in service.tags for tag in tags):
                matching_services.append(service)
        
        return matching_services
    
    async def get_service_instances(self, service_id: str) -> List[ServiceInstance]:
        """Get all instances for a service"""
        return self.instances.get(service_id, [])
    
    async def get_healthy_instances(self, service_id: str) -> List[ServiceInstance]:
        """Get only healthy instances for a service"""
        instances = self.instances.get(service_id, [])
        return [i for i in instances if i.status == ServiceStatus.HEALTHY]

class MicroserviceOrchestrator:
    """
    Enterprise Microservice Orchestrator
    
    Demonstrates expertise in:
    - Microservices: Service mesh, discovery, communication patterns
    - DevOps: Auto-scaling, health monitoring, resilience patterns
    - Backend Senior: Complex async orchestration, performance optimization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.registry = ServiceRegistry()
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.auto_scaler = AutoScaler(
            scale_up_threshold=self.config.get('scale_up_threshold', 70.0),
            scale_down_threshold=self.config.get('scale_down_threshold', 30.0),
            cooldown_minutes=self.config.get('cooldown_minutes', 5.0)
        )
        
        self.health_check_interval = self.config.get('health_check_interval', 30)  # seconds
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'circuit_breaker_trips': 0,
            'auto_scaling_actions': 0,
            'average_response_time': 0.0
        }
        
        # Start background tasks
        self._health_check_task = None
        self._auto_scaling_task = None
        self._start_background_tasks()
        
        logger.info("Microservice Orchestrator initialized",
                   config=self.config)
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._auto_scaling_task = asyncio.create_task(self._auto_scaling_loop())
    
    async def register_service(self, service_def: ServiceDefinition) -> bool:
        """Register a new service with the orchestrator"""
        success = await self.registry.register_service(service_def)
        
        if success:
            # Initialize load balancer
            self.load_balancers[service_def.service_id] = LoadBalancer(
                service_def.load_balancing_strategy
            )
            
            # Initialize circuit breaker if enabled
            if service_def.circuit_breaker_enabled:
                self.circuit_breakers[service_def.service_id] = CircuitBreaker(
                    service_def.service_id,
                    failure_threshold=self.config.get('circuit_breaker_failure_threshold', 5),
                    recovery_timeout=self.config.get('circuit_breaker_recovery_timeout', 60.0)
                )
        
        return success
    
    async def register_instance(self, service_id: str, endpoint: ServiceEndpoint) -> Optional[ServiceInstance]:
        """Register a new service instance"""
        return await self.registry.register_instance(service_id, endpoint)
    
    async def call_service(self, service_id: str, method: str = "GET", 
                          path: str = "/", data: Any = None, 
                          headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Make a call to a service through the orchestrator
        
        Microservices: Service-to-service communication
        Backend Senior: Resilient request handling
        DevOps: Circuit breaker, load balancing
        """
        start_time = time.time()
        
        try:
            # Get service instances
            instances = await self.registry.get_service_instances(service_id)
            if not instances:
                raise Exception(f"No instances available for service {service_id}")
            
            # Select instance using load balancer
            load_balancer = self.load_balancers.get(service_id)
            if not load_balancer:
                raise Exception(f"No load balancer configured for service {service_id}")
            
            selected_instance = await load_balancer.select_instance(instances)
            if not selected_instance:
                raise Exception(f"No healthy instances available for service {service_id}")
            
            # Get circuit breaker
            circuit_breaker = self.circuit_breakers.get(service_id)
            
            # Make the actual request
            async def make_request():
                return await self._execute_http_request(
                    selected_instance, method, path, data, headers
                )
            
            # Execute with circuit breaker if available
            if circuit_breaker:
                result = await circuit_breaker.call(make_request)
            else:
                result = await make_request()
            
            # Update metrics
            response_time = time.time() - start_time
            self.metrics['total_requests'] += 1
            self.metrics['successful_requests'] += 1
            self._update_average_response_time(response_time)
            
            # Update load balancer metrics
            load_balancer.record_request(selected_instance.instance_id, response_time, True)
            
            # Update instance metrics
            selected_instance.total_requests += 1
            selected_instance.successful_requests += 1
            selected_instance.active_connections = max(0, selected_instance.active_connections - 1)
            
            logger.info("Service call successful",
                       service_id=service_id,
                       instance_id=selected_instance.instance_id,
                       response_time=response_time,
                       method=method,
                       path=path)
            
            return result
            
        except Exception as e:
            # Update failure metrics
            response_time = time.time() - start_time
            self.metrics['total_requests'] += 1
            self.metrics['failed_requests'] += 1
            
            logger.error("Service call failed",
                        service_id=service_id,
                        error=str(e),
                        response_time=response_time,
                        method=method,
                        path=path)
            
            raise
    
    async def _execute_http_request(self, instance: ServiceInstance, method: str,
                                  path: str, data: Any, headers: Dict[str, str]) -> Dict[str, Any]:
        """Execute HTTP request to service instance"""
        url = f"{instance.endpoint.url.rstrip('/')}{path}"
        timeout = aiohttp.ClientTimeout(total=instance.endpoint.timeout_seconds)
        
        # Update active connections
        instance.active_connections += 1
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    headers=headers or {}
                ) as response:
                    
                    if response.status >= 400:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}"
                        )
                    
                    return {
                        'status': response.status,
                        'data': await response.json() if response.content_type == 'application/json' else await response.text(),
                        'headers': dict(response.headers)
                    }
        
        except Exception as e:
            instance.failed_requests += 1
            raise
        
        finally:
            instance.active_connections = max(0, instance.active_connections - 1)
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(5)  # Short retry interval
    
    async def _perform_health_checks(self):
        """Perform health checks on all service instances"""
        all_services = await self.registry.discover_services()
        
        for service in all_services:
            instances = await self.registry.get_service_instances(service.service_id)
            
            # Perform health checks in parallel
            health_check_tasks = [
                self._check_instance_health(instance)
                for instance in instances
            ]
            
            if health_check_tasks:
                await asyncio.gather(*health_check_tasks, return_exceptions=True)
    
    async def _check_instance_health(self, instance: ServiceInstance):
        """Check health of a single service instance"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    instance.endpoint.health_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Update instance status
                        old_status = instance.status
                        instance.status = ServiceStatus.HEALTHY
                        instance.last_health_check = datetime.now()
                        instance.consecutive_failures = 0
                        
                        # Update resource utilization if available
                        if 'cpu_utilization' in health_data:
                            instance.cpu_utilization = health_data['cpu_utilization']
                        if 'memory_utilization' in health_data:
                            instance.memory_utilization = health_data['memory_utilization']
                        
                        # Update average response time
                        if instance.average_response_time == 0:
                            instance.average_response_time = response_time
                        else:
                            # Exponential moving average
                            alpha = 0.1
                            instance.average_response_time = (
                                alpha * response_time + 
                                (1 - alpha) * instance.average_response_time
                            )
                        
                        if old_status != ServiceStatus.HEALTHY:
                            logger.info("Instance recovered",
                                       service_id=instance.service_id,
                                       instance_id=instance.instance_id)
                    
                    else:
                        await self._mark_instance_unhealthy(instance, f"Health check returned {response.status}")
        
        except Exception as e:
            await self._mark_instance_unhealthy(instance, str(e))
    
    async def _mark_instance_unhealthy(self, instance: ServiceInstance, reason: str):
        """Mark instance as unhealthy"""
        instance.consecutive_failures += 1
        
        if instance.consecutive_failures >= 3:
            old_status = instance.status
            instance.status = ServiceStatus.UNHEALTHY
            
            if old_status != ServiceStatus.UNHEALTHY:
                logger.warning("Instance marked unhealthy",
                             service_id=instance.service_id,
                             instance_id=instance.instance_id,
                             reason=reason,
                             consecutive_failures=instance.consecutive_failures)
        elif instance.consecutive_failures >= 1:
            instance.status = ServiceStatus.DEGRADED
    
    async def _auto_scaling_loop(self):
        """Background auto-scaling loop"""
        while True:
            try:
                await self._perform_auto_scaling()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error("Auto-scaling loop error", error=str(e))
                await asyncio.sleep(30)  # Retry after 30 seconds
    
    async def _perform_auto_scaling(self):
        """Perform auto-scaling evaluation for all services"""
        all_services = await self.registry.discover_services()
        
        for service in all_services:
            try:
                instances = await self.registry.get_service_instances(service.service_id)
                scaling_direction = await self.auto_scaler.evaluate_scaling(
                    service.service_id, instances, service
                )
                
                if scaling_direction == ScalingDirection.UP:
                    await self._scale_up_service(service)
                elif scaling_direction == ScalingDirection.DOWN:
                    await self._scale_down_service(service)
                    
            except Exception as e:
                logger.error("Auto-scaling evaluation failed",
                           service_id=service.service_id,
                           error=str(e))
    
    async def _scale_up_service(self, service: ServiceDefinition):
        """Scale up a service by adding instances"""
        try:
            # In a real implementation, this would trigger container/VM creation
            # For now, we'll simulate by adding a new endpoint
            
            instances = await self.registry.get_service_instances(service.service_id)
            if len(instances) >= service.max_instances:
                return
            
            # Create new endpoint (simulated)
            new_port = 8000 + len(instances)
            new_endpoint = ServiceEndpoint(
                host="localhost",
                port=new_port,
                protocol="http"
            )
            
            new_instance = await self.registry.register_instance(service.service_id, new_endpoint)
            if new_instance:
                self.auto_scaler.record_scaling_action(service.service_id)
                self.metrics['auto_scaling_actions'] += 1
                
                logger.info("Service scaled up",
                           service_id=service.service_id,
                           new_instance_id=new_instance.instance_id,
                           total_instances=len(instances) + 1)
                
        except Exception as e:
            logger.error("Scale up failed",
                        service_id=service.service_id,
                        error=str(e))
    
    async def _scale_down_service(self, service: ServiceDefinition):
        """Scale down a service by removing instances"""
        try:
            instances = await self.registry.get_service_instances(service.service_id)
            if len(instances) <= service.min_instances:
                return
            
            # Find least utilized instance to remove
            healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
            if not healthy_instances:
                return
            
            # Remove instance with lowest utilization
            instance_to_remove = min(
                healthy_instances,
                key=lambda i: max(i.cpu_utilization, i.memory_utilization)
            )
            
            success = await self.registry.deregister_instance(
                service.service_id, instance_to_remove.instance_id
            )
            
            if success:
                self.auto_scaler.record_scaling_action(service.service_id)
                self.metrics['auto_scaling_actions'] += 1
                
                logger.info("Service scaled down",
                           service_id=service.service_id,
                           removed_instance_id=instance_to_remove.instance_id,
                           total_instances=len(instances) - 1)
                
        except Exception as e:
            logger.error("Scale down failed",
                        service_id=service.service_id,
                        error=str(e))
    
    def _update_average_response_time(self, response_time: float):
        """Update average response time metric"""
        total = self.metrics['total_requests']
        if total <= 1:
            self.metrics['average_response_time'] = response_time
        else:
            current_avg = self.metrics['average_response_time']
            self.metrics['average_response_time'] = (
                (current_avg * (total - 1) + response_time) / total
            )
    
    async def get_service_topology(self) -> Dict[str, Any]:
        """Get complete service topology and dependencies"""
        topology = {
            'services': {},
            'dependencies': {},
            'metrics': self.metrics
        }
        
        all_services = await self.registry.discover_services()
        
        for service in all_services:
            instances = await self.registry.get_service_instances(service.service_id)
            
            topology['services'][service.service_id] = {
                'definition': service.dict(),
                'instances': [
                    {
                        'instance_id': instance.instance_id,
                        'endpoint': f"{instance.endpoint.host}:{instance.endpoint.port}",
                        'status': instance.status.value,
                        'health': {
                            'consecutive_failures': instance.consecutive_failures,
                            'last_health_check': instance.last_health_check.isoformat() if instance.last_health_check else None,
                            'response_time': instance.average_response_time
                        },
                        'metrics': {
                            'total_requests': instance.total_requests,
                            'successful_requests': instance.successful_requests,
                            'failed_requests': instance.failed_requests,
                            'active_connections': instance.active_connections,
                            'cpu_utilization': instance.cpu_utilization,
                            'memory_utilization': instance.memory_utilization
                        }
                    }
                    for instance in instances
                ],
                'circuit_breaker': None,
                'load_balancer': {
                    'strategy': service.load_balancing_strategy.value
                }
            }
            
            # Add circuit breaker info if available
            if service.service_id in self.circuit_breakers:
                cb_metrics = self.circuit_breakers[service.service_id].get_metrics()
                topology['services'][service.service_id]['circuit_breaker'] = cb_metrics
            
            # Add dependencies
            topology['dependencies'][service.service_id] = list(service.dependencies)
        
        return topology
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator metrics"""
        all_services = await self.registry.discover_services()
        
        service_metrics = {}
        for service in all_services:
            instances = await self.registry.get_service_instances(service.service_id)
            healthy_count = len([i for i in instances if i.status == ServiceStatus.HEALTHY])
            
            service_metrics[service.service_id] = {
                'total_instances': len(instances),
                'healthy_instances': healthy_count,
                'health_ratio': healthy_count / max(len(instances), 1),
                'circuit_breaker_state': (
                    self.circuit_breakers[service.service_id].state.value
                    if service.service_id in self.circuit_breakers else None
                )
            }
        
        return {
            **self.metrics,
            'services': service_metrics,
            'total_services': len(all_services),
            'orchestrator_status': 'healthy'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Orchestrator health check"""
        all_services = await self.registry.discover_services()
        total_instances = sum(
            len(await self.registry.get_service_instances(service.service_id))
            for service in all_services
        )
        
        return {
            'service': 'microservice_orchestrator',
            'status': 'healthy',
            'version': '1.0.0',
            'registered_services': len(all_services),
            'total_instances': total_instances,
            'background_tasks': {
                'health_check': not self._health_check_task.done() if self._health_check_task else False,
                'auto_scaling': not self._auto_scaling_task.done() if self._auto_scaling_task else False
            }
        }
    
    async def shutdown(self):
        """Graceful shutdown of orchestrator"""
        logger.info("Shutting down Microservice Orchestrator")
        
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._auto_scaling_task:
            self._auto_scaling_task.cancel()
        
        # Wait for tasks to complete
        if self._health_check_task:
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._auto_scaling_task:
            try:
                await self._auto_scaling_task
            except asyncio.CancelledError:
                pass

# Example usage and testing
async def example_usage():
    """Example usage of the Microservice Orchestrator"""
    
    # Initialize orchestrator
    orchestrator = MicroserviceOrchestrator({
        'health_check_interval': 10,
        'scale_up_threshold': 70.0,
        'scale_down_threshold': 30.0,
        'cooldown_minutes': 2.0
    })
    
    # Define a service
    user_service = ServiceDefinition(
        service_id="user_service",
        name="User Management Service",
        version="1.0.0",
        description="Manages user accounts and authentication",
        dependencies=["database_service"],
        tags=["authentication", "user_management"],
        min_instances=2,
        max_instances=5,
        load_balancing_strategy=LoadBalancingStrategy.LEAST_CONNECTIONS
    )
    
    # Register service
    await orchestrator.register_service(user_service)
    
    # Register service instances
    for i in range(2):
        endpoint = ServiceEndpoint(
            host="localhost",
            port=8000 + i,
            protocol="http",
            health_check_path="/health"
        )
        await orchestrator.register_instance("user_service", endpoint)
    
    # Wait a bit for health checks
    await asyncio.sleep(2)
    
    # Get service topology
    topology = await orchestrator.get_service_topology()
    print(f"Service topology: {json.dumps(topology, indent=2, default=str)}")
    
    # Get metrics
    metrics = await orchestrator.get_service_metrics()
    print(f"Orchestrator metrics: {metrics}")
    
    # Shutdown
    await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(example_usage())