"""Base Platform Adapter - Foundation for All Platform Integrations

Ultra-advanced base adapter providing common functionality for all platform adapters
with standardized interfaces, error handling, and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import aiohttp
from decimal import Decimal
import backoff
from urllib.parse import urlencode

from ...core.distribution_engine import ContentMetadata, PlatformType, ContentType
from ....core.exceptions import PlatformError, AuthenticationError, QuotaExceededError, RateLimitError
from ....core.config import settings
from ....monitoring.metrics import MetricsCollector
from ....security.authentication import AuthenticationManager
from ....utils.rate_limiter import RateLimiter
from ....core.cache import RedisCache

logger = logging.getLogger(__name__)

class AdapterStatus(Enum):
    """
Platform adapter status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_ERROR = "authentication_error"
    QUOTA_EXCEEDED = "quota_exceeded"

class RequestMethod(Enum):
    """HTTP request methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

@dataclass
class PlatformCredentials:
    """Platform authentication credentials"""
    platform: PlatformType
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PublishRequest:
    """
Standardized content publishing request"""
    content_metadata: ContentMetadata
    platform_specific_config: Dict[str, Any] = field(default_factory=dict)
    scheduling_config: Optional[Dict[str, Any]] = None
    monetization_config: Optional[Dict[str, Any]] = None
    audience_targeting: Optional[Dict[str, Any]] = None
    collaboration_config: Optional[Dict[str, Any]] = None

@dataclass
class PublishResponse:
    """
Standardized content publishing response"""
    success: bool
    platform_content_id: Optional[str] = None
    platform_url: Optional[str] = None
    published_at: Optional[datetime] = None
    initial_metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_after: Optional[int] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsRequest:
    """
Analytics data request"""
    content_id: str
    metrics: List[str] = field(default_factory=list)
    date_range: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now() - timedelta(days=7), datetime.now()))
    granularity: str = "day"  # hour, day, week, month

@dataclass
class AnalyticsResponse:
    """Analytics data response"""
    content_id: str
    metrics_data: Dict[str, Any] = field(default_factory=dict)
    time_series_data: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)

class BasePlatformAdapter(ABC):
    """
    Abstract base class for all platform adapters
    
    Provides:
    - Standardized authentication handling
    - Rate limiting and quota management
    - Error handling and retries
    - Metrics collection
    - Caching strategies
    - Request/response standardization
    """
    
    def __init__(self, platform: PlatformType, config: Optional[Dict[str, Any]] = None):
        self.platform = platform
        self.config = config or {}
        
        # Core Components
        self.auth_manager = AuthenticationManager()
        self.metrics_collector = MetricsCollector()
        self.cache = RedisCache()
        
        # Rate Limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.get('rate_limit', 100),
            burst_size=self.config.get('burst_size', 10)
        )
        
        # HTTP Session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Adapter State
        self.status = AdapterStatus.HEALTHY
        self.last_error: Optional[str] = None
        self.quota_used = 0
        self.quota_limit = self.config.get('quota_limit', 10000)
        self.reset_time: Optional[datetime] = None
        
        # Performance Metrics
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'last_24h_requests': 0,
            'error_rate': 0.0
        }
        
        # Platform-specific configuration
        self.base_url = self._get_base_url()
        self.api_version = self._get_api_version()
        self.supported_content_types = self._get_supported_content_types()
        self.max_file_size = self._get_max_file_size()
        
        logger.info(f"{self.platform.value} adapter initialized")

    @abstractmethod
    def _get_base_url(self) -> str:
        """Get platform API base URL"""
        pass

    @abstractmethod
    def _get_api_version(self) -> str:
        """
Get platform API version"""
        pass

    @abstractmethod
    def _get_supported_content_types(self) -> List[ContentType]:
        """
Get supported content types for this platform"""
        pass

    @abstractmethod
    def _get_max_file_size(self) -> int:
        """
Get maximum file size for uploads"""
        pass

    async def initialize(self) -> None:
        """
Initialize the adapter and HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_default_headers()
            )
        
        # Validate platform connection
        await self._validate_platform_connection()
        
        logger.info(f"{self.platform.value} adapter initialized successfully")

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for requests"""
        return {
            'User-Agent': f'Ainflue-DistributionAgent/1.0 ({self.platform.value})',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    async def _validate_platform_connection(self) -> None:
        """
