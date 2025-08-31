"""
Rumble Video Crawler
Advanced industrial-grade Rumble crawler for video content protection and analytics
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 - All rights reserved
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse, quote

import aiohttp
from bs4 import BeautifulSoup
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


class RumbleVideo(BaseModel):
    """Rumble Video data model"""
    video_id: str
    title: str
    description: str
    duration: int = 0  # in seconds
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    upload_date: datetime
    last_updated: Optional[datetime] = None
    video_url: str
    embed_url: str
    thumbnail_url: Optional[str] = None
    poster_url: Optional[str] = None
    uploader: str
    uploader_id: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    country: Optional[str] = None
    quality_levels: List[str] = Field(default_factory=list)
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    bitrate: Optional[int] = None
    fps: Optional[int] = None
    resolution: Optional[str] = None
    file_size: Optional[int] = None
    monetized: bool = False
    live_stream: bool = False
    premiere: bool = False
    age_restricted: bool = False
    geographical_restrictions: List[str] = Field(default_factory=list)
    license_type: Optional[str] = None
    copyright_claim: bool = False
    content_warnings: List[str] = Field(default_factory=list)
    engagement_rate: float = 0.0
    trending_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RumbleChannel(BaseModel):
    """Rumble Channel data model"""
    channel_id: str
    name: str
    username: str
    description: Optional[str] = None
    subscriber_count: int = 0
    video_count: int = 0
    total_views: int = 0
    created_date: datetime
    last_active: Optional[datetime] = None
    verified: bool = False
    partner: bool = False
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    channel_url: str
    website: Optional[str] = None
    location: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    social_links: Dict[str, str] = Field(default_factory=dict)
    upload_frequency: float = 0.0  # videos per week
    average_views: float = 0.0
    engagement_rate: float = 0.0
    growth_rate: float = 0.0
    content_style: List[str] = Field(default_factory=list)
    collaboration_count: int = 0
    controversy_score: float = 0.0


class RumblePlaylist(BaseModel):
    """Rumble Playlist data model"""
    playlist_id: str
    title: str
    description: Optional[str] = None
    creator: str
    creator_id: Optional[str] = None
    video_count: int = 0
    total_duration: int = 0
    view_count: int = 0
    created_date: datetime
    updated_date: Optional[datetime] = None
    public: bool = True
    thumbnail_url: Optional[str] = None
    url: str
    videos: List[str] = Field(default_factory=list)


class RumbleLiveStream(BaseModel):
    """Rumble Live Stream data model"""
    stream_id: str
    title: str
    description: Optional[str] = None
    streamer: str
    streamer_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    current_viewers: int = 0
    peak_viewers: int = 0
    total_viewers: int = 0
    chat_message_count: int = 0
    super_chat_revenue: float = 0.0
    stream_url: str
    thumbnail_url: Optional[str] = None
    quality_options: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    mature_content: bool = False
    stream_status: str = "live"  # live, ended, scheduled
    language: Optional[str] = None


class RumbleCrawler(BaseCrawler):
    """
    Advanced Rumble crawler for comprehensive video content monitoring
    
    Features:
    - Video content analysis with metadata extraction
    - Channel monitoring and growth analytics
    - Live stream tracking and performance metrics
    - Trending content identification and analysis
    - Copyright infringement detection
    - Political and controversial content analysis
    - Engagement metrics and audience insights
    - Monetization and revenue tracking
    - Content moderation and safety analysis
    - Alternative platform migration tracking
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "rumble"
        self.base_url = "https://rumble.com"
        self.api_base = "https://rumble.com/api"
        self.rate_limiter = RateLimiter(
            requests_per_minute=180,  # Conservative rate limiting
            requests_per_hour=2500
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Video Protection)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    async def authenticate(self, username: str = None, password: str = None) -> bool:
        """Authenticate with Rumble (optional for basic access)"""



        try:
            if username and password:
                login_data = {
                    'username': username,
                    'password': password
                }
                
                login_url = f"{self.base_url}/login"
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.post(login_url, data=login_data) as response:
                        if response.status == 200:
                            # Check if login was successful
                            html_content = await response.text()
                            if "dashboard" in html_content.lower() or "logout" in html_content.lower():
                                logger.info("Successfully authenticated with Rumble")
                                return True
                            else:
                                logger.error("Rumble authentication failed - invalid credentials")
                                return False
                        else:
                            logger.error(f"Rumble authentication failed: {response.status}")
                            return False
            else:
                logger.info("Using Rumble without authentication (public access)")
                return True
                
        except Exception as e:
            logger.error(f"Rumble authentication error: {str(e)}")
            return False
    
    async def search_videos(
        self,
        query: str,
        sort: str = "relevance",
        upload_date: str = None,
        duration: str = None,
        quality: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search Rumble videos with filtering options
        
        Args:
            query: Search query
            sort: Sort method (relevance, upload_date, view_count, rating)
            upload_date: Upload date filter (hour, today, week, month, year)
            duration: Duration filter (short, medium, long)
            quality: Quality filter (hd, 4k)
            limit: Maximum results to return
            
        Returns:
            List of matching videos
        """
        await self.rate_limiter.wait()
        
        try:
            search_url = f"{self.base_url}/search/video"
            
            params = {
                'q': query,
                'sort': sort
            }
            
            if upload_date:
                params['date'] = upload_date
            if duration:
                params['duration'] = duration
            if quality:
                params['quality'] = quality
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        videos = await self._parse_search_results(html_content)
                        
                        logger.info(f"Found {len(videos)} videos for query: {query}")
                        return videos[:limit]
                    else:
                        logger.error(f"Rumble search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Rumble search error: {str(e)}")
            return []
    
    async def get_video_details(self, video_id: str) -> Optional[RumbleVideo]:
        """Get detailed information about a specific video"""
        await self.rate_limiter.wait()
        
        try:
            video_url = f"{self.base_url}/v{video_id}"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        video_data = await self._parse_video_page(html_content, video_id)
                        return await self._create_video_model(video_data)
                    else:
                        logger.error(f"Failed to get video details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return None
    
    async def get_channel_details(self, channel_id: str) -> Optional[RumbleChannel]:
        """Get detailed information about a specific channel"""
        await self.rate_limiter.wait()
        
        try:
            channel_url = f"{self.base_url}/c/{channel_id}"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(channel_url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        channel_data = await self._parse_channel_page(html_content, channel_id)
                        return await self._create_channel_model(channel_data)
                    else:
                        logger.error(f"Failed to get channel details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting channel details: {str(e)}")
            return None
    
    async def get_channel_videos(self, channel_id: str, limit: int = 100) -> List[RumbleVideo]:
        """Get all videos from a specific channel"""
        await self.rate_limiter.wait()
        
        try:
            videos_url = f"{self.base_url}/c/{channel_id}/videos"
            
            videos = []
            page = 1
            
            while len(videos) < limit:
                params = {'page': page}
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(videos_url, params=params) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            page_videos = await self._parse_channel_videos_page(html_content)
                            
                            if not page_videos:
                                break
                            
                            for video_data in page_videos:
                                video = await self._create_video_model(video_data)
                                if video:
                                    videos.append(video)
                            
                            page += 1
                            await asyncio.sleep(0.5)  # Be respectful with pagination
                        else:
                            logger.error(f"Failed to get channel videos: {response.status}")
                            break
            
            logger.info(f"Retrieved {len(videos)} videos from channel {channel_id}")
            return videos[:limit]
            
        except Exception as e:
            logger.error(f"Error getting channel videos: {str(e)}")
            return []
    
    async def get_trending_videos(
        self,
        category: str = None,
        time_period: str = "today",
        limit: int = 50
    ) -> List[RumbleVideo]:
        """
        Get trending videos on Rumble
        
        Args:
            category: Category filter
            time_period: Time period (today, week, month, all_time)
            limit: Maximum videos to return
            
        Returns:
            List of trending videos
        """
        await self.rate_limiter.wait()
        
        try:
            trending_url = f"{self.base_url}/trending"
            
            params = {}
            if category:
                params['category'] = category
            if time_period:
                params['period'] = time_period
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(trending_url, params=params) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        videos_data = await self._parse_trending_page(html_content)
                        
                        videos = []
                        for video_data in videos_data[:limit]:
                            video = await self._create_video_model(video_data)
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
    
    async def get_live_streams(self, category: str = None, limit: int = 20) -> List[RumbleLiveStream]:
        """Get current live streams on Rumble"""
        await self.rate_limiter.wait()
        
        try:
            live_url = f"{self.base_url}/live"
            
            params = {}
            if category:
                params['category'] = category
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(live_url, params=params) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        streams_data = await self._parse_live_streams_page(html_content)
                        
                        streams = []
                        for stream_data in streams_data[:limit]:
                            stream = await self._create_live_stream_model(stream_data)
                            if stream:
                                streams.append(stream)
                        
                        logger.info(f"Retrieved {len(streams)} live streams")
                        return streams
                    else:
                        logger.error(f"Failed to get live streams: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting live streams: {str(e)}")
            return []
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """
        Monitor Rumble for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """
        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_videos(query, limit=30)
                
                for result in results:
                    video = await self._create_video_model(result)
                    if video:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, video
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="rumble",
                                content_id=video.video_id,
                                url=video.video_url,
                                title=video.title,
                                description=video.description,
                                creator=video.uploader,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type="video",
                                metadata={
                                    'duration': video.duration,
                                    'view_count': video.view_count,
                                    'upload_date': video.upload_date.isoformat(),
                                    'channel': video.channel,
                                    'categories': video.categories,
                                    'tags': video.tags,
                                    'quality_levels': video.quality_levels,
                                    'monetized': video.monetized,
                                    'age_restricted': video.age_restricted
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Rumble")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Rumble content infringement: {str(e)}")
            return []
    
    async def analyze_video_performance(self, video_id: str) -> Dict[str, Any]:
        """
        Analyze video performance metrics and engagement
        
        Args:
            video_id: Rumble video ID
            
        Returns:
            Comprehensive performance analysis
        """



        try:
            video = await self.get_video_details(video_id)
            if not video:
                return {}
            
            # Calculate performance metrics
            video_age_days = (datetime.utcnow() - video.upload_date).days
            if video_age_days == 0:
                video_age_days = 1
            
            views_per_day = video.view_count / video_age_days
            engagement_score = video.like_count + video.comment_count
            engagement_rate = engagement_score / max(video.view_count, 1)
            
            performance_analysis = {
                'video_id': video.video_id,
                'basic_metrics': {
                    'views': video.view_count,
                    'likes': video.like_count,
                    'dislikes': video.dislike_count,
                    'comments': video.comment_count,
                    'engagement_rate': engagement_rate
                },
                'growth_metrics': {
                    'views_per_day': views_per_day,
                    'viral_coefficient': self._calculate_viral_coefficient(video),
                    'trending_score': video.trending_score,
                    'growth_velocity': self._calculate_growth_velocity(video)
                },
                'content_analysis': {
                    'duration_category': self._categorize_duration(video.duration),
                    'quality_score': self._calculate_quality_score(video),
                    'content_safety_score': self._calculate_content_safety_score(video),
                    'categories': video.categories,
                    'tags': video.tags
                },
                'technical_metrics': {
                    'quality_levels': video.quality_levels,
                    'resolution': video.resolution,
                    'fps': video.fps,
                    'bitrate': video.bitrate,
                    'file_size': video.file_size
                },
                'monetization_analysis': {
                    'monetized': video.monetized,
                    'revenue_potential': self._estimate_revenue_potential(video),
                    'advertiser_friendliness': self._assess_advertiser_friendliness(video)
                },
                'audience_insights': {
                    'demographic_appeal': await self._analyze_demographic_appeal(video),
                    'geographic_performance': await self._analyze_geographic_performance(video),
                    'discovery_sources': await self._analyze_discovery_sources(video)
                },
                'optimization_recommendations': self._generate_video_optimization_recommendations(video)
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video performance: {str(e)}")
            return {}
    
    async def analyze_channel_growth(self, channel_id: str) -> Dict[str, Any]:
        """
        Analyze channel growth and performance metrics
        
        Args:
            channel_id: Rumble channel ID
            
        Returns:
            Comprehensive channel growth analysis
        """



        try:
            channel = await self.get_channel_details(channel_id)
            if not channel:
                return {}
            
            recent_videos = await self.get_channel_videos(channel_id, limit=50)
            
            growth_analysis = {
                'channel_id': channel.channel_id,
                'channel_profile': {
                    'name': channel.name,
                    'subscribers': channel.subscriber_count,
                    'total_videos': channel.video_count,
                    'total_views': channel.total_views,
                    'verified': channel.verified,
                    'partner': channel.partner
                },
                'growth_metrics': {
                    'subscriber_growth_rate': channel.growth_rate,
                    'upload_frequency': channel.upload_frequency,
                    'average_views_per_video': channel.average_views,
                    'engagement_rate': channel.engagement_rate,
                    'view_to_subscriber_ratio': channel.total_views / max(channel.subscriber_count, 1)
                },
                'content_analysis': {
                    'content_consistency': self._analyze_content_consistency(recent_videos),
                    'video_performance_distribution': self._analyze_video_performance_distribution(recent_videos),
                    'optimal_upload_timing': await self._analyze_optimal_upload_timing(recent_videos),
                    'content_diversification': self._analyze_content_diversification(recent_videos)
                },
                'audience_development': {
                    'audience_retention': await self._analyze_audience_retention(channel_id),
                    'community_engagement': await self._analyze_community_engagement(channel_id),
                    'cross_platform_presence': self._analyze_cross_platform_presence(channel)
                },
                'competitive_analysis': {
                    'market_position': await self._determine_channel_market_position(channel),
                    'competitive_advantages': self._identify_channel_competitive_advantages(channel),
                    'growth_opportunities': self._identify_growth_opportunities(channel)
                },
                'monetization_potential': {
                    'current_monetization': await self._analyze_current_monetization(channel_id),
                    'revenue_optimization': self._suggest_revenue_optimization(channel),
                    'brand_partnership_potential': self._assess_brand_partnership_potential(channel)
                },
                'strategic_recommendations': {
                    'content_strategy': self._generate_content_strategy_recommendations(channel, recent_videos),
                    'growth_tactics': self._generate_growth_tactics(channel),
                    'optimization_priorities': self._prioritize_optimization_efforts(channel)
                }
            }
            
            return growth_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing channel growth: {str(e)}")
            return {}
    
    async def track_platform_trends(
        self,
        category: str = None,
        time_period: str = "week",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze overall platform trends on Rumble
        
        Args:
            category: Category filter for trend analysis
            time_period: Time period for analysis
            limit: Maximum content to analyze
            
        Returns:
            Comprehensive platform trend analysis
        """



        try:
            trending_videos = await self.get_trending_videos(category, time_period, limit)
            live_streams = await self.get_live_streams(category, limit=20)
            
            trends_analysis = {
                'analysis_metadata': {
                    'category': category,
                    'time_period': time_period,
                    'videos_analyzed': len(trending_videos),
                    'streams_analyzed': len(live_streams)
                },
                'content_trends': {
                    'trending_categories': await self._analyze_trending_categories(trending_videos),
                    'viral_content_patterns': await self._analyze_viral_patterns(trending_videos),
                    'content_length_trends': await self._analyze_content_length_trends(trending_videos),
                    'quality_trends': await self._analyze_platform_quality_trends(trending_videos)
                },
                'creator_ecosystem': {
                    'emerging_creators': await self._identify_emerging_creators(trending_videos),
                    'creator_diversity': await self._analyze_creator_diversity(trending_videos),
                    'collaboration_networks': await self._analyze_collaboration_networks(trending_videos)
                },
                'engagement_patterns': {
                    'engagement_distribution': await self._analyze_engagement_distribution(trending_videos),
                    'comment_sentiment_trends': await self._analyze_comment_sentiment_trends(trending_videos),
                    'viral_threshold_analysis': await self._analyze_viral_thresholds(trending_videos)
                },
                'live_streaming_insights': {
                    'stream_popularity': await self._analyze_stream_popularity(live_streams),
                    'streaming_categories': await self._analyze_streaming_categories(live_streams),
                    'audience_engagement_live': await self._analyze_live_engagement(live_streams)
                },
                'platform_health': {
                    'content_diversity_score': self._calculate_content_diversity_score(trending_videos),
                    'creator_economy_health': self._assess_creator_economy_health(trending_videos),
                    'content_quality_index': self._calculate_content_quality_index(trending_videos)
                },
                'migration_analysis': {
                    'youtube_migration_patterns': await self._analyze_youtube_migration(trending_videos),
                    'creator_onboarding_trends': await self._analyze_creator_onboarding(trending_videos),
                    'platform_loyalty_metrics': await self._analyze_platform_loyalty(trending_videos)
                },
                'predictions': {
                    'emerging_trends': await self._predict_emerging_trends(trending_videos),
                    'growth_opportunities': await self._identify_platform_growth_opportunities(trending_videos),
                    'content_gap_analysis': await self._perform_content_gap_analysis(trending_videos)
                }
            }
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"Error tracking platform trends: {str(e)}")
            return {}
    
    # HTML Parsing Methods
    async def _parse_search_results(self, html_content: str) -> List[Dict]:
        """Parse search results from Rumble HTML"""



        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # Look for video containers
            video_containers = soup.find_all('div', class_=re.compile(r'video-listing|video-item|listing-video'))
            
            for container in video_containers:
                try:
                    result_data = {}
                    
                    # Extract video ID and URL
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        result_data['url'] = urljoin(self.base_url, href)
                        result_data['video_id'] = self._extract_video_id_from_url(href)
                    
                    # Extract title
                    title_elem = container.find(['h3', 'h4', 'span'], class_=re.compile(r'title|video-title'))
                    if title_elem:
                        result_data['title'] = title_elem.get_text(strip=True)
                    
                    # Extract uploader
                    uploader_elem = container.find(['span', 'div', 'a'], class_=re.compile(r'channel|uploader|author'))
                    if uploader_elem:
                        result_data['uploader'] = uploader_elem.get_text(strip=True)
                    
                    # Extract view count
                    views_elem = container.find(['span', 'div'], class_=re.compile(r'views|view-count'))
                    if views_elem:
                        views_text = views_elem.get_text(strip=True)
                        result_data['view_count'] = self._parse_count(views_text)
                    
                    # Extract duration
                    duration_elem = container.find(['span', 'div'], class_=re.compile(r'duration|time'))
                    if duration_elem:
                        duration_text = duration_elem.get_text(strip=True)
                        result_data['duration'] = self._parse_duration(duration_text)
                    
                    # Extract thumbnail
                    img_elem = container.find('img', src=True)
                    if img_elem:
                        result_data['thumbnail_url'] = img_elem['src']
                    
                    # Extract upload date
                    date_elem = container.find(['span', 'time'], class_=re.compile(r'date|uploaded|ago'))
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        result_data['upload_date'] = self._parse_relative_date(date_text)
                    
                    if result_data.get('video_id') and result_data.get('title'):
                        results.append(result_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing search result: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}")
            return []
    
    async def _parse_video_page(self, html_content: str, video_id: str) -> Dict:
        """Parse video page HTML for detailed information"""



        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            video_data = {'video_id': video_id}
            
            # Extract title
            title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'media-heading|video-title|title'))
            if title_elem:
                video_data['title'] = title_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description|video-description'))
            if desc_elem:
                video_data['description'] = desc_elem.get_text(strip=True)
            
            # Extract uploader
            uploader_elem = soup.find(['a', 'span'], class_=re.compile(r'channel|uploader'))
            if uploader_elem:
                video_data['uploader'] = uploader_elem.get_text(strip=True)
                if uploader_elem.name == 'a' and uploader_elem.get('href'):
                    video_data['channel_id'] = self._extract_channel_id_from_url(uploader_elem['href'])
            
            # Extract view count
            views_elem = soup.find(['span', 'div'], class_=re.compile(r'views'))
            if views_elem:
                views_text = views_elem.get_text(strip=True)
                video_data['view_count'] = self._parse_count(views_text)
            
            # Extract like/dislike counts
            like_elem = soup.find(['span', 'button'], class_=re.compile(r'like'))
            if like_elem:
                like_text = like_elem.get_text(strip=True)
                video_data['like_count'] = self._parse_count(like_text)
            
            dislike_elem = soup.find(['span', 'button'], class_=re.compile(r'dislike'))
            if dislike_elem:
                dislike_text = dislike_elem.get_text(strip=True)
                video_data['dislike_count'] = self._parse_count(dislike_text)
            
            # Extract upload date
            date_elem = soup.find(['time', 'span'], class_=re.compile(r'uploaded|date'))
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                video_data['upload_date'] = self._parse_date(date_text)
            
            # Extract duration from video player
            duration_elem = soup.find(['span'], class_=re.compile(r'duration'))
            if duration_elem:
                duration_text = duration_elem.get_text(strip=True)
                video_data['duration'] = self._parse_duration(duration_text)
            
            # Extract tags
            tag_elems = soup.find_all(['a', 'span'], class_=re.compile(r'tag'))
            video_data['tags'] = [elem.get_text(strip=True) for elem in tag_elems]
            
            # Extract video URLs
            video_data['video_url'] = f"{self.base_url}/v{video_id}"
            video_data['embed_url'] = f"{self.base_url}/embed/{video_id}"
            
            # Extract thumbnail
            img_elem = soup.find('img', src=True, class_=re.compile(r'thumbnail|poster'))
            if img_elem:
                video_data['thumbnail_url'] = img_elem['src']
            
            return video_data
            
        except Exception as e:
            logger.error(f"Error parsing video page: {str(e)}")
            return {'video_id': video_id}
    
    def _extract_video_id_from_url(self, url: str) -> str:
        """Extract video ID from Rumble URL"""



        try:
            # Rumble video URLs: /v[video_id] or /video/[video_id]
            match = re.search(r'/v([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
            
            match = re.search(r'/video/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
            
            return url.split('/')[-1] if '/' in url else url
            
        except Exception as e:
            logger.error(f"Error extracting video ID: {str(e)}")
            return ""
    
    def _extract_channel_id_from_url(self, url: str) -> str:
        """Extract channel ID from Rumble URL"""



        try:
            # Rumble channel URLs: /c/[channel_id] or /user/[username]
            match = re.search(r'/c/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
            
            match = re.search(r'/user/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
            
            return url.split('/')[-1] if '/' in url else url
            
        except Exception as e:
            logger.error(f"Error extracting channel ID: {str(e)}")
            return ""
    
    def _parse_count(self, count_text: str) -> int:
        """Parse count string (e.g., '1.2K', '10M') to integer"""



        try:
            if not count_text:
                return 0
            
            # Remove non-numeric characters except K, M, B
            clean_text = re.sub(r'[^\d.KMB]', '', count_text.upper())
            
            match = re.search(r'([\d.]+)([KMB]?)', clean_text)
            if match:
                number = float(match.group(1))
                multiplier = match.group(2)
                
                if multiplier == 'K':
                    return int(number * 1000)
                elif multiplier == 'M':
                    return int(number * 1000000)
                elif multiplier == 'B':
                    return int(number * 1000000000)
                else:
                    return int(number)
            
            return 0
            
        except Exception as e:
            logger.debug(f"Error parsing count: {str(e)}")
            return 0
    
    def _parse_duration(self, duration_text: str) -> int:
        """Parse duration string to seconds"""



        try:
            if not duration_text:
                return 0
            
            # Extract time components
            time_parts = re.findall(r'\d+', duration_text)
            
            if len(time_parts) == 1:
                return int(time_parts[0])  # Assume seconds
            elif len(time_parts) == 2:
                return int(time_parts[0]) * 60 + int(time_parts[1])  # MM:SS
            elif len(time_parts) == 3:
                return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])  # HH:MM:SS
            
            return 0
            
        except Exception as e:
            logger.debug(f"Error parsing duration: {str(e)}")
            return 0
    
    def _parse_date(self, date_text: str) -> datetime:
        """Parse date string to datetime object"""



        try:
            if not date_text:
                return datetime.utcnow()
            
            # Handle relative dates
            if 'ago' in date_text.lower():
                return self._parse_relative_date(date_text)
            
            # Try various date formats
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%B %d, %Y',
                '%d %B %Y'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_text.strip(), fmt)
                except ValueError:
                    continue
            
            return datetime.utcnow()
            
        except Exception as e:
            logger.debug(f"Error parsing date: {str(e)}")
            return datetime.utcnow()
    
    def _parse_relative_date(self, relative_text: str) -> datetime:
        """Parse relative date (e.g., '2 hours ago', '3 days ago')"""



        try:
            now = datetime.utcnow()
            
            # Extract number and unit
            match = re.search(r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s*ago', relative_text.lower())
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'second':
                    return now - timedelta(seconds=amount)
                elif unit == 'minute':
                    return now - timedelta(minutes=amount)
                elif unit == 'hour':
                    return now - timedelta(hours=amount)
                elif unit == 'day':
                    return now - timedelta(days=amount)
                elif unit == 'week':
                    return now - timedelta(weeks=amount)
                elif unit == 'month':
                    return now - timedelta(days=amount * 30)
                elif unit == 'year':
                    return now - timedelta(days=amount * 365)
            
            return now
            
        except Exception as e:
            logger.debug(f"Error parsing relative date: {str(e)}")
            return datetime.utcnow()
    
    async def _create_video_model(self, video_data: Dict) -> Optional[RumbleVideo]:
        """Create RumbleVideo model from parsed data"""



        try:
            video = RumbleVideo(
                video_id=video_data.get('video_id', ''),
                title=video_data.get('title', ''),
                description=video_data.get('description', ''),
                duration=video_data.get('duration', 0),
                view_count=video_data.get('view_count', 0),
                like_count=video_data.get('like_count', 0),
                dislike_count=video_data.get('dislike_count', 0),
                comment_count=video_data.get('comment_count', 0),
                upload_date=video_data.get('upload_date', datetime.utcnow()),
                video_url=video_data.get('video_url', ''),
                embed_url=video_data.get('embed_url', ''),
                thumbnail_url=video_data.get('thumbnail_url'),
                uploader=video_data.get('uploader', ''),
                channel_id=video_data.get('channel_id'),
                tags=video_data.get('tags', []),
                metadata=video_data
            )
            
            return video
            
        except Exception as e:
            logger.error(f"Error creating video model: {str(e)}")
            return None
    
    # Placeholder implementations for analysis methods
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""
        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'description' in protected_content:
            words = protected_content['description'].split()
            if len(words) > 5:
                queries.append(' '.join(words[:8]))
        
        if 'creator' in protected_content:
            queries.append(protected_content['creator'])
        
        return queries[:3]
    
    async def _calculate_content_similarity(self, protected_content: Dict, video: RumbleVideo) -> float:
        """Calculate similarity between protected content and Rumble video"""
        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and video.title:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                video.title.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.5)
        
        # Description similarity
        if 'description' in protected_content and video.description:
            desc_similarity = SequenceMatcher(
                None,
                protected_content['description'].lower(),
                video.description.lower()
            ).ratio()
            similarity_scores.append(desc_similarity * 0.3)
        
        # Duration similarity
        if 'duration' in protected_content and video.duration:
            duration_diff = abs(protected_content['duration'] - video.duration)
            duration_tolerance = protected_content['duration'] * 0.1
            if duration_diff <= duration_tolerance:
                duration_similarity = 1.0 - (duration_diff / protected_content['duration'])
                similarity_scores.append(duration_similarity * 0.2)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    # Helper methods for analysis
    def _calculate_viral_coefficient(self, video: RumbleVideo) -> float:
        """Calculate viral coefficient for video"""
        if video.view_count < 1000:
            return 0.0
        
        video_age_days = (datetime.utcnow() - video.upload_date).days
        if video_age_days == 0:
            video_age_days = 1
        
        views_per_day = video.view_count / video_age_days
        engagement_score = video.like_count + video.comment_count
        
        return min(views_per_day * engagement_score / 10000, 10.0)
    
    def _categorize_duration(self, duration: int) -> str:
        """Categorize video duration"""
        if duration < 60:
            return "very_short"
        elif duration < 300:
            return "short"
        elif duration < 1200:
            return "medium"
        elif duration < 3600:
            return "long"
        else:
            return "very_long"
    
    def _calculate_quality_score(self, video: RumbleVideo) -> float:
        """Calculate video quality score"""
        score = 0.5  # Base score
        
        if '720p' in str(video.quality_levels):
            score += 0.2
        if '1080p' in str(video.quality_levels):
            score += 0.3
        if '4K' in str(video.quality_levels):
            score += 0.5
        
        return min(score, 1.0)
    
    def _calculate_content_safety_score(self, video: RumbleVideo) -> float:
        """Calculate content safety score"""
        score = 1.0
        
        if video.age_restricted:
            score -= 0.3
        if video.content_warnings:
            score -= 0.2 * len(video.content_warnings)
        
        return max(score, 0.0)
    
    # Placeholder methods for complex analysis (would need more data/API access)
    async def _parse_channel_page(self, html_content: str, channel_id: str) -> Dict:
        """Parse channel page HTML"""



        return {'channel_id': channel_id}
    
    async def _create_channel_model(self, channel_data: Dict) -> Optional[RumbleChannel]:
        """Create RumbleChannel model"""



        return None
    
    async def _parse_channel_videos_page(self, html_content: str) -> List[Dict]:
        """Parse channel videos page"""



        return []
    
    async def _parse_trending_page(self, html_content: str) -> List[Dict]:
        """Parse trending page"""



        return []
    
    async def _parse_live_streams_page(self, html_content: str) -> List[Dict]:
        """Parse live streams page"""



        return []
    
    async def _create_live_stream_model(self, stream_data: Dict) -> Optional[RumbleLiveStream]:
        """Create RumbleLiveStream model"""



        return None
    
    # Additional placeholder methods for comprehensive analysis
    def _calculate_growth_velocity(self, video: RumbleVideo) -> float:
        """Calculate growth velocity"""



        return 0.0
    
    def _estimate_revenue_potential(self, video: RumbleVideo) -> float:
        """Estimate revenue potential"""



        return 0.0
    
    def _assess_advertiser_friendliness(self, video: RumbleVideo) -> float:
        """Assess advertiser friendliness"""



        return 0.5
    
    async def _analyze_demographic_appeal(self, video: RumbleVideo) -> Dict:
        """Analyze demographic appeal"""



        return {}
    
    async def _analyze_geographic_performance(self, video: RumbleVideo) -> Dict:
        """Analyze geographic performance"""



        return {}
    
    async def _analyze_discovery_sources(self, video: RumbleVideo) -> Dict:
        """Analyze discovery sources"""



        return {}
    
    def _generate_video_optimization_recommendations(self, video: RumbleVideo) -> List[str]:
        """Generate video optimization recommendations"""
        recommendations = []
        
        if len(video.title) < 40:
            recommendations.append("Consider expanding the title for better SEO")
        
        if len(video.description) < 100:
            recommendations.append("Add more detailed description")
        
        if len(video.tags) < 5:
            recommendations.append("Add more relevant tags")
        
        return recommendations
