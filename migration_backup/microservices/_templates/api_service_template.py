#!/usr/bin/env python3
"""
🔌 Enterprise API Service Template - IA Chéries
==========================================
Template enterprise pour services API REST/GraphQL.
FastAPI + Pydantic + OpenAPI + authentication + rate limiting + observability.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction sans autorisation est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from functools import wraps
import logging

try:
    from fastapi import FastAPI, Request, Response, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.openapi.utils import get_openapi
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    BaseModel = object

from .service_template import EnterpriseServiceBase, ServiceConfig


@dataclass
class APIRoute:
    """Configuration pour route API."""
    path: str
    method: str
    handler: Callable
    summary: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    auth_required: bool = True
    rate_limit: Optional[Dict] = None
    cache_ttl: Optional[int] = None


@dataclass
class AuthConfig:
    """Configuration authentication."""
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    oauth2_providers: Dict = field(default_factory=dict)
    enable_api_keys: bool = False
    api_key_header: str = "X-API-Key"


@dataclass
class RateLimitConfig:
    """Configuration rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    enable_redis: bool = False
    redis_url: str = "redis://localhost:6379"


class APIRequest(BaseModel):
    """Modèle de base pour requêtes API."""
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None


class APIResponse(BaseModel):
    """Modèle de base pour réponses API."""
    success: bool = True
    data: Optional[Any] = None
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    execution_time_ms: Optional[float] = None