Validate connection to platform API"""
        try:
            health_endpoint = self._get_health_check_endpoint()
            if health_endpoint:
                response = await self._make_request(
                    RequestMethod.GET,
                    health_endpoint,
                    authenticated=False
                )
                if response.get('status') != 200:
                    self.status = AdapterStatus.DEGRADED
                    logger.warning(f"{self.platform.value} platform connection degraded")
        except Exception as e:
            self.status = AdapterStatus.UNAVAILABLE
            logger.error(f"{self.platform.value} platform connection failed: {e}")

    @abstractmethod
    def _get_health_check_endpoint(self) -> Optional[str]:
        """Get platform health check endpoint"""
        pass

    async def authenticate_user(self, credentials: PlatformCredentials) -> bool:
        """
        Authenticate user credentials with the platform
        
        Args:
            credentials: User's platform credentials
            
        Returns:
            True if authentication successful
        """
        try:
            # Validate credentials format
            if not await self._validate_credentials(credentials):
                raise AuthenticationError("Invalid credentials format")
            
            # Check if token needs refresh
            if await self._needs_token_refresh(credentials):
                credentials = await self._refresh_token(credentials)
            
            # Test authentication with a simple API call
            auth_test_result = await self._test_authentication(credentials)
            
            if auth_test_result:
                # Cache valid credentials
                await self._cache_credentials(credentials)
                self.status = AdapterStatus.HEALTHY
                logger.info(f"User authenticated successfully for {self.platform.value}")
                return True
            else:
                self.status = AdapterStatus.AUTHENTICATION_ERROR
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed for {self.platform.value}: {e}")
            self.status = AdapterStatus.AUTHENTICATION_ERROR
            raise AuthenticationError(f"Authentication failed: {e}")

    @abstractmethod
    async def _validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """Validate credentials format and required fields"""
        pass

    @abstractmethod
    async def _needs_token_refresh(self, credentials: PlatformCredentials) -> bool:
        """
Check if access token needs refresh"""
        pass

    @abstractmethod
    async def _refresh_token(self, credentials: PlatformCredentials) -> PlatformCredentials:
        """
Refresh access token"""
        pass

    @abstractmethod
    async def _test_authentication(self, credentials: PlatformCredentials) -> bool:
        """
Test authentication with platform API"""
        pass

    async def _cache_credentials(self, credentials: PlatformCredentials) -> None:
        """
Cache validated credentials"""
        cache_key = f"credentials:{credentials.user_id}:{self.platform.value}"
        cache_data = {
            'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'expires_at': credentials.token_expires_at.isoformat() if credentials.token_expires_at else None,
            'additional_data': credentials.additional_data
        }
        
        ttl = 3600  # 1 hour default
        if credentials.token_expires_at:
            ttl = max(300, int((credentials.token_expires_at - datetime.now()).total_seconds()))
        
        await self.cache.set(cache_key, json.dumps(cache_data, default=str), ttl=ttl)

    async def publish_content(self, request: PublishRequest, credentials: PlatformCredentials) -> PublishResponse:
        """
        Publish content to the platform
        
        Args:
            request: Content publishing request
            credentials: User's platform credentials
            
        Returns:
            Publishing response with platform-specific data
        """
        start_time = time.time()
        
        try:
            # Validate request
            await self._validate_publish_request(request)
            
            # Check rate limits and quotas
            await self._check_rate_limits()
            await self._check_quotas()
            
            # Prepare content for platform
            prepared_content = await self._prepare_content_for_platform(request)
            
            # Upload content
            upload_result = await self._upload_content(prepared_content, credentials)
            
            # Publish content
            publish_result = await self._publish_content_to_platform(upload_result, request, credentials)
            
            # Update metrics
            processing_time = time.time() - start_time
            await self._update_success_metrics(processing_time)
            
            # Cache publish result
            await self._cache_publish_result(publish_result)
            
            logger.info(f"Content published successfully to {self.platform.value}: {publish_result.platform_content_id}")
            return publish_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            await self._update_error_metrics(processing_time, str(e))
            
            logger.error(f"Content publishing failed for {self.platform.value}: {e}")
            
            return PublishResponse(
                success=False,
                error_message=str(e),
                retry_after=self._calculate_retry_delay(e)
            )

    async def _validate_publish_request(self, request: PublishRequest) -> None:
        """Validate publishing request"""
        if not request.content_metadata.title:
            raise PlatformError("Content title is required")
        
        # Check content type support
        content_type = ContentType(request.content_metadata.format.lower()) if request.content_metadata.format else None
        if content_type not in self.supported_content_types:
            raise PlatformError(f"Content type {content_type} not supported on {self.platform.value}")
        
        # Check file size
        if request.content_metadata.file_size and request.content_metadata.file_size > self.max_file_size:
            raise PlatformError(f"File size exceeds platform limit: {request.content_metadata.file_size} > {self.max_file_size}")
        
        # Platform-specific validation
        await self._validate_platform_specific_request(request)

    @abstractmethod
    async def _validate_platform_specific_request(self, request: PublishRequest) -> None:
        """Platform-specific request validation"""
        pass

    async def _check_rate_limits(self) -> None:
        """
