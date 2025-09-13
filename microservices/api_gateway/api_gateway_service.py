"""
🎯 API Gateway Microservice
Enterprise API gateway with routing, authentication, rate limiting, and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import json
from datetime import datetime, timedelta
import jwt
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RouteMethod(str, Enum):
    """HTTP methods supported by the gateway"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class AuthenticationType(str, Enum):
    """Authentication types"""
    NONE = "none"
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"


@dataclass
class ServiceInstance:
    """Service instance definition"""
    id: str
    host: str
    port: int
    weight: int = 1
    health_check_url: str = "/health"
    is_healthy: bool = True
    connection_count: int = 0
    last_health_check: Optional[datetime] = None


@dataclass
class RouteConfiguration:
    """Route configuration for the gateway"""
    path: str
    methods: List[RouteMethod]
    service_name: str
    target_path: str = None
    authentication: AuthenticationType = AuthenticationType.NONE
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    middleware: List[str] = field(default_factory=list)
    cors_enabled: bool = True


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        
    def is_allowed(self, client_id: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # Clean old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= limit:
            return False
            
        # Add current request
        self.requests[client_id].append(now)
        return True


class LoadBalancer:
    """Load balancer for service instances"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.current_index = 0
        
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Select service instance based on strategy"""
        healthy_instances = [i for i in instances if i.is_healthy]
        
        if not healthy_instances:
            return None
            
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            instance = healthy_instances[self.current_index % len(healthy_instances)]
            self.current_index += 1
            return instance
            
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            # Simple weighted round robin implementation
            total_weight = sum(i.weight for i in healthy_instances)
            if total_weight == 0:
                return healthy_instances[0]
                
            # Select based on weights
            random_weight = (self.current_index % total_weight)
            current_weight = 0
            
            for instance in healthy_instances:
                current_weight += instance.weight
                if random_weight < current_weight:
                    self.current_index += 1
                    return instance
                    
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(healthy_instances, key=lambda x: x.connection_count)
            
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            import random
            return random.choice(healthy_instances)
            
        # Default to first available
        return healthy_instances[0]


class AuthenticationManager:
    """Authentication and authorization manager"""
    
    def __init__(self, jwt_secret: str = "your-secret-key"):
        self.jwt_secret = jwt_secret
        self.api_keys: Set[str] = set()
        
    def add_api_key(self, api_key: str):
        """Add valid API key"""
        self.api_keys.add(api_key)
        
    def validate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
            
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        return api_key in self.api_keys
        
    def authenticate_request(self, request: Request, auth_type: AuthenticationType) -> Optional[Dict[str, Any]]:
        """Authenticate incoming request"""
        if auth_type == AuthenticationType.NONE:
            return {"authenticated": True}
            
        elif auth_type == AuthenticationType.JWT:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            token = auth_header[7:]  # Remove "Bearer " prefix
            return self.validate_jwt(token)
            
        elif auth_type == AuthenticationType.API_KEY:
            api_key = request.headers.get("X-API-Key")
            if not api_key or not self.validate_api_key(api_key):
                return None
            return {"authenticated": True, "api_key": api_key}
            
        return None


class CircuitBreaker:
    """Circuit breaker for service protection"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    def is_allowed(self) -> bool:
        """Check if requests are allowed"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True
            
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.state = "closed"
        
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class APIGatewayService:
    """Enterprise API Gateway Service"""
    
    def __init__(self, name: str = "api_gateway"):
        self.name = name
        self.app = FastAPI(title="Ainflue API Gateway", version="1.0.0")
        self.routes: Dict[str, RouteConfiguration] = {}
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.load_balancer = LoadBalancer()
        self.rate_limiter = RateLimiter()
        self.auth_manager = AuthenticationManager()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
        
        self._setup_middleware()
        self._setup_routes()
        
    def _setup_middleware(self):
        """Setup middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure properly in production
        )
        
    def _setup_routes(self):
        """Setup gateway routes"""
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": self.metrics
            }
            
        @self.app.get("/metrics")
        async def get_metrics():
            return self.metrics
            
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
        async def gateway_handler(request: Request, path: str):
            return await self._handle_request(request, path)
            
    async def _handle_request(self, request: Request, path: str) -> Response:
        """Handle incoming request through the gateway"""
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Find matching route
            route_config = self._find_route(path, request.method)
            if not route_config:
                raise HTTPException(status_code=404, detail="Route not found")
                
            # Authentication
            auth_result = self.auth_manager.authenticate_request(request, route_config.authentication)
            if route_config.authentication != AuthenticationType.NONE and not auth_result:
                raise HTTPException(status_code=401, detail="Authentication failed")
                
            # Rate limiting
            if route_config.rate_limit:
                client_id = self._get_client_id(request)
                if not self.rate_limiter.is_allowed(client_id, route_config.rate_limit):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                    
            # Circuit breaker check
            circuit_breaker = self._get_circuit_breaker(route_config.service_name)
            if route_config.circuit_breaker_enabled and not circuit_breaker.is_allowed():
                raise HTTPException(status_code=503, detail="Service temporarily unavailable")
                
            # Load balancing
            service_instance = self._select_service_instance(route_config.service_name)
            if not service_instance:
                raise HTTPException(status_code=503, detail="No healthy service instances available")
                
            # Forward request
            response = await self._forward_request(request, route_config, service_instance)
            
            # Record success
            circuit_breaker.record_success()
            self.metrics["successful_requests"] += 1
            
            return response
            
        except Exception as e:
            # Record failure
            if 'circuit_breaker' in locals():
                circuit_breaker.record_failure()
            self.metrics["failed_requests"] += 1
            
            if isinstance(e, HTTPException):
                raise e
            else:
                logger.exception(f"Gateway error: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal gateway error")
                
        finally:
            # Update metrics
            response_time = time.time() - start_time
            self.metrics["average_response_time"] = (
                (self.metrics["average_response_time"] * (self.metrics["total_requests"] - 1) + response_time) /
                self.metrics["total_requests"]
            )
            
    def _find_route(self, path: str, method: str) -> Optional[RouteConfiguration]:
        """Find matching route configuration"""
        # Simple path matching - could be enhanced with regex patterns
        for route_path, config in self.routes.items():
            if path.startswith(route_path.rstrip('*')) and RouteMethod(method) in config.methods:
                return config
        return None
        
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Use IP address as default client ID
        return request.client.host if request.client else "unknown"
        
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
        
    def _select_service_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Select healthy service instance"""
        instances = self.services.get(service_name, [])
        return self.load_balancer.select_instance(instances)
        
    async def _forward_request(self, request: Request, config: RouteConfiguration, instance: ServiceInstance) -> Response:
        """Forward request to service instance"""
        import httpx
        
        # Build target URL
        target_path = config.target_path or request.url.path
        target_url = f"http://{instance.host}:{instance.port}{target_path}"
        
        # Forward headers (excluding hop-by-hop headers)
        headers = dict(request.headers)
        hop_by_hop = {'connection', 'upgrade', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding'}
        headers = {k: v for k, v in headers.items() if k.lower() not in hop_by_hop}
        
        # Forward request
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=dict(request.query_params)
            )
            
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    def add_route(self, config: RouteConfiguration):
        """Add route configuration"""
        self.routes[config.path] = config
        logger.info(f"Added route: {config.path} -> {config.service_name}")
        
    def add_service_instance(self, service_name: str, instance: ServiceInstance):
        """Add service instance"""
        if service_name not in self.services:
            self.services[service_name] = []
        self.services[service_name].append(instance)
        logger.info(f"Added service instance: {service_name} -> {instance.host}:{instance.port}")
        
    def remove_service_instance(self, service_name: str, instance_id: str):
        """Remove service instance"""
        if service_name in self.services:
            self.services[service_name] = [
                instance for instance in self.services[service_name]
                if instance.id != instance_id
            ]
            logger.info(f"Removed service instance: {service_name} -> {instance_id}")
            
    async def health_check_services(self):
        """Perform health checks on all service instances"""
        import httpx
        
        for service_name, instances in self.services.items():
            for instance in instances:
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.get(f"http://{instance.host}:{instance.port}{instance.health_check_url}")
                        instance.is_healthy = response.status_code == 200
                        instance.last_health_check = datetime.utcnow()
                except Exception as e:
                    instance.is_healthy = False
                    instance.last_health_check = datetime.utcnow()
                    logger.warning(f"Health check failed for {service_name} {instance.id}: {str(e)}")
                    
    def get_status(self) -> Dict[str, Any]:
        """Get gateway status"""
        return {
            "name": self.name,
            "status": "running",
            "routes_count": len(self.routes),
            "services_count": len(self.services),
            "total_instances": sum(len(instances) for instances in self.services.values()),
            "healthy_instances": sum(
                len([i for i in instances if i.is_healthy])
                for instances in self.services.values()
            ),
            "metrics": self.metrics,
            "timestamp": datetime.utcnow().isoformat()
        }


def create_api_gateway_service(config: Dict[str, Any] = None) -> APIGatewayService:
    """Factory function to create API Gateway service"""
    config = config or {}
    service_name = config.get('name', 'api_gateway')
    
    gateway = APIGatewayService(service_name)
    
    # Configure JWT secret if provided
    if 'jwt_secret' in config:
        gateway.auth_manager.jwt_secret = config['jwt_secret']
        
    # Add API keys if provided
    if 'api_keys' in config:
        for api_key in config['api_keys']:
            gateway.auth_manager.add_api_key(api_key)
            
    # Configure load balancing strategy
    if 'load_balancing_strategy' in config:
        gateway.load_balancer.strategy = LoadBalancingStrategy(config['load_balancing_strategy'])
        
    return gateway


__all__ = [
    'APIGatewayService', 'RouteConfiguration', 'ServiceInstance',
    'RouteMethod', 'AuthenticationType', 'LoadBalancingStrategy',
    'create_api_gateway_service'
]