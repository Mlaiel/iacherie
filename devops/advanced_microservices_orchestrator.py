#!/usr/bin/env python3
"""
Advanced Microservices Orchestration & Service Mesh
=================================================

Enterprise-grade microservices orchestration system for Ainflue platform.
Implements service discovery, load balancing, circuit breakers, API gateway,
distributed tracing, and comprehensive service mesh management.

Author: Expert Team - Microservices Architect + Backend Senior Roles
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited.
"""

import asyncio
import json
import logging
import time
import uuid
import aiohttp
import aioredis
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading
import weakref
from abc import ABC, abstractmethod

# Service mesh and networking
import consul
import etcd3
import grpc
from grpc import aio as aio_grpc

# Monitoring and tracing
import opentelemetry
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Load balancing and circuit breaking
import circuit_breaker
from tenacity import retry, stop_after_attempt, wait_exponential

# Security and authentication
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

# Metrics and monitoring
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary


class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ServiceInstance:
    """Service instance information."""
    service_name: str
    instance_id: str
    host: str
    port: int
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_check_url: Optional[str] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    register_time: datetime = field(default_factory=datetime.now)
    weight: int = 100
    tags: List[str] = field(default_factory=list)


@dataclass
class ServiceRoute:
    """Service routing configuration."""
    service_name: str
    path_pattern: str
    methods: List[str] = field(default_factory=list)
    version_constraints: Optional[str] = None
    weight: int = 100
    timeout_seconds: int = 30
    retries: int = 3
    circuit_breaker_enabled: bool = True
    rate_limit: Optional[int] = None
    authentication_required: bool = True


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = Exception
    name: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Service performance metrics."""
    request_count: int = 0
    error_count: int = 0
    success_count: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    current_connections: int = 0
    total_connections: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


class ServiceDiscovery(ABC):
    """Abstract service discovery interface."""
    
    @abstractmethod
    async def register_service(self, service: ServiceInstance) -> bool:
        """Register a service instance."""
        pass
    
    @abstractmethod
    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service instance."""
        pass
    
    @abstractmethod
    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover service instances."""
        pass
    
    @abstractmethod
    async def health_check(self, service: ServiceInstance) -> ServiceStatus:
        """Check service health."""
        pass


class ConsulServiceDiscovery(ServiceDiscovery):
    """Consul-based service discovery implementation."""
    
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul_client = consul.Consul(host=consul_host, port=consul_port)
        self.logger = logging.getLogger("consul_discovery")
    
    async def register_service(self, service: ServiceInstance) -> bool:
        """Register service with Consul."""
        try:
            self.consul_client.agent.service.register(
                name=service.service_name,
                service_id=service.instance_id,
                address=service.host,
                port=service.port,
                tags=service.tags,
                check=consul.Check.http(
                    service.health_check_url or f"http://{service.host}:{service.port}/health",
                    interval="10s"
                ) if service.health_check_url else None,
                meta=service.metadata
            )
            self.logger.info(f"Registered service: {service.service_name} ({service.instance_id})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register service: {str(e)}")
            return False
    
    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister service from Consul."""
        try:
            self.consul_client.agent.service.deregister(instance_id)
            self.logger.info(f"Deregistered service: {service_name} ({instance_id})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to deregister service: {str(e)}")
            return False
    
    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover services from Consul."""
        try:
            _, services = self.consul_client.health.service(service_name, passing=True)
            
            instances = []
            for service_data in services:
                service_info = service_data['Service']
                instances.append(ServiceInstance(
                    service_name=service_info['Service'],
                    instance_id=service_info['ID'],
                    host=service_info['Address'],
                    port=service_info['Port'],
                    version=service_info.get('Meta', {}).get('version', '1.0.0'),
                    metadata=service_info.get('Meta', {}),
                    tags=service_info.get('Tags', []),
                    status=ServiceStatus.HEALTHY
                ))
            
            return instances
        except Exception as e:
            self.logger.error(f"Failed to discover services: {str(e)}")
            return []
    
    async def health_check(self, service: ServiceInstance) -> ServiceStatus:
        """Check service health via Consul."""
        try:
            _, checks = self.consul_client.health.service(service.service_name)
            for check_data in checks:
                if check_data['Service']['ID'] == service.instance_id:
                    for check in check_data['Checks']:
                        if check['Status'] == 'passing':
                            return ServiceStatus.HEALTHY
                        elif check['Status'] == 'warning':
                            return ServiceStatus.DEGRADED
                        else:
                            return ServiceStatus.UNHEALTHY
            return ServiceStatus.UNKNOWN
        except Exception:
            return ServiceStatus.UNKNOWN


class LoadBalancer:
    """Advanced load balancer with multiple strategies."""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.current_index = 0
        self.connections_count: Dict[str, int] = {}
        self.response_times: Dict[str, List[float]] = {}
        self.logger = logging.getLogger("load_balancer")
    
    async def select_instance(
        self, 
        instances: List[ServiceInstance], 
        client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """Select service instance based on load balancing strategy."""
        
        if not instances:
            return None
        
        # Filter healthy instances
        healthy_instances = [
            instance for instance in instances 
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            # Fallback to degraded instances if no healthy ones
            healthy_instances = [
                instance for instance in instances 
                if instance.status == ServiceStatus.DEGRADED
            ]
        
        if not healthy_instances:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_selection(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.IP_HASH:
            return self._ip_hash_selection(healthy_instances, client_ip)
        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_selection(healthy_instances)
        else:
            return self._round_robin_selection(healthy_instances)
    
    def _round_robin_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin selection."""
        instance = instances[self.current_index % len(instances)]
        self.current_index += 1
        return instance
    
    def _least_connections_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection."""
        min_connections = float('inf')
        selected_instance = instances[0]
        
        for instance in instances:
            instance_key = f"{instance.host}:{instance.port}"
            connections = self.connections_count.get(instance_key, 0)
            
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance
        
        return selected_instance
    
    def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection."""
        import random
        return random.choice(instances)
    
    def _weighted_round_robin_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round-robin selection."""
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return self._round_robin_selection(instances)
        
        # Simplified weighted selection
        import random
        rand_weight = random.randint(1, total_weight)
        current_weight = 0
        
        for instance in instances:
            current_weight += instance.weight
            if rand_weight <= current_weight:
                return instance
        
        return instances[0]
    
    def _ip_hash_selection(self, instances: List[ServiceInstance], client_ip: Optional[str]) -> ServiceInstance:
        """IP hash-based selection for session affinity."""
        if not client_ip:
            return self._round_robin_selection(instances)
        
        hash_value = hash(client_ip) % len(instances)
        return instances[hash_value]
    
    def _least_response_time_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least response time selection."""
        min_response_time = float('inf')
        selected_instance = instances[0]
        
        for instance in instances:
            instance_key = f"{instance.host}:{instance.port}"
            response_times = self.response_times.get(instance_key, [])
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                if avg_response_time < min_response_time:
                    min_response_time = avg_response_time
                    selected_instance = instance
        
        return selected_instance
    
    async def record_connection_start(self, instance: ServiceInstance):
        """Record connection start."""
        instance_key = f"{instance.host}:{instance.port}"
        self.connections_count[instance_key] = self.connections_count.get(instance_key, 0) + 1
    
    async def record_connection_end(self, instance: ServiceInstance, response_time: float):
        """Record connection end and response time."""
        instance_key = f"{instance.host}:{instance.port}"
        
        # Decrement connection count
        if instance_key in self.connections_count:
            self.connections_count[instance_key] = max(0, self.connections_count[instance_key] - 1)
        
        # Record response time (keep last 100 measurements)
        if instance_key not in self.response_times:
            self.response_times[instance_key] = []
        
        self.response_times[instance_key].append(response_time)
        if len(self.response_times[instance_key]) > 100:
            self.response_times[instance_key] = self.response_times[instance_key][-100:]


