"""Ainflue Core API Gateway - Enterprise API Gateway Management
=========================================================

Advanced API gateway providing request routing, authentication, rate limiting,
load balancing, API versioning, and microservices orchestration
for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import re
from urllib.parse import urlparse, parse_qs

try:
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import httpx
except ImportError:
    FastAPI = None
    Request = None
    Response = None
    HTTPException = None
    CORSMiddleware = None
    JSONResponse = None
    httpx = None

logger = logging.getLogger(__name__)

class RoutingStrategy(str, Enum):
    """API routing strategies"""
    PATH_BASED = "path_based"
    SUBDOMAIN_BASED = "subdomain_based"
    HEADER_BASED = "header_based"
    VERSION_BASED = "version_based"
    WEIGHTED = "weighted"

class LoadBalancingMethod(str, Enum):
    """Load balancing methods"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    HEALTH_CHECK = "health_check"

class AuthenticationMethod(str, Enum):
    """Authentication methods"""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    service_id: str
    name: str
    url: str
    health_check_url: str
    weight: int = 100
    timeout: int = 30
    retries: int = 3
    circuit_breaker: bool = True
    is_healthy: bool = True
    last_health_check: float = field(default_factory=time.time)
    request_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0

@dataclass
class RouteConfig:
    """Route configuration"""
    path: str
    methods: List[str]
    service_id: str
    endpoints: List[ServiceEndpoint]
    auth_required: bool = True
    auth_method: AuthenticationMethod = AuthenticationMethod.JWT
    rate_limit: Optional[int] = None
    timeout: int = 30
    retries: int = 3
    circuit_breaker: bool = True
    load_balancing: LoadBalancingMethod = LoadBalancingMethod.ROUND_ROBIN
    middleware: List[str] = field(default_factory=list)
    transformation_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GatewayConfig:
    """API Gateway configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    routing_strategy: RoutingStrategy = RoutingStrategy.PATH_BASED
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl: int = 300
    enable_metrics: bool = True
    enable_tracing: bool = True
    health_check_interval: int = 30
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    default_timeout: int = 30
    max_request_size: int = 10485760  # 10MB

@dataclass
class GatewayMetrics:
    """API Gateway metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    requests_per_second: float = 0.0
    active_connections: int = 0
    circuit_breakers_open: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    bytes_transferred: int = 0
    uptime_seconds: int = 0
    last_health_check: float = field(default_factory=time.time)

