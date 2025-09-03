"""Advanced API Manager - External API Integration and Management System
=====================================================================

Sophisticated API management system providing centralized API integration,
rate limiting, authentication management, request/response handling, and
comprehensive API monitoring for external service integrations.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/api_manager.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import time
from urllib.parse import urlencode
import base64

logger = logging.getLogger(__name__)


class HTTPMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIAuthType(str, Enum):
    """API authentication types."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


class RequestStatus(str, Enum):
    """Request status."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    RETRYING = "retrying"


@dataclass
class APIEndpoint:
    """API endpoint configuration."""
    id: str
    name: str
    base_url: str
    path: str
    method: HTTPMethod
    auth_type: APIAuthType
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1
    rate_limit_per_minute: int = 60
    cache_ttl: int = 0  # Cache time-to-live in seconds
    description: str = ""


@dataclass
class APICredentials:
    """API credentials configuration."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    expires_at: Optional[datetime] = None


@dataclass
class APIRequest:
    """API request data."""
    id: str
    endpoint_id: str
    method: HTTPMethod
    url: str
    headers: Dict[str, str]
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    files: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIResponse:
    """API response data."""
    request_id: str
    status_code: int
    status: RequestStatus
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    error_message: Optional[str] = None
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    from_cache: bool = False


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    current_minute: int = 0
    current_hour: int = 0
    current_day: int = 0
    last_reset_minute: datetime = field(default_factory=datetime.utcnow)
    last_reset_hour: datetime = field(default_factory=datetime.utcnow)
    last_reset_day: datetime = field(default_factory=datetime.utcnow)


