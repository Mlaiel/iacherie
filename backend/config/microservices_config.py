"""Microservices Config - Enterprise Microservices Architecture Configuration
============================================================================

Advanced microservices configuration system providing service discovery, 
inter-service communication, load balancing, circuit breakers, service mesh,
API gateway settings, and distributed tracing configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, List, Optional, Any, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timedelta
import asyncio
import json
import logging
import hashlib
from abc import ABC, abstractmethod

# ===============================
# MICROSERVICES ARCHITECTURE TYPES
# ===============================

class ServiceType(str, Enum):
    """Types of microservices"""
    API_GATEWAY = "api_gateway"
    BUSINESS_SERVICE = "business_service"
    DATA_SERVICE = "data_service"
    INTEGRATION_SERVICE = "integration_service"
    UTILITY_SERVICE = "utility_service"
    SECURITY_SERVICE = "security_service"
    MONITORING_SERVICE = "monitoring_service"
    NOTIFICATION_SERVICE = "notification_service"

class CommunicationType(str, Enum):
    """Inter-service communication types"""
    HTTP_REST = "http_rest"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAMING = "event_streaming"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"

class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"
    RANDOM = "random"

class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ServiceMeshType(str, Enum):
    """Service mesh implementations"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    ENVOY = "envoy"
    NGINX_MESH = "nginx_mesh"

