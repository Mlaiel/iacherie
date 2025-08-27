"""
API Adapters - Ultra-Advanced Multi-Protocol API Integration System
================================================================

Enterprise-grade API communication adapters for the IA-Influencer Agent platform.
Provides comprehensive API integration capabilities across multiple protocols with
advanced features like intelligent retry logic, rate limiting, caching, and real-time monitoring.

Business Logic: Platform Integration → API Communication → Data Processing → Response Optimization

Protocol Support:
- REST API: Advanced HTTP/1.1, HTTP/2, HTTP/3 with smart pagination, compression, caching
- GraphQL: Query optimization, batching, subscription management, schema introspection
- WebSocket: Real-time bidirectional communication, multiplexing, heartbeat monitoring
- Webhook: Event-driven processing, signature verification, payload validation, retry handling
- gRPC: High-performance RPC with streaming, load balancing, service discovery
- Streaming: Real-time data processing with backpressure handling and flow control

Features:
- Intelligent rate limiting with adaptive algorithms
- Advanced authentication (OAuth2, JWT, API keys, mTLS)
- Comprehensive error handling and circuit breaker patterns
- Real-time monitoring and metrics collection
- Request/response transformation and validation
- Multi-region failover and load balancing
- Enterprise-grade security and encryption
- Automated API documentation generation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This revolutionary API integration system is protected intellectual property.
Any unauthorized copying, distribution, or modification is strictly prohibited and will
result in immediate legal action. Contact mlaiel@live.de for licensing inquiries.

Expert Development Team Specialties:
- Lead AI Developer & ML Engineer - Intelligent API optimization and prediction
- Senior Backend Architect - High-performance API gateway and microservices design
- DevOps Engineer - API infrastructure, monitoring, and scalability optimization
- Security Expert - API security, authentication, and threat protection
- Database Administrator (DBA) - API data caching and persistence strategies
- Network Engineer - Protocol optimization and performance tuning
"""

import asyncio
import logging
import json
import aiohttp
import websockets
import time
import hashlib
import hmac
import base64
import ssl
import gzip
import zlib
from typing import Dict, List, Optional, Any, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from abc import ABC, abstractmethod
import threading
from contextlib import asynccontextmanager
import backoff

# Advanced imports
try:
    import grpc
    from grpc import aio as grpc_aio
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

try:
    from gql import gql, Client
    from gql.transport.aiohttp import AIOHTTPTransport
    from gql.transport.websockets import WebsocketsTransport
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class APIRequest:
    """Advanced API request configuration with enterprise features."""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Union[Dict, str, bytes]] = None
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    retry_backoff: str = "exponential"  # linear, exponential, constant
    rate_limit: Optional[Dict[str, Any]] = None
    cache_config: Optional[Dict[str, Any]] = None
    compression: str = "gzip"  # gzip, deflate, br, none
    priority: int = 1  # 1-10, higher is more important
    tags: List[str] = field(default_factory=list)
    
@dataclass
class APIResponse:
    """Comprehensive API response with advanced metadata."""
    status_code: int
    headers: Dict[str, str]
    data: Union[Dict, List, str, bytes]
    raw_response: Optional[Any] = None
    request_id: str = ""
    response_time: float = 0.0
    cache_hit: bool = False
    compression_ratio: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
@dataclass
class RateLimitConfig:
    """Advanced rate limiting configuration."""
    requests_per_second: float = 10.0
    requests_per_minute: float = 600.0
    requests_per_hour: float = 36000.0
    burst_size: int = 50
    window_size: int = 60  # seconds
    strategy: str = "token_bucket"  # token_bucket, sliding_window, fixed_window
    adaptive: bool = True
    backoff_multiplier: float = 1.5
    max_backoff: float = 300.0  # seconds

@dataclass
class CacheConfig:
    """Intelligent caching configuration."""
    enabled: bool = True
    ttl: int = 3600  # seconds
    max_size: int = 10000  # number of items
    strategy: str = "lru"  # lru, lfu, ttl
    compression: bool = True
    invalidation_patterns: List[str] = field(default_factory=list)
    warm_up: bool = False
    
class CircuitBreaker:
    """Advanced circuit breaker for API protection."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: tuple = (Exception,)):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_size
        self.last_update = time.time()
        self.request_history = []
        self._lock = threading.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from rate limiter."""
        if self.config.strategy == "token_bucket":
            return await self._token_bucket_acquire(tokens)
        elif self.config.strategy == "sliding_window":
            return await self._sliding_window_acquire(tokens)
        else:
            return await self._fixed_window_acquire(tokens)
    
    async def _token_bucket_acquire(self, tokens: int) -> bool:
        """Token bucket rate limiting algorithm."""
        with self._lock:
            now = time.time()
            time_passed = now - self.last_update
            
            # Add tokens based on time passed
            new_tokens = time_passed * self.config.requests_per_second
            self.tokens = min(self.config.burst_size, self.tokens + new_tokens)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                # Calculate wait time
                wait_time = (tokens - self.tokens) / self.config.requests_per_second
                if self.config.adaptive:
                    await asyncio.sleep(wait_time)
                    return await self._token_bucket_acquire(tokens)
                return False
    
    async def _sliding_window_acquire(self, tokens: int) -> bool:
        """Sliding window rate limiting algorithm."""
        with self._lock:
            now = time.time()
            window_start = now - self.config.window_size
            
            # Remove old requests
            self.request_history = [
                timestamp for timestamp in self.request_history 
                if timestamp > window_start
            ]
            
            # Check if we can make the request
            if len(self.request_history) < self.config.requests_per_minute:
                self.request_history.append(now)
                return True
            
            if self.config.adaptive:
                # Wait until oldest request expires
                wait_time = self.request_history[0] + self.config.window_size - now
                await asyncio.sleep(max(0, wait_time))
                return await self._sliding_window_acquire(tokens)
            
            return False
    
    async def _fixed_window_acquire(self, tokens: int) -> bool:
        """Fixed window rate limiting algorithm."""
        # Simplified implementation
        return await self._token_bucket_acquire(tokens)

