"""
Dailymotion Crawler Implementation
==================================

Advanced Dailymotion video platform crawler for European video content monitoring.
Implements comprehensive video analysis and French/European creator tracking.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  CRITICAL WARNING 
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
class DailymotionVideo:
    """Dailymotion video information"""
    video_id: str
    title: str
    description: Optional[str]
    url: str
    embed_url: str
    thumbnail_60_url: Optional[str]
    thumbnail_120_url: Optional[str] 
    thumbnail_180_url: Optional[str]
    thumbnail_240_url: Optional[str]
    thumbnail_360_url: Optional[str]
    thumbnail_480_url: Optional[str]
    thumbnail_720_url: Optional[str]
    duration: int
    created_time: datetime
    updated_time: datetime
    published_time: datetime
    views_total: int
    views_last_hour: int
    views_last_day: int
    views_last_week: int
    views_last_month: int
    comments_total: int
    bookmarks_total: int
    likes_total: int
    rating: float
    availability: str
    status: str
    language: str
    country: str
    genre: Optional[str]
    mood: Optional[str]
    tags: List[str]
    explicit: bool
    partner: bool
    private: bool
    verified: bool
    live_stream: bool
    live_publish_url: Optional[str]
    live_rtmp_url: Optional[str]
    live_hls_url: Optional[str]
    aspect_ratio: Optional[str]
    audience: str
    geoblocking: List[str]
    advertising: bool
    stream_h264_url: Optional[str]
    stream_h264_hd_url: Optional[str]
    stream_h264_hq_url: Optional[str]
    stream_h264_ld_url: Optional[str]
    stream_h264_auto_url: Optional[str]
    owner: str
    owner_id: str
    owner_screenname: str
    owner_verified: bool
    channel: Optional[str]
    channel_id: Optional[str]
    channel_name: Optional[str]
    subtitles: List[Dict[str, Any]]
    encoding_progress: int
    quality: str
    framerate: int
    aspect_ratio_value: Optional[float]


@dataclass
class DailymotionUser:
    """Dailymotion user information"""
    user_id: str
    username: str
    screenname: str
    description: Optional[str]
    url: str
    avatar_25_url: Optional[str]
    avatar_60_url: Optional[str]
    avatar_120_url: Optional[str]
    avatar_190_url: Optional[str]
    avatar_240_url: Optional[str]
    avatar_360_url: Optional[str]
    avatar_480_url: Optional[str]
    avatar_720_url: Optional[str]
    cover_25_url: Optional[str]
    cover_60_url: Optional[str]
    cover_120_url: Optional[str]
    cover_190_url: Optional[str]
    cover_240_url: Optional[str]
    cover_360_url: Optional[str]
    cover_480_url: Optional[str]
    cover_720_url: Optional[str]
    created_time: datetime
    updated_time: datetime
    country: Optional[str]
    language: Optional[str]
    verified: bool
    partner: bool
    parent: bool
    views_total: int
    videos_total: int
    followers_total: int
    following_total: int
    playlists_total: int
    channels_total: int
    groups_total: int
    favorites_total: int
    subscriptions_total: int
    status: str
    email_notification: bool
    comment_notification: bool
    video_notification: bool
    fullname: Optional[str]
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    website: Optional[str]
    facebook_url: Optional[str]
    twitter_url: Optional[str]
    google_plus_url: Optional[str]
    revenues_total: float
    estimated_revenues: float
    ad_supported: bool
    channel_page_url: Optional[str]


@dataclass
class DailymotionChannel:
    """Dailymotion channel information"""
    channel_id: str
    name: str
    description: Optional[str]
    url: str
    avatar_25_url: Optional[str]
    avatar_60_url: Optional[str]
    avatar_120_url: Optional[str]
    avatar_190_url: Optional[str]
    avatar_240_url: Optional[str]
    avatar_360_url: Optional[str]
    avatar_480_url: Optional[str]
    avatar_720_url: Optional[str]
    banner_url: Optional[str]
    created_time: datetime
    updated_time: datetime
    owner: str
    owner_id: str
    slug: str
    language: str
    tags: List[str]
    videos_total: int
    followers_total: int
    views_total: int
    layout: str
    theme: str
    videos: List[DailymotionVideo]


class DailymotionCrawler(PlatformCrawler):
    """
    Advanced Dailymotion crawler for European video content monitoring.
    
    Features:
    - Video discovery and metadata extraction
    - User/creator profile monitoring  
    - Channel and playlist tracking
    - European content focus
    - Live streaming monitoring
    - Multi-language support
    - Geographic content analysis
    - Partner content tracking
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, api_key: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "dailymotion"
        self.base_url = "https://www.dailymotion.com"
        self.api_base_url = "https://www.dailymotion.com/api"
        
        # Dailymotion API credentials
        self.api_key = api_key
        
        # Rate limiting (Dailymotion is moderate)
        self.requests_per_minute = 60
        self.min_delay = 1.0
        self.max_delay = 2.0
        
        # Content type mappings
        self.content_types = {
            'videos': self._crawl_videos,
            'users': self._crawl_users,
            'channels': self._crawl_channels,
            'search': self._crawl_search,
            'featured': self._crawl_featured,
            'most_viewed': self._crawl_most_viewed,
            'recent': self._crawl_recent,
            'live': self._crawl_live
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Dailymotion-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,de;q=0.7',
            'Origin': 'https://www.dailymotion.com',
            'Referer': 'https://www.dailymotion.com/',
            'User-Agent': 'IA-Influencer-Agent/1.0.0'
        })
    
    async def search_content(self, query: str, content_type: str = "videos", 
                           max_results: int = 50) -> List[CrawlerResult]:
        """
        Search for content on Dailymotion.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            
        Returns:
            List of crawler results
        """



        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results)
            
            self.logger.info(f"Found {len(results)} Dailymotion {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Dailymotion content: {str(e)}")
            return []
    
    async def _crawl_videos(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Dailymotion videos"""



        try:
            results = []
            
            # Search for videos
            params = {
                'search': query,
                'limit': min(max_results, 100),
                'page': 1,
                'sort': 'relevance',
                'fields': 'id,title,description,url,embed_url,thumbnail_60_url,thumbnail_120_url,thumbnail_180_url,thumbnail_240_url,thumbnail_360_url,thumbnail_480_url,thumbnail_720_url,duration,created_time,updated_time,published_time,views_total,views_last_hour,views_last_day,views_last_week,views_last_month,comments_total,bookmarks_total,likes_total,rating,availability,status,language,country,genre,mood,tags,explicit,partner,private,verified,live_stream,aspect_ratio,audience,geoblocking,advertising,owner,owner.id,owner.screenname,owner.verified,channel,channel.id,channel.name,subtitles,encoding_progress,quality,framerate'
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/videos"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for video_data in data.get('list', []):
                        # Parse video data
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.url,
                                title=video.title,
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'dailymotion',
                                    'content_type': 'video',
                                    'duration': video.duration,
                                    'views_total': video.views_total,
                                    'likes_total': video.likes_total,
                                    'comments_total': video.comments_total,
                                    'language': video.language,
                                    'country': video.country,
                                    'genre': video.genre,
                                    'explicit': video.explicit,
                                    'partner': video.partner,
                                    'verified': video.verified,
                                    'live_stream': video.live_stream
                                },
                                timestamp=video.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching videos: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion videos: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Dailymotion users"""



        try:
            results = []
            
            # Search for users
            params = {
                'search': query,
                'limit': min(max_results, 100),
                'page': 1,
                'sort': 'relevance',
                'fields': 'id,username,screenname,description,url,avatar_60_url,avatar_120_url,avatar_190_url,avatar_240_url,avatar_360_url,avatar_480_url,avatar_720_url,cover_60_url,cover_120_url,cover_190_url,cover_240_url,cover_360_url,cover_480_url,cover_720_url,created_time,updated_time,country,language,verified,partner,parent,views_total,videos_total,followers_total,following_total,playlists_total,channels_total,groups_total,favorites_total,subscriptions_total,status,fullname,address,city,postal_code,website,facebook_url,twitter_url,google_plus_url,revenues_total,estimated_revenues,ad_supported,channel_page_url'
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/users"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for user_data in data.get('list', []):
                        # Parse user data
                        user = await self._parse_user_data(user_data)
                        if user:
                            result = CrawlerResult(
                                url=user.url,
                                title=user.screenname or user.username,
                                content=user.description or '',
                                metadata={
                                    'user_data': asdict(user),
                                    'platform': 'dailymotion',
                                    'content_type': 'user',
                                    'verified': user.verified,
                                    'partner': user.partner,
                                    'videos_total': user.videos_total,
                                    'followers_total': user.followers_total,
                                    'views_total': user.views_total,
                                    'country': user.country,
                                    'language': user.language
                                },
                                timestamp=user.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching users: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion users: {str(e)}")
            return []
    
    async def _crawl_channels(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Dailymotion channels"""



        try:
            results = []
            
            # Search for channels
            params = {
                'search': query,
                'limit': min(max_results, 100),
                'page': 1,
                'sort': 'relevance',
                'fields': 'id,name,description,url,avatar_60_url,avatar_120_url,avatar_190_url,avatar_240_url,avatar_360_url,avatar_480_url,avatar_720_url,banner_url,created_time,updated_time,owner,owner.id,slug,language,tags,videos_total,followers_total,views_total,layout,theme'
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/channels"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for channel_data in data.get('list', []):
                        # Parse channel data
                        channel = await self._parse_channel_data(channel_data)
                        if channel:
                            result = CrawlerResult(
                                url=channel.url,
                                title=channel.name,
                                content=channel.description or '',
                                metadata={
                                    'channel_data': asdict(channel),
                                    'platform': 'dailymotion',
                                    'content_type': 'channel',
                                    'videos_total': channel.videos_total,
                                    'followers_total': channel.followers_total,
                                    'views_total': channel.views_total,
                                    'language': channel.language,
                                    'layout': channel.layout,
                                    'theme': channel.theme
                                },
                                timestamp=channel.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                
                else:
                    self.logger.error(f"Error fetching channels: {response.status}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion channels: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """General Dailymotion search"""



        try:
            results = []
            
            # Search across different content types
            videos = await self._crawl_videos(query, max_results // 2)
            users = await self._crawl_users(query, max_results // 4)
            channels = await self._crawl_channels(query, max_results // 4)
            
            results.extend(videos)
            results.extend(users)
            results.extend(channels)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Dailymotion search: {str(e)}")
            return []
    
    async def _crawl_featured(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl featured content"""



        try:
            results = []
            
            # Get featured videos
            params = {
                'limit': min(max_results, 100),
                'page': 1,
                'sort': 'featured',
                'fields': 'id,title,description,url,embed_url,thumbnail_240_url,duration,created_time,views_total,likes_total,comments_total,owner,owner.screenname,verified,partner'
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/videos"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for video_data in data.get('list', []):
                        # Filter by query if provided
                        if query and query.lower() not in video_data.get('title', '').lower():
                            continue
                        
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.url,
                                title=f"[FEATURED] {video.title}",
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'dailymotion',
                                    'content_type': 'featured_video',
                                    'featured': True
                                },
                                timestamp=video.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching featured content: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion featured: {str(e)}")
            return []
    
    async def _crawl_most_viewed(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl most viewed content"""



        try:
            results = []
            
            # Get most viewed videos
            params = {
                'limit': min(max_results, 100),
                'page': 1,
                'sort': 'most_viewed',
                'period': 'today',
                'fields': 'id,title,description,url,embed_url,thumbnail_240_url,duration,created_time,views_total,likes_total,comments_total,owner,owner.screenname,verified,partner'
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/videos"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for video_data in data.get('list', []):
                        # Filter by query if provided
                        if query and query.lower() not in video_data.get('title', '').lower():
                            continue
                        
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.url,
                                title=f"[MOST VIEWED] {video.title}",
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'dailymotion',
                                    'content_type': 'most_viewed_video',
                                    'trending': True,
                                    'views_rank': len(results) + 1
                                },
                                timestamp=video.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching most viewed content: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion most viewed: {str(e)}")
            return []
    
    async def _crawl_recent(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl recent content"""



        try:
            results = []
            
            # Get recent videos
            params = {
                'limit': min(max_results, 100),
                'page': 1,
                'sort': 'recent',
                'fields': 'id,title,description,url,embed_url,thumbnail_240_url,duration,created_time,views_total,likes_total,comments_total,owner,owner.screenname,verified,partner'
            }
            
            if query:
                params['search'] = query
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/videos"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for video_data in data.get('list', []):
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.url,
                                title=f"[RECENT] {video.title}",
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'dailymotion',
                                    'content_type': 'recent_video',
                                    'is_recent': True
                                },
                                timestamp=video.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching recent content: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion recent: {str(e)}")
            return []
    
    async def _crawl_live(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl live streams"""



        try:
            results = []
            
            # Get live videos
            params = {
                'limit': min(max_results, 100),
                'page': 1,
                'live_stream': 'true',
                'fields': 'id,title,description,url,embed_url,thumbnail_240_url,duration,created_time,live_stream,live_publish_url,live_rtmp_url,live_hls_url,views_total,likes_total,comments_total,owner,owner.screenname,verified,partner'
            }
            
            if query:
                params['search'] = query
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            api_url = f"{self.api_base_url}/videos"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for video_data in data.get('list', []):
                        if video_data.get('live_stream'):
                            video = await self._parse_video_data(video_data)
                            if video:
                                result = CrawlerResult(
                                    url=video.url,
                                    title=f"[LIVE] {video.title}",
                                    content=video.description or '',
                                    metadata={
                                        'video_data': asdict(video),
                                        'platform': 'dailymotion',
                                        'content_type': 'live_video',
                                        'is_live': True,
                                        'live_urls': {
                                            'publish': video.live_publish_url,
                                            'rtmp': video.live_rtmp_url,
                                            'hls': video.live_hls_url
                                        }
                                    },
                                    timestamp=video.created_time,
                                    similarity_score=0.0
                                )
                                results.append(result)
                
                else:
                    self.logger.error(f"Error fetching live streams: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Dailymotion live: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_video_data(self, video_data: Dict[str, Any]) -> Optional[DailymotionVideo]:
        """Parse video data from API response"""



        try:
            created_time = datetime.fromtimestamp(video_data.get('created_time', 0))
            updated_time = datetime.fromtimestamp(video_data.get('updated_time', 0))
            published_time = datetime.fromtimestamp(video_data.get('published_time', 0))
            
            # Parse owner data
            owner_data = video_data.get('owner', {})
            
            # Parse channel data
            channel_data = video_data.get('channel', {})
            
            video = DailymotionVideo(
                video_id=video_data.get('id', ''),
                title=video_data.get('title', ''),
                description=video_data.get('description'),
                url=video_data.get('url', ''),
                embed_url=video_data.get('embed_url', ''),
                thumbnail_60_url=video_data.get('thumbnail_60_url'),
                thumbnail_120_url=video_data.get('thumbnail_120_url'),
                thumbnail_180_url=video_data.get('thumbnail_180_url'),
                thumbnail_240_url=video_data.get('thumbnail_240_url'),
                thumbnail_360_url=video_data.get('thumbnail_360_url'),
                thumbnail_480_url=video_data.get('thumbnail_480_url'),
                thumbnail_720_url=video_data.get('thumbnail_720_url'),
                duration=video_data.get('duration', 0),
                created_time=created_time,
                updated_time=updated_time,
                published_time=published_time,
                views_total=video_data.get('views_total', 0),
                views_last_hour=video_data.get('views_last_hour', 0),
                views_last_day=video_data.get('views_last_day', 0),
                views_last_week=video_data.get('views_last_week', 0),
                views_last_month=video_data.get('views_last_month', 0),
                comments_total=video_data.get('comments_total', 0),
                bookmarks_total=video_data.get('bookmarks_total', 0),
                likes_total=video_data.get('likes_total', 0),
                rating=video_data.get('rating', 0.0),
                availability=video_data.get('availability', 'public'),
                status=video_data.get('status', 'published'),
                language=video_data.get('language', 'en'),
                country=video_data.get('country', ''),
                genre=video_data.get('genre'),
                mood=video_data.get('mood'),
                tags=video_data.get('tags', []),
                explicit=video_data.get('explicit', False),
                partner=video_data.get('partner', False),
                private=video_data.get('private', False),
                verified=video_data.get('verified', False),
                live_stream=video_data.get('live_stream', False),
                live_publish_url=video_data.get('live_publish_url'),
                live_rtmp_url=video_data.get('live_rtmp_url'),
                live_hls_url=video_data.get('live_hls_url'),
                aspect_ratio=video_data.get('aspect_ratio'),
                audience=video_data.get('audience', 'all'),
                geoblocking=video_data.get('geoblocking', []),
                advertising=video_data.get('advertising', True),
                stream_h264_url=video_data.get('stream_h264_url'),
                stream_h264_hd_url=video_data.get('stream_h264_hd_url'),
                stream_h264_hq_url=video_data.get('stream_h264_hq_url'),
                stream_h264_ld_url=video_data.get('stream_h264_ld_url'),
                stream_h264_auto_url=video_data.get('stream_h264_auto_url'),
                owner=owner_data.get('screenname', ''),
                owner_id=owner_data.get('id', ''),
                owner_screenname=owner_data.get('screenname', ''),
                owner_verified=owner_data.get('verified', False),
                channel=channel_data.get('name'),
                channel_id=channel_data.get('id'),
                channel_name=channel_data.get('name'),
                subtitles=video_data.get('subtitles', []),
                encoding_progress=video_data.get('encoding_progress', 100),
                quality=video_data.get('quality', 'auto'),
                framerate=video_data.get('framerate', 25),
                aspect_ratio_value=video_data.get('aspect_ratio_value')
            )
            
            return video
            
        except Exception as e:
            self.logger.error(f"Error parsing video data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[DailymotionUser]:
        """Parse user data from API response"""



        try:
            created_time = datetime.fromtimestamp(user_data.get('created_time', 0))
            updated_time = datetime.fromtimestamp(user_data.get('updated_time', 0))
            
            user = DailymotionUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                screenname=user_data.get('screenname', ''),
                description=user_data.get('description'),
                url=user_data.get('url', ''),
                avatar_25_url=user_data.get('avatar_25_url'),
                avatar_60_url=user_data.get('avatar_60_url'),
                avatar_120_url=user_data.get('avatar_120_url'),
                avatar_190_url=user_data.get('avatar_190_url'),
                avatar_240_url=user_data.get('avatar_240_url'),
                avatar_360_url=user_data.get('avatar_360_url'),
                avatar_480_url=user_data.get('avatar_480_url'),
                avatar_720_url=user_data.get('avatar_720_url'),
                cover_25_url=user_data.get('cover_25_url'),
                cover_60_url=user_data.get('cover_60_url'),
                cover_120_url=user_data.get('cover_120_url'),
                cover_190_url=user_data.get('cover_190_url'),
                cover_240_url=user_data.get('cover_240_url'),
                cover_360_url=user_data.get('cover_360_url'),
                cover_480_url=user_data.get('cover_480_url'),
                cover_720_url=user_data.get('cover_720_url'),
                created_time=created_time,
                updated_time=updated_time,
                country=user_data.get('country'),
                language=user_data.get('language'),
                verified=user_data.get('verified', False),
                partner=user_data.get('partner', False),
                parent=user_data.get('parent', False),
                views_total=user_data.get('views_total', 0),
                videos_total=user_data.get('videos_total', 0),
                followers_total=user_data.get('followers_total', 0),
                following_total=user_data.get('following_total', 0),
                playlists_total=user_data.get('playlists_total', 0),
                channels_total=user_data.get('channels_total', 0),
                groups_total=user_data.get('groups_total', 0),
                favorites_total=user_data.get('favorites_total', 0),
                subscriptions_total=user_data.get('subscriptions_total', 0),
                status=user_data.get('status', 'active'),
                email_notification=user_data.get('email_notification', True),
                comment_notification=user_data.get('comment_notification', True),
                video_notification=user_data.get('video_notification', True),
                fullname=user_data.get('fullname'),
                address=user_data.get('address'),
                city=user_data.get('city'),
                postal_code=user_data.get('postal_code'),
                website=user_data.get('website'),
                facebook_url=user_data.get('facebook_url'),
                twitter_url=user_data.get('twitter_url'),
                google_plus_url=user_data.get('google_plus_url'),
                revenues_total=user_data.get('revenues_total', 0.0),
                estimated_revenues=user_data.get('estimated_revenues', 0.0),
                ad_supported=user_data.get('ad_supported', False),
                channel_page_url=user_data.get('channel_page_url')
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _parse_channel_data(self, channel_data: Dict[str, Any]) -> Optional[DailymotionChannel]:
        """Parse channel data from API response"""



        try:
            created_time = datetime.fromtimestamp(channel_data.get('created_time', 0))
            updated_time = datetime.fromtimestamp(channel_data.get('updated_time', 0))
            
            # Parse owner data
            owner_data = channel_data.get('owner', {})
            
            channel = DailymotionChannel(
                channel_id=channel_data.get('id', ''),
                name=channel_data.get('name', ''),
                description=channel_data.get('description'),
                url=channel_data.get('url', ''),
                avatar_25_url=channel_data.get('avatar_25_url'),
                avatar_60_url=channel_data.get('avatar_60_url'),
                avatar_120_url=channel_data.get('avatar_120_url'),
                avatar_190_url=channel_data.get('avatar_190_url'),
                avatar_240_url=channel_data.get('avatar_240_url'),
                avatar_360_url=channel_data.get('avatar_360_url'),
                avatar_480_url=channel_data.get('avatar_480_url'),
                avatar_720_url=channel_data.get('avatar_720_url'),
                banner_url=channel_data.get('banner_url'),
                created_time=created_time,
                updated_time=updated_time,
                owner=owner_data.get('screenname', ''),
                owner_id=owner_data.get('id', ''),
                slug=channel_data.get('slug', ''),
                language=channel_data.get('language', 'en'),
                tags=channel_data.get('tags', []),
                videos_total=channel_data.get('videos_total', 0),
                followers_total=channel_data.get('followers_total', 0),
                views_total=channel_data.get('views_total', 0),
                layout=channel_data.get('layout', 'grid'),
                theme=channel_data.get('theme', 'default'),
                videos=[]  # Would need separate API call
            )
            
            return channel
            
        except Exception as e:
            self.logger.error(f"Error parsing channel data: {str(e)}")
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
        """Extract metadata from Dailymotion content"""



        try:
            # Parse Dailymotion URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'dailymotion',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Video URL pattern: dailymotion.com/video/{video_id}
            if len(path_parts) >= 2 and path_parts[0] == 'video':
                video_id = path_parts[1]
                metadata.update({
                    'video_id': video_id,
                    'content_type': 'video'
                })
            
            # User URL pattern: dailymotion.com/{username}
            elif len(path_parts) == 1 and path_parts[0]:
                username = path_parts[0]
                metadata.update({
                    'username': username,
                    'content_type': 'user'
                })
            
            # Channel URL pattern would need specific identification
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Dailymotion metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Dailymotion platform information"""



        return {
            'platform_name': 'Dailymotion',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Video discovery and metadata extraction',
                'User/creator profile monitoring',
                'Channel and playlist tracking',
                'European content focus',
                'Live streaming monitoring',
                'Multi-language support',
                'Geographic content analysis',
                'Partner content tracking'
            ],
            'authentication': {
                'required': False,
                'type': 'API Key (optional)',
                'scope': 'Enhanced access with API key'
            },
            'geographic_focus': 'European market',
            'languages': ['French', 'English', 'German', 'Spanish', 'Italian']
        }
