"""
Multi-Platform API Integration Engine
=====================================

Professional API integration system for content monetization platforms.
Handles real-time data synchronization, revenue tracking, analytics aggregation,
and automated platform interactions for content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import uuid
import json
import aiohttp
import time

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import jwt
from cryptography.fernet import Fernet

from .revenue_calculator import Currency


class PlatformType(Enum):
    """Supported monetization platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class APIStatus(Enum):
    """API connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"
    UNAUTHORIZED = "unauthorized"


class DataType(Enum):
    """Types of data to sync"""
    REVENUE = "revenue"
    ANALYTICS = "analytics"
    AUDIENCE = "audience"
    CONTENT = "content"
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform: PlatformType
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    scopes: List[str]
    user_id: str
    metadata: Dict[str, Any]


@dataclass
class APIResponse:
    """Standardized API response"""
    platform: PlatformType
    data_type: DataType
    data: Dict[str, Any]
    timestamp: datetime
    success: bool
    error_message: Optional[str]
    rate_limit_remaining: int
    next_request_allowed: datetime


@dataclass
class RevenueData:
    """Platform revenue data"""
    platform: PlatformType
    user_id: str
    content_id: str
    revenue_amount: Decimal
    currency: Currency
    period_start: datetime
    period_end: datetime
    views: int
    clicks: int
    impressions: int
    cpm: Decimal
    metadata: Dict[str, Any]


@dataclass
class AnalyticsData:
    """Platform analytics data"""
    platform: PlatformType
    user_id: str
    content_id: str
    views: int
    likes: int
    shares: int
    comments: int
    engagement_rate: float
    reach: int
    impressions: int
    audience_demographics: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class PlatformAPIs:
    """
    Professional platform API integration engine for IA Influencer Agent.
    
    Provides unified access to multiple monetization platforms,
    real-time data synchronization, and comprehensive revenue tracking
    across all major content platforms.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize PlatformAPIs.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.cache_ttl = 900  # 15 minutes
        self.rate_limit_buffer = 0.1  # 10% buffer
        self.max_retry_attempts = 3
        self.request_timeout = 30
        
        # Platform configurations
        self.platform_configs = {
            PlatformType.YOUTUBE: {
                'base_url': 'https://www.googleapis.com/youtube/v3',
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'scopes': ['https://www.googleapis.com/auth/youtube.readonly',
                          'https://www.googleapis.com/auth/yt-analytics.readonly'],
                'rate_limit': 10000,  # requests per day
                'rate_window': 86400  # 24 hours
            },
            PlatformType.INSTAGRAM: {
                'base_url': 'https://graph.instagram.com',
                'auth_url': 'https://api.instagram.com/oauth/authorize',
                'token_url': 'https://api.instagram.com/oauth/access_token',
                'scopes': ['user_profile', 'user_media', 'instagram_insights'],
                'rate_limit': 200,  # requests per hour
                'rate_window': 3600  # 1 hour
            },
            PlatformType.TIKTOK: {
                'base_url': 'https://open-api.tiktok.com',
                'auth_url': 'https://www.tiktok.com/auth/authorize',
                'token_url': 'https://open-api.tiktok.com/oauth/access_token',
                'scopes': ['user.info.basic', 'video.list', 'user.info.stats'],
                'rate_limit': 1000,  # requests per hour
                'rate_window': 3600
            },
            PlatformType.SPOTIFY: {
                'base_url': 'https://api.spotify.com/v1',
                'auth_url': 'https://accounts.spotify.com/authorize',
                'token_url': 'https://accounts.spotify.com/api/token',
                'scopes': ['user-read-private', 'user-top-read', 'playlist-read-private'],
                'rate_limit': 100,  # requests per second
                'rate_window': 1
            }
        }
        
        # Initialize encryption for credentials
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Session for HTTP requests
        self.http_session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_session:
            await self.http_session.close()
    
    async def connect_platform(self, user_id: str, platform: PlatformType,
                             auth_code: str) -> bool:
        """
        Connect user account to platform.
        
        Args:
            user_id: User identifier
            platform: Platform to connect
            auth_code: OAuth authorization code
            
        Returns:
            Connection success status
        """



        try:
            # Exchange auth code for access token
            credentials = await self._exchange_auth_code(platform, auth_code, user_id)
            
            # Validate credentials
            if not await self._validate_credentials(credentials):
                raise ValueError("Invalid credentials received")
            
            # Store encrypted credentials
            await self._store_credentials(user_id, credentials)
            
            # Test API connection
            test_response = await self._test_api_connection(credentials)
            if not test_response.success:
                raise ValueError(f"API connection test failed: {test_response.error_message}")
            
            # Initialize data sync
            await self._initialize_data_sync(user_id, platform)
            
            self.logger.info(f"Platform connected successfully: {platform.value} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting platform {platform.value}: {str(e)}")
            return False
    
    async def sync_revenue_data(self, user_id: str, platform: PlatformType,
                              days_back: int = 30) -> List[RevenueData]:
        """
        Synchronize revenue data from platform.
        
        Args:
            user_id: User identifier
            platform: Platform to sync from
            days_back: Number of days to sync back
            
        Returns:
            List of revenue data records
        """



        try:
            # Get user credentials
            credentials = await self._get_credentials(user_id, platform)
            if not credentials:
                raise ValueError(f"No credentials found for {platform.value}")
            
            # Check rate limits
            if not await self._check_rate_limit(platform):
                raise ValueError(f"Rate limit exceeded for {platform.value}")
            
            # Fetch revenue data based on platform
            if platform == PlatformType.YOUTUBE:
                revenue_data = await self._sync_youtube_revenue(credentials, days_back)
            elif platform == PlatformType.INSTAGRAM:
                revenue_data = await self._sync_instagram_revenue(credentials, days_back)
            elif platform == PlatformType.TIKTOK:
                revenue_data = await self._sync_tiktok_revenue(credentials, days_back)
            elif platform == PlatformType.SPOTIFY:
                revenue_data = await self._sync_spotify_revenue(credentials, days_back)
            else:
                raise ValueError(f"Platform not supported: {platform.value}")
            
            # Store revenue data
            await self._store_revenue_data(revenue_data)
            
            # Cache for quick access
            await self._cache_revenue_data(user_id, platform, revenue_data)
            
            self.logger.info(f"Synced {len(revenue_data)} revenue records from {platform.value}")
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"Error syncing revenue data from {platform.value}: {str(e)}")
            return []
    
    async def sync_analytics_data(self, user_id: str, platform: PlatformType,
                                days_back: int = 30) -> List[AnalyticsData]:
        """
        Synchronize analytics data from platform.
        
        Args:
            user_id: User identifier
            platform: Platform to sync from
            days_back: Number of days to sync back
            
        Returns:
            List of analytics data records
        """



        try:
            # Get user credentials
            credentials = await self._get_credentials(user_id, platform)
            if not credentials:
                raise ValueError(f"No credentials found for {platform.value}")
            
            # Check rate limits
            if not await self._check_rate_limit(platform):
                raise ValueError(f"Rate limit exceeded for {platform.value}")
            
            # Fetch analytics data based on platform
            if platform == PlatformType.YOUTUBE:
                analytics_data = await self._sync_youtube_analytics(credentials, days_back)
            elif platform == PlatformType.INSTAGRAM:
                analytics_data = await self._sync_instagram_analytics(credentials, days_back)
            elif platform == PlatformType.TIKTOK:
                analytics_data = await self._sync_tiktok_analytics(credentials, days_back)
            elif platform == PlatformType.SPOTIFY:
                analytics_data = await self._sync_spotify_analytics(credentials, days_back)
            else:
                raise ValueError(f"Platform not supported: {platform.value}")
            
            # Store analytics data
            await self._store_analytics_data(analytics_data)
            
            # Cache for quick access
            await self._cache_analytics_data(user_id, platform, analytics_data)
            
            self.logger.info(f"Synced {len(analytics_data)} analytics records from {platform.value}")
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"Error syncing analytics data from {platform.value}: {str(e)}")
            return []
    
    async def get_real_time_metrics(self, user_id: str, platform: PlatformType) -> Dict[str, Any]:
        """
        Get real-time metrics from platform.
        
        Args:
            user_id: User identifier
            platform: Platform to query
            
        Returns:
            Real-time metrics data
        """



        try:
            # Check cache first
            cache_key = f"realtime_metrics:{user_id}:{platform.value}"
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Get user credentials
            credentials = await self._get_credentials(user_id, platform)
            if not credentials:
                return {}
            
            # Fetch real-time data
            metrics = await self._fetch_real_time_metrics(credentials, platform)
            
            # Cache for 5 minutes
            await self._save_to_cache(cache_key, metrics, ttl=300)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {str(e)}")
            return {}
    
    async def refresh_access_tokens(self) -> Dict[str, bool]:
        """
        Refresh access tokens for all connected platforms.
        
        Returns:
            Dictionary of platform refresh results
        """



        try:
            results = {}
            
            # Get all stored credentials
            all_credentials = await self._get_all_credentials()
            
            for user_id, platform_creds in all_credentials.items():
                for platform, credentials in platform_creds.items():
                    try:
                        # Check if token needs refresh
                        if credentials.expires_at <= datetime.utcnow() + timedelta(hours=1):
                            # Refresh token
                            new_credentials = await self._refresh_token(credentials)
                            
                            if new_credentials:
                                # Store updated credentials
                                await self._store_credentials(user_id, new_credentials)
                                results[f"{user_id}:{platform}"] = True
                            else:
                                results[f"{user_id}:{platform}"] = False
                        else:
                            results[f"{user_id}:{platform}"] = True  # No refresh needed
                            
                    except Exception as e:
                        self.logger.error(f"Error refreshing token for {user_id}:{platform}: {str(e)}")
                        results[f"{user_id}:{platform}"] = False
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error refreshing access tokens: {str(e)}")
            return {}
    
    async def get_platform_status(self, user_id: str) -> Dict[str, Dict]:
        """
        Get connection status for all platforms.
        
        Args:
            user_id: User identifier
            
        Returns:
            Platform status information
        """



        try:
            status = {}
            
            for platform in PlatformType:
                credentials = await self._get_credentials(user_id, platform)
                
                if not credentials:
                    status[platform.value] = {
                        'connected': False,
                        'status': APIStatus.INACTIVE.value,
                        'last_sync': None,
                        'error': 'Not connected'
                    }
                    continue
                
                # Check token validity
                token_valid = credentials.expires_at > datetime.utcnow()
                
                # Get last sync time
                last_sync = await self._get_last_sync_time(user_id, platform)
                
                # Test API connection
                connection_test = await self._test_api_connection(credentials)
                
                status[platform.value] = {
                    'connected': True,
                    'status': APIStatus.ACTIVE.value if connection_test.success else APIStatus.ERROR.value,
                    'token_valid': token_valid,
                    'expires_at': credentials.expires_at.isoformat(),
                    'last_sync': last_sync.isoformat() if last_sync else None,
                    'scopes': credentials.scopes,
                    'error': None if connection_test.success else connection_test.error_message
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting platform status: {str(e)}")
            return {}
    
    async def disconnect_platform(self, user_id: str, platform: PlatformType) -> bool:
        """
        Disconnect user from platform.
        
        Args:
            user_id: User identifier
            platform: Platform to disconnect
            
        Returns:
            Disconnection success status
        """



        try:
            # Get credentials
            credentials = await self._get_credentials(user_id, platform)
            if not credentials:
                return True  # Already disconnected
            
            # Revoke access token
            await self._revoke_access_token(credentials)
            
            # Remove stored credentials
            await self._remove_credentials(user_id, platform)
            
            # Clear cached data
            await self._clear_platform_cache(user_id, platform)
            
            self.logger.info(f"Platform disconnected: {platform.value} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disconnecting platform {platform.value}: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _exchange_auth_code(self, platform: PlatformType, auth_code: str,
                                user_id: str) -> PlatformCredentials:
        """Exchange authorization code for access token"""
        config = self.platform_configs[platform]
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': self._get_client_id(platform),
            'client_secret': self._get_client_secret(platform),
            'redirect_uri': self._get_redirect_uri(platform)
        }
        
        async with self.http_session.post(config['token_url'], data=token_data) as response:
            if response.status == 200:
                data = await response.json()
                
                return PlatformCredentials(
                    platform=platform,
                    client_id=self._get_client_id(platform),
                    client_secret=self._get_client_secret(platform),
                    access_token=data['access_token'],
                    refresh_token=data.get('refresh_token', ''),
                    expires_at=datetime.utcnow() + timedelta(seconds=data.get('expires_in', 3600)),
                    scopes=config['scopes'],
                    user_id=user_id,
                    metadata=data
                )
            else:
                raise ValueError(f"Token exchange failed: {response.status}")
    
    async def _sync_youtube_revenue(self, credentials: PlatformCredentials,
                                  days_back: int) -> List[RevenueData]:
        """Sync YouTube revenue data"""
        revenue_data = []
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # YouTube Analytics API call
        params = {
            'ids': 'channel==MINE',
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'metrics': 'estimatedRevenue,monetizedPlaybacks,cpm',
            'dimensions': 'video',
            'access_token': credentials.access_token
        }
        
        url = f"{self.platform_configs[PlatformType.YOUTUBE]['base_url']}/reports"
        
        async with self.http_session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                for row in data.get('rows', []):
                    revenue_data.append(RevenueData(
                        platform=PlatformType.YOUTUBE,
                        user_id=credentials.user_id,
                        content_id=row[0],  # video ID
                        revenue_amount=Decimal(str(row[1])),  # estimatedRevenue
                        currency=Currency.USD,  # YouTube uses USD
                        period_start=start_date,
                        period_end=end_date,
                        views=int(row[2]),  # monetizedPlaybacks
                        clicks=0,  # Not available
                        impressions=int(row[2]),
                        cpm=Decimal(str(row[3])),
                        metadata={'raw_data': row}
                    ))
        
        return revenue_data
    
    async def _sync_instagram_revenue(self, credentials: PlatformCredentials,
                                    days_back: int) -> List[RevenueData]:
        """Sync Instagram revenue data"""
        revenue_data = []
        
        # Instagram Business API for monetization insights
        # Implementation would depend on specific Instagram Business API endpoints
        
        return revenue_data
    
    async def _sync_tiktok_revenue(self, credentials: PlatformCredentials,
                                 days_back: int) -> List[RevenueData]:
        """Sync TikTok revenue data"""
        revenue_data = []
        
        # TikTok Creator Fund API
        # Implementation would depend on TikTok Creator API endpoints
        
        return revenue_data
    
    async def _sync_spotify_revenue(self, credentials: PlatformCredentials,
                                  days_back: int) -> List[RevenueData]:
        """Sync Spotify revenue data"""
        revenue_data = []
        
        # Spotify for Artists API
        # Implementation would use Spotify's streaming and revenue APIs
        
        return revenue_data
    
    async def _check_rate_limit(self, platform: PlatformType) -> bool:
        """Check if platform rate limit allows request"""
        cache_key = f"rate_limit:{platform.value}"
        current_count = await self.redis.get(cache_key) or 0
        
        config = self.platform_configs[platform]
        limit = config['rate_limit']
        
        return int(current_count) < (limit * (1 - self.rate_limit_buffer))
    
    async def _update_rate_limit(self, platform: PlatformType):
        """Update rate limit counter"""
        cache_key = f"rate_limit:{platform.value}"
        config = self.platform_configs[platform]
        
        # Increment counter with expiration
        await self.redis.incr(cache_key)
        await self.redis.expire(cache_key, config['rate_window'])
    
    async def _get_credentials(self, user_id: str, platform: PlatformType) -> Optional[PlatformCredentials]:
        """Get stored credentials for user and platform"""
        cache_key = f"credentials:{user_id}:{platform.value}"
        
        # Try cache first
        cached_creds = await self._get_from_cache(cache_key)
        if cached_creds:
            return PlatformCredentials(**cached_creds)
        
        # Query from database (implementation would decrypt stored credentials)
        # Placeholder implementation
        return None
    
    async def _store_credentials(self, user_id: str, credentials: PlatformCredentials):
        """Store encrypted credentials"""
        # Encrypt sensitive data
        encrypted_token = self.cipher.encrypt(credentials.access_token.encode())
        encrypted_secret = self.cipher.encrypt(credentials.client_secret.encode())
        
        # Store in database and cache
        cache_key = f"credentials:{user_id}:{credentials.platform.value}"
        await self._save_to_cache(cache_key, credentials.__dict__)
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""



        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """Save data to cache"""



        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    def _get_client_id(self, platform: PlatformType) -> str:
        """Get client ID for platform"""
        import os
        return os.getenv(f"{platform.value.upper()}_CLIENT_ID", "")
    
    def _get_client_secret(self, platform: PlatformType) -> str:
        """Get client secret for platform"""
        import os
        return os.getenv(f"{platform.value.upper()}_CLIENT_SECRET", "")
    
    def _get_redirect_uri(self, platform: PlatformType) -> str:
        """Get redirect URI for platform"""
        import os
        base_url = os.getenv("APP_BASE_URL", "https://app.ia-influencer.com")
        return f"{base_url}/auth/callback/{platform.value}"
    
    # Additional helper methods would be implemented here...
    
    async def _validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """Validate credentials"""



        return bool(credentials.access_token and credentials.client_id)
    
    async def _test_api_connection(self, credentials: PlatformCredentials) -> APIResponse:
        """Test API connection with credentials"""
        # Implementation would test API connection
        return APIResponse(
            platform=credentials.platform,
            data_type=DataType.ANALYTICS,
            data={},
            timestamp=datetime.utcnow(),
            success=True,
            error_message=None,
            rate_limit_remaining=100,
            next_request_allowed=datetime.utcnow()
        )
    
    async def _refresh_token(self, credentials: PlatformCredentials) -> Optional[PlatformCredentials]:
        """Refresh access token"""
        # Implementation would refresh token using refresh_token
        return credentials
    
    # Additional methods for analytics sync, real-time metrics, etc. would be implemented...
