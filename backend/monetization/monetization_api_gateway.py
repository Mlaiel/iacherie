"""
🌐 Monetization API Gateway - Unified API Gateway for Monetization Services
=========================================================================

Professional Module: Centralized API gateway for all monetization endpoints and services
Created by: Fahed Mlaiel (Lead Developer AI & Backend Senior & FinTech & DevOps Expert)
Role Combination: Lead Dev IA + Backend Senior + FinTech + DevOps + API Architecture

Technologies: FastAPI Gateway, Service Orchestration, API Management
Security: OAuth2, Rate Limiting, API Key Management, Request Validation
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import redis.asyncio as redis
from pydantic import BaseModel, ValidationError
import jwt

# Rate limiting
from collections import defaultdict, deque

class APIEndpoint(Enum):
    """APIEndpoint class implementation"""
    REVENUE_MANAGEMENT = "/api/v1/revenue"
    CONTENT_MONETIZATION = "/api/v1/content"
    PAYMENT_PROCESSING = "/api/v1/payments"
    SUBSCRIPTION_MANAGEMENT = "/api/v1/subscriptions"
    PAYOUT_AUTOMATION = "/api/v1/payouts"
    ANALYTICS_REPORTING = "/api/v1/analytics"
    COMPLIANCE_REPORTING = "/api/v1/compliance"
    BLOCKCHAIN_SERVICES = "/api/v1/blockchain"

class ServiceStatus(Enum):
    """ServiceStatus class implementation"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

@dataclass
class APIMetrics:
    """APIMetrics: class implementation"""
    endpoint: str
    requests_count: int
    average_response_time: float
    error_rate: float
    last_24h_requests: int

@dataclass
class ServiceHealth:
    """ServiceHealth: class implementation"""
    service_name: str
    status: ServiceStatus
    response_time_ms: float
    last_check: datetime
    error_count: int

