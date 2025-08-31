"""Dailymotion Video Crawler
Advanced industrial-grade Dailymotion crawler for video content protection and analytics
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 - All rights reserved
"""import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

import aiohttp
import pandas as pd
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class DailymotionVideo(BaseModel):
    """Dailymotion Video data model"""    video_id: str
    title: str
    description: str
    duration: int = 0  # in seconds
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    favorite_count: int = 0
    created_time: datetime
    updated_time: Optional[datetime] = None
    video_url: str
    embed_url: str
    thumbnail_url: Optional[str] = None
    poster_url: Optional[str] = None
    owner_username: str
    owner_screenname: str
    channel: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    explicit: bool = False
    private: bool = False
    password_protected: bool = False
    aspect_ratio: Optional[str] = None
    framerate: Optional[float] = None
    quality: List[str] = Field(default_factory=list)
    allow_embed: bool = True
    encoding_status: str = "ready"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DailymotionUser(BaseModel):
    """Dailymotion User data model"""    user_id: str
    username: str
    screenname: str
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    avatar_120_url: Optional[str] = None
    avatar_240_url: Optional[str] = None
    cover_250_url: Optional[str] = None
    fan_count: int = 0
    following_count: int = 0
    video_count: int = 0
    total_views: int = 0
    created_time: datetime
    verified: bool = False
    partner: bool = False
    revenue_share: bool = False
    url: str


class DailymotionChannel(BaseModel):
    """Dailymotion Channel data model"""    channel_id: str
    name: str
    description: Optional[str] = None
    slug: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_time: datetime
    updated_time: Optional[datetime] = None
    owner_username: str
    video_count: int = 0
    view_count: int = 0
    logo_120_url: Optional[str] = None
    logo_240_url: Optional[str] = None
    url: str


class DailymotionPlaylist(BaseModel):
    """Dailymotion Playlist data model"""    playlist_id: str
    name: str
    description: Optional[str] = None
    video_count: int = 0
    view_count: int = 0
    created_time: datetime
    updated_time: Optional[datetime] = None
    owner_username: str
    private: bool = False
    thumbnail_60_url: Optional[str] = None
    thumbnail_120_url: Optional[str] = None
    url: str


