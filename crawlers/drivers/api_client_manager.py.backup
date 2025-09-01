"""Enterprise API Client Management System
=======================================

Professional API client management for industrial-grade platform integrations.
Handles authentication, rate limiting, retries, and client lifecycle management.

Key Features:
- Multi-platform API client support (Twitter, YouTube, Instagram, TikTok, etc.)
- OAuth2/JWT authentication management
- Intelligent rate limiting and quota management
- Circuit breaker pattern for resilience
- Request/response caching and optimization
- Health monitoring and failover capabilities

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""
import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Type
import json
import hashlib
from urllib.parse import urlencode, urlparse
import base64
import secrets

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import jwt
from cryptography.fernet import Fernet
import redis
from tenacity import retry, stop_after_attempt, wait_exponential

from ...core.config import settings
from ...core.exceptions import APIError, AuthenticationError, RateLimitError
from ...utils.rate_limiter import RateLimiter
from ...utils.cache_manager import CacheManager
from ...utils.circuit_breaker import CircuitBreaker
from ...utils.encryption_manager import EncryptionManager

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types for API integration"""
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    TWITCH = "twitch"
    GENERIC = "generic"


class AuthType(Enum):
    """Supported authentication types"""
    OAUTH2 = "oauth2"
    JWT = "jwt"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    CUSTOM_HEADER = "custom_header"
    SESSION_TOKEN = "session_token"


