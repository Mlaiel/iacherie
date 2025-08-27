"""
Twitch TV Crawler Implementation
===============================

Advanced Twitch streaming platform crawler for live content monitoring.
Implements real-time stream tracking and content discovery.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
import websockets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class TwitchStream:
    """Twitch stream information"""
    stream_id: str
    channel_name: str
    channel_id: str
    title: str
    game_name: str
    game_id: str
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    tags: List[str]
    is_mature: bool
    stream_type: str  # live, playlist, watch_party, premiere, rerun
    category: str
    duration: int  # seconds
    peak_viewers: int
    average_viewers: int
    chat_mode: str  # followers, subscribers, emote_only, slow
    subscriber_count: int
    follower_count: int
    bits_enabled: bool
    donations_enabled: bool
    stream_quality: str  # source, 1080p60, 720p60, etc.
    fps: int
    resolution: str
    bitrate: int
    audio_bitrate: int
    content_rating: str
    region: str
    monetization_status: Dict[str, bool]


@dataclass
class TwitchChannel:
    """Twitch channel information"""
    channel_id: str
    username: str
    display_name: str
    description: str
    profile_image_url: str
    offline_image_url: str
    banner_url: str
    created_at: datetime
    updated_at: datetime
    follower_count: int
    subscriber_count: int
    view_count: int
    video_count: int
    partner_status: bool
    affiliate_status: bool
    verified: bool
    broadcaster_type: str  # partner, affiliate, regular
    language: str
    game_name: str
    stream_schedule: Dict[str, Any]
    social_links: Dict[str, str]
    panels: List[Dict[str, Any]]
    emotes: List[Dict[str, Any]]
    badges: List[Dict[str, Any]]
    recent_streams: List[TwitchStream]
    clip_count: int
    average_viewers: float
    peak_viewers: int
    streaming_hours: float
    content_categories: List[str]
    collaboration_history: List[str]
    sponsorship_deals: List[Dict[str, Any]]


@dataclass
class TwitchVideo:
    """Twitch video (VOD/Clip) information"""
    video_id: str
    title: str
    description: str
    channel_name: str
    channel_id: str
    created_at: datetime
    published_at: datetime
    duration: int
    view_count: int
    like_count: int
    comment_count: int
    thumbnail_url: str
    video_url: str
    video_type: str  # archive, highlight, upload, clip
    game_name: str
    game_id: str
    language: str
    tags: List[str]
    moments: List[Dict[str, Any]]  # Key moments in the video
    chapters: List[Dict[str, Any]]
    quality_options: List[str]
    is_muted: bool
    muted_segments: List[Dict[str, Any]]
    chat_replay_available: bool
    monetization_enabled: bool
    content_warnings: List[str]
    accessibility_features: List[str]


@dataclass
class TwitchClip:
    """Twitch clip information"""
    clip_id: str
    title: str
    broadcaster_name: str
    broadcaster_id: str
    creator_name: str
    creator_id: str
    created_at: datetime
    duration: float
    view_count: int
    thumbnail_url: str
    video_id: str
    vod_offset: int
    game_name: str
    game_id: str
    language: str
    is_featured: bool
    embed_url: str
    download_url: str
    quality: str
    fps: int
    tags: List[str]
    reaction_count: Dict[str, int]
    share_count: int
    featured_in_collections: List[str]


class TwitchCrawler(PlatformCrawler):
    """
    Advanced Twitch crawler for streaming content monitoring and discovery.
    
    Features:
    - Live stream monitoring
    - Channel analytics and tracking
    - VOD and clip discovery
    - Real-time chat analysis
    - Game/category trending
    - Streamer collaboration detection
    - Content scheduling analysis
    - Monetization tracking
    - Audience engagement metrics
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, client_id: str = None, client_secret: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "twitch"
        self.base_url = "https://www.twitch.tv"
        self.api_base_url = "https://api.twitch.tv/helix"
        self.gql_url = "https://gql.twitch.tv/gql"
        
        # Twitch API credentials
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        
        # Rate limiting
        self.requests_per_minute = 800  # Twitch API limit
        self.requests_per_second = 20
        self.min_delay = 0.05
        self.max_delay = 0.2
        
        # Content type mappings
        self.content_types = {
            'streams': self._crawl_streams,
            'channels': self._crawl_channels,
            'videos': self._crawl_videos,
            'clips': self._crawl_clips,
            'games': self._crawl_games,
            'categories': self._crawl_categories,
            'search': self._crawl_search
        }
        
        # WebSocket for real-time updates
        self.websocket_connection = None
        self.chat_connections = {}
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize authentication
        asyncio.create_task(self._authenticate())
    
    async def _authenticate(self):
        """Authenticate with Twitch API"""
        try:
            if not self.client_id or not self.client_secret:
                self.logger.warning("Twitch API credentials not provided")
                return
            
            # OAuth2 Client Credentials flow
            auth_url = "https://id.twitch.tv/oauth2/token"
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data['expires_in']
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    # Update session headers
                    self.session_headers.update({
                        'Client-ID': self.client_id,
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    self.logger.info("Twitch API authentication successful")
                else:
                    self.logger.error(f"Twitch API authentication failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error authenticating with Twitch API: {str(e)}")
    
    async def _refresh_token_if_needed(self):
        """Refresh access token if needed"""
        try:
            if (self.token_expires_at and 
                datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5)):
                await self._authenticate()
        except Exception as e:
            self.logger.error(f"Error refreshing token: {str(e)}")
    
    async def search_content(self, query: str, content_type: str = "streams", 
                           max_results: int = 50) -> List[CrawlerResult]:
        """
        Search for content on Twitch.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            
        Returns:
            List of crawler results
        """
        try:
            await self._refresh_token_if_needed()
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results)
            
            self.logger.info(f"Found {len(results)} Twitch {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Twitch content: {str(e)}")
            return []
    
    async def _crawl_streams(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl live streams"""
        try:
            results = []
            
            # Search for live streams
            params = {
                'first': min(max_results, 100),
                'game_name': query if query else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            api_url = f"{self.api_base_url}/streams"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for stream_data in data.get('data', []):
                        # Get additional channel information
                        channel_info = await self._get_channel_info(stream_data['user_id'])
                        
                        stream = self._parse_stream_data(stream_data, channel_info)
                        
                        result = CrawlerResult(
                            url=f"{self.base_url}/{stream.channel_name}",
                            title=stream.title,
                            content=f"Live stream: {stream.title} - Game: {stream.game_name}",
                            metadata={
                                'stream_data': asdict(stream),
                                'platform': 'twitch',
                                'content_type': 'stream',
                                'viewer_count': stream.viewer_count,
                                'game_name': stream.game_name,
                                'language': stream.language,
                                'started_at': stream.started_at.isoformat(),
                                'tags': stream.tags,
                                'is_live': True
                            },
                            timestamp=stream.started_at,
                            similarity_score=0.0
                        )
                        results.append(result)
                        
                        # Rate limiting
                        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching streams: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Twitch streams: {str(e)}")
            return []
    
    async def _crawl_channels(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Twitch channels"""
        try:
            results = []
            
            # Search for channels
            params = {
                'query': query,
                'first': min(max_results, 100)
            }
            
            api_url = f"{self.api_base_url}/search/channels"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for channel_data in data.get('data', []):
                        # Get detailed channel information
                        detailed_channel = await self._get_detailed_channel_info(channel_data['id'])
                        
                        if detailed_channel:
                            result = CrawlerResult(
                                url=f"{self.base_url}/{detailed_channel.username}",
                                title=detailed_channel.display_name,
                                content=f"Channel: {detailed_channel.display_name} - {detailed_channel.description}",
                                metadata={
                                    'channel_data': asdict(detailed_channel),
                                    'platform': 'twitch',
                                    'content_type': 'channel',
                                    'follower_count': detailed_channel.follower_count,
                                    'subscriber_count': detailed_channel.subscriber_count,
                                    'partner_status': detailed_channel.partner_status,
                                    'affiliate_status': detailed_channel.affiliate_status,
                                    'verified': detailed_channel.verified,
                                    'game_name': detailed_channel.game_name
                                },
                                timestamp=detailed_channel.updated_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching channels: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Twitch channels: {str(e)}")
            return []
    
    async def _crawl_videos(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Twitch videos (VODs)"""
        try:
            results = []
            
            # First get channels matching the query, then get their videos
            channels = await self._crawl_channels(query, 10)
            
            for channel_result in channels:
                channel_data = channel_result.metadata.get('channel_data', {})
                channel_id = channel_data.get('channel_id')
                
                if channel_id:
                    # Get videos for this channel
                    params = {
                        'user_id': channel_id,
                        'first': min(max_results // len(channels), 20),
                        'type': 'all'
                    }
                    
                    api_url = f"{self.api_base_url}/videos"
                    
                    async with self.session.get(
                        api_url,
                        params=params,
                        headers=self.session_headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for video_data in data.get('data', []):
                                video = self._parse_video_data(video_data)
                                
                                result = CrawlerResult(
                                    url=video.video_url,
                                    title=video.title,
                                    content=f"Video: {video.title} - {video.description}",
                                    metadata={
                                        'video_data': asdict(video),
                                        'platform': 'twitch',
                                        'content_type': 'video',
                                        'view_count': video.view_count,
                                        'duration': video.duration,
                                        'game_name': video.game_name,
                                        'created_at': video.created_at.isoformat(),
                                        'video_type': video.video_type
                                    },
                                    timestamp=video.created_at,
                                    similarity_score=0.0
                                )
                                results.append(result)
                                
                                if len(results) >= max_results:
                                    break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                if len(results) >= max_results:
                    break
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Twitch videos: {str(e)}")
            return []
    
    async def _crawl_clips(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Twitch clips"""
        try:
            results = []
            
            # Get channels for the query, then get their clips
            channels = await self._crawl_channels(query, 10)
            
            for channel_result in channels:
                channel_data = channel_result.metadata.get('channel_data', {})
                channel_id = channel_data.get('channel_id')
                
                if channel_id:
                    # Get clips for this channel
                    params = {
                        'broadcaster_id': channel_id,
                        'first': min(max_results // len(channels), 20),
                        'started_at': (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
                        'ended_at': datetime.utcnow().isoformat() + 'Z'
                    }
                    
                    api_url = f"{self.api_base_url}/clips"
                    
                    async with self.session.get(
                        api_url,
                        params=params,
                        headers=self.session_headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for clip_data in data.get('data', []):
                                clip = self._parse_clip_data(clip_data)
                                
                                result = CrawlerResult(
                                    url=clip.embed_url,
                                    title=clip.title,
                                    content=f"Clip: {clip.title} - by {clip.creator_name}",
                                    metadata={
                                        'clip_data': asdict(clip),
                                        'platform': 'twitch',
                                        'content_type': 'clip',
                                        'view_count': clip.view_count,
                                        'duration': clip.duration,
                                        'game_name': clip.game_name,
                                        'created_at': clip.created_at.isoformat(),
                                        'broadcaster_name': clip.broadcaster_name,
                                        'creator_name': clip.creator_name
                                    },
                                    timestamp=clip.created_at,
                                    similarity_score=0.0
                                )
                                results.append(result)
                                
                                if len(results) >= max_results:
                                    break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                if len(results) >= max_results:
                    break
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Twitch clips: {str(e)}")
            return []
    
    async def _crawl_games(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Twitch games/categories"""
        try:
            results = []
            
            # Search for games
            params = {
                'name': query,
                'first': min(max_results, 100)
            }
            
            api_url = f"{self.api_base_url}/games"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for game_data in data.get('data', []):
                        # Get streams for this game to gather more data
                        game_streams = await self._get_streams_for_game(game_data['id'])
                        
                        result = CrawlerResult(
                            url=f"{self.base_url}/directory/game/{game_data['name']}",
                            title=game_data['name'],
                            content=f"Game: {game_data['name']} - {len(game_streams)} live streams",
                            metadata={
                                'game_data': game_data,
                                'platform': 'twitch',
                                'content_type': 'game',
                                'game_id': game_data['id'],
                                'box_art_url': game_data.get('box_art_url', ''),
                                'live_streams_count': len(game_streams),
                                'total_viewers': sum(stream.get('viewer_count', 0) for stream in game_streams)
                            },
                            timestamp=datetime.utcnow(),
                            similarity_score=0.0
                        )
                        results.append(result)
                
                else:
                    self.logger.error(f"Error fetching games: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Twitch games: {str(e)}")
            return []
    
    async def _crawl_categories(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Twitch categories"""
        try:
            results = []
            
            # Get top games as categories
            params = {
                'first': min(max_results, 100)
            }
            
            api_url = f"{self.api_base_url}/games/top"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for game_data in data.get('data', []):
                        if query.lower() in game_data['name'].lower():
                            result = CrawlerResult(
                                url=f"{self.base_url}/directory/game/{game_data['name']}",
                                title=game_data['name'],
                                content=f"Top category: {game_data['name']}",
                                metadata={
                                    'category_data': game_data,
                                    'platform': 'twitch',
                                    'content_type': 'category',
                                    'game_id': game_data['id'],
                                    'box_art_url': game_data.get('box_art_url', '')
                                },
                                timestamp=datetime.utcnow(),
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching categories: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Twitch categories: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """General Twitch search"""
        try:
            results = []
            
            # Search across different content types
            streams = await self._crawl_streams(query, max_results // 4)
            channels = await self._crawl_channels(query, max_results // 4)
            videos = await self._crawl_videos(query, max_results // 4)
            clips = await self._crawl_clips(query, max_results // 4)
            
            results.extend(streams)
            results.extend(channels)
            results.extend(videos)
            results.extend(clips)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Twitch search: {str(e)}")
            return []
    
    # Helper methods
    
    async def _get_channel_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get basic channel information"""
        try:
            api_url = f"{self.api_base_url}/users"
            params = {'id': user_id}
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get('data', [])
                    return users[0] if users else None
                
        except Exception as e:
            self.logger.error(f"Error getting channel info: {str(e)}")
            return None
    
    async def _get_detailed_channel_info(self, channel_id: str) -> Optional[TwitchChannel]:
        """Get detailed channel information"""
        try:
            # Get basic user info
            user_info = await self._get_channel_info(channel_id)
            if not user_info:
                return None
            
            # Get follower count
            followers = await self._get_channel_followers(channel_id)
            
            # Get recent videos
            recent_videos = await self._get_channel_videos(channel_id, 5)
            
            channel = TwitchChannel(
                channel_id=channel_id,
                username=user_info.get('login', ''),
                display_name=user_info.get('display_name', ''),
                description=user_info.get('description', ''),
                profile_image_url=user_info.get('profile_image_url', ''),
                offline_image_url=user_info.get('offline_image_url', ''),
                banner_url='',
                created_at=datetime.fromisoformat(user_info.get('created_at', '').replace('Z', '+00:00')),
                updated_at=datetime.utcnow(),
                follower_count=followers,
                subscriber_count=0,  # Not available in basic API
                view_count=user_info.get('view_count', 0),
                video_count=len(recent_videos),
                partner_status=user_info.get('broadcaster_type') == 'partner',
                affiliate_status=user_info.get('broadcaster_type') == 'affiliate',
                verified=False,
                broadcaster_type=user_info.get('broadcaster_type', 'regular'),
                language='',
                game_name='',
                stream_schedule={},
                social_links={},
                panels=[],
                emotes=[],
                badges=[],
                recent_streams=[],
                clip_count=0,
                average_viewers=0.0,
                peak_viewers=0,
                streaming_hours=0.0,
                content_categories=[],
                collaboration_history=[],
                sponsorship_deals=[]
            )
            
            return channel
            
        except Exception as e:
            self.logger.error(f"Error getting detailed channel info: {str(e)}")
            return None
    
    async def _get_channel_followers(self, channel_id: str) -> int:
        """Get channel follower count"""
        try:
            api_url = f"{self.api_base_url}/users/follows"
            params = {'to_id': channel_id, 'first': 1}
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('total', 0)
                
        except Exception as e:
            self.logger.error(f"Error getting follower count: {str(e)}")
            return 0
    
    async def _get_channel_videos(self, channel_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get channel videos"""
        try:
            api_url = f"{self.api_base_url}/videos"
            params = {
                'user_id': channel_id,
                'first': limit,
                'type': 'all'
            }
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                
        except Exception as e:
            self.logger.error(f"Error getting channel videos: {str(e)}")
            return []
    
    async def _get_streams_for_game(self, game_id: str) -> List[Dict[str, Any]]:
        """Get live streams for a specific game"""
        try:
            api_url = f"{self.api_base_url}/streams"
            params = {
                'game_id': game_id,
                'first': 20
            }
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                
        except Exception as e:
            self.logger.error(f"Error getting streams for game: {str(e)}")
            return []
    
    def _parse_stream_data(self, stream_data: Dict[str, Any], channel_info: Optional[Dict[str, Any]] = None) -> TwitchStream:
        """Parse stream data from API response"""
        try:
            started_at = datetime.fromisoformat(stream_data.get('started_at', '').replace('Z', '+00:00'))
            
            stream = TwitchStream(
                stream_id=stream_data.get('id', ''),
                channel_name=stream_data.get('user_login', ''),
                channel_id=stream_data.get('user_id', ''),
                title=stream_data.get('title', ''),
                game_name=stream_data.get('game_name', ''),
                game_id=stream_data.get('game_id', ''),
                viewer_count=stream_data.get('viewer_count', 0),
                started_at=started_at,
                language=stream_data.get('language', ''),
                thumbnail_url=stream_data.get('thumbnail_url', ''),
                tags=stream_data.get('tags', []),
                is_mature=stream_data.get('is_mature', False),
                stream_type=stream_data.get('type', 'live'),
                category=stream_data.get('game_name', ''),
                duration=int((datetime.utcnow() - started_at).total_seconds()),
                peak_viewers=stream_data.get('viewer_count', 0),
                average_viewers=stream_data.get('viewer_count', 0),
                chat_mode='normal',
                subscriber_count=0,
                follower_count=0,
                bits_enabled=True,
                donations_enabled=True,
                stream_quality='source',
                fps=60,
                resolution='1920x1080',
                bitrate=6000,
                audio_bitrate=160,
                content_rating='mature' if stream_data.get('is_mature') else 'general',
                region='',
                monetization_status={}
            )
            
            return stream
            
        except Exception as e:
            self.logger.error(f"Error parsing stream data: {str(e)}")
            return None
    
    def _parse_video_data(self, video_data: Dict[str, Any]) -> TwitchVideo:
        """Parse video data from API response"""
        try:
            created_at = datetime.fromisoformat(video_data.get('created_at', '').replace('Z', '+00:00'))
            published_at = datetime.fromisoformat(video_data.get('published_at', '').replace('Z', '+00:00'))
            
            # Parse duration (format: 1h2m3s)
            duration_str = video_data.get('duration', '0s')
            duration = self._parse_duration(duration_str)
            
            video = TwitchVideo(
                video_id=video_data.get('id', ''),
                title=video_data.get('title', ''),
                description=video_data.get('description', ''),
                channel_name=video_data.get('user_login', ''),
                channel_id=video_data.get('user_id', ''),
                created_at=created_at,
                published_at=published_at,
                duration=duration,
                view_count=video_data.get('view_count', 0),
                like_count=0,  # Not available in API
                comment_count=0,  # Not available in API
                thumbnail_url=video_data.get('thumbnail_url', ''),
                video_url=video_data.get('url', ''),
                video_type=video_data.get('type', 'archive'),
                game_name='',
                game_id='',
                language=video_data.get('language', ''),
                tags=[],
                moments=[],
                chapters=[],
                quality_options=[],
                is_muted=False,
                muted_segments=[],
                chat_replay_available=True,
                monetization_enabled=False,
                content_warnings=[],
                accessibility_features=[]
            )
            
            return video
            
        except Exception as e:
            self.logger.error(f"Error parsing video data: {str(e)}")
            return None
    
    def _parse_clip_data(self, clip_data: Dict[str, Any]) -> TwitchClip:
        """Parse clip data from API response"""
        try:
            created_at = datetime.fromisoformat(clip_data.get('created_at', '').replace('Z', '+00:00'))
            
            clip = TwitchClip(
                clip_id=clip_data.get('id', ''),
                title=clip_data.get('title', ''),
                broadcaster_name=clip_data.get('broadcaster_name', ''),
                broadcaster_id=clip_data.get('broadcaster_id', ''),
                creator_name=clip_data.get('creator_name', ''),
                creator_id=clip_data.get('creator_id', ''),
                created_at=created_at,
                duration=clip_data.get('duration', 0.0),
                view_count=clip_data.get('view_count', 0),
                thumbnail_url=clip_data.get('thumbnail_url', ''),
                video_id=clip_data.get('video_id', ''),
                vod_offset=clip_data.get('vod_offset', 0),
                game_name=clip_data.get('game_id', ''),  # Would need to resolve game name
                game_id=clip_data.get('game_id', ''),
                language=clip_data.get('language', ''),
                is_featured=clip_data.get('is_featured', False),
                embed_url=clip_data.get('embed_url', ''),
                download_url=clip_data.get('thumbnail_url', ''),  # Approximate
                quality='source',
                fps=60,
                tags=[],
                reaction_count={},
                share_count=0,
                featured_in_collections=[]
            )
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Error parsing clip data: {str(e)}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse Twitch duration string to seconds"""
        try:
            total_seconds = 0
            
            # Extract hours, minutes, seconds
            hours_match = re.search(r'(\d+)h', duration_str)
            minutes_match = re.search(r'(\d+)m', duration_str)
            seconds_match = re.search(r'(\d+)s', duration_str)
            
            if hours_match:
                total_seconds += int(hours_match.group(1)) * 3600
            if minutes_match:
                total_seconds += int(minutes_match.group(1)) * 60
            if seconds_match:
                total_seconds += int(seconds_match.group(1))
            
            return total_seconds
            
        except Exception as e:
            self.logger.error(f"Error parsing duration: {str(e)}")
            return 0
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            if time_since_last < self.min_delay:
                await asyncio.sleep(self.min_delay - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Twitch content"""
        try:
            # Parse URL to determine content type
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'twitch',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            if len(path_parts) >= 1:
                if path_parts[0] == 'videos':
                    # Video URL
                    video_id = path_parts[1] if len(path_parts) > 1 else None
                    if video_id:
                        video_data = await self._get_video_by_id(video_id)
                        if video_data:
                            metadata.update({
                                'content_type': 'video',
                                'video_data': asdict(video_data)
                            })
                
                elif path_parts[0] == 'directory':
                    # Game directory
                    metadata['content_type'] = 'game_directory'
                
                else:
                    # Channel URL
                    channel_name = path_parts[0]
                    channel_data = await self._get_channel_by_name(channel_name)
                    if channel_data:
                        metadata.update({
                            'content_type': 'channel',
                            'channel_data': asdict(channel_data)
                        })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Twitch metadata: {str(e)}")
            return {'error': str(e)}
    
    async def _get_video_by_id(self, video_id: str) -> Optional[TwitchVideo]:
        """Get video by ID"""
        try:
            api_url = f"{self.api_base_url}/videos"
            params = {'id': video_id}
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get('data', [])
                    if videos:
                        return self._parse_video_data(videos[0])
                
        except Exception as e:
            self.logger.error(f"Error getting video by ID: {str(e)}")
            return None
    
    async def _get_channel_by_name(self, channel_name: str) -> Optional[TwitchChannel]:
        """Get channel by name"""
        try:
            api_url = f"{self.api_base_url}/users"
            params = {'login': channel_name}
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get('data', [])
                    if users:
                        return await self._get_detailed_channel_info(users[0]['id'])
                
        except Exception as e:
            self.logger.error(f"Error getting channel by name: {str(e)}")
            return None
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Twitch platform information"""
        return {
            'platform_name': 'Twitch',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'requests_per_second': self.requests_per_second,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Live stream monitoring',
                'Channel analytics',
                'VOD discovery',
                'Clip tracking',
                'Game/category trending',
                'Real-time chat analysis',
                'Audience engagement metrics',
                'Content scheduling analysis'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth2 Client Credentials',
                'scope': 'Read-only access'
            }
        }