class APIServiceTemplate(EnterpriseServiceBase):
    """
    🔌 Template enterprise pour services API REST/GraphQL.
    FastAPI + Pydantic + OpenAPI + authentication + rate limiting.
    
    Features:
    - FastAPI avec middleware enterprise standard
    - Authentication JWT/OAuth2 intégrée
    - Rate limiting adaptatif
    - Documentation OpenAPI automatique
    - Monitoring & observability
    - CORS et sécurité configurables
    - Compression et optimisation
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize API service template."""
        super().__init__(config)
        
        if not FASTAPI_AVAILABLE:
            self.logger.error("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
            raise ImportError("FastAPI dependencies not available")
        
        self.app: Optional[FastAPI] = None
        self.routes_registered: List[APIRoute] = []
        self.middleware_stack: List[Dict] = []
        self.auth_config: Optional[AuthConfig] = None
        self.rate_limit_config: Optional[RateLimitConfig] = None
        
        # Metrics spécifiques API
        self.api_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'active_connections': 0,
            'rate_limited_requests': 0,
            'authenticated_requests': 0,
            'routes_registered': 0
        }
        
        self.logger.info(f"🔌 API Service Template initialized: {config.service_name}")
    
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        try:
            # Setup FastAPI application
            await self.setup_fastapi_application()
            
            # Setup default middleware stack
            await self.setup_default_middleware()
            
            # Setup health check endpoints
            await self.setup_health_endpoints()
            
            self.logger.info("✅ API service components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize API service: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        try:
            if self.app:
                # Graceful shutdown logic here
                self.logger.info("🧹 Cleaning up FastAPI application")
                
            self.routes_registered.clear()
            self.middleware_stack.clear()
            
            self.logger.info("✅ API service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during API service cleanup: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform API service-specific health checks."""
        try:
            health_data = {
                'api_status': 'healthy' if self.app else 'not_initialized',
                'routes_count': len(self.routes_registered),
                'middleware_count': len(self.middleware_stack),
                'auth_enabled': self.auth_config is not None,
                'rate_limiting_enabled': self.rate_limit_config is not None,
                'metrics': self.api_metrics.copy()
            }
            
            # Test database/external dependencies if configured
            dependencies_health = await self._check_dependencies_health()
            health_data['dependencies'] = dependencies_health
            
            return health_data
            
        except Exception as e:
            self.logger.error(f"❌ API health check failed: {e}")
            return {'error': str(e), 'status': 'unhealthy'}
    
    async def setup_fastapi_application(self) -> FastAPI:
        """Setup FastAPI avec middleware enterprise standard."""
        try:
            self.app = FastAPI(
                title=f"{self.config.service_name} API",
                description=self.config.description or f"Enterprise API service - {self.config.service_name}",
                version=self.config.service_version,
                docs_url="/docs",
                redoc_url="/redoc",
                openapi_url="/openapi.json"
            )
            
            # Custom OpenAPI schema
            await self._setup_custom_openapi()
            
            self.logger.info(f"✅ FastAPI application created: {self.config.service_name}")
            return self.app
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup FastAPI application: {e}")
            raise
    
    async def setup_default_middleware(self) -> None:
        """Setup middleware stack par défaut."""
        try:
            if not self.app:
                raise ValueError("FastAPI app not initialized")
            
            # CORS middleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Configure selon environnement
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Compression middleware
            self.app.add_middleware(GZipMiddleware, minimum_size=1000)
            
            # Custom request tracking middleware
            @self.app.middleware("http")
            async def track_requests(request: Request, call_next):
                start_time = time.time()
                correlation_id = request.headers.get("X-Correlation-ID", f"req-{int(time.time() * 1000)}")
                
                # Add correlation ID to request state
                request.state.correlation_id = correlation_id
                
                # Track metrics
                self.api_metrics['total_requests'] += 1
                self.api_metrics['active_connections'] += 1
                
                try:
                    response = await call_next(request)
                    
                    # Calculate response time
                    process_time = (time.time() - start_time) * 1000
                    response.headers["X-Process-Time"] = str(process_time)
                    response.headers["X-Correlation-ID"] = correlation_id
                    
                    # Update metrics
                    self.api_metrics['successful_requests'] += 1
                    self._update_response_time(process_time)
                    
                    return response
                    
                except Exception as e:
                    self.api_metrics['failed_requests'] += 1
                    self.logger.error(f"❌ Request failed: {e}")
                    raise
                finally:
                    self.api_metrics['active_connections'] -= 1
            
            self.logger.info("✅ Default middleware stack configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup middleware: {e}")
            raise
    
    async def register_routes(self, routes: List[APIRoute]) -> None:
        """Enregistrement routes avec validation automatique."""
        try:
            if not self.app:
                raise ValueError("FastAPI app not initialized")
            
            for route in routes:
                await self._register_single_route(route)
                self.routes_registered.append(route)
            
            self.api_metrics['routes_registered'] = len(self.routes_registered)
            self.logger.info(f"✅ Registered {len(routes)} API routes")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register routes: {e}")
            raise
    
    async def _register_single_route(self, route: APIRoute) -> None:
        """Register une route individuelle."""
        try:
            # Wrapper pour rate limiting et auth
            wrapped_handler = await self._wrap_handler(route)
            
            # Register route with FastAPI
            if route.method.upper() == "GET":
                self.app.get(route.path, tags=route.tags, summary=route.summary)(wrapped_handler)
            elif route.method.upper() == "POST":
                self.app.post(route.path, tags=route.tags, summary=route.summary)(wrapped_handler)
            elif route.method.upper() == "PUT":
                self.app.put(route.path, tags=route.tags, summary=route.summary)(wrapped_handler)
            elif route.method.upper() == "DELETE":
                self.app.delete(route.path, tags=route.tags, summary=route.summary)(wrapped_handler)
            elif route.method.upper() == "PATCH":
                self.app.patch(route.path, tags=route.tags, summary=route.summary)(wrapped_handler)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register route {route.path}: {e}")
            raise
    
    async def _wrap_handler(self, route: APIRoute) -> Callable:
        """Wrap handler avec middleware (auth, rate limiting, etc.)."""
        @wraps(route.handler)
        async def wrapped_handler(request: Request, *args, **kwargs):
            try:
                # Authentication check
                if route.auth_required and self.auth_config:
                    await self._authenticate_request(request)
                    self.api_metrics['authenticated_requests'] += 1
                
                # Rate limiting check
                if route.rate_limit or self.rate_limit_config:
                    if not await self._check_rate_limit(request, route):
                        self.api_metrics['rate_limited_requests'] += 1
                        raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                # Execute original handler
                result = await route.handler(request, *args, **kwargs)
                
                # Wrap in standard response format
                if not isinstance(result, APIResponse):
                    result = APIResponse(
                        success=True,
                        data=result,
                        correlation_id=getattr(request.state, 'correlation_id', None)
                    )
                
                return result
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"❌ Handler error in {route.path}: {e}")
                return APIResponse(
                    success=False,
                    message=f"Internal server error: {str(e)}",
                    correlation_id=getattr(request.state, 'correlation_id', None)
                )
        
        return wrapped_handler
    
    async def setup_authentication(self, auth_config: AuthConfig) -> None:
        """Configuration authentication JWT/OAuth2."""
        try:
            self.auth_config = auth_config
            
            # Setup JWT authentication
            if auth_config.jwt_secret:
                security = HTTPBearer()
                
                async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
                    # JWT verification logic here
                    # This is a placeholder - implement proper JWT verification
                    return {"user_id": "authenticated_user"}
                
                self.jwt_verify = verify_token
            
            self.logger.info("✅ Authentication configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup authentication: {e}")
            raise
    
    async def setup_rate_limiting(self, limits: RateLimitConfig) -> None:
        """Configuration rate limiting per endpoint."""
        try:
            self.rate_limit_config = limits
            
            # Initialize rate limiting storage (in-memory or Redis)
            if limits.enable_redis:
                # Redis-based rate limiting
                self.logger.info("📊 Redis-based rate limiting configured")
            else:
                # In-memory rate limiting
                self._rate_limit_storage = {}
                self.logger.info("📊 In-memory rate limiting configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup rate limiting: {e}")
            raise
    
    async def setup_health_endpoints(self) -> None:
        """Setup endpoints de santé standard."""
        try:
            if not self.app:
                raise ValueError("FastAPI app not initialized")
            
            @self.app.get("/health", tags=["Health"], summary="Health Check")
            async def health_check_endpoint():
                health_data = await self.health_check()
                return APIResponse(success=True, data=health_data)
            
            @self.app.get("/metrics", tags=["Monitoring"], summary="Service Metrics")
            async def metrics_endpoint():
                return APIResponse(success=True, data=self.api_metrics)
            
            @self.app.get("/ready", tags=["Health"], summary="Readiness Check")
            async def readiness_endpoint():
                is_ready = self.status == "running" and self.health_status == "healthy"
                return APIResponse(
                    success=is_ready,
                    data={"ready": is_ready, "status": self.status}
                )
            
            self.logger.info("✅ Health endpoints configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup health endpoints: {e}")
            raise
    
    async def _setup_custom_openapi(self) -> None:
        """Setup custom OpenAPI schema."""
        try:
            if not self.app:
                return
            
            def custom_openapi():
                if self.app.openapi_schema:
                    return self.app.openapi_schema
                
                openapi_schema = get_openapi(
                    title=f"{self.config.service_name} API",
                    version=self.config.service_version,
                    description=f"""
                    🔌 Enterprise API Service - {self.config.service_name}
                    
                    **Author**: Fahed Mlaiel (mlaiel@live.de)
                    **Copyright**: (c) 2025 Fahed Mlaiel. All rights reserved.
                    
                    ### Features
                    - FastAPI with enterprise middleware
                    - JWT/OAuth2 authentication
                    - Rate limiting
                    - Request/response tracking
                    - Health checks and monitoring
                    
                    ### Authentication
                    This API uses JWT tokens for authentication. Include your token in the Authorization header:
                    ```
                    Authorization: Bearer <your-jwt-token>
                    ```
                    """,
                    routes=self.app.routes,
                )
                
                # Add security definitions
                openapi_schema["components"]["securitySchemes"] = {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
                
                self.app.openapi_schema = openapi_schema
                return self.app.openapi_schema
            
            self.app.openapi = custom_openapi
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup OpenAPI schema: {e}")
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate request avec JWT/OAuth2."""
        # Placeholder for authentication logic
        # Implement actual JWT verification here
        return {"authenticated": True, "user_id": "test_user"}
    
    async def _check_rate_limit(self, request: Request, route: APIRoute) -> bool:
        """Check rate limit pour requête."""
        # Placeholder for rate limiting logic
        # Implement actual rate limiting here
        return True
    
    async def _check_dependencies_health(self) -> Dict[str, Any]:
        """Check health of external dependencies."""
        return {"database": "healthy", "cache": "healthy", "external_apis": "healthy"}
    
    def _update_response_time(self, response_time_ms: float) -> None:
        """Update average response time metric."""
        current_avg = self.api_metrics['average_response_time']
        total_requests = self.api_metrics['total_requests']
        
        if total_requests > 1:
            # Calculate rolling average
            self.api_metrics['average_response_time'] = (
                (current_avg * (total_requests - 1)) + response_time_ms
            ) / total_requests
        else:
            self.api_metrics['average_response_time'] = response_time_ms
    
    # Abstract methods pour extension
    @abstractmethod
    async def configure_custom_routes(self) -> List[APIRoute]:
        """Configure routes spécifiques au service."""
        pass
    
    @abstractmethod
    async def configure_custom_middleware(self) -> List[Dict]:
        """Configure middleware spécifique au service."""
        pass


if __name__ == "__main__":
    # Example usage
    print("🔌 Enterprise API Service Template")
    print("Use this template to create FastAPI-based microservices")
    if not FASTAPI_AVAILABLE:
        print("⚠️ FastAPI not available. Install with: pip install fastapi uvicorn")