class ClientStatus(Enum):
    """API client status tracking"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_ERROR = "auth_error"
    CIRCUIT_OPEN = "circuit_open"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    backoff_factor: float = 1.5
    max_backoff: int = 300


@dataclass
class AuthCredentials:
    """Authentication credentials container"""
    auth_type: AuthType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    expires_at: Optional[float] = None
    scope: List[str] = field(default_factory=list)


@dataclass
class APIClientConfig:
    """Comprehensive API client configuration"""
    platform: PlatformType
    base_url: str
    auth_credentials: AuthCredentials
    rate_limit_config: RateLimitConfig = field(default_factory=RateLimitConfig)
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    enable_caching: bool = True
    cache_ttl: int = 300
    user_agent: str = "IA-Influencer-Agent/2.0"
    verify_ssl: bool = True
    proxy: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    debug_mode: bool = False


@dataclass
class APIResponse:
    """Standardized API response container"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    url: str
    response_time: float
    from_cache: bool = False
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[float] = None
    pagination_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIClient(ABC):
    """Abstract base class for platform-specific API clients"""
    
    def __init__(self, config: APIClientConfig):
        self.config = config
        self.platform = config.platform
        self.status = ClientStatus.INITIALIZING
        
        # Core components
        self.rate_limiter = RateLimiter(
            max_requests=config.rate_limit_config.requests_per_minute,
            time_window=60
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            timeout=config.circuit_breaker_timeout
        )
        self.cache_manager = CacheManager() if config.enable_caching else None
        self.encryption_manager = EncryptionManager()
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_session: Optional[requests.Session] = None
        
        # Statistics and monitoring
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'cached_requests': 0,
            'average_response_time': 0.0
        }
        
        # Authentication state
        self.is_authenticated = False
        self.last_auth_check = 0.0
        self.auth_lock = asyncio.Lock()
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Platform-specific authentication implementation"""
        pass
    
    @abstractmethod
    async def refresh_authentication(self) -> bool:
        """Refresh authentication tokens"""
        pass
    
    @abstractmethod
    def _build_request_headers(self) -> Dict[str, str]:
        """Build platform-specific request headers"""
        pass
    
    @abstractmethod
    def _extract_rate_limit_info(self, headers: Dict[str, str]) -> Dict[str, Optional[int]]:
        """Extract rate limit information from response headers"""
        pass
    
    async def initialize(self) -> None:
        """Initialize API client and establish connection"""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                verify_ssl=self.config.verify_ssl
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._build_request_headers()
            )
            
            # Initialize auth session for OAuth flows
            self.auth_session = requests.Session()
            retry_strategy = Retry(
                total=self.config.max_retries,
                backoff_factor=self.config.backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.auth_session.mount("http://", adapter)
            self.auth_session.mount("https://", adapter)
            
            # Authenticate
            if await self.authenticate():
                self.status = ClientStatus.ACTIVE
                logger.info(f"{self.platform.value} API client initialized successfully")
            else:
                self.status = ClientStatus.AUTHENTICATION_ERROR
                raise AuthenticationError(f"Failed to authenticate {self.platform.value} client")
                
        except Exception as e:
            self.status = ClientStatus.ERROR
            logger.error(f"Failed to initialize {self.platform.value} client: {str(e)}")
            raise APIError(f"Client initialization failed: {str(e)}")
    
    async def request(self, method: str, endpoint: str, 
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     cache_key: Optional[str] = None) -> APIResponse:
        """Make authenticated API request with full error handling"""
        
        # Check circuit breaker
        if self.circuit_breaker.is_open():
            self.status = ClientStatus.CIRCUIT_OPEN
            raise APIError("Circuit breaker is open")
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        # Authentication check
        await self._ensure_authenticated()
        
        # Build request URL
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Cache check
        if cache_key and self.cache_manager:
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                self.stats['cached_requests'] += 1
                return cached_response
        
        # Prepare request
        request_headers = self._build_request_headers()
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            # Make request
            async with self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                proxy=self.config.proxy
            ) as response:
                
                response_time = time.time() - start_time
                response_data = await self._process_response(response)
                
                # Extract rate limit info
                rate_limit_info = self._extract_rate_limit_info(dict(response.headers))
                
                # Create API response
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    headers=dict(response.headers),
                    url=str(response.url),
                    response_time=response_time,
                    rate_limit_remaining=rate_limit_info.get('remaining'),
                    rate_limit_reset=rate_limit_info.get('reset')
                )
                
                # Update statistics
                self._update_statistics(response_time, True)
                
                # Cache response if successful
                if cache_key and self.cache_manager and 200 <= response.status < 300:
                    await self.cache_manager.set(
                        cache_key, api_response, ttl=self.config.cache_ttl
                    )
                
                # Circuit breaker success
                self.circuit_breaker.record_success()
                
                return api_response
                
        except aiohttp.ClientResponseError as e:
            self._handle_client_error(e)
            raise
        except Exception as e:
            self._update_statistics(time.time() - start_time, False)
            self.circuit_breaker.record_failure()
            logger.error(f"API request failed: {str(e)}")
            raise APIError(f"Request failed: {str(e)}")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                 cache_key: Optional[str] = None) -> APIResponse:
        """Make GET request"""
        return await self.request("GET", endpoint, params=params, cache_key=cache_key)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make POST request"""
        return await self.request("POST", endpoint, data=data, headers=headers)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make PUT request"""
        return await self.request("PUT", endpoint, data=data)
    
    async def delete(self, endpoint: str) -> APIResponse:
        """Make DELETE request"""
        return await self.request("DELETE", endpoint)
    
    async def paginated_request(self, endpoint: str, 
                               params: Optional[Dict[str, Any]] = None,
                               max_pages: int = 10) -> List[APIResponse]:
        """Handle paginated API requests"""
        responses = []
        current_params = params.copy() if params else {}
        page_count = 0
        
        while page_count < max_pages:
            response = await self.get(endpoint, params=current_params)
            responses.append(response)
            
            # Check for pagination
            pagination_info = self._extract_pagination_info(response)
            if not pagination_info or not pagination_info.get('has_next'):
                break
            
            # Update params for next page
            current_params.update(pagination_info.get('next_params', {}))
            page_count += 1
        
        return responses
    
    async def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated and tokens are valid"""
        async with self.auth_lock:
            current_time = time.time()
            
            # Check if authentication needs refresh
            if (not self.is_authenticated or 
                (self.config.auth_credentials.expires_at and 
                 self.config.auth_credentials.expires_at <= current_time + 300)):  # 5 min buffer
                
                if not await self.refresh_authentication():
                    raise AuthenticationError("Failed to refresh authentication")
    
    async def _process_response(self, response: aiohttp.ClientResponse) -> Any:
        """Process HTTP response and extract data"""
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            return await response.json()
        elif 'text/' in content_type:
            return await response.text()
        else:
            return await response.read()
    
    def _extract_pagination_info(self, response: APIResponse) -> Optional[Dict[str, Any]]:
        """Extract pagination information from response (override in subclasses)"""
        return None
    
    def _handle_client_error(self, error: aiohttp.ClientResponseError) -> None:
        """Handle client-specific HTTP errors"""
        if error.status == 429:
            self.status = ClientStatus.RATE_LIMITED
            self.stats['rate_limited_requests'] += 1
            raise RateLimitError("Rate limit exceeded")
        elif error.status == 401:
            self.status = ClientStatus.AUTHENTICATION_ERROR
            raise AuthenticationError("Authentication failed")
        else:
            self.status = ClientStatus.ERROR
            raise APIError(f"HTTP {error.status}: {error.message}")
    
    def _update_statistics(self, response_time: float, success: bool) -> None:
        """Update client statistics"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update average response time
        total_requests = self.stats['total_requests']
        current_avg = self.stats['average_response_time']
        self.stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get client health and status information"""
        return {
            'platform': self.platform.value,
            'status': self.status.value,
            'authenticated': self.is_authenticated,
            'circuit_breaker_open': self.circuit_breaker.is_open(),
            'rate_limiter_available': self.rate_limiter.is_available(),
            'statistics': self.stats.copy()
        }
    
    async def cleanup(self) -> None:
        """Cleanup client resources"""
        if self.session:
            await self.session.close()
        
        if self.auth_session:
            self.auth_session.close()
        
        self.status = ClientStatus.DISABLED
        logger.info(f"{self.platform.value} client cleaned up")


