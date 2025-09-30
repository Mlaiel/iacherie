"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

REST API Template for Ainflue Microservices Platform
===================================================

Enterprise-grade REST API service template providing:
- FastAPI framework with advanced features
- OpenAPI/Swagger documentation
- Request validation and serialization
- Response caching and compression
- Rate limiting and throttling
- Authentication and authorization
- CORS and security headers
- Health checks and monitoring
- Database integration
- Background task processing

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & API Specialist
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Type
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.background import BackgroundTasks
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from prometheus_client import Counter, Histogram

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig

logger = logging.getLogger(__name__)


class ApiResponse(BaseModel):
    """Standard API response model"""
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Response message")
    errors: Optional[List[str]] = Field(default=None, description="Error messages")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Base filter parameters"""
    search: Optional[str] = Field(default=None, description="Search query")
    created_after: Optional[datetime] = Field(default=None, description="Created after date")
    created_before: Optional[datetime] = Field(default=None, description="Created before date")
    status: Optional[str] = Field(default=None, description="Status filter")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    requests_per_minute: int = Field(default=60, description="Requests per minute")
    requests_per_hour: int = Field(default=1000, description="Requests per hour")
    burst_limit: int = Field(default=100, description="Burst limit")
    enable_per_user_limits: bool = Field(default=True, description="Enable per-user limits")


class CacheConfig(BaseModel):
    """Caching configuration"""
    enable_response_cache: bool = Field(default=True, description="Enable response caching")
    default_cache_ttl: int = Field(default=300, description="Default cache TTL in seconds")
    cache_prefix: str = Field(default="api", description="Cache key prefix")
    enable_etag: bool = Field(default=True, description="Enable ETag headers")


class SecurityConfig(BaseModel):
    """Security configuration"""
    enable_https_redirect: bool = Field(default=True, description="Enable HTTPS redirect")
    enable_security_headers: bool = Field(default=True, description="Enable security headers")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed hosts")
    enable_request_logging: bool = Field(default=True, description="Enable request logging")


class RestApiConfig(ServiceConfig):
    """REST API specific configuration"""
    api_title: str = Field(default="Ainflue API Service", description="API title")
    api_description: str = Field(default="Enterprise REST API service", description="API description")
    api_version: str = Field(default="1.0.0", description="API version")
    docs_url: str = Field(default="/docs", description="Documentation URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI schema URL")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig, description="Rate limiting config")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Caching config")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security config")
    enable_background_tasks: bool = Field(default=True, description="Enable background tasks")
    max_request_size: int = Field(default=10*1024*1024, description="Maximum request size in bytes")


class AuthenticationError(HTTPException):
    """Authentication error"""
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """Authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationError(HTTPException):
    """Validation error"""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class RateLimitExceeded(HTTPException):
    """Rate limit exceeded error"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class RestApiTemplate(BaseMicroservice):
    """
    Enterprise REST API service template
    
    Provides comprehensive REST API functionality including:
    - FastAPI framework with advanced configuration
    - Automatic OpenAPI/Swagger documentation
    - Request validation and response serialization
    - Rate limiting and throttling
    - Response caching with Redis
    - Authentication and authorization
    - CORS and security middleware
    - Background task processing
    - Database integration patterns
    - Monitoring and metrics collection
    - Error handling and logging
    - Health checks and status endpoints
    """
    
    def __init__(self, config: RestApiConfig):
        """Initialize REST API service"""
        # Override FastAPI app configuration
        self.api_config = config
        
        # Call parent constructor with modified config
        super().__init__(config)
        
        # Reconfigure FastAPI app with API-specific settings
        self.app = FastAPI(
            title=config.api_title,
            description=config.api_description,
            version=config.api_version,
            docs_url=config.docs_url,
            redoc_url=config.redoc_url,
            openapi_url=config.openapi_url,
            debug=config.debug
        )
        
        # API-specific components
        self.cache_client: Optional[redis.Redis] = None
        self.rate_limiter: Optional[Dict[str, Any]] = None
        self.background_tasks_queue: Optional[List[Callable]] = []
        
        # Request/response tracking
        self.request_counter = Counter(
            f"{config.name.replace('-', '_')}_api_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"]
        )
        
        self.request_duration = Histogram(
            f"{config.name.replace('-', '_')}_api_request_duration_seconds",
            "API request duration",
            ["method", "endpoint"]
        )
        
        # Re-setup with API-specific middleware and routes
        self._setup_api_middleware()
        self._setup_api_routes()
        
        logger.info(f"REST API service initialized: {config.api_title}")
    
    def _setup_api_middleware(self):
        """Setup API-specific middleware"""
        # Security headers middleware
        if self.api_config.security.enable_security_headers:
            @self.app.middleware("http")
            async def security_headers_middleware(request: Request, call_next):
                response = await call_next(request)
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                return response
        
        # Trusted host middleware
        if self.api_config.security.allowed_hosts != ["*"]:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=self.api_config.security.allowed_hosts
            )
        
        # Rate limiting middleware
        @self.app.middleware("http")
        async def rate_limiting_middleware(request: Request, call_next):
            # Check rate limits
            if await self._check_rate_limit(request):
                response = await call_next(request)
                return response
            else:
                raise RateLimitExceeded()
        
        # Request logging middleware
        if self.api_config.security.enable_request_logging:
            @self.app.middleware("http")
            async def request_logging_middleware(request: Request, call_next):
                start_time = datetime.utcnow()
                
                # Log request
                logger.info(f"API Request: {request.method} {request.url}")
                
                response = await call_next(request)
                
                # Log response
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"API Response: {response.status_code} ({duration:.3f}s)")
                
                return response
        
        # Caching middleware
        if self.api_config.cache.enable_response_cache:
            @self.app.middleware("http")
            async def caching_middleware(request: Request, call_next):
                # Only cache GET requests
                if request.method != "GET":
                    return await call_next(request)
                
                # Check cache
                cache_key = self._generate_cache_key(request)
                cached_response = await self._get_cached_response(cache_key)
                
                if cached_response:
                    return JSONResponse(content=cached_response)
                
                # Process request
                response = await call_next(request)
                
                # Cache successful responses
                if response.status_code == 200:
                    await self._cache_response(cache_key, response)
                
                return response
    
    def _setup_api_routes(self):
        """Setup API-specific routes"""
        
        @self.app.get("/api/v1/status", response_model=ApiResponse)
        async def api_status():
            """API status endpoint"""
            return ApiResponse(
                success=True,
                data={
                    "service": self.config.name,
                    "version": self.api_config.api_version,
                    "status": self.status.value,
                    "timestamp": datetime.utcnow().isoformat()
                },
                message="API is operational"
            )
        
        @self.app.get("/api/v1/health", response_model=ApiResponse)
        async def api_health():
            """API health check endpoint"""
            health_status = await self.get_health_status()
            
            return ApiResponse(
                success=health_status.status == ServiceStatus.HEALTHY,
                data=health_status.dict(),
                message=f"Service is {health_status.status.value}"
            )
        
        @self.app.get("/api/v1/metrics", response_model=ApiResponse)
        async def api_metrics():
            """API metrics endpoint"""
            metrics_data = {
                "requests_total": self.metrics.requests_total,
                "requests_success": self.metrics.requests_success,
                "requests_failed": self.metrics.requests_failed,
                "response_time_avg": self.metrics.response_time_avg,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "active_connections": self.metrics.active_connections
            }
            
            return ApiResponse(
                success=True,
                data=metrics_data,
                message="Metrics retrieved successfully"
            )
        
        # Add custom API routes
        self.register_api_routes()
    
    def register_api_routes(self):
        """Register custom API routes - override in concrete implementation"""
        
        @self.app.post("/api/v1/example", response_model=ApiResponse)
        async def example_endpoint(
            request_data: Dict[str, Any],
            background_tasks: BackgroundTasks
        ):
            """Example API endpoint"""
            try:
                # Process request
                result = await self._process_api_request(request_data)
                
                # Add background task if enabled
                if self.api_config.enable_background_tasks:
                    background_tasks.add_task(self._example_background_task, request_data)
                
                return ApiResponse(
                    success=True,
                    data=result,
                    message="Request processed successfully"
                )
                
            except Exception as e:
                logger.error(f"API request failed: {str(e)}")
                return ApiResponse(
                    success=False,
                    errors=[str(e)],
                    message="Request processing failed"
                )
        
        @self.app.get("/api/v1/items", response_model=ApiResponse)
        async def list_items(
            pagination: PaginationParams = Depends(),
            filters: FilterParams = Depends()
        ):
            """List items with pagination and filtering"""
            try:
                items = await self._get_items_list(pagination, filters)
                
                return ApiResponse(
                    success=True,
                    data=items["items"],
                    metadata={
                        "pagination": {
                            "page": pagination.page,
                            "size": pagination.size,
                            "total": items["total"],
                            "pages": (items["total"] + pagination.size - 1) // pagination.size
                        },
                        "filters": filters.dict(exclude_none=True)
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to list items: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve items")
    
    async def _check_rate_limit(self, request: Request) -> bool:
        """Check rate limit for request"""
        if not self.cache_client:
            return True  # Allow if no cache available
        
        # Get client identifier (IP or user ID)
        client_id = self._get_client_identifier(request)
        
        # Check rate limits
        minute_key = f"rate_limit:minute:{client_id}"
        hour_key = f"rate_limit:hour:{client_id}"
        
        try:
            # Get current counts
            minute_count = await self.cache_client.get(minute_key) or 0
            hour_count = await self.cache_client.get(hour_key) or 0
            
            minute_count = int(minute_count)
            hour_count = int(hour_count)
            
            # Check limits
            if minute_count >= self.api_config.rate_limit.requests_per_minute:
                return False
            
            if hour_count >= self.api_config.rate_limit.requests_per_hour:
                return False
            
            # Increment counters
            pipe = self.cache_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            await pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return True  # Allow on error
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from authentication
        auth_header = request.headers.get("Authorization")
        if auth_header:
            # Parse user ID from token (simplified)
            return f"user:{auth_header[-8:]}"
        
        # Fall back to IP address
        client_ip = request.client.host
        return f"ip:{client_ip}"
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        key_parts = [
            self.api_config.cache.cache_prefix,
            request.method,
            str(request.url.path),
            str(request.url.query)
        ]
        return ":".join(key_parts)
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        if not self.cache_client:
            return None
        
        try:
            cached_data = await self.cache_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache retrieval failed: {str(e)}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: Response):
        """Cache response"""
        if not self.cache_client:
            return
        
        try:
            # Only cache JSON responses
            if response.headers.get("content-type", "").startswith("application/json"):
                response_data = json.loads(response.body)
                
                await self.cache_client.setex(
                    cache_key,
                    self.api_config.cache.default_cache_ttl,
                    json.dumps(response_data)
                )
        except Exception as e:
            logger.error(f"Cache storage failed: {str(e)}")
    
    async def _process_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API request - override in concrete implementation"""
        # Example processing logic
        return {
            "processed": True,
            "request_id": str(datetime.utcnow().timestamp()),
            "data": request_data
        }
    
    async def _get_items_list(self, pagination: PaginationParams, filters: FilterParams) -> Dict[str, Any]:
        """Get items list with pagination and filtering - override in concrete implementation"""
        # Example implementation
        items = []
        total = 0
        
        # Apply filters and pagination logic here
        # This would typically query a database
        
        return {
            "items": items,
            "total": total
        }
    
    async def _example_background_task(self, data: Dict[str, Any]):
        """Example background task"""
        logger.info(f"Processing background task with data: {data}")
        await asyncio.sleep(1)  # Simulate processing
        logger.info("Background task completed")
    
    # Override abstract methods from BaseMicroservice
    
    async def initialize_service(self):
        """Initialize REST API service"""
        # Initialize cache client
        if hasattr(self, '_redis_config'):
            self.cache_client = redis.Redis(
                host=self._redis_config.get('host', 'localhost'),
                port=self._redis_config.get('port', 6379),
                password=self._redis_config.get('password'),
                decode_responses=True
            )
            await self.cache_client.ping()
            logger.info("Cache client initialized")
        
        logger.info(f"REST API service {self.config.name} initialized")
    
    async def cleanup_service(self):
        """Cleanup REST API service"""
        if self.cache_client:
            await self.cache_client.close()
        logger.info(f"REST API service {self.config.name} cleaned up")
    
    def register_routes(self):
        """Register service-specific routes"""
        # Routes are registered in _setup_api_routes
        pass
    
    async def register_service(self):
        """Register service with service discovery"""
        logger.info(f"REST API service {self.config.name} registered")
    
    async def deregister_service(self):
        """Deregister service from service discovery"""
        logger.info(f"REST API service {self.config.name} deregistered")
    
    async def get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        return f"http://{service_name}:8000"
    
    async def start_background_tasks(self):
        """Start background tasks"""
        if self.api_config.enable_background_tasks:
            logger.info("Background task processing enabled")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        logger.info("Background task processing stopped")


def create_rest_api_service(
    service_name: str = "rest-api-service",
    api_title: str = "Ainflue REST API",
    api_description: str = "Enterprise REST API service for Ainflue platform"
) -> RestApiTemplate:
    """Factory function to create REST API service"""
    
    config = RestApiConfig(
        name=service_name,
        api_title=api_title,
        api_description=api_description,
        port=8000,
        enable_cors=True,
        enable_gzip=True,
        enable_metrics=True
    )
    
    return RestApiTemplate(config)


if __name__ == "__main__":
    # Example usage
    service = create_rest_api_service()
    service.run()