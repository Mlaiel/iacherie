"""
Professional API integration system for content platform monitoring.

This module implements comprehensive API integrations for major content platforms
including YouTube, Instagram, TikTok, Twitter, and Spotify with advanced
rate limiting, authentication handling, and data normalization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- API Integration Specialist: Multi-Platform Connectivity Expert
- OAuth & Authentication Engineer: Secure API Access Management
- Data Normalization Expert: Cross-Platform Data Standardization
- Rate Limiting Engineer: API Quota Management & Optimization
- Social Media API Specialist: Platform-Specific Implementation

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple, AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import re
import time
import hashlib
import uuid
from urllib.parse import urlencode, parse_qs
import base64
from concurrent.futures import ThreadPoolExecutor

# HTTP and API clients
import aiohttp
import requests
from aiohttp import ClientSession, ClientTimeout
import httpx

# Platform-specific API clients
import tweepy
from instagrapi import Client as InstagramClient
from pytube import YouTube
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
import tikapi
from linkedin_api import Linkedin

# Authentication and security
import jwt
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
import secrets

# Data processing
import pandas as pd
import numpy as np
from dateutil import parser as date_parser

from . import WebCrawler, CrawlResult, CrawlTarget, ContentType, PlatformType
from ..core.exceptions import CrawlerException, ValidationException, APIException
from ..core.models import BaseModel
from ..security.encryption import EncryptionManager
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager


class APIProvider(Enum):
    """API service providers."""
    YOUTUBE_DATA_API = "youtube_data_api"
    INSTAGRAM_BASIC_DISPLAY = "instagram_basic_display"
    INSTAGRAM_BUSINESS = "instagram_business"
    TWITTER_API_V2 = "twitter_api_v2"
    TIKTOK_BUSINESS = "tiktok_business"
    FACEBOOK_GRAPH = "facebook_graph"
    SPOTIFY_WEB_API = "spotify_web_api"
    LINKEDIN_API = "linkedin_api"
    PINTEREST_API = "pinterest_api"
    TWITCH_HELIX = "twitch_helix"
    DISCORD_API = "discord_api"
    REDDIT_API = "reddit_api"


class AuthenticationType(Enum):
    """API authentication types."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"
    DEVICE_CODE = "device_code"
    JWT_TOKEN = "jwt_token"


class DataFormat(Enum):
    """API response data formats."""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    PROTOBUF = "protobuf"
    YAML = "yaml"


@dataclass
class APICredentials:
    """API authentication credentials."""
    provider: APIProvider
    auth_type: AuthenticationType
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    redirect_uri: Optional[str] = None
    expires_at: Optional[datetime] = None
    rate_limit: int = 1000
    rate_window: int = 3600  # seconds
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIRequest:
    """API request configuration."""
    request_id: str
    provider: APIProvider
    endpoint: str
    method: str = "GET"
    parameters: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    cache_duration: int = 300  # seconds
    priority: int = 5  # 1-10 scale
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIResponse:
    """API response wrapper."""
    request_id: str
    provider: APIProvider
    status_code: int
    headers: Dict[str, str]
    data: Any
    raw_response: str = ""
    processing_time: float = 0.0
    from_cache: bool = False
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    error_message: Optional[str] = None
    pagination_token: Optional[str] = None
    total_items: Optional[int] = None
    received_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NormalizedContent:
    """Normalized content across platforms."""
    content_id: str
    platform: str
    content_type: str  # post, video, image, story, etc.
    title: str = ""
    description: str = ""
    text_content: str = ""
    media_urls: List[str] = field(default_factory=list)
    thumbnail_url: str = ""
    author_id: str = ""
    author_name: str = ""
    author_handle: str = ""
    publish_date: Optional[datetime] = None
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[str] = None
    language: str = ""
    is_verified: bool = False
    is_sponsored: bool = False
    content_rating: str = ""
    duration: Optional[int] = None  # seconds for video/audio
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.utcnow)


