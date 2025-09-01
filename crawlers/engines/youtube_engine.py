"""YouTube Video Content Crawling Engine

Ultra-advanced industry-grade engine for YouTube content analysis with AI-powered
video understanding, monetization analytics, and viral trend prediction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. 
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action under German and international law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum
import json
import re
from urllib.parse import urlparse, parse_qs
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from ..base import BaseCrawlerEngine
from ...core.platforms.youtube import YouTubePlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...ai.video_analyzer import VideoAnalyzer
from ...ai.trend_analyzer import TrendAnalyzer
from ...ai.monetization_analyzer import MonetizationAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector
from ...audio.transcription import AudioTranscriptionService
from ...ml.sentiment_analyzer import SentimentAnalyzer


class VideoCategory(Enum):
    """
YouTube video categories"""

    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    MUSIC = "music"
    GAMING = "gaming"
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    SPORTS = "sports"
    NEWS = "news"
    COMEDY = "comedy"
    TUTORIAL = "tutorial"


class VideoQuality(Enum):
    """Video content quality levels"""

    EXCEPTIONAL = "exceptional"
    HIGH_QUALITY = "high_quality"
    PROFESSIONAL = "professional"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    SPAM = "spam"


class MonetizationStatus(Enum):
    """Video monetization status"""

    MONETIZED = "monetized"
    DEMONETIZED = "demonetized"
    LIMITED = "limited"
    NOT_ELIGIBLE = "not_eligible"
    UNKNOWN = "unknown"


@dataclass
class YouTubeVideo:
    """YouTube video data structure"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: int
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    subscriber_count: int
    category: VideoCategory
    tags: List[str]
    thumbnail_urls: Dict[str, str]
    video_url: str
    embed_url: str
    quality_score: float
    video_quality: VideoQuality
    monetization_status: MonetizationStatus
    estimated_revenue: float
    engagement_rate: float
    viral_potential: float
    trending_score: float
    educational_value: float
    entertainment_value: float
    content_fingerprint: str
    protection_level: str
    social_impact_score: float
    watch_time_ratio: float
    audience_retention: float
    click_through_rate: float
    revenue_per_view: float
    transcript: str
    sentiment_analysis: Dict[str, float]
    keyword_analysis: Dict[str, Any]
    competitor_analysis: Dict[str, Any]
    optimization_suggestions: List[str]


@dataclass 
class YouTubeChannel:
    """
YouTube channel data structure"""
    channel_id: str
    title: str
    description: str
    published_at: datetime
    subscriber_count: int
    video_count: int
    view_count: int
    playlist_count: int
    country: str
    custom_url: str
    thumbnail_urls: Dict[str, str]
    keywords: List[str]
    branding_settings: Dict[str, Any]
    upload_frequency: float
    avg_video_duration: float
    avg_views_per_video: float
    engagement_rate: float
    growth_rate: float
    monetization_enabled: bool
    estimated_monthly_revenue: float
    top_performing_videos: List[str]
    content_categories: List[VideoCategory]
    audience_demographics: Dict[str, Any]
    content_strategy_score: float
    brand_safety_score: float
    influence_score: float
    collaboration_potential: float