class TwitterAPIClient(APIClient):
    """Twitter API v2 client implementation"""
    
    def __init__(self, config: APIClientConfig):
        super().__init__(config)
        self.api_version = "2"
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API using Bearer Token"""
        try:
            if self.config.auth_credentials.bearer_token:
                # Test authentication with a simple request
                headers = {"Authorization": f"Bearer {self.config.auth_credentials.bearer_token}"}
                
                async with self.session.get(
                    f"{self.config.base_url}/users/me",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        self.is_authenticated = True
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {str(e)}")
            return False
    
    async def refresh_authentication(self) -> bool:
        """Twitter Bearer tokens don't need refresh"""
        return await self.authenticate()
    
    def _build_request_headers(self) -> Dict[str, str]:
        """Build Twitter-specific request headers"""
        headers = {
            "Authorization": f"Bearer {self.config.auth_credentials.bearer_token}",
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json"
        }
        headers.update(self.config.custom_headers)
        return headers
    
    def _extract_rate_limit_info(self, headers: Dict[str, str]) -> Dict[str, Optional[int]]:
        """Extract Twitter rate limit information"""
        return {
            'remaining': int(headers.get('x-rate-limit-remaining', 0)),
            'reset': int(headers.get('x-rate-limit-reset', 0))
        }


class YouTubeAPIClient(APIClient):
    """YouTube Data API v3 client implementation"""
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube API using API key"""
        try:
            # Test with a simple quota-free request
            params = {'key': self.config.auth_credentials.api_key, 'part': 'id'}
            
            async with self.session.get(
                f"{self.config.base_url}/channels",
                params=params
            ) as response:
                if response.status == 200:
                    self.is_authenticated = True
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {str(e)}")
            return False
    
    async def refresh_authentication(self) -> bool:
        """YouTube API keys don't need refresh"""
        return await self.authenticate()
    
    def _build_request_headers(self) -> Dict[str, str]:
        """Build YouTube-specific request headers"""
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "application/json"
        }
        headers.update(self.config.custom_headers)
        return headers
    
    def _extract_rate_limit_info(self, headers: Dict[str, str]) -> Dict[str, Optional[int]]:
        """YouTube doesn't provide rate limit headers"""
        return {'remaining': None, 'reset': None}