class APIGatewayCore:
    """Enterprise API Gateway core management system"""
    
    def __init__(self, config -> None: Optional[GatewayConfig] = None, level -> None: str = "enterprise") -> None:
        """Initialize API Gateway core"""
        self.config = config or GatewayConfig()
        self.level = level
        self.metrics = GatewayMetrics()
        self.start_time = time.time()
        
        # FastAPI application
        self.app: Optional[Any] = None
        
        # Service management
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.routes: Dict[str, RouteConfig] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Load balancing state
        self.load_balancer_state: Dict[str, int] = {}
        
        # Authentication handlers
        self.auth_handlers: Dict[AuthenticationMethod, Callable] = {}
        
        # Middleware registry
        self.middleware_registry: Dict[str, Callable] = {}
        
        # Cache
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        
        # Health monitoring
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("🌐 API Gateway Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize API Gateway"""
        try:
            logger.info("🚀 Initializing API Gateway core")
            
            if not FastAPI:
                logger.warning("⚠️ FastAPI not available, using mock API Gateway")
                return True
            
            # Create FastAPI application
            self.app = FastAPI(
                title="Ainflue API Gateway",
                description="Enterprise API Gateway for Ainflue Platform",
                version="1.0.0"
            )
            
            # Configure CORS
            if self.config.enable_cors:
                self.app.add_middleware(
                    CORSMiddleware,
                    allow_origins=self.config.cors_origins,
                    allow_credentials=True,
                    allow_methods=self.config.cors_methods,
                    allow_headers=self.config.cors_headers,
                )
            
            # Setup middleware
            self._setup_middleware()
            
            # Setup routes
            self._setup_routes()
            
            # Initialize circuit breakers
            self._initialize_circuit_breakers()
            
            logger.info("✅ API Gateway core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ API Gateway initialization failed: {str(e)}")
            return False
    
    def _setup_middleware(self) -> None:
        """Setup gateway middleware"""
        if not self.app:
            return
        
        @self.app.middleware("http")
        async def gateway_middleware(request -> None: Request, call_next) -> None:
            start_time = time.time()
            
            # Metrics
            self.metrics.total_requests += 1
            
            # Request size check
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.config.max_request_size:
                return JSONResponse(
                    status_code=413,
                    content={"error": "Request too large"}
                )
            
            try:
                # Process request
                response = await call_next(request)
                
                # Update metrics
                processing_time = time.time() - start_time
                self.metrics.successful_requests += 1
                self._update_avg_response_time(processing_time)
                
                return response
                
            except Exception as e:
                self.metrics.failed_requests += 1
                logger.error(f"Gateway middleware error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal gateway error"}
                )
    
    def _setup_routes(self) -> None:
        """Setup dynamic routes"""
        if not self.app:
            return
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
        async def dynamic_route_handler(request -> None: Request, path -> None: str) -> None:
            return await self._handle_request(request, path)
        
        @self.app.get("/health")
        async def health_check() -> None:
            return {"status": "healthy", "timestamp": time.time()}
        
        @self.app.get("/metrics")
        async def get_metrics() -> None:
            return self.get_metrics_summary()
    
    async def _handle_request(self, request: Request, path: str) -> Any:
        """Handle incoming request"""
        try:
            # Find matching route
            route_config = self._find_route(path, request.method)
            if not route_config:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Route not found"}
                )
            
            # Authentication
            if route_config.auth_required:
                auth_result = await self._authenticate_request(request, route_config.auth_method)
                if not auth_result:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Authentication failed"}
                    )
            
            # Rate limiting
            if route_config.rate_limit:
                rate_limit_result = await self._check_rate_limit(request, route_config.rate_limit)
                if not rate_limit_result:
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Rate limit exceeded"}
                    )
            
            # Check cache
            if self.config.enable_caching:
                cached_response = self._get_cached_response(request)
                if cached_response:
                    self.metrics.cache_hits += 1
                    return cached_response
            
            # Load balancing
            endpoint = self._select_endpoint(route_config)
            if not endpoint:
                return JSONResponse(
                    status_code=503,
                    content={"error": "Service unavailable"}
                )
            
            # Circuit breaker check
            if self._is_circuit_breaker_open(endpoint.service_id):
                return JSONResponse(
                    status_code=503,
                    content={"error": "Service circuit breaker open"}
                )
            
            # Forward request
            response = await self._forward_request(request, endpoint, route_config)
            
            # Cache response
            if self.config.enable_caching and response.status_code == 200:
                self._cache_response(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Request handling error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
    
    def _find_route(self, path: str, method: str) -> Optional[RouteConfig]:
        """Find matching route configuration"""
        for route_path, route_config in self.routes.items():
            if method.upper() in route_config.methods:
                # Simple path matching (can be enhanced with regex)
                if route_path == path or path.startswith(route_path.rstrip("*")):
                    return route_config
        return None
    
    async def _authenticate_request(self, request: Request, auth_method: AuthenticationMethod) -> bool:
        """Authenticate request"""
        try:
            handler = self.auth_handlers.get(auth_method)
            if handler:
                return await handler(request)
            
            # Default authentication (API key in header)
            api_key = request.headers.get("X-API-Key")
            return bool(api_key)  # Simple check
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    async def _check_rate_limit(self, request: Request, limit: int) -> bool:
        """Check rate limit"""
        # Simple implementation - can be enhanced with Redis
        client_ip = request.client.host if request.client else "unknown"
        current_time = int(time.time())
        
        # Reset counter every minute
        rate_key = f"{client_ip}:{current_time // 60}"
        
        # This is a simplified implementation
        return True  # Always allow for now
    
    def _get_cached_response(self, request: Request) -> Optional[Any]:
        """Get cached response"""
        cache_key = self._generate_cache_key(request)
        cached = self.response_cache.get(cache_key)
        
        if cached and time.time() - cached["timestamp"] < self.config.cache_ttl:
            return JSONResponse(content=cached["content"])
        
        return None
    
    def _cache_response(self, request -> None: Request, response -> None: Any) -> None:
        """Cache response"""
        cache_key = self._generate_cache_key(request)
        self.response_cache[cache_key] = {
            "content": response.body,
            "timestamp": time.time()
        }
        
        # Cleanup old cache entries
        if len(self.response_cache) > 1000:
            oldest_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]["timestamp"]
            )[:100]
            for key in oldest_keys:
                del self.response_cache[key]
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key"""
        return f"{request.method}:{request.url.path}:{request.url.query}"
    
    def _select_endpoint(self, route_config: RouteConfig) -> Optional[ServiceEndpoint]:
        """Select endpoint using load balancing"""
        healthy_endpoints = [ep for ep in route_config.endpoints if ep.is_healthy]
        if not healthy_endpoints:
            return None
        
        if route_config.load_balancing == LoadBalancingMethod.ROUND_ROBIN:
            service_state = self.load_balancer_state.get(route_config.service_id, 0)
            endpoint = healthy_endpoints[service_state % len(healthy_endpoints)]
            self.load_balancer_state[route_config.service_id] = service_state + 1
            return endpoint
        
        elif route_config.load_balancing == LoadBalancingMethod.RANDOM:
            import random
            return random.choice(healthy_endpoints)
        
        elif route_config.load_balancing == LoadBalancingMethod.LEAST_CONNECTIONS:
            return min(healthy_endpoints, key=lambda ep: ep.request_count)
        
        else:
            return healthy_endpoints[0]
    
    async def _forward_request(self, request: Request, endpoint: ServiceEndpoint, route_config: RouteConfig) -> Any:
        """Forward request to backend service"""
        try:
            if not httpx:
                return JSONResponse(content={"mock": "response"})
            
            # Build target URL
            target_url = f"{endpoint.url.rstrip('/')}/{request.url.path.lstrip('/')}"
            
            # Prepare headers
            headers = dict(request.headers)
            headers.pop("host", None)  # Remove host header
            
            # Read request body
            body = await request.body()
            
            # Make request
            async with httpx.AsyncClient(timeout=route_config.timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params
                )
            
            # Update endpoint metrics
            endpoint.request_count += 1
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except Exception as e:
            logger.error(f"Request forwarding error: {str(e)}")
            endpoint.error_count += 1
            self._handle_circuit_breaker(endpoint.service_id)
            
            return JSONResponse(
                status_code=502,
                content={"error": "Bad gateway"}
            )
    
    def _is_circuit_breaker_open(self, service_id: str) -> bool:
        """Check if circuit breaker is open"""
        circuit_breaker = self.circuit_breakers.get(service_id)
        if not circuit_breaker:
            return False
        
        if circuit_breaker["state"] == "open":
            if time.time() - circuit_breaker["last_failure"] > self.config.circuit_breaker_timeout:
                circuit_breaker["state"] = "half_open"
                return False
            return True
        
        return False
    
    def _handle_circuit_breaker(self, service_id -> None: str) -> None:
        """Handle circuit breaker logic"""
        if service_id not in self.circuit_breakers:
            return
        
        circuit_breaker = self.circuit_breakers[service_id]
        circuit_breaker["failure_count"] += 1
        circuit_breaker["last_failure"] = time.time()
        
        if circuit_breaker["failure_count"] >= self.config.circuit_breaker_threshold:
            circuit_breaker["state"] = "open"
            self.metrics.circuit_breakers_open += 1
            logger.warning(f"Circuit breaker opened for service {service_id}")
    
    def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for all services"""
        for service_id in self.services:
            self.circuit_breakers[service_id] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": 0
            }
    
    def _update_avg_response_time(self, processing_time -> None: float) -> None:
        """Update average response time"""
        total_requests = self.metrics.total_requests
        self.metrics.avg_response_time = (
            (self.metrics.avg_response_time * (total_requests - 1) + processing_time) /
            total_requests
        )
    
    async def register_service(self, service_id: str, endpoints: List[ServiceEndpoint]) -> bool:
        """Register service with endpoints"""
        try:
            self.services[service_id] = endpoints
            logger.info(f"🔗 Registered service '{service_id}' with {len(endpoints)} endpoints")
            return True
        except Exception as e:
            logger.error(f"Service registration failed: {str(e)}")
            return False
    
    async def register_route(self, route_config: RouteConfig) -> bool:
        """Register route configuration"""
        try:
            self.routes[route_config.path] = route_config
            logger.info(f"🛣️ Registered route '{route_config.path}'")
            return True
        except Exception as e:
            logger.error(f"Route registration failed: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start API Gateway"""
        try:
            if not hasattr(self, '_initialized'):
                await self.initialize()
                self._initialized = True
            
            # Start health monitoring
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            logger.info("🚀 API Gateway core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ API Gateway start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop API Gateway"""
        try:
            logger.info("🛑 Stopping API Gateway core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel health monitoring
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ API Gateway core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ API Gateway stop failed: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Perform API Gateway health check"""
        try:
            # Check all registered services
            for service_id, endpoints in self.services.items():
                for endpoint in endpoints:
                    if httpx and endpoint.health_check_url:
                        try:
                            async with httpx.AsyncClient(timeout=5) as client:
                                response = await client.get(endpoint.health_check_url)
                                endpoint.is_healthy = response.status_code == 200
                        except:
                            endpoint.is_healthy = False
                    endpoint.last_health_check = time.time()
            
            # Update metrics
            self.metrics.uptime_seconds = int(time.time() - self.start_time)
            self.metrics.last_health_check = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"API Gateway health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"API Gateway health monitor error: {str(e)}")
                await asyncio.sleep(60)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get API Gateway metrics summary"""
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": (
                self.metrics.successful_requests / max(self.metrics.total_requests, 1) * 100
            ),
            "avg_response_time_ms": round(self.metrics.avg_response_time * 1000, 2),
            "active_services": len(self.services),
            "active_routes": len(self.routes),
            "circuit_breakers_open": self.metrics.circuit_breakers_open,
            "cache_hit_ratio": (
                self.metrics.cache_hits / max(self.metrics.cache_hits + self.metrics.cache_misses, 1) * 100
            ),
            "uptime_seconds": int(time.time() - self.start_time)
        }

# Module exports
__all__ = [
    "APIGatewayCore", "GatewayConfig", "GatewayMetrics", "ServiceEndpoint",
    "RouteConfig", "RoutingStrategy", "LoadBalancingMethod", "AuthenticationMethod"
]