Check and enforce rate limits"""
        if not await self.rate_limiter.can_proceed():
            self.status = AdapterStatus.RATE_LIMITED
            raise RateLimitError("Rate limit exceeded")

    async def _check_quotas(self) -> None:
        """Check API quotas"""
        if self.quota_used >= self.quota_limit:
            if self.reset_time and datetime.now() < self.reset_time:
                self.status = AdapterStatus.QUOTA_EXCEEDED
                raise QuotaExceededError(f"API quota exceeded. Resets at {self.reset_time}")

    @abstractmethod
    async def _prepare_content_for_platform(self, request: PublishRequest) -> Dict[str, Any]:
        """Prepare content according to platform requirements"""
        pass

    @abstractmethod
    async def _upload_content(self, prepared_content: Dict[str, Any], credentials: PlatformCredentials) -> Dict[str, Any]:
        """
Upload content to platform"""
        pass

    @abstractmethod
    async def _publish_content_to_platform(self, upload_result: Dict[str, Any], request: PublishRequest, credentials: PlatformCredentials) -> PublishResponse:
        """
Publish uploaded content on platform"""
        pass

    async def get_content_analytics(self, request: AnalyticsRequest, credentials: PlatformCredentials) -> AnalyticsResponse:
        """
        Get analytics data for published content
        
        Args:
            request: Analytics request
            credentials: User's platform credentials
            
        Returns:
            Analytics data response
        """
        try:
            # Check cache first
            cache_key = f"analytics:{self.platform.value}:{request.content_id}:{request.date_range[0].date()}:{request.date_range[1].date()}"
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                logger.debug(f"Returning cached analytics for {request.content_id}")
                return AnalyticsResponse(**json.loads(cached_data))
            
            # Fetch fresh analytics data
            analytics_data = await self._fetch_platform_analytics(request, credentials)
            
            # Process and normalize data
            processed_data = await self._process_analytics_data(analytics_data, request)
            
            response = AnalyticsResponse(
                content_id=request.content_id,
                metrics_data=processed_data['metrics'],
                time_series_data=processed_data['time_series'],
                summary_stats=processed_data['summary']
            )
            
            # Cache result
            await self.cache.set(cache_key, json.dumps(response.__dict__, default=str), ttl=1800)  # 30 minutes
            
            logger.info(f"Analytics retrieved for {request.content_id} on {self.platform.value}")
            return response
            
        except Exception as e:
            logger.error(f"Analytics retrieval failed for {self.platform.value}: {e}")
            raise PlatformError(f"Failed to get analytics: {e}")

    @abstractmethod
    async def _fetch_platform_analytics(self, request: AnalyticsRequest, credentials: PlatformCredentials) -> Dict[str, Any]:
        """Fetch analytics data from platform API"""
        pass

    @abstractmethod
    async def _process_analytics_data(self, raw_data: Dict[str, Any], request: AnalyticsRequest) -> Dict[str, Any]:
        """
Process and normalize analytics data"""
        pass

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def _make_request(self, method: RequestMethod, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                           params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                           authenticated: bool = True, credentials: Optional[PlatformCredentials] = None) -> Dict[str, Any]:
        """
        Make HTTP request to platform API with retries and error handling
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            authenticated: Whether request requires authentication
            credentials: User credentials for authentication
            
        Returns:
            Response data
        """
        if not self.session:
            await self.initialize()
        
        # Build full URL
        url = f"{self.base_url}/{self.api_version}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        # Add authentication headers
        if authenticated and credentials:
            auth_headers = await self._get_auth_headers(credentials)
            request_headers.update(auth_headers)
        
        # Prepare request parameters
        kwargs = {
            'headers': request_headers,
            'timeout': aiohttp.ClientTimeout(total=30)
        }
        
        if params:
            url += '?' + urlencode(params)
        
        if data and method in [RequestMethod.POST, RequestMethod.PUT, RequestMethod.PATCH]:
            kwargs['json'] = data
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        start_time = time.time()
        
        try:
            async with self.session.request(method.value, url, **kwargs) as response:
                response_time = time.time() - start_time
                
                # Update quota usage from headers
                await self._update_quota_from_headers(response.headers)
                
                # Handle different status codes
                if response.status == 200 or response.status == 201:
                    response_data = await response.json()
                    await self._update_success_metrics(response_time)
                    return response_data
                
                elif response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.status = AdapterStatus.RATE_LIMITED
                    raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds")
                
                elif response.status == 401:  # Unauthorized
                    self.status = AdapterStatus.AUTHENTICATION_ERROR
                    raise AuthenticationError("Authentication failed")
                
                elif response.status == 403:  # Forbidden/Quota exceeded
                    self.status = AdapterStatus.QUOTA_EXCEEDED
                    raise QuotaExceededError("API quota exceeded")
                
                else:
                    error_data = await response.text()
                    raise PlatformError(f"API request failed: {response.status} - {error_data}")
                
        except Exception as e:
            response_time = time.time() - start_time
            await self._update_error_metrics(response_time, str(e))
            raise

    @abstractmethod
    async def _get_auth_headers(self, credentials: PlatformCredentials) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        pass

    async def _update_quota_from_headers(self, headers: aiohttp.ClientResponse.headers) -> None:
        """