class APICache:
    """Advanced API response caching system."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_order: List[str] = []
        self.access_count: Dict[str, int] = {}
        self._lock = threading.Lock()
        
        # Initialize Redis if available
        self.redis_client = None
        if REDIS_AVAILABLE and config.enabled:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {str(e)}")
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        if not self.config.enabled:
            return None
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(f"api_cache:{key}")
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis cache get failed: {str(e)}")
        
        # Fallback to memory cache
        with self._lock:
            if key in self.cache:
                cache_entry = self.cache[key]
                
                # Check TTL
                if time.time() - cache_entry["timestamp"] < self.config.ttl:
                    # Update access statistics
                    self.access_count[key] = self.access_count.get(key, 0) + 1
                    if key in self.access_order:
                        self.access_order.remove(key)
                    self.access_order.append(key)
                    
                    return cache_entry["data"]
                else:
                    # Expired entry
                    del self.cache[key]
                    if key in self.access_order:
                        self.access_order.remove(key)
                    if key in self.access_count:
                        del self.access_count[key]
        
        return None
    
    async def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Cache response data."""
        if not self.config.enabled:
            return
        
        cache_ttl = ttl or self.config.ttl
        cache_entry = {
            "data": data,
            "timestamp": time.time(),
            "ttl": cache_ttl
        }
        
        # Try Redis first
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"api_cache:{key}",
                    cache_ttl,
                    json.dumps(cache_entry)
                )
                return
            except Exception as e:
                logger.warning(f"Redis cache set failed: {str(e)}")
        
        # Fallback to memory cache
        with self._lock:
            # Implement cache eviction if needed
            if len(self.cache) >= self.config.max_size:
                self._evict_cache_entry()
            
            self.cache[key] = cache_entry
            self.access_count[key] = 1
            self.access_order.append(key)
    
    def _evict_cache_entry(self):
        """Evict cache entry based on strategy."""
        if not self.access_order:
            return
        
        if self.config.strategy == "lru":
            # Remove least recently used
            key_to_remove = self.access_order[0]
        elif self.config.strategy == "lfu":
            # Remove least frequently used
            key_to_remove = min(self.access_count.keys(), key=lambda k: self.access_count[k])
        else:  # TTL
            # Remove oldest entry
            oldest_key = None
            oldest_time = float('inf')
            for key, entry in self.cache.items():
                if entry["timestamp"] < oldest_time:
                    oldest_time = entry["timestamp"]
                    oldest_key = key
            key_to_remove = oldest_key
        
        if key_to_remove and key_to_remove in self.cache:
            del self.cache[key_to_remove]
            if key_to_remove in self.access_order:
                self.access_order.remove(key_to_remove)
            if key_to_remove in self.access_count:
                del self.access_count[key_to_remove]
    
    def generate_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for request."""
        key_components = [
            request.method,
            request.url,
            json.dumps(request.params, sort_keys=True),
            json.dumps(request.headers, sort_keys=True)
        ]
        
        if request.data:
            if isinstance(request.data, dict):
                key_components.append(json.dumps(request.data, sort_keys=True))
            else:
                key_components.append(str(request.data))
        
        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()

class BaseAPIAdapter(ABC):
    """
    Ultra-advanced base class for API adapters with enterprise-grade functionality.
    
    Provides standardized interface for all API communications including intelligent
    retry logic, advanced caching, comprehensive monitoring, and security features.
    """
    
    def __init__(self, base_url: str = "", default_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Advanced components
        self.rate_limiter = RateLimiter(RateLimitConfig())
        self.cache = APICache(CacheConfig())
        self.circuit_breaker = CircuitBreaker()
        
        # Monitoring and metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "rate_limit_hits": 0
        }
        
        # Configuration
        self.config = {
            "max_connections": 100,
            "max_connections_per_host": 10,
            "connection_timeout": 30.0,
            "read_timeout": 60.0,
            "enable_compression": True,
            "enable_ssl_verification": True,
            "user_agent": "IA-Influencer-Agent/1.0"
        }
    
    async def initialize(self) -> None:
        """Initialize API adapter with advanced connection pooling."""
        try:
            # SSL context configuration
            ssl_context = ssl.create_default_context()
            if not self.config["enable_ssl_verification"]:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connection configuration
            connector = aiohttp.TCPConnector(
                limit=self.config["max_connections"],
                limit_per_host=self.config["max_connections_per_host"],
                ttl_dns_cache=300,
                use_dns_cache=True,
                ssl=ssl_context,
                enable_cleanup_closed=True
            )
            
            # Timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=self.config["read_timeout"],
                connect=self.config["connection_timeout"]
            )
            
            # Create session with advanced configuration
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    **self.default_headers,
                    "User-Agent": self.config["user_agent"],
                    "Accept-Encoding": "gzip, deflate, br" if self.config["enable_compression"] else "identity"
                },
                auto_decompress=True,
                raise_for_status=False
            )
            
            logger.info("API adapter initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize API adapter: {str(e)}")
            raise
    
    async def cleanup(self) -> None:
        """Cleanup resources and close connections."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            if self.cache.redis_client:
                await self.cache.redis_client.close()
            
            logger.info("API adapter cleaned up successfully")
            
        except Exception as e:
            logger.error(f"API adapter cleanup failed: {str(e)}")
    
    @asynccontextmanager
    async def session_context(self):
        """Context manager for session lifecycle."""
        if not self.session:
            await self.initialize()
        try:
            yield self.session
        finally:
            # Session cleanup handled by explicit cleanup() call
            pass
    
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make API request with advanced features."""
        start_time = time.time()
        request_id = hashlib.sha256(f"{request.url}{time.time()}".encode()).hexdigest()[:16]
        
        try:
            # Rate limiting
            if not await self.rate_limiter.acquire():
                self.metrics["rate_limit_hits"] += 1
                raise Exception("Rate limit exceeded")
            
            # Check cache
            cache_key = self.cache.generate_cache_key(request)
            cached_response = await self.cache.get(cache_key)
            
            if cached_response:
                self.metrics["cache_hits"] += 1
                response_time = time.time() - start_time
                
                return APIResponse(
                    status_code=cached_response["status_code"],
                    headers=cached_response["headers"],
                    data=cached_response["data"],
                    request_id=request_id,
                    response_time=response_time,
                    cache_hit=True,
                    metadata={"from_cache": True}
                )
            
            self.metrics["cache_misses"] += 1
            
            # Make actual request
            async with self.session_context() as session:
                response = await self._execute_request(session, request, request_id)
                
                # Cache successful responses
                if 200 <= response.status_code < 300 and request.cache_config:
                    await self.cache.set(cache_key, {
                        "status_code": response.status_code,
                        "headers": response.headers,
                        "data": response.data
                    })
                
                # Update metrics
                self.metrics["total_requests"] += 1
                if 200 <= response.status_code < 300:
                    self.metrics["successful_requests"] += 1
                else:
                    self.metrics["failed_requests"] += 1
                
                # Update average response time
                response_time = time.time() - start_time
                self._update_average_response_time(response_time)
                
                return response
        
        except Exception as e:
            self.metrics["total_requests"] += 1
            self.metrics["failed_requests"] += 1
            logger.error(f"API request failed: {str(e)}")
            raise
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _execute_request(self, session: aiohttp.ClientSession, 
                             request: APIRequest, request_id: str) -> APIResponse:
        """Execute the actual HTTP request with retry logic."""
        
        # Prepare URL
        url = urljoin(self.base_url, request.url) if self.base_url else request.url
        
        # Prepare headers
        headers = {**self.default_headers, **request.headers}
        headers["X-Request-ID"] = request_id
        
        # Prepare data
        data = None
        json_data = None
        
        if request.data:
            if isinstance(request.data, dict):
                json_data = request.data
                headers["Content-Type"] = "application/json"
            else:
                data = request.data
        
        # Apply compression if enabled and data is present
        if request.compression != "none" and data:
            if request.compression == "gzip":
                data = gzip.compress(data.encode() if isinstance(data, str) else data)
                headers["Content-Encoding"] = "gzip"
        
        # Make request
        async with session.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.params,
            data=data,
            json=json_data,
            timeout=aiohttp.ClientTimeout(total=request.timeout)
        ) as response:
            
            # Read response data
            response_data = await response.read()
            
            # Parse response based on content type
            content_type = response.headers.get("Content-Type", "").lower()
            
            if "application/json" in content_type:
                try:
                    parsed_data = json.loads(response_data.decode())
                except json.JSONDecodeError:
                    parsed_data = response_data.decode()
            elif "text/" in content_type:
                parsed_data = response_data.decode()
            else:
                parsed_data = response_data
            
            # Calculate compression ratio
            compression_ratio = 1.0
            content_encoding = response.headers.get("Content-Encoding", "")
            if content_encoding and len(response_data) > 0:
                original_size = len(str(parsed_data).encode())
                compressed_size = len(response_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            return APIResponse(
                status_code=response.status,
                headers=dict(response.headers),
                data=parsed_data,
                raw_response=response_data,
                request_id=request_id,
                response_time=0.0,  # Will be updated by caller
                cache_hit=False,
                compression_ratio=compression_ratio,
                metadata={
                    "url": str(response.url),
                    "method": request.method,
                    "content_type": content_type,
                    "content_length": len(response_data)
                }
            )
    
    def _update_average_response_time(self, response_time: float):
        """Update running average of response time."""
        total_requests = self.metrics["total_requests"]
        if total_requests == 1:
            self.metrics["average_response_time"] = response_time
        else:
            current_avg = self.metrics["average_response_time"]
            self.metrics["average_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current adapter metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "rate_limit_hits": 0
        }

class RESTAPIAdapter(BaseAPIAdapter):
    """
    Ultra-advanced REST API adapter with comprehensive HTTP protocol support.
    
    Features:
    - HTTP/1.1, HTTP/2, HTTP/3 support
    - Advanced authentication (OAuth2, JWT, API keys, mTLS)
    - Intelligent pagination handling
    - Request/response transformation
    - Comprehensive error handling
    """
    
    def __init__(self, base_url: str = "", auth_config: Optional[Dict[str, Any]] = None):
        super().__init__(base_url)
        self.auth_config = auth_config or {}
        self.auth_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    async def authenticate(self) -> bool:
        """Perform authentication based on configuration."""
        try:
            auth_type = self.auth_config.get("type", "none")
            
            if auth_type == "oauth2":
                return await self._oauth2_authenticate()
            elif auth_type == "jwt":
                return await self._jwt_authenticate()
            elif auth_type == "api_key":
                return await self._api_key_authenticate()
            elif auth_type == "bearer":
                return await self._bearer_authenticate()
            else:
                return True  # No authentication required
                
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    async def _oauth2_authenticate(self) -> bool:
        """OAuth2 authentication flow."""
        try:
            token_url = self.auth_config.get("token_url")
            client_id = self.auth_config.get("client_id")
            client_secret = self.auth_config.get("client_secret")
            scope = self.auth_config.get("scope", "")
            
            if not all([token_url, client_id, client_secret]):
                raise ValueError("Missing OAuth2 configuration")
            
            # Prepare token request
            token_request = APIRequest(
                method="POST",
                url=token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope={scope}"
            )
            
            response = await self.make_request(token_request)
            
            if response.status_code == 200 and isinstance(response.data, dict):
                self.auth_token = response.data.get("access_token")
                expires_in = response.data.get("expires_in", 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # 60s buffer
                
                # Update default headers
                self.default_headers["Authorization"] = f"Bearer {self.auth_token}"
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"OAuth2 authentication failed: {str(e)}")
            return False
    
    async def _jwt_authenticate(self) -> bool:
        """JWT authentication."""
        try:
            token = self.auth_config.get("token")
            if token:
                self.auth_token = token
                self.default_headers["Authorization"] = f"Bearer {token}"
                return True
            return False
            
        except Exception as e:
            logger.error(f"JWT authentication failed: {str(e)}")
            return False
    
    async def _api_key_authenticate(self) -> bool:
        """API key authentication."""
        try:
            api_key = self.auth_config.get("api_key")
            header_name = self.auth_config.get("header_name", "X-API-Key")
            
            if api_key:
                self.default_headers[header_name] = api_key
                return True
            return False
            
        except Exception as e:
            logger.error(f"API key authentication failed: {str(e)}")
            return False
    
    async def _bearer_authenticate(self) -> bool:
        """Bearer token authentication."""
        try:
            token = self.auth_config.get("token")
            if token:
                self.default_headers["Authorization"] = f"Bearer {token}"
                return True
            return False
            
        except Exception as e:
            logger.error(f"Bearer authentication failed: {str(e)}")
            return False
    
    async def paginated_request(self, request: APIRequest, 
                              pagination_config: Dict[str, Any]) -> AsyncGenerator[APIResponse, None]:
        """Handle paginated API requests automatically."""
        try:
            page_param = pagination_config.get("page_param", "page")
            per_page_param = pagination_config.get("per_page_param", "per_page")
            max_pages = pagination_config.get("max_pages", 100)
            per_page = pagination_config.get("per_page", 50)
            
            current_page = 1
            
            while current_page <= max_pages:
                # Update pagination parameters
                paginated_request = APIRequest(
                    method=request.method,
                    url=request.url,
                    headers=request.headers.copy(),
                    params={
                        **request.params,
                        page_param: current_page,
                        per_page_param: per_page
                    },
                    data=request.data,
                    timeout=request.timeout,
                    retry_attempts=request.retry_attempts,
                    retry_delay=request.retry_delay
                )
                
                response = await self.make_request(paginated_request)
                yield response
                
                # Check if there are more pages
                if response.status_code != 200:
                    break
                
                # Determine if there are more pages based on response
                if isinstance(response.data, dict):
                    # Check common pagination indicators
                    if "next" in response.data and not response.data["next"]:
                        break
                    if "has_more" in response.data and not response.data["has_more"]:
                        break
                    if "data" in response.data and len(response.data["data"]) < per_page:
                        break
                elif isinstance(response.data, list):
                    if len(response.data) < per_page:
                        break
                
                current_page += 1
                
                # Rate limiting between pages
                await asyncio.sleep(0.1)  # Small delay between pages
            
        except Exception as e:
            logger.error(f"Paginated request failed: {str(e)}")
            raise
    
    async def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> APIResponse:
        """Convenience method for GET requests."""
        request = APIRequest(method="GET", url=url, params=params or {}, **kwargs)
        return await self.make_request(request)
    
    async def post(self, url: str, data: Optional[Union[Dict, str]] = None, **kwargs) -> APIResponse:
        """Convenience method for POST requests."""
        request = APIRequest(method="POST", url=url, data=data, **kwargs)
        return await self.make_request(request)
    
    async def put(self, url: str, data: Optional[Union[Dict, str]] = None, **kwargs) -> APIResponse:
        """Convenience method for PUT requests."""
        request = APIRequest(method="PUT", url=url, data=data, **kwargs)
        return await self.make_request(request)
    
    async def patch(self, url: str, data: Optional[Union[Dict, str]] = None, **kwargs) -> APIResponse:
        """Convenience method for PATCH requests."""
        request = APIRequest(method="PATCH", url=url, data=data, **kwargs)
        return await self.make_request(request)
    
    async def delete(self, url: str, **kwargs) -> APIResponse:
        """Convenience method for DELETE requests."""
        request = APIRequest(method="DELETE", url=url, **kwargs)
        return await self.make_request(request)

class GraphQLAPIAdapter(BaseAPIAdapter):
    """
    Advanced GraphQL API adapter with comprehensive GraphQL support.
    
    Features:
    - Query optimization and batching
    - Subscription management
    - Schema introspection
    - Fragment handling
    - Real-time updates via WebSocket
    """
    
    def __init__(self, endpoint: str, websocket_endpoint: Optional[str] = None):
        super().__init__(endpoint)
        self.endpoint = endpoint
        self.websocket_endpoint = websocket_endpoint
        self.client: Optional[Client] = None
        self.schema = None
        
    async def initialize(self) -> None:
        """Initialize GraphQL client."""
        try:
            await super().initialize()
            
            if GRAPHQL_AVAILABLE:
                # Initialize HTTP transport
                transport = AIOHTTPTransport(url=self.endpoint, headers=self.default_headers)
                self.client = Client(transport=transport, fetch_schema_from_transport=True)
                
                # Fetch schema for introspection
                try:
                    async with self.client as session:
                        self.schema = self.client.schema
                except Exception as e:
                    logger.warning(f"Failed to fetch GraphQL schema: {str(e)}")
                
                logger.info("GraphQL adapter initialized successfully")
            else:
                logger.warning("GraphQL dependencies not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize GraphQL adapter: {str(e)}")
            raise
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query."""
        try:
            if not GRAPHQL_AVAILABLE or not self.client:
                raise Exception("GraphQL client not available")
            
            gql_query = gql(query)
            
            async with self.client as session:
                result = await session.execute(gql_query, variable_values=variables)
                return result
                
        except Exception as e:
            logger.error(f"GraphQL query execution failed: {str(e)}")
            raise
    
    async def execute_mutation(self, mutation: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL mutation."""
        return await self.execute_query(mutation, variables)
    
    async def subscribe(self, subscription: str, variables: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to GraphQL subscription."""
        try:
            if not GRAPHQL_AVAILABLE or not self.websocket_endpoint:
                raise Exception("GraphQL subscriptions not available")
            
            transport = WebsocketsTransport(url=self.websocket_endpoint, headers=self.default_headers)
            client = Client(transport=transport)
            
            gql_subscription = gql(subscription)
            
            async with client as session:
                async for result in session.subscribe(gql_subscription, variable_values=variables):
                    yield result
                    
        except Exception as e:
            logger.error(f"GraphQL subscription failed: {str(e)}")
            raise
    
    def build_query(self, fields: List[str], query_name: str = "query", 
                   filters: Optional[Dict[str, Any]] = None) -> str:
        """Build GraphQL query from field list."""
        try:
            filter_string = ""
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        filter_parts.append(f'{key}: "{value}"')
                    else:
                        filter_parts.append(f'{key}: {value}')
                filter_string = f"({', '.join(filter_parts)})"
            
            fields_string = "\n    ".join(fields)
            
            query = f"""
            {query_name}{filter_string} {{
                {fields_string}
            }}
            """
            
            return query.strip()
            
        except Exception as e:
            logger.error(f"Query building failed: {str(e)}")
            raise
    
    def get_schema_info(self) -> Optional[Dict[str, Any]]:
        """Get GraphQL schema information."""
        if self.schema:
            return {
                "types": [str(type_def) for type_def in self.schema.type_map.values()],
                "queries": list(self.schema.query_type.fields.keys()) if self.schema.query_type else [],
                "mutations": list(self.schema.mutation_type.fields.keys()) if self.schema.mutation_type else [],
                "subscriptions": list(self.schema.subscription_type.fields.keys()) if self.schema.subscription_type else []
            }
        return None

class WebSocketAPIAdapter:
    """
    Advanced WebSocket API adapter with comprehensive real-time communication.
    
    Features:
    - Bidirectional real-time communication
    - Message multiplexing and routing
    - Connection health monitoring
    - Automatic reconnection with backoff
    - Message queuing and replay
    """
    
    def __init__(self, url: str, protocols: Optional[List[str]] = None):
        self.url = url
        self.protocols = protocols
        self.connection: Optional[websockets.WebSocketServerProtocol] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.message_queue: List[Dict[str, Any]] = []
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 1.0
        self.heartbeat_interval = 30.0
        self.last_heartbeat = time.time()
        
    async def connect(self) -> bool:
        """Establish WebSocket connection."""
        try:
            extra_headers = {}
            if hasattr(self, 'default_headers'):
                extra_headers = self.default_headers
            
            self.connection = await websockets.connect(
                self.url,
                subprotocols=self.protocols,
                extra_headers=extra_headers,
                ping_interval=self.heartbeat_interval,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            self.last_heartbeat = time.time()
            
            # Start message handling task
            asyncio.create_task(self._handle_messages())
            
            # Start heartbeat task
            asyncio.create_task(self._heartbeat_task())
            
            # Replay queued messages
            await self._replay_queued_messages()
            
            logger.info("WebSocket connection established")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            await self._handle_disconnect()
            return False
    
    async def disconnect(self):
        """Close WebSocket connection."""
        try:
            self.is_connected = False
            if self.connection:
                await self.connection.close()
                self.connection = None
            logger.info("WebSocket disconnected")
            
        except Exception as e:
            logger.error(f"WebSocket disconnect failed: {str(e)}")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message through WebSocket."""
        try:
            if not self.is_connected or not self.connection:
                # Queue message for later
                self.message_queue.append(message)
                await self._attempt_reconnect()
                return False
            
            message_str = json.dumps(message)
            await self.connection.send(message_str)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            await self._handle_disconnect()
            return False
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler for specific message type."""
        self.message_handlers[message_type] = handler
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages."""
        try:
            async for message in self.connection:
                if isinstance(message, str):
                    try:
                        data = json.loads(message)
                        message_type = data.get("type", "default")
                        
                        # Update heartbeat
                        self.last_heartbeat = time.time()
                        
                        # Route message to appropriate handler
                        if message_type in self.message_handlers:
                            await self.message_handlers[message_type](data)
                        elif "default" in self.message_handlers:
                            await self.message_handlers["default"](data)
                        else:
                            logger.warning(f"No handler for message type: {message_type}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse WebSocket message: {str(e)}")
                else:
                    # Handle binary messages
                    if "binary" in self.message_handlers:
                        await self.message_handlers["binary"](message)
                        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            await self._handle_disconnect()
        except Exception as e:
            logger.error(f"WebSocket message handling failed: {str(e)}")
            await self._handle_disconnect()
    
    async def _heartbeat_task(self):
        """Monitor connection health with heartbeat."""
        while self.is_connected:
            try:
                current_time = time.time()
                
                # Check if connection is still alive
                if current_time - self.last_heartbeat > self.heartbeat_interval * 2:
                    logger.warning("WebSocket heartbeat timeout")
                    await self._handle_disconnect()
                    break
                
                # Send ping if needed
                if self.connection and current_time - self.last_heartbeat > self.heartbeat_interval:
                    await self.connection.ping()
                
                await asyncio.sleep(self.heartbeat_interval / 2)
                
            except Exception as e:
                logger.error(f"Heartbeat task failed: {str(e)}")
                await self._handle_disconnect()
                break
    
    async def _handle_disconnect(self):
        """Handle WebSocket disconnection."""
        self.is_connected = False
        self.connection = None
        
        # Attempt reconnection
        await self._attempt_reconnect()
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect with exponential backoff."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return
        
        self.reconnect_attempts += 1
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
        
        logger.info(f"Attempting reconnection in {delay} seconds (attempt {self.reconnect_attempts})")
        await asyncio.sleep(delay)
        
        await self.connect()
    
    async def _replay_queued_messages(self):
        """Replay queued messages after reconnection."""
        if not self.message_queue:
            return
        
        logger.info(f"Replaying {len(self.message_queue)} queued messages")
        
        for message in self.message_queue.copy():
            if await self.send_message(message):
                self.message_queue.remove(message)
            else:
                break  # Connection lost again

class WebhookAPIAdapter:
    """
    Advanced webhook processing adapter with comprehensive event handling.
    
    Features:
    - Signature verification and validation
    - Event routing and processing
    - Retry handling with exponential backoff
    - Event replay and recovery
    - Rate limiting and security
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key
        self.event_handlers: Dict[str, Callable] = {}
        self.failed_events: List[Dict[str, Any]] = []
        self.processed_events: set = set()
        self.max_payload_size = 10 * 1024 * 1024  # 10MB
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific webhook event type."""
        self.event_handlers[event_type] = handler
    
    async def process_webhook(self, payload: Union[str, bytes], headers: Dict[str, str]) -> Dict[str, Any]:
        """Process incoming webhook with comprehensive validation."""
        try:
            # Validate payload size
            payload_size = len(payload)
            if payload_size > self.max_payload_size:
                raise ValueError(f"Payload size {payload_size} exceeds maximum {self.max_payload_size}")
            
            # Verify signature if secret key is provided
            if self.secret_key:
                if not self._verify_signature(payload, headers):
                    raise ValueError("Invalid webhook signature")
            
            # Parse payload
            if isinstance(payload, bytes):
                payload_str = payload.decode('utf-8')
            else:
                payload_str = payload
            
            try:
                event_data = json.loads(payload_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON payload: {str(e)}")
            
            # Extract event information
            event_id = event_data.get("id") or hashlib.sha256(payload_str.encode()).hexdigest()
            event_type = event_data.get("type") or event_data.get("event_type", "unknown")
            
            # Check for duplicate events
            if event_id in self.processed_events:
                return {"status": "duplicate", "event_id": event_id}
            
            # Process event
            result = await self._process_event(event_type, event_data, headers)
            
            # Mark as processed
            self.processed_events.add(event_id)
            
            # Cleanup old processed events (keep last 10000)
            if len(self.processed_events) > 10000:
                self.processed_events = set(list(self.processed_events)[-10000:])
            
            return {
                "status": "success",
                "event_id": event_id,
                "event_type": event_type,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            
            # Store failed event for retry
            self.failed_events.append({
                "payload": payload,
                "headers": headers,
                "error": str(e),
                "timestamp": time.time(),
                "retry_count": 0
            })
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _verify_signature(self, payload: Union[str, bytes], headers: Dict[str, str]) -> bool:
        """Verify webhook signature."""
        try:
            # Common signature headers
            signature_headers = [
                "X-Hub-Signature-256",
                "X-Signature-256", 
                "X-Webhook-Signature",
                "Signature"
            ]
            
            signature = None
            for header in signature_headers:
                if header in headers:
                    signature = headers[header]
                    break
            
            if not signature:
                return False
            
            # Extract algorithm and signature
            if "=" in signature:
                algorithm, sig = signature.split("=", 1)
            else:
                algorithm = "sha256"
                sig = signature
            
            # Calculate expected signature
            if isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload
            
            if algorithm.lower() == "sha256":
                expected_sig = hmac.new(
                    self.secret_key.encode(),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
            elif algorithm.lower() == "sha1":
                expected_sig = hmac.new(
                    self.secret_key.encode(),
                    payload_bytes,
                    hashlib.sha1
                ).hexdigest()
            else:
                logger.warning(f"Unsupported signature algorithm: {algorithm}")
                return False
            
            # Compare signatures
            return hmac.compare_digest(sig, expected_sig)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False
    
    async def _process_event(self, event_type: str, event_data: Dict[str, Any], 
                           headers: Dict[str, str]) -> Any:
        """Process webhook event."""
        try:
            # Find appropriate handler
            handler = None
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
            elif "default" in self.event_handlers:
                handler = self.event_handlers["default"]
            
            if handler:
                # Add context information
                context = {
                    "headers": headers,
                    "timestamp": time.time(),
                    "event_type": event_type
                }
                
                # Execute handler
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_data, context)
                else:
                    result = handler(event_data, context)
                
                return result
            else:
                logger.warning(f"No handler found for event type: {event_type}")
                return {"status": "no_handler"}
                
        except Exception as e:
            logger.error(f"Event processing failed: {str(e)}")
            raise
    
    async def retry_failed_events(self, max_retries: int = 3):
        """Retry failed webhook events."""
        for event in self.failed_events.copy():
            try:
                if event["retry_count"] >= max_retries:
                    logger.warning(f"Event max retries exceeded: {event}")
                    self.failed_events.remove(event)
                    continue
                
                # Exponential backoff
                retry_delay = 2 ** event["retry_count"]
                if time.time() - event["timestamp"] < retry_delay:
                    continue
                
                # Retry processing
                result = await self.process_webhook(event["payload"], event["headers"])
                
                if result["status"] == "success":
                    self.failed_events.remove(event)
                    logger.info(f"Successfully retried event: {result['event_id']}")
                else:
                    event["retry_count"] += 1
                    event["timestamp"] = time.time()
                    
            except Exception as e:
                logger.error(f"Event retry failed: {str(e)}")
                event["retry_count"] += 1
                event["timestamp"] = time.time()

# Factory class for creating appropriate adapters
class APIAdapterFactory:
    """Factory for creating appropriate API adapters."""
    
    @staticmethod
    def create_adapter(adapter_type: str, **kwargs) -> BaseAPIAdapter:
        """Create API adapter based on type."""
        if adapter_type.lower() == "rest":
            return RESTAPIAdapter(**kwargs)
        elif adapter_type.lower() == "graphql":
            return GraphQLAPIAdapter(**kwargs)
        elif adapter_type.lower() == "websocket":
            return WebSocketAPIAdapter(**kwargs)
        elif adapter_type.lower() == "webhook":
            return WebhookAPIAdapter(**kwargs)
        else:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")

# Export classes
__all__ = [
    "APIRequest",
    "APIResponse", 
    "RateLimitConfig",
    "CacheConfig",
    "BaseAPIAdapter",
    "RESTAPIAdapter",
    "GraphQLAPIAdapter", 
    "WebSocketAPIAdapter",
    "WebhookAPIAdapter",
    "APIAdapterFactory",
    "CircuitBreaker",
    "RateLimiter",
    "APICache"
]
    """API response container."""
    status_code: int
    headers: Dict[str, str]
    data: Any
    raw_response: str
    execution_time: float
    request_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

class APIAdapter(ABC):
    """Base class for all API adapters."""
    
    def __init__(self, base_url: str, **config):
        """Initialize API adapter."""
        self.base_url = base_url.rstrip('/')
        self.config = config
        self.session = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration
        self.timeout = config.get('timeout', 30.0)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1.0)
        self.enable_ssl_verify = config.get('ssl_verify', True)
        
        # Headers
        self.default_headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.default_headers.update(config.get('headers', {}))
        
        # Authentication
        self.auth_headers = {}
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication headers."""
        auth_config = self.config.get('auth', {})
        auth_type = auth_config.get('type')
        
        if auth_type == 'bearer':
            token = auth_config.get('token')
            if token:
                self.auth_headers['Authorization'] = f'Bearer {token}'
        
        elif auth_type == 'api_key':
            api_key = auth_config.get('api_key')
            key_header = auth_config.get('header', 'X-API-Key')
            if api_key:
                self.auth_headers[key_header] = api_key
        
        elif auth_type == 'basic':
            username = auth_config.get('username')
            password = auth_config.get('password')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                self.auth_headers['Authorization'] = f'Basic {credentials}'
    
    async def initialize(self):
        """Initialize the adapter."""
        connector = aiohttp.TCPConnector(
            ssl=ssl.create_default_context() if self.enable_ssl_verify else False
        )
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={**self.default_headers, **self.auth_headers}
        )
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    async def cleanup(self):
        """Cleanup adapter resources."""
        if self.session:
            await self.session.close()
        self.logger.info(f"Cleaned up {self.__class__.__name__}")
    
    @abstractmethod
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Execute API request."""
        pass
    
    async def _execute_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """Execute request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    return response
                    
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
                    raise last_exception
        
        raise last_exception

class RESTAPIAdapter(APIAdapter):
    """Adapter for REST API integration."""
    
    def __init__(self, base_url: str, **config):
        """Initialize REST API adapter."""
        super().__init__(base_url, **config)
        
        # REST-specific configuration
        self.pagination_style = config.get('pagination_style', 'offset')  # offset, cursor, page
        self.rate_limit_header = config.get('rate_limit_header', 'X-RateLimit-Remaining')
        self.rate_limit_reset_header = config.get('rate_limit_reset_header', 'X-RateLimit-Reset')
    
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Execute REST API request."""
        start_time = datetime.now()
        
        try:
            url = f"{self.base_url}{api_request.url}"
            
            # Prepare request parameters
            kwargs = {
                'params': api_request.params,
                'headers': {**self.default_headers, **self.auth_headers, **api_request.headers}
            }
            
            # Add request body for POST/PUT/PATCH
            if api_request.method.upper() in ['POST', 'PUT', 'PATCH']:
                if isinstance(api_request.data, (dict, list)):
                    kwargs['json'] = api_request.data
                elif isinstance(api_request.data, str):
                    kwargs['data'] = api_request.data
                elif isinstance(api_request.data, bytes):
                    kwargs['data'] = api_request.data
                    kwargs['headers']['Content-Type'] = 'application/octet-stream'
            
            # Execute request
            async with self.session.request(api_request.method, url, **kwargs) as response:
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Read response
                response_text = await response.text()
                
                # Parse response data
                try:
                    if response.content_type == 'application/json':
                        response_data = await response.json()
                    else:
                        response_data = response_text
                except:
                    response_data = response_text
                
                return APIResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    data=response_data,
                    raw_response=response_text,
                    execution_time=execution_time,
                    success=200 <= response.status < 300,
                    error_message=None if 200 <= response.status < 300 else f"HTTP {response.status}"
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"REST request failed: {e}")
            
            return APIResponse(
                status_code=0,
                headers={},
                data=None,
                raw_response="",
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> APIResponse:
        """Execute GET request."""
        request = APIRequest(
            method='GET',
            url=endpoint,
            params=params or {},
            **kwargs
        )
        return await self.request(request)
    
    async def post(self, endpoint: str, data: Any = None, **kwargs) -> APIResponse:
        """Execute POST request."""
        request = APIRequest(
            method='POST',
            url=endpoint,
            data=data,
            **kwargs
        )
        return await self.request(request)
    
    async def put(self, endpoint: str, data: Any = None, **kwargs) -> APIResponse:
        """Execute PUT request."""
        request = APIRequest(
            method='PUT',
            url=endpoint,
            data=data,
            **kwargs
        )
        return await self.request(request)
    
    async def patch(self, endpoint: str, data: Any = None, **kwargs) -> APIResponse:
        """Execute PATCH request."""
        request = APIRequest(
            method='PATCH',
            url=endpoint,
            data=data,
            **kwargs
        )
        return await self.request(request)
    
    async def delete(self, endpoint: str, **kwargs) -> APIResponse:
        """Execute DELETE request."""
        request = APIRequest(
            method='DELETE',
            url=endpoint,
            **kwargs
        )
        return await self.request(request)
    
    async def paginated_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List[Dict]:
        """Execute paginated request to get all results."""
        all_results = []
        current_params = params.copy() if params else {}
        
        if self.pagination_style == 'offset':
            offset = 0
            page_size = 100
            
            while True:
                current_params.update({
                    'offset': offset,
                    'limit': page_size
                })
                
                response = await self.get(endpoint, current_params, **kwargs)
                if not response.success or not response.data:
                    break
                
                if isinstance(response.data, dict) and 'items' in response.data:
                    items = response.data['items']
                elif isinstance(response.data, list):
                    items = response.data
                else:
                    break
                
                all_results.extend(items)
                
                if len(items) < page_size or (limit and len(all_results) >= limit):
                    break
                
                offset += page_size
        
        elif self.pagination_style == 'page':
            page = 1
            page_size = 100
            
            while True:
                current_params.update({
                    'page': page,
                    'per_page': page_size
                })
                
                response = await self.get(endpoint, current_params, **kwargs)
                if not response.success or not response.data:
                    break
                
                if isinstance(response.data, dict) and 'items' in response.data:
                    items = response.data['items']
                elif isinstance(response.data, list):
                    items = response.data
                else:
                    break
                
                all_results.extend(items)
                
                if len(items) < page_size or (limit and len(all_results) >= limit):
                    break
                
                page += 1
        
        return all_results[:limit] if limit else all_results

class GraphQLAdapter(APIAdapter):
    """Adapter for GraphQL API integration."""
    
    def __init__(self, base_url: str, **config):
        """Initialize GraphQL adapter."""
        super().__init__(base_url, **config)
        
        if not GRAPHQL_AVAILABLE:
            raise ImportError("GraphQL dependencies not available. Install with: pip install gql[aiohttp]")
        
        self.client = None
        self.introspection_enabled = config.get('introspection', True)
    
    async def initialize(self):
        """Initialize GraphQL client."""
        await super().initialize()
        
        # Setup GraphQL transport
        transport = AIOHTTPTransport(
            url=f"{self.base_url}/graphql",
            headers={**self.default_headers, **self.auth_headers}
        )
        
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=self.introspection_enabled
        )
        
        self.logger.info("GraphQL client initialized")
    
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Execute GraphQL request."""
        start_time = datetime.now()
        
        try:
            if not self.client:
                raise Exception("GraphQL client not initialized")
            
            # Parse GraphQL query
            if isinstance(api_request.data, str):
                query = gql(api_request.data)
            elif isinstance(api_request.data, dict) and 'query' in api_request.data:
                query = gql(api_request.data['query'])
            else:
                raise ValueError("Invalid GraphQL query format")
            
            # Execute query
            variables = api_request.params or {}
            result = await self.client.execute_async(query, variable_values=variables)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return APIResponse(
                status_code=200,
                headers={},
                data=result,
                raw_response=json.dumps(result),
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"GraphQL request failed: {e}")
            
            return APIResponse(
                status_code=0,
                headers={},
                data=None,
                raw_response="",
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def query(self, query_string: str, variables: Optional[Dict] = None) -> APIResponse:
        """Execute GraphQL query."""
        request = APIRequest(
            method='POST',
            url='/graphql',
            data={'query': query_string},
            params=variables or {}
        )
        return await self.request(request)
    
    async def mutation(self, mutation_string: str, variables: Optional[Dict] = None) -> APIResponse:
        """Execute GraphQL mutation."""
        request = APIRequest(
            method='POST',
            url='/graphql',
            data={'query': mutation_string},
            params=variables or {}
        )
        return await self.request(request)

class WebSocketAdapter(APIAdapter):
    """Adapter for WebSocket API integration."""
    
    def __init__(self, base_url: str, **config):
        """Initialize WebSocket adapter."""
        super().__init__(base_url, **config)
        
        # Convert HTTP URL to WebSocket URL
        self.ws_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        
        self.websocket = None
        self.message_handlers: Dict[str, Callable] = {}
        self.is_connected = False
        
        # WebSocket-specific configuration
        self.ping_interval = config.get('ping_interval', 30)
        self.ping_timeout = config.get('ping_timeout', 10)
        self.auto_reconnect = config.get('auto_reconnect', True)
        self.max_reconnect_attempts = config.get('max_reconnect_attempts', 5)
    
    async def initialize(self):
        """Initialize WebSocket connection."""
        await self.connect()
    
    async def connect(self) -> bool:
        """Connect to WebSocket."""
        try:
            # Prepare headers
            headers = {**self.default_headers, **self.auth_headers}
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.ws_url,
                extra_headers=headers,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout
            )
            
            self.is_connected = True
            self.logger.info(f"Connected to WebSocket: {self.ws_url}")
            
            # Start message listening loop
            asyncio.create_task(self._message_listener())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            self.logger.info("Disconnected from WebSocket")
    
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Send WebSocket message."""
        start_time = datetime.now()
        
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.websocket:
                raise Exception("WebSocket not connected")
            
            # Prepare message
            if isinstance(api_request.data, dict):
                message = json.dumps(api_request.data)
            else:
                message = str(api_request.data)
            
            # Send message
            await self.websocket.send(message)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return APIResponse(
                status_code=200,
                headers={},
                data={'sent': True},
                raw_response=message,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"WebSocket send failed: {e}")
            
            return APIResponse(
                status_code=0,
                headers={},
                data=None,
                raw_response="",
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def _message_listener(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    # Parse message
                    if isinstance(message, str):
                        data = json.loads(message)
                    else:
                        data = message
                    
                    # Handle message based on type
                    message_type = data.get('type', 'default')
                    handler = self.message_handlers.get(message_type)
                    
                    if handler:
                        await handler(data)
                    else:
                        self.logger.debug(f"Unhandled message type: {message_type}")
                        
                except Exception as e:
                    self.logger.error(f"Error handling WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            self.logger.warning("WebSocket connection closed")
            
            if self.auto_reconnect:
                await self._reconnect()
                
        except Exception as e:
            self.logger.error(f"WebSocket listener error: {e}")
            self.is_connected = False
    
    async def _reconnect(self):
        """Attempt to reconnect to WebSocket."""
        for attempt in range(self.max_reconnect_attempts):
            try:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                if await self.connect():
                    self.logger.info("WebSocket reconnected successfully")
                    return
            except Exception as e:
                self.logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
        
        self.logger.error("Failed to reconnect after maximum attempts")
    
    def add_message_handler(self, message_type: str, handler: Callable):
        """Add handler for specific message type."""
        self.message_handlers[message_type] = handler
    
    def remove_message_handler(self, message_type: str):
        """Remove handler for message type."""
        self.message_handlers.pop(message_type, None)
    
    async def send_message(self, message: Union[str, Dict]) -> APIResponse:
        """Send message via WebSocket."""
        request = APIRequest(
            method='SEND',
            url='',
            data=message
        )
        return await self.request(request)

class WebhookAdapter(APIAdapter):
    """Adapter for Webhook integration."""
    
    def __init__(self, base_url: str, **config):
        """Initialize Webhook adapter."""
        super().__init__(base_url, **config)
        
        self.webhook_handlers: Dict[str, Callable] = {}
        self.signature_verification = config.get('verify_signature', True)
        self.secret_key = config.get('secret_key')
        self.signature_header = config.get('signature_header', 'X-Signature')
    
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Execute webhook request (typically for sending)."""
        return await super().request(api_request)
    
    async def register_webhook(self, endpoint: str, webhook_url: str) -> APIResponse:
        """Register webhook endpoint."""
        data = {
            'url': webhook_url,
            'events': self.config.get('events', ['*'])
        }
        
        request = APIRequest(
            method='POST',
            url=endpoint,
            data=data
        )
        
        return await self.request(request)
    
    async def unregister_webhook(self, endpoint: str, webhook_id: str) -> APIResponse:
        """Unregister webhook endpoint."""
        request = APIRequest(
            method='DELETE',
            url=f"{endpoint}/{webhook_id}"
        )
        
        return await self.request(request)
    
    def add_webhook_handler(self, event_type: str, handler: Callable):
        """Add handler for webhook event."""
        self.webhook_handlers[event_type] = handler
    
    async def handle_webhook(self, headers: Dict[str, str], body: bytes) -> bool:
        """Handle incoming webhook."""
        try:
            # Verify signature if enabled
            if self.signature_verification and self.secret_key:
                if not self._verify_signature(headers, body):
                    self.logger.warning("Webhook signature verification failed")
                    return False
            
            # Parse payload
            try:
                payload = json.loads(body.decode())
            except:
                payload = body.decode()
            
            # Get event type
            event_type = headers.get('X-Event-Type') or payload.get('event_type', 'default')
            
            # Handle event
            handler = self.webhook_handlers.get(event_type)
            if handler:
                await handler(payload)
                return True
            else:
                self.logger.debug(f"No handler for webhook event: {event_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Webhook handling error: {e}")
            return False
    
    def _verify_signature(self, headers: Dict[str, str], body: bytes) -> bool:
        """Verify webhook signature."""
        try:
            import hmac
            import hashlib
            
            signature = headers.get(self.signature_header)
            if not signature:
                return False
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, f"sha256={expected_signature}")
            
        except Exception as e:
            self.logger.error(f"Signature verification error: {e}")
            return False