class DailymotionCrawler(BaseCrawler):
    """    Advanced Dailymotion crawler for comprehensive video content monitoring
    
    Features:
    - Video content analysis with detailed metadata extraction
    - User and channel profile monitoring
    - Playlist tracking and curation analysis
    - Advanced video quality and encoding analysis
    - Copyright infringement detection
    - Engagement metrics and trend analysis
    - Geographic and language-based content filtering
    - Revenue and monetization tracking for partners
    """    
    def __init__(self):
        super().__init__()
        self.platform = "dailymotion"
        self.base_url = "https://www.dailymotion.com"
        self.api_base = "https://www.dailymotion.com/api"
        self.rate_limiter = RateLimiter(
            requests_per_minute=300,  # Dailymotion API rate limit
            requests_per_hour=3000
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Video Protection)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.access_token = None
        
    async def authenticate(self, api_key: str, api_secret: str = None, access_token: str = None) -> bool:
        """Authenticate with Dailymotion API"""        try:
            if access_token:
                self.access_token = access_token
                self.session_headers['Authorization'] = f'Bearer {access_token}'
            else:
                # Use API key for read-only access
                self.session_headers['X-DM-AppKey'] = api_key
            
            # Test API access
            test_endpoint = f"{self.api_base}/videos?limit=1"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(test_endpoint) as response:
                    if response.status == 200:
                        logger.info("Successfully authenticated with Dailymotion API")
                        return True
                    else:
                        logger.error(f"Dailymotion authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Dailymotion authentication error: {str(e)}")
            return False
    
    async def search_videos(
        self,
        query: str,
        sort: str = "relevance",
        duration: str = None,
        country: str = None,
        language: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """        Search Dailymotion videos with advanced filtering
        
        Args:
            query: Search query
            sort: Sort method (relevance, recent, visited, visited-hour, visited-today, visited-week, visited-month, commented, commented-hour, commented-today, commented-week, commented-month, rated, rated-hour, rated-today, rated-week, rated-month, random)
            duration: Duration filter (short, medium, long)
            country: Country filter (ISO 3166-1 alpha-2 code)
            language: Language filter (ISO 639-1 code)
            limit: Maximum results to return
            
        Returns:
            List of matching videos
        """        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'search': query,
                'sort': sort,
                'limit': min(limit, 100),
                'fields': 'id,title,description,duration,created_time,updated_time,url,embed_url,thumbnail_120_url,thumbnail_240_url,owner,channel,tags,language,country,views_total,likes_total,comments_total,bookmarks_total,explicit,private,password_protected,aspect_ratio,framerate,available_formats,allow_embed,encoding_status'
            }
            
            if duration:
                search_params['duration'] = duration
            if country:
                search_params['country'] = country
            if language:
                search_params['language'] = language
            
            endpoint = f"{self.api_base}/videos"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = data.get('list', [])
                        
                        logger.info(f"Found {len(videos)} videos for query: {query}")
                        return videos
                    else:
                        logger.error(f"Dailymotion search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Dailymotion search error: {str(e)}")
            return []
    
    async def get_video_details(self, video_id: str) -> Optional[DailymotionVideo]:
        """Get detailed information about a specific video"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/video/{video_id}"
            params = {
                'fields': 'id,title,description,duration,created_time,updated_time,url,embed_url,thumbnail_120_url,thumbnail_240_url,thumbnail_480_url,poster_url,owner,channel,tags,language,country,views_total,likes_total,comments_total,bookmarks_total,explicit,private,password_protected,aspect_ratio,framerate,available_formats,allow_embed,encoding_status,media_type,rating'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        video_data = await response.json()
                        return await self._parse_video_data(video_data)
                    else:
                        logger.error(f"Failed to get video details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return None
    
    async def get_user_details(self, username: str) -> Optional[DailymotionUser]:
        """Get detailed information about a specific user"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/user/{username}"
            params = {
                'fields': 'id,username,screenname,description,website,location,avatar_120_url,avatar_240_url,cover_250_url,fans_total,following_total,videos_total,views_total,created_time,verified,partner,revenue_sharing_enabled,url'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return await self._parse_user_data(user_data)
                    else:
                        logger.error(f"Failed to get user details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting user details: {str(e)}")
            return None
    
    async def get_user_videos(self, username: str, limit: int = 100) -> List[DailymotionVideo]:
        """Get all videos from a specific user"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/user/{username}/videos"
            params = {
                'limit': min(limit, 100),
                'fields': 'id,title,description,duration,created_time,url,thumbnail_120_url,owner,views_total,likes_total,comments_total',
                'sort': 'recent'
            }
            
            videos = []
            page = 1
            
            while len(videos) < limit:
                params['page'] = page
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            video_list = data.get('list', [])
                            
                            if not video_list:
                                break
                            
                            for video_data in video_list:
                                video = await self._parse_video_data(video_data)
                                if video:
                                    videos.append(video)
                            
                            if not data.get('has_more', False):
                                break
                                
                            page += 1
                            await asyncio.sleep(0.2)
                        else:
                            logger.error(f"Failed to get user videos: {response.status}")
                            break
            
            logger.info(f"Retrieved {len(videos)} videos from user {username}")
            return videos[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user videos: {str(e)}")
            return []
    
    async def get_channel_details(self, channel_id: str) -> Optional[DailymotionChannel]:
        """Get detailed information about a specific channel"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/channel/{channel_id}"
            params = {
                'fields': 'id,name,description,slug,category,tags,created_time,updated_time,owner,videos_total,views_total,logo_120_url,logo_240_url,url'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        channel_data = await response.json()
                        return await self._parse_channel_data(channel_data)
                    else:
                        logger.error(f"Failed to get channel details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting channel details: {str(e)}")
            return None
    
    async def get_trending_videos(
        self,
        country: str = None,
        language: str = None,
        category: str = None,
        limit: int = 100
    ) -> List[DailymotionVideo]:
        """        Get trending videos on Dailymotion
        
        Args:
            country: Country filter
            language: Language filter
            category: Category filter
            limit: Maximum videos to return
            
        Returns:
            List of trending videos
        """        await self.rate_limiter.wait()
        
        try:
            params = {
                'sort': 'visited',
                'limit': min(limit, 100),
                'fields': 'id,title,description,duration,created_time,url,thumbnail_120_url,owner,views_total,likes_total,comments_total,tags'
            }
            
            if country:
                params['country'] = country
            if language:
                params['language'] = language
            if category:
                params['channel'] = category
            
            endpoint = f"{self.api_base}/videos"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos_data = data.get('list', [])
                        
                        videos = []
                        for video_data in videos_data:
                            video = await self._parse_video_data(video_data)
                            if video:
                                videos.append(video)
                        
                        logger.info(f"Retrieved {len(videos)} trending videos")
                        return videos
                    else:
                        logger.error(f"Failed to get trending videos: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting trending videos: {str(e)}")
            return []
    
    async def get_video_comments(self, video_id: str, limit: int = 100) -> List[Dict]:
        """Get comments from a specific video"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/video/{video_id}/comments"
            params = {
                'limit': min(limit, 100),
                'fields': 'id,message,created_time,owner,likes_total'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        comments = data.get('list', [])
                        
                        logger.info(f"Retrieved {len(comments)} comments from video {video_id}")
                        return comments
                    else:
                        logger.error(f"Failed to get video comments: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting video comments: {str(e)}")
            return []
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """        Monitor Dailymotion for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_videos(query, limit=50)
                
                for result in results:
                    video = await self._parse_video_data(result)
                    if video:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, video
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="dailymotion",
                                content_id=video.video_id,
                                url=video.video_url,
                                title=video.title,
                                description=video.description,
                                creator=video.owner_username,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type="video",
                                metadata={
                                    'duration': video.duration,
                                    'view_count': video.view_count,
                                    'like_count': video.like_count,
                                    'embed_url': video.embed_url,
                                    'language': video.language,
                                    'country': video.country,
                                    'explicit': video.explicit
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Dailymotion")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Dailymotion content infringement: {str(e)}")
            return []
    
    async def analyze_video_performance(self, video_id: str) -> Dict[str, Any]:
        """        Analyze video performance metrics and engagement
        
        Args:
            video_id: Dailymotion video ID
            
        Returns:
            Comprehensive performance analysis
        """        try:
            video = await self.get_video_details(video_id)
            if not video:
                return {}
            
            comments = await self.get_video_comments(video_id, limit=100)
            
            # Calculate performance metrics
            video_age_days = (datetime.utcnow() - video.created_time).days
            if video_age_days == 0:
                video_age_days = 1
            
            views_per_day = video.view_count / video_age_days
            engagement_rate = (video.like_count + video.comment_count + video.favorite_count) / max(video.view_count, 1)
            
            performance_analysis = {
                'video_id': video.video_id,
                'basic_metrics': {
                    'views': video.view_count,
                    'likes': video.like_count,
                    'comments': video.comment_count,
                    'favorites': video.favorite_count
                },
                'engagement_metrics': {
                    'engagement_rate': engagement_rate,
                    'views_per_day': views_per_day,
                    'virality_score': self._calculate_virality_score(video),
                    'comment_ratio': video.comment_count / max(video.view_count, 1) * 1000  # Comments per 1000 views
                },
                'content_analysis': {
                    'duration_category': self._categorize_duration(video.duration),
                    'title_optimization_score': self._analyze_title_optimization(video.title),
                    'description_quality_score': self._analyze_description_quality(video.description),
                    'tag_count': len(video.tags),
                    'language': video.language,
                    'country': video.country
                },
                'technical_quality': {
                    'available_qualities': video.quality,
                    'aspect_ratio': video.aspect_ratio,
                    'framerate': video.framerate,
                    'encoding_status': video.encoding_status,
                    'embed_allowed': video.allow_embed
                },
                'temporal_analysis': {
                    'video_age_days': video_age_days,
                    'created_time': video.created_time.isoformat(),
                    'last_updated': video.updated_time.isoformat() if video.updated_time else None
                },
                'content_flags': {
                    'explicit': video.explicit,
                    'private': video.private,
                    'password_protected': video.password_protected
                },
                'performance_category': self._categorize_performance(video),
                'optimization_suggestions': self._generate_optimization_suggestions(video)
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video performance: {str(e)}")
            return {}
    
    async def analyze_content_trends(
        self,
        country: str = None,
        language: str = None,
        time_period: str = "week",
        limit: int = 100
    ) -> Dict[str, Any]:
        """        Analyze content trends on Dailymotion
        
        Args:
            country: Country filter for trend analysis
            language: Language filter for trend analysis
            time_period: Time period for analysis
            limit: Maximum videos to analyze
            
        Returns:
            Comprehensive trend analysis
        """        try:
            # Get trending videos for analysis
            trending_videos = await self.get_trending_videos(country, language, limit=limit)
            
            if not trending_videos:
                return {}
            
            # Analyze trends
            trends_analysis = {
                'analysis_metadata': {
                    'country': country,
                    'language': language,
                    'time_period': time_period,
                    'videos_analyzed': len(trending_videos)
                },
                'content_trends': {
                    'avg_duration': sum(v.duration for v in trending_videos) / len(trending_videos),
                    'avg_views': sum(v.view_count for v in trending_videos) / len(trending_videos),
                    'avg_engagement': sum(v.like_count + v.comment_count for v in trending_videos) / len(trending_videos),
                    'explicit_content_percentage': len([v for v in trending_videos if v.explicit]) / len(trending_videos) * 100
                },
                'duration_distribution': await self._analyze_duration_distribution(trending_videos),
                'language_distribution': await self._analyze_language_distribution(trending_videos),
                'tag_trends': await self._analyze_tag_trends(trending_videos),
                'top_creators': await self._identify_top_creators(trending_videos),
                'engagement_patterns': await self._analyze_engagement_patterns(trending_videos),
                'quality_trends': await self._analyze_quality_trends(trending_videos),
                'geographic_insights': await self._analyze_geographic_distribution(trending_videos)
            }
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content trends: {str(e)}")
            return {}
    
    async def bulk_video_analysis(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple videos in bulk for efficiency"""        results = []
        
        # Process videos in batches to respect rate limits
        batch_size = 20
        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i + batch_size]
            
            batch_tasks = [self.analyze_video_performance(video_id) for video_id in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, dict) and result:
                    results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in bulk analysis: {str(result)}")
            
            # Rate limiting between batches
            await asyncio.sleep(1)
        
        return results
    
    async def _parse_video_data(self, video_data: Dict) -> Optional[DailymotionVideo]:
        """Parse Dailymotion API video data into DailymotionVideo model"""        try:
            # Parse owner information
            owner_info = video_data.get('owner', {})
            
            # Parse available formats/quality
            available_formats = video_data.get('available_formats', [])
            quality_list = []
            if isinstance(available_formats, list):
                quality_list = [fmt for fmt in available_formats if isinstance(fmt, str)]
            
            # Parse creation and update times
            created_time = datetime.fromtimestamp(video_data.get('created_time', 0))
            updated_time = None
            if video_data.get('updated_time'):
                updated_time = datetime.fromtimestamp(video_data['updated_time'])
            
            video = DailymotionVideo(
                video_id=video_data.get('id', ''),
                title=video_data.get('title', ''),
                description=video_data.get('description', ''),
                duration=video_data.get('duration', 0),
                view_count=video_data.get('views_total', 0),
                like_count=video_data.get('likes_total', 0),
                comment_count=video_data.get('comments_total', 0),
                favorite_count=video_data.get('bookmarks_total', 0),
                created_time=created_time,
                updated_time=updated_time,
                video_url=video_data.get('url', ''),
                embed_url=video_data.get('embed_url', ''),
                thumbnail_url=video_data.get('thumbnail_240_url') or video_data.get('thumbnail_120_url'),
                poster_url=video_data.get('poster_url'),
                owner_username=owner_info.get('username', '') if isinstance(owner_info, dict) else str(owner_info),
                owner_screenname=owner_info.get('screenname', '') if isinstance(owner_info, dict) else '',
                channel=video_data.get('channel'),
                language=video_data.get('language'),
                country=video_data.get('country'),
                tags=video_data.get('tags', []) if isinstance(video_data.get('tags'), list) else [],
                explicit=video_data.get('explicit', False),
                private=video_data.get('private', False),
                password_protected=video_data.get('password_protected', False),
                aspect_ratio=video_data.get('aspect_ratio'),
                framerate=video_data.get('framerate'),
                quality=quality_list,
                allow_embed=video_data.get('allow_embed', True),
                encoding_status=video_data.get('encoding_status', 'ready'),
                metadata={
                    'media_type': video_data.get('media_type'),
                    'rating': video_data.get('rating'),
                    'audience': video_data.get('audience'),
                    'mode': video_data.get('mode')
                }
            )
            
            return video
            
        except Exception as e:
            logger.error(f"Error parsing video data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict) -> Optional[DailymotionUser]:
        """Parse Dailymotion API user data into DailymotionUser model"""        try:
            created_time = datetime.fromtimestamp(user_data.get('created_time', 0))
            
            user = DailymotionUser(
                user_id=user_data.get('id', ''),
                username=user_data.get('username', ''),
                screenname=user_data.get('screenname', ''),
                description=user_data.get('description'),
                website=user_data.get('website'),
                location=user_data.get('location'),
                avatar_120_url=user_data.get('avatar_120_url'),
                avatar_240_url=user_data.get('avatar_240_url'),
                cover_250_url=user_data.get('cover_250_url'),
                fan_count=user_data.get('fans_total', 0),
                following_count=user_data.get('following_total', 0),
                video_count=user_data.get('videos_total', 0),
                total_views=user_data.get('views_total', 0),
                created_time=created_time,
                verified=user_data.get('verified', False),
                partner=user_data.get('partner', False),
                revenue_share=user_data.get('revenue_sharing_enabled', False),
                url=user_data.get('url', '')
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    async def _parse_channel_data(self, channel_data: Dict) -> Optional[DailymotionChannel]:
        """Parse Dailymotion API channel data into DailymotionChannel model"""        try:
            created_time = datetime.fromtimestamp(channel_data.get('created_time', 0))
            updated_time = None
            if channel_data.get('updated_time'):
                updated_time = datetime.fromtimestamp(channel_data['updated_time'])
            
            # Parse owner information
            owner_info = channel_data.get('owner', {})
            owner_username = owner_info.get('username', '') if isinstance(owner_info, dict) else str(owner_info)
            
            channel = DailymotionChannel(
                channel_id=channel_data.get('id', ''),
                name=channel_data.get('name', ''),
                description=channel_data.get('description'),
                slug=channel_data.get('slug', ''),
                category=channel_data.get('category'),
                tags=channel_data.get('tags', []) if isinstance(channel_data.get('tags'), list) else [],
                created_time=created_time,
                updated_time=updated_time,
                owner_username=owner_username,
                video_count=channel_data.get('videos_total', 0),
                view_count=channel_data.get('views_total', 0),
                logo_120_url=channel_data.get('logo_120_url'),
                logo_240_url=channel_data.get('logo_240_url'),
                url=channel_data.get('url', '')
            )
            
            return channel
            
        except Exception as e:
            logger.error(f"Error parsing channel data: {str(e)}")
            return None
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'description' in protected_content:
            # Extract key phrases from description
            words = protected_content['description'].split()
            if len(words) > 5:
                queries.append(' '.join(words[:10]))
        
        if 'tags' in protected_content:
            queries.extend(protected_content['tags'][:3])
        
        if 'creator' in protected_content:
            queries.append(protected_content['creator'])
        
        return queries[:5]
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        video: DailymotionVideo
    ) -> float:
        """Calculate similarity between protected content and Dailymotion video"""        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and video.title:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                video.title.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.4)
        
        # Description similarity
        if 'description' in protected_content and video.description:
            desc_similarity = SequenceMatcher(
                None,
                protected_content['description'].lower(),
                video.description.lower()
            ).ratio()
            similarity_scores.append(desc_similarity * 0.3)
        
        # Tag similarity
        if 'tags' in protected_content and video.tags:
            protected_tags = set(tag.lower() for tag in protected_content['tags'])
            video_tags = set(tag.lower() for tag in video.tags)
            
            if protected_tags and video_tags:
                tag_similarity = len(protected_tags.intersection(video_tags)) / len(protected_tags.union(video_tags))
                similarity_scores.append(tag_similarity * 0.2)
        
        # Duration similarity (within 10% tolerance)
        if 'duration' in protected_content and video.duration:
            duration_diff = abs(protected_content['duration'] - video.duration)
            duration_tolerance = protected_content['duration'] * 0.1
            if duration_diff <= duration_tolerance:
                duration_similarity = 1.0 - (duration_diff / protected_content['duration'])
                similarity_scores.append(duration_similarity * 0.1)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _calculate_virality_score(self, video: DailymotionVideo) -> float:
        """Calculate video virality score"""        video_age_days = (datetime.utcnow() - video.created_time).days
        if video_age_days == 0:
            video_age_days = 1
        
        views_per_day = video.view_count / video_age_days
        engagement_score = video.like_count + video.comment_count + video.favorite_count
        engagement_rate = engagement_score / max(video.view_count, 1)
        
        # Normalize and combine metrics
        virality_score = (views_per_day * 0.6 + engagement_score * 0.4) * engagement_rate
        
        return min(virality_score, 10000)  # Cap at 10000
    
    def _categorize_duration(self, duration: int) -> str:
        """Categorize video duration"""        if duration < 60:
            return "very_short"
        elif duration < 300:
            return "short"
        elif duration < 1200:
            return "medium"
        elif duration < 3600:
            return "long"
        else:
            return "very_long"
    
    def _analyze_title_optimization(self, title: str) -> float:
        """Analyze title optimization score"""        if not title:
            return 0.0
        
        score = 0.0
        
        # Length optimization (40-70 characters is optimal for Dailymotion)
        if 30 <= len(title) <= 80:
            score += 0.3
        
        # Word count (6-12 words is optimal)
        word_count = len(title.split())
        if 4 <= word_count <= 15:
            score += 0.3
        
        # Contains engaging words
        engaging_words = ['amazing', 'incredible', 'best', 'top', 'ultimate', 'must', 'watch']
        if any(word.lower() in title.lower() for word in engaging_words):
            score += 0.2
        
        # Not all caps
        if not title.isupper():
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_description_quality(self, description: str) -> float:
        """Analyze description quality score"""        if not description:
            return 0.0
        
        score = 0.0
        
        # Length (100-300 words is optimal)
        word_count = len(description.split())
        if 50 <= word_count <= 400:
            score += 0.4
        
        # Contains keywords or hashtags
        if '#' in description or any(word in description.lower() for word in ['subscribe', 'like', 'comment', 'share']):
            score += 0.3
        
        # Contains links or mentions
        if 'http' in description or '@' in description:
            score += 0.2
        
        # Good structure (sentences, paragraphs)
        if '.' in description and len(description.split('.')) > 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _categorize_performance(self, video: DailymotionVideo) -> str:
        """Categorize video performance level"""        views = video.view_count
        engagement = video.like_count + video.comment_count + video.favorite_count
        
        if views > 1000000 and engagement > 10000:
            return "viral"
        elif views > 100000 and engagement > 1000:
            return "high"
        elif views > 10000 and engagement > 100:
            return "medium"
        else:
            return "low"
    
    def _generate_optimization_suggestions(self, video: DailymotionVideo) -> List[str]:
        """Generate optimization suggestions for video"""        suggestions = []
        
        if len(video.title) < 30:
            suggestions.append("Consider expanding the title for better SEO")
        
        if len(video.description) < 100:
            suggestions.append("Add more detailed description for better discoverability")
        
        if len(video.tags) < 3:
            suggestions.append("Add more relevant tags to improve categorization")
        
        if not video.thumbnail_url:
            suggestions.append("Add a custom thumbnail to increase click-through rate")
        
        if video.view_count < 100:
            suggestions.append("Promote video on social media for initial traction")
        
        if not video.allow_embed:
            suggestions.append("Enable embedding to increase video reach")
        
        return suggestions
    
    async def _analyze_duration_distribution(self, videos: List[DailymotionVideo]) -> Dict[str, Any]:
        """Analyze duration distribution in videos"""        durations = [v.duration for v in videos if v.duration > 0]
        
        if not durations:
            return {}
        
        avg_duration = sum(durations) / len(durations)
        short_videos = len([d for d in durations if d < 300])  # < 5 minutes
        medium_videos = len([d for d in durations if 300 <= d <= 1200])  # 5-20 minutes
        long_videos = len([d for d in durations if d > 1200])  # > 20 minutes
        
        return {
            'average_duration_seconds': avg_duration,
            'average_duration_minutes': avg_duration / 60,
            'short_videos_percentage': (short_videos / len(durations)) * 100,
            'medium_videos_percentage': (medium_videos / len(durations)) * 100,
            'long_videos_percentage': (long_videos / len(durations)) * 100,
            'total_analyzed': len(durations)
        }
    
    async def _analyze_language_distribution(self, videos: List[DailymotionVideo]) -> Dict[str, int]:
        """Analyze language distribution in videos"""        language_counts = {}
        
        for video in videos:
            language = video.language or 'unknown'
            language_counts[language] = language_counts.get(language, 0) + 1
        
        return dict(sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    async def _analyze_tag_trends(self, videos: List[DailymotionVideo]) -> Dict[str, int]:
        """Analyze trending tags in videos"""        tag_counts = {}
        
        for video in videos:
            for tag in video.tags:
                tag_lower = tag.lower()
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
        
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20])
    
    async def _identify_top_creators(self, videos: List[DailymotionVideo]) -> List[Dict[str, Any]]:
        """Identify top creators from trending videos"""        creator_stats = {}
        
        for video in videos:
            creator = video.owner_username
            if creator not in creator_stats:
                creator_stats[creator] = {
                    'video_count': 0,
                    'total_views': 0,
                    'total_engagement': 0
                }
            
            creator_stats[creator]['video_count'] += 1
            creator_stats[creator]['total_views'] += video.view_count
            creator_stats[creator]['total_engagement'] += video.like_count + video.comment_count + video.favorite_count
        
        # Sort by total engagement
        top_creators = sorted(
            creator_stats.items(),
            key=lambda x: x[1]['total_engagement'],
            reverse=True
        )[:10]
        
        return [
            {
                'username': creator,
                'video_count': stats['video_count'],
                'total_views': stats['total_views'],
                'total_engagement': stats['total_engagement'],
                'avg_views_per_video': stats['total_views'] // stats['video_count'],
                'avg_engagement_per_video': stats['total_engagement'] // stats['video_count']
            }
            for creator, stats in top_creators
        ]
    
    async def _analyze_engagement_patterns(self, videos: List[DailymotionVideo]) -> Dict[str, Any]:
        """Analyze engagement patterns in videos"""        if not videos:
            return {}
        
        view_counts = [v.view_count for v in videos]
        like_counts = [v.like_count for v in videos]
        comment_counts = [v.comment_count for v in videos]
        
        return {
            'avg_views': sum(view_counts) / len(view_counts),
            'avg_likes': sum(like_counts) / len(like_counts),
            'avg_comments': sum(comment_counts) / len(comment_counts),
            'like_to_view_ratio': sum(like_counts) / sum(view_counts) if sum(view_counts) > 0 else 0,
            'comment_to_view_ratio': sum(comment_counts) / sum(view_counts) if sum(view_counts) > 0 else 0,
            'engagement_rate': (sum(like_counts) + sum(comment_counts)) / sum(view_counts) if sum(view_counts) > 0 else 0
        }
    
    async def _analyze_quality_trends(self, videos: List[DailymotionVideo]) -> Dict[str, Any]:
        """Analyze video quality trends"""        quality_analysis = {
            'hd_percentage': 0,
            'uhd_percentage': 0,
            'avg_qualities_per_video': 0,
            'encoding_status_distribution': {}
        }
        
        hd_count = 0
        uhd_count = 0
        total_qualities = 0
        encoding_counts = {}
        
        for video in videos:
            # Check for HD/UHD qualities
            if any('720' in q or '1080' in q for q in video.quality):
                hd_count += 1
            if any('1440' in q or '2160' in q or '4k' in q.lower() for q in video.quality):
                uhd_count += 1
            
            total_qualities += len(video.quality)
            
            # Count encoding statuses
            status = video.encoding_status
            encoding_counts[status] = encoding_counts.get(status, 0) + 1
        
        if videos:
            quality_analysis.update({
                'hd_percentage': (hd_count / len(videos)) * 100,
                'uhd_percentage': (uhd_count / len(videos)) * 100,
                'avg_qualities_per_video': total_qualities / len(videos),
                'encoding_status_distribution': encoding_counts
            })
        
        return quality_analysis
    
    async def _analyze_geographic_distribution(self, videos: List[DailymotionVideo]) -> Dict[str, int]:
        """Analyze geographic distribution of videos"""        country_counts = {}
        
        for video in videos:
            country = video.country or 'unknown'
            country_counts[country] = country_counts.get(country, 0) + 1
        
        return dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:15])