Update quota usage from response headers"""
        # Common header names for quota information
        quota_headers = [
            'X-RateLimit-Remaining',
            'X-Rate-Limit-Remaining',
            'RateLimit-Remaining',
            'X-API-Quota-Remaining'
        ]
        
        for header in quota_headers:
            if header in headers:
                try:
                    remaining = int(headers[header])
                    self.quota_used = self.quota_limit - remaining
                    break
                except ValueError:
                    pass
        
        # Check for reset time
        reset_headers = [
            'X-RateLimit-Reset',
            'X-Rate-Limit-Reset',
            'RateLimit-Reset'
        ]
        
        for header in reset_headers:
            if header in headers:
                try:
                    reset_timestamp = int(headers[header])
                    self.reset_time = datetime.fromtimestamp(reset_timestamp)
                    break
                except ValueError:
                    pass

    async def _update_success_metrics(self, response_time: float) -> None:
        """
Update performance metrics for successful requests"""
        self.performance_metrics['total_requests'] += 1
        self.performance_metrics['successful_requests'] += 1
        
        # Update average response time
        total_time = (self.performance_metrics['average_response_time'] * 
                     (self.performance_metrics['total_requests'] - 1) + response_time)
        self.performance_metrics['average_response_time'] = total_time / self.performance_metrics['total_requests']
        
        # Update error rate
        self.performance_metrics['error_rate'] = (
            self.performance_metrics['failed_requests'] / self.performance_metrics['total_requests']
        )
        
        # Send metrics to collector
        await self.metrics_collector.record_adapter_metrics(
            platform=self.platform.value,
            metrics=self.performance_metrics,
            response_time=response_time,
            success=True
        )

    async def _update_error_metrics(self, response_time: float, error_message: str) -> None:
        """
Update performance metrics for failed requests"""
        self.performance_metrics['total_requests'] += 1
        self.performance_metrics['failed_requests'] += 1
        self.last_error = error_message
        
        # Update error rate
        self.performance_metrics['error_rate'] = (
            self.performance_metrics['failed_requests'] / self.performance_metrics['total_requests']
        )
        
        # Send metrics to collector
        await self.metrics_collector.record_adapter_metrics(
            platform=self.platform.value,
            metrics=self.performance_metrics,
            response_time=response_time,
            success=False,
            error=error_message
        )

    def _calculate_retry_delay(self, error: Exception) -> Optional[int]:
        """
Calculate retry delay based on error type"""
        if isinstance(error, RateLimitError):
            return 60  # 1 minute for rate limits
        elif isinstance(error, QuotaExceededError):
            if self.reset_time:
                return int((self.reset_time - datetime.now()).total_seconds())
            return 3600  # 1 hour default
        elif isinstance(error, AuthenticationError):
            return None  # Don't retry auth errors
        else:
            return 30  # 30 seconds for other errors

    async def _cache_publish_result(self, result: PublishResponse) -> None:
        """
Cache publishing result"""
        if result.success and result.platform_content_id:
            cache_key = f"publish_result:{self.platform.value}:{result.platform_content_id}"
            await self.cache.set(
                cache_key, 
                json.dumps(result.__dict__, default=str), 
                ttl=86400  # 24 hours
            )

    async def get_status(self) -> Dict[str, Any]:
        """Get adapter status and health information"""
        return {
            'platform': self.platform.value,
            'status': self.status.value,
            'last_error': self.last_error,
            'quota_used': self.quota_used,
            'quota_limit': self.quota_limit,
            'reset_time': self.reset_time.isoformat() if self.reset_time else None,
            'performance_metrics': self.performance_metrics,
            'supported_content_types': [ct.value for ct in self.supported_content_types],
            'max_file_size': self.max_file_size
        }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
Get detailed performance metrics"""
        return self.performance_metrics.copy()

    async def reset_quota(self) -> None:
        """
Reset quota counters (for testing or manual reset)"""
        self.quota_used = 0
        self.reset_time = None
        if self.status == AdapterStatus.QUOTA_EXCEEDED:
            self.status = AdapterStatus.HEALTHY

    async def shutdown(self) -> None:
        """
Graceful shutdown of the adapter"""
        logger.info(f"Shutting down {self.platform.value} adapter...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        await self.cache.close()
        
        logger.info(f"{self.platform.value} adapter shutdown complete")
