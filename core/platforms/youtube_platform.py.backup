"""Advanced YouTube Platform Integration - Ultra-Advanced Implementation
AI-Powered YouTube Content Management and Analytics System

This module provides comprehensive YouTube platform integration with advanced content management,
analytics, monetization optimization, and AI-powered insights for influencer marketing.
"""
import asyncio
import aiohttp
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import hashlib
import statistics
import numpy as np
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import threading
from urllib.parse import urlparse, parse_qs
import isodate
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_platform import BasePlatform
from ..utils.rate_limiter import RateLimiter
from ..utils.cache import CacheManager
from ..utils.encryption import ContentEncryption

logger = logging.getLogger(__name__)


class YouTubeContentType(str, Enum):
    """YouTube content types"""
    VIDEO = "video"
    SHORT = "short"
    LIVE_STREAM = "live_stream"
    PREMIERE = "premiere"
    PLAYLIST = "playlist"
    COMMUNITY_POST = "community_post"
    STORY = "story"


class YouTubeVideoCategory(str, Enum):
    """YouTube video categories"""
    FILM_ANIMATION = "1"
    AUTOS_VEHICLES = "2"
    MUSIC = "10"
    PETS_ANIMALS = "15"
    SPORTS = "17"
    TRAVEL_EVENTS = "19"
    GAMING = "20"
    PEOPLE_BLOGS = "22"
    COMEDY = "23"
    ENTERTAINMENT = "24"
    NEWS_POLITICS = "25"
    HOWTO_STYLE = "26"
    EDUCATION = "27"
    SCIENCE_TECHNOLOGY = "28"
    NONPROFITS_ACTIVISM = "29"


class YouTubePrivacyStatus(str, Enum):
    """YouTube video privacy status"""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    SCHEDULED = "scheduled"


class YouTubeEngagementType(str, Enum):
    """YouTube engagement types"""
    LIKE = "like"
    DISLIKE = "dislike"
    COMMENT = "comment"
    SHARE = "share"
    SUBSCRIBE = "subscribe"
    VIEW = "view"
    IMPRESSION = "impression"
    CLICK = "click"


class YouTubeVideo(BaseModel):
    """YouTube video model"""
    video_id: str
    title: str
    description: str = ""
    
    # Channel information
    channel_id: str
    channel_title: str
    
    # Content details
    duration: Optional[str] = None  # ISO 8601 duration
    category_id: str = "22"  # Default to People & Blogs
    tags: List[str] = Field(default_factory=list)
    default_language: str = "en"
    
    # Privacy and publishing
    privacy_status: YouTubePrivacyStatus = YouTubePrivacyStatus.PUBLIC
    published_at: Optional[datetime] = None
    scheduled_publish_time: Optional[datetime] = None
    
    # Thumbnails
    thumbnail_url: Optional[str] = None
    custom_thumbnail: Optional[str] = None
    
    # Statistics
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    favorite_count: int = 0
    
    # Engagement metrics
    engagement_rate: float = 0.0
    watch_time_hours: float = 0.0
    average_view_duration: float = 0.0
    retention_rate: float = 0.0
    
    # Revenue and monetization
    estimated_revenue: float = 0.0
    ad_revenue: float = 0.0
    membership_revenue: float = 0.0
    super_chat_revenue: float = 0.0
    
    # SEO and discovery
    search_rankings: Dict[str, int] = Field(default_factory=dict)
    traffic_sources: Dict[str, float] = Field(default_factory=dict)
    
    # AI insights
    content_quality_score: float = 0.0
    virality_potential: float = 0.0
    audience_retention_score: float = 0.0
    optimization_score: float = 0.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_analyzed: Optional[datetime] = None


