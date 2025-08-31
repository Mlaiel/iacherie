"""Enterprise Platform Adapters - Base Adapter Framework

This module provides the foundational adapter framework for all external platform
integrations, following enterprise design patterns with comprehensive error handling,
rate limiting, authentication management, and performance optimization.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Components:
- BasePlatformAdapter: Abstract base class for all platform adapters
- AdapterRegistry: Central registry for adapter management
- AdapterFactory: Factory pattern for adapter instantiation
- AdapterMetrics: Performance monitoring and analytics
- AdapterAuth: Authentication management across platforms
- AdapterRateLimit: Intelligent rate limiting and throttling
- AdapterCache: Caching strategy for optimal performance
- AdapterError: Comprehensive error handling framework
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import time
from contextlib import asynccontextmanager
import aiohttp
import redis
from tenacity import retry, stop_after_attempt, wait_exponential

# Type definitions
T = TypeVar('T')
AdapterResponse = TypeVar('AdapterResponse')

# Configure logging
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Enumeration of supported platform types."""    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    PAYMENT_GATEWAY = "payment_gateway"
    CLOUD_STORAGE = "cloud_storage"
    ANALYTICS_SERVICE = "analytics_service"
    CONTENT_DELIVERY = "content_delivery"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    NOTIFICATION_SERVICE = "notification_service"
    AI_PLATFORM = "ai_platform"
    CONTENT_PROTECTION = "content_protection"
    EMAIL_MARKETING = "email_marketing"
    SEO_PLATFORM = "seo_platform"

class AdapterStatus(Enum):
    """Adapter operational status."""    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class AuthenticationType(Enum):
    """Authentication method types."""    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"

@dataclass
class AdapterCredentials:
    """Secure credential storage for platform authentication."""    auth_type: AuthenticationType
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    base_url: Optional[str] = None
    
    def is_token_expired(self) -> bool:
        """Check if the access token is expired."""        if not self.token_expires_at:
            return False
        return datetime.now() >= self.token_expires_at
    
    def to_headers(self) -> Dict[str, str]:
        """Convert credentials to HTTP headers."""        headers = self.custom_headers.copy()
        
        if self.auth_type == AuthenticationType.API_KEY and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.auth_type == AuthenticationType.BEARER_TOKEN and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.auth_type == AuthenticationType.JWT and self.access_token:
            headers["Authorization"] = f"JWT {self.access_token}"
        
        return headers

@dataclass
class RateLimitConfig:
    """Rate limiting configuration for adapters."""    requests_per_second: float = 10.0
    requests_per_minute: float = 600.0
    requests_per_hour: float = 36000.0
    burst_limit: int = 50
    backoff_factor: float = 2.0
    max_retries: int = 3
    