class AdvancedCircuitBreaker:
    """Advanced circuit breaker with configurable behavior."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.half_open_success_threshold = 3
        self.lock = threading.Lock()
        self.logger = logging.getLogger("circuit_breaker")
        
        # Metrics
        self.state_change_count = Counter(
            'circuit_breaker_state_changes_total',
            'Circuit breaker state changes',
            ['service', 'from_state', 'to_state']
        )
        self.request_count = Counter(
            'circuit_breaker_requests_total',
            'Circuit breaker requests',
            ['service', 'state', 'result']
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._change_state(CircuitState.HALF_OPEN)
                else:
                    raise circuit_breaker.CircuitBreakerOpenException("Circuit breaker is open")
            
            return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        with self.lock:
            if exc_type is None:
                # Success
                self._on_success()
                self.request_count.labels(
                    service=self.config.name or 'unknown',
                    state=self.state.value,
                    result='success'
                ).inc()
            elif issubclass(exc_type, self.config.expected_exception):
                # Expected failure
                self._on_failure()
                self.request_count.labels(
                    service=self.config.name or 'unknown',
                    state=self.state.value,
                    result='failure'
                ).inc()
        
        return False  # Don't suppress exceptions
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() > self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                self._change_state(CircuitState.CLOSED)
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._change_state(CircuitState.OPEN)
        elif self.state == CircuitState.HALF_OPEN:
            self._change_state(CircuitState.OPEN)
            self.success_count = 0
    
    def _change_state(self, new_state: CircuitState):
        """Change circuit breaker state."""
        old_state = self.state
        self.state = new_state
        
        self.logger.info(f"Circuit breaker state changed: {old_state.value} -> {new_state.value}")
        
        self.state_change_count.labels(
            service=self.config.name or 'unknown',
            from_state=old_state.value,
            to_state=new_state.value
        ).inc()


class APIGateway:
    """Advanced API Gateway with routing, authentication, and rate limiting."""
    
    def __init__(self, service_discovery: ServiceDiscovery):
        self.service_discovery = service_discovery
        self.load_balancer = LoadBalancer()
        self.routes: Dict[str, ServiceRoute] = {}
        self.circuit_breakers: Dict[str, AdvancedCircuitBreaker] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("api_gateway")
        
        # Metrics
        self._setup_metrics()
        
        # HTTP client session
        self.session = None
    
    def _setup_metrics(self):
        """Setup Prometheus metrics."""
        self.metrics = {
            'requests_total': Counter(
                'gateway_requests_total',
                'Total gateway requests',
                ['service', 'method', 'status']
            ),
            'request_duration': Histogram(
                'gateway_request_duration_seconds',
                'Gateway request duration',
                ['service', 'method']
            ),
            'active_connections': Gauge(
                'gateway_active_connections',
                'Active gateway connections',
                ['service']
            )
        }
    
    async def initialize(self):
        """Initialize API Gateway."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=1000)
        )
        self.logger.info("API Gateway initialized")
    
    async def shutdown(self):
        """Shutdown API Gateway."""
        if self.session:
            await self.session.close()
        self.logger.info("API Gateway shutdown")
    
    def add_route(self, route: ServiceRoute):
        """Add service route."""
        self.routes[route.path_pattern] = route
        
        # Create circuit breaker for service
        if route.circuit_breaker_enabled:
            circuit_config = CircuitBreakerConfig(name=route.service_name)
            self.circuit_breakers[route.service_name] = AdvancedCircuitBreaker(circuit_config)
        
        self.logger.info(f"Added route: {route.path_pattern} -> {route.service_name}")
    
    async def handle_request(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        query_params: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[int, Dict[str, str], Optional[bytes]]:
        """Handle incoming request through gateway."""
        
        # Find matching route
        route = self._find_route(path, method)
        if not route:
            return 404, {}, b'{"error": "Route not found"}'
        
        # Check authentication
        if route.authentication_required and not self._authenticate_request(headers):
            return 401, {}, b'{"error": "Authentication required"}'
        
        # Check rate limiting
        if route.rate_limit and not await self._check_rate_limit(route, client_ip):
            return 429, {}, b'{"error": "Rate limit exceeded"}'
        
        # Discover service instances
        instances = await self.service_discovery.discover_services(route.service_name)
        if not instances:
            return 503, {}, b'{"error": "Service unavailable"}'
        
        # Select instance using load balancer
        instance = await self.load_balancer.select_instance(instances, client_ip)
        if not instance:
            return 503, {}, b'{"error": "No healthy instances"}'
        
        # Handle request with circuit breaker
        start_time = time.time()
        
        try:
            circuit_breaker = self.circuit_breakers.get(route.service_name)
            
            if circuit_breaker:
                async with circuit_breaker:
                    return await self._proxy_request(
                        instance, route, path, method, headers, body, query_params
                    )
            else:
                return await self._proxy_request(
                    instance, route, path, method, headers, body, query_params
                )
        
        except circuit_breaker.CircuitBreakerOpenException:
            return 503, {}, b'{"error": "Service temporarily unavailable"}'
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            return 500, {}, b'{"error": "Internal server error"}'
        
        finally:
            # Record metrics
            duration = time.time() - start_time
            await self.load_balancer.record_connection_end(instance, duration)
            
            self.metrics['request_duration'].labels(
                service=route.service_name,
                method=method
            ).observe(duration)
    
    async def _proxy_request(
        self,
        instance: ServiceInstance,
        route: ServiceRoute,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes],
        query_params: Optional[Dict[str, str]]
    ) -> Tuple[int, Dict[str, str], Optional[bytes]]:
        """Proxy request to service instance."""
        
        # Record connection start
        await self.load_balancer.record_connection_start(instance)
        
        # Build target URL
        target_url = f"http://{instance.host}:{instance.port}{path}"
        
        # Prepare headers (remove hop-by-hop headers)
        proxy_headers = {k: v for k, v in headers.items() 
                        if k.lower() not in ['connection', 'upgrade', 'proxy-authenticate']}
        
        # Add instance metadata to headers
        proxy_headers['X-Instance-ID'] = instance.instance_id
        proxy_headers['X-Instance-Version'] = instance.version
        
        try:
            # Make request with retries
            for attempt in range(route.retries + 1):
                try:
                    async with self.session.request(
                        method=method,
                        url=target_url,
                        headers=proxy_headers,
                        data=body,
                        params=query_params,
                        timeout=aiohttp.ClientTimeout(total=route.timeout_seconds)
                    ) as response:
                        
                        response_body = await response.read()
                        response_headers = dict(response.headers)
                        
                        # Record success metric
                        self.metrics['requests_total'].labels(
                            service=route.service_name,
                            method=method,
                            status=str(response.status)
                        ).inc()
                        
                        return response.status, response_headers, response_body
                
                except aiohttp.ClientError as e:
                    if attempt == route.retries:
                        raise
                    await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
        
        except Exception as e:
            # Record failure metric
            self.metrics['requests_total'].labels(
                service=route.service_name,
                method=method,
                status='error'
            ).inc()
            raise
    
    def _find_route(self, path: str, method: str) -> Optional[ServiceRoute]:
        """Find matching route for path and method."""
        for pattern, route in self.routes.items():
            if self._match_path(pattern, path) and (not route.methods or method in route.methods):
                return route
        return None
    
    def _match_path(self, pattern: str, path: str) -> bool:
        """Match path against pattern (simplified)."""
        # In a real implementation, this would support regex patterns
        return pattern == path or pattern.rstrip('/*') in path
    
    def _authenticate_request(self, headers: Dict[str, str]) -> bool:
        """Authenticate request (simplified)."""
        auth_header = headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # In real implementation, verify JWT token
            return len(token) > 0
        return False
    
    async def _check_rate_limit(self, route: ServiceRoute, client_ip: Optional[str]) -> bool:
        """Check rate limiting (simplified)."""
        if not route.rate_limit or not client_ip:
            return True
        
        # In real implementation, use Redis or similar for distributed rate limiting
        key = f"{route.service_name}:{client_ip}"
        current_time = time.time()
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = {'count': 1, 'window_start': current_time}
            return True
        
        rate_data = self.rate_limiters[key]
        
        # Reset window if needed (1-minute window)
        if current_time - rate_data['window_start'] > 60:
            rate_data['count'] = 1
            rate_data['window_start'] = current_time
            return True
        
        if rate_data['count'] >= route.rate_limit:
            return False
        
        rate_data['count'] += 1
        return True


