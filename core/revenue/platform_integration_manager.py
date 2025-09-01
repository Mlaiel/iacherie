"""Revenue Platform Integration Manager - Multi-Platform Revenue Management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLATFORM INTEGRATION MANAGER - ENTERPRISE EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Developed by Expert Team:
🎯 Lead Dev IA: Fahed Mlaiel (Advanced AI/ML Architecture)
🛠️  Backend Senior: System Architecture & Performance Optimization  
🤖 ML Engineer: Cross-Platform Revenue Optimization
🗄️  DBA: Advanced Data Management & Analytics
🔒 Security Expert: Enterprise-Grade Security & Encryption
🚀 Microservices: Scalable Distributed Architecture
🎵 Audio Expert: Audio Platform Integration
⚙️  DevOps: Production Infrastructure & Monitoring
🧠 IA Prompt Engineer: AI-Powered Platform Optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
import json
import aiohttp
import numpy as np
import pandas as pd

from ..utils.exceptions import PlatformIntegrationError
from ..utils.validators import validate_platform_data
from ..utils.cache import cache_platform_results
from ..analytics.metrics import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """
Supported platform types"""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM = "custom"


class PlatformStatus(Enum):
    """Platform integration status"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTHENTICATING = "authenticating"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class RevenueStreamType(Enum):
    """Revenue stream types by platform"""

    STREAMING_ROYALTIES = "streaming_royalties"
    AD_REVENUE = "ad_revenue"
    SUBSCRIPTION_FEES = "subscription_fees"
    MERCHANDISE_SALES = "merchandise_sales"
    LIVE_PERFORMANCE = "live_performance"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    TIP_DONATIONS = "tip_donations"
    LICENSING_FEES = "licensing_fees"
    PREMIUM_CONTENT = "premium_content"
    AFFILIATE_COMMISSIONS = "affiliate_commissions"


class DataSyncFrequency(Enum):
    """Data synchronization frequency"""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform_type: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    oauth_tokens: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        """
Check if credentials are expired"""
        if self.expires_at:
            return datetime.utcnow() >= self.expires_at
        return False


@dataclass
class PlatformConfiguration:
    """
Platform integration configuration"""
    platform_type: PlatformType
    name: str
    api_base_url: str
    revenue_endpoints: Dict[str, str]
    analytics_endpoints: Dict[str, str]
    authentication_type: str  # oauth2, api_key, bearer_token
    rate_limits: Dict[str, int]
    data_sync_frequency: DataSyncFrequency
    supported_metrics: List[str]
    revenue_streams: List[RevenueStreamType]
    currency: str = "USD"
    timezone: str = "UTC"