class APIRequest(BaseModel):
    """APIRequest class implementation"""
    endpoint: str
    method: str
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel):
    """APIResponse class implementation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime
    request_id: str

class RateLimiter:
    """Advanced rate limiting with sliding window"""
    
    def __init__(self) -> None:
        self.requests = defaultdict(deque)
        self.limits = {
            "default": (100, 3600),    # 100 requests per hour
            "premium": (1000, 3600),   # 1000 requests per hour
            "enterprise": (10000, 3600) # 10000 requests per hour
        }
    
    def is_allowed(self, api_key: str, tier: str = "default") -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        limit, window = self.limits.get(tier, self.limits["default"])
        
        # Clean old requests
        while self.requests[api_key] and self.requests[api_key][0] <= now - window:
            self.requests[api_key].popleft()
        
        # Check if under limit
        if len(self.requests[api_key]) < limit:
            self.requests[api_key].append(now)
            return True
        
        return False

class MonetizationAPIGateway:
    """Unified API Gateway for all monetization services"""
    
    def __init__(self) -> None:
        self.app = FastAPI(
            title="Ainflue Monetization API Gateway",
            description="Unified gateway for all monetization services",
            version="2.0.0"
        )
        self.logger = logging.getLogger(__name__)
        self.redis_client = None
        self.rate_limiter = RateLimiter()
        self.security = HTTPBearer()
        
        # Service registry
        self.services = {
            "revenue_management": "http://revenue-service:8001",
            "content_monetization": "http://content-service:8002",
            "payment_processing": "http://payment-service:8003",
            "subscription_management": "http://subscription-service:8004",
            "payout_automation": "http://payout-service:8005",
            "analytics_reporting": "http://analytics-service:8006",
            "compliance_reporting": "http://compliance-service:8007",
            "blockchain_services": "http://blockchain-service:8008"
        }
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_middleware(self) -> None:
        """Configure API gateway middleware"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://ainflue.com", "https://api.ainflue.com"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["ainflue.com", "*.ainflue.com", "localhost"]
        )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request -> None: Request, call_next) -> None:
            start_time = time.time()
            
            # Log incoming request
            self.logger.info(f"Request: {request.method} {request.url}")
            
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            self.logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
            
            return response
    
    def _setup_routes(self) -> None:
        """Setup API gateway routes"""
        
        @self.app.get("/health")
        async def health_check() -> None:
            """Gateway health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.utcnow()}
        
        @self.app.get("/services/health")
        async def services_health() -> None:
            """Check health of all downstream services"""
            health_checks = await self.check_services_health()
            return {"services": health_checks, "timestamp": datetime.utcnow()}
        
        @self.app.get("/metrics")
        async def api_metrics() -> None:
            """Get API gateway metrics"""
            metrics = await self.get_api_metrics()
            return {"metrics": metrics, "timestamp": datetime.utcnow()}
        
        # Revenue Management Routes
        @self.app.api_route("/api/v1/revenue/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def revenue_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("revenue_management", request, path)
        
        # Content Monetization Routes
        @self.app.api_route("/api/v1/content/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def content_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("content_monetization", request, path)
        
        # Payment Processing Routes
        @self.app.api_route("/api/v1/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def payment_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("payment_processing", request, path)
        
        # Subscription Management Routes
        @self.app.api_route("/api/v1/subscriptions/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def subscription_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("subscription_management", request, path)
        
        # Payout Automation Routes
        @self.app.api_route("/api/v1/payouts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def payout_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("payout_automation", request, path)
        
        # Analytics Routes
        @self.app.api_route("/api/v1/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def analytics_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("analytics_reporting", request, path)
        
        # Compliance Routes
        @self.app.api_route("/api/v1/compliance/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def compliance_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("compliance_reporting", request, path)
        
        # Blockchain Routes
        @self.app.api_route("/api/v1/blockchain/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def blockchain_proxy(request -> None: Request, path -> None: str) -> None:
            return await self.proxy_request("blockchain_services", request, path)
    
    async def authenticate_request(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> Dict[str, Any]:
        """Authenticate API request"""
        try:
            token = credentials.credentials
            
            # Decode JWT token
            payload = jwt.decode(
                token,
                "your-secret-key",  # In production: use proper secret management
                algorithms=["HS256"]
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limits"""
        try:
            # Extract API key from headers
            api_key = request.headers.get("X-API-Key", "anonymous")
            
            # Determine tier based on API key (mock logic)
            tier = "premium" if "premium" in api_key else "default"
            
            # Check rate limit
            if not self.rate_limiter.is_allowed(api_key, tier):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request on error
    
    async def proxy_request(
        self,
        service_name: str,
        request: Request,
        path: str
    ) -> JSONResponse:
        """Proxy request to downstream service"""
        try:
            # Check rate limits
            await self.check_rate_limit(request)
            
            # Get service URL
            service_url = self.services.get(service_name)
            if not service_url:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service not found: {service_name}"
                )
            
            # Build target URL
            target_url = f"{service_url}/{path}"
            if request.query_params:
                target_url += f"?{request.query_params}"
            
            # Mock downstream service response
            mock_response = {
                "service": service_name,
                "path": path,
                "method": request.method,
                "status": "success",
                "data": {
                    "message": f"Response from {service_name}",
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
            
            # Log request
            self.logger.info(f"Proxying {request.method} {path} to {service_name}")
            
            return JSONResponse(content=mock_response)
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Proxy request failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal gateway error"
            )
    
    async def check_services_health(self) -> List[ServiceHealth]:
        """Check health of all downstream services"""
        health_checks = []
        
        for service_name, service_url in self.services.items():
            try:
                # Mock health check (in production: actual HTTP health check)
                start_time = time.time()
                await asyncio.sleep(0.01)  # Simulate network call
                response_time = (time.time() - start_time) * 1000
                
                # Simulate random service status
                import random
                statuses = [ServiceStatus.OPERATIONAL, ServiceStatus.DEGRADED]
                status = random.choice(statuses)
                
                health = ServiceHealth(
                    service_name=service_name,
                    status=status,
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    error_count=random.randint(0, 5)
                )
                
                health_checks.append(health)
                
            except Exception as e:
                health = ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.OFFLINE,
                    response_time_ms=0.0,
                    last_check=datetime.utcnow(),
                    error_count=1
                )
                health_checks.append(health)
                self.logger.error(f"Health check failed for {service_name}: {e}")
        
        return health_checks
    
    async def get_api_metrics(self) -> List[APIMetrics]:
        """Get API gateway metrics"""
        try:
            # Mock metrics (in production: get from Redis/monitoring system)
            metrics = [
                APIMetrics(
                    endpoint="/api/v1/revenue",
                    requests_count=1250,
                    average_response_time=125.5,
                    error_rate=0.02,
                    last_24h_requests=1250
                ),
                APIMetrics(
                    endpoint="/api/v1/payments",
                    requests_count=980,
                    average_response_time=89.3,
                    error_rate=0.01,
                    last_24h_requests=980
                ),
                APIMetrics(
                    endpoint="/api/v1/analytics",
                    requests_count=654,
                    average_response_time=234.7,
                    error_rate=0.03,
                    last_24h_requests=654
                )
            ]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get API metrics: {e}")
            return []
    
    async def log_api_request(
        self,
        request -> None: APIRequest,
        response -> None: APIResponse,
        processing_time -> None: float
    ) -> None:
        """Log API request for analytics"""
        try:
            log_entry = {
                "request_id": response.request_id,
                "endpoint": request.endpoint,
                "method": request.method,
                "user_id": request.user_id,
                "processing_time": processing_time,
                "success": response.success,
                "timestamp": response.timestamp.isoformat()
            }
            
            # Store in Redis for analytics
            if self.redis_client:
                await self.redis_client.lpush(
                    "api_logs",
                    json.dumps(log_entry)
                )
            
        except Exception as e:
            self.logger.error(f"Failed to log API request: {e}")
    
    def create_app(self) -> FastAPI:
        """Create and return FastAPI application"""
        return self.app

# Gateway instance
gateway = MonetizationAPIGateway()
app = gateway.create_app()

__all__ = [
    'MonetizationAPIGateway',
    'APIRequest',
    'APIResponse',
    'APIMetrics',
    'ServiceHealth',
    'RateLimiter',
    'app'
]
