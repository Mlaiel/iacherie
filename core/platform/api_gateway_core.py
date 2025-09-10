"""Ainflue Core API Gateway - Enterprise API Gateway Management
=============================================================

Core API gateway management system providing advanced API orchestration,
request routing, load balancing, authentication, rate limiting, and
enterprise-grade API gateway operations for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import hashlib
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt

logger = logging.getLogger(__name__)

class RoutingStrategy(str, Enum):
    """API routing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    GEOGRAPHIC = "geographic"
    HEALTH_BASED = "health_based"

class AuthenticationType(str, Enum):
    """Authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    id: str
    url: str
    weight: int = 1
    health_check_url: Optional[str] = None
    is_healthy: bool = True
    connection_count: int = 0
    response_time: float = 0.0
    last_health_check: float = field(default_factory=time.time)

@dataclass
class RouteConfig:
    """API route configuration"""
    path: str
    method: str = "GET"
    service_endpoints: List[ServiceEndpoint] = field(default_factory=list)
    routing_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    authentication: AuthenticationType = AuthenticationType.JWT
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 30
    retries: int = 3
    cache_ttl: Optional[int] = None
    transform_request: Optional[Callable] = None
    transform_response: Optional[Callable] = None

@dataclass
class GatewayConfig:
    """API Gateway configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    jwt_secret: str = "ainflue_secret_key"
    jwt_algorithm: str = "HS256"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_redis_url: str = "redis://localhost:6379/4"
    health_check_interval: int = 30
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

@dataclass
class GatewayMetrics:
    """API Gateway metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    active_connections: int = 0
    rate_limited_requests: int = 0
    circuit_breaker_trips: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        import redis.asyncio as redis
        self.redis_client = redis.from_url(self.redis_url)
    
    async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed within rate limit"""
        if not self.redis_client:
            return True
        
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            request_count = await self.redis_client.zcard(key)
            
            if request_count >= limit:
                return False
            
            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, window)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Rate limiter error: {e}")
            return True  # Allow on error

class CircuitBreaker:
    """Circuit breaker for service endpoints"""
    
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        
        # HALF_OPEN state
        return True

