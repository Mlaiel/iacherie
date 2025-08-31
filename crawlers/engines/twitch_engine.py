"""Twitch Crawling Engine
=====================

Advanced Twitch crawler for streaming content monitoring and analytics.
Handles streams, clips, channels, and chat data extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.

🏗️ Architecture Enterprise - Équipe Projet Spécialisée :
• Lead Developer IA : Fahed Mlaiel (mlaiel@live.de)
• Backend Senior Engineer : Architecture microservices & APIs
• ML/AI Engineer : Intelligence artificielle & algorithmes avancés
• Database Administrator : Optimisation données & performance
• Security Expert : Cybersécurité & protection contenu
• DevOps Engineer : Infrastructure cloud & déploiement
• Audio/Video Specialist : Traitement multimédia avancé
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time

import aiohttp
import requests
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent, VideoType
from twitchAPI.chat import Chat, EventData, ChatMessage
from selenium import webdriver
from selenium.webdriver.common.by import By

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    StreamOfflineError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..models.content_models import StreamContent, ClipContent, ChannelContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TwitchStreamData:
    """Twitch stream data structure"""
    stream_id: str
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    type: str  # live, vodcast, etc.
    title: str
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    tag_ids: List[str]
    tags: List[str]
    is_mature: bool
    stream_url: str
    duration: Optional[timedelta] = None
    peak_viewers: Optional[int] = None
    average_viewers: Optional[int] = None
    chat_messages: List[Dict[str, Any]] = None
    clips_created: int = 0
    followers_gained: int = 0
    subscribers_gained: int = 0
    bits_received: int = 0
    donations_received: float = 0.0


@dataclass
class TwitchChannelData:
    """Twitch channel data structure"""
    user_id: str
    user_login: str
    user_name: str
    display_name: str
    type: str  # staff, admin, global_mod, user
    broadcaster_type: str  # partner, affiliate, ""
    description: str
    profile_image_url: str
    offline_image_url: str
    email: str
    created_at: datetime
    view_count: int
    follower_count: int
    subscriber_count: Optional[int]
    game_name: str
    language: str
    title: str
    tags: List[str]
    content_classification_labels: List[str]
    is_branded_content: bool
    delay: int
    is_live: bool = False
    stream_data: Optional[TwitchStreamData] = None
    recent_clips: List['TwitchClipData'] = None
    social_media: Dict[str, str] = None
    panels: List[Dict[str, Any]] = None
    schedule: Dict[str, Any] = None
    emotes: List[Dict[str, Any]] = None


@dataclass
class TwitchClipData:
    """Twitch clip data structure"""
    clip_id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    game_name: str
    language: str
    title: str
    view_count: int
    created_at: datetime
    thumbnail_url: str
    duration: float
    vod_offset: Optional[int]
    is_featured: bool
    quality: str
    video_url: str
    download_url: Optional[str] = None
    engagement_rate: float = 0.0
    comments: List[Dict[str, Any]] = None


@dataclass
class TwitchAnalyticsData:
    """Twitch analytics data structure"""
    channel_id: str
    date_range: Dict[str, datetime]
    total_view_time: int
    unique_viewers: int
    peak_concurrent_viewers: int
    average_concurrent_viewers: int
    follower_growth: int
    subscriber_growth: int
    bits_received: int
    ad_revenue: float
    subscription_revenue: float
    top_games: List[Dict[str, Any]]
    top_clips: List[Dict[str, Any]]
    chat_activity: Dict[str, Any]
    stream_schedule_adherence: float
    content_tags_performance: Dict[str, Any]
    audience_demographics: Dict[str, Any]
    device_breakdown: Dict[str, Any]
    geographic_distribution: Dict[str, Any]


class TwitchCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced Twitch crawler engine with comprehensive API integration.
    
    Features:
    - Official Twitch API integration
    - Live stream monitoring
    - Clip analysis and extraction
    - Chat monitoring and analysis
    - Channel analytics and metrics
    - VOD content analysis
    - Subscriber and follower tracking
    - Revenue and monetization data
    """
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 access_token: Optional[str] = None,
                 user_token: Optional[str] = None,
                 monitor_chat: bool = False,
                 proxy_config: Optional[Dict] = None,
                 rate_limit_config: Optional[Dict] = None):
        """
        Initialize Twitch crawler engine.
        
        Args:
            client_id: Twitch API client ID
            client_secret: Twitch API client secret
            access_token: App access token
            user_token: User access token for authenticated requests
            monitor_chat: Whether to monitor chat messages
            proxy_config: Proxy configuration
            rate_limit_config: Rate limiting configuration
        """
        super().__init__()
        
        # API Configuration
        self.client_id = client_id or settings.TWITCH_CLIENT_ID
        self.client_secret = client_secret or settings.TWITCH_CLIENT_SECRET
        self.access_token = access_token
        self.user_token = user_token
        
        # Twitch API client
        self.twitch = None
        self.chat = None
        self.monitor_chat = monitor_chat
        
        # Rate limiting (Twitch: 800 requests per minute)
        rate_config = rate_limit_config or {
            'requests_per_minute': 800,
            'requests_per_hour': 48000,
            'burst_limit': 100
        }
        self.rate_limiter = RateLimiter(**rate_config)
        
        # Cache manager
        self.cache_manager = CacheManager(
            cache_type='redis',
            ttl=900,  # 15 minute cache
            key_prefix='twitch_'
        )
        
        # Proxy manager
        if proxy_config:
            self.proxy_manager = ProxyManager(proxy_config)
        else:
            self.proxy_manager = None

    async def authenticate(self) -> bool:
        """Authenticate with Twitch API"""
        try:
            # Initialize Twitch API client
            self.twitch = await Twitch(self.client_id, self.client_secret)
            
            # Set user token if available
            if self.user_token:
                await self.twitch.set_user_authentication(
                    self.user_token,
                    [AuthScope.CHANNEL_READ_SUBSCRIPTIONS, 
                     AuthScope.BITS_READ,
                     AuthScope.ANALYTICS_READ_EXTENSIONS,
                     AuthScope.ANALYTICS_READ_GAMES,
                     AuthScope.CHANNEL_READ_STREAM_KEY,
                     AuthScope.CHAT_READ]
                )
            
            # Test authentication
            users = await self.twitch.get_users()
            if users:
                if self.user_token:
                    user = users[0]
                    logger.info(f"Authenticated Twitch user: {user.display_name}")
                else:
                    logger.info("Authenticated with Twitch API (app-only)")
                
                # Initialize chat if requested
                if self.monitor_chat and self.user_token:
                    self.chat = await Chat(self.twitch)
                
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Twitch authentication failed: {e}")
            return False

    async def get_channel_info(self, channel_login: str) -> TwitchChannelData:
        """
        Get Twitch channel information.
        
        Args:
            channel_login: Channel login name
        
        Returns:
            TwitchChannelData object
        """
        cache_key = f"channel_info_{channel_login}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return TwitchChannelData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            # Get user information
            users = await self.twitch.get_users(logins=[channel_login])
            if not users:
                raise ContentNotFoundError(f"Channel not found: {channel_login}")
            
            user = users[0]
            
            # Get channel information
            channels = await self.twitch.get_channel_information(broadcaster_ids=[user.id])
            channel_info = channels[0] if channels else None
            
            # Get follower count
            follow_count = 0
            try:
                followers = await self.twitch.get_channel_followers(broadcaster_id=user.id)
                follow_count = followers['total']
            except:
                pass
            
            # Check if live
            streams = await self.twitch.get_streams(user_ids=[user.id])
            is_live = len(streams) > 0
            stream_data = None
            
            if is_live:
                stream = streams[0]
                stream_data = TwitchStreamData(
                    stream_id=stream.id,
                    user_id=stream.user_id,
                    user_login=stream.user_login,
                    user_name=stream.user_name,
                    game_id=stream.game_id,
                    game_name=stream.game_name,
                    type=stream.type,
                    title=stream.title,
                    viewer_count=stream.viewer_count,
                    started_at=stream.started_at,
                    language=stream.language,
                    thumbnail_url=stream.thumbnail_url,
                    tag_ids=stream.tag_ids or [],
                    tags=stream.tags or [],
                    is_mature=stream.is_mature,
                    stream_url=f"https://www.twitch.tv/{stream.user_login}"
                )
            
            channel_data = TwitchChannelData(
                user_id=user.id,
                user_login=user.login,
                user_name=user.display_name,
                display_name=user.display_name,
                type=user.type,
                broadcaster_type=user.broadcaster_type,
                description=user.description,
                profile_image_url=user.profile_image_url,
                offline_image_url=user.offline_image_url,
                email=getattr(user, 'email', ''),
                created_at=user.created_at,
                view_count=user.view_count,
                follower_count=follow_count,
                game_name=channel_info.game_name if channel_info else '',
                language=channel_info.broadcaster_language if channel_info else user.broadcaster_type,
                title=channel_info.title if channel_info else '',
                tags=channel_info.tags if channel_info else [],
                content_classification_labels=channel_info.content_classification_labels if channel_info else [],
                is_branded_content=channel_info.is_branded_content if channel_info else False,
                delay=channel_info.delay if channel_info else 0,
                is_live=is_live,
                stream_data=stream_data
            )
            
            # Cache result
            await self.cache_manager.set(cache_key, asdict(channel_data))
            
            return channel_data
        
        except Exception as e:
            logger.error(f"Error getting Twitch channel info: {e}")
            raise CrawlerError(f"Twitch channel info retrieval failed: {e}")

    async def get_channel_clips(self, 
                              channel_login: str,
                              started_at: Optional[datetime] = None,
                              ended_at: Optional[datetime] = None,
                              is_featured: Optional[bool] = None,
                              limit: int = 100) -> List[TwitchClipData]:
        """
        Get clips from a Twitch channel.
        
        Args:
            channel_login: Channel login name
            started_at: Start date for clip search
            ended_at: End date for clip search
            is_featured: Filter for featured clips only
            limit: Maximum number of clips to return
        
        Returns:
            List of TwitchClipData objects
        """
        cache_key = f"channel_clips_{channel_login}_{started_at}_{ended_at}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [TwitchClipData(**clip) for clip in cached_result]

        clips = []
        
        try:
            await self.rate_limiter.acquire()
            
            # Get user ID
            users = await self.twitch.get_users(logins=[channel_login])
            if not users:
                raise ContentNotFoundError(f"Channel not found: {channel_login}")
            
            user_id = users[0].id
            
            # Get clips
            clip_results = await self.twitch.get_clips(
                broadcaster_id=user_id,
                started_at=started_at,
                ended_at=ended_at,
                is_featured=is_featured,
                first=min(limit, 100)  # API limit is 100
            )
            
            for clip in clip_results:
                clip_data = TwitchClipData(
                    clip_id=clip.id,
                    url=clip.url,
                    embed_url=clip.embed_url,
                    broadcaster_id=clip.broadcaster_id,
                    broadcaster_name=clip.broadcaster_name,
                    creator_id=clip.creator_id,
                    creator_name=clip.creator_name,
                    video_id=clip.video_id,
                    game_id=clip.game_id,
                    game_name=clip.game_name,
                    language=clip.language,
                    title=clip.title,
                    view_count=clip.view_count,
                    created_at=clip.created_at,
                    thumbnail_url=clip.thumbnail_url,
                    duration=clip.duration,
                    vod_offset=clip.vod_offset,
                    is_featured=getattr(clip, 'is_featured', False),
                    quality='source',  # Default quality
                    video_url=clip.url
                )
                clips.append(clip_data)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(clip) for clip in clips]
            )
        
        except Exception as e:
            logger.error(f"Error getting Twitch channel clips: {e}")
            raise CrawlerError(f"Twitch channel clips retrieval failed: {e}")
        
        return clips

    async def search_channels(self, 
                            query: str,
                            live_only: bool = False,
                            limit: int = 100) -> List[TwitchChannelData]:
        """
        Search for Twitch channels.
        
        Args:
            query: Search query
            live_only: Only return live channels
            limit: Maximum number of channels to return
        
        Returns:
            List of TwitchChannelData objects
        """
        cache_key = f"search_channels_{hashlib.md5(query.encode()).hexdigest()}_{live_only}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [TwitchChannelData(**channel) for channel in cached_result]

        channels = []
        
        try:
            await self.rate_limiter.acquire()
            
            # Search channels
            search_results = await self.twitch.search_channels(
                query=query,
                live_only=live_only,
                first=min(limit, 100)  # API limit is 100
            )
            
            for result in search_results:
                # Get additional channel info
                try:
                    channel_data = await self.get_channel_info(result.broadcaster_login)
                    channels.append(channel_data)
                except:
                    # Fallback to basic data from search
                    basic_channel = TwitchChannelData(
                        user_id=result.id,
                        user_login=result.broadcaster_login,
                        user_name=result.display_name,
                        display_name=result.display_name,
                        type='user',
                        broadcaster_type='',
                        description='',
                        profile_image_url=result.thumbnail_url,
                        offline_image_url='',
                        email='',
                        created_at=datetime.now(),
                        view_count=0,
                        follower_count=0,
                        game_name=result.game_name,
                        language=result.broadcaster_language,
                        title=result.title,
                        tags=result.tags or [],
                        content_classification_labels=[],
                        is_branded_content=False,
                        delay=0,
                        is_live=result.is_live
                    )
                    channels.append(basic_channel)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(channel) for channel in channels]
            )
        
        except Exception as e:
            logger.error(f"Error searching Twitch channels: {e}")
            raise CrawlerError(f"Twitch channel search failed: {e}")
        
        return channels

    async def get_top_games(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get top games on Twitch.
        
        Args:
            limit: Maximum number of games to return
        
        Returns:
            List of game dictionaries
        """
        cache_key = f"top_games_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        try:
            await self.rate_limiter.acquire()
            
            games = await self.twitch.get_top_games(first=min(limit, 100))
            
            game_list = []
            for game in games:
                game_list.append({
                    'game_id': game.id,
                    'name': game.name,
                    'box_art_url': game.box_art_url,
                    'igdb_id': getattr(game, 'igdb_id', None)
                })
            
            # Cache results
            await self.cache_manager.set(cache_key, game_list)
            
            return game_list
        
        except Exception as e:
            logger.error(f"Error getting top Twitch games: {e}")
            raise CrawlerError(f"Twitch top games retrieval failed: {e}")

    async def monitor_streams(self, 
                            channel_logins: List[str],
                            keywords: List[str],
                            check_interval: int = 300) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor Twitch streams for content matches.
        
        Args:
            channel_logins: List of channel login names to monitor
            keywords: Keywords to search for in stream titles
            check_interval: Check interval in seconds
        
        Yields:
            Dictionary containing monitoring results
        """
        logger.info(f"Starting Twitch stream monitoring for {len(channel_logins)} channels")
        
        while True:
            for channel_login in channel_logins:
                try:
                    # Get channel info
                    channel_data = await self.get_channel_info(channel_login)
                    
                    if channel_data.is_live and channel_data.stream_data:
                        stream = channel_data.stream_data
                        title_lower = stream.title.lower()
                        
                        for keyword in keywords:
                            if keyword.lower() in title_lower:
                                yield {
                                    'type': 'twitch_stream_match',
                                    'platform': 'twitch',
                                    'channel': channel_login,
                                    'stream_id': stream.stream_id,
                                    'keyword': keyword,
                                    'title': stream.title,
                                    'game': stream.game_name,
                                    'viewers': stream.viewer_count,
                                    'language': stream.language,
                                    'started_at': stream.started_at,
                                    'thumbnail': stream.thumbnail_url,
                                    'stream_url': stream.stream_url,
                                    'tags': stream.tags,
                                    'timestamp': datetime.now()
                                }
                
                except Exception as e:
                    logger.error(f"Error monitoring Twitch channel {channel_login}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'twitch',
                        'channel': channel_login,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def monitor_clips(self, 
                          channel_logins: List[str],
                          keywords: List[str],
                          check_interval: int = 600) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor Twitch clips for content matches.
        
        Args:
            channel_logins: List of channel login names to monitor
            keywords: Keywords to search for in clip titles
            check_interval: Check interval in seconds
        
        Yields:
            Dictionary containing monitoring results
        """
        logger.info(f"Starting Twitch clip monitoring for {len(channel_logins)} channels")
        
        last_check = {}
        
        while True:
            for channel_login in channel_logins:
                try:
                    current_time = datetime.now()
                    since = last_check.get(channel_login, current_time - timedelta(hours=1))
                    
                    # Get recent clips
                    clips = await self.get_channel_clips(
                        channel_login,
                        started_at=since,
                        limit=50
                    )
                    
                    for clip in clips:
                        title_lower = clip.title.lower()
                        for keyword in keywords:
                            if keyword.lower() in title_lower:
                                yield {
                                    'type': 'twitch_clip_match',
                                    'platform': 'twitch',
                                    'channel': channel_login,
                                    'clip_id': clip.clip_id,
                                    'keyword': keyword,
                                    'title': clip.title,
                                    'creator': clip.creator_name,
                                    'game': clip.game_name,
                                    'views': clip.view_count,
                                    'duration': clip.duration,
                                    'created_at': clip.created_at,
                                    'url': clip.url,
                                    'thumbnail': clip.thumbnail_url,
                                    'timestamp': datetime.now()
                                }
                    
                    last_check[channel_login] = current_time
                
                except Exception as e:
                    logger.error(f"Error monitoring Twitch clips for {channel_login}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'twitch',
                        'channel': channel_login,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def get_channel_analytics(self, 
                                  channel_login: str,
                                  started_at: datetime,
                                  ended_at: datetime) -> TwitchAnalyticsData:
        """
        Get analytics data for a Twitch channel.
        
        Args:
            channel_login: Channel login name
            started_at: Start date for analytics
            ended_at: End date for analytics
        
        Returns:
            TwitchAnalyticsData object
        """
        if not self.user_token:
            raise AuthenticationError("User token required for analytics")

        try:
            await self.rate_limiter.acquire()
            
            # Get user ID
            users = await self.twitch.get_users(logins=[channel_login])
            if not users:
                raise ContentNotFoundError(f"Channel not found: {channel_login}")
            
            user_id = users[0].id
            
            # This would require additional analytics endpoints
            # For now, return basic analytics structure
            analytics = TwitchAnalyticsData(
                channel_id=user_id,
                date_range={'start': started_at, 'end': ended_at},
                total_view_time=0,
                unique_viewers=0,
                peak_concurrent_viewers=0,
                average_concurrent_viewers=0,
                follower_growth=0,
                subscriber_growth=0,
                bits_received=0,
                ad_revenue=0.0,
                subscription_revenue=0.0,
                top_games=[],
                top_clips=[],
                chat_activity={},
                stream_schedule_adherence=0.0,
                content_tags_performance={},
                audience_demographics={},
                device_breakdown={},
                geographic_distribution={}
            )
            
            return analytics
        
        except Exception as e:
            logger.error(f"Error getting Twitch analytics: {e}")
            raise CrawlerError(f"Twitch analytics retrieval failed: {e}")

    async def close(self):
        """Close Twitch API connections"""
        if self.chat:
            await self.chat.stop()
        if self.twitch:
            await self.twitch.close()

    def __del__(self):
        """Cleanup resources"""
        try:
            if self.twitch or self.chat:
                asyncio.create_task(self.close())
        except:
            pass