class AdapterMetrics:
    """Performance metrics tracking for adapters."""    
    def __init__(self, adapter_name: str, redis_client: Optional[redis.Redis] = None):
        self.adapter_name = adapter_name
        self.redis_client = redis_client
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'average_response_time': 0.0,
            'total_response_time': 0.0,
            'last_request_time': None,
            'last_error': None,
            'error_count_by_type': {},
            'requests_by_endpoint': {}
        }
    
    def record_request(self, endpoint: str, response_time: float, success: bool, error: Optional[str] = None):
        """Record request metrics."""        self.metrics['total_requests'] += 1
        self.metrics['total_response_time'] += response_time
        self.metrics['average_response_time'] = self.metrics['total_response_time'] / self.metrics['total_requests']
        self.metrics['last_request_time'] = datetime.now()
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
            if error:
                self.metrics['last_error'] = error
                error_type = type(error).__name__ if isinstance(error, Exception) else str(error)
                self.metrics['error_count_by_type'][error_type] = self.metrics['error_count_by_type'].get(error_type, 0) + 1
        
        # Track by endpoint
        if endpoint not in self.metrics['requests_by_endpoint']:
            self.metrics['requests_by_endpoint'][endpoint] = {'count': 0, 'avg_time': 0.0, 'total_time': 0.0}
        
        endpoint_metrics = self.metrics['requests_by_endpoint'][endpoint]
        endpoint_metrics['count'] += 1
        endpoint_metrics['total_time'] += response_time
        endpoint_metrics['avg_time'] = endpoint_metrics['total_time'] / endpoint_metrics['count']
        
        # Store in Redis if available
        if self.redis_client:
            self._store_metrics_in_redis()
    
    def record_rate_limit(self):
        """Record rate limiting event."""        self.metrics['rate_limited_requests'] += 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""        if self.metrics['total_requests'] == 0:
            return 0.0
        return (self.metrics['successful_requests'] / self.metrics['total_requests']) * 100
    
    def _store_metrics_in_redis(self):
        """Store metrics in Redis for persistence."""        try:
            key = f"adapter_metrics:{self.adapter_name}"
            self.redis_client.hset(key, mapping={
                'metrics': json.dumps(self.metrics, default=str)
            })
            self.redis_client.expire(key, 86400)  # 24 hours
        except Exception as e:
            logger.warning(f"Failed to store metrics in Redis: {e}")

