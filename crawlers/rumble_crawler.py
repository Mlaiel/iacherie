"""Rumble Video Crawler
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
    """
Rumble Video data model"""
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
    """
Rumble Channel data model"""
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
    """
Rumble Playlist data model"""
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
    """
Rumble Live Stream data model"""
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
        """
Calculate similarity between protected content and Rumble video"""
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
        """
Calculate viral coefficient for video"""
        if video.view_count < 1000:
            return 0.0
        
        video_age_days = (datetime.utcnow() - video.upload_date).days
        if video_age_days == 0:
            video_age_days = 1
        
        views_per_day = video.view_count / video_age_days
        engagement_score = video.like_count + video.comment_count
        
        return min(views_per_day * engagement_score / 10000, 10.0)
    
    def _categorize_duration(self, duration: int) -> str:
        """
Categorize video duration"""
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
        """
Calculate content safety score"""
        score = 1.0
        
        if video.age_restricted:
            score -= 0.3
        if video.content_warnings:
            score -= 0.2 * len(video.content_warnings)
        
        return max(score, 0.0)
    
    # Enhanced parsing methods for complex analysis
    async def _parse_channel_page(self, html_content: str, channel_id: str) -> Dict:
        """Parse channel page HTML for comprehensive channel data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            channel_data = {'channel_id': channel_id}
            
            # Extract channel name
            name_elem = soup.find(['h1', 'h2'], class_=re.compile(r'channel-name|user-name|title'))
            if name_elem:
                channel_data['name'] = name_elem.get_text(strip=True)
            
            # Extract username from URL or breadcrumbs
            username_elem = soup.find(['span', 'div'], class_=re.compile(r'username|handle'))
            if username_elem:
                channel_data['username'] = username_elem.get_text(strip=True).replace('@', '')
            else:
                channel_data['username'] = channel_id
            
            # Extract description
            desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description|about|bio'))
            if desc_elem:
                channel_data['description'] = desc_elem.get_text(strip=True)
            
            # Extract subscriber count
            subscriber_elem = soup.find(['span', 'div'], text=re.compile(r'subscriber|follower', re.I))
            if subscriber_elem:
                parent = subscriber_elem.find_parent()
                if parent:
                    sub_text = parent.get_text(strip=True)
                    channel_data['subscriber_count'] = self._parse_count(sub_text)
            
            # Extract video count
            video_count_elem = soup.find(['span', 'div'], text=re.compile(r'video|upload', re.I))
            if video_count_elem:
                parent = video_count_elem.find_parent()
                if parent:
                    video_text = parent.get_text(strip=True)
                    channel_data['video_count'] = self._parse_count(video_text)
            
            # Extract total views
            views_elem = soup.find(['span', 'div'], text=re.compile(r'total view|channel view', re.I))
            if views_elem:
                parent = views_elem.find_parent()
                if parent:
                    views_text = parent.get_text(strip=True)
                    channel_data['total_views'] = self._parse_count(views_text)
            
            # Check for verification status
            verified_elem = soup.find(['span', 'img'], class_=re.compile(r'verified|check'))
            channel_data['verified'] = verified_elem is not None
            
            # Check for partner status
            partner_elem = soup.find(['span', 'img'], class_=re.compile(r'partner|pro'))
            channel_data['partner'] = partner_elem is not None
            
            # Extract avatar URL
            avatar_elem = soup.find('img', class_=re.compile(r'avatar|profile|channel-image'))
            if avatar_elem and avatar_elem.get('src'):
                channel_data['avatar_url'] = avatar_elem['src']
            
            # Extract banner URL
            banner_elem = soup.find('img', class_=re.compile(r'banner|header|cover'))
            if banner_elem and banner_elem.get('src'):
                channel_data['banner_url'] = banner_elem['src']
            
            # Set channel URL
            channel_data['channel_url'] = f"{self.base_url}/c/{channel_id}"
            
            # Extract creation date if available
            created_elem = soup.find(['span', 'time'], class_=re.compile(r'joined|created|since'))
            if created_elem:
                date_text = created_elem.get_text(strip=True)
                channel_data['created_date'] = self._parse_date(date_text)
            else:
                channel_data['created_date'] = datetime.utcnow()
            
            # Extract social links
            social_links = {}
            social_elems = soup.find_all('a', href=True)
            for elem in social_elems:
                href = elem['href']
                if 'twitter.com' in href or 'x.com' in href:
                    social_links['twitter'] = href
                elif 'instagram.com' in href:
                    social_links['instagram'] = href
                elif 'youtube.com' in href:
                    social_links['youtube'] = href
                elif 'facebook.com' in href:
                    social_links['facebook'] = href
                elif 'tiktok.com' in href:
                    social_links['tiktok'] = href
            
            channel_data['social_links'] = social_links
            
            # Extract website if available
            website_elem = soup.find('a', href=True, text=re.compile(r'website|site|link', re.I))
            if website_elem:
                channel_data['website'] = website_elem['href']
            
            # Extract categories/tags
            category_elems = soup.find_all(['a', 'span'], class_=re.compile(r'category|tag'))
            channel_data['categories'] = [elem.get_text(strip=True) for elem in category_elems[:5]]
            
            return channel_data
            
        except Exception as e:
            logger.error(f"Error parsing channel page: {str(e)}")
            return {'channel_id': channel_id}
    
    async def _create_channel_model(self, channel_data: Dict) -> Optional[RumbleChannel]:
        """Create RumbleChannel model from parsed data"""
        try:
            # Calculate derived metrics
            upload_frequency = 0.0
            average_views = 0.0
            engagement_rate = 0.0
            growth_rate = 0.0
            
            # Calculate average views per video
            if channel_data.get('video_count', 0) > 0 and channel_data.get('total_views', 0) > 0:
                average_views = channel_data['total_views'] / channel_data['video_count']
            
            # Estimate upload frequency (videos per week) based on channel age
            if channel_data.get('created_date') and channel_data.get('video_count', 0) > 0:
                channel_age_days = (datetime.utcnow() - channel_data['created_date']).days
                if channel_age_days > 0:
                    upload_frequency = (channel_data['video_count'] * 7) / channel_age_days
            
            # Basic engagement rate estimation
            if channel_data.get('total_views', 0) > 0:
                # Rough estimate: engagement is typically 1-5% of views
                engagement_rate = min(0.03, max(0.001, 
                    channel_data.get('subscriber_count', 0) / channel_data['total_views']))
            
            # Growth rate estimation based on recent activity
            growth_rate = min(upload_frequency * 0.1, 1.0)  # Basic estimation
            
            channel = RumbleChannel(
                channel_id=channel_data.get('channel_id', ''),
                name=channel_data.get('name', ''),
                username=channel_data.get('username', ''),
                description=channel_data.get('description'),
                subscriber_count=channel_data.get('subscriber_count', 0),
                video_count=channel_data.get('video_count', 0),
                total_views=channel_data.get('total_views', 0),
                created_date=channel_data.get('created_date', datetime.utcnow()),
                verified=channel_data.get('verified', False),
                partner=channel_data.get('partner', False),
                avatar_url=channel_data.get('avatar_url'),
                banner_url=channel_data.get('banner_url'),
                channel_url=channel_data.get('channel_url', ''),
                website=channel_data.get('website'),
                categories=channel_data.get('categories', []),
                social_links=channel_data.get('social_links', {}),
                upload_frequency=upload_frequency,
                average_views=average_views,
                engagement_rate=engagement_rate,
                growth_rate=growth_rate,
                content_style=self._analyze_content_style_from_categories(
                    channel_data.get('categories', [])
                )
            )
            
            return channel
            
        except Exception as e:
            logger.error(f"Error creating channel model: {str(e)}")
            return None
    
    async def _parse_channel_videos_page(self, html_content: str) -> List[Dict]:
        """Parse channel videos page to extract video data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            videos = []
            
            # Look for video containers in channel videos page
            video_containers = soup.find_all(['div', 'article'], 
                class_=re.compile(r'video-item|media-listing|listing-video|video-card'))
            
            for container in video_containers:
                try:
                    video_data = {}
                    
                    # Extract video ID and URL
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        video_data['url'] = urljoin(self.base_url, href)
                        video_data['video_id'] = self._extract_video_id_from_url(href)
                        video_data['video_url'] = video_data['url']
                        video_data['embed_url'] = f"{self.base_url}/embed/{video_data['video_id']}"
                    
                    # Extract title
                    title_elem = container.find(['h3', 'h4', 'span', 'a'], 
                        class_=re.compile(r'title|video-title|media-heading'))
                    if title_elem:
                        video_data['title'] = title_elem.get_text(strip=True)
                    
                    # Extract thumbnail
                    img_elem = container.find('img', src=True)
                    if img_elem:
                        video_data['thumbnail_url'] = img_elem['src']
                    
                    # Extract view count
                    views_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'views|view-count'))
                    if views_elem:
                        views_text = views_elem.get_text(strip=True)
                        video_data['view_count'] = self._parse_count(views_text)
                    
                    # Extract duration
                    duration_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'duration|time|length'))
                    if duration_elem:
                        duration_text = duration_elem.get_text(strip=True)
                        video_data['duration'] = self._parse_duration(duration_text)
                    
                    # Extract upload date
                    date_elem = container.find(['span', 'time'], 
                        class_=re.compile(r'date|uploaded|ago|time'))
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        video_data['upload_date'] = self._parse_relative_date(date_text)
                    
                    # Extract like count if available
                    like_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'like|thumb-up'))
                    if like_elem:
                        like_text = like_elem.get_text(strip=True)
                        video_data['like_count'] = self._parse_count(like_text)
                    
                    # Extract description if available
                    desc_elem = container.find(['p', 'div'], 
                        class_=re.compile(r'description|summary'))
                    if desc_elem:
                        video_data['description'] = desc_elem.get_text(strip=True)
                    
                    # Only add if we have essential data
                    if video_data.get('video_id') and video_data.get('title'):
                        videos.append(video_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing channel video: {str(e)}")
                    continue
            
            return videos
            
        except Exception as e:
            logger.error(f"Error parsing channel videos page: {str(e)}")
            return []
    
    async def _parse_trending_page(self, html_content: str) -> List[Dict]:
        """Parse trending page to extract trending videos data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            videos = []
            
            # Look for trending video containers
            video_containers = soup.find_all(['div', 'article'], 
                class_=re.compile(r'trending-video|featured-video|hot-video|listing-video|video-item'))
            
            # Fallback to generic video containers if specific ones not found
            if not video_containers:
                video_containers = soup.find_all(['div'], 
                    class_=re.compile(r'video|media'))
            
            for container in video_containers:
                try:
                    video_data = {}
                    
                    # Extract video link and ID
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        video_data['url'] = urljoin(self.base_url, href)
                        video_data['video_id'] = self._extract_video_id_from_url(href)
                        video_data['video_url'] = video_data['url']
                        video_data['embed_url'] = f"{self.base_url}/embed/{video_data['video_id']}"
                    
                    # Extract title
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'span', 'a'], 
                        class_=re.compile(r'title|heading|name'))
                    if not title_elem:
                        title_elem = container.find(['a'], string=True)
                    if title_elem:
                        video_data['title'] = title_elem.get_text(strip=True)
                    
                    # Extract uploader/channel
                    uploader_elem = container.find(['span', 'a', 'div'], 
                        class_=re.compile(r'channel|uploader|author|creator'))
                    if uploader_elem:
                        video_data['uploader'] = uploader_elem.get_text(strip=True)
                        if uploader_elem.name == 'a' and uploader_elem.get('href'):
                            video_data['channel_id'] = self._extract_channel_id_from_url(uploader_elem['href'])
                    
                    # Extract view count
                    views_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'view|watch'))
                    if views_elem:
                        views_text = views_elem.get_text(strip=True)
                        video_data['view_count'] = self._parse_count(views_text)
                    
                    # Extract thumbnail
                    img_elem = container.find('img', src=True)
                    if img_elem:
                        video_data['thumbnail_url'] = img_elem['src']
                    
                    # Extract duration
                    duration_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'duration|time|length'))
                    if duration_elem:
                        duration_text = duration_elem.get_text(strip=True)
                        video_data['duration'] = self._parse_duration(duration_text)
                    
                    # Extract upload date
                    date_elem = container.find(['span', 'time'], 
                        class_=re.compile(r'date|uploaded|ago|time'))
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        video_data['upload_date'] = self._parse_relative_date(date_text)
                    else:
                        video_data['upload_date'] = datetime.utcnow()
                    
                    # Calculate trending score based on position
                    trending_score = max(1.0 - (len(videos) * 0.1), 0.1)
                    video_data['trending_score'] = trending_score
                    
                    # Extract likes if available
                    like_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'like|thumb'))
                    if like_elem:
                        like_text = like_elem.get_text(strip=True)
                        video_data['like_count'] = self._parse_count(like_text)
                    
                    # Only add if we have essential data
                    if video_data.get('video_id') and video_data.get('title'):
                        videos.append(video_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing trending video: {str(e)}")
                    continue
            
            return videos
            
        except Exception as e:
            logger.error(f"Error parsing trending page: {str(e)}")
            return []
    
    async def _parse_live_streams_page(self, html_content: str) -> List[Dict]:
        """Parse live streams page to extract active stream data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            streams = []
            
            # Look for live stream containers
            stream_containers = soup.find_all(['div', 'article'], 
                class_=re.compile(r'live-stream|stream-item|live-video|live-card'))
            
            # Fallback to containers with "live" indicators
            if not stream_containers:
                live_indicators = soup.find_all(['span', 'div'], 
                    class_=re.compile(r'live|streaming'), text=re.compile(r'LIVE|Live', re.I))
                stream_containers = [indicator.find_parent() for indicator in live_indicators if indicator.find_parent()]
            
            for container in stream_containers:
                try:
                    stream_data = {}
                    
                    # Extract stream link and ID
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        stream_data['stream_url'] = urljoin(self.base_url, href)
                        stream_data['stream_id'] = self._extract_video_id_from_url(href)
                    
                    # Extract title
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'span'], 
                        class_=re.compile(r'title|heading|name'))
                    if title_elem:
                        stream_data['title'] = title_elem.get_text(strip=True)
                    
                    # Extract streamer name
                    streamer_elem = container.find(['span', 'a', 'div'], 
                        class_=re.compile(r'channel|streamer|author|creator'))
                    if streamer_elem:
                        stream_data['streamer'] = streamer_elem.get_text(strip=True)
                        if streamer_elem.name == 'a' and streamer_elem.get('href'):
                            stream_data['streamer_id'] = self._extract_channel_id_from_url(streamer_elem['href'])
                    
                    # Extract current viewer count
                    viewers_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'viewer|watching|audience'))
                    if viewers_elem:
                        viewers_text = viewers_elem.get_text(strip=True)
                        stream_data['current_viewers'] = self._parse_count(viewers_text)
                    
                    # Extract thumbnail
                    img_elem = container.find('img', src=True)
                    if img_elem:
                        stream_data['thumbnail_url'] = img_elem['src']
                    
                    # Extract category/tags
                    category_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'category|tag|genre'))
                    if category_elem:
                        stream_data['category'] = category_elem.get_text(strip=True)
                    
                    # Check for mature content indicators
                    mature_elem = container.find(['span', 'div'], 
                        class_=re.compile(r'mature|adult|18\+'))
                    stream_data['mature_content'] = mature_elem is not None
                    
                    # Set stream status and start time
                    stream_data['stream_status'] = 'live'
                    stream_data['start_time'] = datetime.utcnow()  # Approximate
                    
                    # Extract quality options if available
                    quality_elems = container.find_all(['span'], 
                        text=re.compile(r'\d+p|HD|4K', re.I))
                    if quality_elems:
                        stream_data['quality_options'] = [elem.get_text(strip=True) for elem in quality_elems]
                    else:
                        stream_data['quality_options'] = ['720p']  # Default
                    
                    # Only add if we have essential data
                    if stream_data.get('stream_id') and stream_data.get('title'):
                        streams.append(stream_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing live stream: {str(e)}")
                    continue
            
            return streams
            
        except Exception as e:
            logger.error(f"Error parsing live streams page: {str(e)}")
            return []
    
    async def _create_live_stream_model(self, stream_data: Dict) -> Optional[RumbleLiveStream]:
        """Create RumbleLiveStream model from parsed data"""
        try:
            stream = RumbleLiveStream(
                stream_id=stream_data.get('stream_id', ''),
                title=stream_data.get('title', ''),
                description=stream_data.get('description'),
                streamer=stream_data.get('streamer', ''),
                streamer_id=stream_data.get('streamer_id'),
                start_time=stream_data.get('start_time', datetime.utcnow()),
                current_viewers=stream_data.get('current_viewers', 0),
                peak_viewers=stream_data.get('current_viewers', 0),  # Assume current is peak for now
                total_viewers=stream_data.get('current_viewers', 0),  # Estimate
                stream_url=stream_data.get('stream_url', ''),
                thumbnail_url=stream_data.get('thumbnail_url'),
                quality_options=stream_data.get('quality_options', []),
                category=stream_data.get('category'),
                mature_content=stream_data.get('mature_content', False),
                stream_status=stream_data.get('stream_status', 'live'),
                language=stream_data.get('language', 'en')  # Default to English
            )
            
            return stream
            
        except Exception as e:
            logger.error(f"Error creating live stream model: {str(e)}")
            return None
    
    # Advanced analysis methods implementation
    def _calculate_growth_velocity(self, video: RumbleVideo) -> float:
        """Calculate growth velocity based on video performance metrics"""
        try:
            if video.view_count < 100:
                return 0.0
            
            video_age_hours = (datetime.utcnow() - video.upload_date).total_seconds() / 3600
            if video_age_hours <= 0:
                video_age_hours = 1
            
            # Views per hour
            views_per_hour = video.view_count / video_age_hours
            
            # Engagement velocity (likes + comments per hour)
            engagement_per_hour = (video.like_count + video.comment_count) / video_age_hours
            
            # Combine metrics with weights
            velocity = (views_per_hour * 0.7) + (engagement_per_hour * 1000 * 0.3)
            
            # Normalize to 0-10 scale
            return min(velocity / 1000, 10.0)
            
        except Exception as e:
            logger.debug(f"Error calculating growth velocity: {str(e)}")
            return 0.0
    
    def _estimate_revenue_potential(self, video: RumbleVideo) -> float:
        """Estimate revenue potential based on video metrics"""
        try:
            base_cpm = 2.0  # Base CPM for Rumble
            
            # Factors affecting revenue
            view_factor = min(video.view_count / 1000, 1000)  # Views in thousands
            engagement_factor = (video.like_count + video.comment_count) / max(video.view_count, 1)
            quality_factor = self._calculate_quality_score(video)
            safety_factor = self._calculate_content_safety_score(video)
            
            # Duration factor (longer videos generally earn more)
            duration_factor = 1.0
            if video.duration > 600:  # 10+ minutes
                duration_factor = 1.5
            elif video.duration > 300:  # 5+ minutes
                duration_factor = 1.2
            
            # Calculate estimated revenue
            estimated_revenue = (
                view_factor * base_cpm * 
                (1 + engagement_factor) * 
                quality_factor * 
                safety_factor * 
                duration_factor
            )
            
            return round(estimated_revenue, 2)
            
        except Exception as e:
            logger.debug(f"Error estimating revenue potential: {str(e)}")
            return 0.0
    
    def _assess_advertiser_friendliness(self, video: RumbleVideo) -> float:
        """Assess how advertiser-friendly the content is"""
        try:
            score = 1.0  # Start with perfect score
            
            # Age restriction reduces advertiser friendliness
            if video.age_restricted:
                score -= 0.4
            
            # Content warnings reduce score
            warning_penalty = len(video.content_warnings) * 0.1
            score -= warning_penalty
            
            # Controversial keywords in title/description
            controversial_keywords = [
                'war', 'violence', 'death', 'kill', 'weapon', 'blood',
                'suicide', 'depression', 'drug', 'alcohol', 'gambling',
                'sex', 'porn', 'nude', 'adult', 'mature'
            ]
            
            content_text = f"{video.title} {video.description}".lower()
            for keyword in controversial_keywords:
                if keyword in content_text:
                    score -= 0.05
            
            # Very short videos are less advertiser-friendly
            if video.duration < 60:
                score -= 0.1
            
            # Quality affects advertiser appeal
            quality_bonus = (self._calculate_quality_score(video) - 0.5) * 0.2
            score += quality_bonus
            
            return max(min(score, 1.0), 0.0)
            
        except Exception as e:
            logger.debug(f"Error assessing advertiser friendliness: {str(e)}")
            return 0.5
    
    async def _analyze_demographic_appeal(self, video: RumbleVideo) -> Dict:
        """Analyze demographic appeal based on content characteristics"""
        try:
            demographics = {
                'age_groups': {},
                'interests': [],
                'geographic_appeal': {},
                'language_preference': 'en'
            }
            
            # Analyze content for age appeal
            if video.age_restricted or any(word in video.title.lower() + video.description.lower() 
                                         for word in ['mature', 'adult', '18+', 'explicit']):
                demographics['age_groups'] = {
                    '18-24': 0.3,
                    '25-34': 0.4,
                    '35-44': 0.2,
                    '45+': 0.1
                }
            elif any(word in video.title.lower() + video.description.lower() 
                    for word in ['kid', 'child', 'family', 'cartoon', 'animation']):
                demographics['age_groups'] = {
                    '13-17': 0.3,
                    '18-24': 0.2,
                    '25-34': 0.3,
                    '35-44': 0.2
                }
            else:
                # General content
                demographics['age_groups'] = {
                    '13-17': 0.1,
                    '18-24': 0.3,
                    '25-34': 0.3,
                    '35-44': 0.2,
                    '45+': 0.1
                }
            
            # Extract interests from categories and tags
            interest_mapping = {
                'gaming': ['game', 'gaming', 'esports', 'stream'],
                'politics': ['political', 'politics', 'election', 'government'],
                'news': ['news', 'breaking', 'current', 'events'],
                'entertainment': ['entertainment', 'comedy', 'funny', 'humor'],
                'education': ['educational', 'tutorial', 'how-to', 'learn'],
                'technology': ['tech', 'technology', 'gadget', 'software'],
                'lifestyle': ['lifestyle', 'vlog', 'daily', 'personal'],
                'music': ['music', 'song', 'concert', 'album'],
                'sports': ['sport', 'football', 'basketball', 'soccer']
            }
            
            content_text = f"{video.title} {video.description} {' '.join(video.categories)} {' '.join(video.tags)}".lower()
            
            for interest, keywords in interest_mapping.items():
                if any(keyword in content_text for keyword in keywords):
                    demographics['interests'].append(interest)
            
            # Geographic appeal based on language and content
            if any(word in content_text for word in ['america', 'usa', 'trump', 'biden']):
                demographics['geographic_appeal']['US'] = 0.6
                demographics['geographic_appeal']['Canada'] = 0.2
                demographics['geographic_appeal']['UK'] = 0.1
                demographics['geographic_appeal']['Other'] = 0.1
            else:
                demographics['geographic_appeal']['Global'] = 1.0
            
            return demographics
            
        except Exception as e:
            logger.debug(f"Error analyzing demographic appeal: {str(e)}")
            return {}
    
    async def _analyze_geographic_performance(self, video: RumbleVideo) -> Dict:
        """Analyze geographic performance patterns"""
        try:
            # Since we don't have access to actual geographic data, 
            # we'll make educated estimates based on content
            performance = {
                'primary_markets': [],
                'growth_regions': [],
                'performance_by_region': {}
            }
            
            content_text = f"{video.title} {video.description}".lower()
            
            # Determine primary markets based on content
            if any(word in content_text for word in ['america', 'usa', 'trump', 'biden', 'american']):
                performance['primary_markets'] = ['United States', 'Canada']
                performance['performance_by_region'] = {
                    'North America': 0.7,
                    'Europe': 0.2,
                    'Asia': 0.05,
                    'Other': 0.05
                }
            elif any(word in content_text for word in ['europe', 'eu', 'brexit', 'european']):
                performance['primary_markets'] = ['United Kingdom', 'Germany', 'France']
                performance['performance_by_region'] = {
                    'Europe': 0.6,
                    'North America': 0.3,
                    'Asia': 0.05,
                    'Other': 0.05
                }
            else:
                # Global content
                performance['primary_markets'] = ['Global']
                performance['performance_by_region'] = {
                    'North America': 0.4,
                    'Europe': 0.3,
                    'Asia': 0.2,
                    'Other': 0.1
                }
            
            # Identify growth regions based on trending topics
            if video.trending_score > 0.7:
                performance['growth_regions'] = ['Asia', 'South America']
            
            return performance
            
        except Exception as e:
            logger.debug(f"Error analyzing geographic performance: {str(e)}")
            return {}
    
    async def _analyze_discovery_sources(self, video: RumbleVideo) -> Dict:
        """Analyze how users likely discovered this video"""
        try:
            sources = {
                'search': 0.0,
                'suggested': 0.0,
                'direct': 0.0,
                'external': 0.0,
                'social_media': 0.0
            }
            
            # High view count suggests good search optimization
            if video.view_count > 10000:
                sources['search'] = 0.4
                sources['suggested'] = 0.3
            else:
                sources['search'] = 0.3
                sources['suggested'] = 0.2
            
            # High engagement suggests social sharing
            engagement_rate = (video.like_count + video.comment_count) / max(video.view_count, 1)
            if engagement_rate > 0.05:
                sources['social_media'] = 0.3
                sources['external'] = 0.2
            else:
                sources['social_media'] = 0.1
                sources['external'] = 0.1
            
            # Viral content gets more direct traffic
            if video.trending_score > 0.8:
                sources['direct'] = 0.3
            else:
                sources['direct'] = 0.1
            
            # Normalize to sum to 1.0
            total = sum(sources.values())
            if total > 0:
                sources = {k: v/total for k, v in sources.items()}
            
            return sources
            
        except Exception as e:
            logger.debug(f"Error analyzing discovery sources: {str(e)}")
            return {}
    
    def _generate_video_optimization_recommendations(self, video: RumbleVideo) -> List[str]:
        """Generate video optimization recommendations based on analysis"""
        recommendations = []
        
        try:
            # Title optimization
            if len(video.title) < 40:
                recommendations.append("Consider expanding the title to 40-60 characters for better SEO")
            elif len(video.title) > 100:
                recommendations.append("Consider shortening the title for better readability")
            
            # Description optimization
            if len(video.description) < 100:
                recommendations.append("Add more detailed description (aim for 200+ characters)")
            
            # Tags optimization
            if len(video.tags) < 5:
                recommendations.append("Add more relevant tags (aim for 5-10 tags)")
            elif len(video.tags) > 15:
                recommendations.append("Consider reducing tags to most relevant ones")
            
            # Duration optimization
            if video.duration < 60:
                recommendations.append("Consider creating longer content for better engagement")
            elif video.duration > 3600:
                recommendations.append("Consider breaking long content into series")
            
            # Engagement optimization
            engagement_rate = (video.like_count + video.comment_count) / max(video.view_count, 1)
            if engagement_rate < 0.01:
                recommendations.append("Encourage viewer interaction with calls-to-action")
            
            # Quality optimization
            quality_score = self._calculate_quality_score(video)
            if quality_score < 0.7:
                recommendations.append("Consider uploading in higher quality (1080p+)")
            
            # Content safety
            if video.age_restricted:
                recommendations.append("Review content guidelines to improve advertiser appeal")
            
            # Trending potential
            if video.trending_score < 0.3:
                recommendations.append("Focus on trending topics and keywords")
            
            # Upload timing
            video_age_days = (datetime.utcnow() - video.upload_date).days
            if video_age_days < 1 and video.view_count < 100:
                recommendations.append("Promote video on social media and other platforms")
            
            return recommendations
            
        except Exception as e:
            logger.debug(f"Error generating recommendations: {str(e)}")
            return ["Unable to generate recommendations"]
    
    def _analyze_content_style_from_categories(self, categories: List[str]) -> List[str]:
        """Analyze content style from categories"""
        styles = []
        
        category_text = ' '.join(categories).lower()
        
        if any(word in category_text for word in ['educational', 'tutorial', 'how-to']):
            styles.append('educational')
        if any(word in category_text for word in ['entertainment', 'comedy', 'funny']):
            styles.append('entertainment')
        if any(word in category_text for word in ['news', 'political', 'current']):
            styles.append('news')
        if any(word in category_text for word in ['gaming', 'game', 'esports']):
            styles.append('gaming')
        if any(word in category_text for word in ['music', 'song', 'concert']):
            styles.append('music')
        if any(word in category_text for word in ['lifestyle', 'vlog', 'personal']):
            styles.append('lifestyle')
        
        return styles if styles else ['general']
    
    # Additional advanced analysis methods for comprehensive platform insights
    def _analyze_content_consistency(self, videos: List[RumbleVideo]) -> Dict[str, Any]:
        """Analyze content consistency across videos"""
        try:
            if not videos:
                return {}
            
            # Analyze duration consistency
            durations = [v.duration for v in videos if v.duration > 0]
            avg_duration = sum(durations) / len(durations) if durations else 0
            duration_variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations) if durations else 0
            
            # Analyze upload frequency
            upload_dates = [v.upload_date for v in videos]
            upload_dates.sort()
            intervals = []
            for i in range(1, len(upload_dates)):
                interval = (upload_dates[i] - upload_dates[i-1]).days
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            
            # Analyze quality consistency
            quality_scores = [self._calculate_quality_score(v) for v in videos]
            avg_quality = sum(quality_scores) / len(quality_scores)
            
            return {
                'duration_consistency': {
                    'average_duration': avg_duration,
                    'variance': duration_variance,
                    'consistency_score': max(0, 1 - (duration_variance / max(avg_duration, 1)))
                },
                'upload_frequency': {
                    'average_days_between_uploads': avg_interval,
                    'consistency_score': max(0, 1 - (max(intervals) - min(intervals)) / 30) if intervals else 0
                },
                'quality_consistency': {
                    'average_quality': avg_quality,
                    'consistency_score': min(quality_scores) / max(quality_scores) if quality_scores else 0
                }
            }
            
        except Exception as e:
            logger.debug(f"Error analyzing content consistency: {str(e)}")
            return {}
    
    def _analyze_video_performance_distribution(self, videos: List[RumbleVideo]) -> Dict[str, Any]:
        """Analyze performance distribution across videos"""
        try:
            if not videos:
                return {}
            
            view_counts = [v.view_count for v in videos]
            engagement_rates = [(v.like_count + v.comment_count) / max(v.view_count, 1) for v in videos]
            
            # Calculate percentiles
            view_counts.sort()
            top_10_percent = view_counts[int(len(view_counts) * 0.9):]
            bottom_10_percent = view_counts[:int(len(view_counts) * 0.1)]
            
            return {
                'view_distribution': {
                    'average_views': sum(view_counts) / len(view_counts),
                    'median_views': view_counts[len(view_counts) // 2],
                    'top_10_percent_avg': sum(top_10_percent) / len(top_10_percent) if top_10_percent else 0,
                    'bottom_10_percent_avg': sum(bottom_10_percent) / len(bottom_10_percent) if bottom_10_percent else 0
                },
                'engagement_distribution': {
                    'average_engagement_rate': sum(engagement_rates) / len(engagement_rates),
                    'max_engagement_rate': max(engagement_rates),
                    'min_engagement_rate': min(engagement_rates)
                },
                'performance_insights': {
                    'hit_rate': len(top_10_percent) / len(view_counts) if view_counts else 0,
                    'consistency_score': min(view_counts) / max(view_counts) if view_counts else 0
                }
            }
            
        except Exception as e:
            logger.debug(f"Error analyzing performance distribution: {str(e)}")
            return {}
