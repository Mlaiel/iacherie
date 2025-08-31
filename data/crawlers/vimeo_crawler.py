"""Vimeo Crawler Implementation
============================

Advanced Vimeo video platform crawler for professional video content monitoring.
Implements comprehensive video analysis and creator tracking.

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
"""import asyncio
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
class VimeoVideo:
    """Vimeo video information"""    video_id: str
    name: str
    description: Optional[str]
    uri: str
    link: str
    embed_html: str
    duration: int
    width: int
    height: int
    language: Optional[str]
    created_time: datetime
    modified_time: datetime
    release_time: datetime
    content_rating: List[str]
    rating_mod_locked: bool
    license: Optional[str]
    privacy: Dict[str, Any]
    pictures: Dict[str, Any]
    tags: List[Dict[str, Any]]
    stats: Dict[str, int]  # plays, likes, comments
    categories: List[Dict[str, Any]]
    uploader: Dict[str, Any]
    metadata: Dict[str, Any]
    user: Dict[str, Any]
    app: Optional[Dict[str, Any]]
    status: str
    resource_key: str
    upload: Dict[str, Any]
    transcode: Dict[str, Any]
    is_playable: bool
    has_audio: bool
    last_user_action_event_date: Optional[datetime]
    files: List[Dict[str, Any]]
    download: List[Dict[str, Any]]
    play: Dict[str, Any]
    review_page: Dict[str, Any]
    parent_folder: Optional[Dict[str, Any]]
    last_user_action_event_date: Optional[datetime]
    spatial: Optional[Dict[str, Any]]
    live: Optional[Dict[str, Any]]
    type: str  # video, live
    password: Optional[str]
    review_link: Optional[str]
    version: str


@dataclass
class VimeoUser:
    """Vimeo user information"""    user_id: str
    uri: str
    name: str
    link: str
    location: Optional[str]
    gender: Optional[str]
    bio: Optional[str]
    short_bio: Optional[str]
    created_time: datetime
    pictures: Dict[str, Any]
    websites: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    location_details: Optional[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    available_for_hire: bool
    can_work_remotely: bool
    preferences: Dict[str, Any]
    content_filter: List[str]
    upload_quota: Dict[str, Any]
    resource_key: str
    account: str  # basic, plus, pro, business, premium
    verified: bool
    followers_count: int
    following_count: int
    video_count: int
    album_count: int
    channel_count: int
    portfolio_count: int
    group_count: int
    is_staff: bool
    can_search_public: bool
    videos: List[VimeoVideo]


@dataclass
class VimeoChannel:
    """Vimeo channel information"""    channel_id: str
    uri: str
    name: str
    description: Optional[str]
    link: str
    created_time: datetime
    modified_time: datetime
    user: Dict[str, Any]
    pictures: Dict[str, Any]
    header: Dict[str, Any]
    privacy: Dict[str, Any]
    metadata: Dict[str, Any]
    resource_key: str
    tags: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]
    layout: str
    theme: str
    video_count: int
    videos: List[VimeoVideo]