class YouTubeChannel(BaseModel):
    """YouTube channel model"""
    channel_id: str
    title: str
    description: str = ""
    
    # Channel details
    custom_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    
    # Statistics
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
    
    # Content metrics
    upload_frequency: float = 0.0  # videos per week
    average_video_length: float = 0.0  # minutes
    total_watch_time: float = 0.0  # hours
    
    # Audience demographics
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    top_countries: List[Dict[str, Any]] = Field(default_factory=list)
    gender_distribution: Dict[str, float] = Field(default_factory=dict)
    age_distribution: Dict[str, float] = Field(default_factory=dict)
    
    # Performance metrics
    growth_rate: float = 0.0  # percentage
    engagement_rate: float = 0.0
    monetization_enabled: bool = False
    estimated_monthly_revenue: float = 0.0
    
    # Content categories
    primary_category: Optional[str] = None
    content_categories: List[str] = Field(default_factory=list)
    
    # SEO and branding
    keywords: List[str] = Field(default_factory=list)
    brand_safety_score: float = 100.0
    content_quality_score: float = 0.0
    
    # AI insights
    growth_potential: float = 0.0
    content_optimization_score: float = 0.0
    audience_loyalty_score: float = 0.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False


class YouTubeComment(BaseModel):
    """YouTube comment model"""
    comment_id: str
    video_id: str
    
    # Comment details
    text: str
    author_name: str
    author_channel_id: Optional[str] = None
    
    # Engagement
    like_count: int = 0
    reply_count: int = 0
    
    # Metadata
    published_at: datetime
    updated_at: Optional[datetime] = None
    
    # Analysis
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    toxicity_score: float = 0.0
    relevance_score: float = 0.0
    
    # Moderation
    moderation_status: str = "approved"  # "approved", "pending", "rejected"
    auto_moderated: bool = False


class YouTubeAnalytics(BaseModel):
    """YouTube analytics data"""
    channel_id: str
    video_id: Optional[str] = None
    
    # Time period
    start_date: datetime
    end_date: datetime
    
    # View metrics
    views: int = 0
    unique_viewers: int = 0
    impressions: int = 0
    impression_ctr: float = 0.0
    
    # Engagement metrics
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    shares: int = 0
    subscribers_gained: int = 0
    subscribers_lost: int = 0
    
    # Watch time metrics
    watch_time_minutes: float = 0.0
    average_view_duration: float = 0.0
    retention_rate: float = 0.0
    
    # Revenue metrics
    estimated_revenue: float = 0.0
    ad_revenue: float = 0.0
    cpm: float = 0.0  # Cost per mille
    rpm: float = 0.0  # Revenue per mille
    
    # Traffic sources
    traffic_from_youtube_search: float = 0.0
    traffic_from_suggested_videos: float = 0.0
    traffic_from_external_sources: float = 0.0
    traffic_from_playlists: float = 0.0
    
    # Demographics
    viewer_demographics: Dict[str, Any] = Field(default_factory=dict)
    top_countries: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Device and platform data
    device_types: Dict[str, float] = Field(default_factory=dict)
    operating_systems: Dict[str, float] = Field(default_factory=dict)


class YouTubeOptimization(BaseModel):
    """YouTube optimization recommendations"""
    video_id: Optional[str] = None
    channel_id: str
    
    # SEO optimizations
    title_suggestions: List[str] = Field(default_factory=list)
    description_improvements: List[str] = Field(default_factory=list)
    tag_recommendations: List[str] = Field(default_factory=list)
    thumbnail_suggestions: List[str] = Field(default_factory=list)
    
    # Content optimizations
    optimal_video_length: Optional[float] = None
    best_upload_times: List[str] = Field(default_factory=list)
    content_suggestions: List[str] = Field(default_factory=list)
    trending_topics: List[str] = Field(default_factory=list)
    
    # Engagement optimizations
    call_to_action_suggestions: List[str] = Field(default_factory=list)
    community_engagement_tips: List[str] = Field(default_factory=list)
    collaboration_opportunities: List[str] = Field(default_factory=list)
    
    # Monetization optimizations
    ad_placement_recommendations: List[str] = Field(default_factory=list)
    merchandise_opportunities: List[str] = Field(default_factory=list)
    sponsorship_potential: float = 0.0
    
    # Performance predictions
    predicted_views: int = 0
    predicted_engagement_rate: float = 0.0
    predicted_revenue: float = 0.0
    
    # Priority and impact
    optimization_priority: str = "medium"  # "low", "medium", "high", "critical"
    estimated_impact: float = 0.0  # percentage improvement
    
    # Implementation
    implementation_difficulty: str = "medium"  # "easy", "medium", "hard"
    estimated_time_to_implement: int = 0  # hours
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))


