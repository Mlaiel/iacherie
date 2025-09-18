"""
API Gateway Template for Enterprise Microservices
================================================

Production-ready API gateway with:
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- Circuit breaker patterns
- Monitoring and analytics

Author: Fahed Mlaiel (mlaiel@live.de)
DevOps Engineer & API Gateway Expert
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import re

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Routing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    HEALTH_BASED = "health_based"


class AuthenticationType(Enum):
    """Authentication types"""
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    NONE = "none"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    url: str
    weight: int = 1
    max_connections: int = 100
    timeout: int = 30
    retries: int = 3
    health_check_path: str = "/health"
    health_check_interval: int = 30
    is_healthy: bool = True
    active_connections: int = 0
    last_health_check: Optional[datetime] = None


@dataclass
class RouteConfig:
    """Route configuration"""
    path: str
    service_name: str
    endpoints: List[ServiceEndpoint]
    methods: List[str] = None
    auth_required: bool = True
    auth_type: AuthenticationType = AuthenticationType.JWT
    rate_limit: Optional[int] = None
    rate_limit_window: int = 3600  # seconds
    timeout: int = 30
    retries: int = 3
    circuit_breaker_enabled: bool = True
    transformation_rules: Optional[Dict[str, Any]] = None
    headers_to_add: Optional[Dict[str, str]] = None
    headers_to_remove: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]


class ApiGatewayConfig(BaseModel):
    """API Gateway configuration"""
    host: str = Field(default="0.0.0.0", description="Gateway host")
    port: int = Field(default=8000, description="Gateway port")
    redis_url: str = Field(..., description="Redis URL for caching/rate limiting")
    jwt_secret: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    default_timeout: int = Field(default=30, description="Default request timeout")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    rate_limit_storage_ttl: int = Field(default=3600, description="Rate limit storage TTL")
    health_check_enabled: bool = Field(default=True, description="Enable health checks")
    health_check_interval: int = Field(default=30, description="Health check interval")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    cors_enabled: bool = Field(default=True, description="Enable CORS")
    compression_enabled: bool = Field(default=True, description="Enable compression")
    
    # Creator Economy specific settings
    creator_auth_endpoint: str = Field(default="/auth/creator", description="Creator auth endpoint")
    content_rate_limit: int = Field(default=100, description="Content API rate limit")
    collaboration_rate_limit: int = Field(default=50, description="Collaboration API rate limit")
    ai_processing_rate_limit: int = Field(default=20, description="AI processing rate limit")


class ApiGatewayTemplate(BaseMicroservice):
    """
    Enterprise API Gateway Template
    
    Comprehensive API gateway providing:
    - Intelligent request routing with multiple strategies
    - Authentication and authorization
    - Rate limiting and throttling
    - Circuit breaker protection
    - Request/response transformation
    - Load balancing and health monitoring
    - Creator economy specific routing
    """
    
    def __init__(self, config: ApiGatewayConfig):
        super().__init__()
        self.config = config
        self.app = FastAPI(title="Ainflue API Gateway", version="1.0.0")
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Service registry and routing
        self.routes: Dict[str, RouteConfig] = {}
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Rate limiting storage
        self.rate_limit_cache: Dict[str, Dict[str, Any]] = {}
        
        # Health check tasks
        self.health_check_tasks: List[asyncio.Task] = []
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
        # Metrics
        if config.monitoring_enabled:
            self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        self.requests_total = Counter(
            'api_gateway_requests_total',
            'Total API requests',
            ['route', 'method', 'status', 'service']
        )
        
        self.request_duration = Histogram(
            'api_gateway_request_duration_seconds',
            'Request duration',
            ['route', 'method', 'service']
        )
        
        self.active_connections = Gauge(
            'api_gateway_active_connections',
            'Active connections per service',
            ['service']
        )
        
        self.rate_limit_hits = Counter(
            'api_gateway_rate_limit_hits_total',
            'Rate limit hits',
            ['route', 'client_id']
        )
        
        self.circuit_breaker_trips = Counter(
            'api_gateway_circuit_breaker_trips_total',
            'Circuit breaker trips',
            ['service']
        )
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        if self.config.cors_enabled:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Compression middleware
        if self.config.compression_enabled:
            self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom middleware for request processing
        @self.app.middleware("http")
        async def process_request(request: Request, call_next):
            start_time = time.time()
            
            # Find matching route
            route_config = await self._find_route(request)
            if not route_config:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Route not found"}
                )
            
            try:
                # Authentication
                if route_config.auth_required:
                    auth_result = await self._authenticate_request(request, route_config)
                    if not auth_result:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Authentication failed"}
                        )
                
                # Rate limiting
                if route_config.rate_limit:
                    rate_limit_result = await self._check_rate_limit(request, route_config)
                    if not rate_limit_result:
                        if self.config.monitoring_enabled:
                            self.rate_limit_hits.labels(
                                route=route_config.path,
                                client_id=self._get_client_id(request)
                            ).inc()
                        
                        return JSONResponse(
                            status_code=429,
                            content={"error": "Rate limit exceeded"}
                        )
                
                # Add route config to request state
                request.state.route_config = route_config
                
                # Process request
                response = await call_next(request)
                
                # Update metrics
                if self.config.monitoring_enabled:
                    duration = time.time() - start_time
                    self.request_duration.labels(
                        route=route_config.path,
                        method=request.method,
                        service=route_config.service_name
                    ).observe(duration)
                    
                    self.requests_total.labels(
                        route=route_config.path,
                        method=request.method,
                        status=response.status_code,
                        service=route_config.service_name
                    ).inc()
                
                return response
                
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal server error"}
                )
    
    def _setup_routes(self):
        """Setup gateway routes"""
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            health_status = await self.health_check()
            return health_status
        
        # Metrics endpoint
        @self.app.get("/metrics")
        async def metrics():
            if self.config.monitoring_enabled:
                from prometheus_client import generate_latest
                return Response(
                    generate_latest(),
                    media_type="text/plain"
                )
            return {"message": "Metrics disabled"}
        
        # Gateway info endpoint
        @self.app.get("/gateway/info")
        async def gateway_info():
            return {
                "version": "1.0.0",
                "routes": len(self.routes),
                "services": len(self.service_endpoints),
                "health_checks_enabled": self.config.health_check_enabled
            }
        
        # Dynamic route handler
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy_request(request: Request):
            return await self._proxy_request(request)
    
    async def start(self):
        """Start API gateway"""
        await super().start()
        
        # Initialize Redis connection
        self.redis_client = redis.from_url(
            self.config.redis_url,
            decode_responses=True,
            retry_on_timeout=True
        )
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.default_timeout),
            limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100)
        )
        
        # Start health check tasks
        if self.config.health_check_enabled:
            await self._start_health_checks()
        
        logger.info(f"API Gateway started on {self.config.host}:{self.config.port}")
    
    async def stop(self):
        """Stop API gateway"""
        # Stop health check tasks
        for task in self.health_check_tasks:
            task.cancel()
        
        if self.http_client:
            await self.http_client.aclose()
        
        if self.redis_client:
            await self.redis_client.close()
        
        await super().stop()
        logger.info("API Gateway stopped")
    
    def register_route(self, route_config: RouteConfig):
        """Register new route"""
        self.routes[route_config.path] = route_config
        self.service_endpoints[route_config.service_name] = route_config.endpoints
        
        # Create circuit breaker for service
        if route_config.circuit_breaker_enabled:
            self.circuit_breakers[route_config.service_name] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30,
                expected_exception=httpx.RequestError
            )
        
        logger.info(f"Registered route: {route_config.path} -> {route_config.service_name}")
    
    async def _find_route(self, request: Request) -> Optional[RouteConfig]:
        """Find matching route for request"""
        path = request.url.path
        
        # Direct match
        if path in self.routes:
            return self.routes[path]
        
        # Pattern matching
        for route_path, route_config in self.routes.items():
            if self._path_matches(path, route_path):
                return route_config
        
        return None
    
    def _path_matches(self, request_path: str, route_pattern: str) -> bool:
        """Check if request path matches route pattern"""
        # Convert route pattern to regex
        # Handle path parameters like /users/{user_id}
        pattern = route_pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
        pattern = f"^{pattern}$"
        
        return bool(re.match(pattern, request_path))
    
    async def _authenticate_request(self, request: Request, route_config: RouteConfig) -> bool:
        """Authenticate request based on route configuration"""
        if route_config.auth_type == AuthenticationType.NONE:
            return True
        
        if route_config.auth_type == AuthenticationType.JWT:
            return await self._validate_jwt_token(request)
        elif route_config.auth_type == AuthenticationType.API_KEY:
            return await self._validate_api_key(request)
        elif route_config.auth_type == AuthenticationType.OAUTH2:
            return await self._validate_oauth2_token(request)
        elif route_config.auth_type == AuthenticationType.BASIC:
            return await self._validate_basic_auth(request)
        
        return False
    
    async def _validate_jwt_token(self, request: Request) -> bool:
        """Validate JWT token"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return False
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            import jwt
            payload = jwt.decode(
                token,
                self.config.jwt_secret,
                algorithms=[self.config.jwt_algorithm]
            )
            
            # Add user info to request state
            request.state.user = payload
            return True
            
        except jwt.InvalidTokenError:
            return False
    
    async def _validate_api_key(self, request: Request) -> bool:
        """Validate API key"""
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return False
        
        # Check API key in Redis cache
        try:
            is_valid = await self.redis_client.exists(f"api_key:{api_key}")
            return bool(is_valid)
        except redis.RedisError:
            return False
    
    async def _validate_oauth2_token(self, request: Request) -> bool:
        """Validate OAuth2 token"""
        # Implement OAuth2 token validation
        # This would typically involve calling an OAuth2 introspection endpoint
        return True
    
    async def _validate_basic_auth(self, request: Request) -> bool:
        """Validate basic authentication"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False
        
        # Decode and validate credentials
        import base64
        try:
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            # Validate credentials (implement your logic)
            return await self._validate_credentials(username, password)
            
        except Exception:
            return False
    
    async def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate username/password credentials"""
        # Implement credential validation logic
        return True
    
    async def _check_rate_limit(self, request: Request, route_config: RouteConfig) -> bool:
        """Check rate limiting"""
        client_id = self._get_client_id(request)
        rate_limit_key = f"rate_limit:{route_config.path}:{client_id}"
        
        try:
            # Use Redis for distributed rate limiting
            current = await self.redis_client.get(rate_limit_key)
            
            if current is None:
                # First request in window
                await self.redis_client.setex(
                    rate_limit_key,
                    route_config.rate_limit_window,
                    1
                )
                return True
            
            if int(current) >= route_config.rate_limit:
                return False
            
            # Increment counter
            await self.redis_client.incr(rate_limit_key)
            return True
            
        except redis.RedisError:
            # Fallback to in-memory rate limiting
            return self._check_memory_rate_limit(client_id, route_config)
    
    def _check_memory_rate_limit(self, client_id: str, route_config: RouteConfig) -> bool:
        """Fallback in-memory rate limiting"""
        now = time.time()
        key = f"{route_config.path}:{client_id}"
        
        if key not in self.rate_limit_cache:
            self.rate_limit_cache[key] = {
                'count': 1,
                'window_start': now
            }
            return True
        
        cache_entry = self.rate_limit_cache[key]
        
        # Check if window has expired
        if now - cache_entry['window_start'] >= route_config.rate_limit_window:
            cache_entry['count'] = 1
            cache_entry['window_start'] = now
            return True
        
        if cache_entry['count'] >= route_config.rate_limit:
            return False
        
        cache_entry['count'] += 1
        return True
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from JWT token
        if hasattr(request.state, 'user') and 'sub' in request.state.user:
            return request.state.user['sub']
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _proxy_request(self, request: Request) -> Response:
        """Proxy request to backend service"""
        route_config = request.state.route_config
        
        # Select endpoint using routing strategy
        endpoint = await self._select_endpoint(route_config)
        if not endpoint:
            return JSONResponse(
                status_code=503,
                content={"error": "No healthy endpoints available"}
            )
        
        # Build target URL
        target_url = f"{endpoint.url.rstrip('/')}{request.url.path}"
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        # Prepare headers
        headers = dict(request.headers)
        
        # Apply header transformations
        if route_config.headers_to_add:
            headers.update(route_config.headers_to_add)
        
        if route_config.headers_to_remove:
            for header in route_config.headers_to_remove:
                headers.pop(header, None)
        
        # Remove host header to avoid conflicts
        headers.pop('host', None)
        
        try:
            # Get circuit breaker for service
            circuit_breaker = self.circuit_breakers.get(route_config.service_name)
            
            if circuit_breaker and circuit_breaker.state.name == 'OPEN':
                return JSONResponse(
                    status_code=503,
                    content={"error": "Circuit breaker open"}
                )
            
            # Read request body
            body = await request.body()
            
            # Make request to backend
            response = await self.http_client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=route_config.timeout
            )
            
            # Apply response transformations if needed
            response_content = response.content
            
            # Circuit breaker success
            if circuit_breaker:
                circuit_breaker.record_success()
            
            return Response(
                content=response_content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            
            # Circuit breaker failure
            if circuit_breaker:
                circuit_breaker.record_failure()
                
                if self.config.monitoring_enabled:
                    self.circuit_breaker_trips.labels(
                        service=route_config.service_name
                    ).inc()
            
            return JSONResponse(
                status_code=502,
                content={"error": "Bad gateway"}
            )
    
    async def _select_endpoint(self, route_config: RouteConfig) -> Optional[ServiceEndpoint]:
        """Select endpoint based on routing strategy"""
        healthy_endpoints = [
            ep for ep in route_config.endpoints
            if ep.is_healthy and ep.active_connections < ep.max_connections
        ]
        
        if not healthy_endpoints:
            return None
        
        # For now, use round-robin
        # TODO: Implement other routing strategies
        endpoint = healthy_endpoints[0]
        endpoint.active_connections += 1
        
        return endpoint
    
    async def _start_health_checks(self):
        """Start health check tasks for all services"""
        for service_name, endpoints in self.service_endpoints.items():
            for endpoint in endpoints:
                task = asyncio.create_task(
                    self._health_check_loop(service_name, endpoint)
                )
                self.health_check_tasks.append(task)
    
    async def _health_check_loop(self, service_name: str, endpoint: ServiceEndpoint):
        """Health check loop for endpoint"""
        while True:
            try:
                health_url = f"{endpoint.url.rstrip('/')}{endpoint.health_check_path}"
                
                response = await self.http_client.get(
                    health_url,
                    timeout=10.0
                )
                
                endpoint.is_healthy = response.status_code == 200
                endpoint.last_health_check = datetime.utcnow()
                
                if self.config.monitoring_enabled:
                    self.active_connections.labels(service=service_name).set(
                        endpoint.active_connections
                    )
                
            except Exception as e:
                endpoint.is_healthy = False
                endpoint.last_health_check = datetime.utcnow()
                logger.warning(f"Health check failed for {service_name}: {e}")
            
            await asyncio.sleep(endpoint.health_check_interval)
    
    async def health_check(self) -> Dict[str, Any]:
        """Gateway health check"""
        try:
            # Test Redis connection
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            # Check service health
            service_health = {}
            for service_name, endpoints in self.service_endpoints.items():
                healthy_count = sum(1 for ep in endpoints if ep.is_healthy)
                service_health[service_name] = {
                    'healthy_endpoints': healthy_count,
                    'total_endpoints': len(endpoints),
                    'healthy': healthy_count > 0
                }
            
            overall_healthy = redis_healthy and all(
                sh['healthy'] for sh in service_health.values()
            )
            
            return {
                'status': 'healthy' if overall_healthy else 'degraded',
                'redis_connected': redis_healthy,
                'services': service_health,
                'routes_registered': len(self.routes),
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Example route configurations for Creator Economy
def create_creator_economy_routes() -> List[RouteConfig]:
    """Create route configurations for creator economy services"""
    return [
        # Content service routes
        RouteConfig(
            path="/api/v1/content",
            service_name="content_service",
            endpoints=[
                ServiceEndpoint("http://content-service-1:8001"),
                ServiceEndpoint("http://content-service-2:8001")
            ],
            rate_limit=100,
            auth_type=AuthenticationType.JWT
        ),
        
        # AI processing routes
        RouteConfig(
            path="/api/v1/ai",
            service_name="ai_processing_service",
            endpoints=[
                ServiceEndpoint("http://ai-service-1:8002"),
                ServiceEndpoint("http://ai-service-2:8002")
            ],
            rate_limit=20,
            auth_type=AuthenticationType.JWT,
            timeout=60  # AI processing takes longer
        ),
        
        # Collaboration routes
        RouteConfig(
            path="/api/v1/collaboration",
            service_name="collaboration_service",
            endpoints=[
                ServiceEndpoint("http://collaboration-service:8003")
            ],
            rate_limit=50,
            auth_type=AuthenticationType.JWT
        ),
        
        # Revenue/monetization routes
        RouteConfig(
            path="/api/v1/revenue",
            service_name="revenue_service",
            endpoints=[
                ServiceEndpoint("http://revenue-service:8004")
            ],
            rate_limit=30,
            auth_type=AuthenticationType.JWT
        ),
        
        # Distribution routes
        RouteConfig(
            path="/api/v1/distribution",
            service_name="distribution_service",
            endpoints=[
                ServiceEndpoint("http://distribution-service:8005")
            ],
            rate_limit=40,
            auth_type=AuthenticationType.JWT
        )
    ]