class YouTubeEngine(BaseCrawlerEngine):
    """
    Professional YouTube crawling engine with advanced video analytics,
    monetization tracking, and AI-powered content optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = YouTubePlatform(config.get('youtube', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.monetization_analyzer = MonetizationAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.transcription_service = AudioTranscriptionService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # YouTube API configuration
        self.api_key = config.get('youtube_api_key', '')
        self.youtube_service = None
        if self.api_key:
            self.youtube_service = googleapiclient.discovery.build(
                'youtube', 'v3', developerKey=self.api_key
            )
            
        # Configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 300)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 15)
        self.enable_transcript_analysis = config.get('enable_transcript_analysis', True)
        self.enable_monetization_analysis = config.get('enable_monetization_analysis', True)
        self.min_quality_threshold = config.get('min_quality_threshold', 0.6)
        
    async def crawl_trending_videos(
        self,
        region_code: str = 'US',
        category_id: Optional[str] = None,
        max_results: int = 50
    ) -> AsyncGenerator[YouTubeVideo, None]:
        """
        Crawl trending YouTube videos with comprehensive analysis
        
        Args:
            region_code: Country code for trending videos
            category_id: Video category ID filter
            max_results: Maximum number of videos to crawl
            
        Yields:
            YouTubeVideo: Processed YouTube video objects
        """
        self.logger.info(f"Crawling trending videos for region: {region_code}")
        
        try:
            if not self.youtube_service:
                raise Exception("YouTube API service not configured")
                
            # Get trending videos
            request = self.youtube_service.videos().list(
                part='snippet,statistics,contentDetails,status',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=min(max_results, 50)
            )
            
            if category_id:
                request = request.execute(videoCategoryId=category_id)
            else:
                request = request.execute()
                
            # Process each video
            for video_item in request.get('items', []):
                video = await self._process_youtube_video(video_item)
                if video and self._meets_quality_threshold(video):
                    yield video
                    
        except Exception as e:
            self.logger.error(f"Error crawling trending videos: {str(e)}")
            await self.metrics_collector.record_error('youtube_trending_error', str(e))
            raise
            
    async def crawl_channel_videos(
        self,
        channel_id: str,
        max_results: int = 100,
        order: str = 'date'
    ) -> AsyncGenerator[YouTubeVideo, None]:
        """
        Crawl videos from a specific YouTube channel
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to crawl
            order: Sort order (date, relevance, viewCount, rating)
            
        Yields:
            YouTubeVideo: Processed YouTube video objects
        """
        self.logger.info(f"Crawling videos from channel: {channel_id}")
        
        try:
            if not self.youtube_service:
                raise Exception("YouTube API service not configured")
                
            # Get channel's upload playlist
            channel_request = self.youtube_service.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            if not channel_response.get('items'):
                return
                
            uploads_playlist_id = (
                channel_response['items'][0]
                ['contentDetails']['relatedPlaylists']['uploads']
            )
            
            # Get videos from uploads playlist
            next_page_token = None
            video_count = 0
            
            while video_count < max_results:
                playlist_request = self.youtube_service.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - video_count),
                    pageToken=next_page_token
                )
                playlist_response = playlist_request.execute()
                
                # Get video details
                video_ids = [
                    item['snippet']['resourceId']['videoId']
                    for item in playlist_response.get('items', [])
                ]
                
                if not video_ids:
                    break
                    
                videos_request = self.youtube_service.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()
                
                # Process videos
                for video_item in videos_response.get('items', []):
                    video = await self._process_youtube_video(video_item)
                    if video and self._meets_quality_threshold(video):
                        yield video
                        video_count += 1
                        
                # Check for next page
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except Exception as e:
            self.logger.error(f"Error crawling channel videos: {str(e)}")
            await self.metrics_collector.record_error('youtube_channel_error', str(e))
            raise
            
    async def _process_youtube_video(self, video_item: Dict[str, Any]) -> Optional[YouTubeVideo]:
        """Process and analyze YouTube video with comprehensive metrics"""
        
        try:
            # Extract basic video information
            video_id = video_item['id']
            snippet = video_item['snippet']
            statistics = video_item.get('statistics', {})
            content_details = video_item.get('contentDetails', {})
            status = video_item.get('status', {})
            
            # Basic information
            title = snippet.get('title', '')
            description = snippet.get('description', '')
            channel_id = snippet.get('channelId', '')
            channel_title = snippet.get('channelTitle', '')
            published_at = datetime.fromisoformat(
                snippet.get('publishedAt', '').replace('Z', '+00:00')
            )
            
            # Parse duration
            duration_str = content_details.get('duration', 'PT0S')
            duration = self._parse_duration(duration_str)
            
            # Statistics
            view_count = int(statistics.get('viewCount', 0))
            like_count = int(statistics.get('likeCount', 0))
            dislike_count = int(statistics.get('dislikeCount', 0))
            comment_count = int(statistics.get('commentCount', 0))
            
            # Get channel subscriber count
            subscriber_count = await self._get_channel_subscriber_count(channel_id)
            
            # Extract metadata
            tags = snippet.get('tags', [])
            category_id = snippet.get('categoryId', '1')
            category = self._map_category_id_to_enum(category_id)
            
            # URLs
            thumbnail_urls = snippet.get('thumbnails', {})
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
            # Generate content fingerprint
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                f"{video_id}{title}{description}"
            )
            
            # Analyze video quality
            quality_score = await self._analyze_video_quality(video_item)
            video_quality = self._determine_video_quality(quality_score)
            
            # Analyze monetization
            monetization_data = await self._analyze_monetization(video_item)
            monetization_status = monetization_data['status']
            estimated_revenue = monetization_data['estimated_revenue']
            revenue_per_view = monetization_data['revenue_per_view']
            
            # Calculate engagement metrics
            engagement_rate = self._calculate_engagement_rate(statistics, subscriber_count)
            
            # Analyze viral potential
            viral_potential = await self._calculate_viral_potential(video_item, statistics)
            
            # Analyze trending score
            trending_score = await self._calculate_trending_score(video_item, statistics)
            
            # Analyze content value
            educational_value = await self._analyze_educational_value(video_item)
            entertainment_value = await self._analyze_entertainment_value(video_item)
            
            # Analyze social impact
            social_impact_score = await self._analyze_social_impact(video_item, statistics)
            
            # Calculate performance metrics
            watch_time_ratio = await self._estimate_watch_time_ratio(video_item)
            audience_retention = await self._estimate_audience_retention(video_item)
            click_through_rate = await self._estimate_click_through_rate(video_item)
            
            # Generate transcript and analyze
            transcript = ""
            if self.enable_transcript_analysis:
                transcript = await self._get_video_transcript(video_id)
                
            # Perform sentiment analysis
            sentiment_analysis = await self._analyze_video_sentiment(video_item, transcript)
            
            # Keyword analysis
            keyword_analysis = await self._analyze_keywords(video_item, transcript)
            
            # Competitor analysis
            competitor_analysis = await self._analyze_competitors(video_item)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(video_item)
            
            # Determine protection level
            protection_level = "premium" if video_quality in [VideoQuality.EXCEPTIONAL, VideoQuality.HIGH_QUALITY] else "standard"
            
            # Create YouTube video object
            youtube_video = YouTubeVideo(
                video_id=video_id,
                title=title,
                description=description,
                channel_id=channel_id,
                channel_title=channel_title,
                published_at=published_at,
                duration=duration,
                view_count=view_count,
                like_count=like_count,
                dislike_count=dislike_count,
                comment_count=comment_count,
                subscriber_count=subscriber_count,
                category=category,
                tags=tags,
                thumbnail_urls=thumbnail_urls,
                video_url=video_url,
                embed_url=embed_url,
                quality_score=quality_score,
                video_quality=video_quality,
                monetization_status=monetization_status,
                estimated_revenue=estimated_revenue,
                engagement_rate=engagement_rate,
                viral_potential=viral_potential,
                trending_score=trending_score,
                educational_value=educational_value,
                entertainment_value=entertainment_value,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                social_impact_score=social_impact_score,
                watch_time_ratio=watch_time_ratio,
                audience_retention=audience_retention,
                click_through_rate=click_through_rate,
                revenue_per_view=revenue_per_view,
                transcript=transcript,
                sentiment_analysis=sentiment_analysis,
                keyword_analysis=keyword_analysis,
                competitor_analysis=competitor_analysis,
                optimization_suggestions=optimization_suggestions
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='youtube',
                content_type='video',
                quality_score=quality_score
            )
            
            return youtube_video
            
        except Exception as e:
            self.logger.error(f"Error processing YouTube video: {str(e)}")
            return None


@dataclass
class YouTubeVideoData:
    """YouTube video data structure"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    tags: List[str]
    category_id: str
    language: str
    thumbnails: Dict[str, Any]
    statistics: Dict[str, Any]
    content_details: Dict[str, Any]
    snippet: Dict[str, Any]
    monetization_status: Optional[Dict[str, Any]] = None
    copyright_claims: Optional[List[Dict]] = None


