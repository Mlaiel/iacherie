"""Platform Stream Connector for IA Influencer Agent Platform
=========================================================

Multi-platform streaming connector for real-time data synchronization
across social media, music, and content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...utils.logging import get_logger
from ...integrations.spotify import SpotifyClient
from ...integrations.youtube import YouTubeClient
from ...integrations.instagram import InstagramClient
from ...integrations.tiktok import TikTokClient
from .manager import StreamEvent

logger = get_logger(__name__)
settings = get_settings()


class PlatformType(str, Enum):
    """
Supported platform types"""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"


class SyncMode(str, Enum):
    """Data synchronization modes"""

    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"


class DataType(str, Enum):
    """Platform data types"""

    ANALYTICS = "analytics"
    CONTENT = "content"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    FOLLOWERS = "followers"
    STREAMS = "streams"
    COMMENTS = "comments"
    SHARES = "shares"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)


@dataclass
class SyncConfig:
    """
Platform synchronization configuration"""
    platform: PlatformType
    data_types: List[DataType]
    sync_mode: SyncMode
    interval_seconds: int = 300  # 5 minutes default
    enabled: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)
    mapping_rules: Dict[str, str] = field(default_factory=dict)


class PlatformData(BaseModel):
    """
Normalized platform data structure"""
    platform: PlatformType = Field(description="Source platform")
    data_type: DataType = Field(description="Type of data")
    user_id: str = Field(description="Platform user identifier")
    content_id: Optional[str] = Field(default=None, description="Content identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Platform metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw platform response")


class PlatformConnector(ABC):
    """Abstract base class for platform connectors"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.platform = credentials.platform
        self.client = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """
Initialize platform connection"""
        pass
        
    @abstractmethod
    async def fetch_analytics(self, user_id: str, **kwargs) -> List[PlatformData]:
        """
Fetch analytics data"""
        pass
        
    @abstractmethod
    async def fetch_content(self, user_id: str, **kwargs) -> List[PlatformData]:
        """
Fetch content data"""
        pass
        
    @abstractmethod
    async def fetch_engagement(self, user_id: str, **kwargs) -> List[PlatformData]:
        """
Fetch engagement data"""
        pass
        
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
Validate platform credentials"""
        pass
        
    async def refresh_tokens(self) -> bool:
        """
Refresh authentication tokens"""
        return True


class SpotifyConnector(PlatformConnector):
    """