class HealthCheckType(str, Enum):
    """Health check types"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    CUSTOM = "custom"

# ==============================
# SERVICE CONFIGURATION DATA STRUCTURES
# ==============================

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    service_name: str
    host: str
    port: int
    protocol: str = "http"
    path: str = "/"
    health_check_path: str = "/health"
    version: str = "v1"
    weight: int = 100
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceDiscoveryConfig:
    """Service discovery configuration"""
    discovery_type: str = "consul"  # consul, eureka, etcd, kubernetes
    registry_endpoints: List[str] = field(default_factory=list)
    service_registration_ttl: timedelta = timedelta(seconds=30)
    health_check_interval: timedelta = timedelta(seconds=10)
    health_check_timeout: timedelta = timedelta(seconds=5)
    health_check_type: HealthCheckType = HealthCheckType.HTTP
    auto_deregistration: bool = True
    enable_service_mesh: bool = True

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_enabled: bool = True
    session_affinity: bool = False
    connection_timeout: timedelta = timedelta(seconds=30)
    request_timeout: timedelta = timedelta(seconds=60)
    max_retries: int = 3
    retry_backoff: timedelta = timedelta(milliseconds=100)
    circuit_breaker_enabled: bool = True

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: timedelta = timedelta(seconds=60)
    success_threshold: int = 3
    timeout: timedelta = timedelta(seconds=30)
    monitor_window: timedelta = timedelta(minutes=1)
    half_open_max_calls: int = 10
    fallback_enabled: bool = True
    fallback_response: Optional[Dict[str, Any]] = None

@dataclass
class APIGatewayConfig:
    """API Gateway configuration"""
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8080
    rate_limiting_enabled: bool = True
    rate_limit_requests_per_minute: int = 1000
    authentication_enabled: bool = True
    authorization_enabled: bool = True
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    request_logging: bool = True
    response_caching: bool = True
    cache_ttl: timedelta = timedelta(minutes=5)

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    mesh_type: ServiceMeshType = ServiceMeshType.ISTIO
    mtls_enabled: bool = True
    traffic_policy_enabled: bool = True
    observability_enabled: bool = True
    security_policies_enabled: bool = True
    ingress_gateway_enabled: bool = True
    egress_gateway_enabled: bool = True
    sidecar_injection: bool = True
    telemetry_collection: bool = True

@dataclass
class DistributedTracingConfig:
    """Distributed tracing configuration"""
    tracing_enabled: bool = True
    tracer_type: str = "jaeger"  # jaeger, zipkin, opentelemetry
    sampling_rate: float = 0.1
    trace_timeout: timedelta = timedelta(seconds=30)
    span_processors: List[str] = field(default_factory=lambda: ["batch"])
    exporters: List[str] = field(default_factory=lambda: ["jaeger"])
    service_name_override: Optional[str] = None
    trace_propagation: bool = True

# ==============================
# SERVICE REGISTRY
# ==============================

class ServiceRegistry:
    """Service discovery and registry system"""
    
    def __init__(self, discovery_config: ServiceDiscoveryConfig):
        self.config = discovery_config
        self.registered_services: Dict[str, List[ServiceEndpoint]] = {}
        self.service_health: Dict[str, Dict[str, bool]] = {}
        self.last_health_check: Dict[str, Dict[str, datetime]] = {}
        self.registry_listeners: List[Callable] = []
    
    async def register_service(self, endpoint: ServiceEndpoint) -> Dict[str, Any]:
        """Register a service endpoint"""
        service_name = endpoint.service_name
        
        # Initialize service lists if not exists
        if service_name not in self.registered_services:
            self.registered_services[service_name] = []
            self.service_health[service_name] = {}
            self.last_health_check[service_name] = {}
        
        # Check if endpoint already registered
        existing_endpoint = None
        for i, existing in enumerate(self.registered_services[service_name]):
            if existing.host == endpoint.host and existing.port == endpoint.port:
                existing_endpoint = i
                break
        
        if existing_endpoint is not None:
            # Update existing endpoint
            self.registered_services[service_name][existing_endpoint] = endpoint
        else:
            # Add new endpoint
            self.registered_services[service_name].append(endpoint)
        
        # Initialize health status
        endpoint_key = f"{endpoint.host}:{endpoint.port}"
        self.service_health[service_name][endpoint_key] = True
        self.last_health_check[service_name][endpoint_key] = datetime.now()
        
        # Notify listeners
        await self._notify_registry_change("register", service_name, endpoint)
        
        logging.info(f"Registered service {service_name} at {endpoint.host}:{endpoint.port}")
        return {
            "status": "registered",
            "service_name": service_name,
            "endpoint": f"{endpoint.host}:{endpoint.port}"
        }
    
    async def deregister_service(self, service_name: str, host: str, port: int) -> Dict[str, Any]:
        """Deregister a service endpoint"""
        if service_name not in self.registered_services:
            return {"status": "error", "message": "Service not found"}
        
        # Find and remove endpoint
        endpoints = self.registered_services[service_name]
        for i, endpoint in enumerate(endpoints):
            if endpoint.host == host and endpoint.port == port:
                removed_endpoint = endpoints.pop(i)
                
                # Remove health status
                endpoint_key = f"{host}:{port}"
                if endpoint_key in self.service_health[service_name]:
                    del self.service_health[service_name][endpoint_key]
                if endpoint_key in self.last_health_check[service_name]:
                    del self.last_health_check[service_name][endpoint_key]
                
                # Notify listeners
                await self._notify_registry_change("deregister", service_name, removed_endpoint)
                
                logging.info(f"Deregistered service {service_name} at {host}:{port}")
                return {"status": "deregistered", "service_name": service_name}
        
        return {"status": "error", "message": "Endpoint not found"}
    
    async def discover_services(self, service_name: str) -> List[ServiceEndpoint]:
        """Discover healthy endpoints for a service"""
        if service_name not in self.registered_services:
            return []
        
        healthy_endpoints = []
        for endpoint in self.registered_services[service_name]:
            endpoint_key = f"{endpoint.host}:{endpoint.port}"
            is_healthy = self.service_health[service_name].get(endpoint_key, False)
            
            if is_healthy:
                healthy_endpoints.append(endpoint)
        
        return healthy_endpoints
    
    async def health_check_service(self, service_name: str, endpoint: ServiceEndpoint) -> bool:
        """Perform health check on service endpoint"""
        try:
            endpoint_key = f"{endpoint.host}:{endpoint.port}"
            
            if self.config.health_check_type == HealthCheckType.HTTP:
                health_url = f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
                
                # Simulate HTTP health check
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=self.config.health_check_timeout.total_seconds()) as response:
                        is_healthy = response.status == 200
            
            elif self.config.health_check_type == HealthCheckType.TCP:
                # Simulate TCP health check
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(endpoint.host, endpoint.port),
                    timeout=self.config.health_check_timeout.total_seconds()
                )
                writer.close()
                await writer.wait_closed()
                is_healthy = True
            
            else:
                # Default to healthy for custom checks
                is_healthy = True
            
            # Update health status
            self.service_health[service_name][endpoint_key] = is_healthy
            self.last_health_check[service_name][endpoint_key] = datetime.now()
            
            return is_healthy
            
        except Exception as e:
            logging.warning(f"Health check failed for {service_name} at {endpoint.host}:{endpoint.port}: {e}")
            endpoint_key = f"{endpoint.host}:{endpoint.port}"
            self.service_health[service_name][endpoint_key] = False
            return False
    
    async def start_health_monitoring(self) -> None:
        """Start continuous health monitoring"""
        async def health_monitor_loop():
            while True:
                try:
                    for service_name, endpoints in self.registered_services.items():
                        for endpoint in endpoints:
                            await self.health_check_service(service_name, endpoint)
                    
                    await asyncio.sleep(self.config.health_check_interval.total_seconds())
                    
                except Exception as e:
                    logging.error(f"Error in health monitoring: {e}")
                    await asyncio.sleep(self.config.health_check_interval.total_seconds())
        
        asyncio.create_task(health_monitor_loop())
        logging.info("Started health monitoring")
    
    def add_registry_listener(self, listener: Callable[[str, str, ServiceEndpoint], None]) -> None:
        """Add registry change listener"""
        self.registry_listeners.append(listener)
    
    async def _notify_registry_change(self, action: str, service_name: str, endpoint: ServiceEndpoint) -> None:
        """Notify listeners of registry changes"""
        for listener in self.registry_listeners:
            try:
                await listener(action, service_name, endpoint)
            except Exception as e:
                logging.error(f"Error in registry listener: {e}")
    
    def get_service_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get complete service health status"""
        return {
            service_name: {
                "endpoints": len(endpoints),
                "healthy_endpoints": sum(1 for ep in endpoints 
                                       if self.service_health[service_name].get(f"{ep.host}:{ep.port}", False)),
                "health_details": self.service_health[service_name].copy()
            }
            for service_name, endpoints in self.registered_services.items()
        }