class VimeoCrawler(PlatformCrawler):
    """    Advanced Vimeo crawler for professional video content monitoring.
    
    Features:
    - Video discovery and metadata extraction
    - User/creator profile monitoring
    - Channel and showcase tracking
    - Professional video analytics
    - High-quality video fingerprinting
    - Privacy-aware content access
    - Live streaming monitoring
    - Portfolio and showcase analysis
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, access_token: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "vimeo"
        self.base_url = "https://vimeo.com"
        self.api_base_url = "https://api.vimeo.com"
        
        # Vimeo API credentials
        self.access_token = access_token
        
        # Rate limiting (Vimeo is professional)
        self.requests_per_minute = 100
        self.min_delay = 0.6
        self.max_delay = 1.5
        
        # Content type mappings
        self.content_types = {
            'videos': self._crawl_videos,
            'users': self._crawl_users,
            'channels': self._crawl_channels,
            'search': self._crawl_search,
            'featured': self._crawl_featured,
            'staff_picks': self._crawl_staff_picks,
            'categories': self._crawl_categories,
            'live': self._crawl_live
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Vimeo-specific headers"""        self.session_headers.update({
            'Accept': 'application/vnd.vimeo.*+json;version=3.4',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://vimeo.com',
            'Referer': 'https://vimeo.com/',
            'User-Agent': 'IA-Influencer-Agent/1.0.0'
        })
        
        if self.access_token:
            self.session_headers['Authorization'] = f'Bearer {self.access_token}'
    
    async def search_content(self, query: str, content_type: str = "videos", 
                           max_results: int = 50) -> List[CrawlerResult]:
        """        Search for content on Vimeo.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            
        Returns:
            List of crawler results
        """        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results)
            
            self.logger.info(f"Found {len(results)} Vimeo {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Vimeo content: {str(e)}")
            return []
    
    async def _crawl_videos(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Vimeo videos"""        try:
            results = []
            
            # Search for videos
            params = {
                'query': query,
                'per_page': min(max_results, 50),
                'page': 1,
                'sort': 'relevant',
                'direction': 'desc',
                'filter': 'embeddable',
                'filter_embeddable': 'true'
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
                        # Parse video data
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.link,
                                title=video.name,
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'vimeo',
                                    'content_type': 'video',
                                    'duration': video.duration,
                                    'resolution': f"{video.width}x{video.height}",
                                    'plays': video.stats.get('plays', 0),
                                    'likes': video.stats.get('likes', 0),
                                    'comments': video.stats.get('comments', 0),
                                    'privacy': video.privacy,
                                    'content_rating': video.content_rating,
                                    'categories': video.categories
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
            self.logger.error(f"Error crawling Vimeo videos: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Vimeo users"""        try:
            results = []
            
            # Search for users
            params = {
                'query': query,
                'per_page': min(max_results, 50),
                'page': 1,
                'sort': 'relevant'
            }
            
            api_url = f"{self.api_base_url}/users"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for user_data in data.get('data', []):
                        # Parse user data
                        user = await self._parse_user_data(user_data)
                        if user:
                            result = CrawlerResult(
                                url=user.link,
                                title=user.name,
                                content=user.bio or user.short_bio or '',
                                metadata={
                                    'user_data': asdict(user),
                                    'platform': 'vimeo',
                                    'content_type': 'user',
                                    'account_type': user.account,
                                    'verified': user.verified,
                                    'video_count': user.video_count,
                                    'followers_count': user.followers_count,
                                    'following_count': user.following_count,
                                    'available_for_hire': user.available_for_hire,
                                    'can_work_remotely': user.can_work_remotely,
                                    'is_staff': user.is_staff
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
            self.logger.error(f"Error crawling Vimeo users: {str(e)}")
            return []
    
    async def _crawl_channels(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl Vimeo channels"""        try:
            results = []
            
            # Search for channels
            params = {
                'query': query,
                'per_page': min(max_results, 50),
                'page': 1,
                'sort': 'relevant'
            }
            
            api_url = f"{self.api_base_url}/channels"
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for channel_data in data.get('data', []):
                        # Parse channel data
                        channel = await self._parse_channel_data(channel_data)
                        if channel:
                            result = CrawlerResult(
                                url=channel.link,
                                title=channel.name,
                                content=channel.description or '',
                                metadata={
                                    'channel_data': asdict(channel),
                                    'platform': 'vimeo',
                                    'content_type': 'channel',
                                    'video_count': channel.video_count,
                                    'layout': channel.layout,
                                    'theme': channel.theme,
                                    'privacy': channel.privacy,
                                    'categories': channel.categories
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
            self.logger.error(f"Error crawling Vimeo channels: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """General Vimeo search"""        try:
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
            self.logger.error(f"Error performing Vimeo search: {str(e)}")
            return []
    
    async def _crawl_featured(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl featured content"""        try:
            results = []
            
            # Get featured videos
            params = {
                'per_page': min(max_results, 50),
                'page': 1,
                'filter': 'featured'
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
                        # Filter by query if provided
                        if query and query.lower() not in video_data.get('name', '').lower():
                            continue
                        
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.link,
                                title=f"[FEATURED] {video.name}",
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'vimeo',
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
            self.logger.error(f"Error crawling Vimeo featured: {str(e)}")
            return []
    
    async def _crawl_staff_picks(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl staff picks"""        try:
            results = []
            
            # Get staff pick videos
            api_url = f"{self.api_base_url}/channels/staffpicks/videos"
            params = {
                'per_page': min(max_results, 50),
                'page': 1
            }
            
            async with self.session.get(
                api_url,
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for video_data in data.get('data', []):
                        # Filter by query if provided
                        if query and query.lower() not in video_data.get('name', '').lower():
                            continue
                        
                        video = await self._parse_video_data(video_data)
                        if video:
                            result = CrawlerResult(
                                url=video.link,
                                title=f"[STAFF PICK] {video.name}",
                                content=video.description or '',
                                metadata={
                                    'video_data': asdict(video),
                                    'platform': 'vimeo',
                                    'content_type': 'staff_pick',
                                    'staff_pick': True
                                },
                                timestamp=video.created_time,
                                similarity_score=0.0
                            )
                            results.append(result)
                
                else:
                    self.logger.error(f"Error fetching staff picks: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Vimeo staff picks: {str(e)}")
            return []
    
    async def _crawl_categories(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl by categories"""        try:
            results = []
            
            # Get categories first
            api_url = f"{self.api_base_url}/categories"
            
            async with self.session.get(
                api_url,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    categories_data = await response.json()
                    
                    for category in categories_data.get('data', []):
                        category_name = category.get('name', '').lower()
                        if query and query.lower() not in category_name:
                            continue
                        
                        # Get videos from this category
                        category_uri = category.get('uri', '')
                        videos_url = f"{self.api_base_url}{category_uri}/videos"
                        
                        params = {
                            'per_page': min(max_results // 5, 20),
                            'page': 1
                        }
                        
                        async with self.session.get(
                            videos_url,
                            params=params,
                            headers=self.session_headers
                        ) as videos_response:
                            if videos_response.status == 200:
                                videos_data = await videos_response.json()
                                
                                for video_data in videos_data.get('data', []):
                                    video = await self._parse_video_data(video_data)
                                    if video:
                                        result = CrawlerResult(
                                            url=video.link,
                                            title=f"[{category.get('name')}] {video.name}",
                                            content=video.description or '',
                                            metadata={
                                                'video_data': asdict(video),
                                                'platform': 'vimeo',
                                                'content_type': 'category_video',
                                                'category': category.get('name'),
                                                'category_uri': category_uri
                                            },
                                            timestamp=video.created_time,
                                            similarity_score=0.0
                                        )
                                        results.append(result)
                                        
                                        if len(results) >= max_results:
                                            return results
                        
                        # Rate limiting
                        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Vimeo categories: {str(e)}")
            return []
    
    async def _crawl_live(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl live streams"""        try:
            results = []
            
            # Search for live videos
            params = {
                'query': query,
                'per_page': min(max_results, 50),
                'page': 1,
                'filter': 'live'
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
                        if video_data.get('type') == 'live':
                            video = await self._parse_video_data(video_data)
                            if video:
                                result = CrawlerResult(
                                    url=video.link,
                                    title=f"[LIVE] {video.name}",
                                    content=video.description or '',
                                    metadata={
                                        'video_data': asdict(video),
                                        'platform': 'vimeo',
                                        'content_type': 'live_video',
                                        'is_live': True,
                                        'live_data': video.live
                                    },
                                    timestamp=video.created_time,
                                    similarity_score=0.0
                                )
                                results.append(result)
                
                else:
                    self.logger.error(f"Error fetching live streams: {response.status}")
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Vimeo live: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_video_data(self, video_data: Dict[str, Any]) -> Optional[VimeoVideo]:
        """Parse video data from API response"""        try:
            created_time = datetime.fromisoformat(video_data.get('created_time', '').replace('Z', '+00:00'))
            modified_time = datetime.fromisoformat(video_data.get('modified_time', '').replace('Z', '+00:00'))
            release_time = datetime.fromisoformat(video_data.get('release_time', '').replace('Z', '+00:00'))
            
            video = VimeoVideo(
                video_id=str(video_data.get('id', '')),
                name=video_data.get('name', ''),
                description=video_data.get('description'),
                uri=video_data.get('uri', ''),
                link=video_data.get('link', ''),
                embed_html=video_data.get('embed', {}).get('html', ''),
                duration=video_data.get('duration', 0),
                width=video_data.get('width', 0),
                height=video_data.get('height', 0),
                language=video_data.get('language'),
                created_time=created_time,
                modified_time=modified_time,
                release_time=release_time,
                content_rating=video_data.get('content_rating', []),
                rating_mod_locked=video_data.get('rating_mod_locked', False),
                license=video_data.get('license'),
                privacy=video_data.get('privacy', {}),
                pictures=video_data.get('pictures', {}),
                tags=video_data.get('tags', []),
                stats=video_data.get('stats', {}),
                categories=video_data.get('categories', []),
                uploader=video_data.get('uploader', {}),
                metadata=video_data.get('metadata', {}),
                user=video_data.get('user', {}),
                app=video_data.get('app'),
                status=video_data.get('status', 'available'),
                resource_key=video_data.get('resource_key', ''),
                upload=video_data.get('upload', {}),
                transcode=video_data.get('transcode', {}),
                is_playable=video_data.get('is_playable', True),
                has_audio=video_data.get('has_audio', True),
                last_user_action_event_date=None,  # Would need parsing
                files=video_data.get('files', []),
                download=video_data.get('download', []),
                play=video_data.get('play', {}),
                review_page=video_data.get('review_page', {}),
                parent_folder=video_data.get('parent_folder'),
                spatial=video_data.get('spatial'),
                live=video_data.get('live'),
                type=video_data.get('type', 'video'),
                password=video_data.get('password'),
                review_link=video_data.get('review_link'),
                version=video_data.get('version', '1.0')
            )
            
            return video
            
        except Exception as e:
            self.logger.error(f"Error parsing video data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict[str, Any]) -> Optional[VimeoUser]:
        """Parse user data from API response"""        try:
            created_time = datetime.fromisoformat(user_data.get('created_time', '').replace('Z', '+00:00'))
            
            user = VimeoUser(
                user_id=str(user_data.get('id', '')),
                uri=user_data.get('uri', ''),
                name=user_data.get('name', ''),
                link=user_data.get('link', ''),
                location=user_data.get('location'),
                gender=user_data.get('gender'),
                bio=user_data.get('bio'),
                short_bio=user_data.get('short_bio'),
                created_time=created_time,
                pictures=user_data.get('pictures', {}),
                websites=user_data.get('websites', []),
                metadata=user_data.get('metadata', {}),
                location_details=user_data.get('location_details'),
                skills=user_data.get('skills', []),
                available_for_hire=user_data.get('available_for_hire', False),
                can_work_remotely=user_data.get('can_work_remotely', False),
                preferences=user_data.get('preferences', {}),
                content_filter=user_data.get('content_filter', []),
                upload_quota=user_data.get('upload_quota', {}),
                resource_key=user_data.get('resource_key', ''),
                account=user_data.get('account', 'basic'),
                verified=user_data.get('verified', False),
                followers_count=user_data.get('metadata', {}).get('connections', {}).get('followers', {}).get('total', 0),
                following_count=user_data.get('metadata', {}).get('connections', {}).get('following', {}).get('total', 0),
                video_count=user_data.get('metadata', {}).get('connections', {}).get('videos', {}).get('total', 0),
                album_count=user_data.get('metadata', {}).get('connections', {}).get('albums', {}).get('total', 0),
                channel_count=user_data.get('metadata', {}).get('connections', {}).get('channels', {}).get('total', 0),
                portfolio_count=user_data.get('metadata', {}).get('connections', {}).get('portfolios', {}).get('total', 0),
                group_count=user_data.get('metadata', {}).get('connections', {}).get('groups', {}).get('total', 0),
                is_staff=user_data.get('is_staff', False),
                can_search_public=user_data.get('can_search_public', True),
                videos=[]  # Would need separate API call
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _parse_channel_data(self, channel_data: Dict[str, Any]) -> Optional[VimeoChannel]:
        """Parse channel data from API response"""        try:
            created_time = datetime.fromisoformat(channel_data.get('created_time', '').replace('Z', '+00:00'))
            modified_time = datetime.fromisoformat(channel_data.get('modified_time', '').replace('Z', '+00:00'))
            
            channel = VimeoChannel(
                channel_id=str(channel_data.get('id', '')),
                uri=channel_data.get('uri', ''),
                name=channel_data.get('name', ''),
                description=channel_data.get('description'),
                link=channel_data.get('link', ''),
                created_time=created_time,
                modified_time=modified_time,
                user=channel_data.get('user', {}),
                pictures=channel_data.get('pictures', {}),
                header=channel_data.get('header', {}),
                privacy=channel_data.get('privacy', {}),
                metadata=channel_data.get('metadata', {}),
                resource_key=channel_data.get('resource_key', ''),
                tags=channel_data.get('tags', []),
                categories=channel_data.get('categories', []),
                layout=channel_data.get('layout', 'grid'),
                theme=channel_data.get('theme', 'standard'),
                video_count=channel_data.get('metadata', {}).get('connections', {}).get('videos', {}).get('total', 0),
                videos=[]  # Would need separate API call
            )
            
            return channel
            
        except Exception as e:
            self.logger.error(f"Error parsing channel data: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""        try:
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
        """Extract metadata from Vimeo content"""        try:
            # Parse Vimeo URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'vimeo',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Video URL pattern: vimeo.com/{video_id}
            if len(path_parts) == 1 and path_parts[0].isdigit():
                video_id = path_parts[0]
                metadata.update({
                    'video_id': video_id,
                    'content_type': 'video'
                })
            
            # Channel URL pattern: vimeo.com/channels/{channel_name}
            elif len(path_parts) >= 2 and path_parts[0] == 'channels':
                channel_name = path_parts[1]
                metadata.update({
                    'channel_name': channel_name,
                    'content_type': 'channel'
                })
            
            # User URL pattern: vimeo.com/{username}
            elif len(path_parts) == 1 and not path_parts[0].isdigit():
                username = path_parts[0]
                metadata.update({
                    'username': username,
                    'content_type': 'user'
                })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Vimeo metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Vimeo platform information"""        return {
            'platform_name': 'Vimeo',
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
                'Channel and showcase tracking',
                'Professional video analytics',
                'High-quality video fingerprinting',
                'Privacy-aware content access',
                'Live streaming monitoring',
                'Portfolio and showcase analysis'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth2 Access Token',
                'scope': 'Read-only access'
            },
            'content_quality': 'Professional/High-quality',
            'privacy_support': True
        }
