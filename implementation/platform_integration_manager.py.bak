"""Platform Integration Manager

Comprehensive system for managing integrations with multiple social media
and content platforms including YouTube, SoundCloud, Instagram, TikTok, etc.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import urllib.parse

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """
Supported platform types"""

    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"
    CONTENT_SHARING = "content_sharing"
    PROFESSIONAL = "professional"
    BLOG = "blog"
    MARKETPLACE = "marketplace"


class APIMethod(Enum):
    """API method types"""

    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"


@dataclass
class PlatformConfig:
    """Platform configuration"""
    platform_id: str
    name: str
    platform_type: PlatformType
    api_method: APIMethod
    base_url: str
    api_version: str
    rate_limit: int
    requires_auth: bool
    auth_type: str  # oauth2, api_key, bearer_token
    endpoints: Dict[str, str]
    default_params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class APICredentials:
    """
API credentials for a platform"""
    platform_id: str
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class PlatformResponse:
    """
Standardized platform response"""
    platform_id: str
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PlatformIntegrationManager:
    """
    Central manager for all platform integrations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Platform configurations
        self.platforms: Dict[str, PlatformConfig] = {}
        self.credentials: Dict[str, APICredentials] = {}
        
        # HTTP session management
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        
        # Rate limiting and caching
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize built-in platform configurations
        self._initialize_platforms()
    
    def _initialize_platforms(self):
        """
Initialize built-in platform configurations"""
        
        # YouTube configuration
        self.platforms["youtube"] = PlatformConfig(
            platform_id="youtube",
            name="YouTube",
            platform_type=PlatformType.VIDEO_STREAMING,
            api_method=APIMethod.REST,
            base_url="https://www.googleapis.com/youtube/v3",
            api_version="v3",
            rate_limit=10000,  # requests per day
            requires_auth=True,
            auth_type="api_key",
            endpoints={
                "search": "/search",
                "videos": "/videos",
                "channels": "/channels",
                "playlists": "/playlists",
                "comments": "/commentThreads"
            },
            default_params={"part": "snippet", "maxResults": 50}
        )
        
        # SoundCloud configuration
        self.platforms["soundcloud"] = PlatformConfig(
            platform_id="soundcloud",
            name="SoundCloud",
            platform_type=PlatformType.MUSIC_STREAMING,
            api_method=APIMethod.REST,
            base_url="https://api.soundcloud.com",
            api_version="v1",
            rate_limit=15000,  # requests per hour
            requires_auth=True,
            auth_type="client_id",
            endpoints={
                "tracks": "/tracks",
                "users": "/users",
                "playlists": "/playlists",
                "resolve": "/resolve"
            },
            default_params={"limit": 50}
        )
        
        # Instagram configuration
        self.platforms["instagram"] = PlatformConfig(
            platform_id="instagram",
            name="Instagram",
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_method=APIMethod.REST,
            base_url="https://graph.instagram.com",
            api_version="v18.0",
            rate_limit=200,  # requests per hour
            requires_auth=True,
            auth_type="oauth2",
            endpoints={
                "media": "/me/media",
                "hashtags": "/ig_hashtag_search",
                "insights": "/insights"
            }
        )
        
        # TikTok configuration
        self.platforms["tiktok"] = PlatformConfig(
            platform_id="tiktok",
            name="TikTok",
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_method=APIMethod.REST,
            base_url="https://open-api.tiktok.com",
            api_version="v1.3",
            rate_limit=1000,  # requests per day
            requires_auth=True,
            auth_type="oauth2",
            endpoints={
                "user_info": "/user/info/",
                "video_list": "/video/list/",
                "video_search": "/video/search/"
            }
        )
        
        # Twitter/X configuration
        self.platforms["twitter"] = PlatformConfig(
            platform_id="twitter",
            name="Twitter/X",
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_method=APIMethod.REST,
            base_url="https://api.twitter.com/2",
            api_version="v2",
            rate_limit=300,  # requests per 15 minutes
            requires_auth=True,
            auth_type="bearer_token",
            endpoints={
                "tweets": "/tweets",
                "users": "/users",
                "search": "/tweets/search/recent"
            }
        )
        
        # Facebook configuration
        self.platforms["facebook"] = PlatformConfig(
            platform_id="facebook",
            name="Facebook",
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_method=APIMethod.GRAPHQL,
            base_url="https://graph.facebook.com",
            api_version="v18.0",
            rate_limit=200,  # requests per hour
            requires_auth=True,
            auth_type="oauth2",
            endpoints={
                "posts": "/me/posts",
                "feed": "/me/feed",
                "photos": "/me/photos"
            }
        )
        
        # LinkedIn configuration
        self.platforms["linkedin"] = PlatformConfig(
            platform_id="linkedin",
            name="LinkedIn",
            platform_type=PlatformType.PROFESSIONAL,
            api_method=APIMethod.REST,
            base_url="https://api.linkedin.com/v2",
            api_version="v2",
            rate_limit=500,  # requests per day
            requires_auth=True,
            auth_type="oauth2",
            endpoints={
                "profile": "/people/~",
                "shares": "/shares",
                "companies": "/companies"
            }
        )
    
    def add_platform_credentials(self, platform_id: str, credentials: APICredentials):
        """Add credentials for a platform"""
        self.credentials[platform_id] = credentials
        self.logger.info(f"Credentials added for platform: {platform_id}")
    
    async def initialize_session(self, platform_id: str) -> bool:
        """Initialize HTTP session for a platform"""
        try:
            platform_config = self.platforms.get(platform_id)
            if not platform_config:
                self.logger.error(f"Platform not configured: {platform_id}")
                return False
            
            # Create session with platform-specific configuration
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                "User-Agent": "Ainflue-Platform-Integration/1.0",
                **platform_config.headers
            }
            
            self.sessions[platform_id] = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
            
            self.logger.info(f"Session initialized for platform: {platform_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize session for {platform_id}: {e}")
            return False
    
    async def close_session(self, platform_id: str):
        """Close HTTP session for a platform"""
        if platform_id in self.sessions:
            await self.sessions[platform_id].close()
            del self.sessions[platform_id]
            self.logger.info(f"Session closed for platform: {platform_id}")
    
    async def close_all_sessions(self):
        """Close all HTTP sessions"""
        for platform_id in list(self.sessions.keys()):
            await self.close_session(platform_id)
    
    async def make_api_request(
        self,
        platform_id: str,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> PlatformResponse:
        """
        Make API request to a platform
        
        Args:
            platform_id: Platform identifier
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            Standardized platform response
        """
        start_time = datetime.utcnow()
        
        try:
            # Get platform configuration
            platform_config = self.platforms.get(platform_id)
            if not platform_config:
                return PlatformResponse(
                    platform_id=platform_id,
                    success=False,
                    data={},
                    error_message=f"Platform not configured: {platform_id}"
                )
            
            # Check rate limits
            if not await self._check_rate_limit(platform_id):
                return PlatformResponse(
                    platform_id=platform_id,
                    success=False,
                    data={},
                    error_message="Rate limit exceeded"
                )
            
            # Initialize session if needed
            if platform_id not in self.sessions:
                await self.initialize_session(platform_id)
            
            session = self.sessions[platform_id]
            
            # Prepare request
            url = f"{platform_config.base_url}{endpoint}"
            request_params = {**platform_config.default_params, **(params or {})}
            request_headers = {**headers} if headers else {}
            
            # Add authentication
            await self._add_authentication(platform_id, request_params, request_headers)
            
            # Make request
            async with session.request(
                method=method,
                url=url,
                params=request_params,
                json=data,
                headers=request_headers
            ) as response:
                
                response_data = {}
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                # Calculate response time
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Update rate limit tracking
                self._update_rate_limit_tracking(platform_id, response.headers)
                
                # Create response object
                return PlatformResponse(
                    platform_id=platform_id,
                    success=response.status < 400,
                    data=response_data,
                    error_message=None if response.status < 400 else f"HTTP {response.status}",
                    response_time=response_time
                )
        
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return PlatformResponse(
                platform_id=platform_id,
                success=False,
                data={},
                error_message=str(e),
                response_time=response_time
            )
    
    async def _add_authentication(
        self,
        platform_id: str,
        params: Dict[str, Any],
        headers: Dict[str, str]
    ):
        """Add authentication to request"""
        platform_config = self.platforms[platform_id]
        credentials = self.credentials.get(platform_id)
        
        if not credentials:
            return
        
        if platform_config.auth_type == "api_key":
            if platform_id == "youtube":
                params["key"] = credentials.api_key
            elif platform_id == "soundcloud":
                params["client_id"] = credentials.client_id
        
        elif platform_config.auth_type == "bearer_token":
            headers["Authorization"] = f"Bearer {credentials.access_token}"
        
        elif platform_config.auth_type == "oauth2":
            headers["Authorization"] = f"Bearer {credentials.access_token}"
            
            # Check if token needs refresh
            if credentials.expires_at and datetime.utcnow() >= credentials.expires_at:
                await self._refresh_oauth_token(platform_id)
    
    async def _refresh_oauth_token(self, platform_id: str):
        """Refresh OAuth token for a platform"""
        credentials = self.credentials.get(platform_id)
        if not credentials or not credentials.refresh_token:
            return
        
        # This would implement token refresh logic for each platform
        # For now, log the need for refresh
        self.logger.warning(f"OAuth token refresh needed for {platform_id}")
    
    async def _check_rate_limit(self, platform_id: str) -> bool:
        """Check if request is within rate limits"""
        rate_limit_info = self.rate_limits.get(platform_id, {})
        
        if not rate_limit_info:
            return True
        
        current_time = datetime.utcnow()
        
        # Check if rate limit window has reset
        reset_time = rate_limit_info.get("reset_time")
        if reset_time and current_time >= reset_time:
            self.rate_limits[platform_id] = {}
            return True
        
        # Check remaining requests
        remaining = rate_limit_info.get("remaining", float('inf'))
        return remaining > 0
    
    def _update_rate_limit_tracking(self, platform_id: str, response_headers: Dict[str, str]):
        """Update rate limit tracking from response headers"""
        # Common rate limit header patterns
        remaining_headers = [
            "x-ratelimit-remaining",
            "x-rate-limit-remaining",
            "ratelimit-remaining"
        ]
        
        reset_headers = [
            "x-ratelimit-reset",
            "x-rate-limit-reset",
            "ratelimit-reset"
        ]
        
        remaining = None
        reset_time = None
        
        # Look for remaining requests
        for header in remaining_headers:
            if header in response_headers:
                try:
                    remaining = int(response_headers[header])
                    break
                except ValueError:
                    continue
        
        # Look for reset time
        for header in reset_headers:
            if header in response_headers:
                try:
                    reset_timestamp = int(response_headers[header])
                    reset_time = datetime.fromtimestamp(reset_timestamp)
                    break
                except (ValueError, OSError):
                    continue
        
        # Update tracking
        if remaining is not None or reset_time is not None:
            self.rate_limits[platform_id] = {
                "remaining": remaining,
                "reset_time": reset_time,
                "updated_at": datetime.utcnow()
            }
    
    # Platform-specific methods
    
    async def search_youtube(
        self,
        query: str,
        content_type: str = "video",
        max_results: int = 50
    ) -> PlatformResponse:
        """Search YouTube for content"""
        params = {
            "q": query,
            "type": content_type,
            "maxResults": min(max_results, 50),
            "order": "relevance"
        }
        
        return await self.make_api_request("youtube", "/search", params=params)
    
    async def get_youtube_video(self, video_id: str) -> PlatformResponse:
        """Get YouTube video details"""
        params = {
            "id": video_id,
            "part": "snippet,statistics,contentDetails"
        }
        
        return await self.make_api_request("youtube", "/videos", params=params)
    
    async def search_soundcloud(
        self,
        query: str,
        limit: int = 50
    ) -> PlatformResponse:
        """Search SoundCloud for tracks"""
        params = {
            "q": query,
            "limit": min(limit, 200)
        }
        
        return await self.make_api_request("soundcloud", "/tracks", params=params)
    
    async def resolve_soundcloud_url(self, url: str) -> PlatformResponse:
        """Resolve SoundCloud URL to get track info"""
        params = {"url": url}
        
        return await self.make_api_request("soundcloud", "/resolve", params=params)
    
    async def search_instagram_hashtags(self, hashtag: str) -> PlatformResponse:
        """Search Instagram hashtags"""
        params = {"q": hashtag}
        
        return await self.make_api_request("instagram", "/ig_hashtag_search", params=params)
    
    async def search_twitter(
        self,
        query: str,
        max_results: int = 100
    ) -> PlatformResponse:
        """Search Twitter for tweets"""
        params = {
            "query": query,
            "max_results": min(max_results, 100)
        }
        
        return await self.make_api_request("twitter", "/tweets/search/recent", params=params)
    
    # Utility methods
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.platforms.keys())
    
    def get_platform_info(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
Get platform configuration info"""
        platform_config = self.platforms.get(platform_id)
        if platform_config:
            return asdict(platform_config)
        return None
    
    def get_rate_limit_status(self, platform_id: str) -> Dict[str, Any]:
        """
Get current rate limit status for a platform"""
        return self.rate_limits.get(platform_id, {})
    
    async def test_platform_connection(self, platform_id: str) -> bool:
        """
Test connection to a platform"""
        try:
            # Make a simple test request based on platform
            if platform_id == "youtube":
                response = await self.make_api_request("youtube", "/search", params={"q": "test", "maxResults": 1})
            elif platform_id == "soundcloud":
                response = await self.make_api_request("soundcloud", "/tracks", params={"q": "test", "limit": 1})
            else:
                # Generic test - try to access base endpoint
                response = await self.make_api_request(platform_id, "/")
            
            return response.success
            
        except Exception as e:
            self.logger.error(f"Connection test failed for {platform_id}: {e}")
            return False
    
    async def bulk_search(
        self,
        query: str,
        platforms: List[str],
        max_results_per_platform: int = 25
    ) -> Dict[str, PlatformResponse]:
        """Search across multiple platforms simultaneously"""
        tasks = []
        
        for platform_id in platforms:
            if platform_id == "youtube":
                task = self.search_youtube(query, max_results=max_results_per_platform)
            elif platform_id == "soundcloud":
                task = self.search_soundcloud(query, limit=max_results_per_platform)
            elif platform_id == "twitter":
                task = self.search_twitter(query, max_results=max_results_per_platform)
            else:
                # Generic search
                task = self.make_api_request(
                    platform_id, 
                    "/search", 
                    params={"q": query, "limit": max_results_per_platform}
                )
            
            tasks.append((platform_id, task))
        
        # Execute all searches concurrently
        results = {}
        for platform_id, task in tasks:
            try:
                results[platform_id] = await task
            except Exception as e:
                results[platform_id] = PlatformResponse(
                    platform_id=platform_id,
                    success=False,
                    data={},
                    error_message=str(e)
                )
        
        return results