class APIManager:
    """
    Advanced API management system providing centralized external API
    integration with comprehensive monitoring and management capabilities.
    """
    
    def __init__(self, cache_client=None):
        """Initialize the API manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.cache = cache_client
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.credentials: Dict[str, APICredentials] = {}
        self.rate_limits: Dict[str, RateLimitConfig] = {}
        self.request_history: List[APIRequest] = []
        self.response_history: List[APIResponse] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.middleware_functions: List[Callable] = []
        
        self.logger.info("APIManager initialized")
    
    async def initialize(self):
        """Initialize the API manager."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                headers={"User-Agent": "Ainflue-API-Manager/1.0"}
            )
            self.logger.info("✅ API Manager session initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize API Manager: {e}")
    
    async def register_endpoint(
        self,
        endpoint: APIEndpoint,
        credentials: Optional[APICredentials] = None
    ) -> bool:
        """Register an API endpoint."""
        try:
            self.endpoints[endpoint.id] = endpoint
            
            if credentials:
                self.credentials[endpoint.id] = credentials
            
            # Initialize rate limiting
            self.rate_limits[endpoint.id] = RateLimitConfig(
                requests_per_minute=endpoint.rate_limit_per_minute,
                requests_per_hour=endpoint.rate_limit_per_minute * 60,
                requests_per_day=endpoint.rate_limit_per_minute * 60 * 24
            )
            
            self.logger.info(f"✅ API endpoint registered: {endpoint.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register endpoint: {e}")
            return False
    
    async def make_request(
        self,
        endpoint_id: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        override_cache: bool = False
    ) -> APIResponse:
        """Make an API request to a registered endpoint."""
        try:
            if endpoint_id not in self.endpoints:
                return APIResponse(
                    request_id=str(uuid4()),
                    status_code=404,
                    status=RequestStatus.FAILED,
                    error_message=f"Endpoint {endpoint_id} not found"
                )
            
            endpoint = self.endpoints[endpoint_id]
            
            # Check rate limits
            if not await self._check_rate_limit(endpoint_id):
                return APIResponse(
                    request_id=str(uuid4()),
                    status_code=429,
                    status=RequestStatus.RATE_LIMITED,
                    error_message="Rate limit exceeded"
                )
            
            # Check cache first
            if endpoint.cache_ttl > 0 and not override_cache:
                cached_response = await self._get_cached_response(endpoint_id, params)
                if cached_response:
                    return cached_response
            
            # Build request
            request = await self._build_request(endpoint, params, data, files, custom_headers)
            
            # Execute request with retries
            response = await self._execute_request_with_retries(request, endpoint)
            
            # Cache response if configured
            if endpoint.cache_ttl > 0 and response.status == RequestStatus.SUCCESS:
                await self._cache_response(endpoint_id, params, response, endpoint.cache_ttl)
            
            # Store in history
            self.request_history.append(request)
            self.response_history.append(response)
            
            # Update rate limit counters
            await self._update_rate_limit_counters(endpoint_id)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to make request: {e}")
            return APIResponse(
                request_id=str(uuid4()),
                status_code=500,
                status=RequestStatus.FAILED,
                error_message=str(e)
            )
    
    async def _check_rate_limit(self, endpoint_id: str) -> bool:
        """Check if request is within rate limits."""
        try:
            if endpoint_id not in self.rate_limits:
                return True
            
            rate_limit = self.rate_limits[endpoint_id]
            now = datetime.utcnow()
            
            # Reset counters if needed
            if now - rate_limit.last_reset_minute >= timedelta(minutes=1):
                rate_limit.current_minute = 0
                rate_limit.last_reset_minute = now
            
            if now - rate_limit.last_reset_hour >= timedelta(hours=1):
                rate_limit.current_hour = 0
                rate_limit.last_reset_hour = now
            
            if now - rate_limit.last_reset_day >= timedelta(days=1):
                rate_limit.current_day = 0
                rate_limit.last_reset_day = now
            
            # Check limits
            if rate_limit.current_minute >= rate_limit.requests_per_minute:
                return False
            if rate_limit.current_hour >= rate_limit.requests_per_hour:
                return False
            if rate_limit.current_day >= rate_limit.requests_per_day:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            return True
    
    async def _update_rate_limit_counters(self, endpoint_id: str):
        """Update rate limit counters after successful request."""
        try:
            if endpoint_id in self.rate_limits:
                rate_limit = self.rate_limits[endpoint_id]
                rate_limit.current_minute += 1
                rate_limit.current_hour += 1
                rate_limit.current_day += 1
        except Exception as e:
            self.logger.error(f"Error updating rate limit counters: {e}")
    
    async def _get_cached_response(
        self,
        endpoint_id: str,
        params: Optional[Dict[str, Any]]
    ) -> Optional[APIResponse]:
        """Get cached response if available."""
        try:
            if not self.cache:
                return None
            
            # Create cache key
            cache_key = self._create_cache_key(endpoint_id, params)
            
            # Get from cache
            cached_data = await self.cache.get(cache_key)
            if not cached_data:
                return None
            
            # Reconstruct APIResponse from cached data
            response = APIResponse(
                status_code=cached_data.get('status_code', 200),
                data=cached_data.get('data'),
                headers=cached_data.get('headers', {}),
                endpoint_id=endpoint_id,
                timestamp=cached_data.get('timestamp'),
                success=cached_data.get('success', True),
                error_message=cached_data.get('error_message'),
                rate_limit_remaining=cached_data.get('rate_limit_remaining'),
                cache_hit=True  # Mark as cache hit
            )
            
            self.logger.debug(f"🎯 Cache hit for {endpoint_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting cached response: {e}")
            return None
    
    async def _cache_response(
        self,
        endpoint_id: str,
        params: Optional[Dict[str, Any]],
        response: APIResponse,
        ttl: int
    ):
        """Cache API response."""
        try:
            if not self.cache:
                return
            
            # Don't cache error responses or unsuccessful responses
            if not response.success or response.status_code >= 400:
                return
            
            # Create cache key
            cache_key = self._create_cache_key(endpoint_id, params)
            
            # Prepare cache data
            cache_data = {
                'status_code': response.status_code,
                'data': response.data,
                'headers': response.headers,
                'timestamp': response.timestamp,
                'success': response.success,
                'error_message': response.error_message,
                'rate_limit_remaining': response.rate_limit_remaining,
                'cached_at': time.time(),
                'endpoint_id': endpoint_id
            }
            
            # Cache the response
            await self.cache.set(cache_key, cache_data, ttl)
            
            self.logger.debug(f"💾 Response cached for {endpoint_id} (TTL: {ttl}s)")
            
        except Exception as e:
            self.logger.error(f"Error caching response: {e}")
    
    def _create_cache_key(self, endpoint_id: str, params: Optional[Dict[str, Any]]) -> str:
        """Create cache key for request."""
        try:
            # Include user context and request specifics in cache key
            key_components = [
                f"api_response",
                endpoint_id,
                json.dumps(params or {}, sort_keys=True)
            ]
            
            # Add user context if available
            if hasattr(self, 'current_user_id') and self.current_user_id:
                key_components.append(f"user:{self.current_user_id}")
            
            key_data = ":".join(key_components)
            return hashlib.md5(key_data.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error creating cache key: {e}")
            return f"api_response:{endpoint_id}:default"
    
    def _get_cache_ttl(self, endpoint_id: str, response: APIResponse) -> int:
        """Determine appropriate cache TTL for response."""
        try:
            # Default TTLs based on endpoint patterns
            default_ttls = {
                'user_profile': 1800,      # 30 minutes
                'content_list': 600,       # 10 minutes
                'content_detail': 3600,    # 1 hour
                'analytics': 300,          # 5 minutes
                'search': 900,             # 15 minutes
                'static_data': 7200,       # 2 hours
                'config': 14400            # 4 hours
            }
            
            # Check for specific endpoint patterns
            for pattern, ttl in default_ttls.items():
                if pattern in endpoint_id.lower():
                    return ttl
            
            # Check response headers for cache control
            cache_control = response.headers.get('Cache-Control', '')
            if 'max-age=' in cache_control:
                try:
                    max_age = int(cache_control.split('max-age=')[1].split(',')[0])
                    return min(max_age, 3600)  # Cap at 1 hour
                except ValueError:
                    pass
            
            # Default TTL
            return 600  # 10 minutes
            
        except Exception as e:
            self.logger.error(f"Error determining cache TTL: {e}")
            return 600  # Default 10 minutes
    
    async def _should_cache_response(self, endpoint_id: str, response: APIResponse) -> bool:
        """Determine if response should be cached."""
        try:
            # Don't cache error responses
            if not response.success or response.status_code >= 400:
                return False
            
            # Don't cache responses with no-cache header
            cache_control = response.headers.get('Cache-Control', '').lower()
            if 'no-cache' in cache_control or 'no-store' in cache_control:
                return False
            
            # Don't cache responses that are too large
            if response.data and len(str(response.data)) > 1048576:  # 1MB limit
                return False
            
            # Cache patterns - endpoints that should be cached
            cacheable_patterns = [
                'user_profile',
                'content_list', 
                'content_detail',
                'analytics',
                'search',
                'static_data',
                'config'
            ]
            
            # Check if endpoint is cacheable
            for pattern in cacheable_patterns:
                if pattern in endpoint_id.lower():
                    return True
            
            # Don't cache by default for unknown endpoints
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if response should be cached: {e}")
            return False
    
    async def _build_request(
        self,
        endpoint: APIEndpoint,
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]],
        files: Optional[Dict[str, Any]],
        custom_headers: Optional[Dict[str, str]]
    ) -> APIRequest:
        """Build API request object."""
        try:
            request_id = str(uuid4())
            
            # Build URL
            url = f"{endpoint.base_url.rstrip('/')}/{endpoint.path.lstrip('/')}"
            
            # Build headers
            headers = endpoint.headers.copy()
            
            # Add authentication headers
            if endpoint.id in self.credentials:
                auth_headers = await self._build_auth_headers(endpoint, self.credentials[endpoint.id])
                headers.update(auth_headers)
            
            # Add custom headers
            if custom_headers:
                headers.update(custom_headers)
            
            # Merge params with endpoint query params
            final_params = endpoint.query_params.copy()
            if params:
                final_params.update(params)
            
            request = APIRequest(
                id=request_id,
                endpoint_id=endpoint.id,
                method=endpoint.method,
                url=url,
                headers=headers,
                params=final_params,
                data=data,
                files=files,
                timeout=endpoint.timeout,
                max_retries=endpoint.retry_count
            )
            
            return request
            
        except Exception as e:
            self.logger.error(f"Error building request: {e}")
            raise
    
    async def _build_auth_headers(
        self,
        endpoint: APIEndpoint,
        credentials: APICredentials
    ) -> Dict[str, str]:
        """Build authentication headers."""
        headers = {}
        
        try:
            if endpoint.auth_type == APIAuthType.API_KEY:
                if credentials.api_key:
                    headers["X-API-Key"] = credentials.api_key
            
            elif endpoint.auth_type == APIAuthType.BEARER_TOKEN:
                if credentials.access_token:
                    headers["Authorization"] = f"Bearer {credentials.access_token}"
            
            elif endpoint.auth_type == APIAuthType.BASIC_AUTH:
                if credentials.username and credentials.password:
                    auth_string = base64.b64encode(
                        f"{credentials.username}:{credentials.password}".encode()
                    ).decode()
                    headers["Authorization"] = f"Basic {auth_string}"
            
            elif endpoint.auth_type == APIAuthType.OAUTH2:
                if credentials.access_token:
                    headers["Authorization"] = f"Bearer {credentials.access_token}"
            
            elif endpoint.auth_type == APIAuthType.CUSTOM:
                headers.update(credentials.custom_headers)
            
            return headers
            
        except Exception as e:
            self.logger.error(f"Error building auth headers: {e}")
            return {}
    
    async def _execute_request_with_retries(
        self,
        request: APIRequest,
        endpoint: APIEndpoint
    ) -> APIResponse:
        """Execute API request with retry logic."""
        last_exception = None
        
        for attempt in range(request.max_retries + 1):
            try:
                if attempt > 0:
                    # Wait before retry
                    delay = endpoint.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    await asyncio.sleep(delay)
                    self.logger.info(f"🔄 Retrying request {request.id}, attempt {attempt + 1}")
                
                response = await self._execute_single_request(request)
                
                # Check if retry is needed
                if response.status in [RequestStatus.SUCCESS, RequestStatus.UNAUTHORIZED]:
                    return response
                elif attempt < request.max_retries:
                    request.retry_count = attempt + 1
                    continue
                else:
                    return response
                    
            except Exception as e:
                last_exception = e
                if attempt < request.max_retries:
                    continue
                else:
                    break
        
        # All retries failed
        return APIResponse(
            request_id=request.id,
            status_code=500,
            status=RequestStatus.FAILED,
            error_message=f"All retries failed. Last error: {str(last_exception)}"
        )
    
    async def _execute_single_request(self, request: APIRequest) -> APIResponse:
        """Execute a single API request."""
        try:
            if not self.session:
                await self.initialize()
            
            start_time = time.time()
            
            # Prepare request parameters
            kwargs = {
                "headers": request.headers,
                "timeout": aiohttp.ClientTimeout(total=request.timeout)
            }
            
            # Add query parameters for GET requests
            if request.method == HTTPMethod.GET and request.params:
                request.url += "?" + urlencode(request.params)
            
            # Add data for POST/PUT/PATCH requests
            if request.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
                if request.files:
                    # Handle file uploads
                    data = aiohttp.FormData()
                    if request.data:
                        for key, value in request.data.items():
                            data.add_field(key, str(value))
                    for key, file_data in request.files.items():
                        data.add_field(key, file_data)
                    kwargs["data"] = data
                elif request.data:
                    kwargs["json"] = request.data
            
            # Apply middleware
            for middleware in self.middleware_functions:
                await middleware(request, kwargs)
            
            # Execute request
            async with self.session.request(
                request.method.value,
                request.url,
                **kwargs
            ) as response:
                
                response_time = time.time() - start_time
                
                # Read response
                response_data = None
                response_text = None
                
                try:
                    if response.content_type == "application/json":
                        response_data = await response.json()
                    else:
                        response_text = await response.text()
                except:
                    response_text = await response.text()
                
                # Determine status
                if 200 <= response.status < 300:
                    status = RequestStatus.SUCCESS
                elif response.status == 401:
                    status = RequestStatus.UNAUTHORIZED
                elif response.status == 429:
                    status = RequestStatus.RATE_LIMITED
                elif response.status >= 500:
                    status = RequestStatus.FAILED
                else:
                    status = RequestStatus.FAILED
                
                api_response = APIResponse(
                    request_id=request.id,
                    status_code=response.status,
                    status=status,
                    data=response_data,
                    text=response_text,
                    headers=dict(response.headers),
                    response_time=response_time
                )
                
                if status != RequestStatus.SUCCESS:
                    api_response.error_message = response_text or f"HTTP {response.status}"
                
                return api_response
                
        except asyncio.TimeoutError:
            return APIResponse(
                request_id=request.id,
                status_code=408,
                status=RequestStatus.TIMEOUT,
                error_message="Request timeout"
            )
        except Exception as e:
            return APIResponse(
                request_id=request.id,
                status_code=500,
                status=RequestStatus.FAILED,
                error_message=str(e)
            )
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware function to be applied to all requests."""
        self.middleware_functions.append(middleware_func)
    
    async def get_endpoint_statistics(self, endpoint_id: str) -> Dict[str, Any]:
        """Get statistics for an endpoint."""
        try:
            if endpoint_id not in self.endpoints:
                return {}
            
            # Filter requests and responses for this endpoint
            endpoint_requests = [r for r in self.request_history if r.endpoint_id == endpoint_id]
            endpoint_responses = [r for r in self.response_history if r.request_id in [req.id for req in endpoint_requests]]
            
            if not endpoint_responses:
                return {"endpoint_id": endpoint_id, "total_requests": 0}
            
            # Calculate statistics
            success_count = len([r for r in endpoint_responses if r.status == RequestStatus.SUCCESS])
            failed_count = len([r for r in endpoint_responses if r.status == RequestStatus.FAILED])
            timeout_count = len([r for r in endpoint_responses if r.status == RequestStatus.TIMEOUT])
            
            response_times = [r.response_time for r in endpoint_responses if r.response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            stats = {
                "endpoint_id": endpoint_id,
                "total_requests": len(endpoint_responses),
                "success_count": success_count,
                "failed_count": failed_count,
                "timeout_count": timeout_count,
                "success_rate": (success_count / len(endpoint_responses)) * 100 if endpoint_responses else 0,
                "average_response_time": avg_response_time,
                "rate_limit_info": self.rate_limits.get(endpoint_id).__dict__ if endpoint_id in self.rate_limits else {}
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting endpoint statistics: {e}")
            return {}
    
    async def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall API manager statistics."""
        try:
            total_requests = len(self.response_history)
            if total_requests == 0:
                return {"total_requests": 0}
            
            success_count = len([r for r in self.response_history if r.status == RequestStatus.SUCCESS])
            failed_count = len([r for r in self.response_history if r.status == RequestStatus.FAILED])
            
            response_times = [r.response_time for r in self.response_history if r.response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Group by endpoint
            endpoint_stats = {}
            for endpoint_id in self.endpoints.keys():
                endpoint_stats[endpoint_id] = await self.get_endpoint_statistics(endpoint_id)
            
            stats = {
                "total_requests": total_requests,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": (success_count / total_requests) * 100,
                "average_response_time": avg_response_time,
                "registered_endpoints": len(self.endpoints),
                "endpoint_statistics": endpoint_stats
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting overall statistics: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.session:
                await self.session.close()
            self.logger.info("✅ API Manager cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Global API manager instance
_api_manager: Optional[APIManager] = None


async def get_api_manager() -> APIManager:
    """Get global API manager instance."""
    global _api_manager
    
    if _api_manager is None:
        _api_manager = APIManager()
        await _api_manager.initialize()
    
    return _api_manager