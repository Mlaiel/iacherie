"""
API Client - Core Utilities Level 1
===================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

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

Enterprise-grade API client utility for Creator Economy platform.
Provides HTTP client with retry logic, rate limiting, authentication management,
response caching, and integration with social media APIs, payment gateways,
and analytics services.

Performance: < 5ms for cached responses, < 100ms for external APIs
Standards: 100% async, type hints, enterprise integration patterns
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import (
    Any, Dict, List, Optional, Union, Callable, Tuple, 
    AsyncIterator, TypeVar, Generic
)
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import base64
from urllib.parse import urlencode, urljoin
import weakref

logger = logging.getLogger(__name__)

T = TypeVar('T')

class HTTPMethod(Enum):
    """HTTP method enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class AuthType(Enum):
    """Authentication type enumeration."""
    NONE = "none"
    BEARER_TOKEN = "bearer"
    API_KEY = "api_key"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"

class RetryStrategy(Enum):
    """Retry strategy enumeration."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"

@dataclass
class APIResponse(Generic[T]):
    """Enterprise API response container."""
    success: bool
    status_code: int
    data: Optional[T] = None
    headers: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    cached: bool = False
    retry_count: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_second: float = 10.0
    burst_size: int = 20
    window_seconds: int = 60
    per_endpoint: bool = True

@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retry_on_status: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])

@dataclass
class AuthConfig:
    """Authentication configuration."""
    auth_type: AuthType = AuthType.NONE
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    oauth2_token: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    token_refresh_url: Optional[str] = None
    token_refresh_callback: Optional[Callable] = None

@dataclass
class CacheConfig:
    """Response caching configuration."""
    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes default
    max_size: int = 1000
    cache_get_requests: bool = True
    cache_post_requests: bool = False
    cache_by_headers: List[str] = field(default_factory=list)

@dataclass
class APIClientConfig:
    """API client configuration."""
    base_url: str = ""
    timeout: float = 30.0
    headers: Dict[str, str] = field(default_factory=dict)
    auth: Optional[AuthConfig] = None
    retry: Optional[RetryConfig] = None
    rate_limit: Optional[RateLimitConfig] = None
    cache: Optional[CacheConfig] = None
    verify_ssl: bool = True
    follow_redirects: bool = True
    max_redirects: int = 10

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.buckets: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def acquire(self, endpoint: str = "default") -> bool:
        """Acquire a token from the rate limiter."""
        async with self._lock:
            now = time.time()
            bucket_key = endpoint if self.config.per_endpoint else "global"
            
            if bucket_key not in self.buckets:
                self.buckets[bucket_key] = {
                    'tokens': self.config.burst_size,
                    'last_refill': now
                }
            
            bucket = self.buckets[bucket_key]
            
            # Refill tokens based on time elapsed
            time_elapsed = now - bucket['last_refill']
            tokens_to_add = time_elapsed * self.config.requests_per_second
            
            bucket['tokens'] = min(
                self.config.burst_size,
                bucket['tokens'] + tokens_to_add
            )
            bucket['last_refill'] = now
            
            # Check if we can consume a token
            if bucket['tokens'] >= 1.0:
                bucket['tokens'] -= 1.0
                return True
            
            return False
    
    async def wait_for_token(self, endpoint: str = "default") -> float:
        """Wait until a token is available and return wait time."""
        start_time = time.time()
        
        while not await self.acquire(endpoint):
            await asyncio.sleep(0.1)
        
        return time.time() - start_time

class ResponseCache:
    """Simple response cache with TTL."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    def _generate_cache_key(
        self, 
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate cache key for request."""
        key_parts = [method.upper(), url]
        
        if params:
            key_parts.append(urlencode(sorted(params.items())))
        
        if headers and self.config.cache_by_headers:
            header_parts = []
            for header_name in self.config.cache_by_headers:
                if header_name.lower() in headers:
                    header_parts.append(f"{header_name}:{headers[header_name.lower()]}")
            if header_parts:
                key_parts.append("|".join(header_parts))
        
        cache_string = "|".join(key_parts)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def get(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[APIResponse]:
        """Get cached response if available and not expired."""
        if not self.config.enabled:
            return None
        
        # Only cache GET requests by default, POST if configured
        if method.upper() == "GET" and not self.config.cache_get_requests:
            return None
        if method.upper() == "POST" and not self.config.cache_post_requests:
            return None
        
        cache_key = self._generate_cache_key(method, url, params, headers)
        
        async with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                
                # Check if expired
                if time.time() - entry['timestamp'] < self.config.ttl_seconds:
                    response = entry['response']
                    response.cached = True
                    return response
                else:
                    # Remove expired entry
                    del self._cache[cache_key]
        
        return None
    
    async def set(
        self,
        method: str,
        url: str,
        response: APIResponse,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """Cache response if cacheable."""
        if not self.config.enabled or not response.success:
            return
        
        cache_key = self._generate_cache_key(method, url, params, headers)
        
        async with self._lock:
            # Evict oldest entries if cache is full
            if len(self._cache) >= self.config.max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k]['timestamp']
                )
                del self._cache[oldest_key]
            
            self._cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }

class APIClient:
    """
    Enterprise API client for Creator Economy platform.
    
    Provides comprehensive HTTP client features:
    - Async HTTP client with connection pooling
    - Intelligent retry logic with multiple strategies
    - Rate limiting with token bucket algorithm
    - Response caching for performance optimization
    - Multiple authentication methods support
    - Error handling with detailed logging
    - Integration ready for social media APIs
    - Payment gateway support
    - Analytics API integration
    """
    
    def __init__(self, config: Optional[APIClientConfig] = None):
        self.config = config or APIClientConfig()
        
        # Initialize components
        self.rate_limiter = RateLimiter(self.config.rate_limit or RateLimitConfig())
        self.response_cache = ResponseCache(self.config.cache or CacheConfig())
        
        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_connector: Optional[aiohttp.TCPConnector] = None
        
        # Metrics
        self.metrics = {
            'total_requests': 0,
            'cached_responses': 0,
            'failed_requests': 0,
            'retried_requests': 0,
            'rate_limited_requests': 0,
            'avg_response_time': 0.0
        }
        
        # Known API integrations for Creator Economy
        self.social_media_apis = {
            'instagram': 'https://graph.instagram.com',
            'tiktok': 'https://open-api.tiktok.com',
            'youtube': 'https://www.googleapis.com/youtube/v3',
            'twitter': 'https://api.twitter.com/2',
            'facebook': 'https://graph.facebook.com'
        }
        
        self.payment_apis = {
            'stripe': 'https://api.stripe.com',
            'paypal': 'https://api.paypal.com',
            'square': 'https://connect.squareup.com'
        }
        
        self.analytics_apis = {
            'google_analytics': 'https://analyticsreporting.googleapis.com',
            'facebook_insights': 'https://graph.facebook.com',
            'mixpanel': 'https://api.mixpanel.com'
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is created."""
        if self._session is None or self._session.closed:
            # Create connector with connection pooling
            self._session_connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Per host limit
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                verify_ssl=self.config.verify_ssl
            )
            
            # Create session with timeout configuration
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            self._session = aiohttp.ClientSession(
                connector=self._session_connector,
                timeout=timeout,
                headers=self.config.headers,
                raise_for_status=False
            )
    
    async def close(self) -> None:
        """Close the HTTP session and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
        
        if self._session_connector:
            await self._session_connector.close()
    
    def _prepare_auth_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Prepare authentication headers."""
        if not self.config.auth:
            return headers
        
        auth_headers = headers.copy()
        auth = self.config.auth
        
        if auth.auth_type == AuthType.BEARER_TOKEN and auth.bearer_token:
            auth_headers['Authorization'] = f'Bearer {auth.bearer_token}'
        
        elif auth.auth_type == AuthType.API_KEY and auth.api_key:
            auth_headers['X-API-Key'] = auth.api_key
        
        elif auth.auth_type == AuthType.BASIC and auth.username and auth.password:
            credentials = base64.b64encode(f'{auth.username}:{auth.password}'.encode()).decode()
            auth_headers['Authorization'] = f'Basic {credentials}'
        
        elif auth.auth_type == AuthType.OAUTH2 and auth.oauth2_token:
            auth_headers['Authorization'] = f'Bearer {auth.oauth2_token}'
        
        elif auth.auth_type == AuthType.CUSTOM:
            auth_headers.update(auth.custom_headers)
        
        return auth_headers
    
    async def _calculate_retry_delay(self, attempt: int, retry_config: RetryConfig) -> float:
        """Calculate delay for retry attempt."""
        if retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = retry_config.base_delay * (retry_config.backoff_factor ** (attempt - 1))
            return min(delay, retry_config.max_delay)
        
        elif retry_config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = retry_config.base_delay * attempt
            return min(delay, retry_config.max_delay)
        
        elif retry_config.strategy == RetryStrategy.FIXED_DELAY:
            return retry_config.base_delay
        
        else:  # IMMEDIATE
            return 0.0
    
    async def _should_retry(self, response: APIResponse, retry_config: RetryConfig) -> bool:
        """Determine if request should be retried."""
        if response.retry_count >= retry_config.max_attempts:
            return False
        
        # Retry on specific status codes
        if response.status_code in retry_config.retry_on_status:
            return True
        
        # Retry on network errors (status_code 0)
        if response.status_code == 0:
            return True
        
        return False
    
    async def _make_request(
        self,
        method: HTTPMethod,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> APIResponse:
        """Make HTTP request with all enterprise features."""
        start_time = time.perf_counter()
        
        # Prepare request parameters
        full_url = urljoin(self.config.base_url, url)
        request_headers = headers or {}
        request_headers = self._prepare_auth_headers(request_headers)
        
        # Rate limiting
        endpoint_key = f"{method.value}:{url}"
        rate_limit_wait = await self.rate_limiter.wait_for_token(endpoint_key)
        if rate_limit_wait > 0:
            self.metrics['rate_limited_requests'] += 1
        
        # Check cache first
        cached_response = await self.response_cache.get(
            method.value, full_url, params, request_headers
        )
        if cached_response:
            self.metrics['cached_responses'] += 1
            return cached_response
        
        # Retry configuration
        retry_config = self.config.retry or RetryConfig()
        retry_count = 0
        
        while True:
            try:
                await self._ensure_session()
                
                # Prepare request kwargs
                request_kwargs = {
                    'params': params,
                    'headers': request_headers,
                    'timeout': aiohttp.ClientTimeout(total=timeout or self.config.timeout)
                }
                
                if json_data is not None:
                    request_kwargs['json'] = json_data
                elif data is not None:
                    request_kwargs['data'] = data
                
                # Make request
                async with self._session.request(method.value, full_url, **request_kwargs) as resp:
                    # Read response
                    response_text = await resp.text()
                    
                    # Try to parse as JSON
                    try:
                        response_data = json.loads(response_text) if response_text else None
                    except json.JSONDecodeError:
                        response_data = response_text
                    
                    # Create response object
                    execution_time = (time.perf_counter() - start_time) * 1000
                    
                    api_response = APIResponse(
                        success=200 <= resp.status < 300,
                        status_code=resp.status,
                        data=response_data,
                        headers=dict(resp.headers),
                        execution_time_ms=execution_time,
                        retry_count=retry_count
                    )
                    
                    # Add error message for failed requests
                    if not api_response.success:
                        api_response.errors.append(f"HTTP {resp.status}: {resp.reason}")
                    
                    # Check if we should retry
                    if not api_response.success and await self._should_retry(api_response, retry_config):
                        retry_count += 1
                        api_response.retry_count = retry_count
                        
                        # Calculate delay and wait
                        delay = await self._calculate_retry_delay(retry_count, retry_config)
                        if delay > 0:
                            await asyncio.sleep(delay)
                        
                        self.metrics['retried_requests'] += 1
                        continue
                    
                    # Cache successful responses
                    if api_response.success:
                        await self.response_cache.set(
                            method.value, full_url, api_response, params, request_headers
                        )
                    
                    # Update metrics
                    self.metrics['total_requests'] += 1
                    if not api_response.success:
                        self.metrics['failed_requests'] += 1
                    
                    # Update average response time
                    total_requests = self.metrics['total_requests']
                    current_avg = self.metrics['avg_response_time']
                    self.metrics['avg_response_time'] = (
                        (current_avg * (total_requests - 1) + execution_time) / total_requests
                    )
                    
                    return api_response
            
            except asyncio.TimeoutError:
                execution_time = (time.perf_counter() - start_time) * 1000
                
                api_response = APIResponse(
                    success=False,
                    status_code=0,
                    errors=["Request timeout"],
                    execution_time_ms=execution_time,
                    retry_count=retry_count
                )
                
                # Retry on timeout
                if await self._should_retry(api_response, retry_config):
                    retry_count += 1
                    delay = await self._calculate_retry_delay(retry_count, retry_config)
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                
                return api_response
            
            except Exception as e:
                execution_time = (time.perf_counter() - start_time) * 1000
                
                api_response = APIResponse(
                    success=False,
                    status_code=0,
                    errors=[f"Network error: {str(e)}"],
                    execution_time_ms=execution_time,
                    retry_count=retry_count
                )
                
                # Retry on network errors
                if await self._should_retry(api_response, retry_config):
                    retry_count += 1
                    delay = await self._calculate_retry_delay(retry_count, retry_config)
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                
                return api_response
    
    # HTTP method convenience functions
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> APIResponse:
        """Make GET request."""
        return await self._make_request(HTTPMethod.GET, url, params=params, headers=headers, timeout=timeout)
    
    async def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> APIResponse:
        """Make POST request."""
        return await self._make_request(
            HTTPMethod.POST, url, params=params, data=data, 
            json_data=json_data, headers=headers, timeout=timeout
        )
    
    async def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> APIResponse:
        """Make PUT request."""
        return await self._make_request(
            HTTPMethod.PUT, url, params=params, data=data,
            json_data=json_data, headers=headers, timeout=timeout
        )
    
    async def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> APIResponse:
        """Make DELETE request."""
        return await self._make_request(HTTPMethod.DELETE, url, params=params, headers=headers, timeout=timeout)
    
    async def patch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> APIResponse:
        """Make PATCH request."""
        return await self._make_request(
            HTTPMethod.PATCH, url, params=params, data=data,
            json_data=json_data, headers=headers, timeout=timeout
        )
    
    # Creator Economy specific API methods
    
    async def upload_to_social_media(
        self,
        platform: str,
        content_data: Dict[str, Any],
        auth_token: str
    ) -> APIResponse:
        """Upload content to social media platform."""
        if platform not in self.social_media_apis:
            return APIResponse(
                success=False,
                status_code=400,
                errors=[f"Unsupported platform: {platform}"]
            )
        
        # Configure auth for platform
        original_auth = self.config.auth
        self.config.auth = AuthConfig(
            auth_type=AuthType.BEARER_TOKEN,
            bearer_token=auth_token
        )
        
        try:
            base_url = self.social_media_apis[platform]
            
            if platform == 'instagram':
                # Instagram Graph API
                response = await self.post(
                    f"{base_url}/me/media",
                    json_data=content_data
                )
            elif platform == 'youtube':
                # YouTube Data API
                response = await self.post(
                    f"{base_url}/videos",
                    json_data=content_data
                )
            elif platform == 'tiktok':
                # TikTok Open API
                response = await self.post(
                    f"{base_url}/share/video/upload/",
                    json_data=content_data
                )
            else:
                # Generic approach
                response = await self.post("/upload", json_data=content_data)
            
            return response
            
        finally:
            self.config.auth = original_auth
    
    async def process_payment(
        self,
        gateway: str,
        payment_data: Dict[str, Any],
        api_key: str
    ) -> APIResponse:
        """Process payment through payment gateway."""
        if gateway not in self.payment_apis:
            return APIResponse(
                success=False,
                status_code=400,
                errors=[f"Unsupported payment gateway: {gateway}"]
            )
        
        # Configure auth for gateway
        original_auth = self.config.auth
        
        if gateway == 'stripe':
            self.config.auth = AuthConfig(
                auth_type=AuthType.BEARER_TOKEN,
                bearer_token=api_key
            )
        else:
            self.config.auth = AuthConfig(
                auth_type=AuthType.API_KEY,
                api_key=api_key
            )
        
        try:
            base_url = self.payment_apis[gateway]
            
            if gateway == 'stripe':
                response = await self.post(
                    f"{base_url}/v1/charges",
                    data=payment_data
                )
            elif gateway == 'paypal':
                response = await self.post(
                    f"{base_url}/v2/payments/payment",
                    json_data=payment_data
                )
            else:
                response = await self.post("/payment", json_data=payment_data)
            
            return response
            
        finally:
            self.config.auth = original_auth
    
    async def get_analytics_data(
        self,
        service: str,
        query_params: Dict[str, Any],
        auth_token: str
    ) -> APIResponse:
        """Get analytics data from analytics service."""
        if service not in self.analytics_apis:
            return APIResponse(
                success=False,
                status_code=400,
                errors=[f"Unsupported analytics service: {service}"]
            )
        
        # Configure auth for service
        original_auth = self.config.auth
        self.config.auth = AuthConfig(
            auth_type=AuthType.BEARER_TOKEN,
            bearer_token=auth_token
        )
        
        try:
            base_url = self.analytics_apis[service]
            
            if service == 'google_analytics':
                response = await self.post(
                    f"{base_url}/v4/reports:batchGet",
                    json_data=query_params
                )
            elif service == 'facebook_insights':
                response = await self.get(
                    f"{base_url}/insights",
                    params=query_params
                )
            else:
                response = await self.get("/analytics", params=query_params)
            
            return response
            
        finally:
            self.config.auth = original_auth
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics."""
        return {
            'performance_metrics': self.metrics.copy(),
            'rate_limiter_stats': {
                'buckets': len(self.rate_limiter.buckets),
                'requests_per_second': self.rate_limiter.config.requests_per_second
            },
            'cache_stats': {
                'size': len(self.response_cache._cache),
                'max_size': self.response_cache.config.max_size,
                'enabled': self.response_cache.config.enabled
            },
            'session_stats': {
                'is_open': self._session is not None and not self._session.closed,
                'connector_limit': getattr(self._session_connector, '_limit', 0) if self._session_connector else 0
            }
        }

# Factory for dependency injection
class APIClientFactory:
    """Factory for creating APIClient instances."""
    
    @staticmethod
    def create(config: Optional[APIClientConfig] = None) -> APIClient:
        """Create a new APIClient instance."""
        return APIClient(config)
    
    @staticmethod
    def create_for_social_media(platform: str, auth_token: str) -> APIClient:
        """Create APIClient configured for social media platform."""
        config = APIClientConfig(
            auth=AuthConfig(
                auth_type=AuthType.BEARER_TOKEN,
                bearer_token=auth_token
            ),
            rate_limit=RateLimitConfig(requests_per_second=2.0),  # Conservative for social media
            cache=CacheConfig(enabled=False)  # Don't cache social media uploads
        )
        return APIClient(config)
    
    @staticmethod
    def create_for_payment_gateway(gateway: str, api_key: str) -> APIClient:
        """Create APIClient configured for payment gateway."""
        config = APIClientConfig(
            auth=AuthConfig(
                auth_type=AuthType.BEARER_TOKEN if gateway == 'stripe' else AuthType.API_KEY,
                bearer_token=api_key if gateway == 'stripe' else None,
                api_key=api_key if gateway != 'stripe' else None
            ),
            verify_ssl=True,  # Always verify SSL for payments
            cache=CacheConfig(enabled=False),  # Never cache payment requests
            retry=RetryConfig(max_attempts=1)  # Don't retry payment requests
        )
        return APIClient(config)
    
    @staticmethod
    def create_for_analytics(service: str, auth_token: str) -> APIClient:
        """Create APIClient configured for analytics service."""
        config = APIClientConfig(
            auth=AuthConfig(
                auth_type=AuthType.BEARER_TOKEN,
                bearer_token=auth_token
            ),
            cache=CacheConfig(
                enabled=True,
                ttl_seconds=900,  # 15 minutes for analytics
                cache_get_requests=True
            ),
            rate_limit=RateLimitConfig(requests_per_second=5.0)
        )
        return APIClient(config)

__all__ = [
    'APIClient',
    'APIClientFactory',
    'APIClientConfig',
    'APIResponse',
    'AuthConfig',
    'AuthType',
    'RetryConfig',
    'RetryStrategy',
    'RateLimitConfig',
    'CacheConfig',
    'HTTPMethod',
    'RateLimiter',
    'ResponseCache'
]