class ServiceMeshOrchestrator:
    """
    Advanced Service Mesh Orchestrator for enterprise microservices.
    
    Features:
    - Service discovery and registration
    - Intelligent load balancing with multiple strategies
    - Circuit breakers and fault tolerance
    - API Gateway with routing and security
    - Distributed tracing and monitoring
    - Rate limiting and throttling
    - Service health monitoring
    - Configuration management
    """
    
    def __init__(self, config_path: str = "config/service_mesh.yaml"):
        """Initialize service mesh orchestrator."""
        self.config_path = config_path
        self.logger = self._setup_logging()
        
        # Initialize components
        self.service_discovery = ConsulServiceDiscovery()
        self.api_gateway = APIGateway(self.service_discovery)
        self.load_balancer = LoadBalancer()
        
        # Service registry
        self.registered_services: Dict[str, List[ServiceInstance]] = {}
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        
        # Health monitoring
        self.health_check_interval = 30
        self.health_check_task = None
        
        # Configuration
        self.config = {}
        self._load_configuration()
        
        # Distributed tracing
        self._setup_tracing()
        
        self.logger.info("Service Mesh Orchestrator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup service mesh logging."""
        logger = logging.getLogger("service_mesh")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - SERVICE_MESH - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_configuration(self):
        """Load service mesh configuration."""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                import yaml
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                'discovery': {
                    'type': 'consul',
                    'consul': {
                        'host': 'localhost',
                        'port': 8500
                    }
                },
                'load_balancing': {
                    'strategy': 'round_robin'
                },
                'circuit_breaker': {
                    'failure_threshold': 5,
                    'recovery_timeout': 60
                },
                'health_check': {
                    'interval': 30,
                    'timeout': 10
                }
            }
    
    def _setup_tracing(self):
        """Setup distributed tracing."""
        try:
            # Configure OpenTelemetry
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)
            
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Instrument HTTP clients
            AioHttpClientInstrumentor().instrument()
            
            self.tracer = tracer
            self.logger.info("Distributed tracing configured")
            
        except Exception as e:
            self.logger.warning(f"Failed to setup tracing: {str(e)}")
            self.tracer = None
    
    async def start(self):
        """Start service mesh orchestrator."""
        # Initialize API gateway
        await self.api_gateway.initialize()
        
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
        
        self.logger.info("Service Mesh Orchestrator started")
    
    async def stop(self):
        """Stop service mesh orchestrator."""
        # Cancel health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown API gateway
        await self.api_gateway.shutdown()
        
        # Deregister all services
        for service_name, instances in self.registered_services.items():
            for instance in instances:
                await self.service_discovery.deregister_service(service_name, instance.instance_id)
        
        self.logger.info("Service Mesh Orchestrator stopped")
    
    async def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        version: str = "1.0.0",
        health_check_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Register a service with the mesh."""
        
        instance_id = f"{service_name}-{uuid.uuid4().hex[:8]}"
        
        service_instance = ServiceInstance(
            service_name=service_name,
            instance_id=instance_id,
            host=host,
            port=port,
            version=version,
            metadata=metadata or {},
            health_check_url=health_check_url,
            tags=tags or [],
            status=ServiceStatus.STARTING
        )
        
        # Register with service discovery
        success = await self.service_discovery.register_service(service_instance)
        
        if success:
            # Add to local registry
            if service_name not in self.registered_services:
                self.registered_services[service_name] = []
            
            self.registered_services[service_name].append(service_instance)
            
            # Initialize metrics
            self.service_metrics[instance_id] = ServiceMetrics()
            
            self.logger.info(f"Service registered: {service_name} ({instance_id})")
            return instance_id
        else:
            raise Exception(f"Failed to register service: {service_name}")
    
    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service from the mesh."""
        
        # Deregister from service discovery
        success = await self.service_discovery.deregister_service(service_name, instance_id)
        
        if success:
            # Remove from local registry
            if service_name in self.registered_services:
                self.registered_services[service_name] = [
                    instance for instance in self.registered_services[service_name]
                    if instance.instance_id != instance_id
                ]
                
                if not self.registered_services[service_name]:
                    del self.registered_services[service_name]
            
            # Remove metrics
            if instance_id in self.service_metrics:
                del self.service_metrics[instance_id]
            
            self.logger.info(f"Service deregistered: {service_name} ({instance_id})")
            return True
        
        return False
    
    def add_service_route(
        self,
        service_name: str,
        path_pattern: str,
        methods: Optional[List[str]] = None,
        timeout_seconds: int = 30,
        retries: int = 3
    ):
        """Add service route to API gateway."""
        
        route = ServiceRoute(
            service_name=service_name,
            path_pattern=path_pattern,
            methods=methods or ['GET', 'POST', 'PUT', 'DELETE'],
            timeout_seconds=timeout_seconds,
            retries=retries
        )
        
        self.api_gateway.add_route(route)
        self.logger.info(f"Route added: {path_pattern} -> {service_name}")
    
    async def handle_request(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        query_params: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[int, Dict[str, str], Optional[bytes]]:
        """Handle request through service mesh."""
        
        # Create tracing span if available
        if self.tracer:
            with self.tracer.start_as_current_span("service_mesh_request") as span:
                span.set_attribute("http.method", method)
                span.set_attribute("http.url", path)
                span.set_attribute("client.ip", client_ip or "unknown")
                
                return await self.api_gateway.handle_request(
                    path, method, headers, body, query_params, client_ip
                )
        else:
            return await self.api_gateway.handle_request(
                path, method, headers, body, query_params, client_ip
            )
    
    async def discover_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """Discover instances of a service."""
        return await self.service_discovery.discover_services(service_name)
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """Perform health checks on all registered services."""
        
        tasks = []
        for service_name, instances in self.registered_services.items():
            for instance in instances:
                tasks.append(self._check_instance_health(instance))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_instance_health(self, instance: ServiceInstance):
        """Check health of a service instance."""
        try:
            previous_status = instance.status
            new_status = await self.service_discovery.health_check(instance)
            
            if new_status != previous_status:
                instance.status = new_status
                self.logger.info(
                    f"Service {instance.service_name} ({instance.instance_id}) "
                    f"status changed: {previous_status.value} -> {new_status.value}"
                )
            
            instance.last_health_check = datetime.now()
            
        except Exception as e:
            instance.status = ServiceStatus.UNHEALTHY
            self.logger.error(f"Health check failed for {instance.instance_id}: {str(e)}")
    
    async def get_service_mesh_status(self) -> Dict[str, Any]:
        """Get comprehensive service mesh status."""
        
        total_services = len(self.registered_services)
        total_instances = sum(len(instances) for instances in self.registered_services.values())
        
        healthy_instances = 0
        unhealthy_instances = 0
        
        for instances in self.registered_services.values():
            for instance in instances:
                if instance.status == ServiceStatus.HEALTHY:
                    healthy_instances += 1
                elif instance.status == ServiceStatus.UNHEALTHY:
                    unhealthy_instances += 1
        
        return {
            'mesh_status': 'healthy' if unhealthy_instances == 0 else 'degraded',
            'total_services': total_services,
            'total_instances': total_instances,
            'healthy_instances': healthy_instances,
            'unhealthy_instances': unhealthy_instances,
            'services': {
                service_name: {
                    'instance_count': len(instances),
                    'healthy_count': len([i for i in instances if i.status == ServiceStatus.HEALTHY]),
                    'instances': [
                        {
                            'instance_id': instance.instance_id,
                            'host': instance.host,
                            'port': instance.port,
                            'version': instance.version,
                            'status': instance.status.value,
                            'last_health_check': instance.last_health_check.isoformat() if instance.last_health_check else None
                        }
                        for instance in instances
                    ]
                }
                for service_name, instances in self.registered_services.items()
            },
            'circuit_breakers': {
                service_name: cb.state.value
                for service_name, cb in self.api_gateway.circuit_breakers.items()
            }
        }
    
    async def get_service_metrics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get service performance metrics."""
        
        if service_name:
            instances = self.registered_services.get(service_name, [])
            return {
                'service_name': service_name,
                'instances': [
                    {
                        'instance_id': instance.instance_id,
                        'metrics': self.service_metrics.get(instance.instance_id, ServiceMetrics()).__dict__
                    }
                    for instance in instances
                ]
            }
        else:
            return {
                service_name: {
                    'instances': [
                        {
                            'instance_id': instance.instance_id,
                            'metrics': self.service_metrics.get(instance.instance_id, ServiceMetrics()).__dict__
                        }
                        for instance in instances
                    ]
                }
                for service_name, instances in self.registered_services.items()
            }


# Enterprise usage example
async def main():
    """Demonstrate service mesh orchestrator usage."""
    
    # Initialize service mesh
    mesh = ServiceMeshOrchestrator()
    await mesh.start()
    
    try:
        # Register services
        backend_id = await mesh.register_service(
            service_name="ainflue-backend",
            host="localhost",
            port=8000,
            version="1.0.0",
            health_check_url="http://localhost:8000/health",
            metadata={"team": "backend", "environment": "production"},
            tags=["api", "core"]
        )
        
        ai_engine_id = await mesh.register_service(
            service_name="ainflue-ai-engine",
            host="localhost", 
            port=8001,
            version="1.0.0",
            health_check_url="http://localhost:8001/health",
            metadata={"team": "ai", "environment": "production"},
            tags=["ai", "ml"]
        )
        
        # Add routes
        mesh.add_service_route(
            service_name="ainflue-backend",
            path_pattern="/api/*",
            methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        mesh.add_service_route(
            service_name="ainflue-ai-engine",
            path_pattern="/ai/*",
            methods=["POST"]
        )
        
        print("Services registered and routes configured")
        
        # Simulate requests
        headers = {"Authorization": "Bearer test-token"}
        
        # Backend API request
        status, resp_headers, body = await mesh.handle_request(
            path="/api/users",
            method="GET",
            headers=headers,
            client_ip="192.168.1.100"
        )
        print(f"Backend API response: {status}")
        
        # AI Engine request
        status, resp_headers, body = await mesh.handle_request(
            path="/ai/predict",
            method="POST",
            headers=headers,
            body=b'{"input": "test"}',
            client_ip="192.168.1.100"
        )
        print(f"AI Engine response: {status}")
        
        # Get mesh status
        mesh_status = await mesh.get_service_mesh_status()
        print(f"Mesh status: {mesh_status['mesh_status']}")
        print(f"Total services: {mesh_status['total_services']}")
        print(f"Total instances: {mesh_status['total_instances']}")
        
        # Wait for health checks
        await asyncio.sleep(5)
        
        # Get service metrics
        metrics = await mesh.get_service_metrics()
        print(f"Service metrics: {list(metrics.keys())}")
        
    finally:
        # Cleanup
        await mesh.stop()


if __name__ == "__main__":
    asyncio.run(main())