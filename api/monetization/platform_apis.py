"""Multi-platform API integration engine for revenue data collection.

This module provides comprehensive integration with major content platforms
to collect real-time revenue, engagement, and analytics data for creators.
Supports automated data synchronization and revenue tracking across platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Platform Integration Specialist: Multi-API Management & Data Sync
- Data Pipeline Engineer: Real-time Data Processing & ETL
- API Security Expert: OAuth2, Rate Limiting & Data Protection
- Revenue Analytics Engineer: Platform Revenue Model Analysis

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import json
import hashlib
import time
from urllib.parse import urlencode, parse_qs
import jwt
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import redis
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_database, get_redis_client
from ..core.exceptions import PlatformAPIException, AuthenticationException


class PlatformType(Enum):
    """
Supported content platforms."""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITCH = "twitch"
    PATREON = "patreon"
    BANDCAMP = "bandcamp"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"


class DataType(Enum):
    """Types of data collected from platforms."""

    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    ANALYTICS = "analytics"
    AUDIENCE = "audience"
    CONTENT = "content"
    PERFORMANCE = "performance"


class AuthMethod(Enum):
    """Platform authentication methods."""

    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


@dataclass
class PlatformCredentials:
    """Platform API credentials and configuration."""
    platform: PlatformType
    auth_method: AuthMethod
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 10000
    custom_headers: Dict[str, str] = field(default_factory=dict)
    base_url: Optional[str] = None
    webhook_secret: Optional[str] = None


@dataclass
class PlatformData:
    """
Standardized platform data structure."""
    platform: PlatformType
    creator_id: str
    data_type: DataType
    timestamp: datetime
    raw_data: Dict[str, Any]
    processed_data: Dict[str, Any]
    metrics: Dict[str, Union[int, float, Decimal]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APICallResult:
    """