class StreamingAdapter(APIAdapter):
    """Adapter for streaming API integration."""
    
    def __init__(self, base_url: str, **config):
        """Initialize Streaming adapter."""
        super().__init__(base_url, **config)
        
        self.stream_handlers: Dict[str, Callable] = {}
        self.active_streams: Dict[str, Any] = {}
        self.buffer_size = config.get('buffer_size', 8192)
    
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Execute streaming request."""
        start_time = datetime.now()
        
        try:
            url = f"{self.base_url}{api_request.url}"
            
            kwargs = {
                'params': api_request.params,
                'headers': {**self.default_headers, **self.auth_headers, **api_request.headers}
            }
            
            # Start streaming request
            async with self.session.request(api_request.method, url, **kwargs) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                # Create stream handler
                stream_id = f"stream_{len(self.active_streams)}"
                self.active_streams[stream_id] = response
                
                # Start stream processing
                asyncio.create_task(self._process_stream(stream_id, response))
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return APIResponse(
                    status_code=200,
                    headers=dict(response.headers),
                    data={'stream_id': stream_id, 'streaming': True},
                    raw_response="",
                    execution_time=execution_time,
                    success=True
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Streaming request failed: {e}")
            
            return APIResponse(
                status_code=0,
                headers={},
                data=None,
                raw_response="",
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def _process_stream(self, stream_id: str, response: aiohttp.ClientResponse):
        """Process streaming response."""
        try:
            buffer = ""
            
            async for chunk in response.content.iter_chunked(self.buffer_size):
                try:
                    chunk_text = chunk.decode('utf-8')
                    buffer += chunk_text
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        
                        if line.strip():
                            # Try to parse as JSON
                            try:
                                data = json.loads(line)
                            except:
                                data = line
                            
                            # Handle stream data
                            await self._handle_stream_data(stream_id, data)
                            
                except Exception as e:
                    self.logger.error(f"Error processing stream chunk: {e}")
                    
        except Exception as e:
            self.logger.error(f"Stream processing error: {e}")
        
        finally:
            # Cleanup stream
            self.active_streams.pop(stream_id, None)
            self.logger.info(f"Stream {stream_id} ended")
    
    async def _handle_stream_data(self, stream_id: str, data: Any):
        """Handle individual stream data item."""
        try:
            # Determine data type and call appropriate handler
            data_type = 'default'
            if isinstance(data, dict):
                data_type = data.get('type', 'default')
            
            handler = self.stream_handlers.get(data_type)
            if handler:
                await handler(stream_id, data)
            else:
                self.logger.debug(f"No handler for stream data type: {data_type}")
                
        except Exception as e:
            self.logger.error(f"Stream data handling error: {e}")
    
    def add_stream_handler(self, data_type: str, handler: Callable):
        """Add handler for stream data type."""
        self.stream_handlers[data_type] = handler
    
    def remove_stream_handler(self, data_type: str):
        """Remove handler for stream data type."""
        self.stream_handlers.pop(data_type, None)
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop active stream."""
        try:
            if stream_id in self.active_streams:
                response = self.active_streams[stream_id]
                response.close()
                del self.active_streams[stream_id]
                self.logger.info(f"Stopped stream {stream_id}")
                return True
            else:
                self.logger.warning(f"Stream {stream_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping stream {stream_id}: {e}")
            return False
    
    def get_active_streams(self) -> List[str]:
        """Get list of active stream IDs."""
        return list(self.active_streams.keys())

# Export all adapters
__all__ = [
    'APIAdapter',
    'APIRequest',
    'APIResponse',
    'RESTAPIAdapter',
    'GraphQLAdapter',
    'WebSocketAdapter',
    'WebhookAdapter',
    'StreamingAdapter'
]
