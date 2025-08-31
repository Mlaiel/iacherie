"""
Platform Integration Manager
===========================

Enterprise-grade platform integration manager for seamless connectivity across
social media platforms, streaming services, and content distribution networks.

This module provides comprehensive platform integration capabilities including:
- Multi-platform API management with intelligent fallback strategies
- Rate limiting and quota management across platforms
- Authentication and authorization handling
- Platform-specific content adaptation and optimization
- Real-time API health monitoring and circuit breaker patterns

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  IMPORTANT LEGAL NOTICE 
This code is the intellectual property of Fahed Mlaiel. Any unauthorized use,
reproduction, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from urllib.parse import urljoin
import aiohttp
import jwt
from cryptography.fernet import Fernet

from ..utils.rate_limiter import RateLimiter
from ..utils.circuit_breaker import CircuitBreaker
from ..config.platform_config import PlatformConfig
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...core.encryption import EncryptionManager
from ...models.platform_integration import PlatformConnection, APICredentials, PlatformMetrics


class PlatformType(Enum):
    """Supported platform types for integration."""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"


class AuthenticationType(Enum):
    """Authentication methods supported by platforms."""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    JWT_TOKEN = "jwt_token"
    SESSION_COOKIE = "session_cookie"


class APIEndpointType(Enum):
    """API endpoint categories."""
    CONTENT_DISCOVERY = "content_discovery"
    CONTENT_UPLOAD = "content_upload"
    USER_MANAGEMENT = "user_management"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    SOCIAL_INTERACTION = "social_interaction"
    SEARCH = "search"
    STREAMING = "streaming"


@dataclass
class PlatformCredentials:
    """Platform authentication credentials."""
    platform: PlatformType
    auth_type: AuthenticationType
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIEndpoint:
    """API endpoint configuration."""
    endpoint_type: APIEndpointType
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: int = 100
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker_threshold: int = 5


@dataclass
class PlatformConfiguration:
    """Platform configuration settings."""
    platform: PlatformType
    base_url: str
    endpoints: Dict[APIEndpointType, APIEndpoint]
    credentials: PlatformCredentials
    rate_limits: Dict[str, int] = field(default_factory=dict)
    quotas: Dict[str, int] = field(default_factory=dict)
    features: Set[str] = field(default_factory=set)
    health_check_url: Optional[str] = None
    status: str = "active"
    last_health_check: Optional[datetime] = None


@dataclass
class PlatformResponse:
    """Standardized platform API response."""
    platform: PlatformType
    endpoint_type: APIEndpointType
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    timestamp: datetime
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformIntegrationManager:
    """
    Enterprise-grade platform integration manager for multi-platform operations.
    
    Features:
    - Multi-platform API management
    - Intelligent authentication handling
    - Rate limiting and quota management
    - Circuit breaker patterns for fault tolerance
    - Real-time health monitoring
    - Automatic credential refresh
    """
    
    def __init__(self, config: Optional[PlatformConfig] = None):
        """Initialize platform integration manager."""
        self.config = config or PlatformConfig()
        self.logger = get_logger(__name__)
        self.encryption_manager = EncryptionManager()
        
        # Platform configurations
        self.platforms: Dict[PlatformType, PlatformConfiguration] = {}
        
        # Rate limiters per platform
        self.rate_limiters: Dict[PlatformType, RateLimiter] = {}
        
        # Circuit breakers per endpoint
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Active sessions
        self.sessions: Dict[PlatformType, aiohttp.ClientSession] = {}
        
        # Health monitoring
        self.health_status: Dict[PlatformType, bool] = {}
        self.last_health_checks: Dict[PlatformType, datetime] = {}
        
        # Metrics tracking
        self.metrics: Dict[PlatformType, PlatformMetrics] = {}
        
        # Initialize default platform configurations
        self._initialize_platform_configs()
    
    def _initialize_platform_configs(self):
        """Initialize default platform configurations."""
        # YouTube configuration
        youtube_endpoints = {
            APIEndpointType.CONTENT_DISCOVERY: APIEndpoint(
                endpoint_type=APIEndpointType.CONTENT_DISCOVERY,
                url="/youtube/v3/search",
                rate_limit=100,
                timeout=30
            ),
            APIEndpointType.ANALYTICS: APIEndpoint(
                endpoint_type=APIEndpointType.ANALYTICS,
                url="/youtube/analytics/v2/reports",
                rate_limit=50,
                timeout=60
            ),
            APIEndpointType.CONTENT_UPLOAD: APIEndpoint(
                endpoint_type=APIEndpointType.CONTENT_UPLOAD,
                url="/upload/youtube/v3/videos",
                method="POST",
                rate_limit=10,
                timeout=300
            )
        }
        
        # Spotify configuration
        spotify_endpoints = {
            APIEndpointType.CONTENT_DISCOVERY: APIEndpoint(
                endpoint_type=APIEndpointType.CONTENT_DISCOVERY,
                url="/v1/search",
                rate_limit=100,
                timeout=30
            ),
            APIEndpointType.ANALYTICS: APIEndpoint(
                endpoint_type=APIEndpointType.ANALYTICS,
                url="/v1/me/player/recently-played",
                rate_limit=100,
                timeout=30
            ),
            APIEndpointType.USER_MANAGEMENT: APIEndpoint(
                endpoint_type=APIEndpointType.USER_MANAGEMENT,
                url="/v1/me",
                rate_limit=50,
                timeout=30
            )
        }
        
        # Instagram configuration
        instagram_endpoints = {
            APIEndpointType.CONTENT_DISCOVERY: APIEndpoint(
                endpoint_type=APIEndpointType.CONTENT_DISCOVERY,
                url="/v12.0/me/media",
                rate_limit=200,
                timeout=30
            ),
            APIEndpointType.ANALYTICS: APIEndpoint(
                endpoint_type=APIEndpointType.ANALYTICS,
                url="/v12.0/{media-id}/insights",
                rate_limit=100,
                timeout=30
            )
        }
        
        # Store platform configurations
        self.platforms = {
            PlatformType.YOUTUBE: PlatformConfiguration(
                platform=PlatformType.YOUTUBE,
                base_url="https://www.googleapis.com",
                endpoints=youtube_endpoints,
                credentials=PlatformCredentials(
                    platform=PlatformType.YOUTUBE,
                    auth_type=AuthenticationType.OAUTH2
                ),
                health_check_url="https://www.googleapis.com/youtube/v3/channels"
            ),
            PlatformType.SPOTIFY: PlatformConfiguration(
                platform=PlatformType.SPOTIFY,
                base_url="https://api.spotify.com",
                endpoints=spotify_endpoints,
                credentials=PlatformCredentials(
                    platform=PlatformType.SPOTIFY,
                    auth_type=AuthenticationType.OAUTH2
                ),
                health_check_url="https://api.spotify.com/v1/me"
            ),
            PlatformType.INSTAGRAM: PlatformConfiguration(
                platform=PlatformType.INSTAGRAM,
                base_url="https://graph.instagram.com",
                endpoints=instagram_endpoints,
                credentials=PlatformCredentials(
                    platform=PlatformType.INSTAGRAM,
                    auth_type=AuthenticationType.OAUTH2
                ),
                health_check_url="https://graph.instagram.com/me"
            )
        }
    
    async def initialize_platform(self, platform: PlatformType, credentials: PlatformCredentials) -> bool:
        """
        Initialize platform connection with credentials.
        
        Args:
            platform: Platform to initialize
            credentials: Authentication credentials
            
        Returns:
            bool: True if initialization successful
        """



        try:
            if platform not in self.platforms:
                self.logger.error(f"Unsupported platform: {platform}")
                return False
            
            # Store encrypted credentials
            self.platforms[platform].credentials = credentials
            await self._encrypt_and_store_credentials(platform, credentials)
            
            # Initialize rate limiter
            self.rate_limiters[platform] = RateLimiter(
                max_requests=self.platforms[platform].rate_limits.get("default", 100),
                time_window=60
            )
            
            # Initialize circuit breakers for endpoints
            for endpoint_type, endpoint in self.platforms[platform].endpoints.items():
                breaker_key = f"{platform.value}_{endpoint_type.value}"
                self.circuit_breakers[breaker_key] = CircuitBreaker(
                    failure_threshold=endpoint.circuit_breaker_threshold,
                    recovery_timeout=30,
                    expected_exception=Exception
                )
            
            # Create HTTP session
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
            timeout = aiohttp.ClientTimeout(total=300)
            
            self.sessions[platform] = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self._get_default_headers(platform)
            )
            
            # Initialize metrics
            self.metrics[platform] = PlatformMetrics(
                platform=platform,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0
            )
            
            # Perform initial health check
            health_status = await self._perform_health_check(platform)
            self.health_status[platform] = health_status
            
            self.logger.info(f"Platform {platform.value} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize platform {platform.value}: {str(e)}")
            return False
    
    async def make_api_request(
        self,
        platform: PlatformType,
        endpoint_type: APIEndpointType,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> PlatformResponse:
        """
        Make API request to platform endpoint.
        
        Args:
            platform: Target platform
            endpoint_type: Type of endpoint
            params: Query parameters
            data: Request data
            headers: Additional headers
            
        Returns:
            PlatformResponse: Standardized response
        """
        start_time = time.time()
        
        try:
            # Validate platform and endpoint
            if platform not in self.platforms:
                raise ValueError(f"Platform {platform.value} not configured")
            
            platform_config = self.platforms[platform]
            if endpoint_type not in platform_config.endpoints:
                raise ValueError(f"Endpoint {endpoint_type.value} not configured for {platform.value}")
            
            endpoint = platform_config.endpoints[endpoint_type]
            
            # Check rate limits
            rate_limiter = self.rate_limiters.get(platform)
            if rate_limiter and not await rate_limiter.acquire():
                raise Exception("Rate limit exceeded")
            
            # Check circuit breaker
            breaker_key = f"{platform.value}_{endpoint_type.value}"
            circuit_breaker = self.circuit_breakers.get(breaker_key)
            
            if circuit_breaker and circuit_breaker.state == "open":
                raise Exception("Circuit breaker is open")
            
            # Ensure valid authentication
            await self._ensure_valid_authentication(platform)
            
            # Prepare request
            url = urljoin(platform_config.base_url, endpoint.url)
            request_headers = {**endpoint.headers}
            
            if headers:
                request_headers.update(headers)
            
            # Add authentication headers
            auth_headers = await self._get_authentication_headers(platform)
            request_headers.update(auth_headers)
            
            # Make request
            session = self.sessions[platform]
            
            async with session.request(
                method=endpoint.method,
                url=url,
                params=params,
                json=data if endpoint.method != "GET" else None,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as response:
                
                response_time = time.time() - start_time
                response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                # Update metrics
                await self._update_metrics(platform, response.status, response_time)
                
                # Create response object
                platform_response = PlatformResponse(
                    platform=platform,
                    endpoint_type=endpoint_type,
                    status_code=response.status,
                    data=response_data,
                    headers=dict(response.headers),
                    response_time=response_time,
                    timestamp=datetime.utcnow()
                )
                
                if response.status >= 400:
                    platform_response.error = f"HTTP {response.status}: {response_data}"
                    
                    # Record failure in circuit breaker
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                        
                    self.logger.warning(f"API request failed: {platform_response.error}")
                else:
                    # Record success in circuit breaker
                    if circuit_breaker:
                        circuit_breaker.record_success()
                
                return platform_response
                
        except Exception as e:
            response_time = time.time() - start_time
            
            # Update metrics for failed request
            await self._update_metrics(platform, 500, response_time)
            
            # Record failure in circuit breaker
            breaker_key = f"{platform.value}_{endpoint_type.value}"
            circuit_breaker = self.circuit_breakers.get(breaker_key)
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            self.logger.error(f"API request failed for {platform.value}: {str(e)}")
            
            return PlatformResponse(
                platform=platform,
                endpoint_type=endpoint_type,
                status_code=500,
                data=None,
                headers={},
                response_time=response_time,
                timestamp=datetime.utcnow(),
                error=str(e)
            )
    
    async def _ensure_valid_authentication(self, platform: PlatformType):
        """Ensure platform authentication is valid and refresh if needed."""
        credentials = self.platforms[platform].credentials
        
        if not credentials:
            raise Exception(f"No credentials configured for {platform.value}")
        
        # Check if token is expired and refresh if needed
        if credentials.expires_at and credentials.expires_at <= datetime.utcnow():
            await self._refresh_authentication(platform)
    
    async def _refresh_authentication(self, platform: PlatformType):
        """Refresh authentication credentials for platform."""



        try:
            credentials = self.platforms[platform].credentials
            
            if credentials.auth_type == AuthenticationType.OAUTH2:
                if not credentials.refresh_token:
                    raise Exception("No refresh token available")
                
                # Refresh OAuth2 token
                await self._refresh_oauth2_token(platform, credentials)
                
            elif credentials.auth_type == AuthenticationType.JWT_TOKEN:
                # Refresh JWT token
                await self._refresh_jwt_token(platform, credentials)
            
            self.logger.info(f"Authentication refreshed for {platform.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh authentication for {platform.value}: {str(e)}")
            raise
    
    async def _refresh_oauth2_token(self, platform: PlatformType, credentials: PlatformCredentials):
        """Refresh OAuth2 access token."""
        platform_config = self.platforms[platform]
        
        # Platform-specific token refresh endpoints
        refresh_urls = {
            PlatformType.YOUTUBE: "https://oauth2.googleapis.com/token",
            PlatformType.SPOTIFY: "https://accounts.spotify.com/api/token",
            PlatformType.INSTAGRAM: "https://graph.instagram.com/oauth/access_token"
        }
        
        refresh_url = refresh_urls.get(platform)
        if not refresh_url:
            raise Exception(f"Token refresh not supported for {platform.value}")
        
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": credentials.refresh_token,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret
            }
            
            async with session.post(refresh_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    # Update credentials
                    credentials.access_token = token_data.get("access_token")
                    if "refresh_token" in token_data:
                        credentials.refresh_token = token_data["refresh_token"]
                    
                    if "expires_in" in token_data:
                        expires_in = token_data["expires_in"]
                        credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    # Store updated credentials
                    await self._encrypt_and_store_credentials(platform, credentials)
                else:
                    raise Exception(f"Token refresh failed: {response.status}")
    
    async def _get_authentication_headers(self, platform: PlatformType) -> Dict[str, str]:
        """Get authentication headers for platform."""
        credentials = self.platforms[platform].credentials
        headers = {}
        
        if credentials.auth_type == AuthenticationType.OAUTH2:
            if credentials.access_token:
                headers["Authorization"] = f"Bearer {credentials.access_token}"
        
        elif credentials.auth_type == AuthenticationType.API_KEY:
            if credentials.api_key:
                headers["X-API-Key"] = credentials.api_key
        
        elif credentials.auth_type == AuthenticationType.BEARER_TOKEN:
            if credentials.access_token:
                headers["Authorization"] = f"Bearer {credentials.access_token}"
        
        return headers
    
    def _get_default_headers(self, platform: PlatformType) -> Dict[str, str]:
        """Get default headers for platform."""



        return {
            "User-Agent": f"IA-Influencer-Agent/1.0 ({platform.value})",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def _perform_health_check(self, platform: PlatformType) -> bool:
        """Perform health check for platform."""



        try:
            platform_config = self.platforms[platform]
            if not platform_config.health_check_url:
                return True  # Assume healthy if no health check URL
            
            session = self.sessions.get(platform)
            if not session:
                return False
            
            headers = await self._get_authentication_headers(platform)
            
            async with session.get(
                platform_config.health_check_url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                is_healthy = response.status < 400
                self.last_health_checks[platform] = datetime.utcnow()
                return is_healthy
                
        except Exception as e:
            self.logger.warning(f"Health check failed for {platform.value}: {str(e)}")
            return False
    
    async def _update_metrics(self, platform: PlatformType, status_code: int, response_time: float):
        """Update platform metrics."""
        if platform not in self.metrics:
            return
        
        metrics = self.metrics[platform]
        metrics.total_requests += 1
        
        if status_code < 400:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update average response time
        total_time = metrics.average_response_time * (metrics.total_requests - 1) + response_time
        metrics.average_response_time = total_time / metrics.total_requests
    
    async def _encrypt_and_store_credentials(self, platform: PlatformType, credentials: PlatformCredentials):
        """Encrypt and store platform credentials."""



        try:
            # Serialize credentials
            credentials_data = {
                "platform": credentials.platform.value,
                "auth_type": credentials.auth_type.value,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "access_token": credentials.access_token,
                "refresh_token": credentials.refresh_token,
                "api_key": credentials.api_key,
                "expires_at": credentials.expires_at.isoformat() if credentials.expires_at else None,
                "scopes": credentials.scopes,
                "metadata": credentials.metadata
            }
            
            # Encrypt credentials
            encrypted_data = self.encryption_manager.encrypt(json.dumps(credentials_data))
            
            # Store in database
            async with get_database_session() as db:
                existing_creds = await db.execute(
                    "SELECT id FROM platform_credentials WHERE platform = :platform",
                    {"platform": platform.value}
                )
                
                if existing_creds:
                    await db.execute(
                        "UPDATE platform_credentials SET encrypted_data = :data, updated_at = :updated WHERE platform = :platform",
                        {"data": encrypted_data, "updated": datetime.utcnow(), "platform": platform.value}
                    )
                else:
                    await db.execute(
                        "INSERT INTO platform_credentials (platform, encrypted_data, created_at) VALUES (:platform, :data, :created)",
                        {"platform": platform.value, "data": encrypted_data, "created": datetime.utcnow()}
                    )
                
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store credentials for {platform.value}: {str(e)}")
    
    async def get_platform_metrics(self, platform: PlatformType) -> Optional[PlatformMetrics]:
        """Get metrics for specific platform."""



        return self.metrics.get(platform)
    
    async def get_all_platform_metrics(self) -> Dict[PlatformType, PlatformMetrics]:
        """Get metrics for all platforms."""



        return self.metrics.copy()
    
    async def check_platform_health(self, platform: PlatformType) -> bool:
        """Check health status of specific platform."""



        return await self._perform_health_check(platform)
    
    async def check_all_platform_health(self) -> Dict[PlatformType, bool]:
        """Check health status of all platforms."""
        health_results = {}
        
        for platform in self.platforms:
            health_results[platform] = await self._perform_health_check(platform)
        
        return health_results
    
    async def close(self):
        """Close all platform connections and cleanup resources."""



        try:
            # Close all HTTP sessions
            for session in self.sessions.values():
                await session.close()
            
            self.sessions.clear()
            
            # Clear circuit breakers
            self.circuit_breakers.clear()
            
            # Clear rate limiters
            self.rate_limiters.clear()
            
            self.logger.info("Platform integration manager closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing platform integration manager: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry."""



        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Factory functions and utilities
async def create_platform_integration_manager(config: Optional[PlatformConfig] = None) -> PlatformIntegrationManager:
    """Create and initialize platform integration manager."""



    return PlatformIntegrationManager(config)


async def initialize_all_platforms(
    manager: PlatformIntegrationManager,
    credentials_map: Dict[PlatformType, PlatformCredentials]
) -> Dict[PlatformType, bool]:
    """Initialize all platforms with their credentials."""
    results = {}
    
    for platform, credentials in credentials_map.items():
        results[platform] = await manager.initialize_platform(platform, credentials)
    
    return results


async def perform_bulk_health_check(manager: PlatformIntegrationManager) -> Dict[PlatformType, bool]:
    """Perform health check on all configured platforms."""



    return await manager.check_all_platform_health()


# Export all components
__all__ = [
    "PlatformIntegrationManager",
    "PlatformType",
    "AuthenticationType",
    "APIEndpointType",
    "PlatformCredentials",
    "APIEndpoint",
    "PlatformConfiguration",
    "PlatformResponse",
    "create_platform_integration_manager",
    "initialize_all_platforms",
    "perform_bulk_health_check"
]