@dataclass
class PlatformRevenueData:
    """Standardized platform revenue data"""
    platform_type: PlatformType
    user_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    currency: str
    revenue_streams: Dict[str, Decimal]
    metrics: Dict[str, Any]
    raw_data: Dict[str, Any]
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformConnection:
    """
Platform connection information"""
    connection_id: str
    platform_type: PlatformType
    user_id: str
    credentials: PlatformCredentials
    configuration: PlatformConfiguration
    status: PlatformStatus
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    sync_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class BasePlatformConnector(ABC):
    """
Base class for platform connectors"""
    
    def __init__(self, config: PlatformConfiguration, credentials: PlatformCredentials):
        self.config = config
        self.credentials = credentials
        self.session = None
        self.rate_limiter = {}
        
    async def initialize(self) -> None:
        """
Initialize platform connector"""
        self.session = aiohttp.ClientSession()
        await self._setup_authentication()
    
    async def cleanup(self) -> None:
        """
Cleanup resources"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
Authenticate with platform"""
        pass
    
    @abstractmethod
    async def fetch_revenue_data(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PlatformRevenueData:
        """
Fetch revenue data from platform"""
        pass
    
    @abstractmethod
    async def fetch_analytics_data(
        self, 
        user_id: str, 
        metrics: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
Fetch analytics data from platform"""
        pass
    
    async def _setup_authentication(self) -> None:
        """
Setup authentication headers"""
        pass
    
    async def _check_rate_limits(self, endpoint: str) -> bool:
        """
Check rate limits for endpoint"""
        current_time = datetime.utcnow()
        endpoint_limit = self.config.rate_limits.get(endpoint, 100)
        
        if endpoint not in self.rate_limiter:
            self.rate_limiter[endpoint] = {
                'requests': 0,
                'window_start': current_time
            }
        
        # Reset window if needed (assuming 1-hour windows)
        if current_time - self.rate_limiter[endpoint]['window_start'] > timedelta(hours=1):
            self.rate_limiter[endpoint] = {
                'requests': 0,
                'window_start': current_time
            }
        
        if self.rate_limiter[endpoint]['requests'] >= endpoint_limit:
            return False
        
        self.rate_limiter[endpoint]['requests'] += 1
        return True


class SpotifyConnector(BasePlatformConnector):
    """
Spotify platform connector"""
    
    async def authenticate(self) -> bool:
        """
Authenticate with Spotify API"""
        try:
            if self.credentials.is_expired:
                # Refresh token if needed
                await self._refresh_token()
            
            # Test authentication
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                f"{self.config.api_base_url}/me",
                headers=headers
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Spotify authentication error: {e}")
            return False
    
    async def fetch_revenue_data(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PlatformRevenueData:
        """Fetch Spotify revenue data"""
        try:
            if not await self._check_rate_limits('revenue'):
                raise PlatformIntegrationError("Rate limit exceeded for Spotify revenue endpoint")
            
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Fetch artist revenue data
            revenue_endpoint = self.config.revenue_endpoints.get('artist_revenue')
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'market': 'all'
            }
            
            async with self.session.get(
                f"{self.config.api_base_url}{revenue_endpoint}",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_spotify_revenue_data(
                        data, user_id, start_date, end_date
                    )
                else:
                    raise PlatformIntegrationError(f"Spotify API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching Spotify revenue data: {e}")
            raise PlatformIntegrationError(f"Spotify revenue fetch failed: {e}")
    
    async def fetch_analytics_data(
        self, 
        user_id: str, 
        metrics: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch Spotify analytics data"""
        try:
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            analytics_data = {}
            
            # Fetch different analytics based on requested metrics
            if 'streams' in metrics:
                streams_data = await self._fetch_spotify_streams(
                    headers, start_date, end_date
                )
                analytics_data['streams'] = streams_data
            
            if 'listeners' in metrics:
                listeners_data = await self._fetch_spotify_listeners(
                    headers, start_date, end_date
                )
                analytics_data['listeners'] = listeners_data
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error fetching Spotify analytics: {e}")
            raise PlatformIntegrationError(f"Spotify analytics fetch failed: {e}")
    
    async def _process_spotify_revenue_data(
        self, 
        data: Dict[str, Any], 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PlatformRevenueData:
        """Process raw Spotify revenue data"""
        revenue_streams = {}
        total_revenue = Decimal('0')
        
        # Process streaming royalties
        if 'royalties' in data:
            streaming_revenue = Decimal(str(data['royalties'].get('total', 0)))
            revenue_streams[RevenueStreamType.STREAMING_ROYALTIES.value] = streaming_revenue
            total_revenue += streaming_revenue
        
        # Process additional revenue streams
        if 'merchandise' in data:
            merch_revenue = Decimal(str(data['merchandise'].get('total', 0)))
            revenue_streams[RevenueStreamType.MERCHANDISE_SALES.value] = merch_revenue
            total_revenue += merch_revenue
        
        # Extract metrics
        metrics = {
            'total_streams': data.get('total_streams', 0),
            'unique_listeners': data.get('unique_listeners', 0),
            'countries': data.get('countries', []),
            'top_tracks': data.get('top_tracks', [])
        }
        
        return PlatformRevenueData(
            platform_type=PlatformType.SPOTIFY,
            user_id=user_id,
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            currency=data.get('currency', 'USD'),
            revenue_streams=revenue_streams,
            metrics=metrics,
            raw_data=data
        )
    
    async def _refresh_token(self) -> None:
        """
Refresh Spotify access token"""
        # Implementation for token refresh
        pass
    
    async def _fetch_spotify_streams(
        self, 
        headers: Dict[str, str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
Fetch Spotify streams data"""
        # Implementation for fetching streams data
        return {}
    
    async def _fetch_spotify_listeners(
        self, 
        headers: Dict[str, str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
Fetch Spotify listeners data"""
        # Implementation for fetching listeners data
        return {}


class YouTubeConnector(BasePlatformConnector):
    """
YouTube platform connector"""
    
    async def authenticate(self) -> bool:
        """
Authenticate with YouTube API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test authentication with channel info
            async with self.session.get(
                f"{self.config.api_base_url}/channels",
                headers=headers,
                params={'part': 'id', 'mine': 'true'}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"YouTube authentication error: {e}")
            return False
    
    async def fetch_revenue_data(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PlatformRevenueData:
        """Fetch YouTube revenue data"""
        try:
            if not await self._check_rate_limits('revenue'):
                raise PlatformIntegrationError("Rate limit exceeded for YouTube revenue endpoint")
            
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Fetch YouTube Analytics revenue data
            params = {
                'ids': 'channel==MINE',
                'start-date': start_date.strftime('%Y-%m-%d'),
                'end-date': end_date.strftime('%Y-%m-%d'),
                'metrics': 'estimatedRevenue,monetizedPlaybacks,adImpressions',
                'dimensions': 'day'
            }
            
            async with self.session.get(
                f"{self.config.api_base_url}/reports",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_youtube_revenue_data(
                        data, user_id, start_date, end_date
                    )
                else:
                    raise PlatformIntegrationError(f"YouTube API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching YouTube revenue data: {e}")
            raise PlatformIntegrationError(f"YouTube revenue fetch failed: {e}")
    
    async def fetch_analytics_data(
        self, 
        user_id: str, 
        metrics: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch YouTube analytics data"""
        try:
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            analytics_data = {}
            
            # Fetch views and engagement metrics
            if 'views' in metrics:
                views_data = await self._fetch_youtube_views(
                    headers, start_date, end_date
                )
                analytics_data['views'] = views_data
            
            if 'engagement' in metrics:
                engagement_data = await self._fetch_youtube_engagement(
                    headers, start_date, end_date
                )
                analytics_data['engagement'] = engagement_data
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error fetching YouTube analytics: {e}")
            raise PlatformIntegrationError(f"YouTube analytics fetch failed: {e}")
    
    async def _process_youtube_revenue_data(
        self, 
        data: Dict[str, Any], 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PlatformRevenueData:
        """Process raw YouTube revenue data"""
        revenue_streams = {}
        total_revenue = Decimal('0')
        
        # Process ad revenue
        if 'rows' in data:
            ad_revenue = Decimal('0')
            for row in data['rows']:
                if len(row) > 1:  # Assuming revenue is in second column
                    ad_revenue += Decimal(str(row[1]))
            
            revenue_streams[RevenueStreamType.AD_REVENUE.value] = ad_revenue
            total_revenue += ad_revenue
        
        # Extract metrics
        metrics = {
            'monetized_playbacks': sum(row[2] if len(row) > 2 else 0 for row in data.get('rows', [])),
            'ad_impressions': sum(row[3] if len(row) > 3 else 0 for row in data.get('rows', [])),
            'total_views': 0  # Would be fetched separately
        }
        
        return PlatformRevenueData(
            platform_type=PlatformType.YOUTUBE,
            user_id=user_id,
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            currency='USD',  # YouTube typically reports in USD
            revenue_streams=revenue_streams,
            metrics=metrics,
            raw_data=data
        )
    
    async def _fetch_youtube_views(
        self, 
        headers: Dict[str, str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
Fetch YouTube views data"""
        # Implementation for fetching views data
        return {}
    
    async def _fetch_youtube_engagement(
        self, 
        headers: Dict[str, str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
Fetch YouTube engagement data"""
        # Implementation for fetching engagement data
        return {}


class InstagramConnector(BasePlatformConnector):
    """
Instagram platform connector"""
    
    async def authenticate(self) -> bool:
        """
Authenticate with Instagram API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test authentication with user info
            async with self.session.get(
                f"{self.config.api_base_url}/me",
                headers=headers,
                params={'fields': 'id,username'}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Instagram authentication error: {e}")
            return False
    
    async def fetch_revenue_data(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PlatformRevenueData:
        """Fetch Instagram revenue data"""
        try:
            if not await self._check_rate_limits('revenue'):
                raise PlatformIntegrationError("Rate limit exceeded for Instagram revenue endpoint")
            
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Instagram doesn't have direct revenue API, so we estimate from engagement
            # This would typically integrate with brand partnership platforms
            revenue_streams = {
                RevenueStreamType.BRAND_PARTNERSHIPS.value: Decimal('0'),
                RevenueStreamType.AFFILIATE_COMMISSIONS.value: Decimal('0')
            }
            
            # Fetch insights for revenue estimation
            insights_data = await self._fetch_instagram_insights(
                headers, start_date, end_date
            )
            
            return PlatformRevenueData(
                platform_type=PlatformType.INSTAGRAM,
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                total_revenue=Decimal('0'),  # Would be calculated from partnerships
                currency='USD',
                revenue_streams=revenue_streams,
                metrics=insights_data,
                raw_data=insights_data
            )
            
        except Exception as e:
            logger.error(f"Error fetching Instagram revenue data: {e}")
            raise PlatformIntegrationError(f"Instagram revenue fetch failed: {e}")
    
    async def fetch_analytics_data(
        self, 
        user_id: str, 
        metrics: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch Instagram analytics data"""
        try:
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            return await self._fetch_instagram_insights(headers, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error fetching Instagram analytics: {e}")
            raise PlatformIntegrationError(f"Instagram analytics fetch failed: {e}")
    
    async def _fetch_instagram_insights(
        self, 
        headers: Dict[str, str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch Instagram insights data"""
        # Implementation for fetching insights data
        return {
            'reach': 0,
            'impressions': 0,
            'engagement': 0,
            'followers': 0
        }


class PlatformIntegrationManager:
    """
Comprehensive platform integration management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.connections = {}
        self.connectors = {}
        self.platform_configs = {}
        self.metrics_collector = MetricsCollector()
        self.encryption_manager = EncryptionManager()
        
        # Initialize platform configurations
        self._initialize_platform_configs()
    
    async def initialize(self) -> None:
        """
Initialize platform integration manager"""
        try:
            await self._load_existing_connections()
            await self._setup_monitoring()
            
            logger.info("Platform integration manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing platform integration manager: {e}")
            raise
    
    def _initialize_platform_configs(self) -> None:
        """Initialize platform configurations"""
        # Spotify configuration
        self.platform_configs[PlatformType.SPOTIFY] = PlatformConfiguration(
            platform_type=PlatformType.SPOTIFY,
            name="Spotify for Artists",
            api_base_url="https://api.spotify.com/v1",
            revenue_endpoints={
                'artist_revenue': '/artists/{artist_id}/revenue',
                'royalties': '/artists/{artist_id}/royalties'
            },
            analytics_endpoints={
                'streams': '/artists/{artist_id}/stats/streams',
                'listeners': '/artists/{artist_id}/stats/listeners'
            },
            authentication_type="oauth2",
            rate_limits={'revenue': 100, 'analytics': 500},
            data_sync_frequency=DataSyncFrequency.DAILY,
            supported_metrics=['streams', 'listeners', 'revenue', 'countries'],
            revenue_streams=[RevenueStreamType.STREAMING_ROYALTIES, RevenueStreamType.MERCHANDISE_SALES]
        )
        
        # YouTube configuration
        self.platform_configs[PlatformType.YOUTUBE] = PlatformConfiguration(
            platform_type=PlatformType.YOUTUBE,
            name="YouTube Analytics",
            api_base_url="https://youtubeanalytics.googleapis.com/v2",
            revenue_endpoints={
                'channel_revenue': '/reports'
            },
            analytics_endpoints={
                'views': '/reports',
                'engagement': '/reports'
            },
            authentication_type="oauth2",
            rate_limits={'revenue': 100, 'analytics': 1000},
            data_sync_frequency=DataSyncFrequency.DAILY,
            supported_metrics=['views', 'revenue', 'engagement', 'subscribers'],
            revenue_streams=[RevenueStreamType.AD_REVENUE, RevenueStreamType.BRAND_PARTNERSHIPS]
        )
        
        # Instagram configuration
        self.platform_configs[PlatformType.INSTAGRAM] = PlatformConfiguration(
            platform_type=PlatformType.INSTAGRAM,
            name="Instagram Business",
            api_base_url="https://graph.facebook.com/v19.0",
            revenue_endpoints={},  # No direct revenue API
            analytics_endpoints={
                'insights': '/{user_id}/insights'
            },
            authentication_type="oauth2",
            rate_limits={'analytics': 200},
            data_sync_frequency=DataSyncFrequency.DAILY,
            supported_metrics=['reach', 'impressions', 'engagement'],
            revenue_streams=[RevenueStreamType.BRAND_PARTNERSHIPS, RevenueStreamType.AFFILIATE_COMMISSIONS]
        )
    
    async def connect_platform(
        self,
        user_id: str,
        platform_type: PlatformType,
        credentials: Dict[str, Any]
    ) -> str:
        """Connect to a platform"""
        try:
            connection_id = str(uuid.uuid4())
            
            # Create credentials object
            platform_credentials = PlatformCredentials(
                platform_type=platform_type,
                **credentials
            )
            
            # Get platform configuration
            if platform_type not in self.platform_configs:
                raise PlatformIntegrationError(f"Platform {platform_type.value} not supported")
            
            platform_config = self.platform_configs[platform_type]
            
            # Create connector
            connector = self._create_connector(platform_type, platform_config, platform_credentials)
            await connector.initialize()
            
            # Test connection
            is_authenticated = await connector.authenticate()
            if not is_authenticated:
                raise PlatformIntegrationError(f"Authentication failed for {platform_type.value}")
            
            # Create connection record
            connection = PlatformConnection(
                connection_id=connection_id,
                platform_type=platform_type,
                user_id=user_id,
                credentials=platform_credentials,
                configuration=platform_config,
                status=PlatformStatus.CONNECTED,
                last_sync=datetime.utcnow()
            )
            
            self.connections[connection_id] = connection
            self.connectors[connection_id] = connector
            
            logger.info(f"Platform connected: {platform_type.value} for user {user_id}")
            
            return connection_id
            
        except Exception as e:
            logger.error(f"Error connecting platform: {e}")
            raise PlatformIntegrationError(f"Platform connection failed: {e}")
    
    def _create_connector(
        self,
        platform_type: PlatformType,
        config: PlatformConfiguration,
        credentials: PlatformCredentials
    ) -> BasePlatformConnector:
        """Create platform-specific connector"""
        if platform_type == PlatformType.SPOTIFY:
            return SpotifyConnector(config, credentials)
        elif platform_type == PlatformType.YOUTUBE:
            return YouTubeConnector(config, credentials)
        elif platform_type == PlatformType.INSTAGRAM:
            return InstagramConnector(config, credentials)
        else:
            raise PlatformIntegrationError(f"Connector not implemented for {platform_type.value}")
    
    async def sync_platform_data(
        self,
        connection_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync data from platform"""
        try:
            if connection_id not in self.connections:
                raise PlatformIntegrationError(f"Connection not found: {connection_id}")
            
            connection = self.connections[connection_id]
            connector = self.connectors[connection_id]
            
            # Default date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Check connection status
            if connection.status != PlatformStatus.CONNECTED:
                raise PlatformIntegrationError(f"Platform not connected: {connection.status.value}")
            
            # Fetch revenue data
            revenue_data = await connector.fetch_revenue_data(
                connection.user_id, start_date, end_date
            )
            
            # Fetch analytics data
            analytics_data = await connector.fetch_analytics_data(
                connection.user_id, 
                connection.configuration.supported_metrics,
                start_date, 
                end_date
            )
            
            # Update connection
            connection.last_sync = datetime.utcnow()
            connection.sync_history.append({
                'timestamp': datetime.utcnow(),
                'status': 'success',
                'revenue_amount': str(revenue_data.total_revenue),
                'metrics_count': len(analytics_data)
            })
            
            # Record metrics
            await self._record_sync_metrics(connection_id, revenue_data, analytics_data)
            
            return {
                'connection_id': connection_id,
                'platform': connection.platform_type.value,
                'sync_timestamp': datetime.utcnow().isoformat(),
                'revenue_data': {
                    'total_revenue': str(revenue_data.total_revenue),
                    'currency': revenue_data.currency,
                    'revenue_streams': {k: str(v) for k, v in revenue_data.revenue_streams.items()},
                    'period': {
                        'start': revenue_data.period_start.isoformat(),
                        'end': revenue_data.period_end.isoformat()
                    }
                },
                'analytics_data': analytics_data,
                'metrics': revenue_data.metrics
            }
            
        except Exception as e:
            logger.error(f"Error syncing platform data: {e}")
            
            # Update connection with error
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                connection.status = PlatformStatus.ERROR
                connection.error_message = str(e)
                connection.sync_history.append({
                    'timestamp': datetime.utcnow(),
                    'status': 'error',
                    'error': str(e)
                })
            
            raise PlatformIntegrationError(f"Platform sync failed: {e}")
    
    async def sync_all_platforms(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync data from all connected platforms"""
        try:
            results = {}
            
            # Filter connections by user if specified
            connections_to_sync = []
            for connection_id, connection in self.connections.items():
                if user_id is None or connection.user_id == user_id:
                    if connection.status == PlatformStatus.CONNECTED:
                        connections_to_sync.append(connection_id)
            
            # Sync all connections concurrently
            sync_tasks = []
            for connection_id in connections_to_sync:
                task = asyncio.create_task(
                    self.sync_platform_data(connection_id, start_date, end_date)
                )
                sync_tasks.append((connection_id, task))
            
            # Wait for all syncs to complete
            for connection_id, task in sync_tasks:
                try:
                    result = await task
                    results[connection_id] = result
                except Exception as e:
                    results[connection_id] = {'error': str(e)}
            
            # Generate summary
            successful_syncs = len([r for r in results.values() if 'error' not in r])
            total_revenue = sum(
                Decimal(r['revenue_data']['total_revenue']) 
                for r in results.values() 
                if 'error' not in r and 'revenue_data' in r
            )
            
            return {
                'sync_summary': {
                    'total_platforms': len(connections_to_sync),
                    'successful_syncs': successful_syncs,
                    'failed_syncs': len(connections_to_sync) - successful_syncs,
                    'total_revenue': str(total_revenue),
                    'sync_timestamp': datetime.utcnow().isoformat()
                },
                'platform_results': results
            }
            
        except Exception as e:
            logger.error(f"Error syncing all platforms: {e}")
            raise PlatformIntegrationError(f"Bulk platform sync failed: {e}")
    
    async def get_platform_analytics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive platform analytics"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get user's connections
            user_connections = [
                conn for conn in self.connections.values() 
                if conn.user_id == user_id and conn.status == PlatformStatus.CONNECTED
            ]
            
            if not user_connections:
                return {'message': 'No connected platforms found'}
            
            # Sync latest data
            sync_results = await self.sync_all_platforms(user_id, start_date, end_date)
            
            # Aggregate analytics
            total_revenue = Decimal('0')
            platform_breakdown = {}
            revenue_streams = {}
            
            for connection_id, result in sync_results['platform_results'].items():
                if 'error' in result:
                    continue
                
                platform = result['platform']
                revenue_data = result['revenue_data']
                
                platform_revenue = Decimal(revenue_data['total_revenue'])
                total_revenue += platform_revenue
                
                platform_breakdown[platform] = {
                    'revenue': str(platform_revenue),
                    'currency': revenue_data['currency'],
                    'revenue_streams': revenue_data['revenue_streams']
                }
                
                # Aggregate revenue streams
                for stream, amount in revenue_data['revenue_streams'].items():
                    if stream not in revenue_streams:
                        revenue_streams[stream] = Decimal('0')
                    revenue_streams[stream] += Decimal(amount)
            
            # Calculate insights
            insights = await self._generate_platform_insights(
                platform_breakdown, revenue_streams, period_days
            )
            
            return {
                'user_id': user_id,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': period_days
                },
                'summary': {
                    'total_revenue': str(total_revenue),
                    'connected_platforms': len(user_connections),
                    'active_revenue_streams': len(revenue_streams),
                    'top_platform': max(
                        platform_breakdown.items(), 
                        key=lambda x: Decimal(x[1]['revenue'])
                    )[0] if platform_breakdown else None
                },
                'platform_breakdown': platform_breakdown,
                'revenue_streams': {k: str(v) for k, v in revenue_streams.items()},
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating platform analytics: {e}")
            raise PlatformIntegrationError(f"Platform analytics generation failed: {e}")
    
    async def _generate_platform_insights(
        self,
        platform_breakdown: Dict[str, Any],
        revenue_streams: Dict[str, Decimal],
        period_days: int
    ) -> List[Dict[str, Any]]:
        """Generate insights from platform data"""
        insights = []
        
        # Platform diversification insight
        if len(platform_breakdown) == 1:
            insights.append({
                'type': 'diversification',
                'title': 'Platform Diversification Opportunity',
                'description': 'You are only earning from one platform. Consider diversifying to reduce risk.',
                'priority': 'high',
                'recommendation': 'Connect additional platforms to diversify your revenue streams'
            })
        
        # Revenue stream analysis
        if len(revenue_streams) > 1:
            top_stream = max(revenue_streams.items(), key=lambda x: x[1])
            insights.append({
                'type': 'revenue_stream',
                'title': f'Top Revenue Stream: {top_stream[0].replace("_", " ").title()}',
                'description': f'Your primary revenue source generates {(top_stream[1] / sum(revenue_streams.values()) * 100):.1f}% of total revenue',
                'priority': 'medium',
                'recommendation': 'Continue optimizing your top-performing revenue stream'
            })
        
        # Platform performance comparison
        if len(platform_breakdown) > 1:
            revenues = [(platform, Decimal(data['revenue'])) for platform, data in platform_breakdown.items()]
            revenues.sort(key=lambda x: x[1], reverse=True)
            
            top_platform = revenues[0]
            second_platform = revenues[1] if len(revenues) > 1 else None
            
            if second_platform and top_platform[1] > second_platform[1] * 2:
                insights.append({
                    'type': 'platform_performance',
                    'title': f'{top_platform[0]} Significantly Outperforming',
                    'description': f'{top_platform[0]} generates {(top_platform[1] / second_platform[1]):.1f}x more revenue than {second_platform[0]}',
                    'priority': 'medium',
                    'recommendation': f'Analyze {top_platform[0]} strategies and apply them to other platforms'
                })
        
        return insights
    
    async def disconnect_platform(self, connection_id: str) -> bool:
        """Disconnect from platform"""
        try:
            if connection_id not in self.connections:
                raise PlatformIntegrationError(f"Connection not found: {connection_id}")
            
            connection = self.connections[connection_id]
            
            # Cleanup connector
            if connection_id in self.connectors:
                connector = self.connectors[connection_id]
                await connector.cleanup()
                del self.connectors[connection_id]
            
            # Update connection status
            connection.status = PlatformStatus.DISCONNECTED
            
            logger.info(f"Platform disconnected: {connection.platform_type.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting platform: {e}")
            raise PlatformIntegrationError(f"Platform disconnect failed: {e}")
    
    async def _load_existing_connections(self) -> None:
        """Load existing platform connections"""
        # In production, load from database
        pass
    
    async def _setup_monitoring(self) -> None:
        """
Setup platform monitoring"""
        pass
    
    async def _record_sync_metrics(
        self,
        connection_id: str,
        revenue_data: PlatformRevenueData,
        analytics_data: Dict[str, Any]
    ) -> None:
        """
Record sync metrics for monitoring"""
        metrics = {
            'connection_id': connection_id,
            'platform': revenue_data.platform_type.value,
            'revenue_amount': str(revenue_data.total_revenue),
            'currency': revenue_data.currency,
            'metrics_count': len(analytics_data),
            'sync_timestamp': datetime.utcnow().isoformat()
        }
        
        await self.metrics_collector.record_platform_sync(metrics)


def create_platform_integration_manager(config: Optional[Dict[str, Any]] = None) -> PlatformIntegrationManager:
    """
Factory function to create platform integration manager"""
    return PlatformIntegrationManager(config)
