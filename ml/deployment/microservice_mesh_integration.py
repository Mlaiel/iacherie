#!/usr/bin/env python3
"""
🌐 Microservice Mesh Integration for ML Workloads
Microservices Implementation - Service Mesh Coordination & Communication

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

Enterprise service mesh integration for ML microservices with intelligent
routing, load balancing, and inter-service communication optimization.
"""

import asyncio
import logging
import json
import time
import aiohttp
import threading
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import random
import networkx as nx
from collections import defaultdict, deque
import socket
import subprocess

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types of ML microservices"""
    INFERENCE_ENGINE = "inference_engine"
    FEATURE_STORE = "feature_store"
    MODEL_REGISTRY = "model_registry"
    TRAINING_SERVICE = "training_service"
    MONITORING_SERVICE = "monitoring_service"
    DATA_PIPELINE = "data_pipeline"
    GATEWAY = "gateway"
    LOAD_BALANCER = "load_balancer"

class RoutingStrategy(Enum):
    """Service routing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_RANDOM = "weighted_random"
    CREATOR_AFFINITY = "creator_affinity"
    MODEL_AFFINITY = "model_affinity"
    PERFORMANCE_BASED = "performance_based"

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ServiceInstance:
    """Individual service instance information"""
    service_id: str
    service_name: str
    service_type: ServiceType
    host: str
    port: int
    version: str = "1.0.0"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_connections: int = 0
    request_count: int = 0
    error_count: int = 0
    
    @property
    def endpoint(self) -> str:
        """Get full service endpoint"""
        return f"http://{self.host}:{self.port}"
    
    @property
    def health_score(self) -> float:
        """Calculate health score based on metrics"""
        if self.status == ServiceStatus.HEALTHY:
            base_score = 1.0
        elif self.status == ServiceStatus.DEGRADED:
            base_score = 0.7
        elif self.status == ServiceStatus.UNHEALTHY:
            base_score = 0.3
        else:
            base_score = 0.5
        
        # Adjust based on performance metrics
        performance_factor = 1.0
        if self.response_time_ms > 1000:  # >1s response time
            performance_factor *= 0.8
        if self.cpu_usage > 0.8:  # >80% CPU
            performance_factor *= 0.9
        if self.memory_usage > 0.9:  # >90% memory
            performance_factor *= 0.8
        
        # Error rate factor
        if self.request_count > 0:
            error_rate = self.error_count / self.request_count
            if error_rate > 0.1:  # >10% error rate
                performance_factor *= 0.7
        
        return base_score * performance_factor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'service_id': self.service_id,
            'service_name': self.service_name,
            'service_type': self.service_type.value,
            'host': self.host,
            'port': self.port,
            'version': self.version,
            'tags': self.tags,
            'metadata': self.metadata,
            'status': self.status.value,
            'last_health_check': self.last_health_check.isoformat(),
            'response_time_ms': self.response_time_ms,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'active_connections': self.active_connections,
            'request_count': self.request_count,
            'error_count': self.error_count,
            'health_score': self.health_score
        }

