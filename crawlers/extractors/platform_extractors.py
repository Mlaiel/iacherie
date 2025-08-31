"""Platform Extractors - Industrial IA Platform Content Processing System
=====================================================================

Ultra-advanced professional platform-specific extractors for major social media and content platforms.
Implements enterprise-grade content extraction, API integration, and data normalization capabilities with AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""import asyncio
import logging
import re
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, quote_plus
from abc import ABC, abstractmethod
import aiohttp
import base64
import hashlib
from pathlib import Path

# Import core extraction components
from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

# Import third-party libraries conditionally
try:
    import yt_dlp
    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

logger = logging.getLogger(__name__)


@dataclass
class PlatformMetadata:
    """Advanced platform-specific metadata container"""    
    # Basic platform information
    platform_id: Optional[str] = None
    platform_name: Optional[str] = None
    platform_url: Optional[str] = None
    api_version: Optional[str] = None
    
    # Creator/Channel information
    creator_id: Optional[str] = None
    creator_username: Optional[str] = None
    creator_display_name: Optional[str] = None
    creator_bio: Optional[str] = None
    creator_avatar_url: Optional[str] = None
    creator_verified: bool = False
    creator_type: Optional[str] = None  # individual, business, organization
    creator_category: Optional[str] = None
    
    # Content information
    post_id: Optional[str] = None
    post_type: Optional[str] = None  # video, image, text, audio, story
    post_title: Optional[str] = None
    post_description: Optional[str] = None
    post_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    content_urls: List[str] = field(default_factory=list)
    
    # Temporal information
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    crawled_at: datetime = field(default_factory=datetime.now)
    
    # Engagement metrics
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    dislike_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    save_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    reach: Optional[int] = None
    impressions: Optional[int] = None
    
    # Content metadata
    duration: Optional[float] = None
    language: Optional[str] = None
    location: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    # Audience data
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    total_posts: Optional[int] = None
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    
    # Revenue and monetization
    monetization_enabled: bool = False
    estimated_revenue: Optional[float] = None
    ad_revenue: Optional[float] = None
    sponsorship_indicators: List[str] = field(default_factory=list)
    brand_mentions: List[str] = field(default_factory=list)
    
    # AI analysis results
    content_sentiment: Optional[Dict[str, float]] = None
    content_topics: List[str] = field(default_factory=list)
    content_classification: Optional[Dict[str, float]] = None
    virality_score: Optional[float] = None
    trending_potential: Optional[float] = None
    
    # Protection and compliance
    copyright_claims: List[Dict] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    age_restriction: Optional[str] = None
    privacy_level: Optional[str] = None
    
    # Technical metadata
    extraction_method: Optional[str] = None
    api_rate_limit: Optional[Dict] = None
    quality_score: float = 0.0
    data_completeness: float = 0.0


@dataclass
class PlatformEngagement:
    """Advanced engagement metrics container"""    
    # Real-time metrics
    current_views: int = 0
    current_likes: int = 0
    current_comments: int = 0
    current_shares: int = 0
    
    # Historical trends
    view_velocity: Optional[float] = None  # views per hour
    engagement_velocity: Optional[float] = None
    peak_engagement_time: Optional[datetime] = None
    engagement_growth_rate: Optional[float] = None
    
    # Audience insights
    audience_retention: List[float] = field(default_factory=list)
    drop_off_points: List[float] = field(default_factory=list)
    replay_rate: Optional[float] = None
    completion_rate: Optional[float] = None
    
    # Demographic breakdown
    age_demographics: Dict[str, float] = field(default_factory=dict)
    gender_demographics: Dict[str, float] = field(default_factory=dict)
    geographic_demographics: Dict[str, float] = field(default_factory=dict)
    device_demographics: Dict[str, float] = field(default_factory=dict)
    
    # Interaction quality
    comment_sentiment: Optional[Dict[str, float]] = None
    top_comments: List[Dict] = field(default_factory=list)
    interaction_depth: Optional[float] = None
    community_engagement: Optional[float] = None


@dataclass
class RevenueMetrics:
    """Revenue and monetization metrics"""    
    # Direct revenue
    ad_revenue: Optional[float] = None
    sponsorship_revenue: Optional[float] = None
    merchandise_revenue: Optional[float] = None
    subscription_revenue: Optional[float] = None
    tip_revenue: Optional[float] = None
    
    # Estimated revenue
    estimated_total_revenue: Optional[float] = None
    revenue_per_view: Optional[float] = None
    revenue_per_engagement: Optional[float] = None
    
    # Monetization indicators
    brand_partnerships: List[str] = field(default_factory=list)
    affiliate_links: List[str] = field(default_factory=list)
    sponsored_content_indicators: List[str] = field(default_factory=list)
    merchandise_links: List[str] = field(default_factory=list)
    
    # Performance metrics
    monetization_efficiency: Optional[float] = None
    revenue_growth_rate: Optional[float] = None
    audience_value: Optional[float] = None


class BasePlatformExtractor(BaseExtractor):
    """Advanced base class for platform-specific extractors"""    
    def __init__(self, name: str, platform: str):
        super().__init__(name)
        self.platform = platform
        self.api_keys = {}
        self.rate_limits = {}
        self.session_headers = {}
        self.extraction_cache = {}
        self.last_request_time = {}
        
        # Initialize platform-specific configurations
        self._initialize_platform_config()
    
    def _initialize_platform_config(self):
        """Initialize platform-specific configuration"""        self.config = {
            'rate_limit': 100,  # requests per hour
            'retry_attempts': 3,
            'timeout': 30,
            'cache_duration': 3600,  # 1 hour
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ]
        }
    
    async def respect_rate_limit(self, endpoint: str = "default"):
        """Implement rate limiting for API calls"""        current_time = time.time()
        last_time = self.last_request_time.get(endpoint, 0)
        
        rate_limit = self.config.get('rate_limit', 100)
        min_interval = 3600 / rate_limit  # seconds between requests
        
        time_since_last = current_time - last_time
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time[endpoint] = time.time()
    
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[Dict]:
        """Make HTTP request with retry logic and error handling"""        await self.respect_rate_limit()
        
        for attempt in range(self.config.get('retry_attempts', 3)):
            try:
                headers = kwargs.pop('headers', {})
                headers.update(self.session_headers)
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(
                    total=self.config.get('timeout', 30)
                )) as session:
                    
                    async with session.request(method, url, headers=headers, **kwargs) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Rate limited
                            wait_time = 2 ** attempt * 60  # Exponential backoff
                            self.logger.warning(f"Rate limited, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            self.logger.error(f"HTTP {response.status}: {await response.text()}")
                            
            except Exception as e:
                self.logger.error(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.config.get('retry_attempts', 3) - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def extract_engagement_metrics(self, platform_data: Dict) -> PlatformEngagement:
        """Extract engagement metrics from platform data"""        engagement = PlatformEngagement()
        
        try:
            # Extract basic metrics
            engagement.current_views = platform_data.get('view_count', 0)
            engagement.current_likes = platform_data.get('like_count', 0)
            engagement.current_comments = platform_data.get('comment_count', 0)
            engagement.current_shares = platform_data.get('share_count', 0)
            
            # Calculate engagement rate
            total_engagement = (engagement.current_likes + 
                              engagement.current_comments + 
                              engagement.current_shares)
            
            if engagement.current_views > 0:
                engagement_rate = total_engagement / engagement.current_views
                platform_data['engagement_rate'] = engagement_rate
            
            # Extract demographic data if available
            if 'demographics' in platform_data:
                demo_data = platform_data['demographics']
                engagement.age_demographics = demo_data.get('age', {})
                engagement.gender_demographics = demo_data.get('gender', {})
                engagement.geographic_demographics = demo_data.get('geography', {})
            
        except Exception as e:
            self.logger.error(f"Engagement metrics extraction failed: {e}")
        
        return engagement
    
    async def extract_revenue_indicators(self, platform_data: Dict, content: str = "") -> RevenueMetrics:
        """Extract revenue and monetization indicators"""        revenue = RevenueMetrics()
        
        try:
            # Direct revenue data (if available from platform APIs)
            if 'revenue' in platform_data:
                revenue_data = platform_data['revenue']
                revenue.ad_revenue = revenue_data.get('ad_revenue')
                revenue.sponsorship_revenue = revenue_data.get('sponsorship_revenue')
                revenue.subscription_revenue = revenue_data.get('subscription_revenue')
            
            # Detect sponsorship indicators in content
            sponsorship_keywords = [
                'sponsored', 'ad', 'partnership', 'collaboration',
                'affiliate', 'promo code', 'discount code', '#ad',
                '#sponsored', '#partnership', 'brand ambassador'
            ]
            
            content_lower = content.lower()
            detected_indicators = [kw for kw in sponsorship_keywords if kw in content_lower]
            revenue.sponsored_content_indicators = detected_indicators
            
            # Extract affiliate links
            affiliate_patterns = [
                r'amzn\.to/\w+',  # Amazon
                r'bit\.ly/\w+',   # Bitly
                r'tinyurl\.com/\w+',  # TinyURL
                r'geni\.us/\w+',  # Genius Links
            ]
            
            for pattern in affiliate_patterns:
                matches = re.findall(pattern, content)
                revenue.affiliate_links.extend(matches)
            
            # Brand mention detection
            brand_patterns = [
                r'@\w+',  # Brand mentions
                r'#brand\w+',  # Brand hashtags
            ]
            
            for pattern in brand_patterns:
                matches = re.findall(pattern, content)
                revenue.brand_partnerships.extend(matches)
            
        except Exception as e:
            self.logger.error(f"Revenue indicators extraction failed: {e}")
        
        return revenue
    
    async def analyze_content_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze content sentiment using basic text analysis"""        try:
            # Simple sentiment analysis based on keywords
            positive_words = [
                'amazing', 'awesome', 'great', 'love', 'fantastic', 'wonderful',
                'excellent', 'perfect', 'beautiful', 'incredible', 'outstanding'
            ]
            
            negative_words = [
                'terrible', 'awful', 'hate', 'horrible', 'disgusting', 'worst',
                'disappointing', 'frustrating', 'annoying', 'pathetic', 'useless'
            ]
            
            words = content.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            total_words = len(words)
            
            if total_words > 0:
                positive_score = positive_count / total_words
                negative_score = negative_count / total_words
                neutral_score = 1.0 - positive_score - negative_score
                
                return {
                    'positive': positive_score,
                    'negative': negative_score,
                    'neutral': neutral_score
                }
            
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    async def calculate_virality_score(self, engagement: PlatformEngagement, 
                                     metadata: PlatformMetadata) -> float:
        """Calculate virality score based on engagement metrics"""        try:
            score = 0.0
            
            # Views factor (30% weight)
            if metadata.view_count and metadata.view_count > 0:
                view_score = min(100, np.log10(metadata.view_count) * 10)
                score += view_score * 0.3
            
            # Engagement rate factor (40% weight)
            if metadata.engagement_rate:
                engagement_score = min(100, metadata.engagement_rate * 1000)
                score += engagement_score * 0.4
            
            # Share factor (20% weight)
            if metadata.share_count and metadata.view_count:
                share_rate = metadata.share_count / metadata.view_count
                share_score = min(100, share_rate * 1000)
                score += share_score * 0.2
            
            # Growth velocity factor (10% weight)
            if engagement.view_velocity:
                velocity_score = min(100, engagement.view_velocity / 100)
                score += velocity_score * 0.1
            
            return min(100, max(0, score))
            
        except Exception as e:
            self.logger.error(f"Virality score calculation failed: {e}")
            return 0.0
    
    async def estimate_monetization_potential(self, metadata: PlatformMetadata, 
                                            revenue: RevenueMetrics) -> float:
        """Estimate monetization potential based on content characteristics"""        try:
            score = 0.0
            
            # Follower count factor (25% weight)
            if metadata.follower_count:
                follower_score = min(100, np.log10(metadata.follower_count + 1) * 15)
                score += follower_score * 0.25
            
            # Engagement rate factor (25% weight)
            if metadata.engagement_rate:
                engagement_score = min(100, metadata.engagement_rate * 2000)
                score += engagement_score * 0.25
            
            # Content category factor (20% weight)
            high_value_categories = [
                'technology', 'finance', 'business', 'education', 
                'lifestyle', 'beauty', 'fitness', 'gaming'
            ]
            
            if metadata.category and metadata.category.lower() in high_value_categories:
                score += 20
            
            # Existing monetization factor (15% weight)
            if revenue.sponsored_content_indicators or revenue.affiliate_links:
                score += 15
            
            # Audience demographics factor (15% weight)
            # Higher value for adult audiences in affluent regions
            if metadata.audience_demographics:
                demo_score = self._calculate_demographic_value(metadata.audience_demographics)
                score += demo_score * 0.15
            
            return min(100, max(0, score))
            
        except Exception as e:
            self.logger.error(f"Monetization potential estimation failed: {e}")
            return 0.0
    
    def _calculate_demographic_value(self, demographics: Dict[str, Any]) -> float:
        """Calculate demographic value for monetization"""        try:
            score = 50  # Base score
            
            # Age factor
            age_data = demographics.get('age', {})
            if '25-34' in age_data or '35-44' in age_data:
                score += 20  # Prime spending age groups
            
            # Geographic factor
            geo_data = demographics.get('geography', {})
            high_value_regions = ['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'JP']
            
            for region in high_value_regions:
                if region in geo_data:
                    score += geo_data[region] * 0.3  # Weight by percentage
            
            return min(100, score)
            
        except Exception as e:
            self.logger.error(f"Demographic value calculation failed: {e}")
            return 50
        self.platform = platform
        self.rate_limit_delay = 1.0  # Base delay between requests
        self.max_retries = 3
        
    async def extract_platform_metadata(self, content: str, url: str) -> PlatformMetadata:
        """Extract platform-specific metadata"""        return PlatformMetadata()
    
    async def normalize_url(self, url: str) -> str:
        """Normalize platform URL to canonical form"""        return url
    
    async def detect_content_type(self, url: str, content: str) -> ContentType:
        """Detect content type from URL and content"""        if any(keyword in url.lower() for keyword in ['music', 'audio', 'track']):
            return ContentType.AUDIO
        elif any(keyword in url.lower() for keyword in ['video', 'watch', 'reel']):
            return ContentType.VIDEO
        elif any(keyword in url.lower() for keyword in ['photo', 'image', 'pic']):
            return ContentType.IMAGE
        return ContentType.TEXT


class YouTubeExtractor(BasePlatformExtractor):
    """Industrial-grade YouTube content extractor with AI analysis and monetization tracking"""    
    def __init__(self):
        super().__init__("YouTubeExtractor", "youtube")
        self.api_key = None  # Set from config or environment
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        
        # URL patterns for different YouTube content types
        self.video_pattern = re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})')
        self.channel_pattern = re.compile(r'youtube\.com/(?:channel/|c/|user/)([a-zA-Z0-9_-]+)')
        self.playlist_pattern = re.compile(r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)')
        self.shorts_pattern = re.compile(r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})')
        
        # Revenue estimation models
        self.cpm_estimates = {
            'tier1': 2.5,   # US, UK, CA, AU
            'tier2': 1.5,   # EU, JP, KR
            'tier3': 0.8,   # Other developed
            'tier4': 0.3    # Developing countries
        }
        
        self._initialize_youtube_config()
    
    def _initialize_youtube_config(self):
        """Initialize YouTube-specific configuration"""        self.config.update({
            'rate_limit': 10000,  # YouTube API quota per day
            'timeout': 45,
            'extract_comments': True,
            'extract_captions': True,
            'extract_chapters': True,
            'max_comment_pages': 5,
            'revenue_estimation': True
        })
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for YouTube content"""        if not request.url:
            return False
        
        url = request.url.lower()
        return any([
            'youtube.com' in url,
            'youtu.be' in url,
            'youtube-nocookie.com' in url
        ])
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract comprehensive YouTube content and metadata"""        start_time = datetime.now()
        
        try:
            # Normalize and validate URL
            url = await self._normalize_youtube_url(request.url)
            content_id, content_type = await self._identify_content_type(url)
            
            if not content_id:
                return ExtractionResult(
                    extractor_name=self.name,
                    status=ExtractionStatus.FAILED,
                    error="Unable to extract content ID from YouTube URL"
                )
            
            # Extract content based on type
            if content_type == 'video':
                extracted_data = await self._extract_video_content(content_id, url)
            elif content_type == 'channel':
                extracted_data = await self._extract_channel_content(content_id, url)
            elif content_type == 'playlist':
                extracted_data = await self._extract_playlist_content(content_id, url)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # AI-powered content analysis
            ai_analysis = await self._ai_content_analysis(extracted_data)
            
            # Revenue and monetization analysis
            revenue_analysis = await self._analyze_monetization(extracted_data)
            
            # Audience and engagement insights
            engagement_analysis = await self._analyze_engagement(extracted_data)
            
            # Trending and virality analysis
            trending_analysis = await self._analyze_trending_potential(extracted_data)
            
            # Content protection analysis
            protection_analysis = await self._analyze_content_protection(extracted_data)
            
            # Combine all analyses
            extracted_data.update({
                'ai_analysis': ai_analysis,
                'revenue_analysis': revenue_analysis,
                'engagement_analysis': engagement_analysis,
                'trending_analysis': trending_analysis,
                'protection_analysis': protection_analysis
            })
            
            # Create comprehensive metadata
            metadata = await self._create_comprehensive_metadata(extracted_data, url, content_type)
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                extractor_name=self.name,
                status=ExtractionStatus.SUCCESS,
                content_type=ContentType.VIDEO if content_type == 'video' else ContentType.MIXED,
                metadata=metadata,
                data=extracted_data,
                processing_time=extraction_time
            )
            
        except Exception as e:
            self.logger.error(f"YouTube extraction failed: {e}")
            return ExtractionResult(
                extractor_name=self.name,
                status=ExtractionStatus.FAILED,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _normalize_youtube_url(self, url: str) -> str:
        """Normalize YouTube URL to standard format"""        try:
            # Handle youtu.be short URLs
            if 'youtu.be' in url:
                video_id = url.split('/')[-1].split('?')[0]
                return f"https://www.youtube.com/watch?v={video_id}"
            
            # Handle youtube-nocookie.com
            if 'youtube-nocookie.com' in url:
                url = url.replace('youtube-nocookie.com', 'youtube.com')
            
            # Ensure HTTPS
            if url.startswith('http://'):
                url = url.replace('http://', 'https://')
            
            return url
            
        except Exception as e:
            self.logger.error(f"URL normalization failed: {e}")
            return url
    
    async def _identify_content_type(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Identify YouTube content type and extract ID"""        try:
            # Video content
            video_match = self.video_pattern.search(url)
            if video_match:
                return video_match.group(1), 'video'
            
            # Shorts content (treated as video)
            shorts_match = self.shorts_pattern.search(url)
            if shorts_match:
                return shorts_match.group(1), 'video'
            
            # Channel content
            channel_match = self.channel_pattern.search(url)
            if channel_match:
                return channel_match.group(1), 'channel'
            
            # Playlist content
            playlist_match = self.playlist_pattern.search(url)
            if playlist_match:
                return playlist_match.group(1), 'playlist'
            
            return None, None
            
        except Exception as e:
            self.logger.error(f"Content type identification failed: {e}")
            return None, None
    
    async def _extract_video_content(self, video_id: str, url: str) -> Dict[str, Any]:
        """Extract comprehensive video content and metadata"""        video_data = {}
        
        try:
            # Extract using yt-dlp if available (most reliable)
            if HAS_YTDLP:
                ytdlp_data = await self._extract_with_ytdlp(url)
                video_data.update(ytdlp_data)
            
            # Extract using YouTube Data API if available (official, rate-limited)
            if self.api_key:
                api_data = await self._extract_with_youtube_api(video_id)
                video_data.update(api_data)
            
            # Extract using web scraping as fallback
            if not video_data:
                scraping_data = await self._extract_with_web_scraping(url)
                video_data.update(scraping_data)
            
            # Extract comments if enabled
            if self.config.get('extract_comments', True):
                comments_data = await self._extract_comments(video_id)
                video_data['comments'] = comments_data
            
            # Extract captions/transcripts if available
            if self.config.get('extract_captions', True):
                captions_data = await self._extract_captions(video_id)
                video_data['captions'] = captions_data
            
            # Extract video chapters if available
            if self.config.get('extract_chapters', True):
                chapters_data = await self._extract_chapters(video_data)
                video_data['chapters'] = chapters_data
            
            return video_data
            
        except Exception as e:
            self.logger.error(f"Video content extraction failed: {e}")
            return video_data
    
    async def _extract_with_ytdlp(self, url: str) -> Dict[str, Any]:
        """Extract content using yt-dlp library"""        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'fr', 'de', 'es'],
                'ignoreerrors': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract relevant data
                extracted_data = {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader'),
                    'uploader_id': info.get('uploader_id'),
                    'upload_date': info.get('upload_date'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'dislike_count': info.get('dislike_count'),
                    'comment_count': info.get('comment_count'),
                    'subscriber_count': info.get('subscriber_count'),
                    'categories': info.get('categories', []),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail'),
                    'thumbnails': info.get('thumbnails', []),
                    'formats': info.get('formats', []),
                    'subtitles': info.get('subtitles', {}),
                    'automatic_captions': info.get('automatic_captions', {}),
                    'webpage_url': info.get('webpage_url'),
                    'channel_id': info.get('channel_id'),
                    'channel_url': info.get('channel_url'),
                    'age_limit': info.get('age_limit'),
                    'availability': info.get('availability')
                }
                
                return extracted_data
                
        except Exception as e:
            self.logger.error(f"yt-dlp extraction failed: {e}")
            return {}
    
    async def _extract_with_youtube_api(self, video_id: str) -> Dict[str, Any]:
        """Extract content using YouTube Data API v3"""        try:
            if not self.api_key:
                return {}
            
            # Video details
            video_url = f"{self.api_base_url}/videos"
            video_params = {
                'key': self.api_key,
                'id': video_id,
                'part': 'snippet,statistics,contentDetails,status,localizations,recordingDetails,topicDetails'
            }
            
            video_response = await self.make_request(video_url, params=video_params)
            
            if not video_response or 'items' not in video_response or not video_response['items']:
                return {}
            
            video_item = video_response['items'][0]
            snippet = video_item.get('snippet', {})
            statistics = video_item.get('statistics', {})
            content_details = video_item.get('contentDetails', {})
            
            # Channel details
            channel_id = snippet.get('channelId')
            channel_data = {}
            
            if channel_id:
                channel_url = f"{self.api_base_url}/channels"
                channel_params = {
                    'key': self.api_key,
                    'id': channel_id,
                    'part': 'snippet,statistics,brandingSettings,status'
                }
                
                channel_response = await self.make_request(channel_url, params=channel_params)
                
                if channel_response and 'items' in channel_response and channel_response['items']:
                    channel_item = channel_response['items'][0]
                    channel_data = {
                        'channel_title': channel_item.get('snippet', {}).get('title'),
                        'channel_description': channel_item.get('snippet', {}).get('description'),
                        'channel_subscriber_count': int(channel_item.get('statistics', {}).get('subscriberCount', 0)),
                        'channel_video_count': int(channel_item.get('statistics', {}).get('videoCount', 0)),
                        'channel_view_count': int(channel_item.get('statistics', {}).get('viewCount', 0)),
                        'channel_created_at': channel_item.get('snippet', {}).get('publishedAt'),
                        'channel_country': channel_item.get('snippet', {}).get('country'),
                        'channel_custom_url': channel_item.get('snippet', {}).get('customUrl')
                    }
            
            # Parse duration
            duration_str = content_details.get('duration', 'PT0S')
            duration_seconds = self._parse_duration(duration_str)
            
            api_data = {
                'video_id': video_id,
                'title': snippet.get('title'),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt'),
                'channel_id': channel_id,
                'channel_title': snippet.get('channelTitle'),
                'category_id': snippet.get('categoryId'),
                'default_language': snippet.get('defaultLanguage'),
                'tags': snippet.get('tags', []),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'dislike_count': int(statistics.get('dislikeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'favorite_count': int(statistics.get('favoriteCount', 0)),
                'duration': duration_seconds,
                'dimension': content_details.get('dimension'),
                'definition': content_details.get('definition'),
                'caption': content_details.get('caption'),
                'licensed_content': content_details.get('licensedContent'),
                'privacy_status': video_item.get('status', {}).get('privacyStatus'),
                'upload_status': video_item.get('status', {}).get('uploadStatus'),
                'monetization_details': video_item.get('monetizationDetails', {}),
                **channel_data
            }
            
            return api_data
            
        except Exception as e:
            self.logger.error(f"YouTube API extraction failed: {e}")
            return {}
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube duration format (PT#M#S) to seconds"""        try:
            import re
            pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
            match = pattern.match(duration_str)
            
            if not match:
                return 0
            
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            seconds = int(match.group(3)) if match.group(3) else 0
            
            return hours * 3600 + minutes * 60 + seconds
            
        except Exception:
            return 0
    
    async def _extract_with_web_scraping(self, url: str) -> Dict[str, Any]:
        """Extract content using web scraping as fallback"""        try:
            if not HAS_BS4:
                return {}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return {}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract basic metadata from page
                    scraped_data = {}
                    
                    # Title
                    title_tag = soup.find('meta', property='og:title')
                    if title_tag:
                        scraped_data['title'] = title_tag.get('content')
                    
                    # Description
                    desc_tag = soup.find('meta', property='og:description')
                    if desc_tag:
                        scraped_data['description'] = desc_tag.get('content')
                    
                    # Thumbnail
                    thumb_tag = soup.find('meta', property='og:image')
                    if thumb_tag:
                        scraped_data['thumbnail'] = thumb_tag.get('content')
                    
                    # Video ID
                    video_id_match = self.video_pattern.search(url)
                    if video_id_match:
                        scraped_data['video_id'] = video_id_match.group(1)
                    
                    # Try to extract view count from scripts
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and 'viewCount' in script.string:
                            # This is a simplified extraction - YouTube's actual data structure is complex
                            view_match = re.search(r'"viewCount":"(\d+)"', script.string)
                            if view_match:
                                scraped_data['view_count'] = int(view_match.group(1))
                            break
                    
                    return scraped_data
                    
        except Exception as e:
            self.logger.error(f"Web scraping extraction failed: {e}")
            return {}
    
    async def _extract_comments(self, video_id: str) -> List[Dict[str, Any]]:
        """Extract video comments using YouTube API"""        comments = []
        
        try:
            if not self.api_key:
                return comments
            
            comments_url = f"{self.api_base_url}/commentThreads"
            next_page_token = None
            pages_extracted = 0
            max_pages = self.config.get('max_comment_pages', 5)
            
            while pages_extracted < max_pages:
                params = {
                    'key': self.api_key,
                    'videoId': video_id,
                    'part': 'snippet,replies',
                    'order': 'relevance',
                    'maxResults': 100
                }
                
                if next_page_token:
                    params['pageToken'] = next_page_token
                
                response = await self.make_request(comments_url, params=params)
                
                if not response or 'items' not in response:
                    break
                
                for item in response['items']:
                    comment_snippet = item['snippet']['topLevelComment']['snippet']
                    
                    comment_data = {
                        'comment_id': item['id'],
                        'author': comment_snippet.get('authorDisplayName'),
                        'author_channel_id': comment_snippet.get('authorChannelId', {}).get('value'),
                        'text': comment_snippet.get('textDisplay'),
                        'like_count': comment_snippet.get('likeCount', 0),
                        'published_at': comment_snippet.get('publishedAt'),
                        'updated_at': comment_snippet.get('updatedAt'),
                        'reply_count': item['snippet'].get('totalReplyCount', 0)
                    }
                    
                    # Extract replies if available
                    if 'replies' in item:
                        replies = []
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            replies.append({
                                'reply_id': reply['id'],
                                'author': reply_snippet.get('authorDisplayName'),
                                'text': reply_snippet.get('textDisplay'),
                                'like_count': reply_snippet.get('likeCount', 0),
                                'published_at': reply_snippet.get('publishedAt')
                            })
                        comment_data['replies'] = replies
                    
                    comments.append(comment_data)
                
                # Check for next page
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                pages_extracted += 1
            
        except Exception as e:
            self.logger.error(f"Comments extraction failed: {e}")
        
        return comments
    
    async def _extract_captions(self, video_id: str) -> Dict[str, Any]:
        """Extract video captions/transcripts"""        captions_data = {}
        
        try:
            if not self.api_key:
                return captions_data
            
            # Get captions list
            captions_url = f"{self.api_base_url}/captions"
            params = {
                'key': self.api_key,
                'videoId': video_id,
                'part': 'snippet'
            }
            
            response = await self.make_request(captions_url, params=params)
            
            if response and 'items' in response:
                captions_data['available_languages'] = []
                
                for item in response['items']:
                    snippet = item['snippet']
                    captions_data['available_languages'].append({
                        'language': snippet.get('language'),
                        'name': snippet.get('name'),
                        'track_kind': snippet.get('trackKind'),
                        'is_auto_synced': snippet.get('isAutoSynced', False),
                        'is_large': snippet.get('isLarge', False),
                        'is_easy_reader': snippet.get('isEasyReader', False),
                        'is_draft': snippet.get('isDraft', False),
                        'is_cc': snippet.get('isCC', False)
                    })
            
        except Exception as e:
            self.logger.error(f"Captions extraction failed: {e}")
        
        return captions_data
    
    async def _extract_chapters(self, video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract video chapters from description"""        chapters = []
        
        try:
            description = video_data.get('description', '')
            
            # Look for timestamp patterns in description
            timestamp_pattern = re.compile(r'(?:^|\n)(\d{1,2}:?\d{2}:\d{2}|\d{1,2}:\d{2})\s*[-–—]?\s*(.+?)(?=\n|$)', re.MULTILINE)
            
            matches = timestamp_pattern.findall(description)
            
            for timestamp, title in matches:
                # Convert timestamp to seconds
                time_parts = timestamp.split(':')
                if len(time_parts) == 2:  # MM:SS
                    seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                elif len(time_parts) == 3:  # HH:MM:SS
                    seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                else:
                    continue
                
                chapters.append({
                    'timestamp': timestamp,
                    'start_time': seconds,
                    'title': title.strip(),
                    'description': ''
                })
            
            # Sort chapters by start time
            chapters.sort(key=lambda x: x['start_time'])
            
        except Exception as e:
            self.logger.error(f"Chapters extraction failed: {e}")
        
        return chapters
    
    async def _ai_content_analysis(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered content analysis"""        analysis = {
            'content_classification': {},
            'topic_extraction': [],
            'sentiment_analysis': {},
            'engagement_prediction': 0.0,
            'content_quality_score': 0.0,
            'audience_match_score': 0.0
        }
        
        try:
            # Analyze title and description
            title = video_data.get('title', '')
            description = video_data.get('description', '')
            tags = video_data.get('tags', [])
            
            # Content sentiment analysis
            content_text = f"{title} {description}"
            analysis['sentiment_analysis'] = await self.analyze_content_sentiment(content_text)
            
            # Topic extraction from tags and description
            all_text = f"{title} {description} {' '.join(tags)}"
            analysis['topic_extraction'] = await self._extract_topics(all_text)
            
            # Content classification
            analysis['content_classification'] = await self._classify_content(video_data)
            
            # Engagement prediction based on features
            analysis['engagement_prediction'] = await self._predict_engagement(video_data)
            
            # Content quality assessment
            analysis['content_quality_score'] = await self._assess_content_quality(video_data)
            
            # Comments sentiment analysis
            if 'comments' in video_data:
                comments_sentiment = await self._analyze_comments_sentiment(video_data['comments'])
                analysis['comments_sentiment'] = comments_sentiment
            
        except Exception as e:
            self.logger.error(f"AI content analysis failed: {e}")
        
        return analysis
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text content"""        try:
            # Simple keyword-based topic extraction
            tech_keywords = ['AI', 'technology', 'programming', 'software', 'coding', 'tech']
            lifestyle_keywords = ['lifestyle', 'fashion', 'beauty', 'travel', 'food', 'fitness']
            education_keywords = ['education', 'tutorial', 'learning', 'course', 'lesson', 'teach']
            entertainment_keywords = ['music', 'gaming', 'comedy', 'entertainment', 'fun', 'movie']
            business_keywords = ['business', 'marketing', 'entrepreneur', 'finance', 'money', 'startup']
            
            topics = []
            text_lower = text.lower()
            
            if any(keyword in text_lower for keyword in tech_keywords):
                topics.append('technology')
            if any(keyword in text_lower for keyword in lifestyle_keywords):
                topics.append('lifestyle')
            if any(keyword in text_lower for keyword in education_keywords):
                topics.append('education')
            if any(keyword in text_lower for keyword in entertainment_keywords):
                topics.append('entertainment')
            if any(keyword in text_lower for keyword in business_keywords):
                topics.append('business')
            
            return topics or ['general']
            
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            return ['general']
    
    async def _classify_content(self, video_data: Dict[str, Any]) -> Dict[str, float]:
        """Classify content into categories"""        try:
            # Simple classification based on available data
            duration = video_data.get('duration', 0)
            tags = video_data.get('tags', [])
            title = video_data.get('title', '').lower()
            description = video_data.get('description', '').lower()
            
            classification = {
                'educational': 0.0,
                'entertainment': 0.0,
                'music': 0.0,
                'gaming': 0.0,
                'vlog': 0.0,
                'review': 0.0,
                'tutorial': 0.0,
                'news': 0.0
            }
            
            # Duration-based hints
            if duration > 1800:  # >30 minutes
                classification['educational'] += 0.3
            elif duration < 180:  # <3 minutes
                classification['entertainment'] += 0.3
            
            # Keyword-based classification
            for tag in tags:
                tag_lower = tag.lower()
                if any(word in tag_lower for word in ['tutorial', 'how to', 'guide']):
                    classification['tutorial'] += 0.2
                elif any(word in tag_lower for word in ['music', 'song', 'audio']):
                    classification['music'] += 0.2
                elif any(word in tag_lower for word in ['game', 'gaming', 'play']):
                    classification['gaming'] += 0.2
                elif any(word in tag_lower for word in ['vlog', 'daily', 'life']):
                    classification['vlog'] += 0.2
                elif any(word in tag_lower for word in ['review', 'unbox', 'test']):
                    classification['review'] += 0.2
                elif any(word in tag_lower for word in ['news', 'update', 'breaking']):
                    classification['news'] += 0.2
            
            # Title and description analysis
            content_text = f"{title} {description}"
            if any(word in content_text for word in ['tutorial', 'how to', 'learn', 'guide']):
                classification['tutorial'] += 0.3
            if any(word in content_text for word in ['review', 'unboxing', 'test', 'opinion']):
                classification['review'] += 0.3
            
            # Normalize scores
            total_score = sum(classification.values())
            if total_score > 0:
                classification = {k: v / total_score for k, v in classification.items()}
            else:
                classification['entertainment'] = 1.0
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            return {'entertainment': 1.0}
    
    async def _predict_engagement(self, video_data: Dict[str, Any]) -> float:
        """Predict engagement potential based on video features"""        try:
            score = 50.0  # Base score
            
            # Title analysis
            title = video_data.get('title', '')
            if len(title) > 10 and len(title) < 70:  # Optimal title length
                score += 10
            
            # Description analysis
            description = video_data.get('description', '')
            if len(description) > 100:  # Good description length
                score += 10
            
            # Tags analysis
            tags = video_data.get('tags', [])
            if 5 <= len(tags) <= 15:  # Optimal tag count
                score += 10
            
            # Duration analysis
            duration = video_data.get('duration', 0)
            if 180 <= duration <= 900:  # 3-15 minutes (optimal for engagement)
                score += 15
            elif 900 < duration <= 1800:  # 15-30 minutes
                score += 10
            
            # Channel metrics (if available)
            subscriber_count = video_data.get('channel_subscriber_count', 0)
            if subscriber_count > 0:
                # Boost for established channels
                score += min(20, np.log10(subscriber_count + 1) * 2)
            
            # Historical performance (if available)
            view_count = video_data.get('view_count', 0)
            like_count = video_data.get('like_count', 0)
            
            if view_count > 0:
                engagement_rate = like_count / view_count if view_count > 0 else 0
                score += min(20, engagement_rate * 1000)
            
            return min(100, max(0, score))
            
        except Exception as e:
            self.logger.error(f"Engagement prediction failed: {e}")
            return 50.0
    
    async def _assess_content_quality(self, video_data: Dict[str, Any]) -> float:
        """Assess overall content quality"""        try:
            score = 0.0
            
            # Technical quality indicators
            definition = video_data.get('definition', '')
            if definition == 'hd':
                score += 20
            
            # Content completeness
            if video_data.get('title'):
                score += 10
            if video_data.get('description') and len(video_data['description']) > 50:
                score += 15
            if video_data.get('tags') and len(video_data['tags']) > 3:
                score += 10
            if video_data.get('thumbnail'):
                score += 10
            
            # Captions availability
            if video_data.get('captions') and video_data['captions'].get('available_languages'):
                score += 15
            
            # Chapters availability
            if video_data.get('chapters') and len(video_data['chapters']) > 1:
                score += 10
            
            # Duration appropriateness
            duration = video_data.get('duration', 0)
            if duration >= 60:  # At least 1 minute
                score += 10
            
            return min(100, score)
            
        except Exception as e:
            self.logger.error(f"Content quality assessment failed: {e}")
            return 0.0
    
    async def _analyze_comments_sentiment(self, comments: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment of video comments"""        try:
            if not comments:
                return {'overall_sentiment': 'neutral', 'positive_ratio': 0.5}
            
            positive_count = 0
            negative_count = 0
            
            for comment in comments[:100]:  # Analyze top 100 comments
                text = comment.get('text', '')
                sentiment = await self.analyze_content_sentiment(text)
                
                if sentiment['positive'] > sentiment['negative']:
                    positive_count += 1
                elif sentiment['negative'] > sentiment['positive']:
                    negative_count += 1
            
            total_analyzed = positive_count + negative_count
            
            if total_analyzed > 0:
                positive_ratio = positive_count / total_analyzed
                
                if positive_ratio > 0.6:
                    overall_sentiment = 'positive'
                elif positive_ratio < 0.4:
                    overall_sentiment = 'negative'
                else:
                    overall_sentiment = 'neutral'
                
                return {
                    'overall_sentiment': overall_sentiment,
                    'positive_ratio': positive_ratio,
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'total_analyzed': total_analyzed
                }
            
            return {'overall_sentiment': 'neutral', 'positive_ratio': 0.5}
            
        except Exception as e:
            self.logger.error(f"Comments sentiment analysis failed: {e}")
            return {'overall_sentiment': 'neutral', 'positive_ratio': 0.5}
    
    async def _analyze_monetization(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze monetization potential and revenue indicators"""        monetization_analysis = {
            'estimated_revenue': 0.0,
            'revenue_per_thousand_views': 0.0,
            'monetization_indicators': [],
            'sponsorship_detection': {},
            'revenue_optimization_suggestions': []
        }
        
        try:
            view_count = video_data.get('view_count', 0)
            duration = video_data.get('duration', 0)
            channel_subscriber_count = video_data.get('channel_subscriber_count', 0)
            
            # Estimate ad revenue
            if view_count > 0 and duration > 30:  # Eligible for ads
                # Estimate CPM based on content category and audience
                estimated_cpm = await self._estimate_cpm(video_data)
                
                # Calculate estimated revenue (assuming 60% watch time and 70% monetizable views)
                monetizable_views = view_count * 0.7
                estimated_revenue = (monetizable_views / 1000) * estimated_cpm * 0.55  # YouTube takes 45%
                
                monetization_analysis['estimated_revenue'] = round(estimated_revenue, 2)
                monetization_analysis['revenue_per_thousand_views'] = round(estimated_cpm * 0.55, 2)
            
            # Detect sponsorship indicators
            title = video_data.get('title', '')
            description = video_data.get('description', '')
            
            sponsorship_keywords = [
                'sponsored', 'paid promotion', 'partnership', 'collaboration',
                'affiliate', 'promo code', 'discount', '#ad', '#sponsored'
            ]
            
            detected_sponsorships = []
            content_text = f"{title} {description}".lower()
            
            for keyword in sponsorship_keywords:
                if keyword in content_text:
                    detected_sponsorships.append(keyword)
            
            monetization_analysis['sponsorship_detection'] = {
                'has_sponsorship_indicators': len(detected_sponsorships) > 0,
                'detected_keywords': detected_sponsorships,
                'sponsorship_probability': min(1.0, len(detected_sponsorships) * 0.3)
            }
            
            # Monetization optimization suggestions
            suggestions = []
            
            if duration < 600:  # Less than 10 minutes
                suggestions.append("Consider creating longer content (10+ minutes) for mid-roll ad placement")
            
            if not video_data.get('tags') or len(video_data['tags']) < 5:
                suggestions.append("Add more relevant tags to improve discoverability and ad targeting")
            
            if channel_subscriber_count < 1000:
                suggestions.append("Focus on growing subscriber base to 1000+ for YouTube Partner Program eligibility")
            
            if not description or len(description) < 100:
                suggestions.append("Write detailed descriptions with keywords for better ad targeting")
            
            monetization_analysis['revenue_optimization_suggestions'] = suggestions
            
        except Exception as e:
            self.logger.error(f"Monetization analysis failed: {e}")
        
        return monetization_analysis
    
    async def _estimate_cpm(self, video_data: Dict[str, Any]) -> float:
        """Estimate CPM (Cost Per Mille) for the video"""        try:
            base_cpm = 2.0  # Base CPM for general content
            
            # Adjust based on content category
            category_multipliers = {
                'education': 1.5,
                'technology': 1.4,
                'business': 1.3,
                'finance': 1.6,
                'review': 1.2,
                'tutorial': 1.3,
                'gaming': 0.8,
                'entertainment': 0.9,
                'music': 0.7
            }
            
            # Get content classification
            content_class = video_data.get('ai_analysis', {}).get('content_classification', {})
            if content_class:
                max_category = max(content_class.items(), key=lambda x: x[1])
                category_multiplier = category_multipliers.get(max_category[0], 1.0)
                base_cpm *= category_multiplier
            
            # Adjust based on channel size
            subscriber_count = video_data.get('channel_subscriber_count', 0)
            if subscriber_count > 1000000:  # 1M+ subscribers
                base_cpm *= 1.3
            elif subscriber_count > 100000:  # 100K+ subscribers
                base_cpm *= 1.2
            elif subscriber_count > 10000:  # 10K+ subscribers
                base_cpm *= 1.1
            
            # Adjust based on video performance
            view_count = video_data.get('view_count', 0)
            like_count = video_data.get('like_count', 0)
            
            if view_count > 0:
                engagement_rate = like_count / view_count
                if engagement_rate > 0.05:  # High engagement
                    base_cpm *= 1.2
                elif engagement_rate > 0.02:  # Good engagement
                    base_cpm *= 1.1
            
            return round(base_cpm, 2)
            
        except Exception as e:
            self.logger.error(f"CPM estimation failed: {e}")
            return 2.0
    
    async def _analyze_engagement(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze engagement metrics and patterns"""        engagement_analysis = {
            'engagement_rate': 0.0,
            'engagement_quality': 'low',
            'audience_retention_estimate': 0.0,
            'viral_potential': 0.0,
            'community_engagement': 0.0
        }
        
        try:
            view_count = video_data.get('view_count', 0)
            like_count = video_data.get('like_count', 0)
            dislike_count = video_data.get('dislike_count', 0)
            comment_count = video_data.get('comment_count', 0)
            
            if view_count > 0:
                # Calculate engagement rate
                total_engagement = like_count + dislike_count + comment_count
                engagement_rate = total_engagement / view_count
                engagement_analysis['engagement_rate'] = round(engagement_rate, 4)
                
                # Classify engagement quality
                if engagement_rate > 0.05:
                    engagement_analysis['engagement_quality'] = 'excellent'
                elif engagement_rate > 0.03:
                    engagement_analysis['engagement_quality'] = 'good'
                elif engagement_rate > 0.01:
                    engagement_analysis['engagement_quality'] = 'average'
                else:
                    engagement_analysis['engagement_quality'] = 'low'
                
                # Estimate audience retention based on like/dislike ratio
                if like_count + dislike_count > 0:
                    like_ratio = like_count / (like_count + dislike_count)
                    engagement_analysis['audience_retention_estimate'] = round(like_ratio, 3)
                
                # Calculate viral potential
                viral_score = 0.0
                
                # View velocity (if we had timestamp data)
                if view_count > 10000:
                    viral_score += 20
                
                # Engagement velocity
                if engagement_rate > 0.03:
                    viral_score += 30
                
                # Share potential (estimated from comment patterns)
                if comment_count > view_count * 0.01:  # High comment rate
                    viral_score += 25
                
                # Like ratio
                if like_count > dislike_count * 10:  # Very positive reception
                    viral_score += 25
                
                engagement_analysis['viral_potential'] = min(100, viral_score)
            
            # Community engagement analysis
            if 'comments' in video_data:
                comments = video_data['comments']
                community_score = 0.0
                
                # Comments diversity (different authors)
                unique_authors = len(set(comment.get('author', '') for comment in comments))
                if unique_authors > len(comments) * 0.7:  # Good diversity
                    community_score += 30
                
                # Reply engagement
                total_replies = sum(len(comment.get('replies', [])) for comment in comments)
                if total_replies > len(comments) * 0.1:  # Good reply rate
                    community_score += 30
                
                # Creator engagement (if creator responds to comments)
                creator_name = video_data.get('uploader', video_data.get('channel_title', ''))
                creator_responses = sum(1 for comment in comments 
                                     if comment.get('author', '').lower() == creator_name.lower())
                if creator_responses > 0:
                    community_score += 40
                
                engagement_analysis['community_engagement'] = min(100, community_score)
            
        except Exception as e:
            self.logger.error(f"Engagement analysis failed: {e}")
        
        return engagement_analysis
    
    async def _analyze_trending_potential(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trending and virality potential"""        trending_analysis = {
            'trending_score': 0.0,
            'trend_indicators': [],
            'optimal_posting_suggestions': [],
            'audience_growth_potential': 0.0
        }
        
        try:
            # Analyze title for trending keywords
            title = video_data.get('title', '').lower()
            trending_keywords = [
                'viral', 'trending', 'breaking', 'new', 'latest', 'exclusive',
                'revealed', 'exposed', 'shocking', 'amazing', 'incredible',
                'first time', 'world record', 'never seen'
            ]
            
            found_keywords = [kw for kw in trending_keywords if kw in title]
            trending_analysis['trend_indicators'] = found_keywords
            
            # Calculate trending score
            score = 0.0
            
            # Title optimization
            if len(found_keywords) > 0:
                score += 15
            
            # Content freshness
            published_at = video_data.get('published_at')
            if published_at:
                # Recent content has higher trending potential
                from datetime import datetime, timezone
                if isinstance(published_at, str):
                    try:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        hours_since_publish = (datetime.now(timezone.utc) - pub_date).total_seconds() / 3600
                        
                        if hours_since_publish < 24:
                            score += 20
                        elif hours_since_publish < 72:
                            score += 15
                        elif hours_since_publish < 168:  # 1 week
                            score += 10
                    except:
                        pass
            
            # Engagement velocity
            view_count = video_data.get('view_count', 0)
            if view_count > 1000:
                score += min(25, np.log10(view_count) * 5)
            
            # Content category factor
            content_class = video_data.get('ai_analysis', {}).get('content_classification', {})
            trending_categories = ['entertainment', 'news', 'music', 'gaming']
            
            for category in trending_categories:
                if category in content_class and content_class[category] > 0.3:
                    score += 10
                    break
            
            # Social signals
            engagement_rate = video_data.get('engagement_analysis', {}).get('engagement_rate', 0)
            if engagement_rate > 0.02:
                score += 15
            
            trending_analysis['trending_score'] = min(100, score)
            
            # Optimization suggestions
            suggestions = []
            
            if len(found_keywords) == 0:
                suggestions.append("Add trending keywords to title for better discoverability")
            
            if not video_data.get('tags') or len(video_data['tags']) < 5:
                suggestions.append("Use more relevant hashtags and tags")
            
            if video_data.get('duration', 0) > 900:  # >15 minutes
                suggestions.append("Consider shorter content for better trending potential")
            
            trending_analysis['optimal_posting_suggestions'] = suggestions
            
        except Exception as e:
            self.logger.error(f"Trending analysis failed: {e}")
        
        return trending_analysis
    
    async def _analyze_content_protection(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content protection and copyright aspects"""        protection_analysis = {
            'copyright_risk': 'low',
            'protection_recommendations': [],
            'fair_use_indicators': [],
            'monetization_impact': 'none'
        }
        
        try:
            # Analyze for potential copyright issues
            title = video_data.get('title', '').lower()
            description = video_data.get('description', '').lower()
            
            # Check for music/cover indicators
            music_keywords = ['cover', 'remix', 'music', 'song', 'audio', 'soundtrack', 'ost']
            music_indicators = [kw for kw in music_keywords if kw in f"{title} {description}"]
            
            if music_indicators:
                protection_analysis['copyright_risk'] = 'medium'
                protection_analysis['protection_recommendations'].append(
                    "Consider using royalty-free music or obtaining proper licenses"
                )
            
            # Check for brand/trademark mentions
            brand_keywords = ['disney', 'marvel', 'nintendo', 'apple', 'google', 'microsoft']
            brand_mentions = [brand for brand in brand_keywords if brand in f"{title} {description}"]
            
            if brand_mentions:
                protection_analysis['copyright_risk'] = 'medium'
                protection_analysis['protection_recommendations'].append(
                    f"Be cautious with {', '.join(brand_mentions)} content - ensure fair use compliance"
                )
            
            # Check for fair use indicators
            fair_use_keywords = ['review', 'commentary', 'criticism', 'parody', 'education', 'tutorial']
            fair_use_found = [kw for kw in fair_use_keywords if kw in f"{title} {description}"]
            
            protection_analysis['fair_use_indicators'] = fair_use_found
            
            if fair_use_found:
                protection_analysis['copyright_risk'] = 'low'
                protection_analysis['protection_recommendations'].append(
                    "Fair use indicators detected - ensure substantial commentary/criticism"
                )
            
            # Check if content is monetized
            monetization_enabled = video_data.get('monetization_details', {}).get('access', {}).get('allowed', False)
            
            if monetization_enabled and protection_analysis['copyright_risk'] == 'medium':
                protection_analysis['monetization_impact'] = 'medium'
                protection_analysis['protection_recommendations'].append(
                    "Consider Content ID implications for monetization"
                )
            
        except Exception as e:
            self.logger.error(f"Content protection analysis failed: {e}")
        
        return protection_analysis
    
    async def _create_comprehensive_metadata(self, video_data: Dict[str, Any], url: str, content_type: str) -> PlatformMetadata:
        """Create comprehensive platform metadata"""        
        # Extract engagement metrics
        engagement = await self.extract_engagement_metrics(video_data)
        
        # Extract revenue indicators
        content_text = f"{video_data.get('title', '')} {video_data.get('description', '')}"
        revenue = await self.extract_revenue_indicators(video_data, content_text)
        
        # Calculate advanced metrics
        virality_score = await self.calculate_virality_score(engagement, PlatformMetadata())
        
        # Create metadata object
        metadata = PlatformMetadata(
            platform_name="youtube",
            platform_url=url,
            api_version="v3",
            
            # Creator information
            creator_id=video_data.get('channel_id'),
            creator_username=video_data.get('uploader_id'),
            creator_display_name=video_data.get('uploader', video_data.get('channel_title')),
            creator_verified=False,  # Would need additional API call
            follower_count=video_data.get('channel_subscriber_count'),
            
            # Content information
            post_id=video_data.get('video_id'),
            post_type='video',
            post_title=video_data.get('title'),
            post_description=video_data.get('description'),
            post_url=url,
            thumbnail_url=video_data.get('thumbnail'),
            
            # Temporal information
            published_at=video_data.get('published_at'),
            crawled_at=datetime.now(),
            
            # Engagement metrics
            view_count=video_data.get('view_count'),
            like_count=video_data.get('like_count'),
            dislike_count=video_data.get('dislike_count'),
            comment_count=video_data.get('comment_count'),
            engagement_rate=engagement.current_views / engagement.current_likes if engagement.current_likes > 0 else 0,
            
            # Content metadata
            duration=video_data.get('duration'),
            language=video_data.get('default_language'),
            tags=video_data.get('tags', []),
            category=video_data.get('category_id'),
            
            # Revenue and monetization
            monetization_enabled=bool(video_data.get('monetization_details')),
            estimated_revenue=video_data.get('monetization_analysis', {}).get('estimated_revenue'),
            sponsorship_indicators=revenue.sponsored_content_indicators,
            brand_mentions=revenue.brand_partnerships,
            
            # AI analysis results
            content_sentiment=video_data.get('ai_analysis', {}).get('sentiment_analysis'),
            content_topics=video_data.get('ai_analysis', {}).get('topic_extraction', []),
            content_classification=video_data.get('ai_analysis', {}).get('content_classification'),
            virality_score=virality_score,
            trending_potential=video_data.get('trending_analysis', {}).get('trending_score'),
            
            # Protection and compliance
            age_restriction=video_data.get('age_limit'),
            privacy_level=video_data.get('privacy_status'),
            
            # Technical metadata
            extraction_method="multi_source",
            quality_score=video_data.get('ai_analysis', {}).get('content_quality_score', 0),
            data_completeness=self._calculate_data_completeness(video_data)
        )
        
        return metadata
    
    def _calculate_data_completeness(self, video_data: Dict[str, Any]) -> float:
        """Calculate data completeness score"""        try:
            total_fields = 20  # Total important fields
            filled_fields = 0
            
            important_fields = [
                'video_id', 'title', 'description', 'uploader', 'upload_date',
                'duration', 'view_count', 'like_count', 'comment_count',
                'tags', 'thumbnail', 'channel_id', 'category_id'
            ]
            
            for field in important_fields:
                if video_data.get(field):
                    filled_fields += 1
            
            # Bonus for advanced features
            if video_data.get('comments'):
                filled_fields += 2
            if video_data.get('captions'):
                filled_fields += 2
            if video_data.get('chapters'):
                filled_fields += 1
            if video_data.get('ai_analysis'):
                filled_fields += 2
            
            return min(100, (filled_fields / total_fields) * 100)
            
        except Exception as e:
            self.logger.error(f"Data completeness calculation failed: {e}")
            return 0.0
        """Extract content using yt-dlp"""        if not HAS_YTDLP:
            return {}
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'fr', 'de', 'es'],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                    'uploader_id': info.get('uploader_id'),
                    'upload_date': info.get('upload_date'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'comment_count': info.get('comment_count'),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'thumbnails': info.get('thumbnails', []),
                    'subtitles': info.get('subtitles', {}),
                    'automatic_captions': info.get('automatic_captions', {}),
                    'formats': info.get('formats', []),
                }
        except Exception as e:
            self.logger.error(f"yt-dlp extraction failed: {str(e)}")
            return {}
    
    async def _extract_with_api(self, video_id: str) -> Dict[str, Any]:
        """Extract content using YouTube Data API"""        if not self.api_key:
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get video details
                video_url = f"https://www.googleapis.com/youtube/v3/videos"
                video_params = {
                    'part': 'snippet,statistics,contentDetails,status',
                    'id': video_id,
                    'key': self.api_key
                }
                
                async with session.get(video_url, params=video_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        if items:
                            item = items[0]
                            snippet = item.get('snippet', {})
                            statistics = item.get('statistics', {})
                            
                            return {
                                'title': snippet.get('title'),
                                'description': snippet.get('description'),
                                'channel_id': snippet.get('channelId'),
                                'channel_title': snippet.get('channelTitle'),
                                'published_at': snippet.get('publishedAt'),
                                'tags': snippet.get('tags', []),
                                'category_id': snippet.get('categoryId'),
                                'default_language': snippet.get('defaultLanguage'),
                                'view_count': int(statistics.get('viewCount', 0)),
                                'like_count': int(statistics.get('likeCount', 0)),
                                'comment_count': int(statistics.get('commentCount', 0)),
                                'favorite_count': int(statistics.get('favoriteCount', 0)),
                            }
        except Exception as e:
            self.logger.error(f"YouTube API extraction failed: {str(e)}")
            return {}
    
    def _merge_extraction_data(self, ytdlp_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Merge data from different extraction methods"""        merged = {}
        
        # Prioritize API data when available, fallback to yt-dlp
        for key in ['title', 'description', 'view_count', 'like_count', 'comment_count']:
            merged[key] = api_data.get(key) or ytdlp_data.get(key)
        
        # Combine tags from both sources
        tags = set(api_data.get('tags', []) + ytdlp_data.get('tags', []))
        merged['tags'] = list(tags)
        
        # Include all other data
        merged.update(ytdlp_data)
        merged.update(api_data)
        
        return merged
    
    async def _extract_youtube_metadata(self, data: Dict, url: str) -> PlatformMetadata:
        """Extract YouTube-specific metadata"""        return PlatformMetadata(
            platform_id=self._extract_video_id(url),
            platform_url=url,
            creator_username=data.get('uploader_id') or data.get('channel_id'),
            creator_display_name=data.get('uploader') or data.get('channel_title'),
            published_at=self._parse_youtube_date(data.get('upload_date') or data.get('published_at')),
            view_count=data.get('view_count'),
            like_count=data.get('like_count'),
            comment_count=data.get('comment_count'),
            hashtags=self._extract_hashtags(data.get('description', '')),
            language=data.get('default_language')
        )
    
    def _parse_youtube_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse YouTube date string to datetime"""        if not date_str:
            return None
        
        try:
            if len(date_str) == 8:  # YYYYMMDD format
                return datetime.strptime(date_str, '%Y%m%d')
            else:  # ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""        return re.findall(r'#(\w+)', text)
    
    async def normalize_url(self, url: str) -> str:
        """Normalize YouTube URL to canonical form"""        video_id = self._extract_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url


class InstagramExtractor(BasePlatformExtractor):
    """Advanced Instagram content extractor"""    
    def __init__(self):
        super().__init__("InstagramExtractor", "instagram")
        self.post_pattern = re.compile(r'instagram\.com/p/([a-zA-Z0-9_-]+)')
        self.reel_pattern = re.compile(r'instagram\.com/reel/([a-zA-Z0-9_-]+)')
        self.story_pattern = re.compile(r'instagram\.com/stories/([^/]+)/([0-9]+)')
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for Instagram content"""        if not request.source_url:
            return False
        return 'instagram.com' in request.source_url
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract Instagram content and metadata"""        try:
            url = await self.normalize_url(request.source_url)
            
            # Extract using web scraping (requires Selenium)
            if HAS_SELENIUM:
                content_data = await self._extract_with_selenium(url)
            else:
                content_data = await self._extract_with_requests(url)
            
            # Determine content type
            content_type = await self.detect_content_type(url, str(content_data))
            
            # Extract platform metadata
            platform_meta = await self._extract_instagram_metadata(content_data, url)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=content_data,
                metadata={"platform": platform_meta},
                content_type=content_type,
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Instagram extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _extract_with_selenium(self, url: str) -> Dict[str, Any]:
        """Extract Instagram content using Selenium"""        if not HAS_SELENIUM:
            return {}
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for content to load
            wait = WebDriverWait(driver, 10)
            
            try:
                # Extract post data
                post_data = {}
                
                # Try to get caption
                try:
                    caption_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'article div[data-testid="post-caption"]'))
                    )
                    post_data['caption'] = caption_element.text
                except Exception:
                    pass
                
                # Try to get image/video URLs
                try:
                    media_elements = driver.find_elements(By.CSS_SELECTOR, 'article img, article video')
                    media_urls = []
                    for element in media_elements:
                        src = element.get_attribute('src')
                        if src and 'instagram' in src:
                            media_urls.append(src)
                    post_data['media_urls'] = media_urls
                except Exception:
                    pass
                
                # Try to get engagement metrics
                try:
                    likes_element = driver.find_element(By.CSS_SELECTOR, 'article button[data-testid="like-button"] + span')
                    post_data['likes'] = likes_element.text
                except Exception:
                    pass
                
                # Get page source for further parsing
                post_data['page_source'] = driver.page_source
                
                return post_data
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium Instagram extraction failed: {str(e)}")
            return {}
    
    async def _extract_with_requests(self, url: str) -> Dict[str, Any]:
        """Extract Instagram content using requests (limited)"""        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Try to extract JSON data from script tags
                        if HAS_BS4:
                            soup = BeautifulSoup(content, 'html.parser')
                            scripts = soup.find_all('script', type='application/ld+json')
                            
                            for script in scripts:
                                try:
                                    data = json.loads(script.string)
                                    if '@type' in data and 'SocialMediaPosting' in data.get('@type', ''):
                                        return {
                                            'caption': data.get('caption', ''),
                                            'author': data.get('author', {}).get('name', ''),
                                            'date_published': data.get('datePublished', ''),
                                            'interaction_statistic': data.get('interactionStatistic', []),
                                            'page_content': content[:5000]  # Truncated content
                                        }
                                except json.JSONDecodeError:
                                    continue
                        
                        return {'page_content': content[:5000]}
                    
        except Exception as e:
            self.logger.error(f"Requests Instagram extraction failed: {str(e)}")
            return {}
    
    async def _extract_instagram_metadata(self, data: Dict, url: str) -> PlatformMetadata:
        """Extract Instagram-specific metadata"""        post_id = self._extract_post_id(url)
        
        return PlatformMetadata(
            platform_id=post_id,
            platform_url=url,
            creator_username=data.get('author'),
            published_at=self._parse_instagram_date(data.get('date_published')),
            hashtags=self._extract_hashtags(data.get('caption', '')),
            mentions=self._extract_mentions(data.get('caption', ''))
        )
    
    def _extract_post_id(self, url: str) -> Optional[str]:
        """Extract Instagram post ID from URL"""        for pattern in [self.post_pattern, self.reel_pattern]:
            match = pattern.search(url)
            if match:
                return match.group(1)
        return None
    
    def _parse_instagram_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Instagram date string to datetime"""        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""        return re.findall(r'@(\w+)', text)
    
    async def normalize_url(self, url: str) -> str:
        """Normalize Instagram URL to canonical form"""        return url.split('?')[0]  # Remove query parameters


class TikTokExtractor(BasePlatformExtractor):
    """Advanced TikTok content extractor"""    
    def __init__(self):
        super().__init__("TikTokExtractor", "tiktok")
        self.video_pattern = re.compile(r'tiktok\.com/@[^/]+/video/(\d+)')
        self.short_pattern = re.compile(r'vm\.tiktok\.com/([a-zA-Z0-9]+)')
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for TikTok content"""        if not request.source_url:
            return False
        return 'tiktok.com' in request.source_url or 'vm.tiktok.com' in request.source_url
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract TikTok content and metadata"""        try:
            url = await self.normalize_url(request.source_url)
            
            # Extract using yt-dlp if available
            content_data = {}
            if HAS_YTDLP:
                content_data = await self._extract_with_ytdlp(url)
            
            # Fallback to web scraping
            if not content_data and HAS_SELENIUM:
                content_data = await self._extract_with_selenium(url)
            
            # Extract platform metadata
            platform_meta = await self._extract_tiktok_metadata(content_data, url)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=content_data,
                metadata={"platform": platform_meta},
                content_type=ContentType.VIDEO,
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"TikTok extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _extract_with_ytdlp(self, url: str) -> Dict[str, Any]:
        """Extract TikTok content using yt-dlp"""        if not HAS_YTDLP:
            return {}
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                    'uploader_id': info.get('uploader_id'),
                    'upload_date': info.get('upload_date'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'comment_count': info.get('comment_count'),
                    'tags': info.get('tags', []),
                    'thumbnails': info.get('thumbnails', []),
                    'formats': info.get('formats', []),
                }
        except Exception as e:
            self.logger.error(f"yt-dlp TikTok extraction failed: {str(e)}")
            return {}
    
    async def _extract_with_selenium(self, url: str) -> Dict[str, Any]:
        """Extract TikTok content using Selenium"""        if not HAS_SELENIUM:
            return {}
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for content to load
            wait = WebDriverWait(driver, 15)
            
            try:
                video_data = {}
                
                # Try to get video description
                try:
                    desc_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-e2e="video-desc"]'))
                    )
                    video_data['description'] = desc_element.text
                except Exception:
                    pass
                
                # Try to get author info
                try:
                    author_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="video-author-uniqueid"]')
                    video_data['author'] = author_element.text
                except Exception:
                    pass
                
                # Try to get engagement metrics
                try:
                    like_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="like-count"]')
                    video_data['like_count'] = like_element.text
                except Exception:
                    pass
                
                try:
                    comment_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="comment-count"]')
                    video_data['comment_count'] = comment_element.text
                except Exception:
                    pass
                
                try:
                    share_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="share-count"]')
                    video_data['share_count'] = share_element.text
                except Exception:
                    pass
                
                return video_data
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium TikTok extraction failed: {str(e)}")
            return {}
    
    async def _extract_tiktok_metadata(self, data: Dict, url: str) -> PlatformMetadata:
        """Extract TikTok-specific metadata"""        video_id = self._extract_video_id(url)
        
        return PlatformMetadata(
            platform_id=video_id,
            platform_url=url,
            creator_username=data.get('uploader_id') or data.get('author'),
            creator_display_name=data.get('uploader'),
            published_at=self._parse_tiktok_date(data.get('upload_date')),
            view_count=self._parse_count(data.get('view_count')),
            like_count=self._parse_count(data.get('like_count')),
            comment_count=self._parse_count(data.get('comment_count')),
            share_count=self._parse_count(data.get('share_count')),
            hashtags=self._extract_hashtags(data.get('description', '')),
            mentions=self._extract_mentions(data.get('description', ''))
        )
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract TikTok video ID from URL"""        match = self.video_pattern.search(url)
        return match.group(1) if match else None
    
    def _parse_tiktok_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse TikTok date string to datetime"""        if not date_str:
            return None
        
        try:
            if len(date_str) == 8:  # YYYYMMDD format
                return datetime.strptime(date_str, '%Y%m%d')
            else:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def _parse_count(self, count_str: Optional[str]) -> Optional[int]:
        """Parse count string (e.g., '1.2K', '500M') to integer"""        if not count_str:
            return None
        
        if isinstance(count_str, int):
            return count_str
        
        count_str = str(count_str).upper()
        
        try:
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            else:
                return int(count_str)
        except (ValueError, TypeError):
            return None
    
    async def normalize_url(self, url: str) -> str:
        """Normalize TikTok URL to canonical form"""        # Handle short URLs
        if 'vm.tiktok.com' in url:
            # Would need to follow redirect to get full URL
            return url
        
        return url.split('?')[0]  # Remove query parameters


class TwitterExtractor(BasePlatformExtractor):
    """Advanced Twitter/X content extractor"""    
    def __init__(self):
        super().__init__("TwitterExtractor", "twitter")
        self.tweet_pattern = re.compile(r'(?:twitter\.com|x\.com)/\w+/status/(\d+)')
        self.api_bearer_token = None  # Set from config
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for Twitter/X content"""        if not request.source_url:
            return False
        return any(domain in request.source_url for domain in ['twitter.com', 'x.com'])
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract Twitter content and metadata"""        try:
            url = await self.normalize_url(request.source_url)
            tweet_id = self._extract_tweet_id(url)
            
            if not tweet_id:
                return ExtractionResult(
                    request_id=request.request_id,
                    status=ExtractionStatus.FAILED,
                    error="Unable to extract tweet ID from URL"
                )
            
            # Extract using Twitter API if available
            content_data = {}
            if self.api_bearer_token:
                content_data = await self._extract_with_api(tweet_id)
            
            # Fallback to web scraping
            if not content_data and HAS_SELENIUM:
                content_data = await self._extract_with_selenium(url)
            
            # Extract platform metadata
            platform_meta = await self._extract_twitter_metadata(content_data, url)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=content_data,
                metadata={"platform": platform_meta},
                content_type=ContentType.TEXT,
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Twitter extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    def _extract_tweet_id(self, url: str) -> Optional[str]:
        """Extract tweet ID from URL"""        match = self.tweet_pattern.search(url)
        return match.group(1) if match else None
    
    async def _extract_with_api(self, tweet_id: str) -> Dict[str, Any]:
        """Extract tweet using Twitter API v2"""        if not self.api_bearer_token:
            return {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_bearer_token}',
                'Content-Type': 'application/json',
            }
            
            # Define tweet fields to retrieve
            tweet_fields = [
                'created_at', 'author_id', 'public_metrics', 'context_annotations',
                'entities', 'geo', 'in_reply_to_user_id', 'lang', 'possibly_sensitive',
                'referenced_tweets', 'reply_settings', 'source', 'text', 'withheld'
            ]
            
            user_fields = ['username', 'name', 'verified', 'public_metrics', 'description']
            expansions = ['author_id', 'attachments.media_keys', 'referenced_tweets.id']
            
            params = {
                'tweet.fields': ','.join(tweet_fields),
                'user.fields': ','.join(user_fields),
                'expansions': ','.join(expansions),
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.twitter.com/2/tweets/{tweet_id}"
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        tweet = data.get('data', {})
                        includes = data.get('includes', {})
                        users = {user['id']: user for user in includes.get('users', [])}
                        
                        author = users.get(tweet.get('author_id'), {})
                        metrics = tweet.get('public_metrics', {})
                        
                        return {
                            'text': tweet.get('text'),
                            'created_at': tweet.get('created_at'),
                            'author_id': tweet.get('author_id'),
                            'author_username': author.get('username'),
                            'author_name': author.get('name'),
                            'author_verified': author.get('verified', False),
                            'author_followers': author.get('public_metrics', {}).get('followers_count'),
                            'retweet_count': metrics.get('retweet_count', 0),
                            'reply_count': metrics.get('reply_count', 0),
                            'like_count': metrics.get('like_count', 0),
                            'quote_count': metrics.get('quote_count', 0),
                            'impression_count': metrics.get('impression_count', 0),
                            'language': tweet.get('lang'),
                            'entities': tweet.get('entities', {}),
                            'context_annotations': tweet.get('context_annotations', []),
                        }
                        
        except Exception as e:
            self.logger.error(f"Twitter API extraction failed: {str(e)}")
            return {}
    
    async def _extract_with_selenium(self, url: str) -> Dict[str, Any]:
        """Extract Twitter content using Selenium"""        if not HAS_SELENIUM:
            return {}
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for content to load
            wait = WebDriverWait(driver, 10)
            
            try:
                tweet_data = {}
                
                # Try to get tweet text
                try:
                    text_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]'))
                    )
                    tweet_data['text'] = text_element.text
                except Exception:
                    pass
                
                # Try to get author info
                try:
                    author_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    tweet_data['author'] = author_element.text
                except Exception:
                    pass
                
                # Try to get engagement metrics
                try:
                    metrics_elements = driver.find_elements(By.CSS_SELECTOR, '[role="group"] [data-testid]')
                    for element in metrics_elements:
                        test_id = element.get_attribute('data-testid')
                        if 'reply' in test_id:
                            tweet_data['reply_count'] = element.text
                        elif 'retweet' in test_id:
                            tweet_data['retweet_count'] = element.text
                        elif 'like' in test_id:
                            tweet_data['like_count'] = element.text
                except Exception:
                    pass
                
                return tweet_data
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium Twitter extraction failed: {str(e)}")
            return {}
    
    async def _extract_twitter_metadata(self, data: Dict, url: str) -> PlatformMetadata:
        """Extract Twitter-specific metadata"""        tweet_id = self._extract_tweet_id(url)
        
        return PlatformMetadata(
            platform_id=tweet_id,
            platform_url=url,
            creator_id=data.get('author_id'),
            creator_username=data.get('author_username'),
            creator_display_name=data.get('author_name') or data.get('author'),
            published_at=self._parse_twitter_date(data.get('created_at')),
            like_count=self._parse_count(data.get('like_count')),
            comment_count=self._parse_count(data.get('reply_count')),
            share_count=self._parse_count(data.get('retweet_count')),
            view_count=data.get('impression_count'),
            hashtags=self._extract_hashtags(data.get('text', '')),
            mentions=self._extract_mentions(data.get('text', '')),
            language=data.get('language'),
            is_verified=data.get('author_verified', False),
            follower_count=data.get('author_followers')
        )
    
    def _parse_twitter_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Twitter date string to datetime"""        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    async def normalize_url(self, url: str) -> str:
        """Normalize Twitter URL to canonical form"""        # Convert x.com to twitter.com for consistency
        url = url.replace('x.com', 'twitter.com')
        return url.split('?')[0]  # Remove query parameters


class FacebookExtractor(BasePlatformExtractor):
    """Advanced Facebook content extractor"""    
    def __init__(self):
        super().__init__("FacebookExtractor", "facebook")
        self.post_pattern = re.compile(r'facebook\.com/[^/]+/posts/(\d+)')
        self.video_pattern = re.compile(r'facebook\.com/[^/]+/videos/(\d+)')
        self.access_token = None  # Set from config
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for Facebook content"""        if not request.source_url:
            return False
        return 'facebook.com' in request.source_url
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract Facebook content and metadata"""        try:
            url = await self.normalize_url(request.source_url)
            post_id = self._extract_post_id(url)
            
            # Note: Facebook Graph API has strict requirements and limitations
            # Most public content extraction now requires special permissions
            
            content_data = {}
            if self.access_token and post_id:
                content_data = await self._extract_with_api(post_id)
            
            # Web scraping is very limited due to Facebook's anti-bot measures
            if not content_data and HAS_SELENIUM:
                content_data = await self._extract_with_selenium(url)
            
            # Extract platform metadata
            platform_meta = await self._extract_facebook_metadata(content_data, url)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=content_data,
                metadata={"platform": platform_meta},
                content_type=await self.detect_content_type(url, str(content_data)),
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Facebook extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    def _extract_post_id(self, url: str) -> Optional[str]:
        """Extract Facebook post ID from URL"""        for pattern in [self.post_pattern, self.video_pattern]:
            match = pattern.search(url)
            if match:
                return match.group(1)
        return None
    
    async def _extract_with_api(self, post_id: str) -> Dict[str, Any]:
        """Extract Facebook content using Graph API"""        if not self.access_token:
            return {}
        
        try:
            fields = [
                'id', 'message', 'story', 'created_time', 'from',
                'likes.summary(true)', 'comments.summary(true)', 'shares'
            ]
            
            params = {
                'fields': ','.join(fields),
                'access_token': self.access_token
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{post_id}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            'message': data.get('message'),
                            'story': data.get('story'),
                            'created_time': data.get('created_time'),
                            'from': data.get('from', {}).get('name'),
                            'from_id': data.get('from', {}).get('id'),
                            'like_count': data.get('likes', {}).get('summary', {}).get('total_count', 0),
                            'comment_count': data.get('comments', {}).get('summary', {}).get('total_count', 0),
                            'share_count': data.get('shares', {}).get('count', 0),
                        }
                        
        except Exception as e:
            self.logger.error(f"Facebook API extraction failed: {str(e)}")
            return {}
    
    async def _extract_with_selenium(self, url: str) -> Dict[str, Any]:
        """Extract Facebook content using Selenium (very limited)"""        if not HAS_SELENIUM:
            return {}
        
        # Note: This is extremely limited due to Facebook's anti-automation measures
        # Most content requires login and will be blocked
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Facebook will likely redirect to login or show limited content
            time.sleep(3)
            
            try:
                page_title = driver.title
                page_source = driver.page_source[:1000]  # Limited sample
                
                return {
                    'page_title': page_title,
                    'limited_content': page_source,
                    'note': 'Facebook content extraction is very limited without proper API access'
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Selenium Facebook extraction failed: {str(e)}")
            return {}
    
    async def _extract_facebook_metadata(self, data: Dict, url: str) -> PlatformMetadata:
        """Extract Facebook-specific metadata"""        post_id = self._extract_post_id(url)
        
        return PlatformMetadata(
            platform_id=post_id,
            platform_url=url,
            creator_id=data.get('from_id'),
            creator_display_name=data.get('from'),
            published_at=self._parse_facebook_date(data.get('created_time')),
            like_count=data.get('like_count'),
            comment_count=data.get('comment_count'),
            share_count=data.get('share_count'),
            hashtags=self._extract_hashtags(data.get('message', '')),
            mentions=self._extract_mentions(data.get('message', ''))
        )
    
    def _parse_facebook_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Facebook date string to datetime"""        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    async def normalize_url(self, url: str) -> str:
        """Normalize Facebook URL to canonical form"""        return url.split('?')[0]  # Remove query parameters


class SpotifyExtractor(BasePlatformExtractor):
    """Advanced Spotify content extractor"""    
    def __init__(self):
        super().__init__("SpotifyExtractor", "spotify")
        self.track_pattern = re.compile(r'spotify\.com/track/([a-zA-Z0-9]+)')
        self.album_pattern = re.compile(r'spotify\.com/album/([a-zA-Z0-9]+)')
        self.artist_pattern = re.compile(r'spotify\.com/artist/([a-zA-Z0-9]+)')
        self.playlist_pattern = re.compile(r'spotify\.com/playlist/([a-zA-Z0-9]+)')
        self.client_id = None  # Set from config
        self.client_secret = None  # Set from config
        self.access_token = None
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for Spotify content"""        if not request.source_url:
            return False
        return 'spotify.com' in request.source_url
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract Spotify content and metadata"""        try:
            url = await self.normalize_url(request.source_url)
            
            # Get access token if not available
            if not self.access_token:
                await self._get_access_token()
            
            content_data = {}
            if self.access_token:
                content_data = await self._extract_with_api(url)
            
            # Extract platform metadata
            platform_meta = await self._extract_spotify_metadata(content_data, url)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data=content_data,
                metadata={"platform": platform_meta},
                content_type=ContentType.AUDIO,
                processing_time=time.time() - time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Spotify extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _get_access_token(self):
        """Get Spotify API access token"""        if not self.client_id or not self.client_secret:
            return
        
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('utf-8')
            auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            headers = {
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://accounts.spotify.com/api/token',
                    headers=headers,
                    data=data
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        
        except Exception as e:
            self.logger.error(f"Spotify token acquisition failed: {str(e)}")
    
    async def _extract_with_api(self, url: str) -> Dict[str, Any]:
        """Extract Spotify content using Web API"""        if not self.access_token:
            return {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }
            
            # Determine content type and ID
            track_match = self.track_pattern.search(url)
            album_match = self.album_pattern.search(url)
            artist_match = self.artist_pattern.search(url)
            playlist_match = self.playlist_pattern.search(url)
            
            async with aiohttp.ClientSession() as session:
                if track_match:
                    track_id = track_match.group(1)
                    return await self._extract_track(session, headers, track_id)
                elif album_match:
                    album_id = album_match.group(1)
                    return await self._extract_album(session, headers, album_id)
                elif artist_match:
                    artist_id = artist_match.group(1)
                    return await self._extract_artist(session, headers, artist_id)
                elif playlist_match:
                    playlist_id = playlist_match.group(1)
                    return await self._extract_playlist(session, headers, playlist_id)
                    
        except Exception as e:
            self.logger.error(f"Spotify API extraction failed: {str(e)}")
            return {}
    
    async def _extract_track(self, session: aiohttp.ClientSession, headers: Dict, track_id: str) -> Dict[str, Any]:
        """Extract Spotify track data"""        async with session.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers) as response:
            if response.status == 200:
                track = await response.json()
                
                return {
                    'type': 'track',
                    'id': track.get('id'),
                    'name': track.get('name'),
                    'artists': [artist.get('name') for artist in track.get('artists', [])],
                    'album': track.get('album', {}).get('name'),
                    'duration_ms': track.get('duration_ms'),
                    'explicit': track.get('explicit'),
                    'popularity': track.get('popularity'),
                    'preview_url': track.get('preview_url'),
                    'external_urls': track.get('external_urls', {}),
                    'release_date': track.get('album', {}).get('release_date'),
                    'genres': track.get('album', {}).get('genres', []),
                    'images': track.get('album', {}).get('images', []),
                }
        return {}
    
    async def _extract_album(self, session: aiohttp.ClientSession, headers: Dict, album_id: str) -> Dict[str, Any]:
        """Extract Spotify album data"""        async with session.get(f'https://api.spotify.com/v1/albums/{album_id}', headers=headers) as response:
            if response.status == 200:
                album = await response.json()
                
                return {
                    'type': 'album',
                    'id': album.get('id'),
                    'name': album.get('name'),
                    'artists': [artist.get('name') for artist in album.get('artists', [])],
                    'total_tracks': album.get('total_tracks'),
                    'release_date': album.get('release_date'),
                    'genres': album.get('genres', []),
                    'popularity': album.get('popularity'),
                    'images': album.get('images', []),
                    'tracks': [
                        {
                            'name': track.get('name'),
                            'duration_ms': track.get('duration_ms'),
                            'track_number': track.get('track_number')
                        }
                        for track in album.get('tracks', {}).get('items', [])
                    ]
                }
        return {}
    
    async def _extract_artist(self, session: aiohttp.ClientSession, headers: Dict, artist_id: str) -> Dict[str, Any]:
        """Extract Spotify artist data"""        async with session.get(f'https://api.spotify.com/v1/artists/{artist_id}', headers=headers) as response:
            if response.status == 200:
                artist = await response.json()
                
                return {
                    'type': 'artist',
                    'id': artist.get('id'),
                    'name': artist.get('name'),
                    'genres': artist.get('genres', []),
                    'popularity': artist.get('popularity'),
                    'followers': artist.get('followers', {}).get('total'),
                    'images': artist.get('images', []),
                    'external_urls': artist.get('external_urls', {}),
                }
        return {}
    
    async def _extract_playlist(self, session: aiohttp.ClientSession, headers: Dict, playlist_id: str) -> Dict[str, Any]:
        """Extract Spotify playlist data"""        async with session.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers) as response:
            if response.status == 200:
                playlist = await response.json()
                
                return {
                    'type': 'playlist',
                    'id': playlist.get('id'),
                    'name': playlist.get('name'),
                    'description': playlist.get('description'),
                    'owner': playlist.get('owner', {}).get('display_name'),
                    'owner_id': playlist.get('owner', {}).get('id'),
                    'public': playlist.get('public'),
                    'collaborative': playlist.get('collaborative'),
                    'followers': playlist.get('followers', {}).get('total'),
                    'tracks_total': playlist.get('tracks', {}).get('total'),
                    'images': playlist.get('images', []),
                    'tracks': [
                        {
                            'name': item.get('track', {}).get('name'),
                            'artists': [artist.get('name') for artist in item.get('track', {}).get('artists', [])],
                            'added_at': item.get('added_at')
                        }
                        for item in playlist.get('tracks', {}).get('items', [])
                        if item.get('track')
                    ][:50]  # Limit to first 50 tracks
                }
        return {}
    
    async def _extract_spotify_metadata(self, data: Dict, url: str) -> PlatformMetadata:
        """Extract Spotify-specific metadata"""        return PlatformMetadata(
            platform_id=data.get('id'),
            platform_url=url,
            creator_username=data.get('owner_id') if data.get('type') == 'playlist' else None,
            creator_display_name=data.get('owner') if data.get('type') == 'playlist' else None,
            published_at=self._parse_spotify_date(data.get('release_date')),
            follower_count=data.get('followers')
        )
    
    def _parse_spotify_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Spotify date string to datetime"""        if not date_str:
            return None
        
        try:
            # Spotify dates can be YYYY, YYYY-MM, or YYYY-MM-DD
            if len(date_str) == 4:  # Year only
                return datetime.strptime(date_str, '%Y')
            elif len(date_str) == 7:  # Year-Month
                return datetime.strptime(date_str, '%Y-%m')
            else:  # Full date
                return datetime.strptime(date_str, '%Y-%m-%d')
        except Exception:
            return None
    
    async def normalize_url(self, url: str) -> str:
        """Normalize Spotify URL to canonical form"""        return url.split('?')[0]  # Remove query parameters


# Platform Extractor Factory
class PlatformExtractorFactory:
    """Factory for creating platform-specific extractors"""    
    _extractors: Dict[str, BasePlatformExtractor] = {}
    
    @classmethod
    def register_extractor(cls, extractor: BasePlatformExtractor):
        """Register a platform extractor"""        cls._extractors[extractor.platform] = extractor
    
    @classmethod
    def get_extractor(cls, platform: str) -> Optional[BasePlatformExtractor]:
        """Get extractor for specific platform"""        return cls._extractors.get(platform.lower())
    
    @classmethod
    def get_extractor_for_url(cls, url: str) -> Optional[BasePlatformExtractor]:
        """Get appropriate extractor for URL"""        url_lower = url.lower()
        
        for extractor in cls._extractors.values():
            if asyncio.run(extractor.can_handle(ExtractionRequest(source_url=url))):
                return extractor
        
        return None
    
    @classmethod
    def list_supported_platforms(cls) -> List[str]:
        """List all supported platforms"""        return list(cls._extractors.keys())


# Register all platform extractors
def register_default_extractors():
    """Register all default platform extractors"""    factory = PlatformExtractorFactory
    
    factory.register_extractor(YouTubeExtractor())
    factory.register_extractor(InstagramExtractor())
    factory.register_extractor(TikTokExtractor())
    factory.register_extractor(TwitterExtractor())
    factory.register_extractor(FacebookExtractor())
    factory.register_extractor(SpotifyExtractor())


# Initialize on import
register_default_extractors()


__all__ = [
    'PlatformMetadata',
    'BasePlatformExtractor', 
    'YouTubeExtractor',
    'InstagramExtractor',
    'TikTokExtractor', 
    'TwitterExtractor',
    'FacebookExtractor',
    'SpotifyExtractor',
    'PlatformExtractorFactory',
    'register_default_extractors'
]
