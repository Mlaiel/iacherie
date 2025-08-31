"""API Gateway Agent - Core Implementation

Enterprise-grade API Gateway providing intelligent request routing, load balancing,
security, monitoring, and service orchestration for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import json
import aiohttp
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram, Gauge

from ..base import BaseAgent, AgentStatus
from .config import APIGatewayConfig, LoadBalancingStrategy
from .request_router import RequestRouter
from .load_balancer import LoadBalancer
from .rate_limiter import RateLimiter
from .auth_middleware import AuthMiddleware
from .response_aggregator import ResponseAggregator
from .circuit_breaker import CircuitBreaker
from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'api_gateway_requests_total',
    'Total number of requests processed',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'api_gateway_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'api_gateway_active_connections',
    'Number of active connections'
)

UPSTREAM_HEALTH = Gauge(
    'api_gateway_upstream_health',
    'Health status of upstream services',
    ['service']
)


class APIGatewayAgent(BaseAgent):
    """    Enterprise API Gateway Agent
    
    Provides comprehensive API management including:
    - Intelligent request routing
    - Load balancing with multiple strategies
    - Rate limiting and throttling
    - Circuit breaker patterns
    - Authentication and authorization
    - Request/response transformation
    - Metrics collection and monitoring
    - Service discovery integration
    """    
    def __init__(self, config: Optional[APIGatewayConfig] = None):
        """Initialize API Gateway Agent"""        self.config = config or APIGatewayConfig()
        super().__init__(
            agent_id=f"api-gateway-{uuid.uuid4().hex[:8]}",
            agent_type="api_gateway_agent",
            config=self.config.dict()
        )
        
        # Initialize components
        self._initialize_components()
        
        # FastAPI application
        self.app = FastAPI(
            title="IA-Influencer API Gateway",
            description="Enterprise API Gateway for IA-Influencer-Agent Platform",
            version=self.config.version,
            docs_url="/docs" if self.config.debug else None,
            openapi_url="/openapi.json" if self.config.debug else None
        )
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
        # Service health tracking
        self.service_health: Dict[str, bool] = {}
        self.service_last_check: Dict[str, datetime] = {}
        
        logger.info(f"API Gateway Agent initialized with config: {self.config.service_name}")
    
    def _initialize_components(self):
        """Initialize all gateway components"""        try:
            # Request router
            self.router = RequestRouter(self.config)
            
            # Load balancer
            self.load_balancer = LoadBalancer(
                strategy=self.config.load_balancing_strategy,
                services=self.config.service_routes
            )
            
            # Rate limiter
            self.rate_limiter = RateLimiter(
                redis_url=self.config.redis_url,
                strategy=self.config.rate_limit_strategy,
                default_limit=self.config.default_rate_limit,
                window=self.config.rate_limit_window
            )
            
            # Authentication middleware
            self.auth_middleware = AuthMiddleware(
                secret_key=self.config.jwt_secret_key,
                algorithm=self.config.jwt_algorithm,
                bypass_paths=self.config.auth_bypass_paths
            )
            
            # Response aggregator
            self.response_aggregator = ResponseAggregator()
            
            # Circuit breaker
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=self.config.circuit_breaker_failure_threshold,
                timeout=self.config.circuit_breaker_timeout
            )
            
            # Metrics collector
            self.metrics_collector = MetricsCollector(
                enabled=self.config.metrics_enabled,
                prometheus_endpoint=self.config.prometheus_endpoint
            )
            
            # Redis connection
            self.redis = aioredis.from_url(self.config.redis_url)
            
            logger.info("All gateway components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gateway components: {e}")
            raise
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_methods=self.config.cors_methods,
            allow_headers=self.config.cors_headers,
            allow_credentials=True
        )
        
        # Custom middleware for request processing
        @self.app.middleware("http")
        async def process_request(request: Request, call_next):
            """Process incoming requests through gateway pipeline"""            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # Add request ID to headers
            request.state.request_id = request_id
            
            try:
                # Authentication check
                if not await self._is_auth_bypass_path(request.url.path):
                    await self.auth_middleware.authenticate_request(request)
                
                # Rate limiting check
                if not await self.rate_limiter.allow_request(request):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                # Process request
                response = await call_next(request)
                
                # Add response headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Gateway-Version"] = self.config.version
                
                # Record metrics
                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(duration)
                
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code
                ).inc()
                
                return response
                
            except HTTPException as e:
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=e.status_code
                ).inc()
                raise
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=500
                ).inc()
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _setup_routes(self):
        """Setup API routes"""        
        @self.app.get("/health")
        async def health_check():
            """Gateway health check endpoint"""            return {
                "status": "healthy",
                "version": self.config.version,
                "timestamp": datetime.utcnow().isoformat(),
                "services": await self._get_services_health()
            }
        
        @self.app.get("/metrics")
        async def metrics_endpoint():
            """Prometheus metrics endpoint"""            if not self.config.metrics_enabled:
                raise HTTPException(status_code=404, detail="Metrics disabled")
            return Response(
                content=self.metrics_collector.generate_metrics(),
                media_type="text/plain"
            )
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
        async def proxy_request(request: Request, path: str):
            """Main request proxying endpoint"""            return await self._proxy_request(request, path)
    
    async def _proxy_request(self, request: Request, path: str) -> Response:
        """Proxy request to appropriate upstream service"""        try:
            # Determine target service
            service_name = self.router.route_request(f"/{path}")
            if not service_name:
                raise HTTPException(status_code=404, detail="Service not found")
            
            # Get upstream URL
            upstream_url = await self.load_balancer.get_upstream(service_name)
            if not upstream_url:
                raise HTTPException(status_code=503, detail="Service unavailable")
            
            # Build target URL
            target_url = f"{upstream_url}/{path}"
            if request.query_params:
                target_url += f"?{request.query_params}"
            
            # Prepare request data
            headers = dict(request.headers)
            headers.update(self.config.request_transformations.get("add_headers", {}))
            
            # Remove unwanted headers
            for header in self.config.request_transformations.get("remove_headers", []):
                headers.pop(header, None)
            
            # Get request body
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
            
            # Make upstream request with circuit breaker
            response_data = await self.circuit_breaker.call(
                self._make_upstream_request,
                target_url, request.method, headers, body, service_name
            )
            
            return Response(
                content=response_data["content"],
                status_code=response_data["status_code"],
                headers=response_data["headers"],
                media_type=response_data.get("media_type")
            )
            
        except Exception as e:
            logger.error(f"Request proxying failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail="Upstream service error")
    
    async def _make_upstream_request(
        self, 
        url: str, 
        method: str, 
        headers: Dict[str, str], 
        body: Optional[bytes],
        service_name: str
    ) -> Dict[str, Any]:
        """Make request to upstream service"""        timeout = aiohttp.ClientTimeout(
            total=self.config.service_routes[service_name].get("timeout", 30)
        )
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=body
            ) as response:
                content = await response.read()
                response_headers = dict(response.headers)
                
                # Apply response transformations
                response_headers.update(
                    self.config.response_transformations.get("add_headers", {})
                )
                
                for header in self.config.response_transformations.get("remove_headers", []):
                    response_headers.pop(header, None)
                
                return {
                    "content": content,
                    "status_code": response.status,
                    "headers": response_headers,
                    "media_type": response.content_type
                }
    
    async def _is_auth_bypass_path(self, path: str) -> bool:
        """Check if path should bypass authentication"""        for bypass_path in self.config.auth_bypass_paths:
            if path.startswith(bypass_path):
                return True
        return False
    
    async def _get_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services"""        services_health = {}
        
        for service_name, config in self.config.service_routes.items():
            if not config.get("health_check", True):
                services_health[service_name] = {"status": "unknown", "reason": "health_check_disabled"}
                continue
            
            try:
                health_url = f"{config['upstream']}{self.config.service_health_check_endpoint}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        health_url, 
                        timeout=aiohttp.ClientTimeout(total=self.config.health_check_timeout)
                    ) as response:
                        if response.status == 200:
                            services_health[service_name] = {
                                "status": "healthy",
                                "last_check": datetime.utcnow().isoformat(),
                                "response_time": response.headers.get("X-Response-Time")
                            }
                            UPSTREAM_HEALTH.labels(service=service_name).set(1)
                        else:
                            services_health[service_name] = {
                                "status": "unhealthy",
                                "reason": f"HTTP {response.status}",
                                "last_check": datetime.utcnow().isoformat()
                            }
                            UPSTREAM_HEALTH.labels(service=service_name).set(0)
            
            except Exception as e:
                services_health[service_name] = {
                    "status": "unhealthy",
                    "reason": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                UPSTREAM_HEALTH.labels(service=service_name).set(0)
        
        return services_health
    
    async def start(self) -> None:
        """Start the API Gateway Agent"""        try:
            self.status = AgentStatus.INITIALIZING
            
            # Start background tasks
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._metrics_collection_loop())
            
            self.status = AgentStatus.RUNNING
            logger.info(f"API Gateway Agent started on {self.config.host}:{self.config.port}")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Failed to start API Gateway Agent: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the API Gateway Agent"""        try:
            self.status = AgentStatus.STOPPING
            
            # Close Redis connection
            if hasattr(self, 'redis'):
                await self.redis.close()
            
            self.status = AgentStatus.STOPPED
            logger.info("API Gateway Agent stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping API Gateway Agent: {e}")
            self.status = AgentStatus.ERROR
    
    async def _health_check_loop(self):
        """Background health checking loop"""        while self.status == AgentStatus.RUNNING:
            try:
                await self._get_services_health()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""        while self.status == AgentStatus.RUNNING:
            try:
                # Update active connections gauge
                # This would typically come from the server
                ACTIVE_CONNECTIONS.set(0)  # Placeholder
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(60)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive gateway statistics"""        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "version": self.config.version,
            "uptime": (datetime.utcnow() - self.created_at).total_seconds(),
            "configuration": {
                "load_balancing_strategy": self.config.load_balancing_strategy.value,
                "rate_limit_strategy": self.config.rate_limit_strategy.value,
                "services_count": len(self.config.service_routes),
                "rate_limit": self.config.default_rate_limit,
                "circuit_breaker_threshold": self.config.circuit_breaker_failure_threshold
            },
            "runtime_stats": {
                "active_connections": 0,  # Would be updated by server
                "total_requests": 0,      # Would be updated by metrics
                "error_rate": 0.0         # Would be calculated from metrics
            }
        }