class APIClientManager:
    """
    Enterprise API Client Management System
    
    Manages multiple API clients, handles failover, load balancing, and monitoring.
    """
    
    def __init__(self):
        self.clients: Dict[str, APIClient] = {}
        self.client_configs: Dict[PlatformType, List[APIClientConfig]] = {}
        self.health_checker = None
        
        # Client factory mapping
        self.client_factory = {
            PlatformType.TWITTER: TwitterAPIClient,
            PlatformType.YOUTUBE: YouTubeAPIClient,
            # Other platform clients would be added here
        }
        
        logger.info("APIClientManager initialized")
    
    async def register_client(self, config: APIClientConfig, 
                            client_id: Optional[str] = None) -> str:
        """Register and initialize a new API client"""
        if not client_id:
            client_id = f"{config.platform.value}_{uuid.uuid4().hex[:8]}"
        
        try:
            client_class = self.client_factory.get(config.platform)
            if not client_class:
                raise APIError(f"Unsupported platform: {config.platform}")
            
            client = client_class(config)
            await client.initialize()
            
            self.clients[client_id] = client
            
            # Track configurations for failover
            if config.platform not in self.client_configs:
                self.client_configs[config.platform] = []
            self.client_configs[config.platform].append(config)
            
            logger.info(f"API client {client_id} registered successfully")
            return client_id
            
        except Exception as e:
            logger.error(f"Failed to register client {client_id}: {str(e)}")
            raise APIError(f"Client registration failed: {str(e)}")
    
    async def get_client(self, client_id: str) -> Optional[APIClient]:
        """Get API client by ID"""
        return self.clients.get(client_id)
    
    async def get_platform_client(self, platform: PlatformType) -> Optional[APIClient]:
        """Get healthy client for specific platform"""
        for client_id, client in self.clients.items():
            if (client.platform == platform and 
                client.status == ClientStatus.ACTIVE):
                return client
        return None
    
    async def remove_client(self, client_id: str) -> bool:
        """Remove and cleanup API client"""
        client = self.clients.get(client_id)
        if client:
            await client.cleanup()
            del self.clients[client_id]
            logger.info(f"API client {client_id} removed")
            return True
        return False
    
    async def get_all_health_status(self) -> Dict[str, Any]:
        """Get health status for all registered clients"""
        health_status = {}
        
        for client_id, client in self.clients.items():
            health_status[client_id] = await client.get_health_status()
        
        return {
            'total_clients': len(self.clients),
            'clients': health_status,
            'platforms': list(set(client.platform.value for client in self.clients.values()))
        }
    
    async def cleanup_all(self) -> None:
        """Cleanup all registered clients"""
        for client_id in list(self.clients.keys()):
            await self.remove_client(client_id)
        
        self.clients.clear()
        self.client_configs.clear()
        logger.info("All API clients cleaned up")


# Factory functions for easy instantiation
def create_twitter_client(bearer_token: str, **kwargs) -> APIClientConfig:
    """Create Twitter API client configuration"""
    return APIClientConfig(
        platform=PlatformType.TWITTER,
        base_url="https://api.twitter.com/2",
        auth_credentials=AuthCredentials(
            auth_type=AuthType.BEARER_TOKEN,
            bearer_token=bearer_token
        ),
        **kwargs
    )


def create_youtube_client(api_key: str, **kwargs) -> APIClientConfig:
    """Create YouTube API client configuration"""
    return APIClientConfig(
        platform=PlatformType.YOUTUBE,
        base_url="https://www.googleapis.com/youtube/v3",
        auth_credentials=AuthCredentials(
            auth_type=AuthType.API_KEY,
            api_key=api_key
        ),
        **kwargs
    )