@dataclass
class YouTubeChannelData:
    """
YouTube channel data structure"""
    channel_id: str
    title: str
    description: str
    custom_url: str
    published_at: datetime
    country: str
    view_count: int
    subscriber_count: int
    video_count: int
    thumbnails: Dict[str, Any]
    branding_settings: Dict[str, Any]
    statistics: Dict[str, Any]
    content_details: Dict[str, Any]
    monetization_enabled: bool = False
    partnership_status: Optional[str] = None


class YouTubeCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced YouTube crawler engine with comprehensive API integration.
    
    Features:
    - YouTube Data API v3 integration
    - Video and channel analytics extraction
    - Monetization data collection
    - Content protection monitoring
    - Rate limiting and caching
    - Selenium-based scraping for restricted data
    """
    
    def __init__(self, api_key: str, config: Optional[Dict] = None):
        """
Initialize YouTube crawler engine"""
        super().__init__(config)
        self.api_key = api_key
        self.youtube_service = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=100,  # YouTube API quota
            requests_per_day=10000
        )
        self.cache_manager = CacheManager(
            cache_duration=timedelta(hours=1),
            max_cache_size=1000
        )
        self._setup_youtube_service()
        self._setup_selenium_driver()
    
    def _setup_youtube_service(self) -> None:
        """