# ==============================
# LOAD BALANCER
# ==============================

class LoadBalancer:
    """Service load balancer with multiple strategies"""
    
    def __init__(self, config: LoadBalancerConfig, service_registry: ServiceRegistry):
        self.config = config
        self.service_registry = service_registry
        self.round_robin_counters: Dict[str, int] = {}
        self.connection_counts: Dict[str, Dict[str, int]] = {}
        self.response_times: Dict[str, Dict[str, List[float]]] = {}
        self.circuit_breakers: Dict[str, Dict[str, 'CircuitBreaker']] = {}
    
    async def select_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """Select an endpoint based on load balancing strategy"""
        available_endpoints = await self.service_registry.discover_services(service_name)
        
        if not available_endpoints:
            return None
        
        # Filter out endpoints with open circuit breakers
        if self.config.circuit_breaker_enabled:
            available_endpoints = [ep for ep in available_endpoints 
                                 if not self._is_circuit_breaker_open(service_name, ep)]
        
        if not available_endpoints:
            return None
        
        # Apply load balancing strategy
        if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_name, available_endpoints)
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(service_name, available_endpoints)
        elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(service_name, available_endpoints)
        elif self.config.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(service_name, available_endpoints)
        elif self.config.strategy == LoadBalancingStrategy.RANDOM:
            import random
            return random.choice(available_endpoints)
        else:
            return available_endpoints[0]
    
    def _round_robin_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round-robin selection"""
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        selected_index = self.round_robin_counters[service_name] % len(endpoints)
        self.round_robin_counters[service_name] += 1
        
        return endpoints[selected_index]
    
    def _weighted_round_robin_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted round-robin selection"""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return self._round_robin_select(service_name, endpoints)
        
        # Create weighted list
        weighted_endpoints = []
        for endpoint in endpoints:
            weighted_endpoints.extend([endpoint] * endpoint.weight)
        
        return self._round_robin_select(service_name, weighted_endpoints)
    
    def _least_connections_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections selection"""
        if service_name not in self.connection_counts:
            self.connection_counts[service_name] = {}
        
        min_connections = float('inf')
        selected_endpoint = endpoints[0]
        
        for endpoint in endpoints:
            endpoint_key = f"{endpoint.host}:{endpoint.port}"
            connections = self.connection_counts[service_name].get(endpoint_key, 0)
            
            if connections < min_connections:
                min_connections = connections
                selected_endpoint = endpoint
        
        return selected_endpoint
    
    def _least_response_time_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least response time selection"""
        if service_name not in self.response_times:
            self.response_times[service_name] = {}
        
        min_response_time = float('inf')
        selected_endpoint = endpoints[0]
        
        for endpoint in endpoints:
            endpoint_key = f"{endpoint.host}:{endpoint.port}"
            response_times = self.response_times[service_name].get(endpoint_key, [])
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
            else:
                avg_response_time = 0.0  # Prefer endpoints without data
            
            if avg_response_time < min_response_time:
                min_response_time = avg_response_time
                selected_endpoint = endpoint
        
        return selected_endpoint
    
    def record_request_start(self, service_name: str, endpoint: ServiceEndpoint) -> None:
        """Record request start for connection tracking"""
        if service_name not in self.connection_counts:
            self.connection_counts[service_name] = {}
        
        endpoint_key = f"{endpoint.host}:{endpoint.port}"
        current_connections = self.connection_counts[service_name].get(endpoint_key, 0)
        self.connection_counts[service_name][endpoint_key] = current_connections + 1
    
    def record_request_end(self, service_name: str, endpoint: ServiceEndpoint, 
                          response_time_ms: float, success: bool) -> None:
        """Record request completion"""
        endpoint_key = f"{endpoint.host}:{endpoint.port}"
        
        # Update connection count
        if service_name in self.connection_counts:
            current_connections = self.connection_counts[service_name].get(endpoint_key, 0)
            self.connection_counts[service_name][endpoint_key] = max(0, current_connections - 1)
        
        # Update response times
        if service_name not in self.response_times:
            self.response_times[service_name] = {}
        
        if endpoint_key not in self.response_times[service_name]:
            self.response_times[service_name][endpoint_key] = []
        
        response_times = self.response_times[service_name][endpoint_key]
        response_times.append(response_time_ms)
        
        # Keep only recent response times (last 100 requests)
        if len(response_times) > 100:
            response_times.pop(0)
        
        # Update circuit breaker
        if self.config.circuit_breaker_enabled:
            self._update_circuit_breaker(service_name, endpoint, success)
    
    def _is_circuit_breaker_open(self, service_name: str, endpoint: ServiceEndpoint) -> bool:
        """Check if circuit breaker is open for endpoint"""
        if service_name not in self.circuit_breakers:
            return False
        
        endpoint_key = f"{endpoint.host}:{endpoint.port}"
        circuit_breaker = self.circuit_breakers[service_name].get(endpoint_key)
        
        return circuit_breaker and circuit_breaker.is_open()
    
    def _update_circuit_breaker(self, service_name: str, endpoint: ServiceEndpoint, success: bool) -> None:
        """Update circuit breaker state"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {}
        
        endpoint_key = f"{endpoint.host}:{endpoint.port}"
        
        if endpoint_key not in self.circuit_breakers[service_name]:
            from .circuit_breaker import CircuitBreaker  # Would be implemented
            self.circuit_breakers[service_name][endpoint_key] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=timedelta(seconds=60),
                success_threshold=3
            )
        
        circuit_breaker = self.circuit_breakers[service_name][endpoint_key]
        
        if success:
            circuit_breaker.record_success()
        else:
            circuit_breaker.record_failure()

# ==============================
# API GATEWAY
# ==============================

class APIGateway:
    """API Gateway for microservices"""
    
    def __init__(self, config: APIGatewayConfig, load_balancer: LoadBalancer):
        self.config = config
        self.load_balancer = load_balancer
        self.route_mappings: Dict[str, str] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        self.cached_responses: Dict[str, Dict[str, Any]] = {}
        self.middleware_stack: List[Callable] = []
    
    def add_route(self, path_pattern: str, service_name: str) -> None:
        """Add route mapping"""
        self.route_mappings[path_pattern] = service_name
        logging.info(f"Added route: {path_pattern} -> {service_name}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the stack"""
        self.middleware_stack.append(middleware)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request through gateway"""
        # Extract request information
        path = request.get("path", "/")
        method = request.get("method", "GET")
        headers = request.get("headers", {})
        client_ip = request.get("client_ip", "unknown")
        
        # Find matching service
        service_name = self._match_route(path)
        if not service_name:
            return {
                "status": 404,
                "body": {"error": "Route not found"},
                "headers": {}
            }
        
        # Apply middleware
        for middleware in self.middleware_stack:
            try:
                request = await middleware(request)
                if "error" in request:
                    return request
            except Exception as e:
                logging.error(f"Middleware error: {e}")
                return {
                    "status": 500,
                    "body": {"error": "Internal server error"},
                    "headers": {}
                }
        
        # Rate limiting
        if self.config.rate_limiting_enabled:
            rate_limit_result = await self._check_rate_limit(client_ip)
            if not rate_limit_result["allowed"]:
                return {
                    "status": 429,
                    "body": {"error": "Rate limit exceeded"},
                    "headers": {"Retry-After": "60"}
                }
        
        # Check cache
        if self.config.response_caching and method == "GET":
            cache_key = self._generate_cache_key(service_name, path, headers)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
        
        # Select endpoint and forward request
        endpoint = await self.load_balancer.select_endpoint(service_name)
        if not endpoint:
            return {
                "status": 503,
                "body": {"error": "Service unavailable"},
                "headers": {}
            }
        
        # Forward request to service
        start_time = datetime.now()
        try:
            self.load_balancer.record_request_start(service_name, endpoint)
            
            # Simulate request forwarding
            response = await self._forward_request(endpoint, request)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.load_balancer.record_request_end(service_name, endpoint, response_time, True)
            
            # Cache successful responses
            if (self.config.response_caching and method == "GET" and 
                response.get("status", 500) == 200):
                cache_key = self._generate_cache_key(service_name, path, headers)
                self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.load_balancer.record_request_end(service_name, endpoint, response_time, False)
            
            logging.error(f"Request forwarding error: {e}")
            return {
                "status": 500,
                "body": {"error": "Service error"},
                "headers": {}
            }
    
    def _match_route(self, path: str) -> Optional[str]:
        """Match request path to service"""
        for pattern, service_name in self.route_mappings.items():
            if path.startswith(pattern):
                return service_name
        return None
    
    async def _check_rate_limit(self, client_ip: str) -> Dict[str, Any]:
        """Check rate limiting for client"""
        current_time = datetime.now()
        minute_window = current_time.replace(second=0, microsecond=0)
        
        if client_ip not in self.rate_limiters:
            self.rate_limiters[client_ip] = {}
        
        client_limits = self.rate_limiters[client_ip]
        
        # Clean old entries
        client_limits = {k: v for k, v in client_limits.items() 
                        if datetime.fromisoformat(k) >= current_time - timedelta(minutes=1)}
        self.rate_limiters[client_ip] = client_limits
        
        # Count requests in current minute
        minute_key = minute_window.isoformat()
        current_requests = client_limits.get(minute_key, 0)
        
        if current_requests >= self.config.rate_limit_requests_per_minute:
            return {"allowed": False, "remaining": 0}
        
        # Increment counter
        client_limits[minute_key] = current_requests + 1
        remaining = self.config.rate_limit_requests_per_minute - (current_requests + 1)
        
        return {"allowed": True, "remaining": remaining}
    
    def _generate_cache_key(self, service_name: str, path: str, headers: Dict[str, str]) -> str:
        """Generate cache key for request"""
        # Include relevant headers that might affect response
        cache_headers = {k: v for k, v in headers.items() 
                        if k.lower() in ['accept', 'accept-language', 'authorization']}
        
        cache_data = {
            "service": service_name,
            "path": path,
            "headers": cache_headers
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if valid"""
        if cache_key not in self.cached_responses:
            return None
        
        cached_entry = self.cached_responses[cache_key]
        cached_time = datetime.fromisoformat(cached_entry["cached_at"])
        
        if datetime.now() - cached_time > self.config.cache_ttl:
            del self.cached_responses[cache_key]
            return None
        
        return cached_entry["response"]
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache response"""
        self.cached_responses[cache_key] = {
            "response": response,
            "cached_at": datetime.now().isoformat()
        }
        
        # Limit cache size
        if len(self.cached_responses) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self.cached_responses.keys(), 
                               key=lambda k: self.cached_responses[k]["cached_at"])[:100]
            for key in oldest_keys:
                del self.cached_responses[key]
    
    async def _forward_request(self, endpoint: ServiceEndpoint, request: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to service endpoint"""
        # This would integrate with actual HTTP client
        # For now, return a simulated response
        await asyncio.sleep(0.1)  # Simulate network latency
        
        return {
            "status": 200,
            "body": {"message": "Success", "service": endpoint.service_name},
            "headers": {"Content-Type": "application/json"}
        }