Spotify platform connector"""
    
    async def initialize(self) -> bool:
        try:
            self.client = SpotifyClient(
                client_id=self.credentials.api_key,
                client_secret=self.credentials.api_secret,
                access_token=self.credentials.access_token
            )
            return await self.client.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize Spotify connector: {e}")
            return False
            
    async def fetch_analytics(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            analytics = await self.client.get_artist_analytics(user_id)
            
            return [PlatformData(
                platform=PlatformType.SPOTIFY,
                data_type=DataType.ANALYTICS,
                user_id=user_id,
                metrics={
                    "monthly_listeners": analytics.get("monthly_listeners", 0),
                    "total_streams": analytics.get("total_streams", 0),
                    "countries": analytics.get("top_countries", []),
                    "cities": analytics.get("top_cities", [])
                },
                raw_data=analytics
            )]
        except Exception as e:
            logger.error(f"Failed to fetch Spotify analytics: {e}")
            return []
            
    async def fetch_content(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            tracks = await self.client.get_artist_tracks(user_id)
            
            content_data = []
            for track in tracks:
                content_data.append(PlatformData(
                    platform=PlatformType.SPOTIFY,
                    data_type=DataType.CONTENT,
                    user_id=user_id,
                    content_id=track.get("id"),
                    metrics={
                        "popularity": track.get("popularity", 0),
                        "duration_ms": track.get("duration_ms", 0),
                        "explicit": track.get("explicit", False)
                    },
                    metadata={
                        "name": track.get("name"),
                        "album": track.get("album", {}).get("name"),
                        "release_date": track.get("album", {}).get("release_date")
                    },
                    raw_data=track
                ))
                
            return content_data
        except Exception as e:
            logger.error(f"Failed to fetch Spotify content: {e}")
            return []
            
    async def fetch_engagement(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            # Spotify doesn't provide direct engagement metrics
            # This would integrate with Spotify for Artists API
            return []
        except Exception as e:
            logger.error(f"Failed to fetch Spotify engagement: {e}")
            return []
            
    async def validate_credentials(self) -> bool:
        try:
            return await self.client.validate_token()
        except Exception as e:
            logger.error(f"Failed to validate Spotify credentials: {e}")
            return False


class YouTubeConnector(PlatformConnector):
    """YouTube platform connector"""
    
    async def initialize(self) -> bool:
        try:
            self.client = YouTubeClient(
                api_key=self.credentials.api_key,
                access_token=self.credentials.access_token
            )
            return await self.client.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize YouTube connector: {e}")
            return False
            
    async def fetch_analytics(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            analytics = await self.client.get_channel_analytics(user_id)
            
            return [PlatformData(
                platform=PlatformType.YOUTUBE,
                data_type=DataType.ANALYTICS,
                user_id=user_id,
                metrics={
                    "subscriber_count": analytics.get("subscriberCount", 0),
                    "video_count": analytics.get("videoCount", 0),
                    "view_count": analytics.get("viewCount", 0),
                    "estimated_minutes_watched": analytics.get("estimatedMinutesWatched", 0)
                },
                raw_data=analytics
            )]
        except Exception as e:
            logger.error(f"Failed to fetch YouTube analytics: {e}")
            return []
            
    async def fetch_content(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            videos = await self.client.get_channel_videos(user_id)
            
            content_data = []
            for video in videos:
                content_data.append(PlatformData(
                    platform=PlatformType.YOUTUBE,
                    data_type=DataType.CONTENT,
                    user_id=user_id,
                    content_id=video.get("id"),
                    metrics={
                        "view_count": int(video.get("statistics", {}).get("viewCount", 0)),
                        "like_count": int(video.get("statistics", {}).get("likeCount", 0)),
                        "comment_count": int(video.get("statistics", {}).get("commentCount", 0)),
                        "duration": video.get("contentDetails", {}).get("duration")
                    },
                    metadata={
                        "title": video.get("snippet", {}).get("title"),
                        "description": video.get("snippet", {}).get("description"),
                        "published_at": video.get("snippet", {}).get("publishedAt"),
                        "thumbnail": video.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url")
                    },
                    raw_data=video
                ))
                
            return content_data
        except Exception as e:
            logger.error(f"Failed to fetch YouTube content: {e}")
            return []
            
    async def fetch_engagement(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            engagement = await self.client.get_engagement_metrics(user_id)
            
            return [PlatformData(
                platform=PlatformType.YOUTUBE,
                data_type=DataType.ENGAGEMENT,
                user_id=user_id,
                metrics={
                    "average_view_duration": engagement.get("averageViewDuration", 0),
                    "click_through_rate": engagement.get("clickThroughRate", 0),
                    "engagement_rate": engagement.get("engagementRate", 0),
                    "retention_rate": engagement.get("retentionRate", 0)
                },
                raw_data=engagement
            )]
        except Exception as e:
            logger.error(f"Failed to fetch YouTube engagement: {e}")
            return []
            
    async def validate_credentials(self) -> bool:
        try:
            return await self.client.validate_api_key()
        except Exception as e:
            logger.error(f"Failed to validate YouTube credentials: {e}")
            return False


class InstagramConnector(PlatformConnector):
    """Instagram platform connector"""
    
    async def initialize(self) -> bool:
        try:
            self.client = InstagramClient(
                access_token=self.credentials.access_token,
                user_id=self.credentials.user_id
            )
            return await self.client.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize Instagram connector: {e}")
            return False
            
    async def fetch_analytics(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            insights = await self.client.get_account_insights(user_id)
            
            return [PlatformData(
                platform=PlatformType.INSTAGRAM,
                data_type=DataType.ANALYTICS,
                user_id=user_id,
                metrics={
                    "follower_count": insights.get("follower_count", 0),
                    "impressions": insights.get("impressions", 0),
                    "reach": insights.get("reach", 0),
                    "profile_views": insights.get("profile_views", 0)
                },
                raw_data=insights
            )]
        except Exception as e:
            logger.error(f"Failed to fetch Instagram analytics: {e}")
            return []
            
    async def fetch_content(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            media = await self.client.get_user_media(user_id)
            
            content_data = []
            for item in media:
                content_data.append(PlatformData(
                    platform=PlatformType.INSTAGRAM,
                    data_type=DataType.CONTENT,
                    user_id=user_id,
                    content_id=item.get("id"),
                    metrics={
                        "like_count": item.get("like_count", 0),
                        "comments_count": item.get("comments_count", 0),
                        "impressions": item.get("insights", {}).get("impressions", 0),
                        "reach": item.get("insights", {}).get("reach", 0)
                    },
                    metadata={
                        "caption": item.get("caption"),
                        "media_type": item.get("media_type"),
                        "permalink": item.get("permalink"),
                        "timestamp": item.get("timestamp")
                    },
                    raw_data=item
                ))
                
            return content_data
        except Exception as e:
            logger.error(f"Failed to fetch Instagram content: {e}")
            return []
            
    async def fetch_engagement(self, user_id: str, **kwargs) -> List[PlatformData]:
        try:
            engagement = await self.client.get_engagement_metrics(user_id)
            
            return [PlatformData(
                platform=PlatformType.INSTAGRAM,
                data_type=DataType.ENGAGEMENT,
                user_id=user_id,
                metrics={
                    "engagement_rate": engagement.get("engagement_rate", 0),
                    "average_likes": engagement.get("average_likes", 0),
                    "average_comments": engagement.get("average_comments", 0),
                    "story_completion_rate": engagement.get("story_completion_rate", 0)
                },
                raw_data=engagement
            )]
        except Exception as e:
            logger.error(f"Failed to fetch Instagram engagement: {e}")
            return []
            
    async def validate_credentials(self) -> bool:
        try:
            return await self.client.validate_token()
        except Exception as e:
            logger.error(f"Failed to validate Instagram credentials: {e}")
            return False


class PlatformStreamer:
    """
    Multi-platform streaming manager for real-time data synchronization
    across social media, music, and content platforms.
    """
    
    def __init__(self):
        self.connectors: Dict[PlatformType, PlatformConnector] = {}
        self.sync_configs: Dict[str, SyncConfig] = {}
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        self.data_callbacks: List[Callable[[List[PlatformData]], None]] = []
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """
Initialize platform streamer"""
        try:
            logger.info("PlatformStreamer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PlatformStreamer: {e}")
            raise
            
    async def add_platform(
        self,
        platform: PlatformType,
        credentials: PlatformCredentials
    ) -> bool:
        """
        Add platform connector
        
        Args:
            platform: Platform type
            credentials: Platform credentials
            
        Returns:
            Success status
        """
        try:
            # Create appropriate connector
            if platform == PlatformType.SPOTIFY:
                connector = SpotifyConnector(credentials)
            elif platform == PlatformType.YOUTUBE:
                connector = YouTubeConnector(credentials)
            elif platform == PlatformType.INSTAGRAM:
                connector = InstagramConnector(credentials)
            else:
                logger.warning(f"Unsupported platform: {platform}")
                return False
                
            # Initialize connector
            if await connector.initialize():
                self.connectors[platform] = connector
                logger.info(f"Added {platform} connector")
                return True
            else:
                logger.error(f"Failed to initialize {platform} connector")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add platform {platform}: {e}")
            return False
            
    async def configure_sync(
        self,
        user_id: str,
        platform: PlatformType,
        config: SyncConfig
    ) -> str:
        """
        Configure platform synchronization
        
        Args:
            user_id: User identifier
            platform: Platform type
            config: Sync configuration
            
        Returns:
            Sync configuration identifier
        """
        try:
            sync_id = f"{user_id}_{platform.value}"
            self.sync_configs[sync_id] = config
            
            # Start sync task if enabled
            if config.enabled:
                await self._start_sync_task(sync_id, user_id)
                
            logger.info(f"Configured sync for {platform} (user: {user_id})")
            return sync_id
            
        except Exception as e:
            logger.error(f"Failed to configure sync: {e}")
            raise
            
    async def start_sync(self, sync_id: str) -> bool:
        """Start synchronization for configuration"""
        try:
            if sync_id not in self.sync_configs:
                return False
                
            config = self.sync_configs[sync_id]
            user_id = sync_id.split("_")[0]
            
            config.enabled = True
            await self._start_sync_task(sync_id, user_id)
            
            logger.info(f"Started sync {sync_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start sync {sync_id}: {e}")
            return False
            
    async def stop_sync(self, sync_id: str) -> bool:
        """Stop synchronization for configuration"""
        try:
            if sync_id in self.sync_configs:
                self.sync_configs[sync_id].enabled = False
                
            if sync_id in self.sync_tasks:
                self.sync_tasks[sync_id].cancel()
                del self.sync_tasks[sync_id]
                
            logger.info(f"Stopped sync {sync_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop sync {sync_id}: {e}")
            return False
            
    async def sync_now(
        self,
        user_id: str,
        platform: PlatformType,
        data_types: Optional[List[DataType]] = None
    ) -> List[PlatformData]:
        """
        Perform immediate synchronization
        
        Args:
            user_id: User identifier
            platform: Platform type
            data_types: Optional data types to sync
            
        Returns:
            Synchronized data
        """
        try:
            if platform not in self.connectors:
                logger.warning(f"No connector for platform {platform}")
                return []
                
            connector = self.connectors[platform]
            all_data = []
            
            # Default to all data types if not specified
            if not data_types:
                data_types = [DataType.ANALYTICS, DataType.CONTENT, DataType.ENGAGEMENT]
                
            # Fetch data for each type
            for data_type in data_types:
                if data_type == DataType.ANALYTICS:
                    data = await connector.fetch_analytics(user_id)
                elif data_type == DataType.CONTENT:
                    data = await connector.fetch_content(user_id)
                elif data_type == DataType.ENGAGEMENT:
                    data = await connector.fetch_engagement(user_id)
                else:
                    continue
                    
                all_data.extend(data)
                
            # Notify callbacks
            await self._notify_data_callbacks(all_data)
            
            logger.info(f"Synced {len(all_data)} items from {platform} for user {user_id}")
            return all_data
            
        except Exception as e:
            logger.error(f"Failed to sync {platform} for user {user_id}: {e}")
            return []
            
    async def register_data_callback(
        self,
        callback: Callable[[List[PlatformData]], None]
    ) -> None:
        """Register callback for synchronized data"""
        self.data_callbacks.append(callback)
        
    async def get_sync_status(self) -> Dict[str, Any]:
        """