Setup YouTube Data API service"""
        try:
            self.youtube_service = googleapiclient.discovery.build(
                'youtube', 'v3', 
                developerKey=self.api_key,
                cache_discovery=False
            )
            logger.info("YouTube API service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API service: {e}")
            raise AuthenticationError(f"YouTube API initialization failed: {e}")
    
    def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver for advanced scraping"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
    
    async def search_videos(
        self, 
        query: str, 
        max_results: int = 50,
        filters: Optional[Dict] = None
    ) -> List[YouTubeVideoData]:
        """
        Search for videos using YouTube Data API
        
        Args:
            query: Search query
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of video data
        """
        await self.rate_limiter.wait()
        
        cache_key = hashlib.md5(f"{query}_{max_results}_{filters}".encode()).hexdigest()
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': 'relevance'
            }
            
            if filters:
                if 'published_after' in filters:
                    search_params['publishedAfter'] = filters['published_after'].isoformat() + 'Z'
                if 'duration' in filters:
                    search_params['videoDuration'] = filters['duration']
                if 'category' in filters:
                    search_params['videoCategoryId'] = filters['category']
            
            search_response = self.youtube_service.search().list(**search_params).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            videos_data = await self.get_videos_details(video_ids)
            
            await self.cache_manager.set(cache_key, videos_data)
            return videos_data
            
        except HttpError as e:
            logger.error(f"YouTube API error during video search: {e}")
            if e.resp.status == 403:
                raise RateLimitError("YouTube API quota exceeded")
            raise CrawlerError(f"YouTube search failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during video search: {e}")
            raise CrawlerError(f"Video search failed: {e}")
    
    async def get_videos_details(self, video_ids: List[str]) -> List[YouTubeVideoData]:
        """
        Get detailed information for multiple videos
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of detailed video data
        """
        videos_data = []
        
        # Process videos in batches of 50 (API limit)
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            await self.rate_limiter.wait()
            
            try:
                videos_response = self.youtube_service.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(batch_ids)
                ).execute()
                
                for item in videos_response['items']:
                    video_data = await self._parse_video_item(item)
                    if video_data:
                        videos_data.append(video_data)
                        
            except HttpError as e:
                logger.error(f"YouTube API error getting video details: {e}")
                continue
                
        return videos_data
    
    async def get_channel_details(self, channel_id: str) -> Optional[YouTubeChannelData]:
        """
        Get detailed channel information
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel data or None if not found
        """
        await self.rate_limiter.wait()
        
        cache_key = f"channel_{channel_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            channel_response = self.youtube_service.channels().list(
                part='snippet,statistics,contentDetails,brandingSettings,status',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return None
                
            item = channel_response['items'][0]
            channel_data = await self._parse_channel_item(item)
            
            await self.cache_manager.set(cache_key, channel_data)
            return channel_data
            
        except HttpError as e:
            logger.error(f"YouTube API error getting channel details: {e}")
            raise CrawlerError(f"Channel details retrieval failed: {e}")
    
    async def get_channel_videos(
        self, 
        channel_id: str, 
        max_results: int = 50
    ) -> List[YouTubeVideoData]:
        """
        Get videos from a specific channel
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of video data from the channel
        """
        videos_data = []
        next_page_token = None
        
        while len(videos_data) < max_results:
            await self.rate_limiter.wait()
            
            try:
                search_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': min(50, max_results - len(videos_data))
                }
                
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                search_response = self.youtube_service.search().list(**search_params).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                batch_videos = await self.get_videos_details(video_ids)
                videos_data.extend(batch_videos)
                
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except HttpError as e:
                logger.error(f"YouTube API error getting channel videos: {e}")
                break
                
        return videos_data[:max_results]
    
    async def monitor_content_theft(
        self, 
        original_content: Dict, 
        search_terms: List[str]
    ) -> List[Dict]:
        """
        Monitor for potential content theft using fingerprinting
        
        Args:
            original_content: Original content metadata
            search_terms: Terms to search for potential theft
            
        Returns:
            List of potentially stolen content matches
        """
        theft_candidates = []
        
        for search_term in search_terms:
            try:
                videos = await self.search_videos(
                    query=search_term,
                    max_results=20,
                    filters={'published_after': datetime.now() - timedelta(days=30)}
                )
                
                for video in videos:
                    similarity_score = await self._calculate_content_similarity(
                        original_content, 
                        asdict(video)
                    )
                    
                    if similarity_score > 0.7:  # 70% similarity threshold
                        theft_candidates.append({
                            'video_data': video,
                            'similarity_score': similarity_score,
                            'detected_at': datetime.now(),
                            'search_term': search_term
                        })
                        
            except Exception as e:
                logger.error(f"Error monitoring content theft for term '{search_term}': {e}")
                continue
                
        return theft_candidates
    
    async def extract_monetization_data(self, video_id: str) -> Optional[Dict]:
        """
        Extract monetization data using Selenium scraping
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Monetization data or None if unavailable
        """
        if not self.driver:
            logger.warning("Selenium driver not available for monetization data extraction")
            return None
            
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "watch7-content"))
            )
            
            monetization_data = {}
            
            # Check for ads
            try:
                ad_elements = self.driver.find_elements(By.CLASS_NAME, "video-ads")
                monetization_data['has_ads'] = len(ad_elements) > 0
            except NoSuchElementError:
                monetization_data['has_ads'] = False
            
            # Check for membership/channel perks
            try:
                membership_elements = self.driver.find_elements(
                    By.XPATH, 
                    "//button[contains(text(), 'Join') or contains(text(), 'Member')]"
                )
                monetization_data['has_membership'] = len(membership_elements) > 0
            except NoSuchElementError:
                monetization_data['has_membership'] = False
            
            # Check for Super Chat/Super Thanks
            try:
                super_chat_elements = self.driver.find_elements(
                    By.XPATH,
                    "//button[contains(text(), 'Super Chat') or contains(text(), 'Thanks')]"
                )
                monetization_data['has_super_features'] = len(super_chat_elements) > 0
            except NoSuchElementError:
                monetization_data['has_super_features'] = False
            
            return monetization_data
            
        except TimeoutException:
            logger.error(f"Timeout while extracting monetization data for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error extracting monetization data: {e}")
            return None
    
    async def _parse_video_item(self, item: Dict) -> Optional[YouTubeVideoData]:
        """Parse YouTube API video item into structured data"""
        try:
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # Extract video duration
            duration = content_details.get('duration', 'PT0S')
            
            # Parse tags
            tags = snippet.get('tags', [])
            
            # Convert statistics to integers with defaults
            view_count = int(statistics.get('viewCount', 0))
            like_count = int(statistics.get('likeCount', 0))
            comment_count = int(statistics.get('commentCount', 0))
            
            return YouTubeVideoData(
                video_id=item['id'],
                title=snippet['title'],
                description=snippet.get('description', ''),
                channel_id=snippet['channelId'],
                channel_title=snippet['channelTitle'],
                published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                duration=duration,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                tags=tags,
                category_id=snippet.get('categoryId', ''),
                language=snippet.get('defaultLanguage', snippet.get('defaultAudioLanguage', 'unknown')),
                thumbnails=snippet.get('thumbnails', {}),
                statistics=statistics,
                content_details=content_details,
                snippet=snippet
            )
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing video item: {e}")
            return None
    
    async def _parse_channel_item(self, item: Dict) -> YouTubeChannelData:
        """Parse YouTube API channel item into structured data"""
        snippet = item['snippet']
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        branding_settings = item.get('brandingSettings', {})
        
        return YouTubeChannelData(
            channel_id=item['id'],
            title=snippet['title'],
            description=snippet.get('description', ''),
            custom_url=snippet.get('customUrl', ''),
            published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
            country=snippet.get('country', 'unknown'),
            view_count=int(statistics.get('viewCount', 0)),
            subscriber_count=int(statistics.get('subscriberCount', 0)),
            video_count=int(statistics.get('videoCount', 0)),
            thumbnails=snippet.get('thumbnails', {}),
            branding_settings=branding_settings,
            statistics=statistics,
            content_details=content_details,
            monetization_enabled=content_details.get('relatedPlaylists', {}).get('uploads') is not None
        )
    
    async def _calculate_content_similarity(
        self, 
        original: Dict, 
        candidate: Dict
    ) -> float:
        """
        Calculate similarity score between original and candidate content
        
        Args:
            original: Original content metadata
            candidate: Candidate content to compare
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Title similarity (using simple word overlap)
            original_title_words = set(original.get('title', '').lower().split())
            candidate_title_words = set(candidate.get('title', '').lower().split())
            
            if not original_title_words or not candidate_title_words:
                title_similarity = 0.0
            else:
                common_words = original_title_words.intersection(candidate_title_words)
                title_similarity = len(common_words) / len(original_title_words.union(candidate_title_words))
            
            # Description similarity (basic)
            original_desc = original.get('description', '').lower()
            candidate_desc = candidate.get('description', '').lower()
            
            if not original_desc or not candidate_desc:
                desc_similarity = 0.0
            else:
                # Simple character overlap
                common_chars = sum(1 for a, b in zip(original_desc, candidate_desc) if a == b)
                desc_similarity = common_chars / max(len(original_desc), len(candidate_desc))
            
            # Tags similarity
            original_tags = set(tag.lower() for tag in original.get('tags', []))
            candidate_tags = set(tag.lower() for tag in candidate.get('tags', []))
            
            if not original_tags or not candidate_tags:
                tags_similarity = 0.0
            else:
                common_tags = original_tags.intersection(candidate_tags)
                tags_similarity = len(common_tags) / len(original_tags.union(candidate_tags))
            
            # Weighted average
            overall_similarity = (
                title_similarity * 0.5 +
                desc_similarity * 0.3 +
                tags_similarity * 0.2
            )
            
            return overall_similarity
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            await self.cache_manager.cleanup()
            logger.info("YouTube crawler engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except:
            pass


# Export main class
__all__ = ['YouTubeCrawlerEngine', 'YouTubeVideoData', 'YouTubeChannelData']