@dataclass
class ServiceRoute:
    """Service routing configuration"""
    route_id: str
    source_pattern: str
    target_services: List[str]
    routing_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    weights: Dict[str, float] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 5000
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    rate_limit_per_minute: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for configuration"""
        return {
            'route_id': self.route_id,
            'source_pattern': self.source_pattern,
            'target_services': self.target_services,
            'routing_strategy': self.routing_strategy.value,
            'weights': self.weights,
            'conditions': self.conditions,
            'timeout_ms': self.timeout_ms,
            'retry_count': self.retry_count,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'rate_limit_per_minute': self.rate_limit_per_minute
        }

@dataclass
class MeshConfig:
    """Service mesh configuration"""
    mesh_name: str = "ml-mesh"
    discovery_interval_seconds: int = 30
    health_check_interval_seconds: int = 15
    circuit_breaker_threshold: float = 0.5
    circuit_breaker_timeout_seconds: int = 60
    enable_load_balancing: bool = True
    enable_circuit_breaker: bool = True
    enable_retry: bool = True
    enable_timeout: bool = True
    enable_rate_limiting: bool = True
    enable_metrics_collection: bool = True
    enable_tracing: bool = True
    mesh_port: int = 8080

class CircuitBreaker:
    """Circuit breaker implementation for service protection"""
    
    def __init__(self, failure_threshold: float = 0.5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "OPEN":
                if (datetime.utcnow() - self.last_failure_time).total_seconds() > self.timeout_seconds:
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            self.success_count += 1
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            total_calls = self.failure_count + self.success_count
            if total_calls > 0 and (self.failure_count / total_calls) > self.failure_threshold:
                self.state = "OPEN"

class ServiceRegistry:
    """Service discovery and registry"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInstance] = {}
        self.services_by_type: Dict[ServiceType, List[str]] = defaultdict(list)
        self.services_by_name: Dict[str, List[str]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def register_service(self, service: ServiceInstance) -> bool:
        """Register a new service instance"""
        with self.lock:
            self.services[service.service_id] = service
            
            # Index by type
            if service.service_id not in self.services_by_type[service.service_type]:
                self.services_by_type[service.service_type].append(service.service_id)
            
            # Index by name
            if service.service_id not in self.services_by_name[service.service_name]:
                self.services_by_name[service.service_name].append(service.service_id)
        
        logger.info(f"🔗 Registered service: {service.service_name} ({service.service_id})")
        return True
    
    def deregister_service(self, service_id: str) -> bool:
        """Deregister a service instance"""
        with self.lock:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # Remove from indexes
            self.services_by_type[service.service_type].remove(service_id)
            self.services_by_name[service.service_name].remove(service_id)
            
            # Remove from main registry
            del self.services[service_id]
        
        logger.info(f"🔌 Deregistered service: {service_id}")
        return True
    
    def discover_services(
        self,
        service_type: Optional[ServiceType] = None,
        service_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[ServiceInstance]:
        """Discover services based on criteria"""
        with self.lock:
            candidates = list(self.services.values())
        
        # Filter by type
        if service_type:
            candidates = [s for s in candidates if s.service_type == service_type]
        
        # Filter by name
        if service_name:
            candidates = [s for s in candidates if s.service_name == service_name]
        
        # Filter by tags
        if tags:
            candidates = [
                s for s in candidates
                if all(s.tags.get(k) == v for k, v in tags.items())
            ]
        
        return candidates
    
    def get_healthy_services(
        self,
        service_type: Optional[ServiceType] = None
    ) -> List[ServiceInstance]:
        """Get only healthy service instances"""
        services = self.discover_services(service_type=service_type)
        return [s for s in services if s.status == ServiceStatus.HEALTHY]

class LoadBalancer:
    """Intelligent load balancer for ML services"""
    
    def __init__(self, routing_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN):
        self.routing_strategy = routing_strategy
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
        self.creator_affinities: Dict[str, str] = {}  # creator_id -> preferred_service_id
        self.model_affinities: Dict[str, str] = {}    # model_id -> preferred_service_id
    
    def select_service(
        self,
        services: List[ServiceInstance],
        request_context: Dict[str, Any] = None
    ) -> Optional[ServiceInstance]:
        """Select best service instance based on routing strategy"""
        if not services:
            return None
        
        healthy_services = [s for s in services if s.status == ServiceStatus.HEALTHY]
        if not healthy_services:
            # Fall back to degraded services if no healthy ones
            healthy_services = [s for s in services if s.status == ServiceStatus.DEGRADED]
            if not healthy_services:
                return None
        
        request_context = request_context or {}
        
        if self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(healthy_services)
        
        elif self.routing_strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(healthy_services)
        
        elif self.routing_strategy == RoutingStrategy.WEIGHTED_RANDOM:
            return self._weighted_random_selection(healthy_services)
        
        elif self.routing_strategy == RoutingStrategy.CREATOR_AFFINITY:
            return self._creator_affinity_selection(healthy_services, request_context)
        
        elif self.routing_strategy == RoutingStrategy.MODEL_AFFINITY:
            return self._model_affinity_selection(healthy_services, request_context)
        
        elif self.routing_strategy == RoutingStrategy.PERFORMANCE_BASED:
            return self._performance_based_selection(healthy_services)
        
        else:
            return random.choice(healthy_services)
    
    def _round_robin_selection(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin service selection"""
        service_group = services[0].service_name
        counter = self.round_robin_counters[service_group]
        selected = services[counter % len(services)]
        self.round_robin_counters[service_group] = counter + 1
        return selected
    
    def _least_connections_selection(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Select service with least active connections"""
        return min(services, key=lambda s: s.active_connections)
    
    def _weighted_random_selection(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Weighted random selection based on health scores"""
        weights = [s.health_score for s in services]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(services)
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for service, weight in zip(services, weights):
            cumulative += weight
            if r <= cumulative:
                return service
        
        return services[-1]  # Fallback
    
    def _creator_affinity_selection(
        self,
        services: List[ServiceInstance],
        request_context: Dict[str, Any]
    ) -> ServiceInstance:
        """Select service based on creator affinity"""
        creator_id = request_context.get('creator_id')
        if creator_id and creator_id in self.creator_affinities:
            preferred_service_id = self.creator_affinities[creator_id]
            for service in services:
                if service.service_id == preferred_service_id:
                    return service
        
        # No affinity found, establish new one
        selected = self._performance_based_selection(services)
        if creator_id:
            self.creator_affinities[creator_id] = selected.service_id
        
        return selected
    
    def _model_affinity_selection(
        self,
        services: List[ServiceInstance],
        request_context: Dict[str, Any]
    ) -> ServiceInstance:
        """Select service based on model affinity"""
        model_id = request_context.get('model_id')
        if model_id and model_id in self.model_affinities:
            preferred_service_id = self.model_affinities[model_id]
            for service in services:
                if service.service_id == preferred_service_id:
                    return service
        
        # No affinity found, establish new one
        selected = self._performance_based_selection(services)
        if model_id:
            self.model_affinities[model_id] = selected.service_id
        
        return selected
    
    def _performance_based_selection(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Select service based on performance metrics"""
        # Score based on multiple factors
        def performance_score(service: ServiceInstance) -> float:
            score = service.health_score
            
            # Lower response time is better
            response_factor = 1.0 / (1.0 + service.response_time_ms / 1000.0)
            score *= response_factor
            
            # Lower resource usage is better
            resource_factor = 1.0 - (service.cpu_usage * 0.5 + service.memory_usage * 0.3)
            score *= max(0.1, resource_factor)
            
            return score
        
        return max(services, key=performance_score)

class MicroserviceMeshIntegration:
    """
    🌐 Enterprise Microservice Mesh Integration
    
    Service mesh coordination for ML workloads with intelligent routing,
    load balancing, circuit breaking, and service discovery.
    """
    
    def __init__(self, config: MeshConfig):
        self.config = config
        self.service_registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.routes: Dict[str, ServiceRoute] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.request_history: deque = deque(maxlen=1000)
        self.metrics: Dict[str, Any] = defaultdict(int)
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Network topology graph
        self.topology_graph = nx.DiGraph()
        
        # Rate limiters
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Start background tasks
        asyncio.create_task(self._service_discovery_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metrics_collection_loop())
        
        logger.info(f"🌐 Microservice Mesh '{config.mesh_name}' initialized")
    
    async def register_service(
        self,
        service_name: str,
        service_type: ServiceType,
        host: str,
        port: int,
        version: str = "1.0.0",
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Register a new service with the mesh
        
        Args:
            service_name: Human-readable service name
            service_type: Type of service
            host: Service host/IP
            port: Service port
            version: Service version
            tags: Service tags for filtering
            metadata: Additional service metadata
            
        Returns:
            Service ID
        """
        service_id = f"{service_name}-{hashlib.sha256(f'{host}:{port}'.encode()).hexdigest()[:8]}"
        
        service = ServiceInstance(
            service_id=service_id,
            service_name=service_name,
            service_type=service_type,
            host=host,
            port=port,
            version=version,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Register with service registry
        self.service_registry.register_service(service)
        
        # Add to topology graph
        self.topology_graph.add_node(
            service_id,
            name=service_name,
            type=service_type.value,
            host=host,
            port=port
        )
        
        # Create circuit breaker for service
        self.circuit_breakers[service_id] = CircuitBreaker(
            failure_threshold=self.config.circuit_breaker_threshold,
            timeout_seconds=self.config.circuit_breaker_timeout_seconds
        )
        
        logger.info(f"✅ Service registered: {service_name} at {host}:{port}")
        return service_id
    
    async def create_route(
        self,
        source_pattern: str,
        target_services: List[str],
        routing_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN,
        conditions: Dict[str, Any] = None
    ) -> str:
        """
        Create a service route configuration
        
        Args:
            source_pattern: Source URL pattern to match
            target_services: List of target service names
            routing_strategy: Strategy for routing
            conditions: Additional routing conditions
            
        Returns:
            Route ID
        """
        route_id = f"route-{hashlib.sha256(source_pattern.encode()).hexdigest()[:8]}"
        
        route = ServiceRoute(
            route_id=route_id,
            source_pattern=source_pattern,
            target_services=target_services,
            routing_strategy=routing_strategy,
            conditions=conditions or {}
        )
        
        self.routes[route_id] = route
        
        # Update topology graph with routing edges
        for target_service in target_services:
            target_instances = self.service_registry.discover_services(service_name=target_service)
            for instance in target_instances:
                self.topology_graph.add_edge(
                    "gateway",
                    instance.service_id,
                    route_pattern=source_pattern,
                    strategy=routing_strategy.value
                )
        
        logger.info(f"🗺️ Route created: {source_pattern} -> {target_services}")
        return route_id
    
    async def route_request(
        self,
        request_path: str,
        request_context: Dict[str, Any] = None
    ) -> Tuple[Optional[ServiceInstance], Optional[str]]:
        """
        Route a request to appropriate service
        
        Args:
            request_path: Request path to route
            request_context: Request context for routing decisions
            
        Returns:
            Tuple of (selected_service, route_id) or (None, None) if no route found
        """
        # Find matching route
        matching_route = None
        for route in self.routes.values():
            if self._matches_pattern(request_path, route.source_pattern):
                matching_route = route
                break
        
        if not matching_route:
            logger.warning(f"⚠️ No route found for path: {request_path}")
            return None, None
        
        # Check rate limiting
        if self.config.enable_rate_limiting:
            if not await self._check_rate_limit(matching_route, request_context):
                logger.warning(f"⚠️ Rate limit exceeded for route: {matching_route.route_id}")
                return None, matching_route.route_id
        
        # Discover target services
        target_services = []
        for service_name in matching_route.target_services:
            services = self.service_registry.get_healthy_services()
            services = [s for s in services if s.service_name == service_name]
            target_services.extend(services)
        
        if not target_services:
            logger.warning(f"⚠️ No healthy services found for route: {matching_route.route_id}")
            return None, matching_route.route_id
        
        # Select service using load balancer
        self.load_balancer.routing_strategy = matching_route.routing_strategy
        selected_service = self.load_balancer.select_service(target_services, request_context)
        
        if selected_service:
            # Record request for metrics
            self._record_request(matching_route.route_id, selected_service.service_id, request_context)
        
        return selected_service, matching_route.route_id
    
    async def execute_request(
        self,
        service: ServiceInstance,
        method: str,
        path: str,
        data: Any = None,
        headers: Dict[str, str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute request to service with circuit breaker protection
        
        Args:
            service: Target service instance
            method: HTTP method
            path: Request path
            data: Request data
            headers: Request headers
            timeout: Request timeout
            
        Returns:
            Response data
        """
        circuit_breaker = self.circuit_breakers.get(service.service_id)
        timeout = timeout or 5000  # Default 5 seconds
        
        async def make_request():
            url = f"{service.endpoint}{path}"
            headers = headers or {}
            
            start_time = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout/1000)
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        # Update service metrics
                        service.response_time_ms = response_time
                        service.request_count += 1
                        
                        if response.status >= 400:
                            service.error_count += 1
                            raise Exception(f"HTTP {response.status}: {await response.text()}")
                        
                        result = await response.json()
                        
                        # Record successful request
                        self.metrics['successful_requests'] += 1
                        self.metrics['total_response_time'] += response_time
                        
                        return {
                            'status_code': response.status,
                            'data': result,
                            'response_time_ms': response_time,
                            'service_id': service.service_id
                        }
            
            except Exception as e:
                service.error_count += 1
                self.metrics['failed_requests'] += 1
                logger.error(f"❌ Request failed to {service.service_id}: {str(e)}")
                raise
        
        # Execute with circuit breaker if enabled
        if self.config.enable_circuit_breaker and circuit_breaker:
            return await asyncio.get_event_loop().run_in_executor(
                self.executor,
                circuit_breaker.call,
                lambda: asyncio.run(make_request())
            )
        else:
            return await make_request()
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches routing pattern"""
        # Simple pattern matching (in production, use more sophisticated matching)
        if pattern == "/*":
            return True
        
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return path.startswith(prefix)
        
        return path == pattern
    
    async def _check_rate_limit(
        self,
        route: ServiceRoute,
        request_context: Dict[str, Any]
    ) -> bool:
        """Check if request exceeds rate limit"""
        # Use IP address or user ID for rate limiting
        identifier = request_context.get('client_ip', 'unknown')
        current_time = time.time()
        
        rate_limiter = self.rate_limiters[f"{route.route_id}:{identifier}"]
        
        # Clean old requests (older than 1 minute)
        while rate_limiter and current_time - rate_limiter[0] > 60:
            rate_limiter.popleft()
        
        # Check if limit exceeded
        if len(rate_limiter) >= route.rate_limit_per_minute:
            return False
        
        # Add current request
        rate_limiter.append(current_time)
        return True
    
    def _record_request(
        self,
        route_id: str,
        service_id: str,
        request_context: Dict[str, Any]
    ):
        """Record request for analytics"""
        request_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'route_id': route_id,
            'service_id': service_id,
            'creator_id': request_context.get('creator_id'),
            'model_id': request_context.get('model_id'),
            'client_ip': request_context.get('client_ip'),
            'user_agent': request_context.get('user_agent')
        }
        
        self.request_history.append(request_record)
        self.metrics['total_requests'] += 1
    
    async def _service_discovery_loop(self):
        """Background service discovery and health updates"""
        while True:
            try:
                await asyncio.sleep(self.config.discovery_interval_seconds)
                
                # Update service topology graph
                await self._update_topology_graph()
                
                # Clean up dead services
                await self._cleanup_dead_services()
                
            except Exception as e:
                logger.error(f"❌ Service discovery error: {str(e)}")
    
    async def _health_check_loop(self):
        """Background health checking for all services"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
                services = list(self.service_registry.services.values())
                
                # Check health of all services in parallel
                health_tasks = [
                    self._check_service_health(service)
                    for service in services
                ]
                
                await asyncio.gather(*health_tasks, return_exceptions=True)
                
            except Exception as e:
                logger.error(f"❌ Health check error: {str(e)}")
    
    async def _check_service_health(self, service: ServiceInstance):
        """Check health of individual service"""
        try:
            # Perform health check request
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service.endpoint}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        service.status = ServiceStatus.HEALTHY
                        health_data = await response.json()
                        
                        # Update metrics from health endpoint
                        service.cpu_usage = health_data.get('cpu_usage', 0.0)
                        service.memory_usage = health_data.get('memory_usage', 0.0)
                        service.active_connections = health_data.get('active_connections', 0)
                    
                    elif response.status == 503:
                        service.status = ServiceStatus.DEGRADED
                    else:
                        service.status = ServiceStatus.UNHEALTHY
                    
                    service.response_time_ms = response_time
                    service.last_health_check = datetime.utcnow()
        
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            service.last_health_check = datetime.utcnow()
            logger.debug(f"⚠️ Health check failed for {service.service_id}: {str(e)}")
    
    async def _metrics_collection_loop(self):
        """Background metrics collection"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect metrics every minute
                
                # Calculate aggregate metrics
                services = list(self.service_registry.services.values())
                
                self.metrics['total_services'] = len(services)
                self.metrics['healthy_services'] = len([
                    s for s in services if s.status == ServiceStatus.HEALTHY
                ])
                self.metrics['degraded_services'] = len([
                    s for s in services if s.status == ServiceStatus.DEGRADED
                ])
                self.metrics['unhealthy_services'] = len([
                    s for s in services if s.status == ServiceStatus.UNHEALTHY
                ])
                
                # Calculate average response time
                if self.metrics['successful_requests'] > 0:
                    self.metrics['avg_response_time_ms'] = (
                        self.metrics['total_response_time'] / self.metrics['successful_requests']
                    )
                
                # Calculate error rate
                total_requests = self.metrics['successful_requests'] + self.metrics['failed_requests']
                if total_requests > 0:
                    self.metrics['error_rate'] = (
                        self.metrics['failed_requests'] / total_requests
                    )
                
                logger.debug(f"📊 Mesh metrics updated: {self.metrics}")
                
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {str(e)}")
    
    async def _update_topology_graph(self):
        """Update service topology graph"""
        # Add service nodes
        for service in self.service_registry.services.values():
            self.topology_graph.add_node(
                service.service_id,
                name=service.service_name,
                type=service.service_type.value,
                status=service.status.value,
                health_score=service.health_score
            )
        
        # Update routing edges based on request history
        for request in list(self.request_history)[-100:]:  # Last 100 requests
            if request.get('route_id') and request.get('service_id'):
                self.topology_graph.add_edge(
                    "gateway",
                    request['service_id'],
                    route_id=request['route_id'],
                    last_used=request['timestamp']
                )
    
    async def _cleanup_dead_services(self):
        """Remove services that haven't been seen for a while"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        dead_services = []
        for service in self.service_registry.services.values():
            if service.last_health_check < cutoff_time:
                dead_services.append(service.service_id)
        
        for service_id in dead_services:
            self.service_registry.deregister_service(service_id)
            
            # Remove from topology graph
            if self.topology_graph.has_node(service_id):
                self.topology_graph.remove_node(service_id)
            
            # Remove circuit breaker
            if service_id in self.circuit_breakers:
                del self.circuit_breakers[service_id]
        
        if dead_services:
            logger.info(f"🧹 Cleaned up {len(dead_services)} dead services")
    
    def get_mesh_analytics(self) -> Dict[str, Any]:
        """Get comprehensive mesh analytics"""
        services = list(self.service_registry.services.values())
        
        # Service distribution by type
        service_distribution = defaultdict(int)
        for service in services:
            service_distribution[service.service_type.value] += 1
        
        # Route analytics
        route_analytics = {}
        for route_id, route in self.routes.items():
            route_requests = [
                r for r in self.request_history
                if r.get('route_id') == route_id
            ]
            route_analytics[route_id] = {
                'total_requests': len(route_requests),
                'target_services': route.target_services,
                'routing_strategy': route.routing_strategy.value
            }
        
        return {
            'mesh_name': self.config.mesh_name,
            'timestamp': datetime.utcnow().isoformat(),
            'service_stats': {
                'total_services': len(services),
                'healthy_services': len([s for s in services if s.status == ServiceStatus.HEALTHY]),
                'service_distribution': dict(service_distribution)
            },
            'request_stats': {
                'total_requests': self.metrics.get('total_requests', 0),
                'successful_requests': self.metrics.get('successful_requests', 0),
                'failed_requests': self.metrics.get('failed_requests', 0),
                'error_rate': self.metrics.get('error_rate', 0.0),
                'avg_response_time_ms': self.metrics.get('avg_response_time_ms', 0.0)
            },
            'route_analytics': route_analytics,
            'topology': {
                'nodes': self.topology_graph.number_of_nodes(),
                'edges': self.topology_graph.number_of_edges()
            }
        }
    
    def export_topology(self, output_path: str) -> str:
        """Export service topology graph"""
        import json
        from networkx.readwrite import json_graph
        
        topology_data = json_graph.node_link_data(self.topology_graph)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(topology_data, f, indent=2)
        
        logger.info(f"📊 Service topology exported to {output_path}")
        return str(output_file)
    
    def get_mesh_summary(self) -> Dict[str, Any]:
        """Get service mesh summary"""
        return {
            "microservice_mesh": "v1.0",
            "mesh_name": self.config.mesh_name,
            "configuration": {
                "discovery_interval_seconds": self.config.discovery_interval_seconds,
                "health_check_interval_seconds": self.config.health_check_interval_seconds,
                "circuit_breaker_enabled": self.config.enable_circuit_breaker,
                "load_balancing_enabled": self.config.enable_load_balancing
            },
            "current_state": {
                "registered_services": len(self.service_registry.services),
                "active_routes": len(self.routes),
                "circuit_breakers": len(self.circuit_breakers),
                "topology_nodes": self.topology_graph.number_of_nodes(),
                "topology_edges": self.topology_graph.number_of_edges()
            },
            "performance": {
                "total_requests": self.metrics.get('total_requests', 0),
                "error_rate": self.metrics.get('error_rate', 0.0),
                "avg_response_time_ms": self.metrics.get('avg_response_time_ms', 0.0)
            }
        }

async def main():
    """Example usage of Microservice Mesh Integration"""
    # Initialize mesh
    config = MeshConfig(
        mesh_name="ml-production-mesh",
        enable_circuit_breaker=True,
        enable_load_balancing=True
    )
    
    mesh = MicroserviceMeshIntegration(config)
    
    # Register ML services
    inference_service_id = await mesh.register_service(
        service_name="ml-inference",
        service_type=ServiceType.INFERENCE_ENGINE,
        host="10.0.1.100",
        port=8000,
        tags={"model_type": "audio", "creator_type": "musician"}
    )
    
    feature_store_id = await mesh.register_service(
        service_name="feature-store",
        service_type=ServiceType.FEATURE_STORE,
        host="10.0.1.101",
        port=8001,
        tags={"cache_enabled": "true"}
    )
    
    # Create routing rules
    await mesh.create_route(
        source_pattern="/api/inference/*",
        target_services=["ml-inference"],
        routing_strategy=RoutingStrategy.CREATOR_AFFINITY
    )
    
    await mesh.create_route(
        source_pattern="/api/features/*",
        target_services=["feature-store"],
        routing_strategy=RoutingStrategy.PERFORMANCE_BASED
    )
    
    # Simulate request routing
    request_context = {
        "creator_id": "musician_123",
        "model_id": "audio_classifier_v2",
        "client_ip": "192.168.1.100"
    }
    
    service, route_id = await mesh.route_request(
        "/api/inference/predict",
        request_context
    )
    
    if service:
        print(f"🎯 Routed to service: {service.service_name} ({service.service_id})")
        
        # Execute request
        response = await mesh.execute_request(
            service=service,
            method="POST",
            path="/predict",
            data={"audio_features": [1, 2, 3, 4, 5]},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response: {response}")
    
    # Get mesh analytics
    analytics = mesh.get_mesh_analytics()
    print(f"📊 Mesh Analytics: {json.dumps(analytics, indent=2)}")
    
    # Export topology
    topology_file = mesh.export_topology("/tmp/mesh_topology.json")
    print(f"🗺️ Topology exported to: {topology_file}")
    
    # Get summary
    summary = mesh.get_mesh_summary()
    print(f"🌐 Mesh Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())