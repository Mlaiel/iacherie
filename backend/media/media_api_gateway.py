"""Media API Gateway - Advanced API Gateway & Service Orchestration System
========================================================================

Advanced API gateway providing unified access to all media services, intelligent routing,
authentication, rate limiting, caching, and comprehensive API management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary API gateway system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or API gateway logic appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import time
import hashlib
import jwt
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from collections import defaultdict, deque
import re

# Web framework and HTTP imports with graceful fallbacks
try:
    from fastapi import FastAPI, Request, Response, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    logging.warning("FastAPI not available - limited API gateway functionality")

try:
    import aiohttp
    import aioredis
    HAS_ASYNC_CLIENTS = True
except ImportError:
    HAS_ASYNC_CLIENTS = False
    logging.warning("Async HTTP clients not available - using basic implementations")

try:
    import prometheus_client
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logging.warning("Prometheus client not available - using basic metrics")

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods"""
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    NONE = "none"


class RouteStrategy(Enum):
    """Routing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    HEALTH_BASED = "health_based"
    LEAST_CONNECTIONS = "least_connections"
    HASH_BASED = "hash_based"


class CacheStrategy(Enum):
    """Caching strategies"""
    NO_CACHE = "no_cache"
    TIME_BASED = "time_based"
    CONTENT_BASED = "content_based"
    CONDITIONAL = "conditional"
    AGGRESSIVE = "aggressive"


class RateLimitType(Enum):
    """Rate limiting types"""
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    BANDWIDTH_PER_MINUTE = "bandwidth_per_minute"
    CONCURRENT_REQUESTS = "concurrent_requests"


@dataclass
class GatewayConfig:
    """API Gateway configuration"""
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Security settings
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_https: bool = True
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Rate limiting
    default_rate_limit: int = 1000  # requests per hour
    burst_limit: int = 100  # burst requests
    
    # Caching
    enable_caching: bool = True
    default_cache_ttl: int = 300  # seconds
    max_cache_size: int = 1000  # entries
    
    # Load balancing
    default_route_strategy: RouteStrategy = RouteStrategy.ROUND_ROBIN
    health_check_interval: int = 30  # seconds
    
    # Monitoring
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    service_id: str
    name: str
    base_url: str
    health_check_path: str = "/health"
    weight: int = 100
    timeout_seconds: int = 30
    max_retries: int = 3
    is_healthy: bool = True
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    active_connections: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Route:
    """API route configuration"""
    route_id: str
    path_pattern: str
    methods: List[str]
    service_endpoints: List[ServiceEndpoint]
    auth_method: AuthMethod = AuthMethod.JWT
    rate_limit: Optional[int] = None
    cache_strategy: CacheStrategy = CacheStrategy.TIME_BASED
    cache_ttl: int = 300
    route_strategy: RouteStrategy = RouteStrategy.ROUND_ROBIN
    middleware: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIRequest:
    """API request information"""
    request_id: str
    path: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[bytes] = None
    client_ip: str = ""
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APIResponse:
    """API response information"""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[bytes] = None
    response_time_ms: float = 0.0
    cache_hit: bool = False
    service_endpoint: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    rule_id: str
    identifier: str  # IP, user_id, api_key
    limit_type: RateLimitType
    limit_value: int
    window_size: int  # seconds
    current_count: int = 0
    window_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_blocked: bool = False


class AuthenticationManager:
    """Handles authentication and authorization"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.jwt_secret = config.jwt_secret
        self.jwt_algorithm = config.jwt_algorithm
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("🔐 Authentication Manager initialized")
    
    async def authenticate_request(self, request: APIRequest, auth_method: AuthMethod) -> Dict[str, Any]:
        """Authenticate API request"""
        try:
            if auth_method == AuthMethod.NONE:
                return {'authenticated': True, 'user_id': 'anonymous'}
            
            elif auth_method == AuthMethod.JWT:
                return await self._authenticate_jwt(request)
            
            elif auth_method == AuthMethod.API_KEY:
                return await self._authenticate_api_key(request)
            
            elif auth_method == AuthMethod.OAUTH2:
                return await self._authenticate_oauth2(request)
            
            elif auth_method == AuthMethod.BASIC:
                return await self._authenticate_basic(request)
            
            else:
                return {'authenticated': False, 'error': 'Unsupported auth method'}
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {'authenticated': False, 'error': str(e)}
    
    async def _authenticate_jwt(self, request: APIRequest) -> Dict[str, Any]:
        """Authenticate using JWT token"""
        try:
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return {'authenticated': False, 'error': 'Missing or invalid Bearer token'}
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check expiration
            if 'exp' in payload:
                if datetime.fromtimestamp(payload['exp'], timezone.utc) < datetime.now(timezone.utc):
                    return {'authenticated': False, 'error': 'Token expired'}
            
            # Extract user information
            user_id = payload.get('user_id') or payload.get('sub')
            if not user_id:
                return {'authenticated': False, 'error': 'Invalid token payload'}
            
            return {
                'authenticated': True,
                'user_id': user_id,
                'payload': payload,
                'scopes': payload.get('scopes', [])
            }
            
        except jwt.ExpiredSignatureError:
            return {'authenticated': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'authenticated': False, 'error': 'Invalid token'}
        except Exception as e:
            return {'authenticated': False, 'error': f'JWT authentication failed: {str(e)}'}
    
    async def _authenticate_api_key(self, request: APIRequest) -> Dict[str, Any]:
        """Authenticate using API key"""
        try:
            # Try header first
            api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
            
            if not api_key:
                # Try query parameter
                api_key = request.query_params.get('api_key')
            
            if not api_key:
                return {'authenticated': False, 'error': 'Missing API key'}
            
            # Remove Bearer prefix if present
            if api_key.startswith('Bearer '):
                api_key = api_key[7:]
            
            # Validate API key
            key_info = self.api_keys.get(api_key)
            if not key_info:
                return {'authenticated': False, 'error': 'Invalid API key'}
            
            # Check if key is active
            if not key_info.get('active', True):
                return {'authenticated': False, 'error': 'API key deactivated'}
            
            # Check expiration
            if 'expires_at' in key_info:
                expires_at = datetime.fromisoformat(key_info['expires_at'])
                if expires_at < datetime.now(timezone.utc):
                    return {'authenticated': False, 'error': 'API key expired'}
            
            return {
                'authenticated': True,
                'user_id': key_info.get('user_id', 'api_user'),
                'api_key': api_key,
                'permissions': key_info.get('permissions', [])
            }
            
        except Exception as e:
            return {'authenticated': False, 'error': f'API key authentication failed: {str(e)}'}
    
    async def _authenticate_oauth2(self, request: APIRequest) -> Dict[str, Any]:
        """Authenticate using OAuth2"""
        # Simplified OAuth2 implementation
        return {'authenticated': False, 'error': 'OAuth2 not implemented'}
    
    async def _authenticate_basic(self, request: APIRequest) -> Dict[str, Any]:
        """Authenticate using Basic authentication"""
        # Simplified Basic auth implementation
        return {'authenticated': False, 'error': 'Basic auth not implemented'}
    
    def create_jwt_token(self, user_id: str, scopes: List[str] = None) -> str:
        """Create JWT token for user"""
        try:
            payload = {
                'user_id': user_id,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(hours=self.config.jwt_expiry_hours),
                'scopes': scopes or []
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise
    
    def add_api_key(self, api_key: str, user_id: str, permissions: List[str] = None) -> bool:
        """Add API key for user"""
        try:
            self.api_keys[api_key] = {
                'user_id': user_id,
                'permissions': permissions or [],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'active': True
            }
            return True
            
        except Exception as e:
            logger.error(f"Failed to add API key: {e}")
            return False


class RateLimiter:
    """Handles rate limiting for API requests"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        
        logger.info("🚦 Rate Limiter initialized")
    
    async def check_rate_limit(self, request: APIRequest, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check if request exceeds rate limit"""
        try:
            # Determine identifier (IP, user_id, or API key)
            identifier = self._get_rate_limit_identifier(request)
            
            # Use provided limit or default
            request_limit = limit or self.config.default_rate_limit
            
            # Get current time
            current_time = datetime.now(timezone.utc)
            window_start = current_time - timedelta(hours=1)  # 1-hour window
            
            # Clean old requests from deque
            request_times = self.request_counts[identifier]
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Check if limit exceeded
            if len(request_times) >= request_limit:
                return {
                    'allowed': False,
                    'limit': request_limit,
                    'current': len(request_times),
                    'reset_time': (window_start + timedelta(hours=1)).isoformat(),
                    'retry_after': 3600  # seconds
                }
            
            # Add current request
            request_times.append(current_time)
            
            return {
                'allowed': True,
                'limit': request_limit,
                'current': len(request_times),
                'remaining': request_limit - len(request_times)
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request on error (fail open)
            return {'allowed': True, 'error': str(e)}
    
    def _get_rate_limit_identifier(self, request: APIRequest) -> str:
        """Get identifier for rate limiting"""
        # Prefer user_id, then API key, then IP address
        if request.user_id:
            return f"user:{request.user_id}"
        elif request.api_key:
            return f"api_key:{request.api_key}"
        else:
            return f"ip:{request.client_ip}"


class LoadBalancer:
    """Handles load balancing across service endpoints"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.endpoint_counters: Dict[str, int] = defaultdict(int)
        self.endpoint_health: Dict[str, bool] = {}
        
        logger.info("⚖️ Load Balancer initialized")
    
    async def select_endpoint(
        self, 
        endpoints: List[ServiceEndpoint], 
        strategy: RouteStrategy = None,
        request: Optional[APIRequest] = None
    ) -> Optional[ServiceEndpoint]:
        """Select service endpoint based on strategy"""
        try:
            if not endpoints:
                return None
            
            # Filter healthy endpoints
            healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
            
            if not healthy_endpoints:
                # If no healthy endpoints, use all (circuit breaker)
                healthy_endpoints = endpoints
            
            strategy = strategy or self.config.default_route_strategy
            
            if strategy == RouteStrategy.ROUND_ROBIN:
                return self._round_robin_select(healthy_endpoints)
            
            elif strategy == RouteStrategy.WEIGHTED:
                return self._weighted_select(healthy_endpoints)
            
            elif strategy == RouteStrategy.HEALTH_BASED:
                return self._health_based_select(healthy_endpoints)
            
            elif strategy == RouteStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(healthy_endpoints)
            
            elif strategy == RouteStrategy.HASH_BASED:
                return self._hash_based_select(healthy_endpoints, request)
            
            else:
                # Default to round robin
                return self._round_robin_select(healthy_endpoints)
            
        except Exception as e:
            logger.error(f"Endpoint selection failed: {e}")
            return endpoints[0] if endpoints else None
    
    def _round_robin_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round robin endpoint selection"""
        if not endpoints:
            return None
        
        # Use combined service IDs as key
        key = "_".join(sorted(ep.service_id for ep in endpoints))
        self.endpoint_counters[key] = (self.endpoint_counters[key] + 1) % len(endpoints)
        
        return endpoints[self.endpoint_counters[key]]
    
    def _weighted_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted endpoint selection"""
        if not endpoints:
            return None
        
        # Calculate total weight
        total_weight = sum(ep.weight for ep in endpoints)
        
        if total_weight == 0:
            return endpoints[0]
        
        # Generate random number and select based on weight
        import random
        rand_weight = random.randint(1, total_weight)
        
        current_weight = 0
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if rand_weight <= current_weight:
                return endpoint
        
        return endpoints[-1]  # Fallback
    
    def _health_based_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Health-based endpoint selection (best response time)"""
        if not endpoints:
            return None
        
        # Select endpoint with best response time
        return min(endpoints, key=lambda ep: ep.response_time_ms)
    
    def _least_connections_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections endpoint selection"""
        if not endpoints:
            return None
        
        return min(endpoints, key=lambda ep: ep.active_connections)
    
    def _hash_based_select(self, endpoints: List[ServiceEndpoint], request: Optional[APIRequest]) -> ServiceEndpoint:
        """Hash-based endpoint selection (sticky sessions)"""
        if not endpoints or not request:
            return endpoints[0] if endpoints else None
        
        # Create hash from user_id or IP
        hash_key = request.user_id or request.client_ip
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        
        return endpoints[hash_value % len(endpoints)]


class CacheManager:
    """Handles response caching"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {'hits': 0, 'misses': 0, 'size': 0}
        
        logger.info("🗄️ Cache Manager initialized")
    
    async def get_cached_response(self, cache_key: str) -> Optional[APIResponse]:
        """Get cached response if available and valid"""
        try:
            if not self.config.enable_caching:
                return None
            
            cached_item = self.cache.get(cache_key)
            if not cached_item:
                self.cache_stats['misses'] += 1
                return None
            
            # Check TTL
            if cached_item['expires_at'] < datetime.now(timezone.utc):
                # Expired, remove from cache
                del self.cache[cache_key]
                self.cache_stats['size'] -= 1
                self.cache_stats['misses'] += 1
                return None
            
            # Cache hit
            self.cache_stats['hits'] += 1
            response = cached_item['response']
            response.cache_hit = True
            
            return response
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    async def cache_response(
        self, 
        cache_key: str, 
        response: APIResponse, 
        ttl: int = None
    ) -> bool:
        """Cache response with TTL"""
        try:
            if not self.config.enable_caching:
                return False
            
            # Check cache size limit
            if len(self.cache) >= self.config.max_cache_size:
                await self._evict_oldest()
            
            ttl = ttl or self.config.default_cache_ttl
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
            
            self.cache[cache_key] = {
                'response': response,
                'cached_at': datetime.now(timezone.utc),
                'expires_at': expires_at,
                'access_count': 0
            }
            
            self.cache_stats['size'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Response caching failed: {e}")
            return False
    
    def generate_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for request"""
        # Include path, method, and relevant parameters
        key_parts = [
            request.method,
            request.path,
            str(sorted(request.query_params.items()))
        ]
        
        # Include user context if relevant
        if request.user_id:
            key_parts.append(f"user:{request.user_id}")
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _evict_oldest(self) -> None:
        """Evict oldest cache entry"""
        if not self.cache:
            return
        
        # Find oldest entry
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['cached_at'])
        del self.cache[oldest_key]
        self.cache_stats['size'] -= 1
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'cache_size': self.cache_stats['size'],
            'max_size': self.config.max_cache_size
        }


class RequestRouter:
    """Routes requests to appropriate services"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.routes: List[Route] = []
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = {}
        
        logger.info("🛣️ Request Router initialized")
    
    def add_route(self, route -> None: Route) -> None:
        """Add route configuration"""
        self.routes.append(route)
        
        # Index service endpoints
        for endpoint in route.service_endpoints:
            if endpoint.service_id not in self.service_endpoints:
                self.service_endpoints[endpoint.service_id] = []
            self.service_endpoints[endpoint.service_id].append(endpoint)
    
    async def find_route(self, request: APIRequest) -> Optional[Route]:
        """Find matching route for request"""
        try:
            for route in self.routes:
                if self._matches_route(request, route):
                    return route
            
            return None
            
        except Exception as e:
            logger.error(f"Route finding failed: {e}")
            return None
    
    def _matches_route(self, request: APIRequest, route: Route) -> bool:
        """Check if request matches route pattern"""
        # Check HTTP method
        if request.method not in route.methods:
            return False
        
        # Check path pattern (simplified regex matching)
        pattern = route.path_pattern.replace('*', '.*').replace('{', '(?P<').replace('}', '>[^/]+)')
        
        try:
            match = re.fullmatch(pattern, request.path)
            return match is not None
        except re.error:
            # Fallback to simple string matching
            return request.path.startswith(route.path_pattern.replace('*', ''))


class ServiceProxy:
    """Proxies requests to backend services"""
    
    def __init__(self, config -> None: GatewayConfig) -> None:
        self.config = config
        self.session = None
        
        logger.info("🔄 Service Proxy initialized")
    
    async def proxy_request(
        self, 
        request: APIRequest, 
        endpoint: ServiceEndpoint
    ) -> APIResponse:
        """Proxy request to service endpoint"""
        try:
            start_time = time.time()
            
            # Build target URL
            target_url = f"{endpoint.base_url.rstrip('/')}{request.path}"
            
            # Prepare headers
            headers = dict(request.headers)
            headers['X-Forwarded-For'] = request.client_ip
            headers['X-Request-ID'] = request.request_id
            
            # Make HTTP request
            if HAS_ASYNC_CLIENTS:
                response = await self._make_async_request(
                    request.method, target_url, headers, request.query_params, request.body, endpoint
                )
            else:
                response = await self._make_basic_request(
                    request.method, target_url, headers, request.query_params, request.body
                )
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Update endpoint metrics
            endpoint.response_time_ms = response_time
            
            return APIResponse(
                request_id=request.request_id,
                status_code=response['status'],
                headers=response['headers'],
                body=response['body'],
                response_time_ms=response_time,
                service_endpoint=endpoint.service_id
            )
            
        except Exception as e:
            logger.error(f"Request proxying failed: {e}")
            return APIResponse(
                request_id=request.request_id,
                status_code=500,
                headers={'Content-Type': 'application/json'},
                body=json.dumps({'error': 'Service proxy error', 'message': str(e)}).encode(),
                response_time_ms=0.0,
                service_endpoint=endpoint.service_id
            )
    
    async def _make_async_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str],
        params: Dict[str, str],
        body: Optional[bytes],
        endpoint: ServiceEndpoint
    ) -> Dict[str, Any]:
        """Make async HTTP request"""
        try:
            if not self.session:
                timeout = aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=body
            ) as response:
                response_body = await response.read()
                response_headers = dict(response.headers)
                
                return {
                    'status': response.status,
                    'headers': response_headers,
                    'body': response_body
                }
                
        except Exception as e:
            logger.error(f"Async HTTP request failed: {e}")
            raise
    
    async def _make_basic_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str],
        params: Dict[str, str],
        body: Optional[bytes]
    ) -> Dict[str, Any]:
        """Make basic HTTP request (fallback)"""
        # Simplified implementation for when aiohttp is not available
        return {
            'status': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'HTTP client not available'}).encode()
        }
    
    async def close(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class MediaAPIGateway:
    """Main API Gateway orchestrating all components"""
    
    def __init__(self, config -> None: Optional[GatewayConfig] = None) -> None:
        """Initialize media API gateway"""
        self.config = config or GatewayConfig()
        
        # Initialize components
        self.auth_manager = AuthenticationManager(self.config)
        self.rate_limiter = RateLimiter(self.config)
        self.load_balancer = LoadBalancer(self.config)
        self.cache_manager = CacheManager(self.config)
        self.request_router = RequestRouter(self.config)
        self.service_proxy = ServiceProxy(self.config)
        
        # FastAPI application
        self.app = None
        if HAS_FASTAPI:
            self._setup_fastapi_app()
        
        # Gateway state
        self.is_running = False
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.now(timezone.utc)
        
        logger.info("🌐 Media API Gateway initialized")
    
    def _setup_fastapi_app(self) -> None:
        """Setup FastAPI application"""
        self.app = FastAPI(
            title="Media API Gateway",
            description="Advanced API Gateway for Media Services",
            version="1.0.0"
        )
        
        # Add CORS middleware
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.allowed_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
        
        # Add trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure as needed
        )
        
        # Add gateway middleware
        @self.app.middleware("http")
        async def gateway_middleware(request -> None: Request, call_next) -> None:
            return await self._handle_request(request, call_next)
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check() -> None:
            return await self.get_health_status()
        
        # Metrics endpoint
        @self.app.get("/metrics")
        async def metrics() -> None:
            return await self.get_metrics()
        
        # Catch-all route
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
        async def gateway_proxy(request -> None: Request) -> None:
            # This will be handled by middleware
            return {"message": "Request processed by gateway"}
    
    async def _handle_request(self, request: Request, call_next) -> Response:
        """Handle incoming request through gateway pipeline"""
        try:
            self.request_count += 1
            
            # Create API request object
            api_request = APIRequest(
                request_id=str(uuid.uuid4()),
                path=request.url.path,
                method=request.method,
                headers=dict(request.headers),
                query_params=dict(request.query_params),
                client_ip=request.client.host,
                body=await request.body() if request.method in ['POST', 'PUT', 'PATCH'] else None
            )
            
            # Skip gateway processing for health and metrics endpoints
            if api_request.path in ['/health', '/metrics']:
                return await call_next(request)
            
            # Find route
            route = await self.request_router.find_route(api_request)
            if not route:
                return Response(
                    content=json.dumps({'error': 'Route not found'}),
                    status_code=404,
                    media_type='application/json'
                )
            
            # Authentication
            auth_result = await self.auth_manager.authenticate_request(api_request, route.auth_method)
            if not auth_result.get('authenticated', False):
                return Response(
                    content=json.dumps({'error': 'Authentication failed', 'message': auth_result.get('error', 'Unknown error')}),
                    status_code=401,
                    media_type='application/json'
                )
            
            # Update request with auth info
            api_request.user_id = auth_result.get('user_id')
            api_request.api_key = auth_result.get('api_key')
            
            # Rate limiting
            rate_limit_result = await self.rate_limiter.check_rate_limit(api_request, route.rate_limit)
            if not rate_limit_result.get('allowed', True):
                return Response(
                    content=json.dumps({'error': 'Rate limit exceeded', 'retry_after': rate_limit_result.get('retry_after')}),
                    status_code=429,
                    media_type='application/json',
                    headers={'Retry-After': str(rate_limit_result.get('retry_after', 3600))}
                )
            
            # Check cache
            cache_key = self.cache_manager.generate_cache_key(api_request)
            cached_response = await self.cache_manager.get_cached_response(cache_key)
            
            if cached_response and route.cache_strategy != CacheStrategy.NO_CACHE:
                return Response(
                    content=cached_response.body,
                    status_code=cached_response.status_code,
                    headers=dict(cached_response.headers),
                    media_type=cached_response.headers.get('Content-Type', 'application/json')
                )
            
            # Load balancing and service selection
            selected_endpoint = await self.load_balancer.select_endpoint(
                route.service_endpoints, 
                route.route_strategy, 
                api_request
            )
            
            if not selected_endpoint:
                return Response(
                    content=json.dumps({'error': 'No healthy service endpoints available'}),
                    status_code=503,
                    media_type='application/json'
                )
            
            # Proxy request to service
            api_response = await self.service_proxy.proxy_request(api_request, selected_endpoint)
            
            # Cache response if applicable
            if (route.cache_strategy != CacheStrategy.NO_CACHE and 
                api_response.status_code == 200 and 
                api_request.method == 'GET'):
                await self.cache_manager.cache_response(cache_key, api_response, route.cache_ttl)
            
            # Return response
            return Response(
                content=api_response.body,
                status_code=api_response.status_code,
                headers=dict(api_response.headers),
                media_type=api_response.headers.get('Content-Type', 'application/json')
            )
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Gateway request handling failed: {e}")
            
            return Response(
                content=json.dumps({'error': 'Internal gateway error', 'message': str(e)}),
                status_code=500,
                media_type='application/json'
            )
    
    async def start_gateway(self) -> bool:
        """Start the API gateway"""
        try:
            if not HAS_FASTAPI:
                logger.error("FastAPI not available - cannot start gateway")
                return False
            
            self.is_running = True
            self.start_time = datetime.now(timezone.utc)
            
            logger.info(f"API Gateway starting on {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start gateway: {e}")
            return False
    
    async def stop_gateway(self) -> bool:
        """Stop the API gateway"""
        try:
            self.is_running = False
            
            # Close service proxy
            await self.service_proxy.close()
            
            logger.info("API Gateway stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop gateway: {e}")
            return False
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get gateway health status"""
        try:
            uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            
            # Calculate error rate
            error_rate = (self.error_count / self.request_count) if self.request_count > 0 else 0
            
            # Determine health status
            if error_rate > 0.1:  # 10% error rate
                status = "unhealthy"
            elif error_rate > 0.05:  # 5% error rate
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                'status': status,
                'uptime_seconds': uptime_seconds,
                'is_running': self.is_running,
                'request_count': self.request_count,
                'error_count': self.error_count,
                'error_rate': error_rate,
                'cache_stats': self.cache_manager.get_cache_stats(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health status check failed: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get gateway metrics"""
        try:
            uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            
            return {
                'gateway_metrics': {
                    'uptime_seconds': uptime_seconds,
                    'requests_total': self.request_count,
                    'errors_total': self.error_count,
                    'requests_per_second': self.request_count / max(uptime_seconds, 1),
                    'error_rate': (self.error_count / self.request_count) if self.request_count > 0 else 0
                },
                'cache_metrics': self.cache_manager.get_cache_stats(),
                'route_metrics': {
                    'total_routes': len(self.request_router.routes),
                    'total_endpoints': sum(len(endpoints) for endpoints in self.request_router.service_endpoints.values())
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {'error': str(e)}
    
    def add_route(self, route -> None: Route) -> None:
        """Add route to gateway"""
        self.request_router.add_route(route)
    
    def add_api_key(self, api_key: str, user_id: str, permissions: List[str] = None) -> bool:
        """Add API key for authentication"""
        return self.auth_manager.add_api_key(api_key, user_id, permissions)
    
    def create_jwt_token(self, user_id: str, scopes: List[str] = None) -> str:
        """Create JWT token for user"""
        return self.auth_manager.create_jwt_token(user_id, scopes)


# Export all classes for import
__all__ = [
    'MediaAPIGateway',
    'GatewayConfig',
    'Route',
    'ServiceEndpoint',
    'APIRequest',
    'APIResponse',
    'AuthenticationManager',
    'RateLimiter',
    'LoadBalancer',
    'CacheManager',
    'RequestRouter',
    'ServiceProxy',
    'AuthMethod',
    'RouteStrategy',
    'CacheStrategy',
    'RateLimitType'
]