Get synchronization status for all configurations"""
        status = {}
        
        for sync_id, config in self.sync_configs.items():
            status[sync_id] = {
                "platform": config.platform.value,
                "enabled": config.enabled,
                "sync_mode": config.sync_mode.value,
                "interval_seconds": config.interval_seconds,
                "data_types": [dt.value for dt in config.data_types],
                "active": sync_id in self.sync_tasks
            }
            
        return status
        
    async def validate_platform_credentials(self, platform: PlatformType) -> bool:
        """Validate credentials for platform"""
        if platform not in self.connectors:
            return False
            
        return await self.connectors[platform].validate_credentials()
        
    async def _start_sync_task(self, sync_id: str, user_id: str) -> None:
        """
Start background sync task"""
        if sync_id in self.sync_tasks:
            self.sync_tasks[sync_id].cancel()
            
        config = self.sync_configs[sync_id]
        
        if config.sync_mode == SyncMode.REAL_TIME:
            task = asyncio.create_task(self._real_time_sync(sync_id, user_id))
        elif config.sync_mode == SyncMode.SCHEDULED:
            task = asyncio.create_task(self._scheduled_sync(sync_id, user_id))
        else:
            task = asyncio.create_task(self._batch_sync(sync_id, user_id))
            
        self.sync_tasks[sync_id] = task
        
    async def _real_time_sync(self, sync_id: str, user_id: str) -> None:
        """