class AdvancedYouTubePlatform(BasePlatform):
    """
    Ultra-Advanced YouTube Platform Integration
    
    Comprehensive YouTube platform management with AI-powered content optimization,
    advanced analytics, monetization tracking, and intelligent recommendations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # YouTube API configuration
        self.api_key = config.get('youtube_api_key')
        self.client_id = config.get('youtube_client_id')
        self.client_secret = config.get('youtube_client_secret')
        self.redirect_uri = config.get('youtube_redirect_uri', 'http://localhost:8080/callback')
        
        # OAuth scopes
        self.scopes = [
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtubepartner',
            'https://www.googleapis.com/auth/yt-analytics.readonly'
        ]
        
        # YouTube services
        self.youtube_service = None
        self.analytics_service = None
        self.credentials = None
        
        # Data storage
        self.channels = {}
        self.videos = {}
        self.comments = {}
        self.analytics_data = defaultdict(list)
        self.optimizations = {}
        
        # AI and ML settings
        self.ai_optimization_enabled = config.get('ai_optimization_enabled', True)
        self.content_analysis_enabled = config.get('content_analysis_enabled', True)
        self.auto_moderation_enabled = config.get('auto_moderation_enabled', True)
        
        # Performance settings
        self.max_videos_per_request = config.get('max_videos_per_request', 50)
        self.analytics_refresh_interval = config.get('analytics_refresh_interval', 3600)  # 1 hour
        self.optimization_refresh_interval = config.get('optimization_refresh_interval', 86400)  # 24 hours
        
        # AI service endpoints
        self.content_analysis_endpoint = config.get('content_analysis_endpoint')
        self.optimization_engine_endpoint = config.get('optimization_engine_endpoint')
        self.trend_prediction_endpoint = config.get('trend_prediction_endpoint')
        
        # Rate limiting (YouTube API limits)
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get('requests_per_minute', 100),
            requests_per_hour=config.get('requests_per_hour', 10000),
            requests_per_day=config.get('requests_per_day', 1000000),
            burst_limit=config.get('burst_limit', 10)
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=config.get('cache_ttl', 300),  # 5 minutes
            max_cache_size=config.get('max_cache_size', 10000)
        )
        
        # Content encryption
        self.content_encryption = ContentEncryption()
        
        # Background tasks
        self.background_tasks = []
        self.monitoring_active = False
        
        logger.info("Advanced YouTube Platform initialized")

    async def authenticate(self, credentials_data: Dict[str, Any] = None) -> bool:
        """
        Authenticate with YouTube API
        
        Args:
            credentials_data: OAuth credentials or API key
            
        Returns:
            bool: Authentication success
        """
        try:
            if credentials_data:
                # Use provided credentials
                self.credentials = Credentials.from_authorized_user_info(credentials_data)
                
                # Refresh credentials if needed
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
            
            elif self.api_key:
                # Use API key for read-only access
                self.youtube_service = build('youtube', 'v3', developerKey=self.api_key)
            
            else:
                # Start OAuth flow
                flow = Flow.from_client_config({
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }, scopes=self.scopes)
                
                flow.redirect_uri = self.redirect_uri
                
                # Generate authorization URL
                auth_url, _ = flow.authorization_url(prompt='consent')
                logger.info(f"Please visit this URL to authorize the application: {auth_url}")
                
                return False  # Requires manual authorization
            
            # Build YouTube services
            if self.credentials:
                self.youtube_service = build('youtube', 'v3', credentials=self.credentials)
                self.analytics_service = build('youtubeAnalytics', 'v2', credentials=self.credentials)
            
            # Test authentication
            if await self._test_authentication():
                logger.info("YouTube authentication successful")
                return True
            else:
                logger.error("YouTube authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating with YouTube: {str(e)}")
            return False

    async def get_channel_info(self, channel_id: str = "mine") -> Optional[YouTubeChannel]:
        """
        Get YouTube channel information
        
        Args:
            channel_id: Channel ID or "mine" for authenticated user's channel
            
        Returns:
            YouTubeChannel: Channel information
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache first
            cache_key = f"youtube_channel:{channel_id}"
            cached_channel = await self.cache_manager.get(cache_key)
            if cached_channel:
                return YouTubeChannel(**cached_channel)
            
            # Fetch channel data
            request = self.youtube_service.channels().list(
                part="snippet,statistics,brandingSettings,contentDetails,status",
                id=channel_id if channel_id != "mine" else None,
                mine=channel_id == "mine"
            )
            
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            channel_data = response['items'][0]
            
            # Parse channel information
            snippet = channel_data.get('snippet', {})
            statistics = channel_data.get('statistics', {})
            branding = channel_data.get('brandingSettings', {})
            
            channel = YouTubeChannel(
                channel_id=channel_data['id'],
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                custom_url=snippet.get('customUrl'),
                profile_image_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
                subscriber_count=int(statistics.get('subscriberCount', 0)),
                video_count=int(statistics.get('videoCount', 0)),
                view_count=int(statistics.get('viewCount', 0)),
                verified=statistics.get('hiddenSubscriberCount', False) == False
            )
            
            # Get additional analytics data
            if self.analytics_service:
                analytics_data = await self._get_channel_analytics(channel.channel_id)
                if analytics_data:
                    await self._enrich_channel_with_analytics(channel, analytics_data)
            
            # AI-powered analysis
            if self.content_analysis_enabled:
                await self._analyze_channel_content(channel)
            
            # Store in cache and local storage
            await self.cache_manager.set(cache_key, channel.dict())
            self.channels[channel.channel_id] = channel
            
            return channel
            
        except HttpError as e:
            logger.error(f"YouTube API error getting channel info: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting channel info: {str(e)}")
            return None

    async def get_video_info(self, video_id: str) -> Optional[YouTubeVideo]:
        """
        Get YouTube video information
        
        Args:
            video_id: Video ID
            
        Returns:
            YouTubeVideo: Video information
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache first
            cache_key = f"youtube_video:{video_id}"
            cached_video = await self.cache_manager.get(cache_key)
            if cached_video:
                return YouTubeVideo(**cached_video)
            
            # Fetch video data
            request = self.youtube_service.videos().list(
                part="snippet,statistics,contentDetails,status,monetizationDetails",
                id=video_id
            )
            
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            video_data = response['items'][0]
            
            # Parse video information
            snippet = video_data.get('snippet', {})
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            status = video_data.get('status', {})
            
            video = YouTubeVideo(
                video_id=video_data['id'],
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                channel_id=snippet.get('channelId', ''),
                channel_title=snippet.get('channelTitle', ''),
                duration=content_details.get('duration'),
                category_id=snippet.get('categoryId', '22'),
                tags=snippet.get('tags', []),
                default_language=snippet.get('defaultLanguage', 'en'),
                privacy_status=YouTubePrivacyStatus(status.get('privacyStatus', 'public')),
                published_at=self._parse_datetime(snippet.get('publishedAt')),
                thumbnail_url=snippet.get('thumbnails', {}).get('maxres', {}).get('url'),
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                dislike_count=int(statistics.get('dislikeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0)),
                favorite_count=int(statistics.get('favoriteCount', 0))
            )
            
            # Calculate engagement metrics
            await self._calculate_video_engagement_metrics(video)
            
            # Get analytics data
            if self.analytics_service:
                analytics_data = await self._get_video_analytics(video_id)
                if analytics_data:
                    await self._enrich_video_with_analytics(video, analytics_data)
            
            # AI-powered content analysis
            if self.content_analysis_enabled:
                await self._analyze_video_content(video)
            
            # Store in cache and local storage
            await self.cache_manager.set(cache_key, video.dict())
            self.videos[video_id] = video
            
            return video
            
        except HttpError as e:
            logger.error(f"YouTube API error getting video info: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return None

    async def upload_video(
        self,
        video_file_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        category_id: str = "22",
        privacy_status: YouTubePrivacyStatus = YouTubePrivacyStatus.PUBLIC,
        scheduled_publish_time: datetime = None
    ) -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_file_path: Path to video file
            title: Video title
            description: Video description
            tags: Video tags
            category_id: Category ID
            privacy_status: Privacy status
            scheduled_publish_time: Scheduled publish time
            
        Returns:
            str: Video ID if successful
        """
        try:
            if not self.youtube_service or not self.credentials:
                raise ValueError("Authentication required for video upload")
            
            await self.rate_limiter.acquire()
            
            # Optimize title and description with AI
            if self.ai_optimization_enabled:
                optimized_metadata = await self._optimize_video_metadata(title, description, tags)
                if optimized_metadata:
                    title = optimized_metadata.get('title', title)
                    description = optimized_metadata.get('description', description)
                    tags = optimized_metadata.get('tags', tags or [])
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status.value,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            if scheduled_publish_time:
                body['status']['publishAt'] = scheduled_publish_time.isoformat()
            
            # Upload video
            from googleapiclient.http import MediaFileUpload
            
            media = MediaFileUpload(
                video_file_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            logger.info(f"Video uploaded successfully: {video_id}")
            
            # Get full video information
            video_info = await self.get_video_info(video_id)
            if video_info:
                # Generate optimization recommendations
                await self._generate_video_optimizations(video_info)
            
            return video_id
            
        except HttpError as e:
            logger.error(f"YouTube API error uploading video: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return None

    async def update_video(
        self,
        video_id: str,
        title: str = None,
        description: str = None,
        tags: List[str] = None,
        category_id: str = None,
        privacy_status: YouTubePrivacyStatus = None
    ) -> bool:
        """
        Update video metadata
        
        Args:
            video_id: Video ID
            title: New title
            description: New description
            tags: New tags
            category_id: New category ID
            privacy_status: New privacy status
            
        Returns:
            bool: Update success
        """
        try:
            if not self.youtube_service or not self.credentials:
                raise ValueError("Authentication required for video update")
            
            await self.rate_limiter.acquire()
            
            # Get current video data
            current_video = await self.get_video_info(video_id)
            if not current_video:
                return False
            
            # Prepare update body
            body = {
                'id': video_id,
                'snippet': {
                    'title': title or current_video.title,
                    'description': description or current_video.description,
                    'tags': tags or current_video.tags,
                    'categoryId': category_id or current_video.category_id,
                    'channelId': current_video.channel_id
                }
            }
            
            if privacy_status:
                body['status'] = {
                    'privacyStatus': privacy_status.value
                }
            
            # AI optimization
            if self.ai_optimization_enabled and (title or description or tags):
                optimized_metadata = await self._optimize_video_metadata(
                    body['snippet']['title'],
                    body['snippet']['description'],
                    body['snippet']['tags']
                )
                if optimized_metadata:
                    body['snippet'].update(optimized_metadata)
            
            # Update video
            request = self.youtube_service.videos().update(
                part='snippet' + (',status' if privacy_status else ''),
                body=body
            )
            
            response = request.execute()
            
            # Update local cache
            if video_id in self.videos:
                video = self.videos[video_id]
                video.title = body['snippet']['title']
                video.description = body['snippet']['description']
                video.tags = body['snippet']['tags']
                video.category_id = body['snippet']['categoryId']
                if privacy_status:
                    video.privacy_status = privacy_status
                video.updated_at = datetime.utcnow()
                
                # Update cache
                cache_key = f"youtube_video:{video_id}"
                await self.cache_manager.set(cache_key, video.dict())
            
            logger.info(f"Video updated successfully: {video_id}")
            return True
            
        except HttpError as e:
            logger.error(f"YouTube API error updating video: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating video: {str(e)}")
            return False

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100
    ) -> List[YouTubeComment]:
        """
        Get video comments
        
        Args:
            video_id: Video ID
            max_results: Maximum number of comments
            
        Returns:
            List[YouTubeComment]: Video comments
        """
        try:
            await self.rate_limiter.acquire()
            
            comments = []
            page_token = None
            
            while len(comments) < max_results:
                request = self.youtube_service.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=page_token,
                    order="relevance"
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    comment_data = item['snippet']['topLevelComment']['snippet']
                    
                    comment = YouTubeComment(
                        comment_id=item['snippet']['topLevelComment']['id'],
                        video_id=video_id,
                        text=comment_data['textDisplay'],
                        author_name=comment_data['authorDisplayName'],
                        author_channel_id=comment_data.get('authorChannelId', {}).get('value'),
                        like_count=comment_data.get('likeCount', 0),
                        reply_count=item['snippet'].get('totalReplyCount', 0),
                        published_at=self._parse_datetime(comment_data['publishedAt']),
                        updated_at=self._parse_datetime(comment_data.get('updatedAt'))
                    )
                    
                    # AI-powered sentiment analysis
                    if self.content_analysis_enabled:
                        await self._analyze_comment_sentiment(comment)
                    
                    comments.append(comment)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            # Store comments
            for comment in comments:
                self.comments[comment.comment_id] = comment
            
            return comments
            
        except HttpError as e:
            logger.error(f"YouTube API error getting comments: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting video comments: {str(e)}")
            return []

    async def get_channel_analytics(
        self,
        channel_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: List[str] = None
    ) -> Optional[YouTubeAnalytics]:
        """
        Get channel analytics data
        
        Args:
            channel_id: Channel ID
            start_date: Start date
            end_date: End date
            metrics: Specific metrics to retrieve
            
        Returns:
            YouTubeAnalytics: Analytics data
        """
        try:
            if not self.analytics_service:
                logger.warning("YouTube Analytics API not available")
                return None
            
            await self.rate_limiter.acquire()
            
            # Default metrics
            if not metrics:
                metrics = [
                    'views', 'estimatedMinutesWatched', 'averageViewDuration',
                    'subscribersGained', 'subscribersLost', 'likes', 'dislikes',
                    'comments', 'shares', 'estimatedRevenue'
                ]
            
            # Fetch analytics data
            request = self.analytics_service.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date.strftime('%Y-%m-%d'),
                endDate=end_date.strftime('%Y-%m-%d'),
                metrics=','.join(metrics),
                dimensions='day'
            )
            
            response = request.execute()
            
            # Parse analytics data
            analytics = YouTubeAnalytics(
                channel_id=channel_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if response.get('rows'):
                # Aggregate data
                for row in response['rows']:
                    # Map metrics to analytics object
                    for i, metric in enumerate(metrics):
                        value = row[i + 1] if len(row) > i + 1 else 0  # Skip date column
                        
                        if metric == 'views':
                            analytics.views += value
                        elif metric == 'estimatedMinutesWatched':
                            analytics.watch_time_minutes += value
                        elif metric == 'subscribersGained':
                            analytics.subscribers_gained += value
                        elif metric == 'subscribersLost':
                            analytics.subscribers_lost += value
                        elif metric == 'likes':
                            analytics.likes += value
                        elif metric == 'dislikes':
                            analytics.dislikes += value
                        elif metric == 'comments':
                            analytics.comments += value
                        elif metric == 'shares':
                            analytics.shares += value
                        elif metric == 'estimatedRevenue':
                            analytics.estimated_revenue += value
            
            # Calculate derived metrics
            if analytics.views > 0:
                analytics.average_view_duration = analytics.watch_time_minutes / analytics.views
                analytics.retention_rate = (analytics.average_view_duration / 10) * 100  # Simplified
            
            # Store analytics data
            self.analytics_data[channel_id].append(analytics)
            
            return analytics
            
        except HttpError as e:
            logger.error(f"YouTube Analytics API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting channel analytics: {str(e)}")
            return None

    async def generate_optimization_recommendations(
        self,
        channel_id: str = None,
        video_id: str = None
    ) -> Optional[YouTubeOptimization]:
        """
        Generate AI-powered optimization recommendations
        
        Args:
            channel_id: Channel ID for channel optimization
            video_id: Video ID for video optimization
            
        Returns:
            YouTubeOptimization: Optimization recommendations
        """
        try:
            if not (channel_id or video_id):
                raise ValueError("Either channel_id or video_id must be provided")
            
            # Get data for analysis
            if video_id:
                video = await self.get_video_info(video_id)
                if not video:
                    return None
                channel_id = video.channel_id
            
            channel = await self.get_channel_info(channel_id)
            if not channel:
                return None
            
            # Get recent analytics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            analytics = await self.get_channel_analytics(channel_id, start_date, end_date)
            
            # AI-powered optimization analysis
            optimization_data = {
                'channel': channel.dict(),
                'analytics': analytics.dict() if analytics else {},
                'video': video.dict() if video_id else None
            }
            
            optimization = await self._generate_ai_optimizations(optimization_data)
            
            if optimization:
                # Store optimization recommendations
                opt_key = video_id or channel_id
                self.optimizations[opt_key] = optimization
                
                logger.info(f"Generated optimization recommendations for {'video' if video_id else 'channel'}: {opt_key}")
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {str(e)}")
            return None

    async def start_monitoring(self):
        """Start background monitoring tasks"""
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            
            # Start background tasks
            analytics_task = asyncio.create_task(self._analytics_monitor_loop())
            optimization_task = asyncio.create_task(self._optimization_monitor_loop())
            trend_task = asyncio.create_task(self._trend_monitoring_loop())
            
            self.background_tasks = [analytics_task, optimization_task, trend_task]
            
            logger.info("YouTube monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting YouTube monitoring: {str(e)}")

    async def stop_monitoring(self):
        """Stop background monitoring tasks"""
        try:
            self.monitoring_active = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            self.background_tasks = []
            
            logger.info("YouTube monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping YouTube monitoring: {str(e)}")

    # AI and Analytics Helper Methods
    
    async def _analyze_video_content(self, video: YouTubeVideo):
        """Analyze video content with AI"""
        try:
            if not self.content_analysis_endpoint:
                return
            
            analysis_request = {
                'title': video.title,
                'description': video.description,
                'tags': video.tags,
                'duration': video.duration,
                'category': video.category_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.content_analysis_endpoint,
                    json=analysis_request,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        analysis_result = await response.json()
                        
                        video.content_quality_score = analysis_result.get('quality_score', 0.0)
                        video.virality_potential = analysis_result.get('virality_potential', 0.0)
                        video.optimization_score = analysis_result.get('optimization_score', 0.0)
            
        except Exception as e:
            logger.error(f"Error analyzing video content: {str(e)}")

    async def _analyze_channel_content(self, channel: YouTubeChannel):
        """Analyze channel content with AI"""
        try:
            if not self.content_analysis_endpoint:
                return
            
            # Get recent videos for analysis
            recent_videos = []
            for video in self.videos.values():
                if (video.channel_id == channel.channel_id and 
                    video.published_at and 
                    video.published_at >= datetime.utcnow() - timedelta(days=30)):
                    recent_videos.append(video.dict())
            
            analysis_request = {
                'channel_info': {
                    'title': channel.title,
                    'description': channel.description,
                    'subscriber_count': channel.subscriber_count,
                    'video_count': channel.video_count
                },
                'recent_videos': recent_videos[:10]  # Last 10 videos
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.content_analysis_endpoint}/channel",
                    json=analysis_request,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        analysis_result = await response.json()
                        
                        channel.content_quality_score = analysis_result.get('quality_score', 0.0)
                        channel.growth_potential = analysis_result.get('growth_potential', 0.0)
                        channel.content_optimization_score = analysis_result.get('optimization_score', 0.0)
                        channel.audience_loyalty_score = analysis_result.get('loyalty_score', 0.0)
                        
                        # Update content categories
                        if 'content_categories' in analysis_result:
                            channel.content_categories = analysis_result['content_categories']
                        
                        # Update keywords
                        if 'keywords' in analysis_result:
                            channel.keywords = analysis_result['keywords']
            
        except Exception as e:
            logger.error(f"Error analyzing channel content: {str(e)}")

    async def _analyze_comment_sentiment(self, comment: YouTubeComment):
        """Analyze comment sentiment"""
        try:
            if not self.content_analysis_endpoint:
                return
            
            analysis_request = {
                'text': comment.text,
                'context': 'youtube_comment'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.content_analysis_endpoint}/sentiment",
                    json=analysis_request,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        sentiment_result = await response.json()
                        
                        comment.sentiment_score = sentiment_result.get('sentiment_score', 0.0)
                        comment.sentiment_label = sentiment_result.get('sentiment_label', 'neutral')
                        comment.toxicity_score = sentiment_result.get('toxicity_score', 0.0)
                        comment.relevance_score = sentiment_result.get('relevance_score', 0.0)
            
        except Exception as e:
            logger.error(f"Error analyzing comment sentiment: {str(e)}")

    async def _optimize_video_metadata(
        self,
        title: str,
        description: str,
        tags: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Optimize video metadata with AI"""
        try:
            if not self.optimization_engine_endpoint:
                return None
            
            optimization_request = {
                'title': title,
                'description': description,
                'tags': tags,
                'optimization_type': 'metadata'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.optimization_engine_endpoint,
                    json=optimization_request,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        optimization_result = await response.json()
                        return optimization_result.get('optimized_metadata', {})
            
            return None
            
        except Exception as e:
            logger.error(f"Error optimizing video metadata: {str(e)}")
            return None

    async def _generate_ai_optimizations(
        self,
        optimization_data: Dict[str, Any]
    ) -> Optional[YouTubeOptimization]:
        """Generate AI-powered optimization recommendations"""
        try:
            if not self.optimization_engine_endpoint:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.optimization_engine_endpoint}/youtube",
                    json=optimization_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        optimization_result = await response.json()
                        
                        optimization = YouTubeOptimization(
                            channel_id=optimization_data['channel']['channel_id'],
                            video_id=optimization_data.get('video', {}).get('video_id'),
                            **optimization_result
                        )
                        
                        return optimization
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating AI optimizations: {str(e)}")
            return None

    # Background monitoring methods
    
    async def _analytics_monitor_loop(self):
        """Analytics monitoring loop"""
        while self.monitoring_active:
            try:
                # Update analytics for all tracked channels
                for channel_id in self.channels.keys():
                    end_date = datetime.utcnow()
                    start_date = end_date - timedelta(days=1)
                    
                    analytics = await self.get_channel_analytics(channel_id, start_date, end_date)
                    if analytics:
                        logger.debug(f"Updated analytics for channel: {channel_id}")
                
                await asyncio.sleep(self.analytics_refresh_interval)
                
            except Exception as e:
                logger.error(f"Error in analytics monitor loop: {str(e)}")
                await asyncio.sleep(self.analytics_refresh_interval)

    async def _optimization_monitor_loop(self):
        """Optimization monitoring loop"""
        while self.monitoring_active:
            try:
                # Generate optimization recommendations for all channels
                for channel_id in self.channels.keys():
                    optimization = await self.generate_optimization_recommendations(channel_id=channel_id)
                    if optimization:
                        logger.debug(f"Generated optimizations for channel: {channel_id}")
                
                await asyncio.sleep(self.optimization_refresh_interval)
                
            except Exception as e:
                logger.error(f"Error in optimization monitor loop: {str(e)}")
                await asyncio.sleep(self.optimization_refresh_interval)

    async def _trend_monitoring_loop(self):
        """Trend monitoring loop"""
        while self.monitoring_active:
            try:
                # Monitor trending topics and update recommendations
                if self.trend_prediction_endpoint:
                    await self._update_trending_topics()
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Error in trend monitoring loop: {str(e)}")
                await asyncio.sleep(3600)

    # Utility methods
    
    async def _test_authentication(self) -> bool:
        """Test YouTube API authentication"""
        try:
            if self.youtube_service:
                # Test with a simple API call
                request = self.youtube_service.channels().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                return 'items' in response
            return False
        except Exception:
            return False

    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse YouTube datetime string"""
        try:
            if not datetime_str:
                return None
            # YouTube uses ISO 8601 format
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except Exception:
            return None

    async def _calculate_video_engagement_metrics(self, video: YouTubeVideo):
        """Calculate engagement metrics for video"""
        try:
            if video.view_count > 0:
                total_engagements = (video.like_count + video.dislike_count + 
                                   video.comment_count + video.favorite_count)
                video.engagement_rate = (total_engagements / video.view_count) * 100
            
            # Calculate additional metrics based on duration
            if video.duration:
                duration_seconds = self._parse_duration(video.duration)
                if duration_seconds > 0:
                    video.average_view_duration = duration_seconds / 2  # Simplified estimation
                    video.retention_rate = (video.average_view_duration / duration_seconds) * 100
            
        except Exception as e:
            logger.error(f"Error calculating engagement metrics: {str(e)}")

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        try:
            return int(isodate.parse_duration(duration_str).total_seconds())
        except Exception:
            return 0

    async def close(self):
        """Close YouTube platform and cleanup resources"""
        try:
            await self.stop_monitoring()
            await self.cache_manager.close()
            await super().close()
            logger.info("Advanced YouTube Platform closed successfully")
        except Exception as e:
            logger.error(f"Error closing YouTube platform: {str(e)}")
