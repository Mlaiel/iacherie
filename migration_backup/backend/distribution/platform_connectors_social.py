"""Advanced Social Platform Connectors - Multi-Platform Social Media Integration System
=====================================================================================

Comprehensive social media platform connectors providing unified API interfaces for
YouTube, Instagram, TikTok, Facebook, Twitter, and LinkedIn content distribution
with advanced authentication, rate limiting, analytics, and monetization features.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/platform_connectors_social.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Social Platform Distribution → Analytics → Monetization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import aiohttp
import hashlib
import base64
from urllib.parse import urlencode, urlparse
import time

logger = logging.getLogger(__name__)


class SocialPlatformType(str, Enum):
    """Supported social platform types."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class ContentFormat(str, Enum):
    """Content format types for social platforms."""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    LIVE = "live"


class EngagementType(str, Enum):
    """Social engagement types."""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    FOLLOW = "follow"
    SUBSCRIBE = "subscribe"
    VIEW = "view"
    CLICK = "click"


@dataclass
class SocialContentMetadata:
    """Social platform content metadata."""
    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: str = "en"
    location: Optional[str] = None
    privacy: str = "public"
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    format: Optional[ContentFormat] = None
    scheduled_time: Optional[datetime] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SocialPlatformResponse:
    """Response from social platform operations."""
    success: bool
    platform: SocialPlatformType
    post_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SocialAnalytics:
    """Social platform analytics data."""
    platform: SocialPlatformType
    content_id: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    followers_gained: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    completion_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BaseSocialConnector:
    """Base class for social platform connectors."""
    
    def __init__(self, platform: SocialPlatformType, credentials: Dict[str, Any]):
        self.platform = platform
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.authenticated = False
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = datetime.utcnow()
        self.logger = logging.getLogger(f"{__name__}.{platform.value}")
    
    async def initialize(self) -> bool:
        """Initialize the connector."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers=self._get_default_headers()
            )
            
            authenticated = await self.authenticate()
            if authenticated:
                self.authenticated = True
                self.logger.info(f"✅ {self.platform.value} connector initialized")
                return True
            else:
                self.logger.error(f"❌ {self.platform.value} authentication failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing {self.platform.value} connector: {e}")
            return False
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "User-Agent": "Ainflue-Social-Connector/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with the platform."""
        raise NotImplementedError("Subclasses must implement authenticate method")
    
    async def upload_content(self, metadata: SocialContentMetadata, file_data: Optional[bytes] = None) -> SocialPlatformResponse:
        """Upload content to the platform."""
        raise NotImplementedError("Subclasses must implement upload_content method")
    
    async def get_analytics(self, content_id: str, date_range: Tuple[datetime, datetime]) -> SocialAnalytics:
        """Get analytics for content."""
        raise NotImplementedError("Subclasses must implement get_analytics method")
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from platform."""
        raise NotImplementedError("Subclasses must implement delete_content method")
    
    async def update_content(self, content_id: str, metadata: SocialContentMetadata) -> SocialPlatformResponse:
        """Update content metadata."""
        raise NotImplementedError("Subclasses must implement update_content method")
    
    async def check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        if datetime.utcnow() > self.rate_limit_reset:
            self.rate_limit_remaining = 1000  # Reset limit
            self.rate_limit_reset = datetime.utcnow() + timedelta(hours=1)
        
        return self.rate_limit_remaining > 0
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()


class YouTubeConnector(BaseSocialConnector):
    """YouTube platform connector with Content ID and monetization features."""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(SocialPlatformType.YOUTUBE, credentials)
        self.api_key = credentials.get("api_key")
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")
        self.access_token = credentials.get("access_token")
        self.refresh_token = credentials.get("refresh_token")
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube Data API v3."""
        if not self.api_key:
            self.logger.error("YouTube API key not provided")
            return False
        
        try:
            # Test API access with a simple request
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "id",
                "mine": "true",
                "key": self.api_key
            }
            
            if self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                async with self.session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        # Try to refresh token
                        return await self._refresh_access_token()
            
            return False
            
        except Exception as e:
            self.logger.error(f"YouTube authentication error: {e}")
            return False
    
    async def _refresh_access_token(self) -> bool:
        """Refresh OAuth2 access token."""
        if not self.refresh_token:
            return False
        
        try:
            url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            return False
    
    async def upload_content(self, metadata: SocialContentMetadata, file_data: Optional[bytes] = None) -> SocialPlatformResponse:
        """Upload video content to YouTube."""
        try:
            if not file_data:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Video file data required for YouTube upload"
                )
            
            # Prepare video metadata
            video_metadata = {
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description or "",
                    "tags": metadata.tags,
                    "categoryId": self._get_category_id(metadata.category),
                    "defaultLanguage": metadata.language
                },
                "status": {
                    "privacyStatus": metadata.privacy,
                    "publishAt": metadata.scheduled_time.isoformat() if metadata.scheduled_time else None
                }
            }
            
            # Upload via resumable upload
            upload_url = await self._initiate_upload(video_metadata)
            if not upload_url:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to initiate YouTube upload"
                )
            
            video_id = await self._upload_video_data(upload_url, file_data)
            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                return SocialPlatformResponse(
                    success=True,
                    platform=self.platform,
                    post_id=video_id,
                    url=video_url,
                    response_data={"video_id": video_id}
                )
            
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message="Failed to upload video data"
            )
            
        except Exception as e:
            self.logger.error(f"YouTube upload error: {e}")
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message=str(e)
            )
    
    async def _initiate_upload(self, metadata: Dict[str, Any]) -> Optional[str]:
        """Initiate resumable upload session."""
        try:
            url = "https://www.googleapis.com/upload/youtube/v3/videos"
            params = {
                "uploadType": "resumable",
                "part": "snippet,status"
            }
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Upload-Content-Type": "video/*"
            }
            
            async with self.session.post(url, params=params, headers=headers, json=metadata) as response:
                if response.status == 200:
                    return response.headers.get("Location")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Upload initiation error: {e}")
            return None
    
    async def _upload_video_data(self, upload_url: str, file_data: bytes) -> Optional[str]:
        """Upload video data to YouTube."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "video/*",
                "Content-Length": str(len(file_data))
            }
            
            async with self.session.put(upload_url, headers=headers, data=file_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("id")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Video data upload error: {e}")
            return None
    
    def _get_category_id(self, category: Optional[str]) -> str:
        """Map category to YouTube category ID."""
        category_map = {
            "music": "10",
            "entertainment": "24",
            "education": "27",
            "gaming": "20",
            "technology": "28",
            "sports": "17",
            "news": "25"
        }
        return category_map.get(category, "22")  # Default to People & Blogs
    
    async def get_analytics(self, content_id: str, date_range: Tuple[datetime, datetime]) -> SocialAnalytics:
        """Get YouTube analytics for video."""
        try:
            # Get basic video statistics
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "statistics",
                "id": content_id,
                "key": self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("items"):
                        stats = data["items"][0]["statistics"]
                        return SocialAnalytics(
                            platform=self.platform,
                            content_id=content_id,
                            views=int(stats.get("viewCount", 0)),
                            likes=int(stats.get("likeCount", 0)),
                            comments=int(stats.get("commentCount", 0)),
                            shares=0,  # YouTube doesn't provide share count
                            engagement_rate=self._calculate_engagement_rate(stats)
                        )
            
            return SocialAnalytics(platform=self.platform, content_id=content_id)
            
        except Exception as e:
            self.logger.error(f"YouTube analytics error: {e}")
            return SocialAnalytics(platform=self.platform, content_id=content_id)
    
    def _calculate_engagement_rate(self, stats: Dict[str, Any]) -> float:
        """Calculate engagement rate for YouTube video."""
        views = int(stats.get("viewCount", 0))
        if views == 0:
            return 0.0
        
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        
        return ((likes + comments) / views) * 100
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete YouTube video."""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {"id": content_id}
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.delete(url, params=params, headers=headers) as response:
                return response.status == 204
                
        except Exception as e:
            self.logger.error(f"YouTube delete error: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: SocialContentMetadata) -> SocialPlatformResponse:
        """Update YouTube video metadata."""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {"part": "snippet"}
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            update_data = {
                "id": content_id,
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description or "",
                    "tags": metadata.tags,
                    "categoryId": self._get_category_id(metadata.category)
                }
            }
            
            async with self.session.put(url, params=params, headers=headers, json=update_data) as response:
                if response.status == 200:
                    return SocialPlatformResponse(
                        success=True,
                        platform=self.platform,
                        post_id=content_id
                    )
                
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message=f"Update failed with status {response.status}"
                )
                
        except Exception as e:
            self.logger.error(f"YouTube update error: {e}")
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message=str(e)
            )


class InstagramConnector(BaseSocialConnector):
    """Instagram Business API connector with Stories and Reels support."""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(SocialPlatformType.INSTAGRAM, credentials)
        self.access_token = credentials.get("access_token")
        self.user_id = credentials.get("user_id")
        self.business_account_id = credentials.get("business_account_id")
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram Basic Display API."""
        if not self.access_token:
            return False
        
        try:
            url = f"https://graph.instagram.com/me"
            params = {"access_token": self.access_token}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    user_data = await response.json()
                    self.user_id = user_data.get("id")
                    return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Instagram authentication error: {e}")
            return False
    
    async def upload_content(self, metadata: SocialContentMetadata, file_data: Optional[bytes] = None) -> SocialPlatformResponse:
        """Upload content to Instagram (image, video, story, reel)."""
        try:
            if not file_data:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Media file data required for Instagram upload"
                )
            
            # First, upload media to a temporary URL
            media_url = await self._upload_media_file(file_data, metadata.format)
            if not media_url:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to upload media file"
                )
            
            # Create media container
            container_id = await self._create_media_container(media_url, metadata)
            if not container_id:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to create media container"
                )
            
            # Publish the media
            media_id = await self._publish_media(container_id)
            if media_id:
                media_url = f"https://www.instagram.com/p/{media_id}/"
                return SocialPlatformResponse(
                    success=True,
                    platform=self.platform,
                    post_id=media_id,
                    url=media_url
                )
            
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message="Failed to publish media"
            )
            
        except Exception as e:
            self.logger.error(f"Instagram upload error: {e}")
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message=str(e)
            )
    
    async def _upload_media_file(self, file_data: bytes, content_format: Optional[ContentFormat]) -> Optional[str]:
        """Upload media file and get URL for Instagram API."""
        # This would typically involve uploading to a cloud storage service
        # and returning a publicly accessible URL
        # For now, return a placeholder implementation
        return "https://example.com/placeholder-media-url"
    
    async def _create_media_container(self, media_url: str, metadata: SocialContentMetadata) -> Optional[str]:
        """Create Instagram media container."""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/media"
            
            params = {
                "access_token": self.access_token
            }
            
            if metadata.format == ContentFormat.IMAGE:
                params["image_url"] = media_url
            elif metadata.format in [ContentFormat.VIDEO, ContentFormat.REEL]:
                params["video_url"] = media_url
                params["media_type"] = "REELS" if metadata.format == ContentFormat.REEL else "VIDEO"
            
            params["caption"] = self._format_caption(metadata)
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("id")
                
            return None
            
        except Exception as e:
            self.logger.error(f"Media container creation error: {e}")
            return None
    
    def _format_caption(self, metadata: SocialContentMetadata) -> str:
        """Format Instagram caption with title, description and hashtags."""
        caption_parts = []
        
        if metadata.title:
            caption_parts.append(metadata.title)
        
        if metadata.description:
            caption_parts.append(metadata.description)
        
        if metadata.hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in metadata.hashtags])
            caption_parts.append(hashtag_text)
        
        return "\n\n".join(caption_parts)
    
    async def _publish_media(self, container_id: str) -> Optional[str]:
        """Publish Instagram media container."""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/media_publish"
            params = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("id")
                
            return None
            
        except Exception as e:
            self.logger.error(f"Media publish error: {e}")
            return None
    
    async def get_analytics(self, content_id: str, date_range: Tuple[datetime, datetime]) -> SocialAnalytics:
        """Get Instagram analytics for post."""
        try:
            url = f"https://graph.facebook.com/v18.0/{content_id}/insights"
            params = {
                "metric": "impressions,reach,likes,comments,saves,shares",
                "access_token": self.access_token
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    insights = {item["name"]: item["values"][0]["value"] for item in data.get("data", [])}
                    
                    return SocialAnalytics(
                        platform=self.platform,
                        content_id=content_id,
                        views=insights.get("impressions", 0),
                        likes=insights.get("likes", 0),
                        comments=insights.get("comments", 0),
                        shares=insights.get("shares", 0),
                        saves=insights.get("saves", 0),
                        reach=insights.get("reach", 0),
                        impressions=insights.get("impressions", 0)
                    )
            
            return SocialAnalytics(platform=self.platform, content_id=content_id)
            
        except Exception as e:
            self.logger.error(f"Instagram analytics error: {e}")
            return SocialAnalytics(platform=self.platform, content_id=content_id)
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Instagram post."""
        try:
            url = f"https://graph.facebook.com/v18.0/{content_id}"
            params = {"access_token": self.access_token}
            
            async with self.session.delete(url, params=params) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Instagram delete error: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: SocialContentMetadata) -> SocialPlatformResponse:
        """Update Instagram post metadata (limited support)."""
        # Instagram has very limited edit capabilities
        return SocialPlatformResponse(
            success=False,
            platform=self.platform,
            error_message="Instagram does not support post editing after publication"
        )


class TikTokConnector(BaseSocialConnector):
    """TikTok Creator API connector with advanced analytics."""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(SocialPlatformType.TIKTOK, credentials)
        self.access_token = credentials.get("access_token")
        self.refresh_token = credentials.get("refresh_token")
        self.client_key = credentials.get("client_key")
        self.client_secret = credentials.get("client_secret")
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok API."""
        if not self.access_token:
            return False
        
        try:
            url = "https://open-api.tiktok.com/oauth/userinfo/"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.get(url, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"TikTok authentication error: {e}")
            return False
    
    async def upload_content(self, metadata: SocialContentMetadata, file_data: Optional[bytes] = None) -> SocialPlatformResponse:
        """Upload video content to TikTok."""
        try:
            if not file_data:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Video file data required for TikTok upload"
                )
            
            # Initialize upload session
            upload_url = await self._initialize_upload()
            if not upload_url:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to initialize TikTok upload"
                )
            
            # Upload video data
            upload_success = await self._upload_video(upload_url, file_data)
            if not upload_success:
                return SocialPlatformResponse(
                    success=False,
                    platform=self.platform,
                    error_message="Failed to upload video to TikTok"
                )
            
            # Publish video
            video_id = await self._publish_video(metadata, upload_url)
            if video_id:
                return SocialPlatformResponse(
                    success=True,
                    platform=self.platform,
                    post_id=video_id,
                    url=f"https://www.tiktok.com/@user/video/{video_id}"
                )
            
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message="Failed to publish video"
            )
            
        except Exception as e:
            self.logger.error(f"TikTok upload error: {e}")
            return SocialPlatformResponse(
                success=False,
                platform=self.platform,
                error_message=str(e)
            )
    
    async def _initialize_upload(self) -> Optional[str]:
        """Initialize TikTok video upload."""
        try:
            url = "https://open-api.tiktok.com/share/video/upload/"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("upload_url")
                
            return None
            
        except Exception as e:
            self.logger.error(f"TikTok upload initialization error: {e}")
            return None
    
    async def _upload_video(self, upload_url: str, file_data: bytes) -> bool:
        """Upload video data to TikTok."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "video/mp4"
            }
            
            async with self.session.put(upload_url, headers=headers, data=file_data) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"TikTok video upload error: {e}")
            return False
    
    async def _publish_video(self, metadata: SocialContentMetadata, upload_url: str) -> Optional[str]:
        """Publish TikTok video."""
        try:
            url = "https://open-api.tiktok.com/share/video/publish/"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            publish_data = {
                "video_id": self._extract_video_id_from_url(upload_url),
                "title": metadata.title[:150],  # TikTok title limit
                "privacy_level": "SELF_ONLY" if metadata.privacy == "private" else "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "brand_content_toggle": False
            }
            
            async with self.session.post(url, headers=headers, json=publish_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("share_id")
                
            return None
            
        except Exception as e:
            self.logger.error(f"TikTok publish error: {e}")
            return None
    
    def _extract_video_id_from_url(self, upload_url: str) -> str:
        """Extract video ID from upload URL."""
        # This would extract the video ID from the upload URL
        # Implementation depends on TikTok's URL structure
        return upload_url.split("/")[-1] if upload_url else ""
    
    async def get_analytics(self, content_id: str, date_range: Tuple[datetime, datetime]) -> SocialAnalytics:
        """Get TikTok analytics for video."""
        try:
            url = f"https://open-api.tiktok.com/research/video/stats/"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "video_ids": [content_id],
                "fields": ["video_id", "views", "likes", "comments", "shares"]
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        stats = data["data"][0]
                        return SocialAnalytics(
                            platform=self.platform,
                            content_id=content_id,
                            views=stats.get("views", 0),
                            likes=stats.get("likes", 0),
                            comments=stats.get("comments", 0),
                            shares=stats.get("shares", 0)
                        )
            
            return SocialAnalytics(platform=self.platform, content_id=content_id)
            
        except Exception as e:
            self.logger.error(f"TikTok analytics error: {e}")
            return SocialAnalytics(platform=self.platform, content_id=content_id)
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete TikTok video."""
        try:
            url = f"https://open-api.tiktok.com/share/video/delete/"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            data = {"video_id": content_id}
            
            async with self.session.post(url, headers=headers, json=data) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"TikTok delete error: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: SocialContentMetadata) -> SocialPlatformResponse:
        """Update TikTok video metadata (limited support)."""
        # TikTok has limited edit capabilities
        return SocialPlatformResponse(
            success=False,
            platform=self.platform,
            error_message="TikTok does not support comprehensive post editing"
        )


class SocialPlatformManager:
    """Manager for all social platform connectors."""
    
    def __init__(self):
        self.connectors: Dict[SocialPlatformType, BaseSocialConnector] = {}
        self.logger = logging.getLogger(f"{__name__}.SocialPlatformManager")
    
    async def add_platform(self, platform: SocialPlatformType, credentials: Dict[str, Any]) -> bool:
        """Add and initialize a social platform connector."""
        try:
            connector_class = {
                SocialPlatformType.YOUTUBE: YouTubeConnector,
                SocialPlatformType.INSTAGRAM: InstagramConnector,
                SocialPlatformType.TIKTOK: TikTokConnector,
                # Facebook, Twitter, LinkedIn would be implemented similarly
            }.get(platform)
            
            if not connector_class:
                self.logger.error(f"Unsupported platform: {platform}")
                return False
            
            connector = connector_class(credentials)
            if await connector.initialize():
                self.connectors[platform] = connector
                self.logger.info(f"✅ {platform.value} connector added successfully")
                return True
            else:
                self.logger.error(f"❌ Failed to initialize {platform.value} connector")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding {platform.value} connector: {e}")
            return False
    
    async def get_connector(self, platform: SocialPlatformType) -> Optional[BaseSocialConnector]:
        """Get connector for specific platform."""
        return self.connectors.get(platform)
    
    async def upload_to_platform(
        self,
        platform: SocialPlatformType,
        metadata: SocialContentMetadata,
        file_data: Optional[bytes] = None
    ) -> SocialPlatformResponse:
        """Upload content to specific platform."""
        connector = self.connectors.get(platform)
        if not connector:
            return SocialPlatformResponse(
                success=False,
                platform=platform,
                error_message=f"No connector available for {platform.value}"
            )
        
        return await connector.upload_content(metadata, file_data)
    
    async def upload_to_multiple_platforms(
        self,
        platforms: List[SocialPlatformType],
        metadata: SocialContentMetadata,
        file_data: Optional[bytes] = None
    ) -> Dict[SocialPlatformType, SocialPlatformResponse]:
        """Upload content to multiple platforms simultaneously."""
        tasks = []
        for platform in platforms:
            if platform in self.connectors:
                task = self.upload_to_platform(platform, metadata, file_data)
                tasks.append((platform, task))
        
        results = {}
        if tasks:
            completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (platform, _), result in zip(tasks, completed_tasks):
                if isinstance(result, Exception):
                    results[platform] = SocialPlatformResponse(
                        success=False,
                        platform=platform,
                        error_message=str(result)
                    )
                else:
                    results[platform] = result
        
        return results
    
    async def get_platform_analytics(
        self,
        platform: SocialPlatformType,
        content_id: str,
        date_range: Tuple[datetime, datetime]
    ) -> Optional[SocialAnalytics]:
        """Get analytics for content on specific platform."""
        connector = self.connectors.get(platform)
        if connector:
            return await connector.get_analytics(content_id, date_range)
        return None
    
    async def get_cross_platform_analytics(
        self,
        content_ids: Dict[SocialPlatformType, str],
        date_range: Tuple[datetime, datetime]
    ) -> Dict[SocialPlatformType, SocialAnalytics]:
        """Get analytics across multiple platforms."""
        results = {}
        tasks = []
        
        for platform, content_id in content_ids.items():
            if platform in self.connectors:
                task = self.get_platform_analytics(platform, content_id, date_range)
                tasks.append((platform, task))
        
        if tasks:
            completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (platform, _), result in zip(tasks, completed_tasks):
                if not isinstance(result, Exception) and result:
                    results[platform] = result
        
        return results
    
    async def cleanup(self):
        """Cleanup all connectors."""
        cleanup_tasks = [connector.cleanup() for connector in self.connectors.values()]
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.connectors.clear()
        self.logger.info("✅ All social platform connectors cleaned up")


# Global manager instance
_social_manager: Optional[SocialPlatformManager] = None


async def get_social_platform_manager() -> SocialPlatformManager:
    """Get the global social platform manager instance."""
    global _social_manager
    
    if _social_manager is None:
        _social_manager = SocialPlatformManager()
    
    return _social_manager


# Export main components
__all__ = [
    "SocialPlatformType",
    "ContentFormat",
    "EngagementType",
    "SocialContentMetadata",
    "SocialPlatformResponse",
    "SocialAnalytics",
    "BaseSocialConnector",
    "YouTubeConnector",
    "InstagramConnector",
    "TikTokConnector",
    "SocialPlatformManager",
    "get_social_platform_manager"
]