class APIIntegrationEngine:
    """
    Advanced API integration engine for content platform monitoring.
    
    Features:
    - Multi-platform API management
    - OAuth 2.0 authentication flows
    - Intelligent rate limiting
    - Response caching and optimization
    - Data normalization across platforms
    - Error handling and retry mechanisms
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("api.integration")
        
        # Core components
        self.rate_limiter = RateLimiter(config.get("rate_limits", {}))
        self.cache_manager = CacheManager(config.get("cache_config", {}))
        self.encryption_manager = EncryptionManager()
        
        # API credentials storage
        self.credentials: Dict[APIProvider, APICredentials] = {}
        
        # Platform clients
        self.platform_clients: Dict[APIProvider, Any] = {}
        
        # Request queue and processing
        self.request_queue = asyncio.Queue()
        self.active_requests: Dict[str, APIRequest] = {}
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cached_responses": 0,
            "rate_limited_requests": 0,
            "average_response_time": 0.0
        }
        
        # Initialize platform clients
        self._setup_platform_clients()
    
    def _setup_platform_clients(self):
        """Initialize platform-specific API clients."""
        try:
            # YouTube Data API
            if self.config.get("youtube_credentials"):
                self.credentials[APIProvider.YOUTUBE_DATA_API] = APICredentials(
                    provider=APIProvider.YOUTUBE_DATA_API,
                    auth_type=AuthenticationType.API_KEY,
                    **self.config["youtube_credentials"]
                )
            
            # Instagram API
            if self.config.get("instagram_credentials"):
                self.credentials[APIProvider.INSTAGRAM_BUSINESS] = APICredentials(
                    provider=APIProvider.INSTAGRAM_BUSINESS,
                    auth_type=AuthenticationType.OAUTH2,
                    **self.config["instagram_credentials"]
                )
            
            # Twitter API v2
            if self.config.get("twitter_credentials"):
                self.credentials[APIProvider.TWITTER_API_V2] = APICredentials(
                    provider=APIProvider.TWITTER_API_V2,
                    auth_type=AuthenticationType.BEARER_TOKEN,
                    **self.config["twitter_credentials"]
                )
            
            # Spotify Web API
            if self.config.get("spotify_credentials"):
                self.credentials[APIProvider.SPOTIFY_WEB_API] = APICredentials(
                    provider=APIProvider.SPOTIFY_WEB_API,
                    auth_type=AuthenticationType.CLIENT_CREDENTIALS,
                    **self.config["spotify_credentials"]
                )
            
            self.logger.info("Platform clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup platform clients: {e}")
    
    async def authenticate_platform(
        self,
        provider: APIProvider,
        credentials: APICredentials
    ) -> bool:
        """Authenticate with a platform API."""
        try:
            self.logger.info(f"Authenticating with {provider.value}")
            
            if provider == APIProvider.YOUTUBE_DATA_API:
                return await self._auth_youtube(credentials)
            elif provider == APIProvider.INSTAGRAM_BUSINESS:
                return await self._auth_instagram(credentials)
            elif provider == APIProvider.TWITTER_API_V2:
                return await self._auth_twitter(credentials)
            elif provider == APIProvider.SPOTIFY_WEB_API:
                return await self._auth_spotify(credentials)
            elif provider == APIProvider.TIKTOK_BUSINESS:
                return await self._auth_tiktok(credentials)
            else:
                self.logger.warning(f"Authentication not implemented for {provider.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication failed for {provider.value}: {e}")
            return False
    
    async def _auth_youtube(self, credentials: APICredentials) -> bool:
        """Authenticate with YouTube Data API."""
        try:
            # Test API key with a simple request
            test_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": "test",
                "maxResults": 1,
                "key": credentials.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, params=params) as response:
                    if response.status == 200:
                        self.credentials[APIProvider.YOUTUBE_DATA_API] = credentials
                        self.logger.info("YouTube API authentication successful")
                        return True
                    else:
                        self.logger.error(f"YouTube API test failed: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"YouTube authentication error: {e}")
            return False
    
    async def _auth_instagram(self, credentials: APICredentials) -> bool:
        """Authenticate with Instagram Business API."""
        try:
            if credentials.auth_type == AuthenticationType.OAUTH2:
                # Use existing access token or initiate OAuth flow
                if credentials.access_token:
                    # Test token validity
                    test_url = "https://graph.instagram.com/me"
                    params = {"access_token": credentials.access_token}
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(test_url, params=params) as response:
                            if response.status == 200:
                                self.credentials[APIProvider.INSTAGRAM_BUSINESS] = credentials
                                return True
                            else:
                                return False
                else:
                    # Need to implement OAuth flow
                    self.logger.warning("Instagram OAuth flow not implemented")
                    return False
            else:
                # Alternative authentication methods
                client = InstagramClient()
                try:
                    if credentials.username and credentials.password:
                        client.login(credentials.username, credentials.password)
                        self.platform_clients[APIProvider.INSTAGRAM_BUSINESS] = client
                        return True
                except Exception as e:
                    self.logger.error(f"Instagram login failed: {e}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Instagram authentication error: {e}")
            return False
    
    async def _auth_twitter(self, credentials: APICredentials) -> bool:
        """Authenticate with Twitter API v2."""
        try:
            if credentials.bearer_token:
                # Test bearer token
                test_url = "https://api.twitter.com/2/users/me"
                headers = {"Authorization": f"Bearer {credentials.bearer_token}"}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers) as response:
                        if response.status == 200:
                            self.credentials[APIProvider.TWITTER_API_V2] = credentials
                            
                            # Setup tweepy client
                            client = tweepy.Client(bearer_token=credentials.bearer_token)
                            self.platform_clients[APIProvider.TWITTER_API_V2] = client
                            
                            return True
                        else:
                            return False
            else:
                self.logger.error("Twitter bearer token required")
                return False
                
        except Exception as e:
            self.logger.error(f"Twitter authentication error: {e}")
            return False
    
    async def _auth_spotify(self, credentials: APICredentials) -> bool:
        """Authenticate with Spotify Web API."""
        try:
            if credentials.client_id and credentials.client_secret:
                # Use client credentials flow
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=credentials.client_id,
                    client_secret=credentials.client_secret
                )
                
                client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
                
                # Test authentication
                try:
                    # Simple search query to test credentials
                    results = client.search(q="test", type="track", limit=1)
                    if results:
                        self.credentials[APIProvider.SPOTIFY_WEB_API] = credentials
                        self.platform_clients[APIProvider.SPOTIFY_WEB_API] = client
                        return True
                except Exception as e:
                    self.logger.error(f"Spotify test query failed: {e}")
                    return False
            else:
                self.logger.error("Spotify client credentials required")
                return False
                
        except Exception as e:
            self.logger.error(f"Spotify authentication error: {e}")
            return False
    
    async def _auth_tiktok(self, credentials: APICredentials) -> bool:
        """Authenticate with TikTok Business API."""
        try:
            # TikTok Business API authentication
            if credentials.access_token:
                # Test access token
                test_url = "https://business-api.tiktok.com/open_api/v1.3/user/info/"
                headers = {"Access-Token": credentials.access_token}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers) as response:
                        if response.status == 200:
                            self.credentials[APIProvider.TIKTOK_BUSINESS] = credentials
                            return True
                        else:
                            return False
            else:
                self.logger.error("TikTok access token required")
                return False
                
        except Exception as e:
            self.logger.error(f"TikTok authentication error: {e}")
            return False
    
    async def make_api_request(
        self,
        request: APIRequest
    ) -> APIResponse:
        """Make an API request with rate limiting and caching."""
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = await self.cache_manager.get(cache_key)
            if cached_response:
                self.metrics["cached_responses"] += 1
                return APIResponse(
                    request_id=request.request_id,
                    provider=request.provider,
                    status_code=200,
                    headers={},
                    data=cached_response,
                    processing_time=time.time() - start_time,
                    from_cache=True
                )
            
            # Rate limiting
            provider_key = f"api_{request.provider.value}"
            await self.rate_limiter.acquire(provider_key)
            
            # Get credentials
            credentials = self.credentials.get(request.provider)
            if not credentials:
                raise APIException(f"No credentials found for {request.provider.value}")
            
            # Prepare request
            url = self._build_request_url(request)
            headers = self._build_request_headers(request, credentials)
            
            # Make request
            response = await self._execute_request(
                request.method,
                url,
                headers=headers,
                params=request.parameters if request.method == "GET" else None,
                json=request.body if request.method in ["POST", "PUT", "PATCH"] else None,
                timeout=request.timeout
            )
            
            # Process response
            api_response = await self._process_response(request, response, start_time)
            
            # Cache successful response
            if api_response.status_code == 200 and request.cache_duration > 0:
                await self.cache_manager.set(
                    cache_key,
                    api_response.data,
                    ttl=request.cache_duration
                )
            
            # Update metrics
            self.metrics["total_requests"] += 1
            if api_response.status_code == 200:
                self.metrics["successful_requests"] += 1
            else:
                self.metrics["failed_requests"] += 1
            
            self._update_average_response_time(api_response.processing_time)
            
            return api_response
            
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            self.metrics["failed_requests"] += 1
            
            return APIResponse(
                request_id=request.request_id,
                provider=request.provider,
                status_code=500,
                headers={},
                data=None,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _generate_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for API request."""
        key_data = f"{request.provider.value}_{request.endpoint}_{hash(str(request.parameters))}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def _build_request_url(self, request: APIRequest) -> str:
        """Build complete request URL."""
        if request.provider == APIProvider.YOUTUBE_DATA_API:
            base_url = "https://www.googleapis.com/youtube/v3"
        elif request.provider == APIProvider.INSTAGRAM_BUSINESS:
            base_url = "https://graph.instagram.com"
        elif request.provider == APIProvider.TWITTER_API_V2:
            base_url = "https://api.twitter.com/2"
        elif request.provider == APIProvider.SPOTIFY_WEB_API:
            base_url = "https://api.spotify.com/v1"
        elif request.provider == APIProvider.TIKTOK_BUSINESS:
            base_url = "https://business-api.tiktok.com/open_api/v1.3"
        else:
            raise APIException(f"Unknown provider: {request.provider.value}")
        
        return f"{base_url}/{request.endpoint.lstrip('/')}"
    
    def _build_request_headers(
        self,
        request: APIRequest,
        credentials: APICredentials
    ) -> Dict[str, str]:
        """Build request headers with authentication."""
        headers = {
            "User-Agent": "IA-Influencer-Bot/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Add custom headers
        headers.update(request.headers)
        
        # Add authentication headers
        if credentials.auth_type == AuthenticationType.API_KEY:
            if request.provider == APIProvider.YOUTUBE_DATA_API:
                # API key added to parameters, not headers
                pass
        elif credentials.auth_type == AuthenticationType.BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {credentials.bearer_token}"
        elif credentials.auth_type == AuthenticationType.OAUTH2:
            if credentials.access_token:
                headers["Authorization"] = f"Bearer {credentials.access_token}"
        
        return headers
    
    async def _execute_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """Execute HTTP request with retry logic."""
        async with aiohttp.ClientSession() as session:
            for attempt in range(kwargs.get("retry_attempts", 3)):
                try:
                    async with session.request(method, url, **kwargs) as response:
                        return response
                except Exception as e:
                    if attempt == kwargs.get("retry_attempts", 3) - 1:
                        raise e
                    await asyncio.sleep(kwargs.get("retry_delay", 1.0) * (attempt + 1))
    
    async def _process_response(
        self,
        request: APIRequest,
        response: aiohttp.ClientResponse,
        start_time: float
    ) -> APIResponse:
        """Process API response."""
        try:
            # Read response data
            response_text = await response.text()
            
            # Parse JSON if applicable
            data = None
            if response.content_type == "application/json":
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError:
                    data = response_text
            else:
                data = response_text
            
            # Extract rate limit information
            rate_limit_remaining = None
            rate_limit_reset = None
            
            if "X-RateLimit-Remaining" in response.headers:
                rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            if "X-RateLimit-Reset" in response.headers:
                reset_timestamp = int(response.headers["X-RateLimit-Reset"])
                rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            
            return APIResponse(
                request_id=request.request_id,
                provider=request.provider,
                status_code=response.status,
                headers=dict(response.headers),
                data=data,
                raw_response=response_text,
                processing_time=time.time() - start_time,
                rate_limit_remaining=rate_limit_remaining,
                rate_limit_reset=rate_limit_reset
            )
            
        except Exception as e:
            self.logger.error(f"Response processing failed: {e}")
            raise APIException(f"Response processing failed: {e}")
    
    def _update_average_response_time(self, response_time: float):
        """Update average response time metric."""
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["total_requests"]
        
        if total_requests == 1:
            self.metrics["average_response_time"] = response_time
        else:
            # Running average calculation
            self.metrics["average_response_time"] = (
                (current_avg * (total_requests - 1)) + response_time
            ) / total_requests
    
    async def search_youtube_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = "relevance"
    ) -> List[NormalizedContent]:
        """Search YouTube videos and return normalized content."""
        try:
            request = APIRequest(
                request_id=str(uuid.uuid4()),
                provider=APIProvider.YOUTUBE_DATA_API,
                endpoint="search",
                parameters={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": min(max_results, 50),
                    "order": order,
                    "key": self.credentials[APIProvider.YOUTUBE_DATA_API].api_key
                }
            )
            
            response = await self.make_api_request(request)
            
            if response.status_code != 200:
                raise APIException(f"YouTube search failed: {response.error_message}")
            
            normalized_content = []
            for item in response.data.get("items", []):
                content = self._normalize_youtube_video(item)
                normalized_content.append(content)
            
            return normalized_content
            
        except Exception as e:
            self.logger.error(f"YouTube search failed: {e}")
            raise APIException(f"YouTube search failed: {e}")
    
    def _normalize_youtube_video(self, video_data: Dict[str, Any]) -> NormalizedContent:
        """Normalize YouTube video data."""
        snippet = video_data.get("snippet", {})
        
        return NormalizedContent(
            content_id=video_data.get("id", {}).get("videoId", ""),
            platform="youtube",
            content_type="video",
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            author_name=snippet.get("channelTitle", ""),
            author_id=snippet.get("channelId", ""),
            publish_date=date_parser.parse(snippet.get("publishedAt")) if snippet.get("publishedAt") else None,
            raw_data=video_data
        )
    
    async def get_instagram_posts(
        self,
        user_id: str,
        limit: int = 25
    ) -> List[NormalizedContent]:
        """Get Instagram posts for a user."""
        try:
            if APIProvider.INSTAGRAM_BUSINESS not in self.platform_clients:
                raise APIException("Instagram client not authenticated")
            
            client = self.platform_clients[APIProvider.INSTAGRAM_BUSINESS]
            posts = client.user_medias(user_id, amount=limit)
            
            normalized_content = []
            for post in posts:
                content = self._normalize_instagram_post(post)
                normalized_content.append(content)
            
            return normalized_content
            
        except Exception as e:
            self.logger.error(f"Instagram posts fetch failed: {e}")
            raise APIException(f"Instagram posts fetch failed: {e}")
    
    def _normalize_instagram_post(self, post_data) -> NormalizedContent:
        """Normalize Instagram post data."""
        return NormalizedContent(
            content_id=post_data.pk,
            platform="instagram",
            content_type="post",
            text_content=post_data.caption_text or "",
            media_urls=[post_data.thumbnail_url] if post_data.thumbnail_url else [],
            thumbnail_url=post_data.thumbnail_url or "",
            author_id=str(post_data.user.pk),
            author_name=post_data.user.full_name or "",
            author_handle=post_data.user.username or "",
            publish_date=post_data.taken_at,
            like_count=post_data.like_count or 0,
            comment_count=post_data.comment_count or 0,
            view_count=post_data.view_count or 0,
            raw_data=post_data.__dict__
        )
    
    async def search_twitter_tweets(
        self,
        query: str,
        max_results: int = 100
    ) -> List[NormalizedContent]:
        """Search Twitter tweets and return normalized content."""
        try:
            if APIProvider.TWITTER_API_V2 not in self.platform_clients:
                raise APIException("Twitter client not authenticated")
            
            client = self.platform_clients[APIProvider.TWITTER_API_V2]
            tweets = client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=[
                    "created_at", "public_metrics", "lang", "context_annotations",
                    "entities", "geo", "author_id"
                ],
                user_fields=["name", "username", "verified"],
                expansions=["author_id"]
            )
            
            normalized_content = []
            if tweets.data:
                # Create user lookup
                users_lookup = {user.id: user for user in tweets.includes.get("users", [])}
                
                for tweet in tweets.data:
                    author = users_lookup.get(tweet.author_id)
                    content = self._normalize_twitter_tweet(tweet, author)
                    normalized_content.append(content)
            
            return normalized_content
            
        except Exception as e:
            self.logger.error(f"Twitter search failed: {e}")
            raise APIException(f"Twitter search failed: {e}")
    
    def _normalize_twitter_tweet(self, tweet_data, author_data) -> NormalizedContent:
        """Normalize Twitter tweet data."""
        # Extract hashtags and mentions
        hashtags = []
        mentions = []
        
        if hasattr(tweet_data, 'entities') and tweet_data.entities:
            if 'hashtags' in tweet_data.entities:
                hashtags = [tag['tag'] for tag in tweet_data.entities['hashtags']]
            if 'mentions' in tweet_data.entities:
                mentions = [mention['username'] for mention in tweet_data.entities['mentions']]
        
        # Extract engagement metrics
        metrics = tweet_data.public_metrics if hasattr(tweet_data, 'public_metrics') else {}
        
        return NormalizedContent(
            content_id=tweet_data.id,
            platform="twitter",
            content_type="tweet",
            text_content=tweet_data.text,
            author_id=tweet_data.author_id,
            author_name=author_data.name if author_data else "",
            author_handle=author_data.username if author_data else "",
            publish_date=tweet_data.created_at if hasattr(tweet_data, 'created_at') else None,
            like_count=metrics.get("like_count", 0),
            comment_count=metrics.get("reply_count", 0),
            share_count=metrics.get("retweet_count", 0),
            hashtags=[f"#{tag}" for tag in hashtags],
            mentions=[f"@{mention}" for mention in mentions],
            language=tweet_data.lang if hasattr(tweet_data, 'lang') else "",
            is_verified=author_data.verified if author_data else False,
            raw_data=tweet_data.__dict__
        )
    
    async def search_spotify_tracks(
        self,
        query: str,
        limit: int = 50,
        market: str = "US"
    ) -> List[NormalizedContent]:
        """Search Spotify tracks and return normalized content."""
        try:
            if APIProvider.SPOTIFY_WEB_API not in self.platform_clients:
                raise APIException("Spotify client not authenticated")
            
            client = self.platform_clients[APIProvider.SPOTIFY_WEB_API]
            results = client.search(q=query, type="track", limit=limit, market=market)
            
            normalized_content = []
            for track in results["tracks"]["items"]:
                content = self._normalize_spotify_track(track)
                normalized_content.append(content)
            
            return normalized_content
            
        except Exception as e:
            self.logger.error(f"Spotify search failed: {e}")
            raise APIException(f"Spotify search failed: {e}")
    
    def _normalize_spotify_track(self, track_data: Dict[str, Any]) -> NormalizedContent:
        """Normalize Spotify track data."""
        artists = track_data.get("artists", [])
        artist_names = [artist["name"] for artist in artists]
        
        return NormalizedContent(
            content_id=track_data.get("id", ""),
            platform="spotify",
            content_type="track",
            title=track_data.get("name", ""),
            author_name=", ".join(artist_names),
            author_id=artists[0]["id"] if artists else "",
            thumbnail_url=track_data.get("album", {}).get("images", [{}])[0].get("url", ""),
            duration=track_data.get("duration_ms", 0) // 1000,  # Convert to seconds
            metadata={
                "album": track_data.get("album", {}).get("name", ""),
                "popularity": track_data.get("popularity", 0),
                "explicit": track_data.get("explicit", False),
                "preview_url": track_data.get("preview_url")
            },
            raw_data=track_data
        )
    
    async def batch_api_requests(
        self,
        requests: List[APIRequest],
        max_concurrent: int = 10
    ) -> List[APIResponse]:
        """Execute multiple API requests concurrently."""
        try:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def request_with_semaphore(request):
                async with semaphore:
                    return await self.make_api_request(request)
            
            tasks = [request_with_semaphore(req) for req in requests]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    self.logger.error(f"Batch request {i} failed: {response}")
                else:
                    valid_responses.append(response)
            
            return valid_responses
            
        except Exception as e:
            self.logger.error(f"Batch API requests failed: {e}")
            raise APIException(f"Batch requests failed: {e}")
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """Get API integration performance metrics."""
        success_rate = 0.0
        if self.metrics["total_requests"] > 0:
            success_rate = (
                self.metrics["successful_requests"] / self.metrics["total_requests"]
            ) * 100
        
        return {
            **self.metrics,
            "success_rate": success_rate,
            "authenticated_providers": list(self.credentials.keys()),
            "active_clients": list(self.platform_clients.keys())
        }
    
    async def refresh_access_tokens(self):
        """Refresh expired access tokens for OAuth providers."""
        try:
            for provider, credentials in self.credentials.items():
                if (credentials.expires_at and 
                    credentials.expires_at < datetime.utcnow() + timedelta(minutes=5)):
                    
                    # Token expires soon, refresh it
                    await self._refresh_token(provider, credentials)
                    
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
    
    async def _refresh_token(self, provider: APIProvider, credentials: APICredentials):
        """Refresh access token for a specific provider."""
        try:
            if credentials.refresh_token and credentials.client_id and credentials.client_secret:
                # Standard OAuth2 refresh flow
                token_url = self._get_token_url(provider)
                
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": credentials.refresh_token,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(token_url, data=data) as response:
                        if response.status == 200:
                            token_data = await response.json()
                            
                            # Update credentials
                            credentials.access_token = token_data["access_token"]
                            if "refresh_token" in token_data:
                                credentials.refresh_token = token_data["refresh_token"]
                            if "expires_in" in token_data:
                                credentials.expires_at = datetime.utcnow() + timedelta(
                                    seconds=token_data["expires_in"]
                                )
                            
                            self.logger.info(f"Token refreshed for {provider.value}")
                        else:
                            self.logger.error(f"Token refresh failed for {provider.value}")
                            
        except Exception as e:
            self.logger.error(f"Token refresh error for {provider.value}: {e}")
    
    def _get_token_url(self, provider: APIProvider) -> str:
        """Get OAuth2 token endpoint URL for provider."""
        token_urls = {
            APIProvider.INSTAGRAM_BUSINESS: "https://api.instagram.com/oauth/access_token",
            APIProvider.TWITTER_API_V2: "https://api.twitter.com/2/oauth2/token",
            APIProvider.SPOTIFY_WEB_API: "https://accounts.spotify.com/api/token"
        }
        
        return token_urls.get(provider, "")


