"""
Kick Crawling Engine
====================

Advanced Kick.com crawler for live streaming content discovery and analytics.
Handles stream metadata extraction, streamer analysis, and chat monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  AVERTISSEMENT LÉGAL 
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import hashlib
import json
from urllib.parse import urljoin, urlparse, parse_qs

import aiohttp
import websockets
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import StreamContent, UserContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class KickStream:
    """Kick stream data structure"""
    id: str
    slug: str
    channel_id: str
    channel_username: str
    title: str
    category: str
    language: str
    thumbnail_url: Optional[str]
    viewer_count: int
    start_time: datetime
    is_live: bool
    is_mature: bool
    tags: List[str]
    chatroom_id: str
    stream_url: str
    playback_url: Optional[str]
    duration: Optional[int]
    created_at: datetime


@dataclass
class KickChannel:
    """Kick channel data structure"""
    id: str
    username: str
    display_name: str
    bio: Optional[str]
    profile_picture_url: Optional[str]
    banner_url: Optional[str]
    follower_count: int
    following_count: int
    is_verified: bool
    is_live: bool
    is_banned: bool
    is_partnered: bool
    created_at: datetime
    recent_categories: List[str]
    social_links: Dict[str, str]
    subscriber_count: Optional[int]
    url: str


@dataclass
class KickChatMessage:
    """Kick chat message data structure"""
    id: str
    channel_id: str
    user_id: str
    username: str
    content: str
    timestamp: datetime
    is_moderator: bool
    is_subscriber: bool
    is_verified: bool
    emotes: List[str]
    message_type: str  # message, subscription, follow, etc.


@dataclass
class KickClip:
    """Kick clip data structure"""
    id: str
    title: str
    channel_id: str
    channel_username: str
    category: str
    view_count: int
    like_count: int
    duration: int
    thumbnail_url: Optional[str]
    video_url: str
    created_at: datetime
    creator_id: str
    creator_username: str


class KickCrawlerEngine(BaseCrawlerEngine):
    """
    Professional Kick.com crawler engine for live streaming content analysis.
    
    Features:
    - Live stream monitoring
    - Channel analytics and insights
    - Chat message tracking
    - Clip discovery and analysis
    - Streamer engagement metrics
    - Content protection monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Kick crawler engine"""
        super().__init__(platform="kick", config=config)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=3600
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(minutes=5),  # Short cache for live content
            max_cache_size=5000
        )
        
        # API endpoints
        self.base_url = "https://kick.com/api/v1"
        self.web_url = "https://kick.com"
        self.ws_url = "wss://ws-us2.pusher.com/app/32cbd69e4b950bf97679"
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connection: Optional[websockets.WebSocketServerProtocol] = None
        
        # Selenium driver
        self.driver: Optional[webdriver.Chrome] = None
        
        logger.info("Kick crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""



        try:
            await self._create_session()
            self._setup_selenium()
            logger.info("Kick engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kick engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://kick.com/',
            'Origin': 'https://kick.com'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=100)
        )
    
    def _setup_selenium(self) -> None:
        """Setup Selenium WebDriver"""



        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized for Kick")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    async def get_live_streams(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50
    ) -> List[KickStream]:
        """
        Get currently live streams
        
        Args:
            category: Filter by category
            language: Filter by language
            limit: Maximum number of streams to return
            
        Returns:
            List of live streams
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"live_streams:{category}:{language}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Build API URL
            url = f"{self.base_url}/channels/live"
            params = {
                'limit': min(limit, 100)
            }
            
            if category:
                params['category'] = category
            if language:
                params['language'] = language
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("Kick API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                streams = []
                
                if 'data' in data:
                    for stream_data in data['data']:
                        stream = self._parse_stream_data(stream_data)
                        streams.append(stream)
                
                # Cache results
                await self.cache_manager.set(cache_key, streams)
                
                logger.info(f"Found {len(streams)} live streams")
                return streams
                
        except Exception as e:
            logger.error(f"Error getting live streams: {e}")
            raise CrawlerError(f"Live streams retrieval failed: {e}")
    
    async def get_channel_info(self, username: str) -> Optional[KickChannel]:
        """
        Get channel information
        
        Args:
            username: Channel username
            
        Returns:
            Channel information or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"channel_info:{username}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/channels/{username}"
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Channel not found: {username}")
                elif response.status == 429:
                    raise RateLimitError("Kick API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                
                if 'data' in data:
                    channel = self._parse_channel_data(data['data'])
                    
                    # Cache result
                    await self.cache_manager.set(cache_key, channel)
                    
                    return channel
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            raise CrawlerError(f"Channel info retrieval failed: {e}")
    
    async def get_stream_details(self, channel_username: str) -> Optional[KickStream]:
        """
        Get current stream details for a channel
        
        Args:
            channel_username: Channel username
            
        Returns:
            Stream details or None if not live
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"stream_details:{channel_username}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/channels/{channel_username}/livestream"
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    return None  # Not live
                elif response.status == 429:
                    raise RateLimitError("Kick API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                
                if 'data' in data and data['data']:
                    stream = self._parse_stream_data(data['data'])
                    
                    # Cache result
                    await self.cache_manager.set(cache_key, stream)
                    
                    return stream
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting stream details: {e}")
            raise CrawlerError(f"Stream details retrieval failed: {e}")
    
    async def get_channel_clips(
        self,
        channel_username: str,
        limit: int = 20
    ) -> List[KickClip]:
        """
        Get clips from a channel
        
        Args:
            channel_username: Channel username
            limit: Number of clips to retrieve
            
        Returns:
            List of channel clips
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"channel_clips:{channel_username}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/channels/{channel_username}/clips"
            params = {'limit': min(limit, 50)}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Channel not found: {channel_username}")
                elif response.status == 429:
                    raise RateLimitError("Kick API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                clips = []
                
                if 'data' in data:
                    for clip_data in data['data']:
                        clip = self._parse_clip_data(clip_data)
                        clips.append(clip)
                
                # Cache results
                await self.cache_manager.set(cache_key, clips)
                
                logger.info(f"Found {len(clips)} clips for channel: {channel_username}")
                return clips
                
        except Exception as e:
            logger.error(f"Error getting channel clips: {e}")
            raise CrawlerError(f"Channel clips retrieval failed: {e}")
    
    async def search_channels(
        self,
        query: str,
        limit: int = 20
    ) -> List[KickChannel]:
        """
        Search for channels
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of matching channels
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search_channels:{hashlib.md5(f'{query}:{limit}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/search/channels"
            params = {
                'query': query,
                'limit': min(limit, 50)
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("Kick API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Search request failed: {response.status}")
                
                data = await response.json()
                channels = []
                
                if 'data' in data:
                    for channel_data in data['data']:
                        channel = self._parse_channel_data(channel_data)
                        channels.append(channel)
                
                # Cache results
                await self.cache_manager.set(cache_key, channels)
                
                logger.info(f"Found {len(channels)} channels for query: {query}")
                return channels
                
        except Exception as e:
            logger.error(f"Error searching channels: {e}")
            raise CrawlerError(f"Channel search failed: {e}")
    
    async def monitor_chat_messages(
        self,
        channel_username: str,
        duration_minutes: int = 60
    ) -> AsyncGenerator[KickChatMessage, None]:
        """
        Monitor chat messages for a channel
        
        Args:
            channel_username: Channel to monitor
            duration_minutes: How long to monitor
            
        Yields:
            Chat messages as they arrive
        """



        try:
            # Get channel info to get chatroom ID
            channel = await self.get_channel_info(channel_username)
            if not channel:
                raise ContentNotFoundError(f"Channel not found: {channel_username}")
            
            # Connect to websocket for chat
            # This would require implementing the Pusher WebSocket protocol
            logger.info(f"Starting chat monitoring for {channel_username}")
            
            # For now, return empty generator as WebSocket implementation would be complex
            return
            yield  # This makes it a generator
            
        except Exception as e:
            logger.error(f"Error monitoring chat messages: {e}")
            raise CrawlerError(f"Chat monitoring failed: {e}")
    
    def _parse_stream_data(self, stream_data: Dict[str, Any]) -> KickStream:
        """Parse stream data from API response"""



        try:
            return KickStream(
                id=str(stream_data.get('id', '')),
                slug=stream_data.get('slug', ''),
                channel_id=str(stream_data.get('channel', {}).get('id', '')),
                channel_username=stream_data.get('channel', {}).get('user', {}).get('username', ''),
                title=stream_data.get('session_title', ''),
                category=stream_data.get('category', {}).get('name', '') if stream_data.get('category') else '',
                language=stream_data.get('language', 'en'),
                thumbnail_url=stream_data.get('thumbnail', {}).get('url') if stream_data.get('thumbnail') else None,
                viewer_count=stream_data.get('viewer_count', 0),
                start_time=datetime.fromisoformat(stream_data.get('start_time', '').replace('Z', '+00:00')) if stream_data.get('start_time') else datetime.utcnow(),
                is_live=stream_data.get('is_live', False),
                is_mature=stream_data.get('is_mature', False),
                tags=stream_data.get('tags', []),
                chatroom_id=str(stream_data.get('chatroom', {}).get('id', '')),
                stream_url=f"https://kick.com/{stream_data.get('channel', {}).get('user', {}).get('username', '')}",
                playback_url=stream_data.get('playback_url'),
                duration=stream_data.get('duration'),
                created_at=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error parsing stream data: {e}")
            raise CrawlerError(f"Stream data parsing failed: {e}")
    
    def _parse_channel_data(self, channel_data: Dict[str, Any]) -> KickChannel:
        """Parse channel data from API response"""



        try:
            user_data = channel_data.get('user', {})
            
            return KickChannel(
                id=str(channel_data.get('id', '')),
                username=user_data.get('username', ''),
                display_name=channel_data.get('user', {}).get('username', ''),
                bio=channel_data.get('user', {}).get('bio'),
                profile_picture_url=user_data.get('profile_pic'),
                banner_url=channel_data.get('banner', {}).get('url') if channel_data.get('banner') else None,
                follower_count=channel_data.get('followers_count', 0),
                following_count=0,  # Not available in API
                is_verified=channel_data.get('verified', False),
                is_live=channel_data.get('livestream') is not None,
                is_banned=False,  # Not available in API
                is_partnered=False,  # Not available in API
                created_at=datetime.fromisoformat(user_data.get('created_at', '').replace('Z', '+00:00')) if user_data.get('created_at') else datetime.utcnow(),
                recent_categories=channel_data.get('recent_categories', []),
                social_links={},  # Extract if available
                subscriber_count=None,  # Not available in API
                url=f"https://kick.com/{user_data.get('username', '')}"
            )
        except Exception as e:
            logger.error(f"Error parsing channel data: {e}")
            raise CrawlerError(f"Channel data parsing failed: {e}")
    
    def _parse_clip_data(self, clip_data: Dict[str, Any]) -> KickClip:
        """Parse clip data from API response"""



        try:
            return KickClip(
                id=str(clip_data.get('id', '')),
                title=clip_data.get('title', ''),
                channel_id=str(clip_data.get('channel', {}).get('id', '')),
                channel_username=clip_data.get('channel', {}).get('user', {}).get('username', ''),
                category=clip_data.get('category', {}).get('name', '') if clip_data.get('category') else '',
                view_count=clip_data.get('view_count', 0),
                like_count=clip_data.get('likes_count', 0),
                duration=clip_data.get('duration', 0),
                thumbnail_url=clip_data.get('thumbnail_url'),
                video_url=clip_data.get('clip_url', ''),
                created_at=datetime.fromisoformat(clip_data.get('created_at', '').replace('Z', '+00:00')) if clip_data.get('created_at') else datetime.utcnow(),
                creator_id=str(clip_data.get('creator', {}).get('id', '')),
                creator_username=clip_data.get('creator', {}).get('username', '')
            )
        except Exception as e:
            logger.error(f"Error parsing clip data: {e}")
            raise CrawlerError(f"Clip data parsing failed: {e}")
    
    async def analyze_streamer_performance(
        self,
        channel_username: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze streamer performance metrics
        
        Args:
            channel_username: Channel to analyze
            days: Number of days to analyze
            
        Returns:
            Performance analytics data
        """



        try:
            # Get channel info
            channel = await self.get_channel_info(channel_username)
            if not channel:
                raise ContentNotFoundError(f"Channel not found: {channel_username}")
            
            # Get clips for engagement analysis
            clips = await self.get_channel_clips(channel_username, limit=50)
            
            # Calculate metrics
            analytics = {
                'channel_username': channel_username,
                'analysis_period_days': days,
                'channel_metrics': {
                    'follower_count': channel.follower_count,
                    'is_verified': channel.is_verified,
                    'is_live': channel.is_live
                },
                'content_metrics': {
                    'total_clips': len(clips),
                    'total_views': sum(clip.view_count for clip in clips),
                    'total_likes': sum(clip.like_count for clip in clips),
                    'average_views_per_clip': sum(clip.view_count for clip in clips) / len(clips) if clips else 0,
                    'average_likes_per_clip': sum(clip.like_count for clip in clips) / len(clips) if clips else 0
                },
                'engagement_rate': 0.0,
                'top_performing_clips': [],
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            # Calculate engagement rate
            if analytics['content_metrics']['total_views'] > 0:
                analytics['engagement_rate'] = (
                    analytics['content_metrics']['total_likes'] / 
                    analytics['content_metrics']['total_views']
                ) * 100
            
            # Get top performing clips
            sorted_clips = sorted(clips, key=lambda x: x.view_count, reverse=True)
            for clip in sorted_clips[:5]:
                analytics['top_performing_clips'].append({
                    'title': clip.title,
                    'view_count': clip.view_count,
                    'like_count': clip.like_count,
                    'duration': clip.duration,
                    'created_at': clip.created_at.isoformat()
                })
            
            logger.info(f"Performance analysis completed for {channel_username}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error analyzing streamer performance: {e}")
            raise CrawlerError(f"Streamer performance analysis failed: {e}")
    
    async def monitor_content_violations(
        self,
        content_keywords: List[str],
        monitoring_duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Monitor for potential content violations
        
        Args:
            content_keywords: Keywords to monitor for
            monitoring_duration_hours: Duration to monitor
            
        Returns:
            Content violation monitoring results
        """



        try:
            violations = {
                'keywords': content_keywords,
                'monitoring_duration_hours': monitoring_duration_hours,
                'potential_violations': [],
                'monitoring_start': datetime.utcnow().isoformat()
            }
            
            # Search for streams containing keywords
            for keyword in content_keywords:
                live_streams = await self.get_live_streams(limit=100)
                
                for stream in live_streams:
                    # Check if keyword appears in title
                    if any(keyword.lower() in stream.title.lower() for keyword in content_keywords):
                        violations['potential_violations'].append({
                            'stream_id': stream.id,
                            'channel_username': stream.channel_username,
                            'title': stream.title,
                            'category': stream.category,
                            'viewer_count': stream.viewer_count,
                            'matched_keywords': [kw for kw in content_keywords if kw.lower() in stream.title.lower()],
                            'url': stream.stream_url,
                            'detected_at': datetime.utcnow().isoformat()
                        })
            
            logger.info(f"Content violation monitoring completed. Found {len(violations['potential_violations'])} potential violations")
            return violations
            
        except Exception as e:
            logger.error(f"Error monitoring content violations: {e}")
            raise CrawlerError(f"Content violation monitoring failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources"""



        try:
            if self.session:
                await self.session.close()
            if self.ws_connection:
                await self.ws_connection.close()
            if self.driver:
                self.driver.quit()
            await super().cleanup()
            logger.info("Kick engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"KickCrawlerEngine(platform=kick)"