class AdapterRateLimit:
    """Intelligent rate limiting for API adapters."""    
    def __init__(self, config: RateLimitConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.local_tokens = config.burst_limit
        self.last_refill = time.time()
        self.request_times = []
    
    async def acquire(self, endpoint: str) -> bool:
        """Acquire permission to make a request."""        current_time = time.time()
        
        # Refill tokens based on time passed
        time_passed = current_time - self.last_refill
        tokens_to_add = time_passed * self.config.requests_per_second
        self.local_tokens = min(self.config.burst_limit, self.local_tokens + tokens_to_add)
        self.last_refill = current_time
        
        # Check if we have tokens available
        if self.local_tokens >= 1:
            self.local_tokens -= 1
            self._record_request_time(current_time)
            return True
        
        return False
    
    async def wait_if_needed(self, endpoint: str) -> float:
        """Wait if rate limiting is needed, return wait time."""        if await self.acquire(endpoint):
            return 0.0
        
        # Calculate wait time
        wait_time = 1.0 / self.config.requests_per_second
        await asyncio.sleep(wait_time)
        return wait_time
    
    def _record_request_time(self, request_time: float):
        """Record request time for monitoring."""        self.request_times.append(request_time)
        # Keep only last hour of data
        cutoff_time = request_time - 3600
        self.request_times = [t for t in self.request_times if t > cutoff_time]
    
    def get_current_rate(self) -> float:
        """Get current request rate per second."""        current_time = time.time()
        recent_requests = [t for t in self.request_times if t > current_time - 60]
        return len(recent_requests) / 60.0

class AdapterCache:
    """Intelligent caching system for adapter responses."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None, default_ttl: int = 300):
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.local_cache = {}
    
    def _generate_cache_key(self, adapter_name: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key from adapter name, endpoint, and parameters."""        params_str = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"adapter_cache:{adapter_name}:{endpoint}:{params_hash}"
    
    async def get(self, adapter_name: str, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached response."""        cache_key = self._generate_cache_key(adapter_name, endpoint, params)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis cache get failed: {e}")
        
        # Fallback to local cache
        if cache_key in self.local_cache:
            entry = self.local_cache[cache_key]
            if entry['expires_at'] > datetime.now():
                return entry['data']
            else:
                del self.local_cache[cache_key]
        
        return None
    
    async def set(self, adapter_name: str, endpoint: str, params: Dict[str, Any], 
                  data: Any, ttl: Optional[int] = None) -> None:
        """Set cached response."""        cache_key = self._generate_cache_key(adapter_name, endpoint, params)
        ttl = ttl or self.default_ttl
        
        # Store in Redis
        if self.redis_client:
            try:
                serialized_data = json.dumps(data, default=str)
                self.redis_client.setex(cache_key, ttl, serialized_data)
            except Exception as e:
                logger.warning(f"Redis cache set failed: {e}")
        
        # Store in local cache as backup
        self.local_cache[cache_key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }
        
        # Clean up old local cache entries
        current_time = datetime.now()
        expired_keys = [k for k, v in self.local_cache.items() if v['expires_at'] <= current_time]
        for key in expired_keys:
            del self.local_cache[key]

class BasePlatformAdapter(ABC):
    """    Abstract base class for all platform adapters.
    
    This class provides the foundation for implementing adapters to external platforms
    with comprehensive error handling, rate limiting, authentication, caching, and
    performance monitoring capabilities.
    """    
    def __init__(self, 
                 platform_name: str,
                 platform_type: PlatformType,
                 credentials: AdapterCredentials,
                 rate_limit_config: Optional[RateLimitConfig] = None,
                 redis_client: Optional[redis.Redis] = None):
        self.platform_name = platform_name
        self.platform_type = platform_type
        self.credentials = credentials
        self.status = AdapterStatus.INACTIVE
        self.redis_client = redis_client
        
        # Initialize components
        self.rate_limiter = AdapterRateLimit(rate_limit_config or RateLimitConfig(), redis_client)
        self.cache = AdapterCache(redis_client)
        self.metrics = AdapterMetrics(platform_name, redis_client)
        
        # HTTP client session
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"Initialized {platform_name} adapter for {platform_type.value}")
    
    async def __aenter__(self):
        """Async context manager entry."""        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        await self.disconnect()
    
    async def connect(self) -> bool:
        """Initialize connection to the platform."""        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.credentials.to_headers()
            )
            
            # Test authentication
            if await self.authenticate():
                self.status = AdapterStatus.ACTIVE
                logger.info(f"Successfully connected to {self.platform_name}")
                return True
            else:
                self.status = AdapterStatus.ERROR
                logger.error(f"Authentication failed for {self.platform_name}")
                return False
                
        except Exception as e:
            self.status = AdapterStatus.ERROR
            logger.error(f"Connection failed for {self.platform_name}: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Clean up resources and disconnect."""        if self.session:
            await self.session.close()
            self.session = None
        
        self.status = AdapterStatus.INACTIVE
        logger.info(f"Disconnected from {self.platform_name}")
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform."""        pass
    
    async def refresh_token(self) -> bool:
        """Refresh authentication token if supported."""        logger.warning(f"Token refresh not implemented for {self.platform_name}")
        return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def make_request(self, 
                          method: str,
                          endpoint: str,
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None,
                          cache_ttl: Optional[int] = None,
                          use_cache: bool = True) -> Dict[str, Any]:
        """        Make HTTP request with comprehensive error handling, rate limiting, and caching.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: URL parameters
            data: Form data
            json_data: JSON payload
            headers: Additional headers
            cache_ttl: Cache time-to-live in seconds
            use_cache: Whether to use caching
            
        Returns:
            Response data as dictionary
            
        Raises:
            AdapterError: When request fails
        """        if not self.session:
            raise AdapterError(f"Adapter {self.platform_name} not connected")
        
        # Check cache first
        if use_cache and method.upper() == 'GET':
            cached_response = await self.cache.get(self.platform_name, endpoint, params or {})
            if cached_response:
                logger.debug(f"Cache hit for {self.platform_name} {endpoint}")
                return cached_response
        
        # Rate limiting
        wait_time = await self.rate_limiter.wait_if_needed(endpoint)
        if wait_time > 0:
            self.metrics.record_rate_limit()
            logger.debug(f"Rate limited, waited {wait_time:.2f}s for {self.platform_name}")
        
        # Check token expiration
        if self.credentials.is_token_expired():
            if not await self.refresh_token():
                raise AdapterError(f"Token expired and refresh failed for {self.platform_name}")
        
        # Prepare request
        url = f"{self.credentials.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self.credentials.to_headers()
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            async with self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers
            ) as response:
                
                response_time = time.time() - start_time
                
                # Handle rate limiting
                if response.status == 429:
                    self.metrics.record_rate_limit()
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited by {self.platform_name}, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    raise AdapterError(f"Rate limited by {self.platform_name}")
                
                # Handle authentication errors
                if response.status in [401, 403]:
                    if await self.refresh_token():
                        # Retry with new token
                        request_headers = self.credentials.to_headers()
                        if headers:
                            request_headers.update(headers)
                        
                        async with self.session.request(
                            method=method.upper(),
                            url=url,
                            params=params,
                            data=data,
                            json=json_data,
                            headers=request_headers
                        ) as retry_response:
                            if retry_response.status >= 400:
                                error_text = await retry_response.text()
                                raise AdapterError(f"Authentication failed for {self.platform_name}: {error_text}")
                            response_data = await retry_response.json()
                    else:
                        error_text = await response.text()
                        raise AdapterError(f"Authentication failed for {self.platform_name}: {error_text}")
                
                # Handle other errors
                if response.status >= 400:
                    error_text = await response.text()
                    error_msg = f"Request failed for {self.platform_name}: {response.status} {error_text}"
                    self.metrics.record_request(endpoint, response_time, False, error_msg)
                    raise AdapterError(error_msg)
                
                # Parse response
                try:
                    response_data = await response.json()
                except:
                    response_data = {'text': await response.text()}
                
                # Record success
                self.metrics.record_request(endpoint, response_time, True)
                
                # Cache if applicable
                if use_cache and method.upper() == 'GET' and cache_ttl:
                    await self.cache.set(self.platform_name, endpoint, params or {}, response_data, cache_ttl)
                
                logger.debug(f"Successful request to {self.platform_name} {endpoint} in {response_time:.2f}s")
                return response_data
                
        except aiohttp.ClientError as e:
            response_time = time.time() - start_time
            error_msg = f"Network error for {self.platform_name}: {str(e)}"
            self.metrics.record_request(endpoint, response_time, False, error_msg)
            raise AdapterError(error_msg)
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Unexpected error for {self.platform_name}: {str(e)}"
            self.metrics.record_request(endpoint, response_time, False, error_msg)
            raise AdapterError(error_msg)
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status and metrics."""        return {
            'platform_name': self.platform_name,
            'platform_type': self.platform_type.value,
            'status': self.status.value,
            'success_rate': self.metrics.get_success_rate(),
            'current_rate': self.rate_limiter.get_current_rate(),
            'metrics': self.metrics.metrics,
            'credentials_valid': not self.credentials.is_token_expired(),
            'last_request': self.metrics.metrics.get('last_request_time')
        }
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check on the platform connection."""        pass

class AdapterError(Exception):
    """Base exception for adapter-related errors."""    
    def __init__(self, message: str, platform: Optional[str] = None, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.platform = platform
        self.error_code = error_code
        self.timestamp = datetime.now()

class AuthenticationError(AdapterError):
    """Authentication-related adapter error."""    pass

class RateLimitError(AdapterError):
    """Rate limiting-related adapter error."""    pass

class ConfigurationError(AdapterError):
    """Configuration-related adapter error."""    pass

class NetworkError(AdapterError):
    """Network-related adapter error."""    pass

# Export all classes and types
__all__ = [
    'BasePlatformAdapter',
    'PlatformType',
    'AdapterStatus',
    'AuthenticationType',
    'AdapterCredentials',
    'RateLimitConfig',
    'AdapterMetrics',
    'AdapterRateLimit',
    'AdapterCache',
    'AdapterError',
    'AuthenticationError',
    'RateLimitError',
    'ConfigurationError',
    'NetworkError'
]