class APIDataNormalizer:
    """Normalize data across different API providers."""
    
    @staticmethod
    def normalize_engagement_metrics(
        platform: str,
        raw_metrics: Dict[str, Any]
    ) -> Dict[str, int]:
        """Normalize engagement metrics across platforms."""
        normalized = {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0,
            "saves": 0
        }
        
        if platform == "youtube":
            normalized["likes"] = raw_metrics.get("likeCount", 0)
            normalized["comments"] = raw_metrics.get("commentCount", 0)
            normalized["views"] = raw_metrics.get("viewCount", 0)
        
        elif platform == "instagram":
            normalized["likes"] = raw_metrics.get("like_count", 0)
            normalized["comments"] = raw_metrics.get("comments_count", 0)
            normalized["views"] = raw_metrics.get("video_view_count", 0)
        
        elif platform == "twitter":
            normalized["likes"] = raw_metrics.get("like_count", 0)
            normalized["comments"] = raw_metrics.get("reply_count", 0)
            normalized["shares"] = raw_metrics.get("retweet_count", 0)
            normalized["views"] = raw_metrics.get("impression_count", 0)
        
        elif platform == "tiktok":
            normalized["likes"] = raw_metrics.get("like_count", 0)
            normalized["comments"] = raw_metrics.get("comment_count", 0)
            normalized["shares"] = raw_metrics.get("share_count", 0)
            normalized["views"] = raw_metrics.get("play_count", 0)
        
        return normalized
    
    @staticmethod
    def normalize_content_metadata(
        platform: str,
        raw_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize content metadata across platforms."""
        normalized = {
            "content_type": "unknown",
            "duration": None,
            "quality": None,
            "language": None,
            "tags": [],
            "location": None,
            "is_live": False,
            "is_sponsored": False
        }
        
        if platform == "youtube":
            normalized["content_type"] = "video"
            normalized["duration"] = raw_metadata.get("duration")
            normalized["language"] = raw_metadata.get("defaultLanguage")
            normalized["tags"] = raw_metadata.get("tags", [])
            normalized["is_live"] = raw_metadata.get("liveBroadcastContent") == "live"
        
        elif platform == "instagram":
            media_type = raw_metadata.get("media_type", 1)
            if media_type == 1:
                normalized["content_type"] = "image"
            elif media_type == 2:
                normalized["content_type"] = "video"
            elif media_type == 8:
                normalized["content_type"] = "carousel"
            
        elif platform == "twitter":
            if "media" in raw_metadata:
                media_types = [m.get("type") for m in raw_metadata["media"]]
                if "video" in media_types:
                    normalized["content_type"] = "video"
                elif "photo" in media_types:
                    normalized["content_type"] = "image"
                else:
                    normalized["content_type"] = "text"
            else:
                normalized["content_type"] = "text"
        
        return normalized