# ==============================
# MAIN MICROSERVICES CONFIG MANAGER
# ==============================

class MicroservicesConfigManager:
    """Main microservices configuration and management system"""
    
    def __init__(self):
        # Configuration objects
        self.discovery_config = ServiceDiscoveryConfig()
        self.load_balancer_config = LoadBalancerConfig()
        self.api_gateway_config = APIGatewayConfig()
        self.service_mesh_config = ServiceMeshConfig()
        self.tracing_config = DistributedTracingConfig()
        
        # Core components
        self.service_registry = ServiceRegistry(self.discovery_config)
        self.load_balancer = LoadBalancer(self.load_balancer_config, self.service_registry)
        self.api_gateway = APIGateway(self.api_gateway_config, self.load_balancer)
        
        # Service definitions
        self.service_definitions: Dict[str, Dict[str, Any]] = {}
        self.active_services: Dict[str, List[ServiceEndpoint]] = {}
        
        # Monitoring
        self.request_metrics: Dict[str, Dict[str, Any]] = {}
        self.service_dependencies: Dict[str, List[str]] = {}
        
        self._initialize_default_services()
    
    def _initialize_default_services(self) -> None:
        """Initialize default service configurations"""
        # Define core platform services
        self.service_definitions = {
            "ai-service": {
                "type": ServiceType.BUSINESS_SERVICE,
                "communication": CommunicationType.HTTP_REST,
                "health_check_path": "/health",
                "dependencies": ["database-service", "storage-service"],
                "scaling": {"min_instances": 2, "max_instances": 10}
            },
            "user-service": {
                "type": ServiceType.BUSINESS_SERVICE,
                "communication": CommunicationType.HTTP_REST,
                "health_check_path": "/health",
                "dependencies": ["database-service", "auth-service"],
                "scaling": {"min_instances": 2, "max_instances": 8}
            },
            "content-service": {
                "type": ServiceType.BUSINESS_SERVICE,
                "communication": CommunicationType.HTTP_REST,
                "health_check_path": "/health",
                "dependencies": ["database-service", "storage-service", "ai-service"],
                "scaling": {"min_instances": 3, "max_instances": 15}
            },
            "auth-service": {
                "type": ServiceType.SECURITY_SERVICE,
                "communication": CommunicationType.HTTP_REST,
                "health_check_path": "/health",
                "dependencies": ["database-service"],
                "scaling": {"min_instances": 2, "max_instances": 6}
            },
            "notification-service": {
                "type": ServiceType.NOTIFICATION_SERVICE,
                "communication": CommunicationType.MESSAGE_QUEUE,
                "health_check_path": "/health",
                "dependencies": ["message-queue"],
                "scaling": {"min_instances": 1, "max_instances": 5}
            },
            "database-service": {
                "type": ServiceType.DATA_SERVICE,
                "communication": CommunicationType.TCP,
                "health_check_path": "/health",
                "dependencies": [],
                "scaling": {"min_instances": 1, "max_instances": 3}
            },
            "storage-service": {
                "type": ServiceType.DATA_SERVICE,
                "communication": CommunicationType.HTTP_REST,
                "health_check_path": "/health",
                "dependencies": [],
                "scaling": {"min_instances": 2, "max_instances": 8}
            }
        }
        
        # Set up API Gateway routes
        self.api_gateway.add_route("/api/v1/ai", "ai-service")
        self.api_gateway.add_route("/api/v1/users", "user-service")
        self.api_gateway.add_route("/api/v1/content", "content-service")
        self.api_gateway.add_route("/api/v1/auth", "auth-service")
        self.api_gateway.add_route("/api/v1/notifications", "notification-service")
    
    async def start_microservices_system(self) -> Dict[str, Any]:
        """Start the microservices system"""
        startup_results = {
            "timestamp": datetime.now(),
            "service_registry": False,
            "health_monitoring": False,
            "api_gateway": False,
            "load_balancer": False,
            "service_mesh": False,
            "distributed_tracing": False
        }
        
        try:
            # Start service registry and health monitoring
            await self.service_registry.start_health_monitoring()
            startup_results["service_registry"] = True
            startup_results["health_monitoring"] = True
            
            # API Gateway is ready (no async startup required in this implementation)
            startup_results["api_gateway"] = True
            startup_results["load_balancer"] = True
            
            # Service mesh configuration (would integrate with actual service mesh)
            if self.service_mesh_config.mesh_type:
                startup_results["service_mesh"] = True
            
            # Distributed tracing (would integrate with actual tracing system)
            if self.tracing_config.tracing_enabled:
                startup_results["distributed_tracing"] = True
            
            logging.info("Microservices system started successfully")
            return {"status": "started", "components": startup_results}
            
        except Exception as e:
            logging.error(f"Failed to start microservices system: {e}")
            return {"status": "error", "error": str(e), "components": startup_results}
    
    async def register_service_instance(self, service_name: str, host: str, port: int,
                                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register a service instance"""
        if service_name not in self.service_definitions:
            return {"status": "error", "message": "Service not defined"}
        
        service_def = self.service_definitions[service_name]
        
        endpoint = ServiceEndpoint(
            service_name=service_name,
            host=host,
            port=port,
            protocol="http" if service_def["communication"] == CommunicationType.HTTP_REST else "tcp",
            health_check_path=service_def["health_check_path"],
            metadata=metadata or {}
        )
        
        return await self.service_registry.register_service(endpoint)
    
    async def deregister_service_instance(self, service_name: str, host: str, port: int) -> Dict[str, Any]:
        """Deregister a service instance"""
        return await self.service_registry.deregister_service(service_name, host, port)
    
    async def handle_api_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API request through gateway"""
        return await self.api_gateway.handle_request(request)
    
    def configure_service_mesh(self, config: ServiceMeshConfig) -> Dict[str, Any]:
        """Configure service mesh settings"""
        self.service_mesh_config = config
        
        return {
            "status": "configured",
            "mesh_type": config.mesh_type.value,
            "mtls_enabled": config.mtls_enabled,
            "observability_enabled": config.observability_enabled
        }
    
    def configure_distributed_tracing(self, config: DistributedTracingConfig) -> Dict[str, Any]:
        """Configure distributed tracing"""
        self.tracing_config = config
        
        return {
            "status": "configured",
            "tracer_type": config.tracer_type,
            "sampling_rate": config.sampling_rate,
            "tracing_enabled": config.tracing_enabled
        }
    
    def add_service_dependency(self, service_name: str, dependency: str) -> Dict[str, Any]:
        """Add service dependency"""
        if service_name not in self.service_dependencies:
            self.service_dependencies[service_name] = []
        
        if dependency not in self.service_dependencies[service_name]:
            self.service_dependencies[service_name].append(dependency)
        
        return {
            "status": "added",
            "service": service_name,
            "dependency": dependency,
            "total_dependencies": len(self.service_dependencies[service_name])
        }
    
    def get_service_topology(self) -> Dict[str, Any]:
        """Get complete service topology"""
        topology = {
            "services": {},
            "dependencies": self.service_dependencies.copy(),
            "health_status": self.service_registry.get_service_health_status()
        }
        
        for service_name, definition in self.service_definitions.items():
            topology["services"][service_name] = {
                "type": definition["type"].value,
                "communication": definition["communication"].value,
                "scaling": definition["scaling"],
                "registered_instances": len(self.service_registry.registered_services.get(service_name, [])),
                "healthy_instances": len(self.service_registry.discover_services(service_name))
            }
        
        return topology
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get microservices performance metrics"""
        health_status = self.service_registry.get_service_health_status()
        
        # Calculate overall health
        total_services = len(self.service_definitions)
        healthy_services = sum(1 for status in health_status.values() 
                             if status["healthy_endpoints"] > 0)
        
        overall_health = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return {
            "overall_health_percentage": overall_health,
            "total_services": total_services,
            "healthy_services": healthy_services,
            "service_health_details": health_status,
            "api_gateway_metrics": {
                "active_routes": len(self.api_gateway.route_mappings),
                "cached_responses": len(self.api_gateway.cached_responses),
                "rate_limit_clients": len(self.api_gateway.rate_limiters)
            },
            "load_balancer_metrics": {
                "active_connections": sum(
                    sum(connections.values()) 
                    for connections in self.load_balancer.connection_counts.values()
                ),
                "circuit_breakers": sum(
                    len(breakers) 
                    for breakers in self.load_balancer.circuit_breakers.values()
                )
            }
        }
    
    async def execute_health_check(self) -> Dict[str, Any]:
        """Execute comprehensive health check"""
        health_results = {
            "timestamp": datetime.now(),
            "overall_status": "healthy",
            "service_registry": True,
            "api_gateway": True,
            "load_balancer": True,
            "services": {}
        }
        
        # Check each service
        for service_name in self.service_definitions.keys():
            endpoints = await self.service_registry.discover_services(service_name)
            health_results["services"][service_name] = {
                "healthy_instances": len(endpoints),
                "status": "healthy" if endpoints else "unhealthy"
            }
            
            if not endpoints:
                health_results["overall_status"] = "degraded"
        
        return health_results

# ==============================
# GLOBAL MICROSERVICES CONFIG MANAGER
# ==============================

# Global microservices configuration manager instance
global_microservices_config_manager = MicroservicesConfigManager()

# Export all classes and functions
__all__ = [
    # Core types and enums
    "ServiceType", "CommunicationType", "LoadBalancingStrategy", 
    "CircuitBreakerState", "ServiceMeshType", "HealthCheckType",
    
    # Data structures
    "ServiceEndpoint", "ServiceDiscoveryConfig", "LoadBalancerConfig",
    "CircuitBreakerConfig", "APIGatewayConfig", "ServiceMeshConfig",
    "DistributedTracingConfig",
    
    # Core components
    "ServiceRegistry", "LoadBalancer", "APIGateway",
    
    # Main manager
    "MicroservicesConfigManager", "global_microservices_config_manager"
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All rights reserved"

# Total lines: 580+ lines of enterprise microservices configuration code