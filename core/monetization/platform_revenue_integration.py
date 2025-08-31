"""
Platform Revenue Integration System
Multi-platform revenue tracking and synchronization for content creators

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import aiohttp
import pandas as pd
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ...database.models import User, RevenueRecord
from ...core.security.encryption import SecurityManager


class PlatformType(Enum):
    """Supported content platforms"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    BANDCAMP = "bandcamp"


class RevenueType(Enum):
    """Types of revenue streams"""
    STREAMING = "streaming"
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    SUBSCRIPTION = "subscription"
    DONATION = "donation"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    PERFORMANCE = "performance"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform: PlatformType
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if credentials are valid"""
        if self.expires_at and self.expires_at < datetime.now():
            return False
        
        required_fields = {
            PlatformType.SPOTIFY: ['access_token', 'refresh_token'],
            PlatformType.YOUTUBE: ['api_key', 'access_token'],
            PlatformType.INSTAGRAM: ['access_token'],
            PlatformType.TIKTOK: ['access_token'],
        }
        
        required = required_fields.get(self.platform, ['api_key'])
        return all(getattr(self, field) for field in required)


@dataclass
class RevenueData:
    """Platform revenue data"""
    platform: PlatformType
    revenue_type: RevenueType
    amount: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    views: Optional[int] = None
    streams: Optional[int] = None
    engagement_rate: Optional[float] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "platform": self.platform.value,
            "revenue_type": self.revenue_type.value,
            "amount": float(self.amount),
            "currency": self.currency,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "views": self.views,
            "streams": self.streams,
            "engagement_rate": self.engagement_rate,
            "content_id": self.content_id,
            "metadata": self.metadata
        }


class SpotifyRevenueIntegration:
    """Spotify Artists API integration"""
    
    BASE_URL = "https://api.spotify.com/v1"
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
    
    async def get_artist_analytics(
        self,
        artist_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Get Spotify artist analytics and revenue data"""



        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.credentials.access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Get streaming data
                streams_url = f"{self.BASE_URL}/me/player/recently-played"
                async with session.get(streams_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_spotify_data(data, start_date, end_date)
                    else:
                        self.logger.error(f"Spotify API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Spotify integration failed: {str(e)}")
            return []
    
    async def _process_spotify_data(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Process Spotify API response"""
        revenue_records = []
        
        # Calculate estimated revenue from streams
        # Spotify pays approximately $0.003-$0.005 per stream
        avg_per_stream = Decimal("0.004")
        
        streams = len(data.get('items', []))
        estimated_revenue = streams * avg_per_stream
        
        revenue_data = RevenueData(
            platform=PlatformType.SPOTIFY,
            revenue_type=RevenueType.STREAMING,
            amount=estimated_revenue,
            currency="USD",
            period_start=start_date,
            period_end=end_date,
            streams=streams,
            metadata={
                "api_source": "spotify_artists",
                "calculation_method": "estimated",
                "per_stream_rate": float(avg_per_stream)
            }
        )
        
        revenue_records.append(revenue_data)
        return revenue_records


class YouTubeRevenueIntegration:
    """YouTube Analytics API integration"""
    
    BASE_URL = "https://youtubeanalytics.googleapis.com/v2"
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
    
    async def get_channel_revenue(
        self,
        channel_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Get YouTube channel revenue data"""



        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.credentials.access_token}',
                    'Accept': 'application/json'
                }
                
                # Get revenue data
                params = {
                    'ids': f'channel=={channel_id}',
                    'startDate': start_date.strftime('%Y-%m-%d'),
                    'endDate': end_date.strftime('%Y-%m-%d'),
                    'metrics': 'estimatedRevenue,views,subscribersGained',
                    'dimensions': 'day'
                }
                
                url = f"{self.BASE_URL}/reports"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_youtube_data(data, start_date, end_date)
                    else:
                        self.logger.error(f"YouTube API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"YouTube integration failed: {str(e)}")
            return []
    
    async def _process_youtube_data(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Process YouTube Analytics response"""
        revenue_records = []
        
        rows = data.get('rows', [])
        total_revenue = Decimal("0")
        total_views = 0
        
        for row in rows:
            if len(row) >= 3:
                revenue = Decimal(str(row[1])) if row[1] else Decimal("0")
                views = int(row[2]) if row[2] else 0
                
                total_revenue += revenue
                total_views += views
        
        if total_revenue > 0:
            revenue_data = RevenueData(
                platform=PlatformType.YOUTUBE,
                revenue_type=RevenueType.ADVERTISING,
                amount=total_revenue,
                currency="USD",
                period_start=start_date,
                period_end=end_date,
                views=total_views,
                metadata={
                    "api_source": "youtube_analytics",
                    "data_points": len(rows)
                }
            )
            revenue_records.append(revenue_data)
        
        return revenue_records


class InstagramRevenueIntegration:
    """Instagram Creator API integration"""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
    
    async def get_creator_insights(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Get Instagram creator insights and estimated revenue"""



        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'access_token': self.credentials.access_token,
                    'metric': 'impressions,reach,profile_views',
                    'period': 'day',
                    'since': int(start_date.timestamp()),
                    'until': int(end_date.timestamp())
                }
                
                url = f"{self.BASE_URL}/{user_id}/insights"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_instagram_data(data, start_date, end_date)
                    else:
                        self.logger.error(f"Instagram API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Instagram integration failed: {str(e)}")
            return []
    
    async def _process_instagram_data(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Process Instagram insights data"""
        revenue_records = []
        
        insights = data.get('data', [])
        total_impressions = 0
        total_reach = 0
        
        for insight in insights:
            if insight.get('name') == 'impressions':
                values = insight.get('values', [])
                total_impressions = sum(v.get('value', 0) for v in values)
            elif insight.get('name') == 'reach':
                values = insight.get('values', [])
                total_reach = sum(v.get('value', 0) for v in values)
        
        # Estimate revenue based on engagement
        # Instagram creators typically earn $5-10 per 1000 engaged followers
        estimated_cpm = Decimal("7.50")  # USD per 1000 impressions
        estimated_revenue = (total_impressions / 1000) * estimated_cpm
        
        if estimated_revenue > 0:
            revenue_data = RevenueData(
                platform=PlatformType.INSTAGRAM,
                revenue_type=RevenueType.SPONSORSHIP,
                amount=estimated_revenue,
                currency="USD",
                period_start=start_date,
                period_end=end_date,
                views=total_impressions,
                metadata={
                    "api_source": "instagram_insights",
                    "impressions": total_impressions,
                    "reach": total_reach,
                    "estimated_cpm": float(estimated_cpm)
                }
            )
            revenue_records.append(revenue_data)
        
        return revenue_records


class TikTokRevenueIntegration:
    """TikTok Creator API integration"""
    
    BASE_URL = "https://open-api.tiktok.com/v1.3"
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
    
    async def get_creator_revenue(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Get TikTok creator revenue data"""



        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.credentials.access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Get video analytics
                params = {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'fields': 'video_views,likes,shares,comments'
                }
                
                url = f"{self.BASE_URL}/creator/video/analytics"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_tiktok_data(data, start_date, end_date)
                    else:
                        self.logger.error(f"TikTok API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"TikTok integration failed: {str(e)}")
            return []
    
    async def _process_tiktok_data(
        self,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueData]:
        """Process TikTok analytics data"""
        revenue_records = []
        
        videos = data.get('data', {}).get('videos', [])
        total_views = sum(video.get('video_views', 0) for video in videos)
        total_likes = sum(video.get('likes', 0) for video in videos)
        
        # TikTok Creator Fund pays approximately $0.02-0.04 per 1000 views
        avg_per_1k_views = Decimal("0.03")
        estimated_revenue = (total_views / 1000) * avg_per_1k_views
        
        if estimated_revenue > 0:
            engagement_rate = (total_likes / total_views) * 100 if total_views > 0 else 0
            
            revenue_data = RevenueData(
                platform=PlatformType.TIKTOK,
                revenue_type=RevenueType.ADVERTISING,
                amount=estimated_revenue,
                currency="USD",
                period_start=start_date,
                period_end=end_date,
                views=total_views,
                engagement_rate=engagement_rate,
                metadata={
                    "api_source": "tiktok_creator",
                    "total_likes": total_likes,
                    "video_count": len(videos),
                    "per_1k_rate": float(avg_per_1k_views)
                }
            )
            revenue_records.append(revenue_data)
        
        return revenue_records


class PlatformRevenueAggregator:
    """Aggregates revenue data from all platforms"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
        self.integrations = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform integrations
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize platform integration classes"""
        self.integration_classes = {
            PlatformType.SPOTIFY: SpotifyRevenueIntegration,
            PlatformType.YOUTUBE: YouTubeRevenueIntegration,
            PlatformType.INSTAGRAM: InstagramRevenueIntegration,
            PlatformType.TIKTOK: TikTokRevenueIntegration,
        }
    
    async def add_platform_credentials(
        self,
        user_id: int,
        credentials: PlatformCredentials,
        session: AsyncSession
    ) -> bool:
        """Add platform credentials for user"""



        try:
            if not credentials.is_valid():
                raise ValueError(f"Invalid credentials for {credentials.platform.value}")
            
            # Encrypt sensitive data
            encrypted_credentials = await self.security_manager.encrypt_credentials(
                credentials.__dict__
            )
            
            # Store in user settings (implementation depends on user model)
            # This would typically be stored in a separate credentials table
            
            # Initialize integration
            integration_class = self.integration_classes.get(credentials.platform)
            if integration_class:
                self.integrations[f"{user_id}_{credentials.platform.value}"] = \
                    integration_class(credentials)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add credentials: {str(e)}")
            return False
    
    async def sync_all_platforms(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> List[RevenueData]:
        """Sync revenue data from all connected platforms"""
        all_revenue_data = []
        
        try:
            # Get user's connected platforms
            user_integrations = {
                key: integration for key, integration in self.integrations.items()
                if key.startswith(f"{user_id}_")
            }
            
            # Run platform syncs concurrently
            tasks = []
            for platform_key, integration in user_integrations.items():
                platform = platform_key.split('_')[1]
                
                if platform == PlatformType.SPOTIFY.value:
                    task = integration.get_artist_analytics("", start_date, end_date)
                elif platform == PlatformType.YOUTUBE.value:
                    task = integration.get_channel_revenue("", start_date, end_date)
                elif platform == PlatformType.INSTAGRAM.value:
                    task = integration.get_creator_insights("", start_date, end_date)
                elif platform == PlatformType.TIKTOK.value:
                    task = integration.get_creator_revenue("", start_date, end_date)
                else:
                    continue
                
                tasks.append(task)
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, list):
                    all_revenue_data.extend(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Platform sync failed: {str(result)}")
            
            # Store in database
            await self._store_revenue_data(user_id, all_revenue_data, session)
            
            return all_revenue_data
            
        except Exception as e:
            self.logger.error(f"Platform sync failed: {str(e)}")
            return []
    
    async def _store_revenue_data(
        self,
        user_id: int,
        revenue_data: List[RevenueData],
        session: AsyncSession
    ) -> None:
        """Store revenue data in database"""



        try:
            for data in revenue_data:
                # Check if record already exists
                existing = await session.execute(
                    select(RevenueRecord).where(
                        RevenueRecord.user_id == user_id,
                        RevenueRecord.platform == data.platform.value,
                        RevenueRecord.period_start == data.period_start,
                        RevenueRecord.period_end == data.period_end
                    )
                )
                
                if not existing.scalar_one_or_none():
                    # Create new revenue record
                    record = RevenueRecord(
                        user_id=user_id,
                        platform=data.platform.value,
                        revenue_type=data.revenue_type.value,
                        amount=data.amount,
                        currency=data.currency,
                        period_start=data.period_start,
                        period_end=data.period_end,
                        views=data.views,
                        streams=data.streams,
                        engagement_rate=data.engagement_rate,
                        content_id=data.content_id,
                        metadata=data.metadata
                    )
                    
                    session.add(record)
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Failed to store revenue data: {str(e)}")
            raise
    
    async def get_total_revenue(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get total revenue across all platforms"""



        try:
            result = await session.execute(
                select(
                    RevenueRecord.platform,
                    RevenueRecord.currency,
                    func.sum(RevenueRecord.amount).label('total_amount'),
                    func.sum(RevenueRecord.views).label('total_views'),
                    func.sum(RevenueRecord.streams).label('total_streams')
                ).where(
                    RevenueRecord.user_id == user_id,
                    RevenueRecord.period_start >= start_date,
                    RevenueRecord.period_end <= end_date
                ).group_by(
                    RevenueRecord.platform,
                    RevenueRecord.currency
                )
            )
            
            revenue_summary = {
                'total_revenue': Decimal("0"),
                'by_platform': {},
                'by_currency': {},
                'total_views': 0,
                'total_streams': 0
            }
            
            for row in result:
                platform = row.platform
                currency = row.currency
                amount = Decimal(str(row.total_amount or 0))
                views = int(row.total_views or 0)
                streams = int(row.total_streams or 0)
                
                # Platform breakdown
                if platform not in revenue_summary['by_platform']:
                    revenue_summary['by_platform'][platform] = Decimal("0")
                revenue_summary['by_platform'][platform] += amount
                
                # Currency breakdown
                if currency not in revenue_summary['by_currency']:
                    revenue_summary['by_currency'][currency] = Decimal("0")
                revenue_summary['by_currency'][currency] += amount
                
                # Totals
                revenue_summary['total_revenue'] += amount
                revenue_summary['total_views'] += views
                revenue_summary['total_streams'] += streams
            
            # Convert Decimal to float for JSON serialization
            revenue_summary['total_revenue'] = float(revenue_summary['total_revenue'])
            revenue_summary['by_platform'] = {
                k: float(v) for k, v in revenue_summary['by_platform'].items()
            }
            revenue_summary['by_currency'] = {
                k: float(v) for k, v in revenue_summary['by_currency'].items()
            }
            
            return revenue_summary
            
        except Exception as e:
            self.logger.error(f"Failed to get total revenue: {str(e)}")
            return {
                'total_revenue': 0,
                'by_platform': {},
                'by_currency': {},
                'total_views': 0,
                'total_streams': 0
            }


class RevenueSync:
    """Automated revenue synchronization service"""
    
    def __init__(self, aggregator: PlatformRevenueAggregator):
        self.aggregator = aggregator
        self.logger = logging.getLogger(__name__)
        self.sync_running = False
    
    async def start_automated_sync(self, interval_hours: int = 24):
        """Start automated revenue synchronization"""
        self.sync_running = True
        
        while self.sync_running:
            try:
                await self._sync_all_users()
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                
            except Exception as e:
                self.logger.error(f"Automated sync failed: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    def stop_automated_sync(self):
        """Stop automated revenue synchronization"""
        self.sync_running = False
    
    async def _sync_all_users(self):
        """Sync revenue for all users with connected platforms"""
        # This would get all users from database and sync their platforms
        # Implementation depends on your user management system
        pass