Result of platform API call."""
    platform: PlatformType
    endpoint: str
    success: bool
    status_code: int
    data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    rate_limit_remaining: int
    response_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PlatformAPIManager:
    """
    Comprehensive platform API integration and data management system.
    
    Provides unified interface for collecting revenue, engagement, and analytics
    data from major content platforms with robust error handling and rate limiting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("monetization.platform_apis")
        self.db = get_database()
        self.redis = get_redis_client()
        
        # API session management
        self.session = None
        self.session_timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Platform configurations
        self.platform_configs = self._initialize_platform_configs()
        self.credentials_cache = {}
        self.rate_limits = {}
        
        # Data processing settings
        self.batch_size = self.config.get("batch_size", 100)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        
        # Initialize session
        asyncio.create_task(self._initialize_session())
        
        self.logger.info("PlatformAPIManager initialized successfully")
    
    async def _initialize_session(self):
        """Initialize aiohttp session with proper configuration."""
        try:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.session_timeout,
                headers={
                    "User-Agent": "IA-Influencer-Agent/2.0 Revenue-Tracker",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            self.logger.info("HTTP session initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise PlatformAPIException(f"Session initialization error: {e}")
    
    def _initialize_platform_configs(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform-specific configurations."""
        return {
            PlatformType.SPOTIFY: {
                "base_url": "https://api.spotify.com/v1",
                "auth_url": "https://accounts.spotify.com/api/token",
                "scopes": ["user-read-playback-position", "user-library-read"],
                "rate_limit": 100,
                "auth_method": AuthMethod.OAUTH2
            },
            PlatformType.YOUTUBE: {
                "base_url": "https://www.googleapis.com/youtube/v3",
                "auth_url": "https://oauth2.googleapis.com/token",
                "scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
                "rate_limit": 10000,
                "auth_method": AuthMethod.OAUTH2
            },
            PlatformType.INSTAGRAM: {
                "base_url": "https://graph.instagram.com",
                "auth_url": "https://api.instagram.com/oauth/access_token",
                "scopes": ["user_profile", "user_media"],
                "rate_limit": 200,
                "auth_method": AuthMethod.OAUTH2
            },
            PlatformType.TIKTOK: {
                "base_url": "https://open-api.tiktok.com/platform/v1",
                "auth_url": "https://open-api.tiktok.com/platform/oauth/token",
                "scopes": ["user.info.basic", "video.list"],
                "rate_limit": 100,
                "auth_method": AuthMethod.OAUTH2
            },
            PlatformType.TWITCH: {
                "base_url": "https://api.twitch.tv/helix",
                "auth_url": "https://id.twitch.tv/oauth2/token",
                "scopes": ["analytics:read:extensions", "analytics:read:games"],
                "rate_limit": 800,
                "auth_method": AuthMethod.OAUTH2
            },
            PlatformType.PATREON: {
                "base_url": "https://www.patreon.com/api/oauth2/v2",
                "auth_url": "https://www.patreon.com/api/oauth2/token",
                "scopes": ["identity", "campaigns"],
                "rate_limit": 60,
                "auth_method": AuthMethod.OAUTH2
            },
            PlatformType.BANDCAMP: {
                "base_url": "https://bandcamp.com/api",
                "rate_limit": 100,
                "auth_method": AuthMethod.API_KEY
            },
            PlatformType.SOUNDCLOUD: {
                "base_url": "https://api.soundcloud.com",
                "auth_url": "https://api.soundcloud.com/oauth2/token",
                "scopes": ["non-expiring"],
                "rate_limit": 15000,
                "auth_method": AuthMethod.OAUTH2
            }
        }
    
    async def register_platform_credentials(
        self,
        creator_id: str,
        credentials: PlatformCredentials
    ) -> bool:
        """
        Register and validate platform credentials for creator.
        
        Args:
            creator_id: Unique creator identifier
            credentials: Platform credentials configuration
            
        Returns:
            Success status of credential registration
        """
        try:
            self.logger.info(f"Registering {credentials.platform.value} credentials for creator: {creator_id}")
            
            # Validate credentials
            is_valid = await self._validate_credentials(credentials)
            if not is_valid:
                raise AuthenticationException(f"Invalid credentials for {credentials.platform.value}")
            
            # Encrypt sensitive data
            encrypted_credentials = await self._encrypt_credentials(credentials)
            
            # Store credentials in database
            await self._store_credentials(creator_id, encrypted_credentials)
            
            # Cache credentials
            cache_key = f"credentials:{creator_id}:{credentials.platform.value}"
            self.credentials_cache[cache_key] = credentials
            
            # Initialize rate limiting
            await self._initialize_rate_limiting(creator_id, credentials.platform)
            
            self.logger.info(f"Credentials registered successfully for {credentials.platform.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Credential registration failed: {e}")
            raise PlatformAPIException(f"Credential registration error: {e}")
    
    async def _validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """Validate platform credentials by making test API call."""
        try:
            platform_config = self.platform_configs.get(credentials.platform)
            if not platform_config:
                return False
            
            # Make test API call based on platform
            test_endpoint = self._get_test_endpoint(credentials.platform)
            headers = await self._build_auth_headers(credentials)
            
            if not self.session:
                await self._initialize_session()
            
            url = f"{platform_config['base_url']}{test_endpoint}"
            
            async with self.session.get(url, headers=headers) as response:
                return response.status in [200, 201, 202]
                
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def _get_test_endpoint(self, platform: PlatformType) -> str:
        """Get test endpoint for credential validation."""
        test_endpoints = {
            PlatformType.SPOTIFY: "/me",
            PlatformType.YOUTUBE: "/channels?part=snippet&mine=true",
            PlatformType.INSTAGRAM: "/me?fields=id,username",
            PlatformType.TIKTOK: "/user/info",
            PlatformType.TWITCH: "/users",
            PlatformType.PATREON: "/identity",
            PlatformType.SOUNDCLOUD: "/me"
        }
        return test_endpoints.get(platform, "/")
    
    async def _build_auth_headers(self, credentials: PlatformCredentials) -> Dict[str, str]:
        """Build authentication headers for API requests."""
        headers = {}
        
        if credentials.auth_method == AuthMethod.OAUTH2:
            if credentials.access_token:
                headers["Authorization"] = f"Bearer {credentials.access_token}"
        elif credentials.auth_method == AuthMethod.API_KEY:
            if credentials.api_key:
                headers["Authorization"] = f"Token {credentials.api_key}"
        elif credentials.auth_method == AuthMethod.BEARER_TOKEN:
            if credentials.access_token:
                headers["Authorization"] = f"Bearer {credentials.access_token}"
        
        # Add custom headers
        headers.update(credentials.custom_headers)
        
        # Platform-specific headers
        if credentials.platform == PlatformType.TWITCH:
            headers["Client-Id"] = credentials.client_id or ""
        
        return headers
    
    async def _encrypt_credentials(self, credentials: PlatformCredentials) -> PlatformCredentials:
        """Encrypt sensitive credential data."""
        # In production, use proper encryption (AES, etc.)
        # For now, return as-is (implement proper encryption)
        return credentials
    
    async def _store_credentials(self, creator_id: str, credentials: PlatformCredentials):
        """
Store encrypted credentials in database."""
        try:
            query = """
            INSERT INTO platform_credentials (
                creator_id, platform, auth_method, client_id, client_secret,
                api_key, access_token, refresh_token, token_expires_at,
                scopes, rate_limit_per_minute, rate_limit_per_day,
                custom_headers, base_url, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            ON CONFLICT (creator_id, platform) DO UPDATE SET
                auth_method = $3, client_id = $4, client_secret = $5,
                api_key = $6, access_token = $7, refresh_token = $8,
                token_expires_at = $9, scopes = $10, rate_limit_per_minute = $11,
                rate_limit_per_day = $12, custom_headers = $13, base_url = $14,
                updated_at = $16
            """
            
            await self.db.execute(
                query,
                creator_id,
                credentials.platform.value,
                credentials.auth_method.value,
                credentials.client_id,
                credentials.client_secret,
                credentials.api_key,
                credentials.access_token,
                credentials.refresh_token,
                credentials.token_expires_at,
                json.dumps(credentials.scopes),
                credentials.rate_limit_per_minute,
                credentials.rate_limit_per_day,
                json.dumps(credentials.custom_headers),
                credentials.base_url,
                datetime.utcnow(),
                datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Credential storage failed: {e}")
            raise PlatformAPIException(f"Credential storage error: {e}")
    
    async def _initialize_rate_limiting(self, creator_id: str, platform: PlatformType):
        """Initialize rate limiting for creator-platform combination."""
        rate_key = f"rate_limit:{creator_id}:{platform.value}"
        platform_config = self.platform_configs.get(platform, {})
        
        self.rate_limits[rate_key] = {
            "per_minute": platform_config.get("rate_limit", 60),
            "per_day": platform_config.get("daily_limit", 10000),
            "current_minute": 0,
            "current_day": 0,
            "reset_time": datetime.utcnow() + timedelta(minutes=1),
            "daily_reset": datetime.utcnow() + timedelta(days=1)
        }
    
    async def collect_platform_data(
        self,
        creator_id: str,
        platforms: List[PlatformType],
        data_types: List[DataType],
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[PlatformType, List[PlatformData]]:
        """
        Collect data from multiple platforms simultaneously.
        
        Args:
            creator_id: Unique creator identifier
            platforms: List of platforms to collect data from
            data_types: Types of data to collect
            date_range: Optional date range for historical data
            
        Returns:
            Dictionary of platform data organized by platform
        """
        try:
            self.logger.info(f"Collecting data for creator: {creator_id} from {len(platforms)} platforms")
            
            # Prepare collection tasks
            tasks = []
            for platform in platforms:
                for data_type in data_types:
                    task = self._collect_single_platform_data(
                        creator_id, platform, data_type, date_range
                    )
                    tasks.append(task)
            
            # Execute tasks concurrently with rate limiting
            results = await self._execute_with_rate_limiting(tasks)
            
            # Organize results by platform
            platform_data = {}
            for result in results:
                if result and isinstance(result, list):
                    for data_item in result:
                        platform = data_item.platform
                        if platform not in platform_data:
                            platform_data[platform] = []
                        platform_data[platform].append(data_item)
            
            # Store collected data
            await self._store_platform_data(creator_id, platform_data)
            
            self.logger.info(f"Data collection completed for {len(platform_data)} platforms")
            
            return platform_data
            
        except Exception as e:
            self.logger.error(f"Platform data collection failed: {e}")
            raise PlatformAPIException(f"Data collection error: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _collect_single_platform_data(
        self,
        creator_id: str,
        platform: PlatformType,
        data_type: DataType,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> List[PlatformData]:
        """Collect data from a single platform with retry logic."""
        try:
            # Get credentials
            credentials = await self._get_credentials(creator_id, platform)
            if not credentials:
                raise AuthenticationException(f"No credentials found for {platform.value}")
            
            # Check rate limits
            await self._check_rate_limit(creator_id, platform)
            
            # Refresh token if needed
            await self._refresh_token_if_needed(credentials)
            
            # Get appropriate collector method
            collector = self._get_data_collector(platform, data_type)
            if not collector:
                raise PlatformAPIException(f"No collector available for {platform.value}/{data_type.value}")
            
            # Collect data
            raw_data = await collector(credentials, date_range)
            
            # Process and standardize data
            platform_data = await self._process_platform_data(
                platform, creator_id, data_type, raw_data
            )
            
            # Update rate limit counters
            await self._update_rate_limit_counters(creator_id, platform)
            
            return platform_data
            
        except Exception as e:
            self.logger.error(f"Single platform data collection failed for {platform.value}: {e}")
            raise PlatformAPIException(f"{platform.value} collection error: {e}")
    
    async def _get_credentials(
        self,
        creator_id: str,
        platform: PlatformType
    ) -> Optional[PlatformCredentials]:
        """Get cached or retrieve platform credentials."""
        cache_key = f"credentials:{creator_id}:{platform.value}"
        
        # Check cache first
        if cache_key in self.credentials_cache:
            return self.credentials_cache[cache_key]
        
        # Retrieve from database
        try:
            query = """
            SELECT * FROM platform_credentials 
            WHERE creator_id = $1 AND platform = $2
            """
            
            result = await self.db.fetchrow(query, creator_id, platform.value)
            
            if not result:
                return None
            
            credentials = PlatformCredentials(
                platform=PlatformType(result["platform"]),
                auth_method=AuthMethod(result["auth_method"]),
                client_id=result["client_id"],
                client_secret=result["client_secret"],
                api_key=result["api_key"],
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                token_expires_at=result["token_expires_at"],
                scopes=json.loads(result["scopes"] or "[]"),
                rate_limit_per_minute=result["rate_limit_per_minute"],
                rate_limit_per_day=result["rate_limit_per_day"],
                custom_headers=json.loads(result["custom_headers"] or "{}"),
                base_url=result["base_url"]
            )
            
            # Cache credentials
            self.credentials_cache[cache_key] = credentials
            
            return credentials
            
        except Exception as e:
            self.logger.error(f"Credential retrieval failed: {e}")
            return None
    
    async def _check_rate_limit(self, creator_id: str, platform: PlatformType):
        """Check and enforce rate limits."""
        rate_key = f"rate_limit:{creator_id}:{platform.value}"
        
        if rate_key not in self.rate_limits:
            await self._initialize_rate_limiting(creator_id, platform)
        
        limits = self.rate_limits[rate_key]
        now = datetime.utcnow()
        
        # Reset counters if time windows expired
        if now >= limits["reset_time"]:
            limits["current_minute"] = 0
            limits["reset_time"] = now + timedelta(minutes=1)
        
        if now >= limits["daily_reset"]:
            limits["current_day"] = 0
            limits["daily_reset"] = now + timedelta(days=1)
        
        # Check limits
        if limits["current_minute"] >= limits["per_minute"]:
            wait_time = (limits["reset_time"] - now).total_seconds()
            await asyncio.sleep(wait_time)
        
        if limits["current_day"] >= limits["per_day"]:
            raise PlatformAPIException(f"Daily rate limit exceeded for {platform.value}")
    
    async def _refresh_token_if_needed(self, credentials: PlatformCredentials):
        """Refresh access token if it's expired or close to expiring."""
        if not credentials.refresh_token:
            return
        
        if credentials.token_expires_at:
            # Check if token expires within next 5 minutes
            buffer_time = datetime.utcnow() + timedelta(minutes=5)
            if credentials.token_expires_at > buffer_time:
                return  # Token is still valid
        
        # Refresh token
        await self._refresh_access_token(credentials)
    
    async def _refresh_access_token(self, credentials: PlatformCredentials):
        """
Refresh OAuth2 access token."""
        try:
            platform_config = self.platform_configs.get(credentials.platform)
            if not platform_config or not platform_config.get("auth_url"):
                return
            
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": credentials.refresh_token,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret
            }
            
            if not self.session:
                await self._initialize_session()
            
            async with self.session.post(
                platform_config["auth_url"],
                data=refresh_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                
                if response.status == 200:
                    token_data = await response.json()
                    
                    # Update credentials
                    credentials.access_token = token_data.get("access_token")
                    if "refresh_token" in token_data:
                        credentials.refresh_token = token_data["refresh_token"]
                    
                    # Calculate expiration time
                    if "expires_in" in token_data:
                        expires_in = int(token_data["expires_in"])
                        credentials.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.logger.info(f"Token refreshed for {credentials.platform.value}")
                else:
                    self.logger.error(f"Token refresh failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
    
    def _get_data_collector(
        self,
        platform: PlatformType,
        data_type: DataType
    ) -> Optional[callable]:
        """Get appropriate data collector method for platform and data type."""
        collectors = {
            (PlatformType.SPOTIFY, DataType.REVENUE): self._collect_spotify_revenue,
            (PlatformType.SPOTIFY, DataType.ANALYTICS): self._collect_spotify_analytics,
            (PlatformType.YOUTUBE, DataType.REVENUE): self._collect_youtube_revenue,
            (PlatformType.YOUTUBE, DataType.ANALYTICS): self._collect_youtube_analytics,
            (PlatformType.INSTAGRAM, DataType.ENGAGEMENT): self._collect_instagram_engagement,
            (PlatformType.TIKTOK, DataType.ANALYTICS): self._collect_tiktok_analytics,
            (PlatformType.TWITCH, DataType.REVENUE): self._collect_twitch_revenue,
            (PlatformType.PATREON, DataType.REVENUE): self._collect_patreon_revenue,
            (PlatformType.SOUNDCLOUD, DataType.ANALYTICS): self._collect_soundcloud_analytics
        }
        
        return collectors.get((platform, data_type))
    
    async def _collect_spotify_revenue(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """
Collect Spotify revenue data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.SPOTIFY]["base_url"]
            
            # Spotify doesn't provide direct revenue API, so we collect play data
            # and estimate revenue based on industry rates
            endpoints = [
                "/me/player/recently-played?limit=50",
                "/me/tracks?limit=50",
                "/me/albums?limit=50"
            ]
            
            collected_data = {}
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_key = endpoint.split('/')[-1].split('?')[0]
                        collected_data[endpoint_key] = data
                    else:
                        self.logger.warning(f"Spotify API error {response.status} for {endpoint}")
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Spotify data collection failed: {e}")
            return {}
    
    async def _collect_spotify_analytics(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect Spotify analytics data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.SPOTIFY]["base_url"]
            
            # Collect user profile and listening data
            endpoints = [
                "/me",
                "/me/playlists?limit=50",
                "/me/following?type=artist&limit=50",
                "/me/top/artists?time_range=medium_term&limit=50",
                "/me/top/tracks?time_range=medium_term&limit=50"
            ]
            
            analytics_data = {}
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_key = endpoint.split('/')[-1].split('?')[0]
                        analytics_data[endpoint_key] = data
                    await asyncio.sleep(0.1)  # Rate limiting
            
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"Spotify analytics collection failed: {e}")
            return {}
    
    async def _collect_youtube_revenue(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect YouTube revenue data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.YOUTUBE]["base_url"]
            
            # YouTube Analytics API endpoints
            params = {
                "ids": "channel==MINE",
                "metrics": "estimatedRevenue,monetizedPlaybacks,playbackBasedCpm",
                "dimensions": "day",
                "key": credentials.api_key
            }
            
            if date_range:
                params["start-date"] = date_range[0].strftime("%Y-%m-%d")
                params["end-date"] = date_range[1].strftime("%Y-%m-%d")
            else:
                params["start-date"] = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
                params["end-date"] = datetime.utcnow().strftime("%Y-%m-%d")
            
            url = f"{base_url}/reports?" + urlencode(params)
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"YouTube revenue API error: {response.status}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"YouTube revenue collection failed: {e}")
            return {}
    
    async def _collect_youtube_analytics(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect YouTube analytics data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.YOUTUBE]["base_url"]
            
            # Collect channel and video statistics
            analytics_data = {}
            
            # Channel analytics
            channel_params = {
                "part": "statistics,snippet,brandingSettings",
                "mine": "true",
                "key": credentials.api_key
            }
            
            channel_url = f"{base_url}/channels?" + urlencode(channel_params)
            async with self.session.get(channel_url, headers=headers) as response:
                if response.status == 200:
                    analytics_data["channel"] = await response.json()
            
            # Video analytics
            video_params = {
                "part": "statistics,snippet,contentDetails",
                "chart": "mostPopular",
                "regionCode": "US",
                "maxResults": 50,
                "key": credentials.api_key
            }
            
            video_url = f"{base_url}/videos?" + urlencode(video_params)
            async with self.session.get(video_url, headers=headers) as response:
                if response.status == 200:
                    analytics_data["videos"] = await response.json()
            
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"YouTube analytics collection failed: {e}")
            return {}
    
    async def _collect_instagram_engagement(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect Instagram engagement data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.INSTAGRAM]["base_url"]
            
            # Instagram Graph API endpoints
            endpoints = [
                "/me?fields=id,username,followers_count,media_count",
                "/me/media?fields=id,media_type,like_count,comments_count,timestamp,permalink"
            ]
            
            engagement_data = {}
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_key = endpoint.split('?')[0].split('/')[-1]
                        engagement_data[endpoint_key] = data
                    await asyncio.sleep(0.2)  # Instagram rate limiting
            
            return engagement_data
            
        except Exception as e:
            self.logger.error(f"Instagram engagement collection failed: {e}")
            return {}
    
    async def _collect_tiktok_analytics(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect TikTok analytics data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.TIKTOK]["base_url"]
            
            # TikTok Research API endpoints
            analytics_data = {}
            
            # User info
            user_url = f"{base_url}/user/info"
            async with self.session.get(user_url, headers=headers) as response:
                if response.status == 200:
                    analytics_data["user"] = await response.json()
            
            # Video list
            video_params = {"count": 20}
            video_url = f"{base_url}/video/list?" + urlencode(video_params)
            async with self.session.get(video_url, headers=headers) as response:
                if response.status == 200:
                    analytics_data["videos"] = await response.json()
            
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"TikTok analytics collection failed: {e}")
            return {}
    
    async def _collect_twitch_revenue(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect Twitch revenue data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.TWITCH]["base_url"]
            
            # Twitch API endpoints for revenue-related data
            revenue_data = {}
            
            # User info and follower count
            user_url = f"{base_url}/users"
            async with self.session.get(user_url, headers=headers) as response:
                if response.status == 200:
                    revenue_data["user"] = await response.json()
            
            # Subscription data (if available)
            subs_url = f"{base_url}/subscriptions"
            async with self.session.get(subs_url, headers=headers) as response:
                if response.status == 200:
                    revenue_data["subscriptions"] = await response.json()
            
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"Twitch revenue collection failed: {e}")
            return {}
    
    async def _collect_patreon_revenue(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect Patreon revenue data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.PATREON]["base_url"]
            
            # Patreon API endpoints
            revenue_data = {}
            
            # Identity and campaigns
            identity_url = f"{base_url}/identity?include=campaigns"
            async with self.session.get(identity_url, headers=headers) as response:
                if response.status == 200:
                    revenue_data["identity"] = await response.json()
            
            # Campaign pledges (if campaign exists)
            # This would require campaign ID from identity response
            
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"Patreon revenue collection failed: {e}")
            return {}
    
    async def _collect_soundcloud_analytics(
        self,
        credentials: PlatformCredentials,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Collect SoundCloud analytics data."""
        try:
            headers = await self._build_auth_headers(credentials)
            base_url = credentials.base_url or self.platform_configs[PlatformType.SOUNDCLOUD]["base_url"]
            
            # SoundCloud API endpoints
            analytics_data = {}
            
            # User info
            me_url = f"{base_url}/me?oauth_token={credentials.access_token}"
            async with self.session.get(me_url) as response:
                if response.status == 200:
                    analytics_data["user"] = await response.json()
            
            # Tracks
            tracks_url = f"{base_url}/me/tracks?oauth_token={credentials.access_token}"
            async with self.session.get(tracks_url) as response:
                if response.status == 200:
                    analytics_data["tracks"] = await response.json()
            
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"SoundCloud analytics collection failed: {e}")
            return {}
    
    async def _process_platform_data(
        self,
        platform: PlatformType,
        creator_id: str,
        data_type: DataType,
        raw_data: Dict[str, Any]
    ) -> List[PlatformData]:
        """Process and standardize raw platform data."""
        try:
            processed_data_list = []
            
            # Platform-specific processing
            if platform == PlatformType.SPOTIFY:
                processed = await self._process_spotify_data(raw_data, data_type)
            elif platform == PlatformType.YOUTUBE:
                processed = await self._process_youtube_data(raw_data, data_type)
            elif platform == PlatformType.INSTAGRAM:
                processed = await self._process_instagram_data(raw_data, data_type)
            elif platform == PlatformType.TIKTOK:
                processed = await self._process_tiktok_data(raw_data, data_type)
            else:
                # Generic processing
                processed = {
                    "total_engagement": 0,
                    "revenue_estimate": Decimal("0.00"),
                    "metrics_count": len(raw_data)
                }
            
            # Calculate metrics
            metrics = await self._calculate_platform_metrics(platform, processed, data_type)
            
            # Create standardized data object
            platform_data = PlatformData(
                platform=platform,
                creator_id=creator_id,
                data_type=data_type,
                timestamp=datetime.utcnow(),
                raw_data=raw_data,
                processed_data=processed,
                metrics=metrics,
                metadata={
                    "collection_method": "api",
                    "data_points": len(raw_data) if isinstance(raw_data, (list, dict)) else 1,
                    "processing_version": "2.0"
                }
            )
            
            processed_data_list.append(platform_data)
            
            return processed_data_list
            
        except Exception as e:
            self.logger.error(f"Platform data processing failed: {e}")
            return []
    
    async def _process_spotify_data(
        self,
        raw_data: Dict[str, Any],
        data_type: DataType
    ) -> Dict[str, Any]:
        """Process Spotify-specific data."""
        processed = {
            "total_tracks": 0,
            "total_plays": 0,
            "estimated_revenue": Decimal("0.00"),
            "top_genres": [],
            "listening_time": 0
        }
        
        try:
            # Process recently played tracks
            if "recently-played" in raw_data:
                items = raw_data["recently-played"].get("items", [])
                processed["total_plays"] = len(items)
                
                # Estimate revenue (Spotify pays ~$0.003 per stream)
                processed["estimated_revenue"] = Decimal(str(len(items) * 0.003))
            
            # Process user tracks
            if "tracks" in raw_data:
                items = raw_data["tracks"].get("items", [])
                processed["total_tracks"] = len(items)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Spotify data processing failed: {e}")
            return processed
    
    async def _process_youtube_data(
        self,
        raw_data: Dict[str, Any],
        data_type: DataType
    ) -> Dict[str, Any]:
        """Process YouTube-specific data."""
        processed = {
            "total_views": 0,
            "total_revenue": Decimal("0.00"),
            "subscriber_count": 0,
            "video_count": 0,
            "engagement_rate": 0.0
        }
        
        try:
            # Process channel data
            if "channel" in raw_data:
                items = raw_data["channel"].get("items", [])
                if items:
                    stats = items[0].get("statistics", {})
                    processed["total_views"] = int(stats.get("viewCount", 0))
                    processed["subscriber_count"] = int(stats.get("subscriberCount", 0))
                    processed["video_count"] = int(stats.get("videoCount", 0))
            
            # Process revenue data
            if "rows" in raw_data:
                for row in raw_data["rows"]:
                    if len(row) >= 2:
                        revenue = row[1]  # Estimated revenue column
                        processed["total_revenue"] += Decimal(str(revenue or 0))
            
            return processed
            
        except Exception as e:
            self.logger.error(f"YouTube data processing failed: {e}")
            return processed
    
    async def _process_instagram_data(
        self,
        raw_data: Dict[str, Any],
        data_type: DataType
    ) -> Dict[str, Any]:
        """Process Instagram-specific data."""
        processed = {
            "followers_count": 0,
            "media_count": 0,
            "total_likes": 0,
            "total_comments": 0,
            "engagement_rate": 0.0
        }
        
        try:
            # Process user data
            if "me" in raw_data:
                user_data = raw_data["me"]
                processed["followers_count"] = user_data.get("followers_count", 0)
                processed["media_count"] = user_data.get("media_count", 0)
            
            # Process media data
            if "media" in raw_data:
                media_data = raw_data["media"].get("data", [])
                for media in media_data:
                    processed["total_likes"] += media.get("like_count", 0)
                    processed["total_comments"] += media.get("comments_count", 0)
                
                # Calculate engagement rate
                if processed["followers_count"] > 0:
                    total_engagement = processed["total_likes"] + processed["total_comments"]
                    processed["engagement_rate"] = total_engagement / processed["followers_count"]
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Instagram data processing failed: {e}")
            return processed
    
    async def _process_tiktok_data(
        self,
        raw_data: Dict[str, Any],
        data_type: DataType
    ) -> Dict[str, Any]:
        """Process TikTok-specific data."""
        processed = {
            "followers_count": 0,
            "video_count": 0,
            "total_views": 0,
            "total_likes": 0,
            "engagement_rate": 0.0
        }
        
        try:
            # Process user data
            if "user" in raw_data:
                user_data = raw_data["user"].get("data", {})
                processed["followers_count"] = user_data.get("follower_count", 0)
            
            # Process video data
            if "videos" in raw_data:
                videos = raw_data["videos"].get("data", {}).get("videos", [])
                processed["video_count"] = len(videos)
                
                for video in videos:
                    stats = video.get("statistics", {})
                    processed["total_views"] += stats.get("view_count", 0)
                    processed["total_likes"] += stats.get("like_count", 0)
                
                # Calculate engagement rate
                if processed["followers_count"] > 0:
                    processed["engagement_rate"] = processed["total_likes"] / processed["followers_count"]
            
            return processed
            
        except Exception as e:
            self.logger.error(f"TikTok data processing failed: {e}")
            return processed
    
    async def _calculate_platform_metrics(
        self,
        platform: PlatformType,
        processed_data: Dict[str, Any],
        data_type: DataType
    ) -> Dict[str, Union[int, float, Decimal]]:
        """Calculate standardized metrics from processed data."""
        metrics = {}
        
        try:
            # Common metrics calculation
            if "total_views" in processed_data:
                metrics["views"] = int(processed_data["total_views"])
            
            if "followers_count" in processed_data:
                metrics["followers"] = int(processed_data["followers_count"])
            
            if "engagement_rate" in processed_data:
                metrics["engagement_rate"] = float(processed_data["engagement_rate"])
            
            if "estimated_revenue" in processed_data:
                metrics["revenue_estimate"] = Decimal(str(processed_data["estimated_revenue"]))
            elif "total_revenue" in processed_data:
                metrics["revenue_estimate"] = Decimal(str(processed_data["total_revenue"]))
            
            # Platform-specific metric calculations
            if platform == PlatformType.SPOTIFY:
                metrics["stream_count"] = processed_data.get("total_plays", 0)
                metrics["track_count"] = processed_data.get("total_tracks", 0)
            
            elif platform == PlatformType.YOUTUBE:
                metrics["subscriber_count"] = processed_data.get("subscriber_count", 0)
                metrics["video_count"] = processed_data.get("video_count", 0)
            
            elif platform in [PlatformType.INSTAGRAM, PlatformType.TIKTOK]:
                metrics["likes_count"] = processed_data.get("total_likes", 0)
                metrics["comments_count"] = processed_data.get("total_comments", 0)
                metrics["media_count"] = processed_data.get("media_count", 0)
            
            # Calculate derived metrics
            if "views" in metrics and "followers" in metrics and metrics["followers"] > 0:
                metrics["views_per_follower"] = float(metrics["views"] / metrics["followers"])
            
            if "revenue_estimate" in metrics and "views" in metrics and metrics["views"] > 0:
                metrics["revenue_per_view"] = metrics["revenue_estimate"] / metrics["views"]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {e}")
            return {}
    
    async def _execute_with_rate_limiting(self, tasks: List) -> List:
        """Execute tasks with proper rate limiting and error handling."""
        results = []
        
        # Group tasks by platform to manage rate limits
        platform_tasks = {}
        for task in tasks:
            # Extract platform from task (simplified)
            platform_key = "default"  # In real implementation, extract from task
            if platform_key not in platform_tasks:
                platform_tasks[platform_key] = []
            platform_tasks[platform_key].append(task)
        
        # Execute tasks for each platform sequentially, but platforms in parallel
        platform_results = await asyncio.gather(
            *[self._execute_platform_tasks(tasks) for tasks in platform_tasks.values()],
            return_exceptions=True
        )
        
        # Flatten results
        for platform_result in platform_results:
            if isinstance(platform_result, Exception):
                self.logger.error(f"Platform task execution failed: {platform_result}")
            elif isinstance(platform_result, list):
                results.extend(platform_result)
        
        return results
    
    async def _execute_platform_tasks(self, tasks: List) -> List:
        """Execute tasks for a single platform with rate limiting."""
        results = []
        
        for task in tasks:
            try:
                result = await task
                results.append(result)
                
                # Rate limiting delay
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Task execution failed: {e}")
                results.append(None)
        
        return results
    
    async def _update_rate_limit_counters(self, creator_id: str, platform: PlatformType):
        """Update rate limit counters after successful API call."""
        rate_key = f"rate_limit:{creator_id}:{platform.value}"
        
        if rate_key in self.rate_limits:
            self.rate_limits[rate_key]["current_minute"] += 1
            self.rate_limits[rate_key]["current_day"] += 1
    
    async def _store_platform_data(
        self,
        creator_id: str,
        platform_data: Dict[PlatformType, List[PlatformData]]
    ):
        """Store collected platform data in database."""
        try:
            for platform, data_list in platform_data.items():
                for data in data_list:
                    query = """
                    INSERT INTO platform_data_collection (
                        creator_id, platform, data_type, timestamp,
                        raw_data, processed_data, metrics, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """
                    
                    await self.db.execute(
                        query,
                        creator_id,
                        data.platform.value,
                        data.data_type.value,
                        data.timestamp,
                        json.dumps(data.raw_data, default=str),
                        json.dumps(data.processed_data, default=str),
                        json.dumps({k: str(v) for k, v in data.metrics.items()}),
                        json.dumps(data.metadata)
                    )
            
            self.logger.info(f"Platform data stored successfully for creator: {creator_id}")
            
        except Exception as e:
            self.logger.error(f"Platform data storage failed: {e}")
    
    async def get_platform_summary(
        self,
        creator_id: str,
        days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get summary of platform performance and revenue data.
        
        Args:
            creator_id: Unique creator identifier
            days: Number of days to include in summary
            
        Returns:
            Dictionary of platform summaries with key metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = """
            SELECT 
                platform,
                data_type,
                COUNT(*) as data_points,
                AVG((metrics->>'revenue_estimate')::decimal) as avg_revenue,
                AVG((metrics->>'engagement_rate')::decimal) as avg_engagement,
                MAX((metrics->>'followers')::bigint) as max_followers,
                SUM((metrics->>'views')::bigint) as total_views
            FROM platform_data_collection
            WHERE creator_id = $1 
            AND timestamp BETWEEN $2 AND $3
            GROUP BY platform, data_type
            """
            
            results = await self.db.fetch(query, creator_id, start_date, end_date)
            
            # Organize results by platform
            platform_summary = {}
            for row in results:
                platform = row["platform"]
                if platform not in platform_summary:
                    platform_summary[platform] = {
                        "data_points": 0,
                        "avg_revenue": Decimal("0.00"),
                        "avg_engagement": 0.0,
                        "max_followers": 0,
                        "total_views": 0,
                        "data_types": []
                    }
                
                summary = platform_summary[platform]
                summary["data_points"] += row["data_points"] or 0
                summary["avg_revenue"] += Decimal(str(row["avg_revenue"] or 0))
                summary["avg_engagement"] = max(summary["avg_engagement"], float(row["avg_engagement"] or 0))
                summary["max_followers"] = max(summary["max_followers"], row["max_followers"] or 0)
                summary["total_views"] += row["total_views"] or 0
                summary["data_types"].append(row["data_type"])
            
            return platform_summary
            
        except Exception as e:
            self.logger.error(f"Platform summary generation failed: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
            
            # Clear caches
            self.credentials_cache.clear()
            self.rate_limits.clear()
            
            self.logger.info("PlatformAPIManager resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Factory function for easy instantiation
def create_platform_api_manager(config: Optional[Dict[str, Any]] = None) -> PlatformAPIManager:
    """Create and return configured platform API manager instance."""
    return PlatformAPIManager(config)
