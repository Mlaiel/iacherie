"""Kick Crawler Implementation
===========================

Advanced Kick platform crawler for gaming and live streaming content monitoring.
Implements comprehensive Stream, User, Channel, and Chat tracking.

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
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class KickStream:
    """Kick stream information"""
    stream_id: str
    channel_id: str
    channel_name: str
    streamer_username: str
    title: str
    description: str
    game_category: str
    game_name: str
    thumbnail_url: str
    viewer_count: int
    follower_count: int
    subscriber_count: int
    is_live: bool
    started_at: datetime
    duration_seconds: Optional[int]
    language: str
    tags: List[str]
    stream_quality: str  # 1080p, 720p, etc.
    chat_enabled: bool
    subscribers_only: bool
    follower_mode: bool
    slow_mode: bool
    emote_only_mode: bool
    stream_url: str
    chat_url: str
    vod_url: Optional[str]
    is_mature: bool
    country: str
    region: str
    category_id: str


@dataclass
class KickUser:
    """Kick user information"""
    user_id: str
    username: str
    display_name: str
    bio: str
    profile_picture_url: str
    banner_url: Optional[str]
    follower_count: int
    following_count: int
    verified: bool
    partner: bool
    created_at: datetime
    last_live: Optional[datetime]
    total_views: int
    streaming_hours: int
    country: Optional[str]
    social_links: Dict[str, str]
    donation_link: Optional[str]
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    youtube_handle: Optional[str]
    discord_server: Optional[str]
    website_url: Optional[str]
    offline_banner_url: Optional[str]
    subscription_enabled: bool
    chat_settings: Dict[str, Any]
    stream_schedule: List[Dict[str, Any]]
    recent_games: List[str]


@dataclass
class KickClip:
    """Kick clip information"""
    clip_id: str
    title: str
    channel_id: str
    channel_name: str
    creator_username: str
    duration_seconds: int
    view_count: int
    like_count: int
    created_at: datetime
    game_name: str
    thumbnail_url: str
    video_url: str
    quality: str
    language: str
    is_featured: bool
    category: str
    tags: List[str]
    description: str
    chat_replay_url: Optional[str]


@dataclass
class KickChatMessage:
    """Kick chat message information"""
    message_id: str
    channel_id: str
    user_id: str
    username: str
    display_name: str
    content: str
    timestamp: datetime
    is_subscriber: bool
    is_moderator: bool
    is_vip: bool
    is_broadcaster: bool
    badges: List[str]
    emotes: List[Dict[str, Any]]
    color: Optional[str]
    is_action: bool
    is_deleted: bool
    reply_to: Optional[str]
    mentions: List[str]
    message_type: str  # chat, donation, subscription, etc.


@dataclass
class KickCategory:
    """Kick category information"""
    category_id: str
    name: str
    slug: str
    description: str
    cover_image_url: str
    banner_url: Optional[str]
    viewer_count: int
    stream_count: int
    follower_count: int
    tags: List[str]
    is_mature: bool
    parent_category_id: Optional[str]
    subcategories: List[str]
    top_streamers: List[str]
    trending_clips: List[str]


class KickCrawler(PlatformCrawler):
    """
    Advanced Kick crawler for gaming and live streaming content monitoring.
    
    Features:
    - Live stream monitoring
    - User profile analysis
    - Chat message tracking
    - Clip discovery and analysis
    - Game category monitoring
    - Viewership analytics
    - Streamer performance tracking
    - Community engagement analysis
    - Real-time alerts
    - Gaming trend analysis
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "kick"
        self.base_url = "https://kick.com"
        self.api_base_url = "https://kick.com/api/v1"
        
        # Rate limiting (Kick has moderate limits)
        self.requests_per_minute = 30
        self.min_delay = 2.0
        self.max_delay = 4.0
        
        # Content type mappings
        self.content_types = {
            'streams': self._crawl_streams,
            'users': self._crawl_users,
            'clips': self._crawl_clips,
            'chat': self._crawl_chat,
            'categories': self._crawl_categories,
            'live': self._crawl_live_streams,
            'trending': self._crawl_trending,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Kick-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://kick.com/',
            'Origin': 'https://kick.com',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search_content(self, query: str, content_type: str = "streams", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """
        Search for content on Kick.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Kick {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Kick content: {str(e)}")
            return []
    
    async def _crawl_streams(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Kick streams"""
        try:
            results = []
            
            # Mock stream data
            mock_streams = await self._get_mock_streams(query, max_results)
            
            for stream_data in mock_streams:
                stream = await self._parse_stream_data(stream_data)
                if stream:
                    result = CrawlerResult(
                        url=f"{self.base_url}/{stream.channel_name}",
                        title=f"[{stream.game_name}] {stream.title}",
                        content=stream.description,
                        metadata={
                            'stream_data': asdict(stream),
                            'platform': 'kick',
                            'content_type': 'stream',
                            'channel_name': stream.channel_name,
                            'streamer_username': stream.streamer_username,
                            'game_category': stream.game_category,
                            'game_name': stream.game_name,
                            'viewer_count': stream.viewer_count,
                            'follower_count': stream.follower_count,
                            'is_live': stream.is_live,
                            'language': stream.language,
                            'tags': stream.tags,
                            'stream_quality': stream.stream_quality,
                            'duration_seconds': stream.duration_seconds,
                            'is_mature': stream.is_mature,
                            'country': stream.country
                        },
                        timestamp=stream.started_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Kick streams: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Kick users"""
        try:
            results = []
            
            # Mock user data
            mock_users = await self._get_mock_users(query, max_results)
            
            for user_data in mock_users:
                user = await self._parse_user_data(user_data)
                if user:
                    result = CrawlerResult(
                        url=f"{self.base_url}/{user.username}",
                        title=f"{user.display_name} (@{user.username})",
                        content=user.bio,
                        metadata={
                            'user_data': asdict(user),
                            'platform': 'kick',
                            'content_type': 'user',
                            'username': user.username,
                            'display_name': user.display_name,
                            'follower_count': user.follower_count,
                            'following_count': user.following_count,
                            'verified': user.verified,
                            'partner': user.partner,
                            'total_views': user.total_views,
                            'streaming_hours': user.streaming_hours,
                            'country': user.country,
                            'social_links': user.social_links,
                            'recent_games': user.recent_games
                        },
                        timestamp=user.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Kick users: {str(e)}")
            return []
    
    async def _crawl_clips(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Kick clips"""
        try:
            results = []
            
            # Mock clip data
            mock_clips = await self._get_mock_clips(query, max_results)
            
            for clip_data in mock_clips:
                clip = await self._parse_clip_data(clip_data)
                if clip:
                    result = CrawlerResult(
                        url=f"{self.base_url}/clip/{clip.clip_id}",
                        title=f"[CLIP] {clip.title}",
                        content=clip.description,
                        metadata={
                            'clip_data': asdict(clip),
                            'platform': 'kick',
                            'content_type': 'clip',
                            'channel_name': clip.channel_name,
                            'creator_username': clip.creator_username,
                            'game_name': clip.game_name,
                            'duration_seconds': clip.duration_seconds,
                            'view_count': clip.view_count,
                            'like_count': clip.like_count,
                            'is_featured': clip.is_featured,
                            'category': clip.category,
                            'tags': clip.tags,
                            'language': clip.language,
                            'quality': clip.quality
                        },
                        timestamp=clip.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Kick clips: {str(e)}")
            return []
    
    async def _crawl_chat(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Kick chat messages"""
        try:
            results = []
            
            # Mock chat data
            mock_messages = await self._get_mock_chat_messages(query, max_results)
            
            for message_data in mock_messages:
                message = await self._parse_chat_message_data(message_data)
                if message:
                    result = CrawlerResult(
                        url=f"{self.base_url}/chat/{message.channel_id}",
                        title=f"Chat: {message.username} in {message.channel_id}",
                        content=message.content,
                        metadata={
                            'message_data': asdict(message),
                            'platform': 'kick',
                            'content_type': 'chat_message',
                            'username': message.username,
                            'channel_id': message.channel_id,
                            'is_subscriber': message.is_subscriber,
                            'is_moderator': message.is_moderator,
                            'is_vip': message.is_vip,
                            'badges': message.badges,
                            'emotes': message.emotes,
                            'message_type': message.message_type,
                            'mentions': message.mentions
                        },
                        timestamp=message.timestamp,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Kick chat: {str(e)}")
            return []
    
    async def _crawl_categories(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Kick categories"""
        try:
            results = []
            
            # Mock category data
            mock_categories = await self._get_mock_categories(query, max_results)
            
            for category_data in mock_categories:
                category = await self._parse_category_data(category_data)
                if category:
                    result = CrawlerResult(
                        url=f"{self.base_url}/categories/{category.slug}",
                        title=category.name,
                        content=category.description,
                        metadata={
                            'category_data': asdict(category),
                            'platform': 'kick',
                            'content_type': 'category',
                            'name': category.name,
                            'slug': category.slug,
                            'viewer_count': category.viewer_count,
                            'stream_count': category.stream_count,
                            'follower_count': category.follower_count,
                            'tags': category.tags,
                            'is_mature': category.is_mature,
                            'top_streamers': category.top_streamers
                        },
                        timestamp=datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Kick categories: {str(e)}")
            return []
    
    async def _crawl_live_streams(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl live Kick streams"""
        try:
            results = []
            
            # Get live streams
            live_streams = await self._get_live_streams(query, max_results, filters)
            
            for stream_data in live_streams:
                stream = await self._parse_stream_data(stream_data)
                if stream and stream.is_live:
                    result = CrawlerResult(
                        url=f"{self.base_url}/{stream.channel_name}",
                        title=f"[LIVE] {stream.title}",
                        content=stream.description,
                        metadata={
                            'stream_data': asdict(stream),
                            'platform': 'kick',
                            'content_type': 'live_stream',
                            'is_live': True,
                            'viewer_count': stream.viewer_count,
                            'game_name': stream.game_name,
                            'streamer_username': stream.streamer_username,
                            'language': stream.language
                        },
                        timestamp=stream.started_at,
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling live Kick streams: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl trending Kick content"""
        try:
            results = []
            
            # Get trending content
            trending_content = await self._get_trending_content(query, max_results, filters)
            
            for content in trending_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[TRENDING] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'trending_data': content,
                        'platform': 'kick',
                        'content_type': 'trending',
                        'is_trending': True,
                        'trend_score': content.get('trend_score', 0),
                        'category': content.get('category', 'gaming')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling trending Kick content: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Kick search"""
        try:
            results = []
            
            # Search across different content types
            streams = await self._crawl_streams(query, max_results // 3, filters)
            users = await self._crawl_users(query, max_results // 3, filters)
            clips = await self._crawl_clips(query, max_results // 3, filters)
            
            results.extend(streams)
            results.extend(users)
            results.extend(clips)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Kick search: {str(e)}")
            return []
    
    # Mock data generators (for demonstration)
    
    async def _get_mock_streams(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock stream data"""
        streams = []
        games = ['Fortnite', 'Valorant', 'League of Legends', 'Call of Duty', 'Minecraft', 'GTA V']
        
        for i in range(min(max_results, 20)):
            started_at = datetime.utcnow() - timedelta(hours=random.randint(1, 8))
            game = random.choice(games)
            streams.append({
                'id': f'stream_{i}',
                'channel_id': f'channel_{i}',
                'channel_name': f'{query.lower() if query else "streamer"}{i}',
                'streamer_username': f'{query.lower() if query else "streamer"}{i}',
                'title': f'{query} Gameplay {i}' if query else f'{game} Stream {i}',
                'description': f'Live {query} stream' if query else f'Playing {game} live!',
                'game_category': 'Gaming',
                'game_name': game,
                'viewer_count': random.randint(10, 10000),
                'follower_count': random.randint(100, 50000),
                'subscriber_count': random.randint(10, 5000),
                'is_live': random.choice([True, False]),
                'started_at': started_at.isoformat(),
                'duration_seconds': random.randint(1800, 28800) if random.choice([True, False]) else None,
                'language': random.choice(['en', 'es', 'fr', 'de', 'pt']),
                'tags': [query] if query else ['gaming', 'live', game.lower()],
                'stream_quality': random.choice(['1080p', '720p', '480p']),
                'is_mature': random.choice([True, False]),
                'country': random.choice(['US', 'BR', 'ES', 'FR', 'DE'])
            })
        
        return streams
    
    async def _get_mock_users(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock user data"""
        users = []
        
        for i in range(min(max_results, 15)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            users.append({
                'id': f'user_{i}',
                'username': f'{query.lower() if query else "gamer"}{i}',
                'display_name': f'{query} Gamer {i}' if query else f'Gamer {i}',
                'bio': f'Pro {query} player' if query else f'Gaming streamer {i}',
                'follower_count': random.randint(100, 100000),
                'following_count': random.randint(50, 1000),
                'verified': random.choice([True, False]),
                'partner': random.choice([True, False]),
                'created_at': created_at.isoformat(),
                'total_views': random.randint(1000, 1000000),
                'streaming_hours': random.randint(100, 5000),
                'country': random.choice(['US', 'BR', 'ES', 'FR', 'DE', None]),
                'social_links': {
                    'twitter': f'@{query.lower() if query else "gamer"}{i}',
                    'youtube': f'{query.lower() if query else "gamer"}{i}',
                    'instagram': f'@{query.lower() if query else "gamer"}{i}'
                },
                'recent_games': ['Fortnite', 'Valorant', 'League of Legends'][:random.randint(1, 3)]
            })
        
        return users
    
    async def _get_mock_clips(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock clip data"""
        clips = []
        
        for i in range(min(max_results, 25)):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 168))
            clips.append({
                'id': f'clip_{i}',
                'title': f'{query} Epic Moment {i}' if query else f'Epic Clip {i}',
                'channel_id': f'channel_{i}',
                'channel_name': f'{query.lower() if query else "streamer"}{i}',
                'creator_username': f'{query.lower() if query else "viewer"}{i}',
                'duration_seconds': random.randint(10, 60),
                'view_count': random.randint(100, 50000),
                'like_count': random.randint(10, 5000),
                'created_at': created_at.isoformat(),
                'game_name': random.choice(['Fortnite', 'Valorant', 'League of Legends']),
                'quality': random.choice(['1080p', '720p', '480p']),
                'language': random.choice(['en', 'es', 'fr']),
                'is_featured': random.choice([True, False]),
                'category': 'Gaming',
                'tags': [query] if query else ['epic', 'highlight', 'gaming'],
                'description': f'Amazing {query} play' if query else f'Epic gaming moment'
            })
        
        return clips
    
    async def _get_mock_chat_messages(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock chat message data"""
        messages = []
        
        for i in range(min(max_results, 50)):
            timestamp = datetime.utcnow() - timedelta(minutes=random.randint(1, 60))
            messages.append({
                'id': f'message_{i}',
                'channel_id': f'channel_{i % 10}',
                'user_id': f'user_{i}',
                'username': f'{query.lower() if query else "viewer"}{i}',
                'display_name': f'{query} Viewer {i}' if query else f'Viewer {i}',
                'content': f'Great {query} stream!' if query else f'Message content {i}',
                'timestamp': timestamp.isoformat(),
                'is_subscriber': random.choice([True, False]),
                'is_moderator': random.choice([True, False]),
                'is_vip': random.choice([True, False]),
                'badges': ['subscriber'] if random.choice([True, False]) else [],
                'emotes': [],
                'message_type': random.choice(['chat', 'donation', 'subscription']),
                'mentions': [f'@{query.lower() if query else "streamer"}'] if random.choice([True, False]) else []
            })
        
        return messages
    
    async def _get_mock_categories(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock category data"""
        categories = []
        game_categories = [
            'Action', 'Adventure', 'RPG', 'Strategy', 'Sports', 'Racing',
            'Shooter', 'Battle Royale', 'MOBA', 'MMO', 'Indie', 'Simulation'
        ]
        
        for i in range(min(max_results, 12)):
            category_name = random.choice(game_categories)
            categories.append({
                'id': f'category_{i}',
                'name': f'{query} {category_name}' if query else category_name,
                'slug': f'{query.lower() if query else "category"}-{category_name.lower()}',
                'description': f'{category_name} games featuring {query}' if query else f'{category_name} gaming category',
                'viewer_count': random.randint(1000, 100000),
                'stream_count': random.randint(10, 1000),
                'follower_count': random.randint(500, 50000),
                'tags': [query] if query else [category_name.lower(), 'gaming'],
                'is_mature': random.choice([True, False]),
                'top_streamers': [f'streamer_{j}' for j in range(5)]
            })
        
        return categories
    
    async def _get_live_streams(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get live stream data"""
        streams = await self._get_mock_streams(query, max_results)
        # Filter for live streams
        live_streams = [stream for stream in streams if stream.get('is_live', False)]
        return live_streams[:max_results]
    
    async def _get_trending_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get trending content"""
        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Trending: {query} {i}' if query else f'Trending Gaming Content {i}',
                'url': f'{self.base_url}/trending/{i}',
                'description': f'Trending {query} content' if query else f'Trending gaming description {i}',
                'trend_score': random.randint(70, 100),
                'category': 'gaming'
            })
        
        return content
    
    # Parser methods
    
    async def _parse_stream_data(self, stream_data: Dict[str, Any]) -> Optional[KickStream]:
        """Parse stream data"""
        try:
            started_at = datetime.fromisoformat(stream_data.get('started_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            stream = KickStream(
                stream_id=stream_data.get('id', ''),
                channel_id=stream_data.get('channel_id', ''),
                channel_name=stream_data.get('channel_name', ''),
                streamer_username=stream_data.get('streamer_username', ''),
                title=stream_data.get('title', ''),
                description=stream_data.get('description', ''),
                game_category=stream_data.get('game_category', ''),
                game_name=stream_data.get('game_name', ''),
                thumbnail_url='',
                viewer_count=stream_data.get('viewer_count', 0),
                follower_count=stream_data.get('follower_count', 0),
                subscriber_count=stream_data.get('subscriber_count', 0),
                is_live=stream_data.get('is_live', False),
                started_at=started_at,
                duration_seconds=stream_data.get('duration_seconds'),
                language=stream_data.get('language', 'en'),
                tags=stream_data.get('tags', []),
                stream_quality=stream_data.get('stream_quality', '720p'),
                chat_enabled=stream_data.get('chat_enabled', True),
                subscribers_only=stream_data.get('subscribers_only', False),
                follower_mode=stream_data.get('follower_mode', False),
                slow_mode=stream_data.get('slow_mode', False),
                emote_only_mode=stream_data.get('emote_only_mode', False),
                stream_url='',
                chat_url='',
                vod_url=stream_data.get('vod_url'),
                is_mature=stream_data.get('is_mature', False),
                country=stream_data.get('country', ''),
                region=stream_data.get('region', ''),
                category_id=stream_data.get('category_id', '')
            )
            
            return stream
            
        except Exception as e:
            self.logger.error(f"Error parsing stream data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[KickUser]:
        """Parse user data"""
        try:
            created_at = datetime.fromisoformat(user_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            user = KickUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                display_name=user_data.get('display_name', ''),
                bio=user_data.get('bio', ''),
                profile_picture_url='',
                banner_url=user_data.get('banner_url'),
                follower_count=user_data.get('follower_count', 0),
                following_count=user_data.get('following_count', 0),
                verified=user_data.get('verified', False),
                partner=user_data.get('partner', False),
                created_at=created_at,
                last_live=None,
                total_views=user_data.get('total_views', 0),
                streaming_hours=user_data.get('streaming_hours', 0),
                country=user_data.get('country'),
                social_links=user_data.get('social_links', {}),
                donation_link=user_data.get('donation_link'),
                instagram_handle=user_data.get('instagram_handle'),
                twitter_handle=user_data.get('twitter_handle'),
                youtube_handle=user_data.get('youtube_handle'),
                discord_server=user_data.get('discord_server'),
                website_url=user_data.get('website_url'),
                offline_banner_url=user_data.get('offline_banner_url'),
                subscription_enabled=user_data.get('subscription_enabled', False),
                chat_settings=user_data.get('chat_settings', {}),
                stream_schedule=user_data.get('stream_schedule', []),
                recent_games=user_data.get('recent_games', [])
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _parse_clip_data(self, clip_data: Dict[str, Any]) -> Optional[KickClip]:
        """Parse clip data"""
        try:
            created_at = datetime.fromisoformat(clip_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            clip = KickClip(
                clip_id=clip_data.get('id', ''),
                title=clip_data.get('title', ''),
                channel_id=clip_data.get('channel_id', ''),
                channel_name=clip_data.get('channel_name', ''),
                creator_username=clip_data.get('creator_username', ''),
                duration_seconds=clip_data.get('duration_seconds', 0),
                view_count=clip_data.get('view_count', 0),
                like_count=clip_data.get('like_count', 0),
                created_at=created_at,
                game_name=clip_data.get('game_name', ''),
                thumbnail_url='',
                video_url='',
                quality=clip_data.get('quality', '720p'),
                language=clip_data.get('language', 'en'),
                is_featured=clip_data.get('is_featured', False),
                category=clip_data.get('category', ''),
                tags=clip_data.get('tags', []),
                description=clip_data.get('description', ''),
                chat_replay_url=clip_data.get('chat_replay_url')
            )
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Error parsing clip data: {str(e)}")
            return None
    
    async def _parse_chat_message_data(self, message_data: Dict[str, Any]) -> Optional[KickChatMessage]:
        """Parse chat message data"""
        try:
            timestamp = datetime.fromisoformat(message_data.get('timestamp', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            message = KickChatMessage(
                message_id=message_data.get('id', ''),
                channel_id=message_data.get('channel_id', ''),
                user_id=message_data.get('user_id', ''),
                username=message_data.get('username', ''),
                display_name=message_data.get('display_name', ''),
                content=message_data.get('content', ''),
                timestamp=timestamp,
                is_subscriber=message_data.get('is_subscriber', False),
                is_moderator=message_data.get('is_moderator', False),
                is_vip=message_data.get('is_vip', False),
                is_broadcaster=message_data.get('is_broadcaster', False),
                badges=message_data.get('badges', []),
                emotes=message_data.get('emotes', []),
                color=message_data.get('color'),
                is_action=message_data.get('is_action', False),
                is_deleted=message_data.get('is_deleted', False),
                reply_to=message_data.get('reply_to'),
                mentions=message_data.get('mentions', []),
                message_type=message_data.get('message_type', 'chat')
            )
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error parsing chat message data: {str(e)}")
            return None
    
    async def _parse_category_data(self, category_data: Dict[str, Any]) -> Optional[KickCategory]:
        """Parse category data"""
        try:
            category = KickCategory(
                category_id=category_data.get('id', ''),
                name=category_data.get('name', ''),
                slug=category_data.get('slug', ''),
                description=category_data.get('description', ''),
                cover_image_url='',
                banner_url=category_data.get('banner_url'),
                viewer_count=category_data.get('viewer_count', 0),
                stream_count=category_data.get('stream_count', 0),
                follower_count=category_data.get('follower_count', 0),
                tags=category_data.get('tags', []),
                is_mature=category_data.get('is_mature', False),
                parent_category_id=category_data.get('parent_category_id'),
                subcategories=category_data.get('subcategories', []),
                top_streamers=category_data.get('top_streamers', []),
                trending_clips=category_data.get('trending_clips', [])
            )
            
            return category
            
        except Exception as e:
            self.logger.error(f"Error parsing category data: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Kick content"""
        try:
            # Parse Kick URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'kick',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle Kick URLs
            if 'kick.com' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 1:
                    if path_parts[0] == 'clip':
                        # Clip URL: kick.com/clip/clip_id
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'clip',
                                'clip_id': path_parts[1]
                            })
                    elif path_parts[0] == 'categories':
                        # Category URL: kick.com/categories/category_slug
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'category',
                                'category_slug': path_parts[1]
                            })
                    else:
                        # Channel URL: kick.com/channel_name
                        metadata.update({
                            'content_type': 'channel',
                            'channel_name': path_parts[0]
                        })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Kick metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Kick platform information"""
        return {
            'platform_name': 'Kick',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Live stream monitoring',
                'User profile analysis',
                'Chat message tracking',
                'Clip discovery and analysis',
                'Game category monitoring',
                'Viewership analytics',
                'Streamer performance tracking',
                'Community engagement analysis',
                'Real-time alerts',
                'Gaming trend analysis'
            ],
            'authentication': {
                'required': False,
                'type': 'API Key (Optional)',
                'scope': 'Public content access'
            },
            'content_characteristics': {
                'gaming_focused': True,
                'live_streaming': True,
                'chat_interaction': True,
                'clip_highlights': True
            },
            'limitations': [
                'Gaming content focus',
                'Limited public API',
                'Rate limiting enforced',
                'Some content requires authentication',
                'Regional restrictions may apply'
            ]
        }