Real-time synchronization task"""
        config = self.sync_configs[sync_id]
        
        while config.enabled and not self._shutdown_event.is_set():
            try:
                data = await self.sync_now(user_id, config.platform, config.data_types)
                await asyncio.sleep(config.interval_seconds)
            except Exception as e:
                logger.error(f"Real-time sync error for {sync_id}: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
    async def _scheduled_sync(self, sync_id: str, user_id: str) -> None:
        """Scheduled synchronization task"""
        config = self.sync_configs[sync_id]
        
        while config.enabled and not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(config.interval_seconds)
                await self.sync_now(user_id, config.platform, config.data_types)
            except Exception as e:
                logger.error(f"Scheduled sync error for {sync_id}: {e}")
                
    async def _batch_sync(self, sync_id: str, user_id: str) -> None:
        """Batch synchronization task"""
        config = self.sync_configs[sync_id]
        
        while config.enabled and not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(config.interval_seconds)
                
                # Collect data in batches
                batch_data = []
                for data_type in config.data_types:
                    data = await self.sync_now(user_id, config.platform, [data_type])
                    batch_data.extend(data)
                    
                # Process batch
                if batch_data:
                    await self._notify_data_callbacks(batch_data)
                    
            except Exception as e:
                logger.error(f"Batch sync error for {sync_id}: {e}")
                
    async def _notify_data_callbacks(self, data: List[PlatformData]) -> None:
        """Notify registered callbacks with synchronized data"""
        for callback in self.data_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Data callback error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown platform streamer"""
        try:
            self._shutdown_event.set()
            
            # Cancel all sync tasks
            for task in self.sync_tasks.values():
                task.cancel()
                
            # Wait for tasks to complete
            if self.sync_tasks:
                await asyncio.gather(*self.sync_tasks.values(), return_exceptions=True)
                
            logger.info("PlatformStreamer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during platform streamer shutdown: {e}")