class APIGatewayCore:
    """Enterprise API Gateway core management system"""
    
    def __init__(self, config: Optional[GatewayConfig] = None):
        """Initialize API Gateway core"""
        self.config = config or GatewayConfig()
        self.metrics = GatewayMetrics()
        
        # FastAPI application
        self.app = FastAPI(title="Ainflue API Gateway", version="1.0.0")
        
        # Route configurations
        self.routes: Dict[str, RouteConfig] = {}
        
        # Service management
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiter = RateLimiter(self.config.rate_limit_redis_url)
        
        # HTTP client for proxying
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Security
        self.security = HTTPBearer(auto_error=False)
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        
        logger.info("🌐 API Gateway Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize API Gateway system"""
        try:
            logger.info("🔌 Initializing API Gateway...")
            
            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_keepalive_connections=100, max_connections=200)
            )
            
            # Initialize rate limiter
            await self.rate_limiter.initialize()
            
            # Configure CORS
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
            
            # Add middleware
            self.app.middleware("http")(self._request_middleware)
            
            # Start health checking
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            logger.info("✅ API Gateway Core initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ API Gateway Core initialization failed: {e}")
            return False
    
    async def _request_middleware(self, request: Request, call_next):
        """Request processing middleware"""
        start_time = time.time()
        self.metrics.total_requests += 1
        self.metrics.active_connections += 1
        
        try:
            # Check if this is a gateway route
            route_key = f"{request.method}:{request.url.path}"
            
            if route_key in self.routes:
                response = await self._handle_gateway_request(request, route_key)
            else:
                response = await call_next(request)
            
            # Update success metrics
            self.metrics.successful_requests += 1
            
        except Exception as e:
            # Update failure metrics
            self.metrics.failed_requests += 1
            logger.error(f"❌ Request failed: {e}")
            
            response = Response(
                content=json.dumps({"error": "Internal server error"}),
                status_code=500,
                media_type="application/json"
            )
        
        finally:
            # Update timing metrics
            request_time = time.time() - start_time
            self._update_response_time(request_time)
            self.metrics.active_connections -= 1
        
        return response
    
    async def _handle_gateway_request(self, request: Request, route_key: str) -> Response:
        """Handle request through API Gateway"""
        route_config = self.routes[route_key]
        
        # Authentication
        if route_config.authentication != AuthenticationType.NONE:
            authenticated = await self._authenticate_request(request, route_config.authentication)
            if not authenticated:
                raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Rate limiting
        if route_config.rate_limit:
            client_id = self._get_client_identifier(request)
            rate_limit_key = f"rate_limit:{client_id}:{route_key}"
            
            allowed = await self.rate_limiter.is_allowed(
                rate_limit_key, route_config.rate_limit, 60
            )
            
            if not allowed:
                self.metrics.rate_limited_requests += 1
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Select service endpoint
        endpoint = self._select_endpoint(route_config)
        if not endpoint:
            raise HTTPException(status_code=503, detail="No healthy endpoints available")
        
        # Check circuit breaker
        circuit_breaker = self._get_circuit_breaker(endpoint.id)
        if not circuit_breaker.can_execute():
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        try:
            # Proxy request
            response = await self._proxy_request(request, endpoint, route_config)
            circuit_breaker.record_success()
            
            return response
            
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"❌ Request to {endpoint.url} failed: {e}")
            
            # Retry logic
            if route_config.retries > 0:
                return await self._retry_request(request, route_config, exclude_endpoint=endpoint)
            
            raise HTTPException(status_code=502, detail="Service unavailable")
    
    async def _authenticate_request(self, request: Request, auth_type: AuthenticationType) -> bool:
        """Authenticate request based on type"""
        try:
            if auth_type == AuthenticationType.JWT:
                credentials = await self.security(request)
                if not credentials:
                    return False
                
                # Verify JWT token
                payload = jwt.decode(
                    credentials.credentials,
                    self.config.jwt_secret,
                    algorithms=[self.config.jwt_algorithm]
                )
                
                # Add user info to request state
                request.state.user = payload
                return True
            
            elif auth_type == AuthenticationType.API_KEY:
                api_key = request.headers.get("X-API-Key")
                if not api_key:
                    return False
                
                # Validate API key (implement your logic)
                return self._validate_api_key(api_key)
            
            return False
            
        except jwt.InvalidTokenError:
            return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        # Implement your API key validation logic
        return True  # Placeholder
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from JWT
        if hasattr(request.state, 'user') and 'user_id' in request.state.user:
            return f"user:{request.state.user['user_id']}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _select_endpoint(self, route_config: RouteConfig) -> Optional[ServiceEndpoint]:
        """Select service endpoint based on routing strategy"""
        healthy_endpoints = [ep for ep in route_config.service_endpoints if ep.is_healthy]
        
        if not healthy_endpoints:
            return None
        
        if route_config.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            # Simple round-robin (stateless)
            return min(healthy_endpoints, key=lambda ep: ep.connection_count)
        
        elif route_config.routing_strategy == RoutingStrategy.WEIGHTED:
            # Weighted selection based on endpoint weights
            total_weight = sum(ep.weight for ep in healthy_endpoints)
            import random
            
            selection_point = random.randint(1, total_weight)
            current_weight = 0
            
            for endpoint in healthy_endpoints:
                current_weight += endpoint.weight
                if selection_point <= current_weight:
                    return endpoint
        
        elif route_config.routing_strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return min(healthy_endpoints, key=lambda ep: ep.connection_count)
        
        elif route_config.routing_strategy == RoutingStrategy.HEALTH_BASED:
            return min(healthy_endpoints, key=lambda ep: ep.response_time)
        
        # Default to first healthy endpoint
        return healthy_endpoints[0]
    
    def _get_circuit_breaker(self, endpoint_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for endpoint"""
        if endpoint_id not in self.circuit_breakers:
            self.circuit_breakers[endpoint_id] = CircuitBreaker(
                threshold=self.config.circuit_breaker_threshold,
                timeout=self.config.circuit_breaker_timeout
            )
        
        return self.circuit_breakers[endpoint_id]
    
    async def _proxy_request(self, request: Request, endpoint: ServiceEndpoint, 
                           route_config: RouteConfig) -> Response:
        """Proxy request to service endpoint"""
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")
        
        # Increment connection count
        endpoint.connection_count += 1
        
        try:
            # Build target URL
            target_url = f"{endpoint.url.rstrip('/')}{request.url.path}"
            if request.url.query:
                target_url += f"?{request.url.query}"
            
            # Prepare headers
            headers = dict(request.headers)
            headers.pop("host", None)  # Remove host header
            
            # Transform request if configured
            if route_config.transform_request:
                headers, target_url = await route_config.transform_request(headers, target_url)
            
            # Make request
            start_time = time.time()
            
            response = await self.http_client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                timeout=route_config.timeout
            )
            
            # Update endpoint response time
            response_time = time.time() - start_time
            endpoint.response_time = (endpoint.response_time + response_time) / 2
            
            # Transform response if configured
            content = response.content
            if route_config.transform_response:
                content = await route_config.transform_response(content)
            
            return Response(
                content=content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        finally:
            # Decrement connection count
            endpoint.connection_count -= 1
    
    async def _retry_request(self, request: Request, route_config: RouteConfig, 
                           exclude_endpoint: Optional[ServiceEndpoint] = None) -> Response:
        """Retry request with different endpoint"""
        # TODO: Implement retry logic with exponential backoff
        raise HTTPException(status_code=502, detail="All retries exhausted")
    
    async def _health_check_loop(self):
        """Background health checking for service endpoints"""
        logger.info("🏥 Health check loop started")
        
        while True:
            try:
                for route_config in self.routes.values():
                    for endpoint in route_config.service_endpoints:
                        await self._check_endpoint_health(endpoint)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(5)
        
        logger.info("🏥 Health check loop stopped")
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """Check individual endpoint health"""
        if not endpoint.health_check_url or not self.http_client:
            return
        
        try:
            response = await self.http_client.get(
                endpoint.health_check_url,
                timeout=10.0
            )
            
            endpoint.is_healthy = response.status_code == 200
            endpoint.last_health_check = time.time()
            
        except Exception:
            endpoint.is_healthy = False
            endpoint.last_health_check = time.time()
    
    def add_route(self, route_config: RouteConfig):
        """Add route configuration"""
        route_key = f"{route_config.method}:{route_config.path}"
        self.routes[route_key] = route_config
        
        logger.info(f"➕ Route added: {route_key} -> {len(route_config.service_endpoints)} endpoints")
    
    def remove_route(self, path: str, method: str = "GET"):
        """Remove route configuration"""
        route_key = f"{method}:{path}"
        if route_key in self.routes:
            del self.routes[route_key]
            logger.info(f"➖ Route removed: {route_key}")
    
    def _update_response_time(self, response_time: float):
        """Update average response time"""
        total_requests = self.metrics.successful_requests + self.metrics.failed_requests
        
        if total_requests > 0:
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (total_requests - 1) + response_time)
                / total_requests
            )
    
    async def health_check(self) -> bool:
        """Perform API Gateway health check"""
        try:
            # Check HTTP client
            if not self.http_client:
                return False
            
            # Check rate limiter Redis connection
            if self.rate_limiter.redis_client:
                await self.rate_limiter.redis_client.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ API Gateway health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown API Gateway"""
        logger.info("🛑 Shutting down API Gateway")
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.http_client:
            await self.http_client.aclose()
        
        logger.info("✅ API Gateway shutdown completed")

# Global API Gateway instance
api_gateway_core = APIGatewayCore()

# Convenience functions
def add_gateway_route(route_config: RouteConfig):
    """Add route to API Gateway"""
    api_gateway_core.add_route(route_config)

def remove_gateway_route(path: str, method: str = "GET"):
    """Remove route from API Gateway"""
    api_gateway_core.remove_route(path, method)

async def start_gateway():
    """Start API Gateway"""
    return await api_gateway_core.initialize()

async def shutdown_gateway():
    """Shutdown API Gateway"""
    await api_gateway_core.shutdown()

# Module exports
__all__ = [
    "APIGatewayCore", "RouteConfig", "ServiceEndpoint", "GatewayConfig",
    "GatewayMetrics", "RoutingStrategy", "AuthenticationType", "RateLimiter",
    "CircuitBreaker", "api_gateway_core", "add_gateway_route", "remove_gateway_route",
    "start_gateway", "shutdown_gateway"
]