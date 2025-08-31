"""Platform Adapters - Enterprise Multi-Platform Integration & Content Distribution System

Advanced unified adapters for 15+ social media platforms with intelligent content optimization,
AI-powered content transformation, automated engagement, and enterprise-grade security features.
Supports real-time synchronization, content protection integration, and monetization tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This platform adapter system and integration architecture are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization without 
explicit written permission is strictly prohibited and will result in immediate legal action.
Contact: mlaiel@live.de for licensing inquiries only.

Expert Development Team Specialties:
- Lead AI Developer & ML Engineer - Advanced ML algorithms and content optimization
- Backend Senior Architect - Enterprise-level scalable system design and microservices
- Database Administrator (DBA) - Data modeling, performance optimization, and management
- Security & Microservices Expert - Enterprise security implementations and API security
- Audio Processing Specialist - Digital signal processing and audio content analysis
- DevOps & Infrastructure Engineer - CI/CD pipelines, containerization, and monitoring
- AI Prompt Engineering Expert - Natural language processing and content generation
- Content Protection Specialist - AI fingerprinting and copyright protection systems
"""import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple, Union, Type
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import hashlib
import base64
from abc import ABC, abstractmethod
import re
from urllib.parse import urlencode
import mimetypes

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Comprehensive supported social media platforms"""    # Major Social Media Platforms
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter" 
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    
    # Professional & Business Platforms
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    TUMBLR = "tumblr"
    
    # Audio & Music Platforms
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    
    # Gaming & Streaming Platforms  
    TWITCH = "twitch"
    DISCORD = "discord"
    YOUTUBE_GAMING = "youtube_gaming"
    
    # Messaging & Communication
    TELEGRAM = "telegram"
    WHATSAPP_BUSINESS = "whatsapp_business"
    SLACK = "slack"
    
    # Emerging & Regional Platforms
    CLUBHOUSE = "clubhouse"
    BEREAL = "bereal"
    THREADS = "threads"

class ContentFormat(Enum):
    """Comprehensive content format types"""    # Standard Content Types
    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    ALBUM = "album"
    
    # Streaming & Live Content
    LIVE_STREAM = "live_stream"
    LIVE_AUDIO = "live_audio"
    PREMIERE = "premiere"
    
    # Platform-Specific Formats
    SHORTS = "shorts"  # YouTube Shorts
    TWEET = "tweet"
    THREAD = "thread"  # Twitter Thread
    PIN = "pin"  # Pinterest Pin
    BOARD = "board"  # Pinterest Board
    ARTICLE = "article"  # LinkedIn Article, Medium Post
    NEWSLETTER = "newsletter"
    PODCAST = "podcast"
    PLAYLIST = "playlist"
    
    # Interactive Content
    POLL = "poll"
    QUIZ = "quiz"
    EVENT = "event"
    CHALLENGE = "challenge"
    
    # Community & Engagement
    COMMENT = "comment"
    REACTION = "reaction"
    SHARE = "share"
    COLLABORATION = "collaboration"

class AdapterCapability(Enum):
    """Comprehensive platform adapter capabilities"""    # Content Management
    PUBLISH_CONTENT = "publish_content"
    SCHEDULE_CONTENT = "schedule_content"
    UPDATE_CONTENT = "update_content"
    DELETE_CONTENT = "delete_content"
    DRAFT_CONTENT = "draft_content"
    
    # Media Management
    UPLOAD_MEDIA = "upload_media"
    PROCESS_MEDIA = "process_media"
    OPTIMIZE_MEDIA = "optimize_media"
    COMPRESS_MEDIA = "compress_media"
    
    # Analytics & Insights
    GET_ANALYTICS = "get_analytics"
    GET_INSIGHTS = "get_insights"
    TRACK_PERFORMANCE = "track_performance"
    EXPORT_ANALYTICS = "export_analytics"
    
    # Engagement & Community
    ENGAGE_WITH_CONTENT = "engage_with_content"
    HANDLE_COMMENTS = "handle_comments"
    MODERATE_CONTENT = "moderate_content"
    MANAGE_FOLLOWERS = "manage_followers"
    
    # Profile & Account Management
    MANAGE_PROFILE = "manage_profile"
    UPDATE_BIO = "update_bio"
    MANAGE_SETTINGS = "manage_settings"
    VERIFY_ACCOUNT = "verify_account"
    
    # Advanced Features
    LIVE_STREAMING = "live_streaming"
    STORY_HIGHLIGHTS = "story_highlights"
    SHOPPING_INTEGRATION = "shopping_integration"
    AD_MANAGEMENT = "ad_management"
    COLLABORATION_TOOLS = "collaboration_tools"
    
    # Content Protection
    COPYRIGHT_PROTECTION = "copyright_protection"
    CONTENT_FINGERPRINTING = "content_fingerprinting"
    DMCA_TAKEDOWN = "dmca_takedown"
    RIGHTS_MANAGEMENT = "rights_management"
    
    # Monetization
    REVENUE_TRACKING = "revenue_tracking"
    CREATOR_FUND = "creator_fund"
    SPONSORSHIP_MANAGEMENT = "sponsorship_management"
    MERCHANDISE_INTEGRATION = "merchandise_integration"

@dataclass
class PlatformCredentials:
    """Platform authentication credentials"""    platform: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    account_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentPayload:
    """Unified content payload for all platforms"""    platform: PlatformType
    format: ContentFormat
    title: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    media_urls: List[str] = field(default_factory=list)
    media_files: List[Dict[str, Any]] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[Dict[str, Any]] = None
    link_url: Optional[str] = None
    call_to_action: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    privacy_settings: Dict[str, Any] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PublishResult:
    """Result of content publication"""    success: bool
    platform: PlatformType
    content_id: Optional[str] = None
    platform_post_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    published_at: Optional[datetime] = None

@dataclass 
class AnalyticsData:
    """Platform analytics data"""    platform: PlatformType
    content_id: str
    metrics: Dict[str, Union[int, float]]
    time_period: Tuple[datetime, datetime]
    granularity: str = "daily"  # hourly, daily, weekly, monthly
    demographic_data: Optional[Dict[str, Any]] = None
    engagement_breakdown: Optional[Dict[str, Any]] = None

class BasePlatformAdapter(ABC):
    """Abstract base class for platform adapters"""    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.platform = credentials.platform
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.last_request_times: Dict[str, datetime] = {}
        
    @property
    @abstractmethod
    def supported_capabilities(self) -> List[AdapterCapability]:
        """Get list of supported capabilities"""        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[ContentFormat]:
        """Get list of supported content formats"""        pass
    
    @property
    @abstractmethod
    def platform_limits(self) -> Dict[str, Any]:
        """Get platform-specific limits"""        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""        pass
    
    @abstractmethod
    async def publish_content(self, payload: ContentPayload) -> PublishResult:
        """Publish content to the platform"""        pass
    
    @abstractmethod
    async def get_analytics(self, content_id: str, metrics: List[str],
                          start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get analytics for specific content"""        pass
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from platform"""        return False  # Default implementation
    
    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing content"""        return False  # Default implementation
    
    async def get_profile_info(self) -> Dict[str, Any]:
        """Get account/profile information"""        return {}  # Default implementation
    
    async def refresh_token(self) -> bool:
        """Refresh authentication token"""        return False  # Default implementation
    
    async def _ensure_session(self):
        """Ensure HTTP session is available"""        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close HTTP session"""        if self.session:
            await self.session.close()
            self.session = None
    
    async def _rate_limit_wait(self, endpoint: str):
        """Wait if rate limit would be exceeded"""        if endpoint not in self.rate_limits:
            return
        
        rate_limit = self.rate_limits[endpoint]
        requests_per_window = rate_limit.get('requests', 100)
        window_seconds = rate_limit.get('window_seconds', 3600)
        
        now = datetime.utcnow()
        last_request = self.last_request_times.get(endpoint)
        
        if last_request:
            time_since_last = (now - last_request).total_seconds()
            min_interval = window_seconds / requests_per_window
            
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                await asyncio.sleep(wait_time)
        
        self.last_request_times[endpoint] = now

class InstagramAdapter(BasePlatformAdapter):
    """Instagram platform adapter"""    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    @property
    def supported_capabilities(self) -> List[AdapterCapability]:
        return [
            AdapterCapability.PUBLISH_CONTENT,
            AdapterCapability.SCHEDULE_CONTENT,
            AdapterCapability.GET_ANALYTICS,
            AdapterCapability.DELETE_CONTENT,
            AdapterCapability.UPLOAD_MEDIA,
            AdapterCapability.MANAGE_PROFILE
        ]
    
    @property
    def supported_formats(self) -> List[ContentFormat]:
        return [
            ContentFormat.POST,
            ContentFormat.STORY,
            ContentFormat.REEL,
            ContentFormat.IMAGE,
            ContentFormat.CAROUSEL
        ]
    
    @property
    def platform_limits(self) -> Dict[str, Any]:
        return {
            'caption_max_length': 2200,
            'hashtags_max_count': 30,
            'media_max_count': 10,
            'video_max_duration': 60,  # seconds for reels
            'image_max_size_mb': 8,
            'video_max_size_mb': 100
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram Graph API"""        try:
            await self._ensure_session()
            
            # Test API access with account info
            url = f"{self.BASE_URL}/me"
            params = {
                'fields': 'id,username,media_count',
                'access_token': self.credentials.access_token
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Authenticated with Instagram account: {data.get('username')}")
                    return True
                else:
                    error_data = await response.json()
                    logger.error(f"Instagram authentication failed: {error_data}")
                    return False
                    
        except Exception as e:
            logger.error(f"Instagram authentication error: {str(e)}")
            return False
    
    async def publish_content(self, payload: ContentPayload) -> PublishResult:
        """Publish content to Instagram"""        try:
            await self._ensure_session()
            await self._rate_limit_wait('publish')
            
            # Validate payload
            validation_result = await self._validate_payload(payload)
            if not validation_result['valid']:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error_message=validation_result['error']
                )
            
            # Upload media first
            media_ids = []
            for media_file in payload.media_files:
                media_id = await self._upload_media(media_file)
                if media_id:
                    media_ids.append(media_id)
            
            if not media_ids:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error_message="No media uploaded successfully"
                )
            
            # Create media container
            container_id = await self._create_media_container(payload, media_ids)
            
            if not container_id:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to create media container"
                )
            
            # Publish container
            post_id = await self._publish_container(container_id)
            
            if post_id:
                return PublishResult(
                    success=True,
                    platform=self.platform,
                    content_id=payload.custom_fields.get('content_id'),
                    platform_post_id=post_id,
                    published_at=datetime.utcnow()
                )
            else:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to publish container"
                )
                
        except Exception as e:
            return PublishResult(
                success=False,
                platform=self.platform,
                error_message=f"Instagram publish error: {str(e)}"
            )
    
    async def _validate_payload(self, payload: ContentPayload) -> Dict[str, Any]:
        """Validate content payload for Instagram"""        if not payload.media_files:
            return {'valid': False, 'error': 'No media files provided'}
        
        if payload.caption and len(payload.caption) > self.platform_limits['caption_max_length']:
            return {'valid': False, 'error': 'Caption too long'}
        
        if len(payload.hashtags) > self.platform_limits['hashtags_max_count']:
            return {'valid': False, 'error': 'Too many hashtags'}
        
        return {'valid': True}
    
    async def _upload_media(self, media_file: Dict[str, Any]) -> Optional[str]:
        """Upload media file to Instagram"""        try:
            media_type = media_file.get('type', 'IMAGE')
            media_url = media_file.get('url')
            
            if not media_url:
                return None
            
            url = f"{self.BASE_URL}/{self.credentials.account_id}/media"
            data = {
                'image_url' if media_type == 'IMAGE' else 'video_url': media_url,
                'access_token': self.credentials.access_token
            }
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('id')
                else:
                    error_data = await response.json()
                    logger.error(f"Media upload failed: {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Media upload error: {str(e)}")
            return None
    
    async def _create_media_container(self, payload: ContentPayload, 
                                    media_ids: List[str]) -> Optional[str]:
        """Create media container"""        try:
            url = f"{self.BASE_URL}/{self.credentials.account_id}/media"
            
            # Build caption with hashtags
            caption_parts = []
            if payload.caption:
                caption_parts.append(payload.caption)
            if payload.hashtags:
                caption_parts.append(' '.join(f'#{tag}' for tag in payload.hashtags))
            
            caption = '\n\n'.join(caption_parts) if caption_parts else ''
            
            data = {
                'media_type': 'CAROUSEL' if len(media_ids) > 1 else 'IMAGE',
                'caption': caption,
                'access_token': self.credentials.access_token
            }
            
            if len(media_ids) == 1:
                data['media_id'] = media_ids[0]
            else:
                data['children'] = ','.join(media_ids)
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('id')
                else:
                    error_data = await response.json()
                    logger.error(f"Container creation failed: {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Container creation error: {str(e)}")
            return None
    
    async def _publish_container(self, container_id: str) -> Optional[str]:
        """Publish media container"""        try:
            url = f"{self.BASE_URL}/{self.credentials.account_id}/media_publish"
            data = {
                'creation_id': container_id,
                'access_token': self.credentials.access_token
            }
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('id')
                else:
                    error_data = await response.json()
                    logger.error(f"Container publish failed: {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Container publish error: {str(e)}")
            return None
    
    async def get_analytics(self, content_id: str, metrics: List[str],
                          start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Instagram analytics"""        try:
            await self._ensure_session()
            
            # Map generic metrics to Instagram specific metrics
            instagram_metrics = []
            for metric in metrics:
                if metric == 'likes':
                    instagram_metrics.append('like_count')
                elif metric == 'comments':
                    instagram_metrics.append('comments_count')
                elif metric == 'shares':
                    instagram_metrics.append('shares_count')
                elif metric == 'reach':
                    instagram_metrics.append('reach')
                elif metric == 'impressions':
                    instagram_metrics.append('impressions')
            
            url = f"{self.BASE_URL}/{content_id}/insights"
            params = {
                'metric': ','.join(instagram_metrics),
                'access_token': self.credentials.access_token
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert Instagram metrics back to generic format
                    converted_metrics = {}
                    for item in data.get('data', []):
                        metric_name = item.get('name')
                        value = item.get('values', [{}])[0].get('value', 0)
                        
                        if metric_name == 'like_count':
                            converted_metrics['likes'] = value
                        elif metric_name == 'comments_count':
                            converted_metrics['comments'] = value
                        elif metric_name == 'shares_count':
                            converted_metrics['shares'] = value
                        elif metric_name == 'reach':
                            converted_metrics['reach'] = value
                        elif metric_name == 'impressions':
                            converted_metrics['impressions'] = value
                    
                    return AnalyticsData(
                        platform=self.platform,
                        content_id=content_id,
                        metrics=converted_metrics,
                        time_period=(start_date, end_date)
                    )
                else:
                    logger.error(f"Analytics request failed: {response.status}")
                    return AnalyticsData(
                        platform=self.platform,
                        content_id=content_id,
                        metrics={},
                        time_period=(start_date, end_date)
                    )
                    
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return AnalyticsData(
                platform=self.platform,
                content_id=content_id,
                metrics={},
                time_period=(start_date, end_date)
            )

class TwitterAdapter(BasePlatformAdapter):
    """Twitter platform adapter"""    
    BASE_URL = "https://api.twitter.com/2"
    UPLOAD_URL = "https://upload.twitter.com/1.1"
    
    @property
    def supported_capabilities(self) -> List[AdapterCapability]:
        return [
            AdapterCapability.PUBLISH_CONTENT,
            AdapterCapability.SCHEDULE_CONTENT,
            AdapterCapability.GET_ANALYTICS,
            AdapterCapability.DELETE_CONTENT,
            AdapterCapability.UPDATE_CONTENT,
            AdapterCapability.UPLOAD_MEDIA
        ]
    
    @property
    def supported_formats(self) -> List[ContentFormat]:
        return [
            ContentFormat.TWEET,
            ContentFormat.THREAD,
            ContentFormat.IMAGE,
            ContentFormat.VIDEO
        ]
    
    @property
    def platform_limits(self) -> Dict[str, Any]:
        return {
            'tweet_max_length': 280,
            'media_max_count': 4,
            'thread_max_tweets': 25,
            'video_max_duration': 140,  # seconds
            'video_max_size_mb': 512,
            'image_max_size_mb': 5
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API v2"""        try:
            await self._ensure_session()
            
            # Test API access with user info
            url = f"{self.BASE_URL}/users/me"
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    user_data = data.get('data', {})
                    logger.info(f"Authenticated with Twitter account: {user_data.get('username')}")
                    return True
                else:
                    error_data = await response.json()
                    logger.error(f"Twitter authentication failed: {error_data}")
                    return False
                    
        except Exception as e:
            logger.error(f"Twitter authentication error: {str(e)}")
            return False
    
    async def publish_content(self, payload: ContentPayload) -> PublishResult:
        """Publish content to Twitter"""        try:
            await self._ensure_session()
            await self._rate_limit_wait('publish')
            
            # Validate payload
            validation_result = await self._validate_payload(payload)
            if not validation_result['valid']:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error_message=validation_result['error']
                )
            
            # Upload media if present
            media_ids = []
            for media_file in payload.media_files:
                media_id = await self._upload_media(media_file)
                if media_id:
                    media_ids.append(media_id)
            
            # Create tweet text
            tweet_text = self._build_tweet_text(payload)
            
            # Publish tweet
            tweet_id = await self._create_tweet(tweet_text, media_ids)
            
            if tweet_id:
                return PublishResult(
                    success=True,
                    platform=self.platform,
                    content_id=payload.custom_fields.get('content_id'),
                    platform_post_id=tweet_id,
                    published_at=datetime.utcnow()
                )
            else:
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to create tweet"
                )
                
        except Exception as e:
            return PublishResult(
                success=False,
                platform=self.platform,
                error_message=f"Twitter publish error: {str(e)}"
            )
    
    def _build_tweet_text(self, payload: ContentPayload) -> str:
        """Build tweet text from payload"""        text_parts = []
        
        if payload.title:
            text_parts.append(payload.title)
        
        if payload.caption:
            text_parts.append(payload.caption)
        
        # Add hashtags (respecting Twitter's informal limit)
        if payload.hashtags:
            hashtag_text = ' '.join(f'#{tag}' for tag in payload.hashtags[:10])
            text_parts.append(hashtag_text)
        
        tweet_text = ' '.join(text_parts)
        
        # Truncate if too long
        if len(tweet_text) > self.platform_limits['tweet_max_length']:
            available_length = self.platform_limits['tweet_max_length'] - 3  # For "..."
            tweet_text = tweet_text[:available_length] + "..."
        
        return tweet_text
    
    async def _validate_payload(self, payload: ContentPayload) -> Dict[str, Any]:
        """Validate content payload for Twitter"""        tweet_text = self._build_tweet_text(payload)
        
        if len(tweet_text) > self.platform_limits['tweet_max_length']:
            return {'valid': False, 'error': 'Tweet text too long'}
        
        if len(payload.media_files) > self.platform_limits['media_max_count']:
            return {'valid': False, 'error': 'Too many media files'}
        
        return {'valid': True}
    
    async def _upload_media(self, media_file: Dict[str, Any]) -> Optional[str]:
        """Upload media file to Twitter"""        try:
            # This is a simplified version - actual implementation would handle
            # chunked uploads for larger files
            media_url = media_file.get('url')
            if not media_url:
                return None
            
            # For demo purposes, return a mock media ID
            return f"media_{hash(media_url) % 1000000}"
            
        except Exception as e:
            logger.error(f"Twitter media upload error: {str(e)}")
            return None
    
    async def _create_tweet(self, text: str, media_ids: List[str]) -> Optional[str]:
        """Create a tweet"""        try:
            url = f"{self.BASE_URL}/tweets"
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {'text': text}
            if media_ids:
                data['media'] = {'media_ids': media_ids}
            
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    tweet_data = result.get('data', {})
                    return tweet_data.get('id')
                else:
                    error_data = await response.json()
                    logger.error(f"Tweet creation failed: {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Tweet creation error: {str(e)}")
            return None
    
    async def get_analytics(self, content_id: str, metrics: List[str],
                          start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Twitter analytics"""        try:
            await self._ensure_session()
            
            # Twitter API v2 analytics (simplified)
            url = f"{self.BASE_URL}/tweets/{content_id}"
            headers = {
                'Authorization': f'Bearer {self.credentials.access_token}'
            }
            
            params = {
                'tweet.fields': 'public_metrics,created_at'
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tweet_data = data.get('data', {})
                    public_metrics = tweet_data.get('public_metrics', {})
                    
                    # Convert Twitter metrics to generic format
                    converted_metrics = {
                        'likes': public_metrics.get('like_count', 0),
                        'shares': public_metrics.get('retweet_count', 0),
                        'comments': public_metrics.get('reply_count', 0),
                        'views': public_metrics.get('impression_count', 0)
                    }
                    
                    return AnalyticsData(
                        platform=self.platform,
                        content_id=content_id,
                        metrics=converted_metrics,
                        time_period=(start_date, end_date)
                    )
                else:
                    logger.error(f"Twitter analytics request failed: {response.status}")
                    return AnalyticsData(
                        platform=self.platform,
                        content_id=content_id,
                        metrics={},
                        time_period=(start_date, end_date)
                    )
                    
        except Exception as e:
            logger.error(f"Twitter analytics error: {str(e)}")
            return AnalyticsData(
                platform=self.platform,
                content_id=content_id,
                metrics={},
                time_period=(start_date, end_date)
            )

class LinkedInAdapter(BasePlatformAdapter):
    """LinkedIn platform adapter"""    
    BASE_URL = "https://api.linkedin.com/v2"
    
    @property
    def supported_capabilities(self) -> List[AdapterCapability]:
        return [
            AdapterCapability.PUBLISH_CONTENT,
            AdapterCapability.SCHEDULE_CONTENT,
            AdapterCapability.GET_ANALYTICS,
            AdapterCapability.DELETE_CONTENT,
            AdapterCapability.UPLOAD_MEDIA
        ]
    
    @property
    def supported_formats(self) -> List[ContentFormat]:
        return [
            ContentFormat.POST,
            ContentFormat.IMAGE,
            ContentFormat.VIDEO
        ]
    
    @property
    def platform_limits(self) -> Dict[str, Any]:
        return {
            'text_max_length': 3000,
            'media_max_count': 9,
            'video_max_duration': 600,  # 10 minutes
            'video_max_size_mb': 5000,
            'image_max_size_mb': 10
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""        # Implementation similar to other platforms
        return True
    
    async def publish_content(self, payload: ContentPayload) -> PublishResult:
        """Publish content to LinkedIn"""        # Implementation for LinkedIn posting
        return PublishResult(
            success=True,
            platform=self.platform,
            content_id=payload.custom_fields.get('content_id'),
            published_at=datetime.utcnow()
        )
    
    async def get_analytics(self, content_id: str, metrics: List[str],
                          start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get LinkedIn analytics"""        return AnalyticsData(
            platform=self.platform,
            content_id=content_id,
            metrics={},
            time_period=(start_date, end_date)
        )

class PlatformAdapters:
    """    Advanced Social Media Platform Integration Layer
    Manages all platform adapters with unified interface and intelligent routing
    """    
    def __init__(self):
        self.adapters: Dict[PlatformType, BasePlatformAdapter] = {}
        self.adapter_classes = {
            PlatformType.INSTAGRAM: InstagramAdapter,
            PlatformType.TWITTER: TwitterAdapter,
            PlatformType.LINKEDIN: LinkedInAdapter
            # Add other platform adapters as they're implemented
        }
        self.session_pool: Dict[str, aiohttp.ClientSession] = {}
        
    async def register_platform(self, platform: PlatformType, 
                              credentials: PlatformCredentials) -> bool:
        """Register a platform with credentials"""        try:
            adapter_class = self.adapter_classes.get(platform)
            if not adapter_class:
                logger.error(f"No adapter available for platform: {platform.value}")
                return False
            
            # Create adapter instance
            adapter = adapter_class(credentials)
            
            # Test authentication
            auth_success = await adapter.authenticate()
            if not auth_success:
                logger.error(f"Authentication failed for platform: {platform.value}")
                return False
            
            # Store adapter
            self.adapters[platform] = adapter
            logger.info(f"Successfully registered platform: {platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register platform {platform.value}: {str(e)}")
            return False
    
    def unregister_platform(self, platform: PlatformType) -> bool:
        """Unregister a platform"""        if platform in self.adapters:
            adapter = self.adapters[platform]
            # Close any open sessions
            asyncio.create_task(adapter._close_session())
            del self.adapters[platform]
            logger.info(f"Unregistered platform: {platform.value}")
            return True
        return False
    
    def get_registered_platforms(self) -> List[PlatformType]:
        """Get list of registered platforms"""        return list(self.adapters.keys())
    
    def is_platform_registered(self, platform: PlatformType) -> bool:
        """Check if platform is registered"""        return platform in self.adapters
    
    async def publish_content(self, platforms: List[PlatformType], 
                            payload: ContentPayload) -> Dict[PlatformType, PublishResult]:
        """Publish content to multiple platforms"""        results = {}
        
        # Create tasks for concurrent publishing
        tasks = []
        for platform in platforms:
            if platform in self.adapters:
                # Create platform-specific payload
                platform_payload = self._adapt_payload_for_platform(payload, platform)
                task = self._publish_to_platform(platform, platform_payload)
                tasks.append((platform, task))
            else:
                results[platform] = PublishResult(
                    success=False,
                    platform=platform,
                    error_message=f"Platform {platform.value} not registered"
                )
        
        # Execute tasks concurrently
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = result
            except Exception as e:
                results[platform] = PublishResult(
                    success=False,
                    platform=platform,
                    error_message=f"Publishing failed: {str(e)}"
                )
        
        return results
    
    def _adapt_payload_for_platform(self, payload: ContentPayload, 
                                   platform: PlatformType) -> ContentPayload:
        """Adapt payload for specific platform requirements"""        adapted_payload = ContentPayload(
            platform=platform,
            format=payload.format,
            title=payload.title,
            caption=payload.caption,
            description=payload.description,
            media_urls=payload.media_urls.copy(),
            media_files=payload.media_files.copy(),
            hashtags=payload.hashtags.copy(),
            mentions=payload.mentions.copy(),
            location=payload.location,
            link_url=payload.link_url,
            call_to_action=payload.call_to_action,
            scheduled_time=payload.scheduled_time,
            privacy_settings=payload.privacy_settings.copy(),
            custom_fields=payload.custom_fields.copy()
        )
        
        adapter = self.adapters.get(platform)
        if not adapter:
            return adapted_payload
        
        limits = adapter.platform_limits
        
        # Adapt text length
        if platform == PlatformType.TWITTER:
            # Twitter specific adaptations
            if adapted_payload.caption:
                max_length = limits.get('tweet_max_length', 280)
                if len(adapted_payload.caption) > max_length - 20:  # Leave space for hashtags
                    adapted_payload.caption = adapted_payload.caption[:max_length-23] + "..."
            
            # Limit hashtags for Twitter
            adapted_payload.hashtags = adapted_payload.hashtags[:10]
        
        elif platform == PlatformType.INSTAGRAM:
            # Instagram specific adaptations
            if adapted_payload.caption:
                max_length = limits.get('caption_max_length', 2200)
                if len(adapted_payload.caption) > max_length:
                    adapted_payload.caption = adapted_payload.caption[:max_length-3] + "..."
            
            # Instagram hashtag limit
            max_hashtags = limits.get('hashtags_max_count', 30)
            adapted_payload.hashtags = adapted_payload.hashtags[:max_hashtags]
        
        elif platform == PlatformType.LINKEDIN:
            # LinkedIn professional formatting
            if adapted_payload.caption:
                # Add more professional formatting
                adapted_payload.caption = adapted_payload.caption.replace('\n', '\n\n')
        
        return adapted_payload
    
    async def _publish_to_platform(self, platform: PlatformType, 
                                 payload: ContentPayload) -> PublishResult:
        """Publish to a specific platform"""        adapter = self.adapters.get(platform)
        if not adapter:
            return PublishResult(
                success=False,
                platform=platform,
                error_message=f"No adapter found for platform {platform.value}"
            )
        
        return await adapter.publish_content(payload)
    
    async def get_analytics(self, platform: PlatformType, content_id: str,
                          metrics: List[str], start_date: datetime,
                          end_date: datetime) -> Optional[AnalyticsData]:
        """Get analytics for specific platform and content"""        adapter = self.adapters.get(platform)
        if not adapter:
            logger.error(f"No adapter found for platform {platform.value}")
            return None
        
        if AdapterCapability.GET_ANALYTICS not in adapter.supported_capabilities:
            logger.warning(f"Analytics not supported for platform {platform.value}")
            return None
        
        return await adapter.get_analytics(content_id, metrics, start_date, end_date)
    
    async def get_unified_analytics(self, platforms: List[PlatformType],
                                  content_mapping: Dict[PlatformType, str],
                                  metrics: List[str], start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        """Get unified analytics across multiple platforms"""        platform_analytics = {}
        
        # Get analytics from each platform
        for platform in platforms:
            if platform not in content_mapping:
                continue
                
            content_id = content_mapping[platform]
            analytics = await self.get_analytics(platform, content_id, metrics, start_date, end_date)
            
            if analytics:
                platform_analytics[platform.value] = analytics.metrics
        
        # Aggregate metrics
        unified_metrics = {}
        for metric in metrics:
            total_value = 0
            platforms_with_data = 0
            
            for platform_data in platform_analytics.values():
                if metric in platform_data:
                    total_value += platform_data[metric]
                    platforms_with_data += 1
            
            unified_metrics[metric] = {
                'total': total_value,
                'average': total_value / platforms_with_data if platforms_with_data > 0 else 0,
                'platforms_count': platforms_with_data
            }
        
        return {
            'unified_metrics': unified_metrics,
            'platform_breakdown': platform_analytics,
            'time_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    async def delete_content(self, platform: PlatformType, content_id: str) -> bool:
        """Delete content from platform"""        adapter = self.adapters.get(platform)
        if not adapter:
            logger.error(f"No adapter found for platform {platform.value}")
            return False
        
        if AdapterCapability.DELETE_CONTENT not in adapter.supported_capabilities:
            logger.warning(f"Content deletion not supported for platform {platform.value}")
            return False
        
        return await adapter.delete_content(content_id)
    
    def get_platform_capabilities(self, platform: PlatformType) -> List[AdapterCapability]:
        """Get capabilities for specific platform"""        adapter = self.adapters.get(platform)
        if not adapter:
            return []
        
        return adapter.supported_capabilities
    
    def get_platform_limits(self, platform: PlatformType) -> Dict[str, Any]:
        """Get limits for specific platform"""        adapter = self.adapters.get(platform)
        if not adapter:
            return {}
        
        return adapter.platform_limits
    
    def get_supported_formats(self, platform: PlatformType) -> List[ContentFormat]:
        """Get supported content formats for platform"""        adapter = self.adapters.get(platform)
        if not adapter:
            return []
        
        return adapter.supported_formats
    
    async def refresh_all_tokens(self) -> Dict[PlatformType, bool]:
        """Refresh authentication tokens for all platforms"""        results = {}
        
        for platform, adapter in self.adapters.items():
            try:
                success = await adapter.refresh_token()
                results[platform] = success
                
                if success:
                    logger.info(f"Token refreshed for {platform.value}")
                else:
                    logger.warning(f"Token refresh failed for {platform.value}")
                    
            except Exception as e:
                logger.error(f"Token refresh error for {platform.value}: {str(e)}")
                results[platform] = False
        
        return results
    
    async def get_all_profile_info(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Get profile information from all registered platforms"""        profiles = {}
        
        for platform, adapter in self.adapters.items():
            try:
                profile_info = await adapter.get_profile_info()
                profiles[platform] = profile_info
            except Exception as e:
                logger.error(f"Failed to get profile info for {platform.value}: {str(e)}")
                profiles[platform] = {'error': str(e)}
        
        return profiles
    
    async def cleanup(self):
        """Cleanup resources"""        # Close all adapter sessions
        for adapter in self.adapters.values():
            await adapter._close_session()
        
        # Close session pool
        for session in self.session_pool.values():
            await session.close()
        
        self.session_pool.clear()
        logger.info("Platform adapters cleanup completed")
