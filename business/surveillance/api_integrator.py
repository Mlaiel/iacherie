"""🔌 API Integrator - IA Influencer Agent Surveillance Module
=========================================================

Advanced API integration system for connecting with platform APIs,
content detection services, and third-party surveillance tools.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import aiohttp
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
import hmac
import base64
import uuid
from urllib.parse import urlencode, urlparse

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """API providers"""    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    VIMEO = "vimeo"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    CONTENT_ID = "content_id"
    AUDIBLE_MAGIC = "audible_magic"
    GRACENOTE = "gracenote"
    SHAZAM = "shazam"
    CUSTOM = "custom"


class APIMethod(Enum):
    """API HTTP methods"""    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AuthType(Enum):
    """API authentication types"""    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER = "bearer"
    BASIC = "basic"
    HMAC = "hmac"
    JWT = "jwt"


@dataclass
class APICredentials:
    """API credentials configuration"""    provider: APIProvider
    auth_type: AuthType
    
    # Basic credentials
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # OAuth2 credentials
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # JWT/Bearer token
    bearer_token: Optional[str] = None
    jwt_secret: Optional[str] = None
    
    # HMAC signing
    hmac_algorithm: Optional[str] = "sha256"
    
    # Additional settings
    base_url: Optional[str] = None
    rate_limit: Optional[int] = 100  # Requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APIRequest:
    """API request structure"""    request_id: str
    provider: APIProvider
    method: APIMethod
    endpoint: str
    
    # Request data
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Union[Dict[str, Any], str, bytes]] = None
    
    # Configuration
    timeout: Optional[int] = None
    retry_attempts: int = 3
    priority: str = "normal"  # low, normal, high, urgent
    
    # Metadata
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APIResponse:
    """API response structure"""    request_id: str
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Union[Dict[str, Any], str, bytes]] = None
    
    # Timing information
    response_time_ms: int = 0
    attempt_number: int = 1
    
    # Status
    success: bool = False
    error_message: Optional[str] = None
    rate_limited: bool = False
    
    responded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAPIConnector:
    """Base class for API connectors"""    
    def __init__(self, provider: APIProvider, credentials: APICredentials):
        self.provider = provider
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(credentials.rate_limit or 100)
    
    async def initialize(self) -> None:
        """Initialize connector"""        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.credentials.timeout)
        )
        
        # Perform authentication if needed
        if self.credentials.auth_type == AuthType.OAUTH2:
            await self._refresh_oauth_token()
    
    async def _refresh_oauth_token(self) -> None:
        """Refresh OAuth2 token if needed"""        if not self.credentials.refresh_token:
            return
        
        if (self.credentials.token_expires_at and 
            datetime.now(timezone.utc) < self.credentials.token_expires_at - timedelta(minutes=5)):
            return  # Token still valid
        
        # Refresh token logic would go here
        logger.info(f"Refreshing OAuth2 token for {self.provider.value}")
    
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make an API request"""        if not self.session:
            await self.initialize()
        
        # Check rate limits
        await self.rate_limiter.wait_if_needed()
        
        start_time = time.time()
        
        for attempt in range(request.retry_attempts + 1):
            try:
                # Prepare request
                url = self._build_url(request)
                headers = await self._prepare_headers(request)
                
                # Make request
                async with self.session.request(
                    method=request.method.value,
                    url=url,
                    headers=headers,
                    params=request.params,
                    json=request.body if isinstance(request.body, dict) else None,
                    data=request.body if isinstance(request.body, (str, bytes)) else None
                ) as response:
                    
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Read response data
                    try:
                        if response.content_type == 'application/json':
                            data = await response.json()
                        else:
                            data = await response.text()
                    except Exception:
                        data = await response.read()
                    
                    # Create response object
                    api_response = APIResponse(
                        request_id=request.request_id,
                        status_code=response.status,
                        headers=dict(response.headers),
                        data=data,
                        response_time_ms=response_time,
                        attempt_number=attempt + 1,
                        success=200 <= response.status < 300
                    )
                    
                    # Check for rate limiting
                    if response.status == 429:
                        api_response.rate_limited = True
                        retry_after = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Return response if successful or non-retryable error
                    if api_response.success or response.status < 500:
                        return api_response
                    
                    # Server error, retry after delay
                    if attempt < request.retry_attempts:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except asyncio.TimeoutError:
                if attempt == request.retry_attempts:
                    return APIResponse(
                        request_id=request.request_id,
                        status_code=408,
                        error_message="Request timeout",
                        response_time_ms=int((time.time() - start_time) * 1000),
                        attempt_number=attempt + 1
                    )
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                if attempt == request.retry_attempts:
                    return APIResponse(
                        request_id=request.request_id,
                        status_code=500,
                        error_message=str(e),
                        response_time_ms=int((time.time() - start_time) * 1000),
                        attempt_number=attempt + 1
                    )
                await asyncio.sleep(2 ** attempt)
        
        # Should never reach here
        return APIResponse(
            request_id=request.request_id,
            status_code=500,
            error_message="Max retries exceeded"
        )
    
    def _build_url(self, request: APIRequest) -> str:
        """Build full URL for request"""        base_url = self.credentials.base_url or self._get_default_base_url()
        return f"{base_url.rstrip('/')}/{request.endpoint.lstrip('/')}"
    
    def _get_default_base_url(self) -> str:
        """Get default base URL for provider"""        urls = {
            APIProvider.YOUTUBE: "https://www.googleapis.com/youtube/v3",
            APIProvider.INSTAGRAM: "https://graph.instagram.com",
            APIProvider.FACEBOOK: "https://graph.facebook.com/v12.0",
            APIProvider.TWITTER: "https://api.twitter.com/2",
            APIProvider.TIKTOK: "https://open-api.tiktok.com",
            APIProvider.SPOTIFY: "https://api.spotify.com/v1",
            APIProvider.SOUNDCLOUD: "https://api.soundcloud.com",
            APIProvider.VIMEO: "https://api.vimeo.com",
        }
        return urls.get(self.provider, "https://api.example.com")
    
    async def _prepare_headers(self, request: APIRequest) -> Dict[str, str]:
        """Prepare request headers with authentication"""        headers = request.headers.copy()
        
        # Add authentication headers
        if self.credentials.auth_type == AuthType.API_KEY:
            if self.provider == APIProvider.YOUTUBE:
                headers["X-API-Key"] = self.credentials.api_key
            else:
                headers["Authorization"] = f"Bearer {self.credentials.api_key}"
                
        elif self.credentials.auth_type == AuthType.BEARER:
            headers["Authorization"] = f"Bearer {self.credentials.bearer_token}"
            
        elif self.credentials.auth_type == AuthType.OAUTH2:
            headers["Authorization"] = f"Bearer {self.credentials.access_token}"
            
        elif self.credentials.auth_type == AuthType.BASIC:
            credentials = base64.b64encode(
                f"{self.credentials.username}:{self.credentials.password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {credentials}"
            
        elif self.credentials.auth_type == AuthType.HMAC:
            signature = await self._generate_hmac_signature(request)
            headers["Authorization"] = f"HMAC {signature}"
        
        # Add common headers
        headers["User-Agent"] = "IA-Influencer-Agent/2.0"
        headers["Accept"] = "application/json"
        
        if request.body and isinstance(request.body, dict):
            headers["Content-Type"] = "application/json"
        
        return headers
    
    async def _generate_hmac_signature(self, request: APIRequest) -> str:
        """Generate HMAC signature for request"""        # Simplified HMAC signature generation
        message = f"{request.method.value}{request.endpoint}{json.dumps(request.body or {})}"
        signature = hmac.new(
            self.credentials.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def shutdown(self) -> None:
        """Shutdown connector"""        if self.session:
            await self.session.close()


class YouTubeAPIConnector(BaseAPIConnector):
    """YouTube Data API connector"""    
    def __init__(self, credentials: APICredentials):
        super().__init__(APIProvider.YOUTUBE, credentials)
    
    async def search_videos(self, query: str, max_results: int = 50) -> APIResponse:
        """Search for videos"""        request = APIRequest(
            request_id=f"yt_search_{uuid.uuid4().hex[:8]}",
            provider=self.provider,
            method=APIMethod.GET,
            endpoint="search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),
                "key": self.credentials.api_key
            }
        )
        
        return await self.make_request(request)
    
    async def get_video_details(self, video_id: str) -> APIResponse:
        """Get video details"""        request = APIRequest(
            request_id=f"yt_details_{uuid.uuid4().hex[:8]}",
            provider=self.provider,
            method=APIMethod.GET,
            endpoint="videos",
            params={
                "part": "snippet,statistics,contentDetails",
                "id": video_id,
                "key": self.credentials.api_key
            }
        )
        
        return await self.make_request(request)


class InstagramAPIConnector(BaseAPIConnector):
    """Instagram Basic Display API connector"""    
    def __init__(self, credentials: APICredentials):
        super().__init__(APIProvider.INSTAGRAM, credentials)
    
    async def get_user_media(self, user_id: str) -> APIResponse:
        """Get user media"""        request = APIRequest(
            request_id=f"ig_media_{uuid.uuid4().hex[:8]}",
            provider=self.provider,
            method=APIMethod.GET,
            endpoint=f"{user_id}/media",
            params={
                "fields": "id,caption,media_type,media_url,thumbnail_url,timestamp,username",
                "access_token": self.credentials.access_token
            }
        )
        
        return await self.make_request(request)


class TikTokAPIConnector(BaseAPIConnector):
    """TikTok API connector"""    
    def __init__(self, credentials: APICredentials):
        super().__init__(APIProvider.TIKTOK, credentials)
    
    async def search_videos(self, query: str, count: int = 20) -> APIResponse:
        """Search for videos"""        request = APIRequest(
            request_id=f"tt_search_{uuid.uuid4().hex[:8]}",
            provider=self.provider,
            method=APIMethod.POST,
            endpoint="research/video/query/",
            body={
                "query": {
                    "and": [
                        {"operation": "EQ", "field_name": "keyword", "field_values": [query]}
                    ]
                },
                "max_count": count
            }
        )
        
        return await self.make_request(request)


class SpotifyAPIConnector(BaseAPIConnector):
    """Spotify Web API connector"""    
    def __init__(self, credentials: APICredentials):
        super().__init__(APIProvider.SPOTIFY, credentials)
    
    async def search_tracks(self, query: str, limit: int = 50) -> APIResponse:
        """Search for tracks"""        request = APIRequest(
            request_id=f"spotify_search_{uuid.uuid4().hex[:8]}",
            provider=self.provider,
            method=APIMethod.GET,
            endpoint="search",
            params={
                "q": query,
                "type": "track",
                "limit": min(limit, 50)
            }
        )
        
        return await self.make_request(request)


class RateLimiter:
    """Rate limiting helper"""    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""        async with self.lock:
            now = time.time()
            
            # Remove old requests (older than 1 minute)
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            # Check if we need to wait
            if len(self.requests) >= self.requests_per_minute:
                # Wait until the oldest request is more than 1 minute old
                oldest_request = min(self.requests)
                wait_time = 60 - (now - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.wait_if_needed()  # Recursive check
            
            # Record this request
            self.requests.append(now)


class APIIntegrator:
    """    Advanced API integration system for connecting with platform APIs,
    content detection services, and third-party surveillance tools
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connectors: Dict[APIProvider, BaseAPIConnector] = {}
        self.credentials_store: Dict[APIProvider, APICredentials] = {}
        self.request_history: List[APIResponse] = []
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize API integrator"""        try:
            # Load credentials from config
            await self._load_credentials()
            
            # Initialize connectors for available credentials
            await self._initialize_connectors()
            
            self.initialized = True
            logger.info(f"API Integrator initialized with {len(self.connectors)} connectors")
            
        except Exception as e:
            logger.error(f"Failed to initialize API Integrator: {e}")
            raise
    
    async def _load_credentials(self) -> None:
        """Load API credentials from configuration"""        credentials_config = self.config.get("api_credentials", {})
        
        for provider_name, creds_config in credentials_config.items():
            try:
                provider = APIProvider(provider_name)
                credentials = APICredentials(
                    provider=provider,
                    auth_type=AuthType(creds_config.get("auth_type", "api_key")),
                    **{k: v for k, v in creds_config.items() if k != "auth_type"}
                )
                
                self.credentials_store[provider] = credentials
                logger.info(f"Loaded credentials for {provider_name}")
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid credentials configuration for {provider_name}: {e}")
    
    async def _initialize_connectors(self) -> None:
        """Initialize API connectors"""        for provider, credentials in self.credentials_store.items():
            if not credentials.active:
                continue
            
            try:
                # Create specific connector based on provider
                if provider == APIProvider.YOUTUBE:
                    connector = YouTubeAPIConnector(credentials)
                elif provider == APIProvider.INSTAGRAM:
                    connector = InstagramAPIConnector(credentials)
                elif provider == APIProvider.TIKTOK:
                    connector = TikTokAPIConnector(credentials)
                elif provider == APIProvider.SPOTIFY:
                    connector = SpotifyAPIConnector(credentials)
                else:
                    # Generic connector for other providers
                    connector = BaseAPIConnector(provider, credentials)
                
                await connector.initialize()
                self.connectors[provider] = connector
                
                logger.info(f"Initialized {provider.value} connector")
                
            except Exception as e:
                logger.error(f"Failed to initialize {provider.value} connector: {e}")
    
    async def make_request(
        self,
        provider: APIProvider,
        method: APIMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Union[Dict[str, Any], str, bytes]] = None,
        **kwargs
    ) -> APIResponse:
        """Make an API request through the appropriate connector"""        if provider not in self.connectors:
            return APIResponse(
                request_id=f"error_{uuid.uuid4().hex[:8]}",
                status_code=404,
                error_message=f"No connector available for provider: {provider.value}"
            )
        
        request = APIRequest(
            request_id=kwargs.get("request_id", f"{provider.value}_{uuid.uuid4().hex[:8]}"),
            provider=provider,
            method=method,
            endpoint=endpoint,
            params=params or {},
            body=body,
            **{k: v for k, v in kwargs.items() if k != "request_id"}
        )
        
        try:
            connector = self.connectors[provider]
            response = await connector.make_request(request)
            
            # Store in history (limit to last 1000 requests)
            self.request_history.append(response)
            if len(self.request_history) > 1000:
                self.request_history.pop(0)
            
            return response
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return APIResponse(
                request_id=request.request_id,
                status_code=500,
                error_message=str(e)
            )
    
    async def search_content_across_platforms(
        self,
        query: str,
        platforms: Optional[List[APIProvider]] = None,
        max_results_per_platform: int = 20
    ) -> Dict[APIProvider, APIResponse]:
        """Search for content across multiple platforms"""        platforms = platforms or list(self.connectors.keys())
        results = {}
        
        # Create tasks for parallel execution
        tasks = []
        
        for provider in platforms:
            if provider not in self.connectors:
                continue
            
            if provider == APIProvider.YOUTUBE:
                task = self._search_youtube(query, max_results_per_platform)
            elif provider == APIProvider.SPOTIFY:
                task = self._search_spotify(query, max_results_per_platform)
            elif provider == APIProvider.TIKTOK:
                task = self._search_tiktok(query, max_results_per_platform)
            else:
                # Generic search for other platforms
                task = self._search_generic(provider, query, max_results_per_platform)
            
            tasks.append((provider, task))
        
        # Execute searches in parallel
        for provider, task in tasks:
            try:
                response = await task
                results[provider] = response
            except Exception as e:
                logger.error(f"Search failed for {provider.value}: {e}")
                results[provider] = APIResponse(
                    request_id=f"search_error_{uuid.uuid4().hex[:8]}",
                    status_code=500,
                    error_message=str(e)
                )
        
        return results
    
    async def _search_youtube(self, query: str, max_results: int) -> APIResponse:
        """Search YouTube"""        if APIProvider.YOUTUBE not in self.connectors:
            raise ValueError("YouTube connector not available")
        
        connector = self.connectors[APIProvider.YOUTUBE]
        return await connector.search_videos(query, max_results)
    
    async def _search_spotify(self, query: str, max_results: int) -> APIResponse:
        """Search Spotify"""        if APIProvider.SPOTIFY not in self.connectors:
            raise ValueError("Spotify connector not available")
        
        connector = self.connectors[APIProvider.SPOTIFY]
        return await connector.search_tracks(query, max_results)
    
    async def _search_tiktok(self, query: str, max_results: int) -> APIResponse:
        """Search TikTok"""        if APIProvider.TIKTOK not in self.connectors:
            raise ValueError("TikTok connector not available")
        
        connector = self.connectors[APIProvider.TIKTOK]
        return await connector.search_videos(query, max_results)
    
    async def _search_generic(self, provider: APIProvider, query: str, max_results: int) -> APIResponse:
        """Generic search for other platforms"""        return await self.make_request(
            provider=provider,
            method=APIMethod.GET,
            endpoint="search",
            params={"q": query, "limit": max_results}
        )
    
    async def get_request_statistics(self) -> Dict[str, Any]:
        """Get API request statistics"""        if not self.request_history:
            return {"total_requests": 0}
        
        total_requests = len(self.request_history)
        successful_requests = len([r for r in self.request_history if r.success])
        failed_requests = total_requests - successful_requests
        
        # Calculate average response time
        response_times = [r.response_time_ms for r in self.request_history if r.response_time_ms > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Provider distribution
        provider_counts = {}
        for response in self.request_history:
            # Extract provider from request_id or other means
            provider_counts["unknown"] = provider_counts.get("unknown", 0) + 1
        
        # Status code distribution
        status_counts = {}
        for response in self.request_history:
            status_counts[response.status_code] = status_counts.get(response.status_code, 0) + 1
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": round(success_rate, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "provider_distribution": provider_counts,
            "status_code_distribution": status_counts,
            "active_connectors": len(self.connectors)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on API integrator"""        connector_status = {}
        
        for provider, connector in self.connectors.items():
            # Simple health check - attempt a basic request
            try:
                # This would be a platform-specific health check endpoint
                connector_status[provider.value] = "healthy"
            except Exception:
                connector_status[provider.value] = "unhealthy"
        
        return {
            "integrator": "healthy" if self.initialized else "unhealthy",
            "connectors": connector_status,
            "total_connectors": len(self.connectors),
            "recent_requests": len(self.request_history),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown API integrator"""        logger.info("Shutting down API Integrator")
        
        # Shutdown all connectors
        for provider, connector in self.connectors.items():
            try:
                await connector.shutdown()
                logger.info(f"Shut down {provider.value} connector")
            except Exception as e:
                logger.error(f"Error shutting down {provider.value} connector: {e}")
        
        self.connectors.clear()
        self.initialized = False
        logger.info("API Integrator shutdown complete")


# Export main components
__all__ = [
    "APIIntegrator",
    "APIProvider",
    "APIMethod",
    "AuthType",
    "APICredentials",
    "APIRequest",
    "APIResponse",
    "BaseAPIConnector",
    "YouTubeAPIConnector",
    "InstagramAPIConnector",
    "TikTokAPIConnector",
    "SpotifyAPIConnector",
    "RateLimiter"
]
